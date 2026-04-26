"""Stibee connector — Korean newsletter REST API."""

from __future__ import annotations

import os

import requests

from base_connector import Connector
from models import Episode, Post, PublishResult


class StibeeConnector(Connector):
    name = "stibee"
    requires_oauth = False
    requires_app_review = False
    notes = "Stibee REST API; AccessToken from workspace settings"

    def adapt(self, episode: Episode) -> Post:
        body_html = (episode.long_form_text or episode.description).replace("\n", "<br>")
        if episode.disclosure_text:
            body_html += (
                f"<hr><p style='font-size:0.85em;color:#888'>{episode.disclosure_text}</p>"
            )
        return Post(
            episode_id=episode.id,
            platform=self.name,
            text=body_html,
            extras={"subject": episode.title, "list_id": os.getenv("STIBEE_LIST_ID", "")},
        )

    def health_check(self) -> dict:
        base = super().health_check()
        base["ready"] = bool(os.getenv("STIBEE_API_KEY") and os.getenv("STIBEE_LIST_ID"))
        return base

    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        if dry_run:
            return self._dry(post, "Would send via Stibee API")
        api_key = os.getenv("STIBEE_API_KEY")
        list_id = post.extras.get("list_id")
        if not (api_key and list_id):
            return self._blocked("creds")

        try:
            resp = requests.post(
                f"https://api.stibee.com/v1/lists/{list_id}/campaigns",
                headers={"AccessToken": api_key, "Content-Type": "application/json"},
                json={
                    "subject": post.extras.get("subject", ""),
                    "content": post.text,
                    "preview": post.text[:120],
                },
                timeout=30,
            )
            if resp.status_code not in (200, 201):
                return self._err(f"HTTP {resp.status_code}: {resp.text[:300]}")
            data = resp.json()
            return PublishResult(
                platform=self.name,
                status="queued",
                post_id=str(data.get("id", "")),
                note="campaign created; manual send-trigger required from Stibee UI",
            )
        except Exception as e:  # noqa: BLE001
            return self._err(f"{type(e).__name__}: {e}")
