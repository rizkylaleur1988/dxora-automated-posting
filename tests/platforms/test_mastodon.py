import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.platforms.mastodon import MastodonPlatform
from app.config import settings


@pytest.mark.asyncio
async def test_mastodon_missing_credentials(monkeypatch):
    monkeypatch.setattr(settings, "mastodon_access_token", None)
    monkeypatch.setattr(settings, "mastodon_visibility", None)

    platform = MastodonPlatform()
    res = await platform.publish("Check https://example.com")
    assert res.status == "failed"
    assert "is required" in res.error


@pytest.mark.asyncio
async def test_mastodon_invalid_visibility(monkeypatch):
    monkeypatch.setattr(settings, "mastodon_access_token", "token-123")
    monkeypatch.setattr(settings, "mastodon_visibility", "unlisted")

    platform = MastodonPlatform()
    res = await platform.publish("Check https://example.com")
    assert res.status == "failed"
    assert "MASTODON_VISIBILITY must be public or private" in res.error


@pytest.mark.asyncio
async def test_mastodon_publish_public_success(monkeypatch):
    monkeypatch.setattr(settings, "mastodon_access_token", "token-123")
    monkeypatch.setattr(settings, "mastodon_visibility", "public")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "url": "https://mastodon.social/@user/11223344"
    }
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        platform = MastodonPlatform()
        res = await platform.publish("Check https://example.com")

    assert res.status == "success"
    assert res.public_access is True
    assert res.posted_url == "https://mastodon.social/@user/11223344"
    assert res.date is not None
    assert res.time is not None


@pytest.mark.asyncio
async def test_mastodon_publish_private_success(monkeypatch):
    monkeypatch.setattr(settings, "mastodon_access_token", "token-123")
    monkeypatch.setattr(settings, "mastodon_visibility", "private")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "url": "https://mastodon.social/@user/11223344"
    }
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        platform = MastodonPlatform()
        res = await platform.publish("Check https://example.com")

    assert res.status == "success"
    assert res.public_access is False
    assert res.posted_url == "https://mastodon.social/@user/11223344"
