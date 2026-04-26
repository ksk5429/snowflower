"""Shorts/Reels cut - long horizontal -> 60s vertical 9:16 via ffmpeg."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ShortsCutResult:
    path: Path
    duration_s: float
    cost_usd: float = 0.0


def cut_vertical(
    source: Path,
    out_path: Path,
    *,
    start_s: float = 0.0,
    duration_s: float = 60.0,
    dry_run: bool = True,
) -> ShortsCutResult:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        out_path.write_text(
            f"# snowflower shorts placeholder\nsource: {source}\n"
            f"start_s: {start_s}\nduration_s: {duration_s}\n",
            encoding="utf-8",
        )
        return ShortsCutResult(path=out_path, duration_s=duration_s)

    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found on PATH")

    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start_s),
        "-i",
        str(source),
        "-t",
        str(duration_s),
        "-vf",
        "crop=ih*9/16:ih,scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return ShortsCutResult(path=out_path, duration_s=duration_s)
