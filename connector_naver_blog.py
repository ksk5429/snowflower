"""Naver Blog connector — semi-manual.

Cron-publishing = high suspension risk (2025-2026 저품대란 sweep).
Emits a draft payload the user can paste into 스마트에디터 ONE manually.
"""

from __future__ import annotations

import os

from base_connector import Connector
from models import Episode, Post, PublishResult


NAVER_BODY_LIMIT = 50_000


class NaverBlogConnector(Connector):
    name = "naver_blog"
    requires_oauth = True
    requires_app_review = False
    manual_only = True
    notes = "API exists but cron = 정지 risk; emits draft for manual paste"

    def adapt(self, episode: Episode) -> Post:
        if "ko" not in episode.target_languages:
            note = (
                "[snowflower] Naver 블로그용 한국어 번역 필요. "
                "위에 영어 원문, 아래에 KR 번역을 붙여주세요."
            )
            body = f"{note}\n\n---\n\n{episode.long_form_text or episode.description}"
        else:
            body = episode.long_form_text or episode.description
        if episode.disclosure_text:
            body = f"{body}\n\n---\n{episode.disclosure_text}"
        return Post(
            episode_id=episode.id,
            platform=self.name,
            text=body[:NAVER_BODY_LIMIT],
            extras={"title": episode.title, "category": "IT/기술"},
        )

    def health_check(self) -> dict:
        base = super().health_check()
        base["ready"] = bool(
            os.getenv("NAVER_CLIENT_ID") and os.getenv("NAVER_CLIENT_SECRET")
        )
        base["note"] = "manual paste recommended; cron risks 영구정지"
        return base

    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        return self._blocked("manual")
