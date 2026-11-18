from abc import ABC, abstractmethod
from datetime import datetime, timezone
from app.schemas import PlatformResult


def now(value: datetime | None = None) -> tuple[str, str]:
    timestamp = value or datetime.now(timezone.utc)
    timestamp = timestamp.astimezone(timezone.utc)
    return timestamp.strftime("%Y-%m-%d"), timestamp.strftime("%H:%M:%S")


class BasePlatform(ABC):
    @abstractmethod
    async def publish(self, message: str) -> PlatformResult:
        raise NotImplementedError

    def failure(self, error: Exception | str) -> PlatformResult:
        return PlatformResult(
            platform=self.name,
            status="failed",
            public_access=False,
            error=str(error),
        )
