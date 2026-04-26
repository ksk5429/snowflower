"""X (Twitter) API v2 connector — pay-per-use post Feb 2026.

Cost: ~$5 per 500 posts; ~$100/mo at 5k writes + 10k reads.
Implementation deferred until paid tier acquired in Sprint 2+.
"""

from __future__ import annotations

import os

from base_connector import Connector
from models import Episode, Post, PublishResult


X_TEXT_LIMIT = 280


class XConnector(Connector):
    name = "x"
    requires_oauth = True
    requires_app_review = False
    notes = "API v2 pay-per-use ($5+ minimum); deferred to Sprint 2"

    def adapt(self, episode: Episode) -> Post:
        text = episode.short_text or episode.title
        if episode.disclosure_text:
            sep = "\n\n"
            budget = X_TEXT_LIMIT - len(text) - len(sep)
            if len(episode.disclosure_text) <= budget:
                text = f"{text}{sep}{episode.disclosure_text}"
            else:
                text = f"{text}{sep}#ad" if episode.disclosure_kind == "sponsored" else text
        if len(text) > X_TEXT_LIMIT:
            text = text[: X_TEXT_LIMIT - 1] + "…"

        return Post(
            episode_id=episode.id,
            platform=self.name,
            text=text,
            media=episode.image_paths[:4],
            extras={},
        )

    def health_check(self) -> dict:
        base = super().health_check()
        base["ready"] = bool(
            os.getenv("X_API_KEY") and os.getenv("X_API_SECRET") and os.getenv("X_ACCESS_TOKEN")
        )
        return base

    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        if dry_run:
            return self._dry(post, f"Would post to X ({len(post.text)} chars)")
        if not os.getenv("X_BEARER_TOKEN"):
            return self._blocked("creds")
        return PublishResult(
            platform=self.name,
            status="not_implemented",
            note="X v2 client wiring deferred to Sprint 2 once paid tier is provisioned",
        )
