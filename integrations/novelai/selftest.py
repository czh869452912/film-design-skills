"""Offline regressions for the optional NovelAI page compiler and measured cropper."""
import copy
import json
import sys
import tempfile
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'shot-design' / 'scripts'))
EXAMPLES = ROOT / 'shot-design' / 'examples'

def read(name):
    return json.loads((EXAMPLES / name).read_text(encoding='utf-8-sig'))


def test_pageboards():
    from PIL import Image, ImageDraw
    from pageboard import compile_page, crop_page, digest
    data = read('cup-handoff.json')
    plan = {'page_id': 'cup', 'columns': 2, 'rows': 2, 'width': 128, 'height': 128,
            'style': 'lineart', 'global_prompt': '2girls, same room', 'negative': '',
            'characters': {'A': {'appearance': 'girl, red coat'}, 'B': {'appearance': 'girl, blue coat'}},
            'panels': [{'panel_id': p['id'], 'shot_id': 'S01', 'summary': p['description'],
                        'instances': [{'character_id': cid, 'prompt': str(i), 'local_center': [x,.5]}
                                      for cid, x in [('A',.25),('B',.75)]]}
                       for i,p in enumerate(data['shots'][0]['panels'])]}
    built = compile_page(plan, data)
    assert len(built['characters']) == 8
    assert built['characters'][0]['centers'] == [{'x':.125,'y':.25}]
    assert built['characters'][-1]['centers'] == [{'x':.875,'y':.75}]
    assert built['characters'][0]['prompt'] == 'girl, red coat, 0'
    assert built['characters'][2]['prompt'] == 'girl, red coat, 1'
    for mutate in [lambda p:p.update(rows=3), lambda p:p['panels'][0].update(shot_id='S99'),
                   lambda p:p['panels'][0]['instances'][0].update(local_center=[float('nan'),.5])]:
        bad = copy.deepcopy(plan); mutate(bad)
        try:
            compile_page(bad, data)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid page accepted')
    large = copy.deepcopy(plan)
    large.update(columns=3, rows=4)
    large['panels'] = [dict(copy.deepcopy(plan['panels'][i%4]), panel_id=f'P{i}') for i in range(12)]
    try:
        compile_page(large)
    except ValueError as error:
        assert '22' in str(error)
    else:
        raise AssertionError('24 occurrence slots accepted')
    with tempfile.TemporaryDirectory() as folder:
        tmp = Path(folder)
        image = Image.new('RGB',(128,128),'white')
        colors = ['red','green','blue','yellow']
        boxes = [[3,2,61,59],[66,2,125,59],[3,66,61,126],[66,66,125,126]]
        draw = ImageDraw.Draw(image)
        for box,color in zip(boxes,colors):
            draw.rectangle([box[0],box[1],box[2]-1,box[3]-1],fill=color)
        image.save(tmp/'page.png')
        review = {'image':'page.png', 'image_sha256':digest(tmp/'page.png'), 'layout_reviewed':True,
                  'panels':[{'panel_id':p['panel_id'], 'box':box, 'content_approved':i!=2,
                             'observation':'actual picture reviewed'}
                            for i,(p,box) in enumerate(zip(plan['panels'],boxes))]}
        original = (tmp/'page.png').read_bytes()
        for mutate in [lambda r:r.update(layout_reviewed=False), lambda r:r.update(image_sha256='stale'),
                       lambda r:r['panels'][0].update(box=[-1,0,61,59]),
                       lambda r:r['panels'][1].update(box=boxes[0])]:
            bad = copy.deepcopy(review); mutate(bad)
            try:
                crop_page(bad,built['layout'],tmp/'review.json',tmp/'rejected')
            except ValueError:
                pass
            else:
                raise AssertionError('invalid crop accepted')
            assert not (tmp/'rejected').exists()
        result = crop_page(review,built['layout'],tmp/'review.json',tmp/'crops')
        assert not result['all_content_approved'] and result['layout_reviewed']
        assert [p['shot_id'] for p in result['panels']] == ['S01']*4
        for entry,color in zip(result['panels'],colors):
            crop = Image.open(tmp/'crops'/entry['image'])
            assert crop.getpixel((0,0)) == Image.new('RGB',(1,1),color).getpixel((0,0))
            assert crop.size == (entry['box'][2]-entry['box'][0],entry['box'][3]-entry['box'][1])
        assert (tmp/'page.png').read_bytes() == original
    return 'per-occurrence identity/state and global coordinates; measured crops; source preserved; content gate separate'


if __name__ == '__main__':
    print('PASS test_pageboards: ' + test_pageboards())
