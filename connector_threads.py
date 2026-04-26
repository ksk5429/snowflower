"""Threads API connector (Meta).

Rate: 250 posts / 24h per profile. 500-char limit.
"""

from __future__ import annotations

import os

import requests

from base_connector import Connector
from models import Episode, Post, PublishResult


THREADS_TEXT_LIMIT = 500


class ThreadsConnector(Connector):
    name = "threads"
    requires_oauth = True
    requires_app_review = False
    notes = "Threads API (Meta); 250 posts/24h"

    def adapt(self, episode: Episode) -> Post:
        text = episode.short_text or episode.title
        if episode.disclosure_text:
            text = f"{text}\n\n{episode.disclosure_text}"
        if len(text) > THREADS_TEXT_LIMIT:
            text = text[: THREADS_TEXT_LIMIT - 1] + "…"

        return Post(
            episode_id=episode.id,
            platform=self.name,
            text=text,
            media=episode.image_paths[:1],
            extras={"media_type": "TEXT" if not episode.image_paths else "IMAGE"},
        )

    def health_check(self) -> dict:
        base = super().health_check()
        base["ready"] = bool(os.getenv("THREADS_USER_ID") and os.getenv("THREADS_ACCESS_TOKEN"))
        return base

    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        if dry_run:
            return self._dry(post, f"Would post to Threads ({len(post.text)} chars)")

        user_id = os.getenv("THREADS_USER_ID")
        token = os.getenv("THREADS_ACCESS_TOKEN")
        if not (user_id and token):
            return self._blocked("creds")

        try:
            create_resp = requests.post(
                f"https://graph.threads.net/v1.0/{user_id}/threads",
                params={
                    "media_type": post.extras.get("media_type", "TEXT"),
                    "text": post.text,
                    "access_token": token,
                },
                timeout=30,
            )
            if create_resp.status_code != 200:
                return self._err(f"create HTTP {create_resp.status_code}: {create_resp.text[:300]}")
            container_id = create_resp.json().get("id")

            publish_resp = requests.post(
                f"https://graph.threads.net/v1.0/{user_id}/threads_publish",
                params={"creation_id": container_id, "access_token": token},
                timeout=30,
            )
            if publish_resp.status_code != 200:
                return self._err(
                    f"publish HTTP {publish_resp.status_code}: {publish_resp.text[:300]}"
                )
            post_id = publish_resp.json().get("id")
            return PublishResult(
                platform=self.name,
                status="published",
                post_id=post_id,
                url=f"https://www.threads.net/@_/post/{post_id}" if post_id else None,
                cost_usd=0.0,
            )
        except Exception as e:  # noqa: BLE001
            return self._err(f"{type(e).__name__}: {e}")
