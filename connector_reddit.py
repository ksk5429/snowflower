"""Reddit connector — read-only metrics.

Posting is intentionally manual (CQS shadowban risk on cron-driven self-promo,
$12k/yr commercial API tier, per-sub karma walls).
"""

from __future__ import annotations

import os

from base_connector import Connector
from models import Episode, Post, PublishResult


class RedditConnector(Connector):
    name = "reddit"
    requires_oauth = True
    requires_app_review = False
    manual_only = True
    notes = "Posting MANUAL (shadowban risk); this connector reads metrics only"

    def adapt(self, episode: Episode) -> Post:
        body = episode.long_form_text or episode.description
        if episode.disclosure_text:
            body = f"{body}\n\n---\n{episode.disclosure_text}"
        return Post(
            episode_id=episode.id,
            platform=self.name,
            text=body,
            extras={
                "title": episode.title,
                "candidate_subs": [
                    "disability",
                    "als",
                    "SCI",
                    "MultipleSclerosis",
                    "Quadriplegia",
                    "Cerebral_Palsy",
                    "Stroke",
                    "Caregivers",
                    "AssistiveTechnology",
                ],
                "instructions": "Hand-post to ONE sub per week max. Read sub rules first.",
            },
        )

    def health_check(self) -> dict:
        base = super().health_check()
        base["ready"] = bool(
            os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET")
        )
        base["note"] = "metrics-only; manual posting required"
        return base

    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        return self._blocked("manual")
