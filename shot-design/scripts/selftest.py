#!/usr/bin/env python3
"""Self-test: run the skill's own tools against its examples and synthetics.

This is the regression gate for the scripts. It needs no network. FFmpeg is
optional: the animatic test is skipped when ffmpeg is not on PATH.

Usage:
    python selftest.py
    python selftest.py --verbose
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
EXAMPLES = SKILL / "examples"
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import shotlist  # noqa: E402


def run(cmd: list[str], cwd: Path | None = None, expect: int = 0) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, cwd=str(cwd or SKILL), capture_output=True, text=True)
    if result.returncode != expect:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"{result.stdout[-800:]}\n{result.stderr[-800:]}"
        )
    return result


def test_examples_validate(python: str) -> int:
    count = 0
    for path in sorted(EXAMPLES.glob("*.json")):
        run([python, str(HERE / "shotlist.py"), "validate", str(path), "--strict"])
        count += 1
    return count


def test_render_formats(python: str) -> int:
    target = EXAMPLES / "descent.json"
    formats = ["md", "beats", "framing", "cuts", "sheet", "timeline", "load", "rhythm", "csv", "storyboard", "brief"]
    for fmt in formats:
        result = run([python, str(HERE / "shotlist.py"), "render", str(target), "--format", fmt, "--quiet"])
        if len(result.stdout.strip()) < 20:
            raise AssertionError(f"format {fmt} produced no output")
    return len(formats)


def test_mechanisms(python: str) -> int:
    result = run([python, str(HERE / "shotlist.py"), "mechanisms"])
    ids = [line.split()[0] for line in result.stdout.splitlines() if line.startswith("M")]
    if len(ids) < 40:
        raise AssertionError(f"only {len(ids)} mechanisms found")
    if len(ids) != len(set(ids)):
        raise AssertionError("duplicate mechanism IDs")
    return len(ids)


def test_eval(python: str) -> int:
    result = run([python, str(HERE / "eval.py"), str(EXAMPLES)])
    if "Doc integrity" not in result.stdout:
        raise AssertionError("eval report missing doc integrity section")
    if "truncated" in result.stdout or "no detail row" in result.stdout:
        raise AssertionError("eval reported doc integrity issues")
    return 1


def test_init_and_synthetic(python: str, verbose: bool) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        scaffold = tmp_dir / "synthetic.json"
        run([python, str(HERE / "shotlist.py"), "init", str(scaffold),
             "--title", "Synthetic", "--duration", "6", "--shots", "2"])
        run([python, str(HERE / "shotlist.py"), "validate", str(scaffold), "--strict"])

        try:
            from PIL import Image
        except ImportError:
            return 1

        panels = tmp_dir / "panels"
        panels.mkdir()
        for name in ("S01", "S02"):
            Image.new("RGB", (640, 360), (200, 200, 200)).save(panels / f"{name}.png")

        annotated = tmp_dir / "annotated"
        run([python, str(HERE / "annotate.py"), str(scaffold),
             "--images", str(panels), "--out", str(annotated)])
        if not (annotated / "S01.png").exists():
            raise AssertionError("annotate did not write a panel")

        if shutil.which("ffmpeg") is None:
            if verbose:
                print("  animatic skipped (no ffmpeg)")
            return 2

        movie = tmp_dir / "animatic.mp4"
        run([python, str(HERE / "animatic.py"), str(scaffold),
             "--images", str(panels), "--out", str(movie)])
        if not movie.exists() or movie.stat().st_size < 1000:
            raise AssertionError("animatic did not write a video")
        return 3


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    python = sys.executable
    tests = [
        ("examples validate --strict", lambda: test_examples_validate(python)),
        ("render formats", lambda: test_render_formats(python)),
        ("mechanism library", lambda: test_mechanisms(python)),
        ("corpus eval", lambda: test_eval(python)),
        ("init + annotate + animatic", lambda: test_init_and_synthetic(python, args.verbose)),
    ]

    failures = 0
    for name, test in tests:
        try:
            detail = test()
            print(f"PASS  {name}" + (f" ({detail})" if args.verbose else ""))
        except AssertionError as error:
            failures += 1
            print(f"FAIL  {name}: {error}")
        except Exception as error:  # noqa: BLE001
            failures += 1
            print(f"ERROR {name}: {type(error).__name__}: {error}")

    print(f"\n{len(tests) - failures}/{len(tests)} tests passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
