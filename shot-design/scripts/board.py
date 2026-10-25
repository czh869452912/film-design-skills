#!/usr/bin/env python3
"""Assemble existing panels into a review grid without cropping or approving content."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from sequence import iter_panels, load, require_valid, resolve_image


def compose(plan: Path, out: Path, *, images: Path | None = None,
            columns: int = 2, cell_width: int = 640, cell_height: int = 360) -> dict:
    from PIL import Image, ImageDraw, ImageOps

    if any(isinstance(n, bool) or not isinstance(n, int) or n < 1
           for n in (columns, cell_width, cell_height)):
        raise ValueError('columns and cell dimensions must be positive integers')
    if out.suffix.lower() != '.png':
        raise ValueError('review board output must be PNG')
    manifest_path = out.with_suffix('.json')
    if out.exists() or manifest_path.exists():
        raise ValueError('output image or manifest already exists')
    data = load(plan)
    require_valid(data)
    panels = list(iter_panels(data))
    sources = [resolve_image(p, images=images, base=plan.parent) for p in panels]
    missing = [p['id'] for p, src in zip(panels, sources) if src is None]
    if missing:
        raise ValueError('missing panels: ' + ', '.join(missing))
    columns = min(columns, len(panels))
    gap, label_height = 12, 24
    width = columns * cell_width + (columns + 1) * gap
    rows = math.ceil(len(panels) / columns)
    height = rows * (cell_height + label_height) + (rows + 1) * gap
    if width * height > 64_000_000:
        raise ValueError('review board exceeds 64 million pixels; reduce cell size or split plan')
    sheet = Image.new('RGB', (width, height), '#e8e8e8')
    draw = ImageDraw.Draw(sheet)
    entries = []
    for index, (panel, source) in enumerate(zip(panels, sources)):
        row, col = divmod(index, columns)
        x, y = gap + col * (cell_width + gap), gap + row * (cell_height + label_height + gap)
        draw.text((x, y + 4), panel['id'] + ' / ' + panel['shot_id'], fill='black')
        y += label_height
        draw.rectangle((x, y, x + cell_width - 1, y + cell_height - 1), fill='#202020')
        with Image.open(source) as opened:
            image = ImageOps.exif_transpose(opened).convert('RGB')
        thumb = ImageOps.contain(image, (cell_width, cell_height))
        left, top = x + (cell_width - thumb.width) // 2, y + (cell_height - thumb.height) // 2
        sheet.paste(thumb, (left, top))
        entries.append({'panel_id': panel['id'], 'shot_id': panel['shot_id'],
                        'source_image': str(source.resolve()),
                        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                        'source_size': list(image.size),
                        'cell_box': [x, y, x + cell_width, y + cell_height],
                        'image_box': [left, top, left + thumb.width, top + thumb.height]})
    result = {'kind': 'review-board', 'title': data.get('title'), 'columns': columns,
              'rows': rows, 'size': [width, height], 'content_reviewed': False, 'panels': entries}
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    manifest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('plan', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--images', type=Path)
    ap.add_argument('--columns', type=int, default=2)
    ap.add_argument('--cell-width', type=int, default=640)
    ap.add_argument('--cell-height', type=int, default=360)
    args = ap.parse_args()
    try:
        result = compose(args.plan, args.out, images=args.images, columns=args.columns,
                         cell_width=args.cell_width, cell_height=args.cell_height)
        print(f'Assembled {len(result["panels"])} panels; content not assessed')
    except (ValueError, OSError) as error:
        ap.exit(1, f'{error}\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
