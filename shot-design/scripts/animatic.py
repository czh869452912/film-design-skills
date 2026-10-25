#!/usr/bin/env python3
"""Build a simple animatic (timed previz clip) from storyboard panels.

Renders timed panels, preserving continuous-shot groups in the EDL.
Supports legacy one-image-per-shot plans. Missing drawings are explicit
placeholders unless --require-images is used. Output is not visual approval.

Options: fade at shot boundaries (`--transition fade`), an external audio track
(`--audio`), label position, size and fps.

Usage:
    python animatic.py shotlist.json --images storyboard --out animatic/animatic.mp4
    python animatic.py shotlist.json --images annotated --out out.mp4 --transition fade --audio scratch.wav
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
from sequence import iter_panels, load, require_valid, resolve_image

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
DEFAULT_FONT = "Arial" if sys.platform.startswith("win") else None


def size_from_aspect(aspect: str) -> tuple[int, int]:
    try:
        w, h = (float(part) for part in aspect.split(":"))
    except (ValueError, AttributeError):
        return 1344, 768
    if not all(math.isfinite(v) and v > 0 for v in (w, h)):
        return 1344, 768
    height = 768
    width = int(round(height * w / h / 2)) * 2
    return width, height


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr[-2000:])
        raise SystemExit(f"ffmpeg failed: {' '.join(cmd[:6])} ...")


def render_segment(src: Path | None, shot_id: str, duration: float, width: int, height: int,
                   out: Path, labels: bool, font: str | None, fps: int,
                   transition: str = "none", label_position: str = "top-left",
                   fade_in: bool = True, fade_out: bool = True) -> None:
    """Render one panel as a video segment of exactly `duration` seconds.

    Fades must be applied to the segment, not to the still: a still has a single
    frame, so fading it produces a black image that then gets repeated.
    """
    vf = [
        f"scale={width}:{height}:force_original_aspect_ratio=decrease",
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0xE8E8E8",
        "format=yuv420p",
    ]
    if labels:
        text = f"{shot_id}  {duration:.1f}s"
        if label_position == "bottom-right":
            x, y = "w-tw-24", "h-th-24"
        else:
            x, y = "24", "20"
        draw = (
            f"drawtext=text='{text}':x={x}:y={y}:fontsize=28:fontcolor=black"
            ":box=1:boxcolor=white@0.75:boxborderw=8"
        )
        if font:
            # use a font *name*: fontfile= cannot parse the Windows drive colon in this build
            draw = draw.replace("drawtext=", f"drawtext=font={font}:", 1)
        vf.append(draw)

    if transition == "fade" and duration > 0.5:
        fade = min(0.25, duration / 4)
        if fade_in:
            vf.append(f"fade=t=in:st=0:d={fade:.2f}")
        if fade_out:
            vf.append(f"fade=t=out:st={duration - fade:.2f}:d={fade:.2f}")

    cmd = ["ffmpeg", "-v", "error", "-y"]
    if src is None:
        cmd += ["-f", "lavfi", "-i", f"color=c=0xBDBDBD:s={width}x{height}"]
    else:
        cmd += ["-loop", "1", "-i", str(src)]
    cmd += [
        "-frames:v", str(round(duration * fps)),
        "-vf", ",".join(vf),
        "-r", str(fps),
        "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        str(out),
    ]
    run(cmd)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("shotlist")
    ap.add_argument("--images", default=None, help="directory holding panel images")
    ap.add_argument("--out", default="animatic/animatic.mp4")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--size", default=None, help="WxH; defaults to 768p for the declared aspect")
    ap.add_argument("--no-labels", action="store_true")
    ap.add_argument("--font", default=None, help="fontconfig font name for labels (default Arial on Windows)")
    ap.add_argument("--label-position", default="top-left", choices=["top-left", "bottom-right"])
    ap.add_argument("--transition", default="none", choices=["none", "fade"],
                    help="fade at shot boundaries; internal panels remain continuous")
    ap.add_argument("--audio", default=None, help="optional audio track (mp3/wav/m4a) trimmed to the runtime")
    ap.add_argument("--require-images", action="store_true", help="fail if any panel drawing is absent")
    args = ap.parse_args()

    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg not found on PATH")

    plan_path = Path(args.shotlist)
    data = load(plan_path)
    require_valid(data, timed=True)
    if args.fps <= 0:
        raise SystemExit("fps must be positive")
    target = data.get("target") or {}
    style = data.get("style") or {}
    aspect = style.get("aspect") or target.get("aspect") or "16:9"
    width, height = size_from_aspect(aspect)
    if args.size:
        try:
            width, height = (int(part) for part in args.size.lower().split("x"))
        except ValueError:
            raise SystemExit("--size must look like 1344x768")

    images = Path(args.images) if args.images else None
    panels = list(iter_panels(data))
    sources = [resolve_image(p, images=images, base=plan_path.parent) for p in panels]
    if args.require_images and any(p is None for p in sources):
        raise SystemExit("missing panels: " + ", ".join(p['id'] for p, src in zip(panels, sources) if src is None))
    if width <= 0 or height <= 0 or width % 2 or height % 2:
        raise SystemExit("video size must have positive even dimensions")
    font = args.font if args.font else DEFAULT_FONT
    labels = not args.no_labels

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    planned_total = sum(p['duration_s'] for p in panels)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        concat_lines: list[str] = []
        edl: list[dict] = []
        cursor = 0.0
        planned_cursor = 0.0
        frame_cursor = 0

        for index, (shot, src) in enumerate(zip(panels, sources), start=1):
            shot_id = shot['shot_id']
            panel_id = shot['id']
            planned_duration = shot['duration_s']
            planned_cursor += planned_duration
            end_frame = round(planned_cursor * args.fps)
            frame_count = end_frame - frame_cursor
            if frame_count < 1:
                raise SystemExit(f"{panel_id}: timing is shorter than a frame at {args.fps}fps")
            duration = frame_count / args.fps
            segment = tmp_dir / f"{index:03d}_{panel_id}.mp4"
            render_segment(
                src, f"{shot_id}/{panel_id}", duration, width, height, segment, labels, font, args.fps,
                transition=args.transition, label_position=args.label_position,
                fade_in=shot['shot_start'],
                fade_out=index == len(panels) or panels[index]['shot_start'],
            )
            concat_lines.append(f"file '{segment.as_posix()}'")
            edl.append(
                {
                    "shot_id": shot_id,
                    "panel_id": panel_id,
                    "shot_start": shot['shot_start'],
                    "start_s": round(cursor, 3),
                    "duration_s": round(duration, 3),
                    "planned_duration_s": planned_duration,
                    "start_frame": frame_cursor,
                    "frame_count": frame_count,
                    "panel": str(src) if src else None,
                    "placeholder": src is None,
                    "beat_ids": shot.get("beat_ids", []),
                }
            )
            cursor += duration
            frame_cursor = end_frame

        concat_file = tmp_dir / "concat.txt"
        concat_file.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")

        cmd = [
            "ffmpeg", "-v", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
        ]
        if args.audio:
            audio_path = Path(args.audio)
            if not audio_path.exists():
                raise SystemExit(f"audio not found: {audio_path}")
            cmd += ["-i", str(audio_path)]
        else:
            cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        cmd += [
            "-map", "0:v:0", "-map", "1:a:0",
            "-t", f"{cursor:.3f}",
            "-c:v", "copy",
            "-af", "apad",
            "-c:a", "aac", "-b:a", "96k", "-shortest",
            str(out_path),
        ]
        run(cmd)

    edl_path = out_path.with_suffix(".edl.json")
    edl_path.write_text(
        json.dumps(
            {
                "title": data.get("title"),
                "size": f"{width}x{height}",
                "fps": args.fps,
                "duration_s": round(cursor, 3),
                "planned_duration_s": round(planned_total, 3),
                "panels": edl,
                "shots": [
                    {"shot_id": sid,
                     "start_s": next(p['start_s'] for p in edl if p['shot_id'] == sid),
                     "duration_s": round(sum(p['frame_count'] for p in edl if p['shot_id'] == sid) / args.fps, 3),
                     "panel_ids": [p['panel_id'] for p in edl if p['shot_id'] == sid]}
                    for sid in [s['id'] for s in data['shots']]
                ],
                "visual_review": "not assessed by this script",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    missing = [item["panel_id"] for item in edl if item["placeholder"]]
    print(f"animatic: {out_path}  ({len(data['shots'])} shots / {len(panels)} panels, {cursor:.3f}s, {width}x{height}, {args.fps}fps)")
    print(f"edl:      {edl_path}")
    if missing:
        print(f"placeholders used for: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
