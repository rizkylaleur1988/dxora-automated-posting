import pytest
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.services.posting_service import PostingService


class SuccessPlatform(BasePlatform):
    def __init__(self, name: str = "success"):
        self.name = name

    async def publish(self, message: str) -> PlatformResult:
        return PlatformResult(
            platform=self.name,
            status="success",
            public_access=True
        )


class FailedPlatform(BasePlatform):
    def __init__(self, name: str = "failed", error_msg: str = "failed"):
        self.name = name
        self.error_msg = error_msg

    async def publish(self, message: str) -> PlatformResult:
        raise RuntimeError(self.error_msg)


@pytest.mark.asyncio
async def test_one_failure_does_not_stop_other_platforms():
    platforms = [SuccessPlatform(), FailedPlatform()]
    service = PostingService(platforms)
    response = await service.publish("Visit https://example.com")
    assert response.success is True
    assert [item.status for item in response.results] == ["success", "failed"]


@pytest.mark.asyncio
async def test_all_platforms_succeed():
    platforms = [SuccessPlatform("p1"), SuccessPlatform("p2")]
    service = PostingService(platforms)
    response = await service.publish("Visit https://example.com")
    assert response.success is True
    assert len(response.results) == 2
    assert all(item.status == "success" for item in response.results)


@pytest.mark.asyncio
async def test_all_platforms_fail():
    platforms = [FailedPlatform("p1"), FailedPlatform("p2")]
    service = PostingService(platforms)
    response = await service.publish("Visit https://example.com")
    assert response.success is False
    assert len(response.results) == 2
    assert all(item.status == "failed" for item in response.results)


@pytest.mark.asyncio
async def test_empty_platforms_list():
    service = PostingService([])
    response = await service.publish("Visit https://example.com")
    assert response.success is False
    assert response.results == []


@pytest.mark.asyncio
async def test_unexpected_exception_captured_as_failure():
    platform = FailedPlatform("crash_platform", error_msg="database exploded")
    service = PostingService([platform])
    response = await service.publish("Visit https://example.com")
    assert response.success is False
    result = response.results[0]
    assert result.status == "failed"
    assert "RuntimeError: database exploded" in result.error
