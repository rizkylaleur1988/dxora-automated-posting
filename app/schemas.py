import re
from pydantic import BaseModel, Field, field_validator
from urllib.parse import urlsplit


URL_PATTERN = re.compile(r"https?://[^\s<>()]+")


def extract_url(value: str) -> list[str]:
    return [match.rstrip(".,!?;:") for match in URL_PATTERN.findall(value)]


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class PlatformResult(BaseModel):
    platform: str
    status: str
    posted_url: str | None = None
    public_access: bool = False
    date: str | None = None
    time: str | None = None
    error: str | None = None


class PostingRequest(BaseModel):
    message: str = Field(min_length=1, max_length=200)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message is required")

        urls = extract_url(value)
        if len(urls) != 1:
            raise ValueError("message must contain exactly one CTA URL")

        parsed = urlsplit(urls[0])
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("CTA URL must be a valid HTTP or HTTPS URL")
        return value


class ApiResponse(BaseModel):
    success: bool = False
    message: str = "success"
    results: dict | list | None = None
    errors: list[ErrorDetail] | None = None
