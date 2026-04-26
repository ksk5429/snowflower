"""Beehiiv connector — Newsletter publishing via API v2.

Owned-audience platform. 0% revenue cut. Auto-fill ad network at $40-80/mo
for ~1,200+ subs (covers tooling cost). API key from Settings → Integrations.

Endpoint: POST /v2/publications/{publicationId}/posts
Auth: Authorization: Bearer {API_KEY}
"""

from __future__ import annotations

import os

import requests

from base_connector import Connector
from models import Episode, Post, PublishResult


BEEHIIV_BASE = "https://api.beehiiv.com/v2"
BEEHIIV_TITLE_LIMIT = 200
BEEHIIV_BODY_LIMIT = 1_000_000  # generous; long-form welcome


class BeehiivConnector(Connector):
    name = "beehiiv"
    requires_oauth = False  # API key auth
    requires_app_review = False
    notes = "Newsletter API v2; API key from Settings -> Integrations"

    def adapt(self, episode: Episode) -> Post:
        body_html = (episode.long_form_text or episode.description).replace("\n\n", "</p><p>").replace("\n", "<br>")
        body_html = f"<p>{body_html}</p>"
        if episode.disclosure_text:
            body_html += (
                f"<hr><p style='font-size:0.85em;color:#666'>"
                f"{episode.disclosure_text}</p>"
            )

        title = episode.title[:BEEHIIV_TITLE_LIMIT]

        return Post(
            episode_id=episode.id,
            platform=self.name,
            text=body_html[:BEEHIIV_BODY_LIMIT],
            extras={
                "title": title,
                "subtitle": episode.short_text or "",
                "publication_id": os.getenv("BEEHIIV_PUBLICATION_ID", ""),
                "status": "draft",  # safe default; flip to "confirmed" via --live
                "publish_to": "both",  # web + email
                "subscribers_only": False,
            },
        )

    def health_check(self) -> dict:
        base = super().health_check()
        base["ready"] = bool(
            os.getenv("BEEHIIV_API_KEY") and os.getenv("BEEHIIV_PUBLICATION_ID")
        )
        return base

    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        if dry_run:
            return self._dry(
                post,
                f"Would publish to Beehiiv as '{post.extras.get('title', '')[:60]}' "
                f"(status={post.extras.get('status')}, publish_to={post.extras.get('publish_to')})",
            )

        api_key = os.getenv("BEEHIIV_API_KEY")
        pub_id = post.extras.get("publication_id")
        if not (api_key and pub_id):
            return self._blocked("creds")

        body = {
            "title": post.extras.get("title", ""),
            "subtitle": post.extras.get("subtitle", ""),
            "body_content": post.text,
            "status": post.extras.get("status", "draft"),
            "publish_to": post.extras.get("publish_to", "both"),
            "subscribers_only": post.extras.get("subscribers_only", False),
        }

        try:
            resp = requests.post(
                f"{BEEHIIV_BASE}/publications/{pub_id}/posts",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=30,
            )
            if resp.status_code not in (200, 201):
                return self._err(f"HTTP {resp.status_code}: {resp.text[:300]}")
            data = resp.json().get("data", {})
            post_id = str(data.get("id", ""))
            web_url = data.get("web_url")
            status_returned = data.get("status", post.extras.get("status"))
            return PublishResult(
                platform=self.name,
                status="published" if status_returned == "confirmed" else "queued",
                url=web_url,
                post_id=post_id,
                cost_usd=0.0,
                note=f"beehiiv status={status_returned}",
            )
        except Exception as e:  # noqa: BLE001
            return self._err(f"{type(e).__name__}: {e}")
