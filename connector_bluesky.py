"""Bluesky connector — AT Protocol via app password.

Easiest connector in the stack. No app review, no business verification.
Rate ceiling: 5,000 points/hour, posts cost 3 points each → ~1666/hr.
Bots are first-class; self-label `#bot` per community convention.
"""

from __future__ import annotations

import os
from pathlib import Path

from base_connector import Connector
from models import Episode, Post, PublishResult


BLUESKY_TEXT_LIMIT = 300


class BlueskyConnector(Connector):
    name = "bluesky"
    requires_oauth = False
    requires_app_review = False
    notes = "AT Protocol; app password from bsky.app/settings/app-passwords"

    def adapt(self, episode: Episode) -> Post:
        text = episode.short_text or episode.title
        if episode.disclosure_text:
            text = f"{text}\n\n{episode.disclosure_text}"
        if len(text) > BLUESKY_TEXT_LIMIT:
            text = text[: BLUESKY_TEXT_LIMIT - 1] + "…"

        media = episode.image_paths[:4]
        return Post(
            episode_id=episode.id,
            platform=self.name,
            text=text,
            media=media,
            extras={"langs": episode.target_languages},
        )

    def health_check(self) -> dict:
        base = super().health_check()
        handle = os.getenv("BLUESKY_HANDLE")
        pw = os.getenv("BLUESKY_APP_PASSWORD")
        base["ready"] = bool(handle and pw)
        base["handle"] = handle or "(unset)"
        return base

    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        if dry_run:
            return self._dry(post, f"Would post to Bluesky as {os.getenv('BLUESKY_HANDLE') or '?'}")

        handle = os.getenv("BLUESKY_HANDLE")
        password = os.getenv("BLUESKY_APP_PASSWORD")
        if not (handle and password):
            return self._blocked("creds")

        try:
            from atproto import Client  # type: ignore[import-not-found]
        except ImportError:
            return self._err("atproto package not installed; run: pip install -r requirements.txt")

        try:
            client = Client()
            client.login(handle, password)

            embed_images = []
            for img_path in post.media:
                p = Path(img_path)
                if not p.exists():
                    continue
                with open(p, "rb") as f:
                    upload = client.upload_blob(f.read())
                embed_images.append({"alt": p.stem, "image": upload.blob})

            if embed_images:
                from atproto import models as bsky_models  # type: ignore[import-not-found]

                embed = bsky_models.AppBskyEmbedImages.Main(
                    images=[bsky_models.AppBskyEmbedImages.Image(**i) for i in embed_images]
                )
                resp = client.send_post(text=post.text, embed=embed, langs=post.extras.get("langs"))
            else:
                resp = client.send_post(text=post.text, langs=post.extras.get("langs"))

            uri = getattr(resp, "uri", "")
            post_id = uri.split("/")[-1] if uri else None
            url = f"https://bsky.app/profile/{handle}/post/{post_id}" if post_id else None

            return PublishResult(
                platform=self.name,
                status="published",
                url=url,
                post_id=post_id,
                cost_usd=0.0,
            )
        except Exception as e:  # noqa: BLE001
            return self._err(f"{type(e).__name__}: {e}")
