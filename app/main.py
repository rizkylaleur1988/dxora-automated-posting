from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.schemas import PostingRequest, ApiResponse
from app.services.posting_service import PostingService
from app.platforms.telegram import TelegramPlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.devto import DevtoPlatform
from app.platforms.mastodon import MastodonPlatform

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    errors = []

    for err in error.errors():
        errors.append({
            "field": ".".join(str(item) for item in err["loc"][1:]),
            "message": err["msg"]
        })

    return JSONResponse(status_code=422, content=ApiResponse(
        success=False,
        errors=errors
    ).model_dump())


@app.get("/health")
def health() -> ApiResponse:
    return ApiResponse(
        success=True,
    )


@app.post("/posting", response_model=ApiResponse)
async def posting(request: PostingRequest) -> ApiResponse:
    return await service().publish(request.message)


def service() -> PostingService:
    return PostingService([
        TelegramPlatform(),
        DiscordPlatform(),
        BlueskyPlatform(),
        DevtoPlatform(),
        MastodonPlatform()
    ])
