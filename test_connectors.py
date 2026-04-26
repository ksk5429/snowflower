"""Smoke tests for connectors. Verifies adapt() shape and dry-run safety."""

from __future__ import annotations

import pytest

from connectors_registry import REGISTRY, get_connector
from models import Episode


@pytest.fixture
def sample_episode() -> Episode:
    return Episode(
        id="test-ep",
        title="Test episode for connector adapt()",
        description="Short description.",
        tags=["accessibility", "testing"],
        long_form_text="Long form body text. " * 50,
        short_text="Short hook.",
        disclosure_kind="neutral",
        disclosure_text="snowflower is independent editorial.",
        target_languages=["en", "ko"],
    )


@pytest.mark.parametrize("name", list(REGISTRY))
def test_adapt_returns_post(name: str, sample_episode: Episode) -> None:
    c = get_connector(name)
    post = c.adapt(sample_episode)
    assert post.platform == name
    assert post.episode_id == sample_episode.id
    assert isinstance(post.text, str)
    assert post.text


@pytest.mark.parametrize("name", list(REGISTRY))
def test_dry_run_makes_no_api_calls(name: str, sample_episode: Episode) -> None:
    c = get_connector(name)
    post = c.adapt(sample_episode)
    result = c.publish(post, dry_run=True)
    assert result.platform == name
    assert result.status in {"dry_run", "blocked_manual_only", "blocked_no_credentials"}


@pytest.mark.parametrize("name", list(REGISTRY))
def test_health_check_returns_dict(name: str) -> None:
    c = get_connector(name)
    h = c.health_check()
    assert h["name"] == name
    assert "ready" in h
