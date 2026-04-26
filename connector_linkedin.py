"""LinkedIn Posts API connector (REST, versioned 2024-12+).

Auth: 3-legged OAuth; scope w_member_social.
Rate: ~100 calls/day per member, 150/day per org.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import requests

from base_connector import Connector
from models import Episode, Post, PublishResult


LINKEDIN_TEXT_LIMIT = 3000
LINKEDIN_API_VERSION = "202409"


class LinkedInConnector(Connector):
    name = "linkedin"
    requires_oauth = True
    requires_app_review = False
    notes = "Posts API REST versioned; w_member_social scope"

    def adapt(self, episode: Episode) -> Post:
        body_parts = [episode.long_form_text or episode.description]
        if episode.disclosure_text:
            body_parts.append("")
            body_parts.append(episode.disclosure_text)
        text = "\n\n".join(p for p in body_parts if p)
        if len(text) > LINKEDIN_TEXT_LIMIT:
            text = text[: LINKEDIN_TEXT_LIMIT - 1] + "…"

        return Post(
            episode_id=episode.id,
            platform=self.name,
            text=text,
            media=episode.image_paths[:1],
            extras={"visibility": "PUBLIC"},
        )

    def health_check(self) -> dict:
        base = super().health_check()
        token_path = os.getenv("LINKEDIN_TOKEN_PATH", "linkedin_token.json")
        author = os.getenv("LINKEDIN_AUTHOR_URN", "")
        base["ready"] = Path(token_path).exists() and bool(author)
        base["token_path"] = token_path
        base["author"] = author or "(unset — first OAuth run discovers it)"
        return base

    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        if dry_run:
            return self._dry(
                post,
                f"Would post to LinkedIn as {os.getenv('LINKEDIN_AUTHOR_URN') or '?'} "
                f"({len(post.text)} chars, {len(post.media)} media)",
            )

        token_path = Path(os.getenv("LINKEDIN_TOKEN_PATH", "linkedin_token.json"))
        author = os.getenv("LINKEDIN_AUTHOR_URN")
        if not (token_path.exists() and author):
            return self._blocked("creds")

        try:
            with open(token_path) as f:
                token_data = json.load(f)
            access_token = token_data["access_token"]
        except Exception as e:  # noqa: BLE001
            return self._err(f"token-load: {type(e).__name__}: {e}")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": LINKEDIN_API_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
        }

        body = {
            "author": author,
            "commentary": post.text,
            "visibility": post.extras.get("visibility", "PUBLIC"),
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }

        try:
            resp = requests.post(
                "https://api.linkedin.com/rest/posts",
                headers=headers,
                json=body,
                timeout=30,
            )
            if resp.status_code not in (200, 201):
                return self._err(f"HTTP {resp.status_code}: {resp.text[:300]}")

            post_urn = resp.headers.get("x-restli-id") or ""
            url = (
                f"https://www.linkedin.com/feed/update/{post_urn}"
                if post_urn.startswith("urn:li:")
                else None
            )
            return PublishResult(
                platform=self.name,
                status="published",
                url=url,
                post_id=post_urn,
                cost_usd=0.0,
            )
        except Exception as e:  # noqa: BLE001
            return self._err(f"{type(e).__name__}: {e}")
