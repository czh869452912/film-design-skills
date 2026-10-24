#!/usr/bin/env python3
"""Corpus statistics and integrity checks for a set of shot lists.

Two jobs:

1. **Corpus stats** — how many shots, beats, mechanisms and cuts a body of work
   uses; which mechanisms are never used; the distribution of cut readiness.
2. **Doc integrity** — verifies that the mechanism index and the mechanism tables
   in `references/templates.md` agree, which catches hand-edited table damage.

Usage:
    python eval.py examples/
    python eval.py examples/ test-run2/ --markdown eval-report.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True  # keep the skill directory clean when importing shotlist

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import shotlist  # noqa: E402  (same directory)

REFERENCE_DIR = HERE.parent / "references"


def load_corpus(paths: list[Path]) -> list[tuple[Path, dict]]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
        elif path.suffix.lower() == ".json":
            files.append(path)
    corpus = []
    for file in files:
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            print(f"SKIP {file}: {error}")
            continue
        if isinstance(data, dict) and isinstance(data.get("shots"), list):
            corpus.append((file, data))
    return corpus


def doc_integrity() -> list[str]:
    issues: list[str] = []
    path = REFERENCE_DIR / "templates.md"
    if not path.exists():
        return ["references/templates.md missing"]
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    index_ids: list[str] = []
    detail_ids: list[str] = []
    in_index = False
    for line in lines:
        if line.startswith("## Index"):
            in_index = True
            continue
        if in_index and line.startswith("## "):
            in_index = False
        match = re.match(r"\|\s*(M\d{2})\s*\|", line)
        if match:
            (index_ids if in_index else detail_ids).append(match.group(1))

    if len(index_ids) != len(set(index_ids)):
        issues.append("templates.md index has duplicate mechanism IDs")
    missing_detail = sorted(set(index_ids) - set(detail_ids))
    missing_index = sorted(set(detail_ids) - set(index_ids))
    if missing_detail:
        issues.append(f"index lists but no detail row: {', '.join(missing_detail)}")
    if missing_index:
        issues.append(f"detail rows absent from index: {', '.join(missing_index)}")

    # column sanity: any table row with fewer than 3 cells is a broken row
    for number, line in enumerate(lines, start=1):
        if line.startswith("|") and not line.startswith("|---") and line.count("|") < 3:
            issues.append(f"templates.md line {number}: truncated table row")
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--markdown", default=None)
    args = ap.parse_args()

    corpus = load_corpus([Path(item) for item in args.paths])
    if not corpus:
        raise SystemExit("no shot lists found")

    shots_total = 0
    beats_total = 0
    duration_total = 0.0
    mechanisms: Counter[str] = Counter()
    beat_names: Counter[str] = Counter()
    sizes: Counter[str] = Counter()
    readiness: list[int] = []
    rhythm_rows: list[tuple[str, str, float]] = []
    warning_rows: list[tuple[str, int, int]] = []
    all_known = shotlist.load_mechanisms()

    for file, data in corpus:
        errors, warnings = shotlist.check(data)
        warning_rows.append((str(file), len(errors), len(warnings)))
        shots = data["shots"]
        shots_total += len(shots)
        duration_total += shotlist.total_duration(data)
        beats = data.get("beats") or []
        beats_total += len(beats)
        beat_map = {shotlist.as_text(b.get("id")): b for b in beats if isinstance(b, dict)}
        for beat in beats:
            if isinstance(beat, dict):
                beat_names[shotlist.as_text(beat.get("name"))] += 1
        for shot in shots:
            raw = shotlist.as_text(shot.get("mechanism")).upper().replace(" ", "")
            for part in [p for p in raw.split("+") if p]:
                mechanisms[part] += 1
            size = shotlist.as_text((shot.get("framing") or {}).get("size"))
            if size:
                sizes[size] += 1
        for prev, shot in zip(shots, shots[1:]):
            checks = shotlist.cut_checks(prev, shot, beat_map)
            readiness.append(sum(w for key, w in shotlist.MURCH_WEIGHTS if checks[key]))

        stats = shotlist.duration_stats(data)
        rhythm_rows.append((str(file), shotlist.detect_shape(data), stats["spread"]))

    used = set(mechanisms)
    unused = sorted(set(all_known) - used)
    avg_cuts = sum(readiness) / len(readiness) if readiness else 0.0
    low_cuts = sum(1 for score in readiness if score < 70)

    lines = [
        "# Shot-design corpus report",
        "",
        f"Files: {len(corpus)} · shots: {shots_total} · beats: {beats_total} · "
        f"planned runtime: {duration_total:.1f}s",
        "",
        "## Mechanisms",
        "",
        f"Used: {len(used)} / {len(all_known)} · distinct in corpus: {len(used)}",
        "",
        "| Mechanism | Uses |",
        "|---|---|",
    ]
    for mech, count in mechanisms.most_common():
        lines.append(f"| {mech} {all_known.get(mech, '')} | {count} |")
    if unused:
        lines += ["", f"Never used: {', '.join(unused)}"]

    lines += [
        "",
        "## Beats",
        "",
        "| Beat | Count |",
        "|---|---|",
    ]
    for name, count in beat_names.most_common():
        lines.append(f"| {name or '(unnamed)'} | {count} |")

    lines += [
        "",
        "## Framing",
        "",
        "| Size | Count |",
        "|---|---|",
    ]
    for size, count in sizes.most_common():
        lines.append(f"| {size} | {count} |")
    if sizes and shots_total:
        top_size, top_count = sizes.most_common(1)[0]
        share = top_count / shots_total
        if share > 0.5 and shots_total >= 4:
            lines += ["", f"Repetition: {top_size} is {share:.0%} of all shots — vary the size ladder."]

    lines += [
        "",
        "## Rhythm",
        "",
        "| File | Shape | Spread |",
        "|---|---|---|",
    ]
    for name, shape, spread in rhythm_rows:
        flag = " (near-uniform)" if spread < 0.3 and shape != "ritual" else ""
        lines.append(f"| {name} | {shape} | {spread:.0%}{flag} |")

    lines += [
        "",
        "## Cuts",
        "",
        f"Audited cuts: {len(readiness)} · average readiness: {avg_cuts:.0f}/100 · "
        f"below 70: {low_cuts}",
        "",
        "## Files",
        "",
        "| File | Errors | Warnings |",
        "|---|---|---|",
    ]
    for name, errors, warnings in warning_rows:
        lines.append(f"| {name} | {errors} | {warnings} |")

    integrity = doc_integrity()
    lines += ["", "## Doc integrity", ""]
    lines += [f"- {issue}" for issue in integrity] or ["- templates.md index and detail rows agree"]

    report = "\n".join(lines) + "\n"
    print(report)
    if args.markdown:
        Path(args.markdown).write_text(report, encoding="utf-8")
        print(f"written: {args.markdown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
