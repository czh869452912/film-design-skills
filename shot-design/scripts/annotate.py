#!/usr/bin/env python3
"""Annotate storyboard panels with deterministic labels and arrows.

Image models draw arrows badly and text worse. This script puts them on after
the fact, from data in the shot list, so annotations stay legible, consistent
and re-runnable.

Panel inputs: `<shot_id>.png|jpg|jpeg|webp` in --images.
Overlay data: `shot.storyboard.overlays` (see references/shot-list-spec.md).

Usage:
    python annotate.py shotlist.json --images panels --out annotated
    python annotate.py shotlist.json --images panels --out annotated --sheet sheet.png --cols 2
    python annotate.py shotlist.json --images panels --out annotated --no-arrows
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    raise SystemExit(
        "Pillow is required for annotation. Install it with: python -m pip install pillow"
    )

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
FONT_CANDIDATES = (
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)
INK = (24, 24, 24, 255)
HALO = (255, 255, 255, 235)


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data.get("shots"), list):
        raise SystemExit("shot list needs a 'shots' array")
    return data


def find_panel(images: Path, shot_id: str) -> Path | None:
    for ext in IMAGE_EXTS:
        candidate = images / f"{shot_id}{ext}"
        if candidate.exists():
            return candidate
    return None


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
    return ImageFont.load_default()


def to_px(point, width: int, height: int) -> tuple[float, float]:
    x, y = float(point[0]), float(point[1])
    return x * width, y * height


def bezier(p0, p1, curve: float, steps: int = 28):
    """Quadratic curve whose control point is offset perpendicular to the chord."""
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy) or 1.0
    cx = mx - dy / length * curve * length
    cy = my + dx / length * curve * length
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * cx + t**2 * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * cy + t**2 * p1[1]
        points.append((x, y))
    return points


def arrow_head(draw: ImageDraw.ImageDraw, tip, prev, size: float):
    angle = math.atan2(tip[1] - prev[1], tip[0] - prev[0])
    left = (tip[0] - size * math.cos(angle - 0.45), tip[1] - size * math.sin(angle - 0.45))
    right = (tip[0] - size * math.cos(angle + 0.45), tip[1] - size * math.sin(angle + 0.45))
    draw.polygon([tip, left, right], fill=INK)


def draw_label(draw: ImageDraw.ImageDraw, xy, text: str, font, padding: int = 6):
    box = draw.textbbox((0, 0), text, font=font, stroke_width=2)
    w, h = box[2] - box[0], box[3] - box[1]
    x, y = xy
    draw.rounded_rectangle(
        [x - padding, y - padding, x + w + padding, y + h + padding * 2],
        radius=4,
        fill=HALO,
    )
    draw.text((x, y), text, font=font, fill=INK)


def draw_overlay(draw: ImageDraw.ImageDraw, width: int, height: int, item: dict, font) -> None:
    kind = str(item.get("type", "arrow")).lower()
    label = str(item.get("label", ""))
    scale = max(width, height)

    if kind in ("arrow", "sight", "dashed") and item.get("from") and item.get("to"):
        p0 = to_px(item["from"], width, height)
        p1 = to_px(item["to"], width, height)
        curve = float(item.get("curve", 0.0) or 0.0)
        pts = bezier(p0, p1, curve * 0.5)
        if kind == "sight":
            step = max(2, len(pts) // 18)
            for i in range(0, len(pts), step):
                x, y = pts[i]
                r = max(1.5, scale * 0.003)
                draw.ellipse([x - r, y - r, x + r, y + r], fill=INK)
        else:
            draw.line(pts, fill=INK, width=max(2, int(scale * 0.006)), joint="curve")
            arrow_head(draw, pts[-1], pts[-2], max(8, scale * 0.022))
        if label:
            anchor = pts[len(pts) // 2]
            draw_label(draw, (anchor[0] + 8, anchor[1] - 8), label, font)

    elif kind == "impact" and item.get("at"):
        cx, cy = to_px(item["at"], width, height)
        r0 = scale * 0.01
        r1 = scale * (float(item.get("size", 0.06)) or 0.06)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            draw.line(
                [(cx + r0 * math.cos(rad), cy + r0 * math.sin(rad)),
                 (cx + r1 * math.cos(rad), cy + r1 * math.sin(rad))],
                fill=INK,
                width=max(2, int(scale * 0.005)),
            )
        if label:
            draw_label(draw, (cx + r1 * 0.6, cy + r1 * 0.4), label, font)

    elif kind == "orbit" and item.get("at"):
        cx, cy = to_px(item["at"], width, height)
        radius = scale * (float(item.get("radius", 0.2)) or 0.2)
        start = float(item.get("start", -140))
        end = float(item.get("end", -20))
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        draw.arc(bbox, start=start, end=end, fill=INK, width=max(2, int(scale * 0.006)))
        tip = (cx + radius * math.cos(math.radians(end)), cy + radius * math.sin(math.radians(end)))
        prev = (cx + radius * math.cos(math.radians(end - 4)), cy + radius * math.sin(math.radians(end - 4)))
        arrow_head(draw, tip, prev, max(8, scale * 0.022))
        if label:
            draw_label(draw, (cx + radius * 0.4, cy - radius - 28), label, font)


def annotate_panel(path: Path, shot: dict, index: int, show_arrows: bool) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    width, height = image.size
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    base = min(width, height)
    font = load_font(max(16, int(base * 0.042)))

    framing = shot.get("framing") or {}
    size = str(framing.get("size", "")).strip()
    angle = str(framing.get("angle", "")).strip()
    duration = float(shot.get("duration_s") or 0)
    label = f"{shot.get('id', f'S{index:02d}')} · {size} · {angle} · {duration:.1f}s"
    draw_label(draw, (base * 0.035, base * 0.035), label, font)

    panel = shot.get("storyboard") or {}
    if show_arrows:
        for item in panel.get("overlays") or []:
            if isinstance(item, dict):
                draw_overlay(draw, width, height, item, font)

    return Image.alpha_composite(image, overlay).convert("RGB")


def compose_sheet(panels: list[tuple[str, Image.Image]], cols: int) -> Image.Image:
    if not panels:
        raise SystemExit("no panels to compose")
    cell_w = 640
    cell_h = int(round(cell_w * panels[0][1].height / panels[0][1].width))
    rows = math.ceil(len(panels) / cols)
    gutter, caption_h = 16, 28
    sheet_w = cols * cell_w + (cols + 1) * gutter
    sheet_h = rows * (cell_h + caption_h) + (rows + 1) * gutter
    sheet = Image.new("RGB", (sheet_w, sheet_h), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    font = load_font(20)
    for i, (shot_id, panel) in enumerate(panels):
        r, c = divmod(i, cols)
        x = gutter + c * (cell_w + gutter)
        y = gutter + r * (cell_h + caption_h + gutter)
        sheet.paste(panel.resize((cell_w, cell_h), Image.LANCZOS), (x, y))
        draw.text((x + 4, y + cell_h + 4), shot_id, font=font, fill=(30, 30, 30))
    return sheet


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("shotlist")
    ap.add_argument("--images", required=True, help="directory with <shot_id> panel images")
    ap.add_argument("--out", required=True, help="directory for annotated panels")
    ap.add_argument("--sheet", default=None, help="optional contact sheet path")
    ap.add_argument("--cols", type=int, default=2)
    ap.add_argument("--no-arrows", action="store_true")
    args = ap.parse_args()

    data = load(Path(args.shotlist))
    images = Path(args.images)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    panels: list[tuple[str, Image.Image]] = []
    missing: list[str] = []
    for index, shot in enumerate(data["shots"], start=1):
        shot_id = str(shot.get("id") or f"S{index:02d}")
        source = find_panel(images, shot_id)
        if source is None:
            missing.append(shot_id)
            continue
        annotated = annotate_panel(source, shot, index, not args.no_arrows)
        target = out_dir / f"{shot_id}.png"
        annotated.save(target)
        written.append(str(target))
        panels.append((shot_id, annotated))

    if args.sheet and panels:
        sheet = compose_sheet(panels, max(1, args.cols))
        sheet.save(args.sheet)
        print(f"sheet: {args.sheet} ({sheet.width}x{sheet.height})")

    print(f"annotated: {len(written)} panels -> {out_dir}")
    if missing:
        print(f"missing panels: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
