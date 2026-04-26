"""TikTok Content Posting API connector.

Mandatory app review (5–10 business days). Until audit clears, all API-posted
content is forced to private. Explicitly forbids "apps that copy arbitrary
content from other platforms" — never use as raw cross-poster.
"""

from __future__ import annotations

import os

from base_connector import Connector
from models import Episode, Post, PublishResult


TIKTOK_CAPTION_LIMIT = 2200


class TikTokConnector(Connector):
    name = "tiktok"
    requires_oauth = True
    requires_app_review = True
    notes = "Content Posting API; audit required (5-10d); private-by-default until approved"

    def adapt(self, episode: Episode) -> Post:
        caption = (episode.short_text or episode.title)[:TIKTOK_CAPTION_LIMIT]
        if episode.disclosure_text:
            caption = f"{caption}\n\n{episode.disclosure_text}"[:TIKTOK_CAPTION_LIMIT]

        return Post(
            episode_id=episode.id,
            platform=self.name,
            text=caption,
            media=[episode.video_path] if episode.video_path else [],
            extras={"privacy_level": "SELF_ONLY"},
        )

    def health_check(self) -> dict:
        base = super().health_check()
        base["ready"] = bool(
            os.getenv("TIKTOK_CLIENT_KEY")
            and os.getenv("TIKTOK_CLIENT_SECRET")
            and os.getenv("TIKTOK_ACCESS_TOKEN")
        )
        return base

    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        if dry_run:
            return self._dry(post, "Would post to TikTok via Content Posting API")
        if not os.getenv("TIKTOK_ACCESS_TOKEN"):
            return self._blocked("app_review")
        return PublishResult(
            platform=self.name,
            status="not_implemented",
            note="TikTok upload flow (init -> upload -> publish) deferred to post-audit Sprint",
        )
