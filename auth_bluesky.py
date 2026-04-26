"""Bluesky login probe.

Run: python auth_bluesky.py

Verifies BLUESKY_HANDLE + BLUESKY_APP_PASSWORD work. App password from
https://bsky.app/settings/app-passwords (NOT main password).
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv


def main() -> int:
    load_dotenv()
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_APP_PASSWORD")

    if not (handle and password):
        print("ERROR: BLUESKY_HANDLE and BLUESKY_APP_PASSWORD must be set in .env")
        return 1

    try:
        from atproto import Client  # type: ignore[import-not-found]
    except ImportError:
        print("ERROR: atproto not installed. Run: pip install -r requirements.txt")
        return 1

    try:
        client = Client()
        profile = client.login(handle, password)
        print(f"OK logged in as @{handle}")
        print(f"   DID: {profile.did}")
        print(f"   followers: {profile.followers_count}")
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
