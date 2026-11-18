import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.platforms.discord import DiscordPlatform
from app.config import settings


@pytest.mark.asyncio
async def test_discord_missing_webhook(monkeypatch):
    monkeypatch.setattr(settings, "discord_webhook_url", None)

    platform = DiscordPlatform()
    res = await platform.publish("Check https://example.com")
    assert res.status == "failed"
    assert "DISCORD_WEBHOOK_URL is required" in res.error


@pytest.mark.asyncio
async def test_discord_publish_success(monkeypatch):
    monkeypatch.setattr(
        settings,
        "discord_webhook_url",
        "https://discord.com/api/webhooks/123/abc"
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "msg_999",
        "channel_id": "chan_888",
        "guild_id": "guild_777"
    }
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        platform = DiscordPlatform()
        res = await platform.publish("Check https://example.com")

    assert res.status == "success"
    assert res.posted_url == (
        "https://discord.com/channels/guild_777/chan_888/msg_999"
    )
    assert res.date is not None
    assert res.time is not None


@pytest.mark.asyncio
async def test_discord_publish_without_ids(monkeypatch):
    monkeypatch.setattr(
        settings,
        "discord_webhook_url",
        "https://discord.com/api/webhooks/123/abc"
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        platform = DiscordPlatform()
        res = await platform.publish("Check https://example.com")

    assert res.status == "success"
    assert res.posted_url is None
