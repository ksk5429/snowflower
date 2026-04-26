"""Korean voiceover via ElevenLabs."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VoiceoverResult:
    path: Path
    voice_id: str
    duration_s_est: float
    cost_usd: float


def synthesize_kr(
    text: str,
    out_path: Path,
    *,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    model: str = "eleven_multilingual_v2",
    dry_run: bool = True,
) -> VoiceoverResult:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    char_count = len(text)
    cost_est = (char_count / 1000) * 0.30
    duration_est = char_count / 13

    if dry_run:
        out_path.write_text(
            f"# snowflower KR voiceover placeholder\nchars: {char_count}\n"
            f"voice_id: {voice_id}\nestimated_cost_usd: {cost_est:.3f}\n",
            encoding="utf-8",
        )
        return VoiceoverResult(
            path=out_path, voice_id=voice_id, duration_s_est=duration_est, cost_usd=0.0
        )

    if not os.getenv("ELEVENLABS_API_KEY"):
        raise RuntimeError("ELEVENLABS_API_KEY not set")

    try:
        from elevenlabs.client import ElevenLabs  # type: ignore[import-not-found]
    except ImportError as e:
        raise RuntimeError("elevenlabs not installed; uncomment in requirements.txt") from e

    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    audio_iter = client.text_to_speech.convert(
        voice_id=voice_id, model_id=model, text=text, output_format="mp3_44100_128"
    )
    with open(out_path, "wb") as f:
        for chunk in audio_iter:
            f.write(chunk)

    return VoiceoverResult(
        path=out_path, voice_id=voice_id, duration_s_est=duration_est, cost_usd=cost_est
    )
