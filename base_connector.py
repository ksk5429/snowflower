"""Connector abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models import Episode, PlatformConfig, Post, PublishResult


class Connector(ABC):
    """Abstract base for every platform connector."""

    name: str = "base"
    requires_oauth: bool = True
    requires_app_review: bool = False
    manual_only: bool = False
    notes: str = ""

    def __init__(self, config: PlatformConfig | None = None):
        self.config = config or PlatformConfig()

    @abstractmethod
    def adapt(self, episode: Episode) -> Post:
        """Reshape the episode into a platform-specific Post."""
        raise NotImplementedError

    @abstractmethod
    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        """Publish post. Must honor dry_run (no API call when True)."""
        raise NotImplementedError

    def health_check(self) -> dict:
        return {
            "name": self.name,
            "requires_oauth": self.requires_oauth,
            "requires_app_review": self.requires_app_review,
            "manual_only": self.manual_only,
            "notes": self.notes,
            "ready": False,
        }

    def _dry(self, post: Post, note: str = "") -> PublishResult:
        return PublishResult(
            platform=self.name,
            status="dry_run",
            note=note or f"Dry-run for {self.name}: {len(post.text)} chars, {len(post.media)} media",
        )

    def _blocked(self, reason: str) -> PublishResult:
        status_map = {
            "app_review": "blocked_app_review",
            "manual": "blocked_manual_only",
            "creds": "blocked_no_credentials",
        }
        return PublishResult(
            platform=self.name,
            status=status_map.get(reason, "blocked_no_credentials"),
            note=reason,
        )

    def _err(self, msg: str) -> PublishResult:
        return PublishResult(platform=self.name, status="error", error=msg)
