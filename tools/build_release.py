#!/usr/bin/env python3
"""Build a reproducible, model-independent five-skill ZIP and SHA256 manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ('film-direction', 'shot-design', 'keyframe-design', 'screen-media', 'animatic-review')


def build(out: Path) -> Path:
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('VERSION must contain a semantic release version')
    entries: dict[str, bytes] = {}
    for name in SKILLS:
        folder = ROOT / name
        for required in ('SKILL.md', 'agents/openai.yaml', 'LICENSE', 'NOTICE'):
            if not (folder / required).is_file():
                raise ValueError(f'{name}: missing {required}')
        for path in sorted(folder.rglob('*')):
            if '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            if path.is_symlink():
                raise ValueError(f'symlinks are not packaged: {path}')
            if not path.is_file():
                continue
            if path.name not in ('LICENSE', 'NOTICE') and path.suffix not in ('.md', '.py', '.json', '.yaml'):
                raise ValueError(f'unexpected skill file: {path}')
            entries[path.relative_to(ROOT).as_posix()] = path.read_bytes().replace(b'\r\n', b'\n')
    for name in ('LICENSE', 'NOTICE', 'VERSION', 'requirements.txt'):
        entries[name] = (ROOT / name).read_bytes().replace(b'\r\n', b'\n')
    entries['INSTALL.md'] = ('''# Film Design Skills

Copy the five skill folders into the same skill directory supported by your host.
Back up local edits before replacing an older installation. Each skill can also be used separately.
Start with `$film-direction` for creative collaboration or enter another skill for existing work.

- film-direction: develop cinematic expression with the creator.
- shot-design: blocking, framing, composition and shot sequence.
- keyframe-design: layout, key poses and drawable keyframes.
- screen-media: use the creator's available image and video models.
- animatic-review: timing, sound, editing and review of actual results.

Design work requires no provider account. Optional local tools use Python 3.10+;
install requirements.txt for image tools, and FFmpeg/FFprobe for media tools.
Run `python shot-design/scripts/selftest.py --verbose` to check the local tools.
No API client, credentials, reference books, research corpus or generated media is bundled.
MANIFEST.json lists SHA256 hashes. Tool validation does not establish artistic quality.
''').encode('utf-8')
    manifest = {'version': version, 'skills': list(SKILLS),
                'files': {name: hashlib.sha256(data).hexdigest() for name, data in sorted(entries.items())}}
    entries['MANIFEST.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    out.mkdir(parents=True, exist_ok=True)
    archive = out / f'film-design-skills-v{version}.zip'
    if archive.exists() or archive.with_suffix('.zip.sha256').exists():
        raise ValueError(f'release output already exists: {archive}')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, data)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(f'{digest}  {archive.name}\n', encoding='utf-8')
    print(f'{archive}: {len(manifest["files"])} files + manifest; SHA256 {digest}')
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    try:
        build(args.out)
    except (ValueError, OSError) as error:
        parser.exit(1, f'{error}\n')
