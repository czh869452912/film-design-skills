#!/usr/bin/env python3
"""Build a simple animatic (timed previz clip) from storyboard panels.

Reads a shot list JSON, looks for one panel image per shot
(`<shot_id>.png|jpg|jpeg|webp`), renders each panel as a video segment of its
declared duration, concatenates them, and writes an mp4 plus an EDL.

Options: per-panel fade in/out (`--transition fade`), an external audio track
(`--audio`), label position, size and fps.

Usage:
    python animatic.py shotlist.json --images storyboard --out animatic/animatic.mp4
    python animatic.py shotlist.json --images annotated --out out.mp4 --transition fade --audio scratch.wav
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
DEFAULT_FONT = "Arial" if sys.platform.startswith("win") else None


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data.get("shots"), list) or not data["shots"]:
        raise SystemExit("shot list needs a non-empty 'shots' array")
    return data


def find_panel(images: Path, shot_id: str) -> Path | None:
    for ext in IMAGE_EXTS:
        candidate = images / f"{shot_id}{ext}"
        if candidate.exists():
            return candidate
    return None


def size_from_aspect(aspect: str) -> tuple[int, int]:
    try:
        w, h = (float(part) for part in aspect.split(":"))
    except (ValueError, AttributeError):
        return 1344, 768
    if not w or not h:
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
                   transition: str = "none", label_position: str = "top-left") -> None:
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
        vf.append(f"fade=t=in:st=0:d={fade:.2f}")
        vf.append(f"fade=t=out:st={duration - fade:.2f}:d={fade:.2f}")

    cmd = ["ffmpeg", "-v", "error", "-y"]
    if src is None:
        cmd += ["-f", "lavfi", "-i", f"color=c=0xBDBDBD:s={width}x{height}"]
    else:
        cmd += ["-loop", "1", "-i", str(src)]
    cmd += [
        "-t", f"{duration:.3f}",
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
                    help="fade = dip through black between panels")
    ap.add_argument("--audio", default=None, help="optional audio track (mp3/wav/m4a) trimmed to the runtime")
    args = ap.parse_args()

    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg not found on PATH")

    data = load(Path(args.shotlist))
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
    font = args.font if args.font else DEFAULT_FONT
    labels = not args.no_labels

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    shots = data["shots"]
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        concat_lines: list[str] = []
        edl: list[dict] = []
        cursor = 0.0

        for index, shot in enumerate(shots, start=1):
            shot_id = str(shot.get("id") or f"S{index:02d}")
            duration = float(shot.get("duration_s") or 0)
            src = find_panel(images, shot_id) if images else None
            segment = tmp_dir / f"{index:03d}_{shot_id}.mp4"
            render_segment(
                src, shot_id, duration, width, height, segment, labels, font, args.fps,
                transition=args.transition, label_position=args.label_position,
            )
            concat_lines.append(f"file '{segment.as_posix()}'")
            edl.append(
                {
                    "shot_id": shot_id,
                    "start_s": round(cursor, 3),
                    "duration_s": round(duration, 3),
                    "panel": str(src) if src else None,
                    "placeholder": src is None,
                    "beat_id": shot.get("beat_id"),
                }
            )
            cursor += duration

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
                "planned_duration_s": round(sum(float(s.get("duration_s") or 0) for s in shots), 3),
                "shots": edl,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    missing = [item["shot_id"] for item in edl if item["placeholder"]]
    print(f"animatic: {out_path}  ({cursor:.1f}s, {width}x{height}, {args.fps}fps)")
    print(f"edl:      {edl_path}")
    if missing:
        print(f"placeholders used for: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
