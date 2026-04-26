"""Thumbnail transformer - fal.ai (Flux/Nano Banana)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ThumbnailResult:
    path: Path
    cost_usd: float
    model: str


def generate(
    prompt: str,
    out_path: Path,
    *,
    aspect: str = "16:9",
    model: str = "fal-ai/flux/schnell",
    dry_run: bool = True,
) -> ThumbnailResult:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        out_path.write_text(
            f"# snowflower thumbnail placeholder\nprompt: {prompt}\naspect: {aspect}\n",
            encoding="utf-8",
        )
        return ThumbnailResult(path=out_path, cost_usd=0.0, model=f"{model} (dry-run)")

    if not os.getenv("FAL_KEY"):
        raise RuntimeError("FAL_KEY not set")

    try:
        import fal_client  # type: ignore[import-not-found]
    except ImportError as e:
        raise RuntimeError("fal-client not installed; uncomment in requirements.txt") from e

    handler = fal_client.submit(
        model,
        arguments={
            "prompt": prompt,
            "image_size": (
                {"width": 1280, "height": 720} if aspect == "16:9" else {"width": 1080, "height": 1920}
            ),
            "num_images": 1,
        },
    )
    result = handler.get()
    image_url = result["images"][0]["url"]

    import requests as _req

    img = _req.get(image_url, timeout=60).content
    out_path.write_bytes(img)
    return ThumbnailResult(
        path=out_path,
        cost_usd=0.003 if "schnell" in model else 0.025,
        model=model,
    )
