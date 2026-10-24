# Source conversion tools

How the two reference books became `build/extracted/*/full.md`. Kept for reproducibility; not needed at skill runtime.

## 1. MinerU extraction

```bash
python tools/mineru_extract.py reference/*.pdf --out build/extracted
```

Uses the MinerU Precision Extract API (v4): request batch upload URLs → `PUT` the files → poll the batch result → download each result zip and unpack it. Reads `MINERU_ACCESS_TOKEN` from `.env`.

Notes from this run:

- Account limit is **200 pages per file**. *Shot by Shot* is 474 pages, so it was split first.
- `--model vlm` was used; `pipeline` is the cheaper default.
- Each extracted folder contains `full.md` plus the book's figures as `images/`.

## 2. Splitting oversized PDFs

```bash
python tools/split_pdf.py "reference/Film Directing Shot by Shot_ Visualizing from Concept to Screen.pdf" \
  --pages-per-file 160 --prefix shotbyshot
```

Writes `build/split/*.pdf`, which are then passed to the extractor and may be deleted afterwards (they are page-range duplicates of the original).

## 3. What remains in the repo

- `build/extracted/` — the Markdown and figures used to write the skill.
- `.env` — tokens, git-ignored; never commit.
