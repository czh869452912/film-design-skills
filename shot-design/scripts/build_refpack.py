#!/usr/bin/env python3
"""Pack selected clean panels, retaining original shot/panel associations."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from sequence import iter_panels, load, require_valid, resolve_image


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("shotlist")
    ap.add_argument("--images", help="override image folder; otherwise paths are relative to JSON")
    ap.add_argument("--out", required=True)
    ap.add_argument("--select", action="append", help="panel id to include; repeat, or omit for all")
    ap.add_argument("--first-frame", action="store_true", help="mark the actual first panel as a first-frame reference")
    ap.add_argument("--allow-missing", action="store_true", help="allow a manifest explicitly marked incomplete")
    args = ap.parse_args()
    plan = Path(args.shotlist)
    data = load(plan)
    require_valid(data)
    all_panels = list(iter_panels(data))
    wanted = set(args.select or [p['id'] for p in all_panels])
    unknown = wanted - {p['id'] for p in all_panels}
    if unknown:
        raise SystemExit("unknown panels: " + ", ".join(sorted(unknown)))
    if args.first_frame and all_panels[0]['id'] not in wanted:
        raise SystemExit("--first-frame requires the actual first panel in the selection")
    panels = [p for p in all_panels if p['id'] in wanted]
    sources = [resolve_image(p, images=Path(args.images) if args.images else None, base=plan.parent) for p in panels]
    missing = [p['id'] for p, src in zip(panels, sources) if src is None]
    if missing and not args.allow_missing:
        raise SystemExit("missing panels: " + ", ".join(missing))
    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    shot_indices = {s['id']: i for i, s in enumerate(data['shots'], 1)}
    entries = []
    for panel, source in zip(panels, sources):
        if source is None:
            continue
        index = len(entries) + 1
        target = dest / f"{index:02d}-{panel['id']}{source.suffix.lower()}"
        if source.resolve() == target.resolve():
            raise SystemExit(f"source and output are the same: {source}")
        shutil.copyfile(source, target)
        role = f"staging reference for shot {panel['shot_id']}, panel {panel['id']}"
        if args.first_frame and panel['id'] == all_panels[0]['id']:
            role += "; first frame"
        entries.append(dict(reference_id=f"R{index:02d}", picture=f"Picture {index}", shot=panel['shot_id'],
                            shot_index=shot_indices[panel['shot_id']], panel=panel['id'],
                            file=target.name, role=role, description=panel['description'],
                            framing=panel.get('framing', {}), staging=panel.get('staging', {})))
    payload = dict(title=data.get('title'), count=len(entries), pictures=entries,
                   missing_panels=missing, complete=not missing,
                   instructions=["Reference index, shot index and panel id are different identifiers.",
                                 "The target adapter chooses supported bindings and reference count.",
                                 "Use clean panels; style exclusion instructions cannot guarantee absence of style leakage."])
    (dest / 'manifest.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')
    lines = [f"# Reference pack — {data.get('title', 'untitled')}", ""]
    lines += [f"- {e['reference_id']}: {e['file']} — {e['role']} (original shot #{e['shot_index']})" for e in entries]
    if missing:
        lines.append("Incomplete: " + ", ".join(missing))
    (dest / 'refs.md').write_text("\n".join(lines) + "\n", encoding='utf-8')
    print(f"refpack: {len(entries)} references; {len(missing)} missing panels -> {dest}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
