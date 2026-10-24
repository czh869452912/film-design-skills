#!/usr/bin/env python3
"""Build a reference pack from storyboard panels.

Copies each shot's panel into an ordered folder and writes a manifest that a
prompt writer can turn into per-picture roles (H3 Ref2VA `<Picture N>`, Seedance
`@Image N`). The panels become the composition/staging references for the video
model — the previs drawing is the input, not just the check.

Usage:
    python build_refpack.py shotlist.json --images storyboard --out refs/run1
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data.get("shots"), list):
        raise SystemExit("shot list needs a 'shots' array")
    return data


def find_panel(images: Path, shot_id: str) -> Path | None:
    for ext in IMAGE_EXTS:
        candidate = images / f"{shot_id}{ext}"
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("shotlist")
    ap.add_argument("--images", required=True, help="directory with <shot_id> panel images")
    ap.add_argument("--out", required=True, help="destination for the ordered reference pack")
    ap.add_argument("--first-frame", action="store_true",
                    help="mark picture 1 as the first frame instead of only a staging reference")
    args = ap.parse_args()

    data = load(Path(args.shotlist))
    images = Path(args.images)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    missing = []
    index = 0
    for shot in data["shots"]:
        shot_id = str(shot.get("id") or f"S{index + 1:02d}")
        source = find_panel(images, shot_id)
        if source is None:
            missing.append(shot_id)
            continue
        index += 1
        target = out_dir / f"{index:02d}-{shot_id}{source.suffix.lower()}"
        shutil.copyfile(source, target)
        framing = shot.get("framing") or {}
        composition = shot.get("composition") or {}
        staging = shot.get("staging") or {}
        role = (
            f"composition and staging of [Shot {index}]"
            + (" and the first frame of the video" if args.first_frame and index == 1 else "")
        )
        entries.append(
            {
                "picture": f"Picture {index}",
                "shot": shot_id,
                "file": target.name,
                "role": role,
                "size": framing.get("size"),
                "angle": framing.get("angle"),
                "subjects": [
                    {
                        "screen": subject.get("screen"),
                        "facing": subject.get("facing"),
                        "pose": subject.get("pose"),
                    }
                    for subject in (staging.get("subjects") or [])
                    if isinstance(subject, dict)
                ],
                "value_masses": composition.get("value_masses"),
                "note": (
                    "Use for layout, subject placement, screen direction and light direction. "
                    "Do not carry over the sketch style, line work, labels or annotations."
                ),
            }
        )

    manifest = {
        "title": data.get("title"),
        "count": len(entries),
        "pictures": entries,
        "instructions": [
            "Feed the files in this order as <Picture 1>..<Picture N> (H3) or @Image N (Seedance).",
            "Panels are staging references; give them that role explicitly and exclude their sketch style.",
            "Use unannotated panels: labels and arrows are for review, not for the model.",
        ],
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [f"# Reference pack — {data.get('title') or 'untitled'}", ""]
    for entry in entries:
        lines.append(
            f"- **{entry['picture']}** `{entry['file']}` — {entry['role']}; "
            f"{entry['size']} / {entry['angle']}"
        )
        if entry["value_masses"]:
            lines.append(f"  - values: {entry['value_masses']}")
        for subject in entry["subjects"]:
            lines.append(
                f"  - {subject['screen']} facing {subject['facing']}: {subject['pose']}"
            )
    lines += ["", "Exclude the sketch style and any labels when describing these references."]
    (out_dir / "refs.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"refpack: {len(entries)} pictures -> {out_dir}")
    if missing:
        print(f"missing panels: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
