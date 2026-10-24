#!/usr/bin/env python3
"""Split a large PDF into page-range chunks (MinerU caps a file at 200 pages)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--pages-per-file", type=int, default=150)
    ap.add_argument("--outdir", default="reference/_split")
    ap.add_argument("--prefix", default=None)
    args = ap.parse_args()

    src = Path(args.pdf).resolve()
    reader = PdfReader(str(src))
    total = len(reader.pages)
    outdir = (src.parents[1] / args.outdir).resolve() if not Path(args.outdir).is_absolute() else Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix or src.stem[:40].replace(" ", "_")

    written = []
    for start in range(0, total, args.pages_per_file):
        end = min(start + args.pages_per_file, total)
        writer = PdfWriter()
        for i in range(start, end):
            writer.add_page(reader.pages[i])
        target = outdir / f"{prefix}_p{start + 1:03d}-{end:03d}.pdf"
        with target.open("wb") as fh:
            writer.write(fh)
        written.append(target)
        print(f"{target}  ({target.stat().st_size / 1e6:.1f} MB)")

    print(f"split {total} pages into {len(written)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
