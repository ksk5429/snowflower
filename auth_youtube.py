"""Interactive YouTube OAuth helper.

Run: python auth_youtube.py

Prereq:
1. Google Cloud Console -> APIs & Services -> Enable "YouTube Data API v3"
2. Credentials -> Create OAuth 2.0 Client ID -> Desktop app
3. Download JSON to youtube_client_secret.json (in this folder)
4. Run this script. Opens browser. Sign in with the channel's Google account.
5. Token saved to youtube_token.json. Refresh handled automatically.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def main() -> int:
    load_dotenv()
    client_secret_path = Path(
        os.getenv("YOUTUBE_CLIENT_SECRET_PATH", "youtube_client_secret.json")
    )
    token_path = Path(os.getenv("YOUTUBE_TOKEN_PATH", "youtube_token.json"))

    if not client_secret_path.exists():
        print(
            f"ERROR: client secret not found at {client_secret_path}\n"
            "Download it from console.cloud.google.com -> Credentials -> "
            "OAuth 2.0 Client ID (Desktop app)."
        )
        return 1

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import-not-found]
    except ImportError:
        print("ERROR: google-auth-oauthlib not installed. Run: pip install -r requirements.txt")
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    with open(token_path, "w") as f:
        f.write(creds.to_json())

    print(f"OK token saved to {token_path}")

    try:
        from googleapiclient.discovery import build  # type: ignore[import-not-found]

        yt = build("youtube", "v3", credentials=creds)
        ch = yt.channels().list(part="id,snippet", mine=True).execute()
        if ch.get("items"):
            cid = ch["items"][0]["id"]
            title = ch["items"][0]["snippet"]["title"]
            print(f"Channel: {title}  (id={cid})")
            print(f"Add to .env: YOUTUBE_CHANNEL_ID={cid}")
    except Exception as e:  # noqa: BLE001
        print(f"(channel discovery skipped: {type(e).__name__}: {e})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
