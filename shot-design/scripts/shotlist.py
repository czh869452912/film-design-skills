#!/usr/bin/env python3
"""Validate structure and render shot/panel plans. Does not assess film quality."""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from sequence import beat_ids, iter_panels, load, normalize, number, resolve_image, shot_duration, validate

REFERENCE_DIR = Path(__file__).resolve().parents[1] / "references"


def as_text(value) -> str:
    return "" if value is None else str(value).strip()


def load_mechanisms() -> dict[str, str]:
    path = REFERENCE_DIR / "templates.md"
    if not path.exists():
        return {}
    found = {}
    for mid, name in re.findall(r"\|\s*(M\d{2})\s*\|\s*([^|]+?)\s*\|", path.read_text(encoding="utf-8")):
        found.setdefault(mid, name.strip())
    return found


def check(data: dict) -> tuple[list[str], list[str]]:
    errors, warnings = validate(data)
    if errors:
        return errors, warnings
    mechanisms = load_mechanisms()
    for shot in data["shots"]:
        for mid in as_text(shot.get("mechanism")).upper().replace(" ", "").split("+"):
            if mid and mid not in mechanisms:
                errors.append(f"{shot['id']}: unknown mechanism {mid}")
    return errors, warnings


def total_duration(data: dict) -> float:
    return sum(shot_duration(s) or 0 for s in data["shots"])


def timing_complete(data: dict) -> bool:
    return all(shot_duration(s) is not None for s in data["shots"])


def time_text(value) -> str:
    return f"{value:g}s" if value is not None else "pending"


def cell(value) -> str:
    return as_text(value).replace("|", "/").replace("\n", " ") or "—"


def table(headers, rows) -> str:
    return "\n".join(["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)] +
                     ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]) + "\n"


def shot_label(framing: dict) -> str:
    fields = [framing.get("size"), framing.get("angle")]
    if number(framing.get("lens_mm")):
        fields.append(f"{framing['lens_mm']:g}mm")
    return " / ".join(as_text(v) for v in fields if v) or "unspecified"


def camera_brief(camera: dict) -> str:
    return ", ".join(as_text(camera[k]) for k in ("move", "amplitude", "speed") if camera.get(k) and camera[k] != "none") or "unspecified"


def mechanism_label(shot: dict, mechanisms=None) -> str:
    return as_text(shot.get("mechanism")) or "—"


def beat_name(beats: dict, bid: str) -> str:
    return as_text((beats.get(bid) or {}).get("name")) or bid


def beat_names(data: dict, shot: dict) -> str:
    beats = {b["id"]: b for b in data.get("beats", [])}
    return ", ".join(beat_name(beats, bid) for bid in beat_ids(shot))


def action_text(shot: dict) -> str:
    return as_text((shot.get("action") or {}).get("primary")) or " → ".join(p["description"] for p in shot["panels"])


def sound_text(sound: dict) -> str:
    return "; ".join(f"{k}: {v}" for k, v in sound.items() if v)


def render_md(data: dict) -> str:
    d = normalize(data)
    rows = [(s["id"], time_text(s["duration_s"]), len(s["panels"]), beat_names(d, s),
             shot_label(s.get("framing") or {}), camera_brief(s.get("camera") or {}), action_text(s)) for s in d["shots"]]
    return f"# {d.get('title') or 'Shot plan'}\n\n" + table(
        ["Shot", "Duration", "Panels", "Beats (optional)", "Framing", "Camera", "Picture & action"], rows)


def render_beats(data: dict) -> str:
    beats = data.get("beats") or []
    if not beats:
        return "No beat sheet declared. Beats are optional; inspect the action and viewing plan.\n"
    rows = []
    for beat in beats:
        owned = [s["id"] for s in data["shots"] if beat["id"] in beat_ids(s)]
        rows.append((beat["id"], beat.get("name"), beat.get("goal"), beat.get("knowledge_change"), ", ".join(owned)))
    return "# Beat associations (may cross cuts)\n\n" + table(["Beat", "Name", "Action / change", "Viewer evidence", "Shots"], rows)


def render_framing(data: dict) -> str:
    out = ["# Viewing choices", ""]
    for shot in data["shots"]:
        framing = shot.get("framing") or {}
        if framing.get("options"):
            out.append(f"{shot['id']} — chosen: {framing.get('chosen', 'open')}")
            for option in framing["options"]:
                out.append(f"- {option.get('name', '')}: " + "; ".join(f"{k}: {v}" for k, v in option.items() if k != "name"))
    if len(out) == 2:
        out.append("No alternatives recorded. Compare only when a viewing decision is genuinely open.")
    return "\n".join(out) + "\n"


def cut_checks(prev: dict, shot: dict, beats=None) -> dict[str, bool]:
    """Presence of notes only. No inferred pass, no weighted total."""
    return {
        "outgoing_state": bool(prev["panels"][-1].get("description")) if prev.get("panels") else bool((prev.get("camera") or {}).get("end_frame")),
        "incoming_state": bool(shot["panels"][0].get("description")) if shot.get("panels") else bool((shot.get("camera") or {}).get("start_frame")),
        "cut_note": bool((prev.get("transition_out") or {}).get("matches")),
        "continuity_notes": bool(prev.get("continuity") or shot.get("continuity")),
    }


def render_cuts(data: dict) -> str:
    d = normalize(data)
    out = ["# Cut review", "", "Notes present is not a pass. Action, gaze and space require visual review; no quality score is computed.", ""]
    if len(d["shots"]) < 2:
        out.append("Single shot: no cuts. Review its internal panel progression.")
    for a, b in zip(d["shots"], d["shots"][1:]):
        out += [f"{a['id']} → {b['id']}", f"  Out: {a['panels'][-1]['description']}", f"  In: {b['panels'][0]['description']}"]
        out += [f"  {key}: {'note present' if present else 'not recorded'}" for key, present in cut_checks(a, b).items()]
        out.append("  Visual action/gaze/space: not assessed by this script")
    return "\n".join(out) + "\n"


def panel_rows(data: dict):
    cursor = 0.0
    for p in iter_panels(data):
        duration = p["duration_s"]
        window = f"{cursor:g}–{cursor + duration:g}s" if cursor is not None and duration is not None else "pending"
        yield p, window
        cursor = cursor + duration if cursor is not None and duration is not None else None


def render_sheet(data: dict) -> str:
    rows = [(f"{p['shot_id']} / {p['id']}", t, shot_label(p.get("framing") or {}),
             camera_brief(p.get("camera") or {}), p["description"], sound_text(p.get("sound") or {})) for p, t in panel_rows(data)]
    return "# Production sheet — panel changes within a shot are not cuts\n\n" + table(
        ["Shot / panel", "Time", "Framing", "Camera", "Picture & action", "Sound"], rows)


def render_timeline(data: dict, width=72) -> str:
    out = ["# Timeline", "", "CUT marks a shot boundary; NEXT is another panel in the same continuous shot."]
    for p, t in panel_rows(data):
        out.append(f"{'CUT ' if p['shot_start'] else 'NEXT'} {p['shot_id']}/{p['id']}  {t}: {p['description']}")
    return "\n".join(out) + "\n"


def render_csv(data: dict) -> str:
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["shot", "panel", "shot_start", "time", "duration_s", "framing", "camera", "description", "sound"])
    for p, t in panel_rows(data):
        writer.writerow([p["shot_id"], p["id"], p["shot_start"], t, p["duration_s"], shot_label(p.get("framing") or {}), camera_brief(p.get("camera") or {}), p["description"], sound_text(p.get("sound") or {})])
    return out.getvalue()


def duration_stats(data: dict) -> dict:
    durations = [shot_duration(s) or 0 for s in data["shots"]]
    total, count = sum(durations), len(durations)
    mean = total / count
    lo, hi = min(durations), max(durations)
    return dict(durations=durations, count=count, total=total, mean=mean, min=lo, max=hi,
                spread=(hi-lo)/mean if mean else 0)


def detect_shape(data: dict) -> str:
    if not timing_complete(data):
        return "timing pending"
    values = duration_stats(data)["durations"]
    if len(values) == 1:
        return "single"
    if max(values) - min(values) < 0.001:
        return "equal durations"
    return "varied durations"


def render_rhythm(data: dict) -> str:
    out = ["# Timing observations", "", f"{detect_shape(data)}. This is descriptive; equal durations and long impacts are not errors.", ""]
    out.append(table(["Shot", "Duration", "Panels"], [(s["id"], time_text(shot_duration(s)), len(s.get("panels") or [None])) for s in data["shots"]]))
    out.append("Set timing by performance, dialogue, sound and playback. No required climax location or duration ratio.")
    return "\n".join(out) + "\n"


def render_load(data: dict) -> str:
    return "# Plan inventory (not cognitive-load measurement)\n\n" + table(
        ["Shot", "Panels", "Beat associations", "Continuity notes"],
        [(s["id"], len(s.get("panels") or [None]), len(beat_ids(s)), len(s.get("continuity") or [])) for s in data["shots"]])


def render_storyboard(data: dict) -> str:
    out = ["# Storyboard drawing brief", "", "Keep shot and panel ids distinct. Multiple panels can describe one continuous action.", ""]
    if data.get("scene"):
        out += ["Scene / blocking:", json.dumps(data["scene"], ensure_ascii=False, indent=2), ""]
    for p, t in panel_rows(data):
        out += [f"[{p['shot_id']} / {p['id']}] {t}", f"  Camera: {camera_brief(p.get('camera') or {})}; {shot_label(p.get('framing') or {})}", f"  Visible: {p['description']}"]
        if p.get("state"):
            out.append("  State: " + json.dumps(p["state"], ensure_ascii=False))
        if p.get("staging"):
            out.append("  Staging: " + json.dumps(p["staging"], ensure_ascii=False))
        if p["storyboard"].get("overlays"):
            out.append("  Overlays: " + json.dumps(p["storyboard"]["overlays"], ensure_ascii=False))
        out.append("")
    out.append("Drawing briefs are not evidence that the panels were rendered or visually reviewed.")
    return "\n".join(out) + "\n"


def render_brief(data: dict) -> str:
    out = [f"# Design handoff — {data.get('title') or 'untitled'}", ""]
    for key in ("intent", "scene", "target"):
        if data.get(key):
            out += [key + ":", json.dumps(data[key], ensure_ascii=False, indent=2), ""]
    out.append(render_sheet(data))
    for shot in data["shots"]:
        for key in ("purpose", "continuity", "bans", "references", "transition_out"):
            if shot.get(key):
                out.append(f"{shot['id']} {key}: " + json.dumps(shot[key], ensure_ascii=False))
    out += ["", "Review record (self-reported, not certified by this script): " + json.dumps(data.get("review") or {"status": "not-reviewed"}, ensure_ascii=False),
            "Use the target model's current adapter only when generation is requested. Panel ids are not model shot numbers."]
    return "\n".join(out) + "\n"


def build_scaffold(title: str, duration: float | None, aspect: str, model: str, count: int) -> dict:
    if count < 1 or (duration is not None and (not number(duration) or duration <= 0)):
        raise SystemExit("shot count and optional duration must be positive")
    result = {"title": title, "review": {"status": "not-reviewed"}, "shots": []}
    target = {k: v for k, v in {"duration_s": duration, "aspect": aspect, "model": model}.items() if v is not None and v != ""}
    if target:
        result["target"] = target
    # Mechanical allocation is clearly provisional, with no invented dramatic arc.
    for i in range(count):
        sid = f"S{i+1:02d}"
        panel = {"id": sid + "-P01", "description": "TODO: visible action/state"}
        if duration is not None:
            panel["duration_s"] = duration / count
        result["shots"].append({"id": sid, "purpose": "TODO: why this view", "panels": [panel]})
    return result


RENDERERS = dict(md=render_md, beats=render_beats, framing=render_framing, cuts=render_cuts,
                 sheet=render_sheet, timeline=render_timeline, load=render_load, rhythm=render_rhythm,
                 csv=render_csv, storyboard=render_storyboard, brief=render_brief)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["validate", "render", "mechanisms", "init"])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--format", default="md", choices=list(RENDERERS))
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--strict", action="store_true", help="treat structural warnings as failures; no artistic rules")
    ap.add_argument("--timed", action="store_true", help="require all panel timings")
    ap.add_argument("--check-images", action="store_true", help="check actual image files; does not inspect visual contents")
    ap.add_argument("--images", default=None)
    ap.add_argument("--title", default="Untitled")
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--aspect", default="")
    ap.add_argument("--model", default="")
    ap.add_argument("--shots", type=int, default=1)
    args = ap.parse_args()
    if args.command == "mechanisms":
        for mid, name in load_mechanisms().items():
            print(f"{mid}  {name}")
        return 0
    if args.command == "init":
        target = Path(args.path or "shot-plan.json")
        if target.exists():
            raise SystemExit(f"refusing to overwrite {target}")
        data = build_scaffold(args.title, args.duration, args.aspect, args.model, args.shots)
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"created draft: {target}; fill TODOs. Supplied timing is provisional, not a designed rhythm.")
        return 0
    if not args.path:
        raise SystemExit("shot list JSON path required")
    path = Path(args.path)
    data = load(path)
    errors, warnings = check(data)
    if not errors and args.timed:
        errors, warnings = validate(data, timed=True)
    if not errors and args.check_images:
        for p in iter_panels(data):
            if resolve_image(p, images=Path(args.images) if args.images else None, base=path.parent) is None:
                errors.append(f"{p['id']}: image file missing")
    for message in errors:
        print("ERROR " + message, file=sys.stderr)
    for message in warnings:
        print("WARN " + message, file=sys.stderr)
    if errors or (args.strict and warnings):
        return 1
    if not args.quiet:
        count = sum(1 for _ in iter_panels(data))
        timing = time_text(total_duration(data)) if timing_complete(data) else "timing pending"
        print(f"STRUCTURE VALID: {len(data['shots'])} shots, {count} panels, {timing}; visual comprehension not assessed.", file=sys.stderr)
    if args.command == "render":
        print(RENDERERS[args.format](data), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
