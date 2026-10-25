#!/usr/bin/env python3
"""Describe a shot-list corpus and check structure; never score film quality."""
from __future__ import annotations
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode = True
import shotlist
from sequence import iter_panels
REFERENCE_DIR = Path(__file__).resolve().parents[1] / 'references'


def doc_integrity() -> list[str]:
    path = REFERENCE_DIR / 'templates.md'
    if not path.is_file():
        return ['references/templates.md missing']
    ids = re.findall(r'^\|\s*(M\d{2})\s*\|', path.read_text(encoding='utf-8-sig'), re.MULTILINE)
    issues = []
    if len(ids) != len(set(ids)):
        issues.append('templates.md: duplicate IDs')
    if set(ids) != {f'M{i:02d}' for i in range(1,43)}:
        issues.append('templates.md: stable M01..M42 IDs incomplete or unexpected')
    return issues


def load_corpus(paths):
    files = set()
    for path in paths:
        files.update(path.rglob('*.json') if path.is_dir() else [path])
    corpus, issues = [], []
    for path in sorted(files):
        try:
            data = json.loads(path.read_text(encoding='utf-8-sig'))
        except (OSError, ValueError) as error:
            issues.append(f'{path}: {error}')
            continue
        if isinstance(data, dict) and 'shots' in data:
            corpus.append((path, data))
    return corpus, issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('paths', nargs='+', type=Path)
    ap.add_argument('--markdown')
    args = ap.parse_args()
    corpus, read_issues = load_corpus(args.paths)
    if not corpus and not read_issues:
        raise SystemExit('no shot lists found')
    rows, errors_all, shots, panels, pending, cuts = [], list(read_issues), 0, 0, 0, 0
    mechanism_counts = Counter()
    for path, data in corpus:
        errors, warnings = shotlist.check(data)
        errors_all.extend(f'{path}: {e}' for e in errors)
        if errors:
            rows.append((path, len(errors), 'invalid', 'not assessed'))
            continue
        views = list(iter_panels(data))
        shots += len(data['shots'])
        panels += len(views)
        cuts += max(0, len(data['shots']) - 1)
        pending += sum(p['duration_s'] is None for p in views)
        rows.append((path, 0, shotlist.detect_shape(data), 'not assessed'))
        for shot in data['shots']:
            for mid in str(shot.get('mechanism') or '').split('+'):
                if mid:
                    mechanism_counts[mid] += 1
    integrity = doc_integrity()
    lines = ['# Shot-design corpus inventory', '',
             f'Files: {len(corpus)} · valid shots: {shots} · panels: {panels} · cuts: {cuts} · untimed panels: {pending}', '',
             'Counts and timing shapes describe the corpus. They do not measure comprehension, quality or required variety.', '',
             '## Files', '', shotlist.table(['File', 'Structural errors', 'Timing', 'Visual comprehension'], rows),
             '## Optional mechanism usage', '', shotlist.table(['ID', 'Uses'], mechanism_counts.most_common()),
             '## Doc integrity', '']
    lines += ['- ' + i for i in integrity] or ['- templates.md stable IDs are complete and unique']
    if errors_all:
        lines += ['', '## Structural / read errors', ''] + ['- ' + i for i in errors_all]
    report = '\n'.join(lines) + '\n'
    print(report)
    if args.markdown:
        Path(args.markdown).write_text(report, encoding='utf-8')
    return 1 if errors_all or integrity else 0


if __name__ == '__main__':
    sys.exit(main())
