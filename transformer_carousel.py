"""LinkedIn PDF-carousel generator (placeholder for Sprint 0)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CarouselResult:
    pdf_path: Path
    slide_count: int


def build_carousel(
    title: str,
    bullets: list[str],
    out_path: Path,
    *,
    dry_run: bool = True,
) -> CarouselResult:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 1 + len(bullets)
    if dry_run:
        out_path.write_text(
            f"# snowflower carousel placeholder\ntitle: {title}\nslides: {n}\n",
            encoding="utf-8",
        )
        return CarouselResult(pdf_path=out_path, slide_count=n)

    raise NotImplementedError(
        "Real Pillow -> PDF rendering deferred. Use placeholder slides for Sprint 1."
    )
