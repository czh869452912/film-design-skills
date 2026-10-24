from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TIMES = ["0", "2", "4", "5.2", "6.6", "9.5"]
ROWS = [
    ("baseline v1", "duel-test/judge2/A1"),
    ("baseline v2", "duel-test/judge2/A2"),
    ("skill v1", "duel-test/judge2/B1"),
    ("skill v2", "duel-test/judge2/B2"),
]
CELL_W, CELL_H, PAD, LABEL = 280, 160, 6, 22
font_path = Path("C:/Windows/Fonts/arial.ttf")
font = ImageFont.truetype(str(font_path), 14) if font_path.exists() else ImageFont.load_default()

width = 130 + len(TIMES) * (CELL_W + PAD) + PAD
height = len(ROWS) * (CELL_H + LABEL + PAD) + PAD
sheet = Image.new("RGB", (width, height), (245, 245, 245))
draw = ImageDraw.Draw(sheet)

for row, (label, folder) in enumerate(ROWS):
    y = PAD + row * (CELL_H + LABEL + PAD)
    draw.text((PAD + 4, y + CELL_H // 2), label, fill=(20, 20, 20), font=font)
    for col, t in enumerate(TIMES):
        x = PAD + 130 + col * (CELL_W + PAD)
        image = Image.open(Path(folder) / f"f_{t}.png").resize((CELL_W, CELL_H), Image.LANCZOS)
        sheet.paste(image, (x, y))
        draw.text((x + 2, y + CELL_H + 3), f"{t}s", fill=(40, 40, 40), font=font)

sheet.save("duel-test/previs-comparison.png")
print(sheet.size)
