import httpx
from datetime import datetime, timezone
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings


def date_time(value: str):
    return value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")


class TelegramPlatform(BasePlatform):
    name = "Telegram"

    async def publish(self, message: str) -> PlatformResult:
        timeout = settings.http_timeout_seconds
        token = settings.telegram_bot_token
        chat_id = settings.telegram_chat_id

        if not token or not chat_id:
            return self.failure(
                "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is required"
            )

        endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(endpoint, json={
                "chat_id": chat_id,
                "text": message
            })
            response.raise_for_status()
            payload = response.json()

        if not payload.get("ok"):
            return self.failure(
                payload.get("description")
                or "Telegram API rejected the message"
            )

        result = payload["result"]
        date, time = date_time(
            datetime.fromtimestamp(result["date"], tz=timezone.utc)
        )
        posted_url = None
        public_access = False
        if chat_id.startswith("@"):
            posted_url = f"https://t.me/{chat_id[1:]}/{result['message_id']}"
            public_access = True

        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=date,
            time=time
        )
