#!/usr/bin/env python3
"""Offline regression tests. Media tests verify real frame order/count, not art quality."""
from __future__ import annotations
import argparse
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
EXAMPLES = SKILL / 'examples'
LEGACY = SKILL.parent / 'tests' / 'fixtures' / 'legacy'
import shotlist
from sequence import iter_panels, normalize, resolve_image, shot_duration, validate


def run(script, *args, ok=True):
    result = subprocess.run([sys.executable, str(HERE / script), *map(str, args)],
                            capture_output=True, text=True, encoding='utf-8', errors='replace',
                            env={**__import__('os').environ, 'PYTHONIOENCODING':'utf-8'})
    if (result.returncode == 0) != ok:
        raise AssertionError(f'{script} exit {result.returncode}: {result.stdout[-500:]} {result.stderr[-1000:]}')
    return result


def read(name):
    return json.loads((EXAMPLES / name).read_text(encoding='utf-8-sig'))


def test_examples():
    count = 0
    for path in [*EXAMPLES.glob('*.json'), *LEGACY.glob('*.json')]:
        run('shotlist.py', 'validate', path, '--strict', '--timed')
        count += 1
    return f'{count} new and legacy examples'


def test_formats():
    paths = [EXAMPLES / name for name in ['cup-handoff.json', 'duel-basic.json', 'display-montage.json']]
    if (LEGACY / 'descent.json').exists():
        paths.append(LEGACY / 'descent.json')
    for path in paths:
        for fmt in shotlist.RENDERERS:
            result = run('shotlist.py', 'render', path, '--format', fmt, '--quiet')
            assert len(result.stdout.strip()) > 20, (name, fmt)
    assert len(shotlist.load_mechanisms()) == 42
    run('inventory.py', EXAMPLES)
    return f'{len(paths)*len(shotlist.RENDERERS)} render paths; 42 mechanism IDs; corpus integrity'


def test_drafts():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'draft.json'
        run('shotlist.py', 'init', path)
        data = json.loads(path.read_text(encoding='utf-8'))
        assert 'beats' not in data and 'target' not in data
        assert shot_duration(data['shots'][0]) is None
        run('shotlist.py', 'validate', path, '--strict')
        run('shotlist.py', 'validate', path, '--timed', ok=False)
        for fmt in shotlist.RENDERERS:
            run('shotlist.py', 'render', path, '--format', fmt, '--quiet')
        run('shotlist.py', 'init', path, ok=False)
    return 'untimed draft round trip; timed gate; no overwrite'


def test_associations():
    cup = read('cup-handoff.json')
    assert len(cup['shots']) == 1 and len(list(iter_panels(cup))) == 4
    assert shot_duration(cup['shots'][0]) == 6
    duel = read('duel-basic.json')
    assert len(duel['shots']) == 3 and len(list(iter_panels(duel))) == 8
    assert sum(shot_duration(s) for s in duel['shots']) == 10
    assert duel['shots'][0]['beat_ids'][0] in duel['shots'][1]['beat_ids']
    assert len(duel['shots'][1]['beat_ids']) == 2
    montage = read('display-montage.json')
    assert shotlist.check(montage) == ([], [])
    assert 'beats' not in montage
    assert len(normalize(montage)['shots'][0]['panels']) == 1
    return 'single-shot action, many-to-many beats, equal montage and legacy panels'


def test_invalid():
    base = read('cup-handoff.json')
    cases = []
    for duration in [0, -1, True, '1', float('nan'), float('inf')]:
        d = copy.deepcopy(base); d['shots'][0]['panels'][0]['duration_s'] = duration; cases.append(d)
    for value in [None, '', {}, [], ['invalid']]:
        d = copy.deepcopy(base); d['shots'][0]['panels'] = value; cases.append(d)
    for field, value in [('id', '../outside'), ('beat_ids', ['unknown']), ('duration_s', 999), ('framing', {'options':['bad']})]:
        d = copy.deepcopy(base); d['shots'][0][field] = value; cases.append(d)
    d = copy.deepcopy(base); d['shots'][0]['panels'][1]['id'] = d['shots'][0]['panels'][0]['id']; cases.append(d)
    d = copy.deepcopy(base); d['shots'][0]['panels'][0]['overlays'] = [{'type':'arrow','from':[2,0],'to':[0,1]}]; cases.append(d)
    d = copy.deepcopy(base); d['target']['duration_s'] = 9; cases.append(d)
    for d in cases:
        errors, _ = validate(d)
        assert errors, d
    # Notes cannot certify contradictory content. The script must not emit a quality score.
    d = read('display-montage.json')
    d['shots'][0]['action']['primary'] = 'A exits screen right holding a red cup.'
    d['shots'][1]['action']['primary'] = 'A enters screen right holding a blue cup.'
    report = shotlist.render_cuts(d)
    assert '/100' not in report and 'not assessed' in report
    return f'{len(cases)} invalid structures rejected; conflicting prose not certified'


def media_fixture(tmp):
    from PIL import Image
    colors = [(220,30,30),(30,210,30),(30,30,220),(220,180,30)]
    ids = ['S01-P01','S01-P02','S01-P03','S02-P01']
    panels = []
    for pid, duration, color in zip(ids,[.13,.23,.31,.33],colors):
        Image.new('RGB',(160,96),color).save(tmp / f'{pid}.png')
        panels.append({'id':pid,'description':f'visible state {pid}','duration_s':duration})
    data = {'shots':[{'id':'S01','panels':panels[:3]},{'id':'S02','panels':panels[3:]}]}
    path = tmp / 'plan.json'
    path.write_text(json.dumps(data),encoding='utf-8')
    return path, data, colors


def test_image_paths_and_refs():
    from PIL import Image
    with tempfile.TemporaryDirectory() as folder:
        tmp = Path(folder)
        path, data, _ = media_fixture(tmp)
        custom = tmp / 'custom.png'
        Image.new('RGB',(160,96),(0,0,0)).save(custom)
        panel = {'id':'S01-P01','image':'custom.png'}
        assert resolve_image(panel,base=tmp) == custom
        assert resolve_image(panel,base=tmp,images=tmp) == tmp / 'S01-P01.png'
        run('annotate.py', path, '--out', tmp/'annotated', '--sheet', tmp/'sheet.png')
        assert len(list((tmp/'annotated').glob('*.png'))) == 4
        with Image.open(tmp/'sheet.png') as sheet:
            assert sheet.width > 1000 and sheet.height > 700
        run('build_refpack.py', path, '--out', tmp/'refs', '--select','S02-P01')
        manifest = json.loads((tmp/'refs/manifest.json').read_text(encoding='utf-8'))
        item = manifest['pictures'][0]
        assert (item['reference_id'],item['shot_index'],item['panel']) == ('R01',2,'S02-P01')
        run('build_refpack.py', path, '--out', tmp/'bad', '--select','S02-P01','--first-frame',ok=False)
        (tmp/'S01-P02.png').unlink()
        run('annotate.py', path, '--out', tmp/'missing',ok=False)
        assert not (tmp/'missing').exists()
        run('build_refpack.py', path, '--out', tmp/'partial', '--allow-missing')
        manifest = json.loads((tmp/'partial/manifest.json').read_text(encoding='utf-8'))
        assert not manifest['complete'] and manifest['missing_panels'] == ['S01-P02']
    return 'real annotation; explicit paths; reference index preserved; missing image preflight'


def test_animatic():
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        return 'SKIP: ffmpeg/ffprobe unavailable'
    with tempfile.TemporaryDirectory() as folder:
        tmp = Path(folder)
        path, data, colors = media_fixture(tmp)
        movie = tmp / 'test.mp4'
        audio = tmp / 'short.wav'
        with wave.open(str(audio), 'wb') as track:
            track.setnchannels(1)
            track.setsampwidth(2)
            track.setframerate(48000)
            track.writeframes(b'\0\0' * 4800)
        run('animatic.py', path, '--out', movie, '--size','160x96','--fps','24','--no-labels','--require-images','--audio',audio)
        edl = json.loads(movie.with_suffix('.edl.json').read_text(encoding='utf-8'))
        assert len(edl['shots']) == 2 and len(edl['panels']) == 4
        assert [p['frame_count'] for p in edl['panels']] == [3,6,7,8]
        assert edl['shots'][0]['panel_ids'] == ['S01-P01','S01-P02','S01-P03']
        probe = subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames','-of','json',str(movie)],capture_output=True,check=True)
        assert int(json.loads(probe.stdout)['streams'][0]['nb_read_frames']) == 24
        decoded = subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-map','0:v:0','-pix_fmt','rgb24','-f','rawvideo','-'],capture_output=True,check=True).stdout
        stride = 160*96*3
        assert len(decoded) == stride * 24
        for panel, expected in zip(edl['panels'],colors):
            n = panel['start_frame'] + panel['frame_count']//2
            pixel = n*stride + (48*160+80)*3
            actual = decoded[pixel:pixel+3]
            assert max(abs(a-b) for a,b in zip(actual,expected)) < 12, (actual,expected)
        (tmp/'S01-P02.png').unlink()
        run('animatic.py',path,'--out',tmp/'missing.mp4','--require-images',ok=False)
        assert not (tmp/'missing.mp4').exists()
    return 'decoded 24 frames in correct order; 2 shot groups; short audio padded to runtime'




def test_review_boards():
    from PIL import Image, ImageDraw
    from board import compose
    with tempfile.TemporaryDirectory() as folder:
        tmp = Path(folder)
        path, data, colors = media_fixture(tmp)
        shapes = [(160, 40), (40, 96), (160, 96), (160, 96)]
        panels = list(iter_panels(data))
        originals = {}
        for panel, size, color in zip(panels, shapes, colors):
            image = Image.new('RGB', size, color)
            draw = ImageDraw.Draw(image)
            draw.point((0, 0), fill='white')
            draw.point((size[0]-1, size[1]-1), fill='black')
            source = tmp / (panel['id'] + '.png')
            image.save(source)
            originals[source] = source.read_bytes()
        out = tmp / 'board.png'
        run('board.py', path, '--out', out, '--columns', 3,
            '--cell-width', 160, '--cell-height', 96)
        result = json.loads(out.with_suffix('.json').read_text(encoding='utf-8'))
        assert len(result['panels']) == 4 and result['rows'] == 2
        assert not result['content_reviewed']
        assert [p['shot_id'] for p in result['panels']] == ['S01']*3 + ['S02']
        sheet = Image.open(out)
        for entry, shape, color in zip(result['panels'], shapes, colors):
            x0, y0, x1, y1 = entry['image_box']
            assert (x1-x0, y1-y0) == shape
            assert sheet.getpixel((x0, y0)) == (255, 255, 255)
            assert sheet.getpixel((x1-1, y1-1)) == (0, 0, 0)
            assert sheet.getpixel(((x0+x1)//2, (y0+y1)//2)) == color
        for source, original in originals.items():
            assert source.read_bytes() == original
        run('board.py', path, '--out', out, ok=False)
        try:
            compose(path, tmp/'huge.png', cell_width=100000, cell_height=100000)
        except ValueError as error:
            assert 'million pixels' in str(error)
        else:
            raise AssertionError('oversized board accepted')
        (tmp / (panels[0]['id'] + '.png')).unlink()
        missing = tmp / 'missing.png'
        run('board.py', path, '--out', missing, ok=False)
        assert not missing.exists() and not missing.with_suffix('.json').exists()
    return 'mixed aspect ratios uncropped; shot IDs retained; source bytes preserved; missing/overwrite rejected'


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--verbose',action='store_true')
    args=ap.parse_args()
    tests=[test_examples,test_formats,test_drafts,test_associations,test_invalid,test_image_paths_and_refs,test_animatic,test_review_boards]
    failures, skipped=0,0
    for test in tests:
        try:
            detail=test()
            if detail.startswith('SKIP'):
                skipped+=1
            print(('SKIP' if detail.startswith('SKIP') else 'PASS')+' '+test.__name__+(f': {detail}' if args.verbose else ''))
        except Exception as error:
            failures+=1
            print(f'FAIL {test.__name__}: {type(error).__name__}: {error}')
    print(f'{len(tests)-failures-skipped} passed, {failures} failed, {skipped} skipped; film quality not assessed')
    return bool(failures)


if __name__=='__main__':
    sys.exit(main())
