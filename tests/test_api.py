import pytest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.schemas import ApiResponse, PlatformResult


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_posting_endpoint_success():
    mock_service = AsyncMock()
    mock_service.publish.return_value = ApiResponse(
        success=True,
        results=[
            PlatformResult(
                platform="Telegram",
                status="success",
                public_access=True,
                posted_url="https://t.me/channel/1",
                date="2026-11-18",
                time="10:00:00"
            )
        ]
    )

    with patch("app.main.service", return_value=mock_service):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as ac:
            response = await ac.post("/posting", json={
                "message": "Hello world https://example.com"
            })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["results"]) == 1
    assert data["results"][0]["platform"] == "Telegram"
    mock_service.publish.assert_awaited_once_with(
        "Hello world https://example.com"
    )


@pytest.mark.asyncio
async def test_posting_endpoint_validation_error_no_url():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/posting", json={
            "message": "Message without any link"
        })

    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert any(err["field"] == "message" for err in data["errors"])


@pytest.mark.asyncio
async def test_posting_endpoint_empty_body():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/posting", json={})

    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
