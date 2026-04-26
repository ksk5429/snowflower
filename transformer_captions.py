"""Caption transformer - Whisper-based SRT generation.

Critical for accessibility content (captions ARE the product when your audience
includes deaf and hard-of-hearing viewers).

Real impl uses faster-whisper (uncomment in requirements.txt).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CaptionResult:
    srt_path: Path
    language: str
    segment_count: int
    cost_usd: float = 0.0


def transcribe(
    audio_or_video: Path,
    out_path: Path,
    *,
    model_size: str = "small",
    language: str | None = None,
    dry_run: bool = True,
) -> CaptionResult:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        out_path.write_text(
            "1\n00:00:00,000 --> 00:00:02,000\n[snowflower dry-run placeholder caption]\n",
            encoding="utf-8",
        )
        return CaptionResult(srt_path=out_path, language=language or "auto", segment_count=1)

    try:
        from faster_whisper import WhisperModel  # type: ignore[import-not-found]
    except ImportError as e:
        raise RuntimeError(
            "faster-whisper not installed; uncomment in requirements.txt"
        ) from e

    model = WhisperModel(model_size, device="auto", compute_type="auto")
    segments, info = model.transcribe(str(audio_or_video), language=language, beam_size=5)

    lines: list[str] = []
    seg_count = 0
    for i, seg in enumerate(segments, 1):
        seg_count += 1
        lines.append(str(i))
        lines.append(f"{_t(seg.start)} --> {_t(seg.end)}")
        lines.append(seg.text.strip())
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return CaptionResult(srt_path=out_path, language=info.language, segment_count=seg_count)


def _t(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
