"""Compile a regular storyboard page for NovelAI; crop only measured, reviewed boxes.

No network or credentials. Generation belongs to the available NovelAI adapter.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
CORE = Path(__file__).resolve().parents[2] / 'shot-design' / 'scripts'
sys.path.insert(0, str(CORE))
from sequence import ID_PATTERN, iter_panels, load, validate


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f'{label} needs text')
    return value.strip()


def unit(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 1


def safe_id(value):
    require(isinstance(value, str) and ID_PATTERN.fullmatch(value), f'unsafe id: {value!r}')
    return value


def compile_page(plan, sequence=None):
    """One appearance-plus-current-state caption per visible person per panel."""
    cols, rows = plan['columns'], plan['rows']
    require(all(integer(n) and n > 0 for n in (cols, rows)), 'positive integer rows/columns required')
    panels = plan['panels']
    require(isinstance(panels, list) and len(panels) == cols * rows, 'grid must match panel count; split pages deliberately')
    width, height = plan['width'], plan['height']
    require(all(integer(n) and 64 <= n <= 4096 and n % 64 == 0 for n in (width, height)), 'size must be 64-pixel aligned, 64..4096')
    require(width * height <= 3145728, 'page exceeds 3,145,728 pixels')
    people = plan['characters']
    require(isinstance(people, dict), 'characters must be an identity dictionary')
    for cid, person in people.items():
        safe_id(cid)
        text(person['appearance'], f'{cid} appearance')
    known = None
    if sequence is not None:
        errors, _ = validate(sequence)
        require(not errors, '; '.join(errors))
        known = {p['id']: p['shot_id'] for p in iter_panels(sequence)}
    prompt = [text(plan['style'], 'style'), text(plan['global_prompt'], 'global_prompt'),
              f'comic, multiple views, storyboard page, exactly {len(panels)} separate panels in {rows} rows and {cols} columns, thin straight panel borders, read left to right then top to bottom']
    captions, layout, seen = [], [], set()
    for index, panel in enumerate(panels):
        pid, sid = safe_id(panel['panel_id']), safe_id(panel['shot_id'])
        require(pid not in seen, f'duplicate panel {pid}')
        seen.add(pid)
        require(known is None or known.get(pid) == sid, f'unknown or mismatched shot/panel: {sid}/{pid}')
        row, col = divmod(index, cols)
        location = f'row {row+1} column {col+1}'
        prompt.append(f'Panel {index+1}, {location}: {text(panel["summary"], pid+" summary")}')
        instances = panel.get('instances', [])
        require(isinstance(instances, list), f'{pid} instances must be a list')
        panel_people = set()
        for instance in instances:
            cid = instance['character_id']
            require(cid in people and cid not in panel_people, f'unknown or duplicate identity in {pid}: {cid}')
            panel_people.add(cid)
            center = instance['local_center']
            require(isinstance(center, list) and len(center) == 2 and all(unit(n) for n in center), 'local_center needs two finite 0..1 numbers')
            appearance = instance.get('visible_appearance', people[cid]['appearance'])
            caption = ', '.join([text(appearance, 'appearance'), text(instance['prompt'], 'instance prompt')])
            captions.append({'prompt': caption, 'uc': instance.get('negative', ''),
                             'centers': [{'x': (col+center[0])/cols, 'y': (row+center[1])/rows}]})
        layout.append({'panel_id': pid, 'shot_id': sid, 'grid_cell': [col, row],
                       'planned_bounds': [col/cols, row/rows, (col+1)/cols, (row+1)/rows]})
    require(len(captions) <= 22, 'V5 page exceeds 22 character occurrence slots; split the page')
    prompt.append('no text, no speech bubbles')
    return {'prompt': '\n'.join(prompt), 'negative': plan.get('negative', ''), 'characters': captions,
            'layout': {'page_id': safe_id(plan['page_id']), 'width': width, 'height': height,
                       'columns': cols, 'rows': rows, 'panels': layout, 'boxes_are': 'planned-only-not-approved-crops'}}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def crop_page(review, layout, review_path, out):
    from PIL import Image
    require(review.get('layout_reviewed') is True, 'inspect the actual page and confirm its layout before cropping')
    image_path = (review_path.parent / review['image']).resolve()
    require(review.get('image_sha256') == digest(image_path), 'review must identify the exact source image SHA256')
    image = Image.open(image_path)
    require(image.size == (layout['width'], layout['height']), 'actual image size differs from planned page')
    safe_id(layout['page_id'])
    expected = {safe_id(p['panel_id']): p for p in layout['panels']}
    require(len(expected) == len(layout['panels']), 'duplicate planned panel ids')
    actual = review['panels']
    require(isinstance(actual, list), 'review panels must be a list')
    require(len(actual) == len(expected) and {p['panel_id'] for p in actual} == set(expected), 'crop ids must match the planned page exactly')
    boxes, entries = [], []
    for panel in actual:
        pid = panel['panel_id']
        box = panel['box']
        require(isinstance(box, list) and len(box) == 4 and all(integer(n) for n in box), f'{pid}: pixel box needs four integers')
        x0, y0, x1, y1 = box
        require(0 <= x0 < x1 <= image.width and 0 <= y0 < y1 <= image.height, f'{pid}: crop outside image or empty')
        require(isinstance(panel.get('content_approved'), bool), f'{pid}: record content_approved separately from layout review')
        text(panel.get('observation'), f'{pid} observation')
        for other in boxes:
            require(min(x1, other[2]) <= max(x0, other[0]) or min(y1, other[3]) <= max(y0, other[1]), 'regular-grid crop boxes overlap')
        boxes.append(box)
        entries.append({**expected[pid], 'box': box, 'image': f'{pid}.png',
                        'content_approved': panel['content_approved'], 'observation': panel['observation']})
    require(not out.exists(), f'output already exists: {out}')
    out.mkdir(parents=True)
    for entry in entries:
        image.crop(entry['box']).save(out / entry['image'])
    result = {'page_id': layout['page_id'], 'source_image': str(image_path), 'source_sha256': digest(image_path),
              'layout_reviewed': True, 'all_content_approved': all(p['content_approved'] for p in entries), 'panels': entries}
    (out / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    build = sub.add_parser('compile')
    build.add_argument('plan', type=Path)
    build.add_argument('--sequence', type=Path)
    build.add_argument('--out', type=Path, required=True)
    crop = sub.add_parser('crop')
    crop.add_argument('review', type=Path)
    crop.add_argument('--layout', type=Path, required=True)
    crop.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    try:
        if args.command == 'compile':
            result = compile_page(load(args.plan), load(args.sequence) if args.sequence else None)
            require(not args.out.exists(), f'output already exists: {args.out}')
            args.out.mkdir(parents=True)
            for name in ('prompt', 'negative'):
                (args.out / f'{name}.txt').write_text(result[name]+'\n', encoding='utf-8')
            for name in ('characters', 'layout'):
                (args.out / f'{name}.json').write_text(json.dumps(result[name], ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            print(f'Compiled {len(result["layout"]["panels"])} panels, {len(result["characters"])} occurrence slots; planned layout only')
        else:
            result = crop_page(load(args.review), load(args.layout), args.review, args.out)
            print(f'Cropped {len(result["panels"])} panels; content approved: {result["all_content_approved"]}')
    except (ValueError, KeyError, TypeError, OSError) as error:
        ap.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
