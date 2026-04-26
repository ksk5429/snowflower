"""Interactive LinkedIn OAuth helper.

Run: python auth_linkedin.py

Prereq:
1. https://www.linkedin.com/developers -> Create App
2. Products tab -> request "Share on LinkedIn" + "Sign In with LinkedIn using OpenID Connect"
3. Auth tab -> Add redirect: http://localhost:8765/callback
4. Set LINKEDIN_CLIENT_ID + LINKEDIN_CLIENT_SECRET in .env
5. Run this script. Opens browser. Sign in.
6. Token + author URN saved to linkedin_token.json. Token expires in 60 days.
"""

from __future__ import annotations

import json
import os
import secrets as pysecrets
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests
from dotenv import load_dotenv


AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
SCOPES = "openid profile w_member_social email"


class _CallbackHandler(BaseHTTPRequestHandler):
    code: str | None = None
    state: str | None = None

    def do_GET(self):  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return
        params = urllib.parse.parse_qs(parsed.query)
        type(self).code = params.get("code", [None])[0]
        type(self).state = params.get("state", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h1>OK</h1><p>You may close this window.</p>")

    def log_message(self, *args):
        return


def main() -> int:
    load_dotenv()
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
    redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8765/callback")
    token_path = Path(os.getenv("LINKEDIN_TOKEN_PATH", "linkedin_token.json"))

    if not (client_id and client_secret):
        print("ERROR: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in .env")
        return 1

    state = pysecrets.token_urlsafe(16)
    auth_query = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": SCOPES,
        }
    )
    auth_url = f"{AUTH_URL}?{auth_query}"
    print(f"Opening browser for LinkedIn OAuth...\n  {auth_url}")
    webbrowser.open(auth_url)

    parsed = urllib.parse.urlparse(redirect_uri)
    server = HTTPServer((parsed.hostname or "localhost", parsed.port or 8765), _CallbackHandler)
    print(f"Waiting for callback on {redirect_uri} ...")
    while _CallbackHandler.code is None:
        server.handle_request()

    if _CallbackHandler.state != state:
        print("ERROR: state mismatch (csrf protection)")
        return 1

    token_resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": _CallbackHandler.code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    if token_resp.status_code != 200:
        print(f"ERROR: token exchange HTTP {token_resp.status_code}: {token_resp.text}")
        return 1
    token_data = token_resp.json()

    user_resp = requests.get(
        USERINFO_URL,
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
        timeout=30,
    )
    if user_resp.status_code == 200:
        sub = user_resp.json().get("sub")
        if sub:
            token_data["author_urn"] = f"urn:li:person:{sub}"
            print(f"Author URN: {token_data['author_urn']}")
            print(f"Add to .env: LINKEDIN_AUTHOR_URN={token_data['author_urn']}")

    with open(token_path, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"OK token saved to {token_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
