from datetime import datetime, timezone
from app.platforms.base import BasePlatform, now
from app.schemas import PlatformResult


class DummyPlatform(BasePlatform):
    name = "Dummy"

    async def publish(self, message: str) -> PlatformResult:
        return PlatformResult(platform=self.name, status="success")


def test_now_default():
    date_str, time_str = now()
    assert len(date_str.split("-")) == 3
    assert len(time_str.split(":")) == 3


def test_now_with_custom_timestamp():
    fixed = datetime(2026, 11, 18, 12, 34, 56, tzinfo=timezone.utc)
    date_str, time_str = now(fixed)
    assert date_str == "2026-11-18"
    assert time_str == "12:34:56"


def test_base_platform_failure():
    platform = DummyPlatform()
    res = platform.failure("Something broke")
    assert res.platform == "Dummy"
    assert res.status == "failed"
    assert res.public_access is False
    assert res.error == "Something broke"
