import asyncio
from app.platforms.base import BasePlatform
from app.schemas import ApiResponse


class PostingService:
    def __init__(self, platforms: list[BasePlatform]) -> None:
        self.platforms = platforms

    async def __publish(self, platform: BasePlatform, message: str) -> str:
        try:
            return await platform.publish(message)
        except Exception as error:
            return platform.failure(f"{type(error).__name__}: {error}")

    async def publish(self, message: str) -> ApiResponse:
        results = await asyncio.gather(*[
            self.__publish(platform, message)
            for platform in self.platforms
        ])
        return ApiResponse(
            success=any(result.status == "success" for result in results),
            results=results
        )
