import httpx
from app.platforms.base import BasePlatform, now
from app.schemas import PlatformResult
from app.config import settings


class MastodonPlatform(BasePlatform):
    name = "Mastodon"

    async def publish(self, message: str) -> PlatformResult:
        timeout = settings.http_timeout_seconds
        access_token = settings.mastodon_access_token
        visibility = settings.mastodon_visibility

        if not access_token or not visibility:
            return self.failure(
                "MASTODON_ACCESS_TOKEN or MASTODON_VISIBILITY is required"
            )

        if visibility not in {"public", "private"}:
            return self.failure(
                "MASTODON_VISIBILITY must be public or private"
            )

        endpoint = "https://mastodon.social/api/v1/statuses"
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
                json={"status": message, "visibility": visibility}
            )
            response.raise_for_status()
            payload = response.json()

        posted_url = payload.get("url")
        public_access = visibility == "public"
        date, time = now()

        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=date,
            time=time
        )
