#!/usr/bin/env python3
"""Convert local PDFs to Markdown with the MinerU "Precision Extract" API (v4).

Flow: request batch upload URLs -> PUT the files -> poll batch results ->
download each result zip -> extract full.md + images.

Token is read from .env (MINERU_ACCESS_TOKEN) or the environment.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
import zipfile
from pathlib import Path

import requests

API = "https://mineru.net/api/v4"
ROOT = Path(__file__).resolve().parents[1]


def load_token() -> str:
    token = os.environ.get("MINERU_ACCESS_TOKEN", "").strip()
    if token:
        return token
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "MINERU_ACCESS_TOKEN":
                return value.strip().strip('"').strip("'")
    raise SystemExit("MINERU_ACCESS_TOKEN not found in .env or environment")


def request_upload_urls(token: str, names: list[str], model: str, language: str) -> tuple[str, list[str]]:
    payload = {
        "files": [{"name": n, "data_id": n} for n in names],
        "model_version": model,
        "language": language,
        "enable_formula": False,
        "enable_table": True,
    }
    resp = requests.post(
        f"{API}/file-urls/batch",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        json=payload,
        timeout=60,
    )
    body = resp.json()
    if resp.status_code != 200 or body.get("code") != 0:
        raise SystemExit(f"request upload urls failed: {resp.status_code} {body}")
    data = body["data"]
    return data["batch_id"], data["file_urls"]


def upload(url: str, path: Path) -> None:
    with path.open("rb") as fh:
        resp = requests.put(url, data=fh, timeout=600)
    if resp.status_code != 200:
        raise SystemExit(f"upload failed for {path.name}: {resp.status_code} {resp.text[:300]}")
    print(f"uploaded {path.name} ({path.stat().st_size / 1e6:.1f} MB)", flush=True)


def poll(token: str, batch_id: str, timeout_s: int) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    deadline = time.time() + timeout_s
    last = ""
    while time.time() < deadline:
        resp = requests.get(f"{API}/extract-results/batch/{batch_id}", headers=headers, timeout=60)
        body = resp.json()
        if resp.status_code != 200 or body.get("code") != 0:
            raise SystemExit(f"poll failed: {resp.status_code} {body}")
        results = body["data"].get("extract_result", [])
        line = " | ".join(
            f"{r.get('file_name')}:{r.get('state')}"
            + (
                f"({r['extract_progress'].get('extracted_pages')}/{r['extract_progress'].get('total_pages')})"
                if r.get("extract_progress")
                else ""
            )
            for r in results
        )
        if line != last:
            print(line, flush=True)
            last = line
        if results and all(r.get("state") in {"done", "failed"} for r in results):
            return results
        time.sleep(10)
    raise SystemExit("timed out waiting for MinerU results")


def download(results: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for r in results:
        name = r.get("file_name", "unknown")
        if r.get("state") != "done":
            print(f"FAILED {name}: {r.get('err_msg')}", flush=True)
            continue
        zip_url = r["full_zip_url"]
        stem = Path(name).stem
        target = out_dir / stem
        target.mkdir(parents=True, exist_ok=True)
        print(f"downloading {name} ...", flush=True)
        raw = requests.get(zip_url, timeout=600)
        raw.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(raw.content)) as zf:
            zf.extractall(target)
        print(f"extracted -> {target}", flush=True)
        for p in sorted(target.rglob("*.md")):
            print(f"  md: {p.name} ({p.stat().st_size / 1024:.0f} KB)", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", help="local PDF/DOCX/PPTX/image files")
    ap.add_argument("--out", default="reference/extracted")
    ap.add_argument("--model", default="vlm", choices=["vlm", "pipeline"])
    ap.add_argument("--language", default="en")
    ap.add_argument("--timeout", type=int, default=3600)
    args = ap.parse_args()

    token = load_token()
    paths = [Path(f).resolve() for f in args.files]
    for p in paths:
        if not p.exists():
            raise SystemExit(f"missing input: {p}")

    batch_id, urls = request_upload_urls(token, [p.name for p in paths], args.model, args.language)
    print(f"batch_id={batch_id}", flush=True)
    for url, path in zip(urls, paths):
        upload(url, path)

    results = poll(token, batch_id, args.timeout)
    out_dir = (ROOT / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
    download(results, out_dir)
    print(json.dumps({"batch_id": batch_id, "out": str(out_dir)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
