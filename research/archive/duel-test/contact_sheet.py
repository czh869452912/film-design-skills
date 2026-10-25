from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TIMES = ["0", "2", "4", "5.2", "6.6", "9.5"]
ROWS = [("X  baseline", "duel-test/judge/x"), ("Y  skill", "duel-test/judge/y")]
CELL_W, CELL_H, PAD, LABEL = 336, 192, 8, 26

font_path = Path("C:/Windows/Fonts/arial.ttf")
font = ImageFont.truetype(str(font_path), 16) if font_path.exists() else ImageFont.load_default()

width = len(TIMES) * (CELL_W + PAD) + PAD + 150
height = len(ROWS) * (CELL_H + LABEL + PAD) + PAD
sheet = Image.new("RGB", (width, height), (245, 245, 245))
draw = ImageDraw.Draw(sheet)

for row, (label, folder) in enumerate(ROWS):
    y = PAD + row * (CELL_H + LABEL + PAD)
    draw.text((PAD, y + CELL_H // 2), label, fill=(20, 20, 20), font=font)
    for col, time_label in enumerate(TIMES):
        x = PAD + 150 + col * (CELL_W + PAD)
        image = Image.open(Path(folder) / f"f_{time_label}.png").resize((CELL_W, CELL_H), Image.LANCZOS)
        sheet.paste(image, (x, y))
        draw.text((x + 4, y + CELL_H + 4), f"{time_label}s", fill=(40, 40, 40), font=font)

sheet.save("duel-test/contact-sheet.png")
print(sheet.size)
