import httpx
from app.platforms.base import BasePlatform, now
from app.schemas import PlatformResult
from app.config import settings


class DiscordPlatform(BasePlatform):
    name = "Discord"

    async def publish(self, message: str) -> PlatformResult:
        timeout = settings.http_timeout_seconds
        url = settings.discord_webhook_url

        if not url:
            return self.failure("DISCORD_WEBHOOK_URL is required")

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{url}?wait=true", json={
                "content": message
            })
            response.raise_for_status()
            payload = response.json()

        message_id = payload.get("id")
        channel_id = payload.get("channel_id")
        guild_id = payload.get("guild_id")
        posted_url = None
        public_access = False
        date, time = now()
        if message_id and channel_id and guild_id:
            posted_url = (
                "https://discord.com/channels/"
                f"{guild_id}/{channel_id}/{message_id}"
            )

        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=date,
            time=time
        )
