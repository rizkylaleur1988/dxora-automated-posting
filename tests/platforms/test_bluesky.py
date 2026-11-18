import pytest
from unittest.mock import MagicMock, patch
from app.platforms.bluesky import BlueskyPlatform
from app.config import settings


@pytest.mark.asyncio
async def test_bluesky_missing_credentials(monkeypatch):
    monkeypatch.setattr(settings, "bluesky_handle", None)
    monkeypatch.setattr(settings, "bluesky_app_password", None)

    platform = BlueskyPlatform()
    res = await platform.publish("Check https://example.com")
    assert res.status == "failed"
    assert "BLUESKY_HANDLE or BLUESKY_APP_PASSWORD is required" in res.error


@pytest.mark.asyncio
async def test_bluesky_publish_success(monkeypatch):
    monkeypatch.setattr(settings, "bluesky_handle", "user.bsky.social")
    monkeypatch.setattr(settings, "bluesky_app_password", "app-pass-123")

    mock_result = MagicMock()
    mock_result.uri = "at://did:plc:12345/app.bsky.feed.post/3lbt7wxgxrs2x"

    mock_client = MagicMock()
    mock_client.post.return_value = mock_result

    with patch("app.platforms.bluesky.Client", return_value=mock_client):
        platform = BlueskyPlatform()
        res = await platform.publish("Check https://example.com")

    assert res.status == "success"
    assert res.public_access is True
    assert res.posted_url == (
        "https://bsky.app/profile/user.bsky.social/post/3lbt7wxgxrs2x"
    )
    mock_client.login.assert_called_once_with(
        "user.bsky.social", "app-pass-123"
    )
    mock_client.post.assert_called_once_with("Check https://example.com")


@pytest.mark.asyncio
async def test_bluesky_publish_no_uri(monkeypatch):
    monkeypatch.setattr(settings, "bluesky_handle", "user.bsky.social")
    monkeypatch.setattr(settings, "bluesky_app_password", "app-pass-123")

    mock_result = MagicMock()
    mock_result.uri = None

    mock_client = MagicMock()
    mock_client.post.return_value = mock_result

    with patch("app.platforms.bluesky.Client", return_value=mock_client):
        platform = BlueskyPlatform()
        res = await platform.publish("Check https://example.com")

    assert res.status == "success"
    assert res.posted_url is None
