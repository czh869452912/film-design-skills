import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

CASES = {
    "baseline": ("duel-test/h3/baseline/output.mp4", [3.5, 5.0, 7.0, 8.5]),
    "skill": ("duel-test/h3/skill/output.mp4", [2.6, 4.7, 6.0, 7.2]),
}
FPS = 5


def frames(video: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"fps={FPS},scale=336:192", str(out_dir / "f_%03d.png")],
        check=True,
    )
    return sorted(out_dir.glob("f_*.png"))


def main() -> int:
    for name, (video, cuts) in CASES.items():
        files = frames(video, Path("duel-test/judge") / f"_diff_{name}")
        diffs = []
        prev = None
        for index, file in enumerate(files, start=1):
            image = Image.open(file).convert("L")
            if prev is not None:
                stat = ImageStat.Stat(ImageChops.difference(prev, image))
                diffs.append((stat.mean[0], (index - 1) / FPS))
            prev = image
        ranked = sorted(diffs, reverse=True)[:8]
        print(f"\n{name}: sampled {len(files)} frames at {FPS}fps")
        print("  declared cuts:", ", ".join(f"{c:.2f}s" for c in cuts))
        print("  strongest frame-to-frame changes:")
        for value, at in ranked:
            near = min(cuts, key=lambda c: abs(c - at))
            print(f"    {at:5.2f}s  diff={value:5.2f}  nearest declared cut={near:.2f}s ({abs(near-at):.2f}s off)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
