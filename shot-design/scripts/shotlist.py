#!/usr/bin/env python3
"""Validate a shot list and render it for design review, storyboard drawing, or handoff.

The tool checks design structure and timing; it never writes prompt syntax for
image or video models — those belong to the model skills.

Usage:
    python shotlist.py validate shotlist.json
    python shotlist.py render shotlist.json --format md          # review table
    python shotlist.py render shotlist.json --format beats       # beat sheet
    python shotlist.py render shotlist.json --format storyboard  # drawing brief per panel
    python shotlist.py render shotlist.json --format brief       # handoff brief for the prompt writer
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

MODEL_LIMITS = {
    "seedance-2.5": (4.0, 30.0),
    "seedance-2-5": (4.0, 30.0),
    "h3": (4.0, 15.0),
    "minimax-h3": (4.0, 15.0),
    "generic": (1.0, 60.0),
}

REQUIRED_PATHS = [
    ("id", ("id",)),
    ("duration_s", ("duration_s",)),
    ("purpose", ("purpose",)),
    ("framing.size", ("framing", "size")),
    ("camera.move", ("camera", "move")),
    ("action.primary", ("action", "primary")),
    ("transition_out.type", ("transition_out", "type")),
]

DIAL_KEYS = ("proximity", "power", "pressure", "stability", "value", "time")
DIRECTIONS = {"left-to-right", "right-to-left", "toward-camera", "away-from-camera", "none"}
OVERLAY_TYPES = {"arrow", "sight", "impact", "orbit"}
KNOWN_ASPECTS = {"16:9", "9:16", "1:1", "4:3", "4:5", "2.39:1", "2.35:1"}
BEAT_NAMES = {
    "establish", "omen", "reveal", "charge", "burst", "impact",
    "aftermath", "reaction", "turn", "landing",
}

REFERENCE_DIR = Path(__file__).resolve().parents[1] / "references"
MECHANISM_RE = re.compile(r"\|\s*(M\d{2})\s*\|\s*([^|]+?)\s*\|")


def load_mechanisms() -> dict[str, str]:
    """Read the mechanism table out of references/templates.md (single source of truth)."""
    path = REFERENCE_DIR / "templates.md"
    if not path.exists():
        return {}
    found: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = MECHANISM_RE.search(line)
        if match:
            found.setdefault(match.group(1), match.group(2).strip())
    return found


def get(data: dict, path: tuple[str, ...]) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value)


def valid_point(value: Any) -> bool:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return False
    return all(isinstance(item, (int, float)) and 0 <= float(item) <= 1 for item in value)


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise SystemExit("shot list must be a JSON object")
    if not isinstance(data.get("shots"), list) or not data["shots"]:
        raise SystemExit("shot list needs a non-empty 'shots' array")
    return data


def total_duration(data: dict) -> float:
    return sum(float(shot.get("duration_s") or 0) for shot in data["shots"])


def check(data: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    known_mechanisms = load_mechanisms()

    if not as_text(data.get("title")):
        warnings.append("missing title")

    intent = data.get("intent") or {}
    for key in ("logline", "turn"):
        if not as_text(intent.get(key)):
            errors.append(f"intent.{key} is required: the sequence needs a stated change")

    target = data.get("target") or {}
    style = data.get("style") or {}
    model = as_text(target.get("model")).lower() or "generic"
    lo, hi = MODEL_LIMITS.get(model, MODEL_LIMITS["generic"])
    total = 0.0

    aspect = as_text(style.get("aspect")) or as_text(target.get("aspect"))
    if aspect:
        if aspect not in KNOWN_ASPECTS:
            warnings.append(f"aspect '{aspect}' is not in {sorted(KNOWN_ASPECTS)}")
        if as_text(style.get("aspect")) and as_text(target.get("aspect")) and style.get("aspect") != target.get("aspect"):
            warnings.append(
                f"style.aspect {style.get('aspect')} differs from target.aspect {target.get('aspect')}"
            )
    vertical = aspect in ("9:16", "4:5")

    beats = data.get("beats") or []
    beat_ids: dict[str, dict] = {}
    beat_total = 0.0
    for index, beat in enumerate(beats, start=1):
        if not isinstance(beat, dict):
            errors.append(f"beat #{index}: must be an object")
            continue
        beat_id = as_text(beat.get("id"))
        if not beat_id:
            errors.append(f"beat #{index}: missing id")
            continue
        if beat_id in beat_ids:
            errors.append(f"duplicate beat id '{beat_id}'")
        beat_ids[beat_id] = beat
        try:
            length = float(beat.get("duration_s") or 0)
        except (TypeError, ValueError):
            errors.append(f"beat {beat_id}: duration_s must be a number")
            length = 0.0
        beat_total += length
        tension = beat.get("tension")
        if not isinstance(tension, (int, float)) or not 0 <= float(tension) <= 10:
            warnings.append(f"beat {beat_id}: tension should be a number 0-10")
        if not as_text(beat.get("goal")):
            warnings.append(f"beat {beat_id}: no goal — a beat without a job is filler")
        name = as_text(beat.get("name")).lower()
        if name and name not in BEAT_NAMES:
            warnings.append(f"beat {beat_id}: '{name}' is not in the beat vocabulary (see beats.md)")

    shots = data["shots"]
    ids: list[str] = []
    mechanism_use: list[str] = []
    for index, shot in enumerate(shots, start=1):
        if not isinstance(shot, dict):
            errors.append(f"shot #{index}: must be an object")
            continue
        label = as_text(shot.get("id")) or f"#{index}"

        for name, path in REQUIRED_PATHS:
            if not as_text(get(shot, path)):
                errors.append(f"shot {label}: missing required field '{name}'")

        shot_id = as_text(shot.get("id"))
        if shot_id:
            if shot_id in ids:
                errors.append(f"duplicate shot id '{shot_id}'")
            ids.append(shot_id)

        try:
            duration = float(shot.get("duration_s") or 0)
        except (TypeError, ValueError):
            errors.append(f"shot {label}: duration_s must be a number")
            duration = 0.0
        total += duration
        if duration <= 0:
            errors.append(f"shot {label}: duration must be positive")
        elif duration < 1.2:
            warnings.append(f"shot {label}: {duration:.1f}s is below the 1.2s reading time")

        beat_id = as_text(shot.get("beat_id"))
        if beats:
            if not beat_id:
                errors.append(f"shot {label}: beat_id is required when the sequence declares beats")
            elif beat_id not in beat_ids:
                errors.append(f"shot {label}: unknown beat_id '{beat_id}'")

        mechanisms = as_text(shot.get("mechanism")).upper().split("+")
        mechanisms = [item.strip() for item in mechanisms if item.strip()]
        if mechanisms:
            if len(mechanisms) > 2:
                warnings.append(f"shot {label}: {len(mechanisms)} mechanisms; one spine + one modifier at most")
            for mech in mechanisms:
                if mech not in known_mechanisms:
                    errors.append(
                        f"shot {label}: unknown mechanism '{mech}' (see references/templates.md)"
                    )
                else:
                    mechanism_use.append(mech)
        elif known_mechanisms:
            warnings.append(f"shot {label}: no mechanism — start from templates.md")

        framing = shot.get("framing") or {}
        options = framing.get("options")
        if options is not None:
            if not isinstance(options, list) or len(options) < 2:
                warnings.append(f"shot {label}: framing.options needs at least two plans to compare")
            else:
                names = []
                for option in options:
                    if not isinstance(option, dict):
                        errors.append(f"shot {label}: framing option must be an object")
                        continue
                    names.append(as_text(option.get("name")))
                    missing = [k for k in ("start", "turn", "end") if not as_text(option.get(k))]
                    if missing:
                        errors.append(
                            f"shot {label}: framing option {as_text(option.get('name')) or '?'} "
                            f"missing {', '.join(missing)}"
                        )
                chosen = as_text(framing.get("chosen"))
                if not chosen:
                    warnings.append(f"shot {label}: framing.chosen is not set")
                elif names and chosen not in names:
                    errors.append(f"shot {label}: framing.chosen '{chosen}' is not one of {names}")

        if not as_text(get(shot, ("camera", "turn_frame"))) and len(shots) > 1:
            warnings.append(f"shot {label}: no camera.turn_frame — the moment information changes")

        emotion = shot.get("emotion") or {}
        dials = emotion.get("dials") or {}
        if not dials:
            warnings.append(f"shot {label}: no emotion dials set")
        for key, value in dials.items():
            if key not in DIAL_KEYS:
                warnings.append(f"shot {label}: unknown dial '{key}'")
            if not isinstance(value, (int, float)) or not 0 <= float(value) <= 10:
                errors.append(f"shot {label}: dial '{key}' must be a number 0-10")

        action = shot.get("action") or {}
        cues = action.get("cues")
        if cues is not None and not isinstance(cues, list):
            errors.append(f"shot {label}: action.cues must be a list")
        elif isinstance(cues, list) and len(cues) > 4:
            warnings.append(f"shot {label}: {len(cues)} performance cues; 2-4 read better")

        move = as_text(get(shot, ("camera", "move"))).lower()
        if move and move != "static" and not as_text(get(shot, ("camera", "motivation"))):
            warnings.append(f"shot {label}: camera move '{move}' has no motivation")

        if len(shots) > 1 and not shot.get("continuity"):
            warnings.append(f"shot {label}: no continuity anchors in a multi-shot sequence")

        for ref in shot.get("references") or []:
            if not isinstance(ref, dict):
                errors.append(f"shot {label}: references must be objects")
                continue
            missing = [k for k in ("label", "role", "defines") if not as_text(ref.get(k))]
            if missing:
                warnings.append(
                    f"shot {label}: reference missing {', '.join(missing)} "
                    "(label, role and what it defines are the handoff contract)"
                )

        panel = shot.get("storyboard")
        if panel is not None:
            if not isinstance(panel, dict):
                errors.append(f"shot {label}: storyboard must be an object")
            else:
                if not as_text(panel.get("panel")):
                    errors.append(f"shot {label}: storyboard.panel is empty")
                if not as_text(panel.get("annotation")):
                    warnings.append(f"shot {label}: storyboard.annotation missing")
                if move and move != "static" and not panel.get("arrows"):
                    warnings.append(
                        f"shot {label}: camera moves but the panel has no arrow"
                    )
                overlays = panel.get("overlays")
                if overlays is not None:
                    if not isinstance(overlays, list):
                        errors.append(f"shot {label}: storyboard.overlays must be a list")
                    elif len(overlays) > 4:
                        warnings.append(f"shot {label}: {len(overlays)} overlays; 4 read better")
                    else:
                        for item in overlays:
                            if not isinstance(item, dict):
                                errors.append(f"shot {label}: overlay must be an object")
                                continue
                            kind = as_text(item.get("type")).lower()
                            if kind not in OVERLAY_TYPES:
                                errors.append(
                                    f"shot {label}: overlay type '{kind}' not in {sorted(OVERLAY_TYPES)}"
                                )
                            elif kind in ("arrow", "sight"):
                                if not (valid_point(item.get("from")) and valid_point(item.get("to"))):
                                    errors.append(
                                        f"shot {label}: {kind} needs 'from' and 'to' as [x, y] in 0-1"
                                    )
                            elif not valid_point(item.get("at")):
                                errors.append(
                                    f"shot {label}: {kind} needs 'at' as [x, y] in 0-1"
                                )

        if duration > 6 and not shot.get("beats"):
            warnings.append(
                f"shot {label}: a shot over 6s needs internal beat windows"
            )

    declared = target.get("duration_s")
    if declared is not None:
        try:
            declared_f = float(declared)
            if abs(declared_f - total) > 0.05:
                warnings.append(f"declared duration {declared_f:.1f}s but shots total {total:.1f}s")
        except (TypeError, ValueError):
            warnings.append("target.duration_s is not a number")

    if total and not (lo <= total <= hi):
        errors.append(f"total {total:.1f}s is outside the {model} single-pass range {lo:g}-{hi:g}s")

    if beats and abs(beat_total - total) > 0.05:
        warnings.append(f"beats total {beat_total:.1f}s but shots total {total:.1f}s")

    tensions = [
        (float(beat.get("tension") or 0), as_text(beat.get("id")))
        for beat in beats
        if isinstance(beat.get("tension"), (int, float))
    ]
    if len(tensions) > 2 and total:
        peak_value, peak_id = max(tensions)
        cursor = 0.0
        peak_at = 0.0
        for beat in beats:
            length = float(beat.get("duration_s") or 0)
            if as_text(beat.get("id")) == peak_id:
                peak_at = cursor + length / 2
                break
            cursor += length
        position = peak_at / total if total else 0
        if not 0.6 <= position <= 0.9:
            warnings.append(
                f"tension peak ({peak_id}) sits at {position:.0%} of the runtime; "
                "aim for 70-85% so there is room to land"
            )

    max_shots = {"h3": 6, "minimax-h3": 6}.get(model)
    if max_shots and len(shots) > max_shots:
        warnings.append(f"{len(shots)} shots for {model}: it tends to drop shots past {max_shots}")

    previous = None
    for shot in shots:
        label = as_text(shot.get("id")) or "?"
        staging = shot.get("staging") or {}
        direction = as_text(staging.get("screen_direction")).lower() or "none"
        if direction not in DIRECTIONS:
            warnings.append(f"shot {label}: unknown screen_direction '{direction}'")
        if previous and previous != "none" and direction != "none" and direction != previous:
            if not as_text(staging.get("reversal_reason")):
                warnings.append(
                    f"shot {label}: screen direction flips {previous} -> {direction} without reversal_reason"
                )
        if direction != "none":
            previous = direction

    contradictions = sum(1 for shot in shots if as_text((shot.get("emotion") or {}).get("contradiction")))
    if contradictions > 1:
        warnings.append(f"{contradictions} shots declare a contradiction; one per sequence reads as intent")

    for mech, count in Counter(mechanism_use).most_common():
        if count > 2:
            warnings.append(f"mechanism {mech} used {count} times; repetition dilutes it")

    for prev, shot in zip(shots, shots[1:]):
        if not isinstance(prev, dict) or not isinstance(shot, dict):
            continue
        checks = cut_checks(prev, shot, beat_ids)
        score = sum(weight for key, weight in MURCH_WEIGHTS if checks[key])
        if score < 70:
            missing = [MURCH_LABELS[key] for key, _ in MURCH_WEIGHTS if not checks[key]]
            warnings.append(
                f"cut {as_text(prev.get('id'))} -> {as_text(shot.get('id'))}: "
                f"readiness {score}/100 — undeclared: {', '.join(missing)}"
            )

    if vertical:
        wide = [
            as_text(shot.get("id"))
            for shot in shots
            if as_text(get(shot, ("framing", "size"))).upper() in ("WS", "EWS", "FS")
        ]
        if wide:
            warnings.append(
                f"vertical {aspect}: wide sizes on {', '.join(wide)} — stack or crop instead"
            )

    if beats:
        referenced = {as_text(shot.get("beat_id")) for shot in shots if isinstance(shot, dict)}
        orphans = [beat_id for beat_id in beat_ids if beat_id not in referenced]
        if orphans:
            warnings.append(
                f"beats with no shot: {', '.join(orphans)} — either give each beat a shot or drop it"
            )

    if len(shots) >= 3:
        has_panel = any(
            isinstance(shot.get("storyboard"), dict) for shot in shots if isinstance(shot, dict)
        )
        waived = as_text(data.get("previs_waived"))
        if not has_panel and not waived:
            warnings.append(
                "previs gate: 3+ shots without storyboard specs — storyboard before any video "
                "handoff, or set previs_waived with a reason"
            )

    stats = duration_stats(data)
    if stats["count"] >= 4 and stats["mean"]:
        declared = as_text((data.get("rhythm") or {}).get("shape")).lower()
        if stats["spread"] < 0.3 and declared != "ritual":
            warnings.append(
                f"near-uniform durations (spread {stats['spread']:.0%}, mean {stats['mean']:.1f}s) — "
                "set each duration from its beat function, or declare rhythm.shape=ritual"
            )
        longest_index = max(range(stats["count"]), key=lambda i: stats["durations"][i])
        longest_beat = beat_ids.get(as_text(shots[longest_index].get("beat_id"))) or {}
        if as_text(longest_beat.get("name")).lower() in ("burst", "impact"):
            warnings.append(
                f"{as_text(shots[longest_index].get('id'))} is the longest shot but its beat is "
                f"{as_text(longest_beat.get('name'))}; give the length to a charge or a landing"
            )

    return errors, warnings


def shot_label(framing: dict) -> str:
    size = as_text(framing.get("size"))
    angle = as_text(framing.get("angle"))
    for word in (" shot", " angle"):
        if angle.lower().endswith(word):
            angle = angle[: -len(word)]
    return f"{size} shot, {angle} angle" if angle else f"{size} shot"


def camera_brief(camera: dict) -> str:
    move = as_text(camera.get("move"))
    speed = as_text(camera.get("speed")).lower()
    if speed and speed not in ("none", "n/a"):
        move += f", {speed}"
    return move


def beat_name(beats: dict[str, dict], beat_id: str) -> str:
    beat = beats.get(beat_id) or {}
    return as_text(beat.get("name")) or beat_id


def mechanism_label(shot: dict, mechanisms: dict[str, str] | None = None) -> str:
    raw = as_text(shot.get("mechanism")).upper().replace(" ", "")
    if not raw:
        return "—"
    mechanisms = mechanisms or {}
    parts = [part for part in raw.split("+") if part]
    return " + ".join(f"{part} {mechanisms.get(part, '')}".strip() for part in parts)


def render_md(data: dict) -> str:
    shots = data["shots"]
    intent = data.get("intent") or {}
    beats = {as_text(b.get("id")): b for b in data.get("beats") or [] if isinstance(b, dict)}
    mechanisms = load_mechanisms()
    lines = [
        f"# {as_text(data.get('title')) or 'Shot list'}",
        "",
        f"**Logline**: {as_text(intent.get('logline'))}",
        f"**Turn**: {as_text(intent.get('turn'))}",
        f"**Viewer knows**: {as_text(intent.get('audience_knows'))}",
        "",
        f"Total {total_duration(data):.1f}s across {len(shots)} shots.",
        "",
        "| Shot | Dur | Beat | Mechanism | Framing | Camera | Action | Cut out |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for shot in shots:
        framing = shot.get("framing") or {}
        camera = shot.get("camera") or {}
        action = shot.get("action") or {}
        cut = shot.get("transition_out") or {}
        frame = f"{as_text(framing.get('size'))} / {as_text(framing.get('angle'))}".strip(" /")
        lens = framing.get("lens_mm")
        if isinstance(lens, (int, float)):
            frame += f" / {lens:g}mm"
        lines.append(
            "| {} | {:.1f}s | {} | {} | {} | {} | {} | {} |".format(
                as_text(shot.get("id")),
                float(shot.get("duration_s") or 0),
                beat_name(beats, as_text(shot.get("beat_id"))),
                mechanism_label(shot, mechanisms),
                frame,
                camera_brief(camera),
                as_text(action.get("primary")),
                as_text(cut.get("type")),
            )
        )
    return "\n".join(lines) + "\n"


def render_beats(data: dict) -> str:
    beats = data.get("beats") or []
    if not beats:
        return "No beats declared. A sequence without beats has no tension curve.\n"
    total = total_duration(data)
    out = [
        f"# Beat sheet — {as_text(data.get('title')) or 'untitled'} ({total:.1f}s)",
        "",
        "| Beat | Name | Dur | Tension | Goal | Knowledge change |",
        "|---|---|---|---|---|---|",
    ]
    for beat in beats:
        out.append(
            "| {} | {} | {:.1f}s | {} | {} | {} |".format(
                as_text(beat.get("id")),
                as_text(beat.get("name")),
                float(beat.get("duration_s") or 0),
                beat.get("tension", ""),
                as_text(beat.get("goal")),
                as_text(beat.get("knowledge_change")),
            )
        )
    shots_by_beat: dict[str, list[str]] = {}
    for shot in data["shots"]:
        shots_by_beat.setdefault(as_text(shot.get("beat_id")), []).append(as_text(shot.get("id")))
    out += ["", "Shots per beat: " + "; ".join(f"{k}: {', '.join(v)}" for k, v in shots_by_beat.items() if k)]
    return "\n".join(out) + "\n"


def render_framing(data: dict) -> str:
    """Show the viewing plans side by side, with the chosen one marked."""
    out = [f"FRAMING DECISIONS — {as_text(data.get('title')) or 'untitled'}", ""]
    any_plan = False
    for shot in data["shots"]:
        framing = shot.get("framing") or {}
        options = framing.get("options") or []
        if not options:
            continue
        any_plan = True
        chosen = as_text(framing.get("chosen"))
        out.append(
            f"[{as_text(shot.get('id'))}] {shot_label(framing)} · "
            f"{mechanism_label(shot, load_mechanisms())}"
        )
        out.append(f"  Purpose: {as_text(shot.get('purpose'))}")
        for option in options:
            name = as_text(option.get("name"))
            mark = "→" if name == chosen else " "
            out.append(f" {mark} {name}: {as_text(option.get('tradeoff'))}")
            out.append(f"     start: {as_text(option.get('start'))}")
            out.append(f"     turn:  {as_text(option.get('turn'))}")
            out.append(f"     end:   {as_text(option.get('end'))}")
        camera = shot.get("camera") or {}
        if as_text(camera.get("turn_frame")):
            out.append(f"  Turn frame (chosen): {as_text(camera.get('turn_frame'))}")
        out.append("")
    if not any_plan:
        return (
            "No framing options declared. For any beat whose viewing choice is still open, "
            "compare 2-3 plans (start / turn / end) before choosing mechanisms.\n"
        )
    out.append("→ marks the chosen plan. Mechanisms must be able to deliver it.")
    return "\n".join(out) + "\n"


MURCH_WEIGHTS = [
    ("emotion", 51),
    ("story", 23),
    ("rhythm", 10),
    ("eye_trace", 7),
    ("screen_plane", 5),
    ("space", 4),
]

MURCH_LABELS = {
    "emotion": "emotion",
    "story": "story",
    "rhythm": "rhythm",
    "eye_trace": "eye-trace",
    "screen_plane": "screen plane",
    "space": "3D space",
}

RHYTHM_SHAPES = ("hold-snap-hold", "accelerate", "decelerate", "wave", "ritual")


def duration_stats(data: dict) -> dict:
    durations = [float(shot.get("duration_s") or 0) for shot in data["shots"]]
    count = len(durations)
    total = sum(durations)
    mean = total / count if count else 0.0
    shortest = min(durations) if durations else 0.0
    longest = max(durations) if durations else 0.0
    spread = (longest - shortest) / mean if mean else 0.0
    return {
        "durations": durations,
        "count": count,
        "total": total,
        "mean": mean,
        "min": shortest,
        "max": longest,
        "spread": spread,
        "max_ratio": longest / mean if mean else 0.0,
        "min_ratio": shortest / mean if mean else 0.0,
    }


def detect_shape(data: dict) -> str:
    stats = duration_stats(data)
    durations = stats["durations"]
    if stats["count"] < 3 or not stats["mean"]:
        return "single"
    declared = as_text((data.get("rhythm") or {}).get("shape")).lower()
    if declared in RHYTHM_SHAPES:
        return declared
    if stats["spread"] < 0.25:
        return "ritual"
    first, last = durations[0], durations[-1]
    half = max(1, stats["count"] // 2)
    head = sum(durations[:half]) / half
    tail = sum(durations[half:]) / (stats["count"] - half)
    if first > stats["mean"] * 1.15 and last > stats["mean"] * 1.15 and min(durations[1:-1] or durations) < stats["mean"] * 0.9:
        return "hold-snap-hold"
    if head > tail * 1.15:
        return "accelerate"
    if tail > head * 1.15:
        return "decelerate"
    return "wave"


def rhythm_bar(value: float, maximum: float, width: int = 24) -> str:
    if maximum <= 0:
        return ""
    filled = max(1, int(round(width * value / maximum)))
    return "█" * filled + "·" * (width - filled)


def cut_checks(prev: dict, shot: dict, beats: dict[str, dict]) -> dict[str, bool]:
    """Which of the Rule of Six the design already specifies for this cut."""
    prev_emotion = prev.get("emotion") or {}
    emotion = shot.get("emotion") or {}
    prev_framing = prev.get("framing") or {}
    framing = shot.get("framing") or {}
    prev_composition = prev.get("composition") or {}
    composition = shot.get("composition") or {}
    prev_staging = prev.get("staging") or {}
    staging = shot.get("staging") or {}
    beat = beats.get(as_text(shot.get("beat_id"))) or {}
    duration = float(shot.get("duration_s") or 0)
    direction = as_text(staging.get("screen_direction")).lower()
    prev_direction = as_text(prev_staging.get("screen_direction")).lower()
    return {
        "emotion": bool(as_text(prev_emotion.get("target")) and as_text(emotion.get("target"))),
        "story": bool(as_text(shot.get("purpose")) and as_text(beat.get("knowledge_change"))),
        "rhythm": 1.2 <= duration <= 6.0,
        "eye_trace": bool(
            as_text(prev_composition.get("focus"))
            and as_text(composition.get("focus"))
            and as_text((prev.get("transition_out") or {}).get("matches"))
        ),
        "screen_plane": bool(as_text(prev_framing.get("size")) and as_text(framing.get("size"))),
        "space": bool(
            (direction and direction != "none")
            or (prev_direction and prev_direction != "none")
            or as_text(composition.get("negative_space"))
        ),
    }


def render_cuts(data: dict) -> str:
    """Per-cut readiness against the Rule of Six. Readiness, not quality."""
    shots = data["shots"]
    if len(shots) < 2:
        return "Single shot: no cuts to audit. Use the shot checks in qc-repair.md.\n"
    beats = {as_text(b.get("id")): b for b in data.get("beats") or [] if isinstance(b, dict)}
    out = [
        f"CUT READINESS — {as_text(data.get('title')) or 'untitled'}",
        "Rule of Six order: emotion 51 · story 23 · rhythm 10 · eye-trace 7 · screen plane 5 · space 4.",
        "This measures what the design specifies, not whether the cut is good.",
        "",
    ]
    for prev, shot in zip(shots, shots[1:]):
        checks = cut_checks(prev, shot, beats)
        score = sum(weight for key, weight in MURCH_WEIGHTS if checks[key])
        missing = [f"{MURCH_LABELS[key]} ({weight})" for key, weight in MURCH_WEIGHTS if not checks[key]]
        marks = "  ".join(
            f"{'✓' if checks[key] else '✗'} {MURCH_LABELS[key]}" for key, _ in MURCH_WEIGHTS
        )
        out.append(
            f"{as_text(prev.get('id'))} → {as_text(shot.get('id'))}   {score} / 100"
        )
        out.append(f"   {marks}")
        if missing:
            out.append(f"   missing: {', '.join(missing)}")
        out.append("")
    return "\n".join(out) + "\n"


def render_sheet(data: dict) -> str:
    """Five-column production sheet: time | shot | camera | picture & action | sound."""
    shots = data["shots"]
    beats = {as_text(b.get("id")): b for b in data.get("beats") or [] if isinstance(b, dict)}
    mechanisms = load_mechanisms()
    lines = [
        f"# {as_text(data.get('title')) or 'Shot sheet'}",
        "",
        "| Time 时间 | Shot 景别·机位 | Camera 摄影机 | Picture & action 画面与动作 | Dialogue & sound 台词·声音 |",
        "|---|---|---|---|---|",
    ]
    cursor = 0.0
    for shot in shots:
        duration = float(shot.get("duration_s") or 0)
        start, end = cursor, cursor + duration
        framing = shot.get("framing") or {}
        camera = shot.get("camera") or {}
        composition = shot.get("composition") or {}
        action = shot.get("action") or {}
        sound = shot.get("sound") or {}
        beat = beats.get(as_text(shot.get("beat_id"))) or {}

        shot_cell = f"{as_text(framing.get('size'))} · {as_text(framing.get('angle'))}"
        lens = framing.get("lens_mm")
        if isinstance(lens, (int, float)):
            shot_cell += f" · {lens:g}mm"
        mech = mechanism_label(shot, mechanisms)
        if mech != "—":
            shot_cell += f" · {mech}"

        camera_cell = camera_brief(camera)
        if as_text(camera.get("motivation")):
            camera_cell += f" — {as_text(camera.get('motivation'))}"

        picture_bits = []
        if as_text(composition.get("value_masses")):
            picture_bits.append(as_text(composition.get("value_masses")))
        if as_text(action.get("primary")):
            picture_bits.append(as_text(action.get("primary")))
        cues = action.get("cues") or []
        if cues:
            picture_bits.append("(" + "; ".join(as_text(cue) for cue in cues) + ")")
        if as_text(beat.get("name")):
            picture_bits.append(f"[{as_text(beat.get('name'))}]")

        sound_bits = [
            bit
            for bit in (
                as_text(sound.get("dialogue")),
                as_text(sound.get("diegetic")),
                as_text(sound.get("music")),
            )
            if bit and bit.lower() not in ("none", "n/a")
        ]

        lines.append(
            "| {:.1f}–{:.1f}s | {} | {} | {} | {} |".format(
                start,
                end,
                shot_cell,
                camera_cell.replace("|", "/"),
                "；".join(picture_bits).replace("|", "/"),
                "；".join(sound_bits).replace("|", "/") or "—",
            )
        )
        cursor = end
    return "\n".join(lines) + "\n"


def render_timeline(data: dict, width: int = 72) -> str:
    """One-glance timing strip: shot cells sized by duration, beats underneath."""
    shots = data["shots"]
    beats = {as_text(b.get("id")): b for b in data.get("beats") or [] if isinstance(b, dict)}
    total = total_duration(data)
    if total <= 0:
        return "no duration declared\n"
    scale = max(1.0, (width - len(shots) - 1) / total)
    cells = []
    for shot in shots:
        duration = float(shot.get("duration_s") or 0)
        cell = max(4, int(round(duration * scale)))
        beat = beats.get(as_text(shot.get("beat_id"))) or {}
        cells.append(
            (
                as_text(shot.get("id")) or "?",
                as_text(beat.get("name")) or "—",
                duration,
                cell,
            )
        )
    line1 = "|" + "|".join(shot_id.ljust(cell)[:cell] for shot_id, _, _, cell in cells) + "|"
    line2 = "|" + "|".join(name.ljust(cell)[:cell] for _, name, _, cell in cells) + "|"
    line3 = "|" + "|".join(f"{duration:.1f}s".ljust(cell)[:cell] for _, _, duration, cell in cells) + "|"
    ruler = f"0.0s{' ' * max(0, width - 8)}{total:.1f}s"
    return "\n".join([f"TIMELINE — {as_text(data.get('title')) or 'untitled'}", ruler, line1, line2, line3]) + "\n"


def render_csv(data: dict) -> str:
    """Flat export for spreadsheets and production tracking."""
    shots = data["shots"]
    beats = {as_text(b.get("id")): b for b in data.get("beats") or [] if isinstance(b, dict)}
    mechanisms = load_mechanisms()
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        [
            "shot", "start_s", "end_s", "duration_s", "beat", "mechanism",
            "size", "angle", "camera", "action", "dialogue", "sound",
        ]
    )
    cursor = 0.0
    for shot in shots:
        duration = float(shot.get("duration_s") or 0)
        framing = shot.get("framing") or {}
        camera = shot.get("camera") or {}
        action = shot.get("action") or {}
        sound = shot.get("sound") or {}
        beat = beats.get(as_text(shot.get("beat_id"))) or {}
        writer.writerow(
            [
                as_text(shot.get("id")),
                f"{cursor:.2f}",
                f"{cursor + duration:.2f}",
                f"{duration:.2f}",
                as_text(beat.get("name")),
                mechanism_label(shot, mechanisms),
                as_text(framing.get("size")),
                as_text(framing.get("angle")),
                camera_brief(camera),
                as_text(action.get("primary")),
                as_text(sound.get("dialogue")),
                as_text(sound.get("diegetic")),
            ]
        )
        cursor += duration
    return buffer.getvalue()


def build_scaffold(title: str, duration: float, aspect: str, model: str, count: int) -> dict:
    """A valid, deliberately empty shot list to fill in.

    Durations are NOT divided evenly: the scaffold opens with a hold, contracts
    through the middle and gives the last shot room to land. Overwrite them once
    the beat functions are known.
    """
    count = max(1, count)
    names = ["establish", "reveal", "turn", "landing", "charge", "aftermath"]
    mechanisms = ["M01", "M18", "M21", "M05", "M32", "M10"]
    ratios = [0.30, 0.22, 0.14, 0.12, 0.10, 0.12][:count]
    scale = sum(ratios)
    durations = [duration * ratio / scale for ratio in ratios]
    durations = [round(value, 2) for value in durations]
    durations[-1] = round(duration - sum(durations[:-1]), 2)
    beats = []
    shots = []
    if count == 1:
        tensions = [3]
    elif count == 2:
        tensions = [3, 6]
    elif count == 3:
        tensions = [3, 7, 5]
    else:
        tensions = [3, 5] + [6] * (count - 4) + [9, 6]
    for index in range(count):
        beat_id = f"B{index + 1}"
        shot_id = f"S{index + 1:02d}"
        name = names[index % len(names)]
        length = durations[index]
        beats.append(
            {
                "id": beat_id,
                "name": name,
                "goal": "TODO: what this beat must achieve",
                "duration_s": length,
                "tension": tensions[index],
                "knowledge_change": "TODO: what the viewer learns",
            }
        )
        shots.append(
            {
                "id": shot_id,
                "beat_id": beat_id,
                "mechanism": mechanisms[index % len(mechanisms)],
                "duration_s": length,
                "purpose": "TODO: what this shot must say in one clause",
                "emotion": {
                    "target": "TODO",
                    "dials": {"proximity": 5, "power": 5, "pressure": 5, "stability": 5, "value": 5, "time": 5},
                },
                "framing": {"size": "MS", "angle": "eye-level", "lens_mm": 40},
                "composition": {"value_masses": "TODO", "focus": "TODO"},
                "staging": {"subjects": [], "screen_direction": "none"},
                "camera": {
                    "move": "static",
                    "amplitude": "none",
                    "speed": "none",
                    "motivation": "TODO",
                    "start_frame": "TODO",
                    "turn_frame": "TODO: the picture at the moment information changes",
                    "end_frame": "TODO",
                },
                "light": {"key": "TODO", "ratio": "4:1", "palette": "TODO"},
                "action": {"primary": "TODO: one readable action", "cues": [], "subtext": "TODO"},
                "sound": {"diegetic": "TODO", "dialogue": "none", "music": "none"},
                "transition_out": {"type": "cut", "matches": "TODO"},
                "continuity": ["TODO"],
                "bans": ["no on-screen text"],
                "references": [],
            }
        )
    return {
        "title": title,
        "intent": {
            "logline": "TODO: subject + place + event",
            "turn": "TODO: from X to Y",
            "audience_knows": "TODO",
        },
        "target": {"model": model, "duration_s": duration, "aspect": aspect, "mode": "ref2va"},
        "style": {"look": "monochrome storyboard for previz", "palette": "paper white, mid grey, black", "aspect": aspect},
        "beats": beats,
        "shots": shots,
    }


def shot_load(shot: dict) -> tuple[int, bool]:
    """Written cue/window density. Counts what is written, not what is meant."""
    cues = len(shot.get("action", {}).get("cues") or [])
    windows = len(shot.get("beats") or [])
    continuity = len(shot.get("continuity") or [])
    duration = float(shot.get("duration_s") or 0)
    load = cues + windows + continuity
    dense = (windows >= 3 and duration < 4.0) or (cues >= 6 and duration < 2.0)
    return load, dense


def render_load(data: dict) -> str:
    """Cue/window density: a proxy for overload, not a judgement of the shot."""
    out = [
        f"CUE DENSITY — {as_text(data.get('title')) or 'untitled'}",
        "Counts what the card declares. It cannot see how many story facts a shot carries — "
        "check that by hand in qc-repair.md (information load).",
        "",
        "| Shot | Dur | Cues | Windows | Continuity | Total | Verdict |",
        "|---|---|---|---|---|---|---|",
    ]
    dense_ids: list[str] = []
    for shot in data["shots"]:
        duration = float(shot.get("duration_s") or 0)
        cues = len((shot.get("action") or {}).get("cues") or [])
        windows = len(shot.get("beats") or [])
        continuity = len(shot.get("continuity") or [])
        load, dense = shot_load(shot)
        if dense:
            dense_ids.append(as_text(shot.get("id")))
        out.append(
            f"| {as_text(shot.get('id'))} | {duration:.1f}s | {cues} | {windows} | "
            f"{continuity} | {load} | {'dense' if dense else 'ok'} |"
        )
    out.append("")
    if dense_ids:
        out.append(f"Dense shots: {', '.join(dense_ids)} — consider splitting or dropping cues.")
    else:
        out.append("No shot is over-loaded by this heuristic.")
    return "\n".join(out) + "\n"


def render_rhythm(data: dict) -> str:
    """Duration shape: bars, spread, and the detected rhythm pattern."""
    stats = duration_stats(data)
    beats = {as_text(b.get("id")): b for b in data.get("beats") or [] if isinstance(b, dict)}
    shape = detect_shape(data)
    out = [
        f"RHYTHM — {as_text(data.get('title')) or 'untitled'}",
        f"shots {stats['count']} · total {stats['total']:.1f}s · mean {stats['mean']:.2f}s · "
        f"max {stats['max']:.1f}s · min {stats['min']:.1f}s · spread {stats['spread']:.0%} · "
        f"shape: {shape}",
        "",
        "| Shot | Beat | Dur | Share | Bar |",
        "|---|---|---|---|---|",
    ]
    maximum = stats["max"] or 1.0
    for shot in data["shots"]:
        duration = float(shot.get("duration_s") or 0)
        beat = beats.get(as_text(shot.get("beat_id"))) or {}
        share = duration / stats["total"] if stats["total"] else 0.0
        out.append(
            f"| {as_text(shot.get('id'))} | {as_text(beat.get('name')) or '—'} | {duration:.1f}s | "
            f"{share:.0%} | {rhythm_bar(duration, maximum)} |"
        )
    declared = as_text((data.get("rhythm") or {}).get("shape"))
    if declared:
        out += ["", f"Declared shape: {declared} — {as_text((data.get('rhythm') or {}).get('note')) or 'no note'}"]
    if stats["count"] >= 4:
        if stats["spread"] < 0.3 and declared.lower() != "ritual":
            out += ["", "Near-uniform: no shot is being held and none is being rushed. Vary by beat function."]
        elif stats["max_ratio"] < 1.35:
            out += ["", "Weak contrast: the longest shot is under 1.35× the mean. Consider one real hold."]
        else:
            out += ["", "Long/short contrast present. Check that the longest shot is a charge or a landing."]
    return "\n".join(out) + "\n"


def render_storyboard(data: dict) -> str:
    """Per-panel drawing brief. The image skill turns each block into a request."""
    style = data.get("style") or {}
    out = [
        f"STORYBOARD BRIEF — {as_text(data.get('title')) or 'untitled'}",
        f"Format: {as_text(style.get('aspect')) or as_text((data.get('target') or {}).get('aspect')) or '16:9'}, "
        f"{as_text(style.get('look')) or 'monochrome storyboard'}, values: "
        f"{as_text(style.get('palette')) or 'paper white / mid grey / black'}",
        "",
    ]
    for shot in data["shots"]:
        panel = shot.get("storyboard")
        if not isinstance(panel, dict):
            out.append(f"[{as_text(shot.get('id'))}] no storyboard block — add one before drawing")
            out.append("")
            continue
        framing = shot.get("framing") or {}
        composition = shot.get("composition") or {}
        action = shot.get("action") or {}
        staging = shot.get("staging") or {}
        out.append(
            f"[{as_text(shot.get('id'))}] {as_text(panel.get('annotation'))} "
            f"({as_text(panel.get('level')) or 'rough'})"
        )
        out.append(f"  Frame: {shot_label(framing)}")
        if as_text(panel.get("panel")):
            out.append(f"  Panel: {as_text(panel.get('panel'))}")
        if as_text(composition.get("value_masses")):
            out.append(f"  Values: {as_text(composition.get('value_masses'))}")
        if as_text(action.get("primary")):
            out.append(f"  Action: {as_text(action.get('primary'))}")
        direction = as_text(staging.get("screen_direction"))
        if direction:
            out.append(f"  Screen direction: {direction}")
        arrows = panel.get("arrows") or []
        if arrows:
            out.append(f"  Arrows: {'; '.join(as_text(a) for a in arrows)}")
        out.append("")
    out.append("Draw panels in shot order; keep the aspect equal to the final video.")
    return "\n".join(out) + "\n"


def render_brief(data: dict) -> str:
    """Model-neutral handoff brief: what the prompt writer needs, no prompt syntax."""
    shots = data["shots"]
    intent = data.get("intent") or {}
    target = data.get("target") or {}
    beats = {as_text(b.get("id")): b for b in data.get("beats") or [] if isinstance(b, dict)}
    out = [
        f"DESIGN BRIEF — {as_text(data.get('title')) or 'untitled'}",
        "",
        f"Logline: {as_text(intent.get('logline'))}",
        f"Turn: {as_text(intent.get('turn'))}",
        f"Viewer knows: {as_text(intent.get('audience_knows'))}",
        f"Target: {as_text(target.get('model')) or 'unspecified'}, "
        f"{total_duration(data):.1f}s, {as_text(target.get('aspect')) or 'unspecified aspect'}",
        "",
    ]

    if beats:
        out.append("BEATS:")
        for beat_id, beat in beats.items():
            out.append(
                f"- {beat_id} {as_text(beat.get('name'))} ({float(beat.get('duration_s') or 0):.1f}s, "
                f"tension {beat.get('tension', '')}): {as_text(beat.get('goal'))}"
            )
        out.append("")

    references: list[dict] = []
    for shot in shots:
        for ref in shot.get("references") or []:
            if isinstance(ref, dict) and ref not in references:
                references.append(ref)
    if references:
        out.append("REFERENCES:")
        for ref in references:
            line = f"- {as_text(ref.get('label'))} — role: {as_text(ref.get('role')) or 'unspecified'}"
            if as_text(ref.get("defines")):
                line += f"; defines: {as_text(ref.get('defines'))}"
            if as_text(ref.get("preserve")):
                line += f"; preserve: {as_text(ref.get('preserve'))}"
            if as_text(ref.get("exclude")):
                line += f"; exclude: {as_text(ref.get('exclude'))}"
            out.append(line)
        out.append("")

    cursor = 0.0
    for index, shot in enumerate(shots, start=1):
        duration = float(shot.get("duration_s") or 0)
        framing = shot.get("framing") or {}
        camera = shot.get("camera") or {}
        staging = shot.get("staging") or {}
        composition = shot.get("composition") or {}
        light = shot.get("light") or {}
        action = shot.get("action") or {}
        sound = shot.get("sound") or {}
        emotion = shot.get("emotion") or {}
        cut = shot.get("transition_out") or {}
        start, end = cursor, cursor + duration
        beat = beats.get(as_text(shot.get("beat_id"))) or {}

        out.append(
            f"[{as_text(shot.get('id')) or f'S{index:02d}'}] {start:.1f}-{end:.1f}s"
            + (f" · {as_text(beat.get('name'))}" if as_text(beat.get("name")) else "")
        )
        out.append(f"  Purpose: {as_text(shot.get('purpose'))}")
        if as_text(shot.get("mechanism")):
            out.append(f"  Mechanism: {mechanism_label(shot, load_mechanisms())}")
        if as_text(emotion.get("target")):
            dials = emotion.get("dials") or {}
            out.append(
                f"  Emotion: {as_text(emotion.get('target'))} "
                f"({', '.join(f'{k}={v}' for k, v in dials.items())})"
            )
            if as_text(emotion.get("contradiction")):
                out.append(f"  Contradiction: {as_text(emotion.get('contradiction'))}")
        out.append(f"  Framing: {shot_label(framing)}")
        chosen = as_text(framing.get("chosen"))
        if chosen:
            out.append(f"  Viewing plan (chosen): {chosen}")
            for option in framing.get("options") or []:
                if isinstance(option, dict) and as_text(option.get("name")) == chosen:
                    out.append(f"    start: {as_text(option.get('start'))}")
                    out.append(f"    turn:  {as_text(option.get('turn'))}")
                    out.append(f"    end:   {as_text(option.get('end'))}")
        if as_text(framing.get("notes")):
            out.append(f"  Framing notes: {as_text(framing.get('notes'))}")
        for key in ("value_masses", "focus", "negative_space"):
            if as_text(composition.get(key)):
                out.append(f"  Composition/{key}: {as_text(composition.get(key))}")
        for subject in staging.get("subjects") or []:
            if isinstance(subject, dict):
                out.append(
                    "  Subject: {name} — screen {screen}, facing {facing}, pose {pose}".format(
                        name=as_text(subject.get("name")),
                        screen=as_text(subject.get("screen")),
                        facing=as_text(subject.get("facing")),
                        pose=as_text(subject.get("pose")),
                    )
                )
        if as_text(staging.get("screen_direction")):
            out.append(f"  Screen direction: {as_text(staging.get('screen_direction'))}")
        if as_text(staging.get("reversal_reason")):
            out.append(f"  Reversal reason: {as_text(staging.get('reversal_reason'))}")
        out.append(
            f"  Camera: {camera_brief(camera)} — motive: {as_text(camera.get('motivation')) or 'n/a'}"
        )
        if as_text(camera.get("start_frame")) or as_text(camera.get("end_frame")):
            out.append(
                f"  Start frame: {as_text(camera.get('start_frame'))} | "
                f"End frame: {as_text(camera.get('end_frame'))}"
            )
        if as_text(camera.get("turn_frame")):
            out.append(f"  Turn frame: {as_text(camera.get('turn_frame'))}")
        if as_text(light.get("key")):
            out.append(
                f"  Light: key {as_text(light.get('key'))}, ratio {as_text(light.get('ratio'))}, "
                f"palette {as_text(light.get('palette'))}"
            )
        out.append(f"  Action: {as_text(action.get('primary'))}")
        cues = action.get("cues") or []
        if cues:
            out.append(f"  Cues: {'; '.join(as_text(cue) for cue in cues)}")
        if as_text(action.get("subtext")):
            out.append(f"  Subtext: {as_text(action.get('subtext'))}")
        for beat_window in shot.get("beats") or []:
            if isinstance(beat_window, dict):
                out.append(f"  Window {as_text(beat_window.get('window'))}: {as_text(beat_window.get('action'))}")
        sound_bits = [
            f"diegetic: {as_text(sound.get('diegetic'))}" if as_text(sound.get("diegetic")) else "",
            f"dialogue: {as_text(sound.get('dialogue'))}" if as_text(sound.get("dialogue")) else "",
            f"music: {as_text(sound.get('music'))}" if as_text(sound.get("music")) else "",
        ]
        if any(sound_bits):
            out.append("  Sound: " + "; ".join(bit for bit in sound_bits if bit))
        if shot.get("continuity"):
            out.append("  Continuity: " + "; ".join(as_text(item) for item in shot["continuity"]))
        if shot.get("bans"):
            out.append("  Bans: " + ", ".join(as_text(item) for item in shot["bans"]))
        out.append(f"  Cut out: {as_text(cut.get('type'))} — {as_text(cut.get('matches'))}")
        out.append("")
        cursor = end

    out.append("Deliver this brief to the target model's prompt skill; do not format the prompt here.")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["validate", "render", "mechanisms", "init"])
    ap.add_argument("path", nargs="?")
    ap.add_argument(
        "--format",
        default="md",
        choices=["md", "beats", "framing", "cuts", "sheet", "timeline", "load", "rhythm", "csv", "storyboard", "brief"],
    )
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--title", default="Untitled")
    ap.add_argument("--duration", type=float, default=10.0)
    ap.add_argument("--aspect", default="16:9")
    ap.add_argument("--model", default="h3")
    ap.add_argument("--shots", type=int, default=3)
    args = ap.parse_args()

    if args.command == "mechanisms":
        mechanisms = load_mechanisms()
        if not mechanisms:
            raise SystemExit("references/templates.md not found or has no mechanism rows")
        for mid, name in mechanisms.items():
            print(f"{mid}  {name}")
        return 0

    if args.command == "init":
        scaffold = build_scaffold(args.title, args.duration, args.aspect, args.model, args.shots)
        target = Path(args.path or f"{args.title.lower().replace(' ', '-')}.json")
        if target.exists():
            raise SystemExit(f"refusing to overwrite {target}")
        target.write_text(json.dumps(scaffold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"created: {target} ({args.shots} shots, {args.duration:.1f}s, {args.aspect})")
        print("next: fill the TODOs, then run validate")
        return 0

    if not args.path:
        raise SystemExit("path to a shot list JSON is required")

    data = load(Path(args.path))
    errors, warnings = check(data)

    if not args.quiet:
        for warning in warnings:
            print(f"WARN  {warning}")
        if errors:
            for error in errors:
                print(f"ERROR {error}")
        elif not warnings:
            print(f"OK    {len(data['shots'])} shots, {total_duration(data):.1f}s")
        else:
            print(f"OK    {len(data['shots'])} shots, {total_duration(data):.1f}s ({len(warnings)} warnings)")

    if errors:
        return 1
    if args.strict and warnings:
        print(f"STRICT  {len(warnings)} warnings treated as failures")
        return 1
    if args.command == "render":
        renderer = {
            "md": render_md,
            "beats": render_beats,
            "framing": render_framing,
            "cuts": render_cuts,
            "sheet": render_sheet,
            "timeline": render_timeline,
            "load": render_load,
            "rhythm": render_rhythm,
            "csv": render_csv,
            "storyboard": render_storyboard,
            "brief": render_brief,
        }[args.format]
        sys.stdout.write(renderer(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
