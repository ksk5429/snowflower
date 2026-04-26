"""YouTube Data API v3 connector — long-form + Shorts via videos.insert.

Quota: 10,000 units/day default; videos.insert = 1,600 → ~6 uploads/day.
Shorts auto-detected when video ≤ 180s and 9:16.
AI policy: disclose realistic synthetic content via altered-content toggle.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from base_connector import Connector
from models import Episode, Post, PublishResult


YOUTUBE_TITLE_LIMIT = 100
YOUTUBE_DESCRIPTION_LIMIT = 5000
YOUTUBE_TAGS_LIMIT_CHARS = 500


class YouTubeConnector(Connector):
    name = "youtube"
    requires_oauth = True
    requires_app_review = False
    notes = "Data API v3; videos.insert; default 10k units/day quota (~6 uploads)"

    def adapt(self, episode: Episode) -> Post:
        title = episode.title[:YOUTUBE_TITLE_LIMIT]

        body_parts = [episode.description]
        if episode.disclosure_text:
            body_parts.append("")
            body_parts.append(episode.disclosure_text)
        if episode.tags:
            body_parts.append("")
            body_parts.append(" ".join(f"#{t.replace(' ', '')}" for t in episode.tags[:5]))
        description = "\n".join(body_parts)[:YOUTUBE_DESCRIPTION_LIMIT]

        tags: list[str] = []
        running = 0
        for tag in episode.tags:
            if running + len(tag) + 1 > YOUTUBE_TAGS_LIMIT_CHARS:
                break
            tags.append(tag)
            running += len(tag) + 1

        media: list[Path] = []
        if episode.video_path:
            media.append(episode.video_path)

        return Post(
            episode_id=episode.id,
            platform=self.name,
            text=description,
            media=media,
            extras={
                "title": title,
                "tags": tags,
                "category_id": "28",
                "privacy_status": "private",
                "made_for_kids": False,
                "altered_content": False,
            },
        )

    def health_check(self) -> dict:
        base = super().health_check()
        token_path = os.getenv("YOUTUBE_TOKEN_PATH", "youtube_token.json")
        client_path = os.getenv("YOUTUBE_CLIENT_SECRET_PATH", "youtube_client_secret.json")
        base["ready"] = Path(token_path).exists() and Path(client_path).exists()
        base["token_path"] = token_path
        base["client_secret_path"] = client_path
        return base

    def publish(self, post: Post, *, dry_run: bool = True) -> PublishResult:
        if dry_run:
            return self._dry(
                post,
                f"Would upload to YouTube: title='{post.extras.get('title', '')[:60]}' "
                f"video={post.media[0] if post.media else 'NONE'}",
            )

        if not post.media:
            return self._err("No video file in post.media")

        video_path = Path(post.media[0])
        if not video_path.exists():
            return self._err(f"Video file not found: {video_path}")

        token_path = Path(os.getenv("YOUTUBE_TOKEN_PATH", "youtube_token.json"))
        if not token_path.exists():
            return self._blocked("creds")

        try:
            from google.oauth2.credentials import Credentials  # type: ignore[import-not-found]
            from googleapiclient.discovery import build  # type: ignore[import-not-found]
            from googleapiclient.http import MediaFileUpload  # type: ignore[import-not-found]
        except ImportError:
            return self._err(
                "google-api-python-client not installed; run: pip install -r requirements.txt"
            )

        try:
            with open(token_path) as f:
                token_data = json.load(f)
            creds = Credentials.from_authorized_user_info(token_data)

            youtube = build("youtube", "v3", credentials=creds)

            body = {
                "snippet": {
                    "title": post.extras.get("title", ""),
                    "description": post.text,
                    "tags": post.extras.get("tags", []),
                    "categoryId": post.extras.get("category_id", "28"),
                },
                "status": {
                    "privacyStatus": post.extras.get("privacy_status", "private"),
                    "selfDeclaredMadeForKids": post.extras.get("made_for_kids", False),
                    "containsSyntheticMedia": post.extras.get("altered_content", False),
                },
            }

            media = MediaFileUpload(
                str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4"
            )
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = None
            while response is None:
                _, response = request.next_chunk()

            video_id = response["id"]
            return PublishResult(
                platform=self.name,
                status="published",
                url=f"https://www.youtube.com/watch?v={video_id}",
                post_id=video_id,
                cost_usd=0.0,
                note="quota cost: ~1600 units",
            )
        except Exception as e:  # noqa: BLE001
            return self._err(f"{type(e).__name__}: {e}")
