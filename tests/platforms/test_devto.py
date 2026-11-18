import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.platforms.devto import DevtoPlatform
from app.config import settings


@pytest.mark.asyncio
async def test_devto_missing_api_key(monkeypatch):
    monkeypatch.setattr(settings, "devto_api_key", None)

    platform = DevtoPlatform()
    res = await platform.publish("Check https://example.com")
    assert res.status == "failed"
    assert "DEVTO_API_KEY is required" in res.error


@pytest.mark.asyncio
async def test_devto_publish_success(monkeypatch):
    monkeypatch.setattr(settings, "devto_api_key", "devto-secret-token")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "url": "https://dev.to/username/my-awesome-post-123"
    }
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        platform = DevtoPlatform()
        res = await platform.publish("Check https://example.com")

    assert res.status == "success"
    assert res.public_access is True
    assert res.posted_url == "https://dev.to/username/my-awesome-post-123"
    assert res.date is not None
    assert res.time is not None
