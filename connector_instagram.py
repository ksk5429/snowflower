"""Instagram Graph API connector — Reels publishing.

Requires Instagram Business + linked FB Page + Meta App Review (1-4 wk).
50 API-published posts/24h per IG account.
"""

from __future__ import annotations

import os

from base_connector import Connector
from models import Episode, Post, PublishResult


IG_CAPTION_LIMIT = 2200


class InstagramConnector(Connector):
    name = "instagram"
    requires_oauth = True
    requires_app_review = True
    notes = "Graph API; Business account + FB Page + App Review required"

    def adapt(self, episode: Episode) -> Post:
        caption = (episode.short_text or episode.title)[:IG_CAPTION_LIMIT]
        if episode.disclosure_text:
            caption = f"{caption}\n\n{episode.disclosure_text}"[:IG_CAPTION_LIMIT]

        return Post(
            episode_id=episode.id,
            platform=self.name,
            text=caption,
            media=[episode.video_path] if episode.video_path else episode.image_paths[:1],
            extras={
                "media_type": "REELS" if episode.video_path else "IMAGE",
                "video_url": None,
            },
        )

    def health_check(self) -> dict:
        base = super().health_check()
        base["ready"] = bool(
            os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
            and os.getenv("INSTAGRAM_ACCESS_TOKEN")
        )
        return base

    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        if dry_run:
            return self._dry(post, "Would post to Instagram Reels via Graph API")
        if not os.getenv("INSTAGRAM_ACCESS_TOKEN"):
            return self._blocked("app_review")
        return PublishResult(
            platform=self.name,
            status="not_implemented",
            note="IG Reels container + publish wiring deferred to post-App-Review Sprint",
        )
