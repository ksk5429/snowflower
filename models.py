"""Core data models for the snowflower engine."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PublishStatus = Literal[
    "dry_run",
    "published",
    "queued",
    "blocked_app_review",
    "blocked_manual_only",
    "blocked_no_credentials",
    "error",
    "not_implemented",
]


class Episode(BaseModel):
    """A source piece of content. Multi-platform fan-out begins here."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)

    video_path: Path | None = None
    audio_path: Path | None = None
    image_paths: list[Path] = Field(default_factory=list)

    long_form_text: str | None = None
    short_text: str | None = None

    disclosure_kind: Literal["neutral", "sample", "sponsored", "attribution"] = "neutral"
    disclosure_text: str = ""

    target_languages: list[str] = Field(default_factory=lambda: ["en"])
    created_at: datetime = Field(default_factory=datetime.now)


class Post(BaseModel):
    """A platform-shaped, ready-to-publish artifact."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    episode_id: str
    platform: str
    text: str
    media: list[Path] = Field(default_factory=list)
    extras: dict = Field(default_factory=dict)


class PublishResult(BaseModel):
    platform: str
    status: PublishStatus
    url: str | None = None
    post_id: str | None = None
    error: str | None = None
    cost_usd: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    note: str = ""


class PlatformConfig(BaseModel):
    enabled: bool = True
    rate_limit_per_day: int | None = None
    notes: str = ""
