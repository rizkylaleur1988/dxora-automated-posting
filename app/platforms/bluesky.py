from atproto import Client
from app.platforms.base import BasePlatform, now
from app.schemas import PlatformResult
from app.config import settings


class BlueskyPlatform(BasePlatform):
    name = "Bluesky"

    async def publish(self, message: str) -> PlatformResult:
        handle = settings.bluesky_handle
        app_password = settings.bluesky_app_password
        public_access = True

        if not handle or not app_password:
            return self.failure(
                "BLUESKY_HANDLE or BLUESKY_APP_PASSWORD is required"
            )

        client = Client()
        client.login(handle, app_password)
        result = client.post(message)

        uri = result.uri
        rkey = uri.rsplit("/", 1)[-1] if uri else None
        posted_url = (
            f"https://bsky.app/profile/{handle}/post/{rkey}"
            if rkey
            else None
        )
        date, time = now()

        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=date,
            time=time
        )
