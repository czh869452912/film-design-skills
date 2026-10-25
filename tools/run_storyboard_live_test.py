"""Run a saved panel manifest through the existing NovelAI CLI, once per job.

Credentials remain inside that client. Completed jobs are never resubmitted.
The manifest and result ledger contain prompts/paths/status, no credentials.
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest', type=Path)
    ap.add_argument('--limit', type=int)
    args = ap.parse_args()
    spec = json.loads(args.manifest.read_text(encoding='utf-8'))
    ledger_path = args.manifest.with_name('generation-ledger.json')
    ledger = json.loads(ledger_path.read_text(encoding='utf-8')) if ledger_path.exists() else []
    jobs = spec['jobs'][:args.limit] if args.limit else spec['jobs']
    for job in jobs:
        raw = Path(job['out'])
        source, final = raw / 'image_0.png', Path(job['final'])
        if not source.exists():
            if any(entry['panel_id'] == job['panel_id'] for entry in ledger):
                raise SystemExit(f"Prior attempt exists for {job['panel_id']}; inspect it rather than retrying")
            cmd = [sys.executable, '.dsh/skills/novelai-image/scripts/nai.py', 'generate',
                   '--prompt-file', job['prompt'], '--negative-file', spec['negative'],
                   '--characters', job['characters'], '--width', str(spec['width']),
                   '--height', str(spec['height']), '--steps', str(spec['steps']),
                   '--seed', str(job['seed']), '--out', str(raw)]
            if job.get('image'):
                cmd += ['--image', job['image'], '--strength', str(job.get('strength', 0.6))]
            start = time.monotonic()
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            entry = dict(panel_id=job['panel_id'], seed=job['seed'], exit_code=result.returncode,
                         elapsed_s=round(time.monotonic()-start, 2), output=result.stdout.strip())
            ledger.append(entry)
            ledger_path.write_text(json.dumps(ledger, indent=2)+'\n', encoding='utf-8')
            print(f"{job['panel_id']}: {result.stdout.strip()}", flush=True)
            if result.returncode or not source.exists():
                raise SystemExit('Generation stopped; no automatic retry')
        final.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, final)
    return 0


if __name__ == '__main__':
    sys.exit(main())
