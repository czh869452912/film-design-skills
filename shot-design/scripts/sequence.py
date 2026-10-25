"""Shared shot/panel representation. No film-quality scores or model defaults."""
from __future__ import annotations

import copy
import json
import math
import re
from pathlib import Path

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def beat_ids(shot: dict) -> list[str]:
    if "beat_ids" in shot:
        return shot["beat_ids"]
    return [shot["beat_id"]] if shot.get("beat_id") else []


def shot_duration(shot: dict) -> float | None:
    panels = shot.get("panels")
    if panels:
        if not isinstance(panels, list) or any(not isinstance(p, dict) for p in panels):
            return None
        values = [p.get("duration_s") for p in panels]
        if all(number(v) for v in values):
            return sum(values)
        if len(panels) == 1 and values[0] is None and number(shot.get("duration_s")):
            return float(shot["duration_s"])
        return None
    value = shot.get("duration_s")
    return float(value) if number(value) else None


def load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        raise SystemExit(f"cannot read {path}: {error}") from error
    return data


def validate(data, *, timed: bool = False) -> tuple[list[str], list[str]]:
    """Check explicit structure only; a valid document is not a reviewed board."""
    errors, warnings = [], []
    if not isinstance(data, dict) or not isinstance(data.get("shots"), list) or not data["shots"]:
        return ["shot list needs a non-empty shots array"], []
    for key in ("target", "style", "intent", "scene", "review", "rhythm"):
        if key in data and not isinstance(data[key], dict):
            errors.append(f"{key} must be an object")
    beats = data.get("beats", [])
    if not isinstance(beats, list):
        errors.append("beats must be a list")
        beats = []
    known_beats = set()
    for b in beats:
        if not isinstance(b, dict) or not isinstance(b.get("id"), str) or not b["id"]:
            errors.append("each beat needs a string id")
            continue
        if b["id"] in known_beats:
            errors.append(f"duplicate beat id {b['id']}")
        known_beats.add(b["id"])
        if "duration_s" in b and (not number(b["duration_s"]) or b["duration_s"] <= 0):
            errors.append(f"beat {b['id']}: duration_s must be finite and positive")
        if "tension" in b and (not number(b["tension"]) or not 0 <= b["tension"] <= 10):
            errors.append(f"beat {b['id']}: tension must be 0-10 when supplied")
    ids, panel_ids, durations = set(), set(), []
    for i, shot in enumerate(data["shots"], 1):
        if not isinstance(shot, dict):
            errors.append(f"shot #{i} must be an object")
            continue
        sid = shot.get("id")
        if not isinstance(sid, str) or not ID_PATTERN.fullmatch(sid):
            errors.append(f"shot #{i}: id must use letters, digits, underscores or hyphens")
            sid = f"#{i}"
        if sid in ids:
            errors.append(f"duplicate shot id {sid}")
        ids.add(sid)
        for key in ("framing", "camera", "action", "composition", "staging", "sound", "emotion", "storyboard", "light", "render", "transition_out"):
            if key in shot and not isinstance(shot[key], dict):
                errors.append(f"{sid}.{key} must be an object")
        for key in ("continuity", "references", "bans", "beats"):
            if key in shot and not isinstance(shot[key], list):
                errors.append(f"{sid}.{key} must be a list")
        framing = shot.get("framing")
        if isinstance(framing, dict) and "options" in framing:
            options = framing["options"]
            if not isinstance(options, list) or any(not isinstance(o, dict) for o in options):
                errors.append(f"{sid}.framing.options must be a list of objects")
        render = shot.get("render")
        if isinstance(render, dict) and "image" in render and (not isinstance(render["image"], str) or not render["image"].strip()):
            errors.append(f"{sid}.render.image must be a non-empty path")
        refs = shot.get("beat_ids", [shot["beat_id"]] if "beat_id" in shot else [])
        if not isinstance(refs, list) or any(not isinstance(v, str) for v in refs):
            errors.append(f"{sid}.beat_ids must be a list of strings")
        else:
            if len(refs) != len(set(refs)):
                errors.append(f"{sid}: duplicate beat reference")
            for bid in refs:
                if bid not in known_beats:
                    errors.append(f"{sid}: unknown beat {bid}")
            if "beat_ids" in shot and "beat_id" in shot and shot["beat_id"] not in refs:
                errors.append(f"{sid}: beat_id conflicts with beat_ids")
        if "duration_s" in shot and (not number(shot["duration_s"]) or shot["duration_s"] <= 0):
            errors.append(f"{sid}: duration_s must be finite and positive")
        raw = shot.get("panels")
        if "panels" in shot and (not isinstance(raw, list) or not raw):
            errors.append(f"{sid}.panels must be a non-empty list")
            raw = None
        action = shot.get("action")
        storyboard = shot.get("storyboard")
        if raw is None:
            desc = action.get("primary") if isinstance(action, dict) else None
            desc = desc or (storyboard.get("panel") if isinstance(storyboard, dict) else None)
            if not isinstance(desc, str) or not desc.strip():
                errors.append(f"{sid}: supply action.primary or panels with descriptions")
        for j, panel in enumerate(raw or [], 1):
            if not isinstance(panel, dict):
                errors.append(f"{sid} panel #{j} must be an object")
                continue
            pid = panel.get("id")
            if not isinstance(pid, str) or not ID_PATTERN.fullmatch(pid):
                errors.append(f"{sid} panel #{j}: invalid id")
                pid = f"{sid}/#{j}"
            if pid in panel_ids:
                errors.append(f"duplicate panel id {pid}")
            panel_ids.add(pid)
            if not isinstance(panel.get("description"), str) or not panel["description"].strip():
                errors.append(f"{pid}: description is required")
            if "duration_s" in panel and (not number(panel["duration_s"]) or panel["duration_s"] <= 0):
                errors.append(f"{pid}: duration_s must be finite and positive")
            for key in ("framing", "composition", "staging", "sound", "state"):
                if key in panel and not isinstance(panel[key], dict):
                    errors.append(f"{pid}.{key} must be an object")
            if "image" in panel and (not isinstance(panel["image"], str) or not panel["image"].strip()):
                errors.append(f"{pid}.image must be a non-empty path")
            if "overlays" in panel:
                validate_overlays(panel["overlays"], pid, errors)
        if isinstance(storyboard, dict) and "overlays" in storyboard:
            validate_overlays(storyboard["overlays"], sid, errors)
        emotion = shot.get("emotion")
        if isinstance(emotion, dict) and "dials" in emotion:
            dials = emotion["dials"]
            if not isinstance(dials, dict) or any(not number(v) or not 0 <= v <= 10 for v in dials.values()):
                errors.append(f"{sid}: optional dials must be numbers 0-10")
        if raw and any(not isinstance(p, dict) for p in raw):
            continue
        duration = shot_duration(shot)
        durations.append(duration)
        if timed and duration is None:
            errors.append(f"{sid}: timing pending; time every panel before media export")
        if raw and number(shot.get("duration_s")):
            if duration is None:
                errors.append(f"{sid}: give each panel a duration; do not divide the shot silently")
            elif abs(duration - shot["duration_s"]) > 0.001:
                errors.append(f"{sid}: panel durations {duration:g}s differ from shot {shot['duration_s']:g}s")
    # Synthesized legacy panels use the shot id. Avoid filename collisions across formats.
    legacy_ids = {s.get("id") for s in data["shots"] if isinstance(s, dict) and not s.get("panels") and isinstance(s.get("id"), str)}
    for pid in legacy_ids & panel_ids:
        errors.append(f"panel id {pid} collides with a legacy shot image id")
    target = data.get("target")
    if isinstance(target, dict) and "duration_s" in target:
        v = target["duration_s"]
        if not number(v) or v <= 0:
            errors.append("target.duration_s must be finite and positive")
        elif len(durations) == len(data["shots"]) and all(v is not None for v in durations):
            if abs(sum(durations) - target["duration_s"]) > 0.001:
                errors.append(f"target duration {target['duration_s']:g}s differs from panels/shots {sum(durations):g}s")
    return errors, warnings


def validate_overlays(items, label: str, errors: list) -> None:
    if not isinstance(items, list):
        errors.append(f"{label}.overlays must be a list")
        return
    def point(p):
        return isinstance(p, (list, tuple)) and len(p) == 2 and all(number(v) and 0 <= v <= 1 for v in p)
    for item in items:
        if not isinstance(item, dict) or item.get("type") not in ("arrow", "sight", "impact", "orbit"):
            errors.append(f"{label}: unknown overlay type")
            continue
        keys = ("from", "to") if item["type"] in ("arrow", "sight") else ("at",)
        if any(not point(item.get(k)) for k in keys):
            errors.append(f"{label}: overlay coordinates must be [x,y] in 0-1")
        for key in ("curve", "size", "radius", "start", "end"):
            if key in item and not number(item[key]):
                errors.append(f"{label}: overlay {key} must be finite")
            elif key in ("size", "radius") and key in item and item[key] <= 0:
                errors.append(f"{label}: overlay {key} must be positive")


def normalize(data: dict) -> dict:
    """Return a copy with panels and derived shot durations; retain legacy fields."""
    result = copy.deepcopy(data)
    for shot in result["shots"]:
        duration = shot_duration(shot)
        if "panels" not in shot:
            board = shot.get("storyboard") or {}
            shot["panels"] = [{
                "id": shot["id"], "duration_s": duration,
                "description": board.get("panel") or (shot.get("action") or {}).get("primary", ""),
                "image": (shot.get("render") or {}).get("image"),
                "overlays": board.get("overlays", []),
            }]
        elif len(shot["panels"]) == 1 and "duration_s" not in shot["panels"][0] and duration is not None:
            shot["panels"][0]["duration_s"] = duration
        shot["duration_s"] = duration
        shot["beat_ids"] = beat_ids(shot)
    return result


def iter_panels(data: dict):
    for shot in normalize(data)["shots"]:
        for i, panel in enumerate(shot["panels"]):
            view = copy.deepcopy(shot)
            for key in ("framing", "composition", "staging", "sound"):
                view[key] = {**(shot.get(key) or {}), **(panel.get(key) or {})}
            view.update(id=panel["id"], shot_id=shot["id"], shot_start=i == 0,
                        duration_s=panel.get("duration_s"), image=panel.get("image"),
                        description=panel["description"], state=panel.get("state", {}),
                        storyboard={"panel": panel["description"], "overlays": panel.get("overlays", [])})
            yield view


def resolve_image(panel: dict, *, images: Path | None = None, base: Path | None = None) -> Path | None:
    root = images if images is not None else (base or Path.cwd())
    value = panel.get("image")
    if images is None and value:
        explicit = Path(value)
        explicit = explicit if explicit.is_absolute() else root / explicit
        if explicit.is_file():
            return explicit
    # An override folder (e.g. annotated copies) takes precedence over original image paths.
    for ext in IMAGE_EXTS:
        path = root / f"{panel['id']}{ext}"
        if path.is_file():
            return path
    if value:
        path = Path(value)
        if images is not None and path.is_absolute():
            return None
        path = path if path.is_absolute() else root / path
        if path.is_file():
            return path
    return None


def require_valid(data: dict, *, timed=False) -> None:
    errors, _ = validate(data, timed=timed)
    if errors:
        raise SystemExit("invalid shot list:\n" + "\n".join(errors))
