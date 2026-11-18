import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.platforms.telegram import TelegramPlatform
from app.config import settings


@pytest.mark.asyncio
async def test_telegram_missing_credentials(monkeypatch):
    monkeypatch.setattr(settings, "telegram_bot_token", None)
    monkeypatch.setattr(settings, "telegram_chat_id", None)

    platform = TelegramPlatform()
    res = await platform.publish("Check https://example.com")
    assert res.status == "failed"
    assert "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is required" in res.error


@pytest.mark.asyncio
async def test_telegram_public_channel_success(monkeypatch):
    monkeypatch.setattr(settings, "telegram_bot_token", "fake_bot_token")
    monkeypatch.setattr(settings, "telegram_chat_id", "@mychannel")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "message_id": 456,
            "date": 1700000000
        }
    }
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        platform = TelegramPlatform()
        res = await platform.publish("Check https://example.com")

    assert res.status == "success"
    assert res.public_access is True
    assert res.posted_url == "https://t.me/mychannel/456"
    assert res.date is not None
    assert res.time is not None


@pytest.mark.asyncio
async def test_telegram_private_chat_success(monkeypatch):
    monkeypatch.setattr(settings, "telegram_bot_token", "fake_bot_token")
    monkeypatch.setattr(settings, "telegram_chat_id", "123456789")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "message_id": 789,
            "date": 1700000000
        }
    }
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        platform = TelegramPlatform()
        res = await platform.publish("Check https://example.com")

    assert res.status == "success"
    assert res.public_access is False
    assert res.posted_url is None


@pytest.mark.asyncio
async def test_telegram_api_rejected(monkeypatch):
    monkeypatch.setattr(settings, "telegram_bot_token", "fake_bot_token")
    monkeypatch.setattr(settings, "telegram_chat_id", "@mychannel")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ok": False,
        "description": "Chat not found"
    }
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        platform = TelegramPlatform()
        res = await platform.publish("Check https://example.com")

    assert res.status == "failed"
    assert "Chat not found" in res.error
