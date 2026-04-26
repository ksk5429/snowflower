"""Per-platform connector registry."""

from __future__ import annotations

from base_connector import Connector
from connector_beehiiv import BeehiivConnector
from connector_bluesky import BlueskyConnector
from connector_instagram import InstagramConnector
from connector_linkedin import LinkedInConnector
from connector_naver_blog import NaverBlogConnector
from connector_reddit import RedditConnector
from connector_stibee import StibeeConnector
from connector_threads import ThreadsConnector
from connector_tiktok import TikTokConnector
from connector_x import XConnector
from connector_youtube import YouTubeConnector


REGISTRY: dict[str, type[Connector]] = {
    "youtube": YouTubeConnector,
    "linkedin": LinkedInConnector,
    "bluesky": BlueskyConnector,
    "beehiiv": BeehiivConnector,
    "threads": ThreadsConnector,
    "x": XConnector,
    "tiktok": TikTokConnector,
    "instagram": InstagramConnector,
    "reddit": RedditConnector,
    "naver_blog": NaverBlogConnector,
    "stibee": StibeeConnector,
}


def get_connector(name: str) -> Connector:
    if name not in REGISTRY:
        raise KeyError(f"Unknown connector: {name}. Known: {list(REGISTRY)}")
    return REGISTRY[name]()
