import httpx
from app.platforms.base import BasePlatform, now
from app.schemas import PlatformResult
from app.config import settings


class DevtoPlatform(BasePlatform):
    name = "Devto"

    async def publish(self, message: str) -> PlatformResult:
        timeout = settings.http_timeout_seconds
        api_key = settings.devto_api_key
        public_access = True

        if not api_key:
            return self.failure("DEVTO_API_KEY is required")

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://dev.to/api/articles",
                headers={
                    "api-key": api_key,
                    "Accept": "application/vnd.forem.api-v1+json"
                },
                json={
                    "article": {
                        "title": message,
                        "body_markdown": message,
                        "published": public_access
                    }
                }
            )
            response.raise_for_status()
            payload = response.json()

        posted_url = payload.get("url")
        date, time = now()

        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=date,
            time=time
        )
