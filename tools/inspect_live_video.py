"""Extract timed review pages and metadata from an actual generated clip."""
from __future__ import annotations
import argparse
import json
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('video', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--fps', type=int, default=8)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                            '-of', 'json', str(args.video)], capture_output=True, check=True)
    meta = json.loads(probe.stdout)
    (args.out/'metadata.json').write_text(json.dumps(meta, indent=2)+'\n', encoding='utf-8')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(args.video),
                    '-vf', f'fps={args.fps},scale=640:-2', '-q:v', '3',
                    str(args.out/'f_%04d.jpg')], check=True)
    files = sorted(args.out.glob('f_*.jpg'))
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
    def pages(items, label):
        cell_w, cell_h, caption, cols, limit = 384, 216, 30, 3, 12
        for start in range(0, len(items), limit):
            part = items[start:start+limit]
            sheet = Image.new('RGB', (cols*cell_w, math.ceil(len(part)/cols)*(cell_h+caption)), 'white')
            draw = ImageDraw.Draw(sheet)
            for j, (idx, path) in enumerate(part):
                x, y = j%cols*cell_w, j//cols*(cell_h+caption)
                with Image.open(path) as frame:
                    sheet.paste(frame.resize((cell_w,cell_h)), (x,y))
                draw.text((x+8,y+cell_h+4),f'~{idx/args.fps:.3f} s',fill='black',font=font)
            sheet.save(args.out/f'{label}-{start//limit+1}.jpg', quality=94)
    indexed = list(enumerate(files))
    pages(indexed[::max(1,args.fps//2)], 'overview')
    pages(indexed, 'dense')
    print(json.dumps({'duration_s':meta['format']['duration'],'sampled_frames':len(files),
                      'sampling_fps':args.fps,'output':str(args.out)}))


if __name__ == '__main__':
    main()
