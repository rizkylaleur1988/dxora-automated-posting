import pytest
from pydantic import ValidationError
from app.schemas import PostingRequest, extract_url, ApiResponse, ErrorDetail


def test_extract_url_single_and_multiple():
    text = "Visit https://google.com and http://github.com/repo."
    urls = extract_url(text)
    assert urls == ["https://google.com", "http://github.com/repo"]


def test_extract_url_strips_trailing_punctuation():
    text = (
        "Look at https://example.com/test!,"
        " or https://site.org?param=1;"
        " and https://foo.bar: done."
    )
    urls = extract_url(text)
    assert urls == [
        "https://example.com/test",
        "https://site.org?param=1",
        "https://foo.bar"
    ]


def test_posting_request_valid():
    req = PostingRequest(
        message="   Check out this article: https://example.com/blog   "
    )
    assert req.message == "Check out this article: https://example.com/blog"


def test_posting_request_empty_or_whitespace():
    with pytest.raises(ValidationError) as exc:
        PostingRequest(message="   ")
    assert "message is required" in str(exc.value)


def test_posting_request_exceeds_max_length():
    long_msg = "https://example.com " + ("a" * 200)
    with pytest.raises(ValidationError) as exc:
        PostingRequest(message=long_msg)
    assert "String should have at most 200 characters" in str(exc.value)


def test_posting_request_missing_url():
    with pytest.raises(ValidationError) as exc:
        PostingRequest(message="This message has no CTA link whatsoever")
    assert "message must contain exactly one CTA URL" in str(exc.value)


def test_posting_request_multiple_urls():
    with pytest.raises(ValidationError) as exc:
        PostingRequest(
            message="Check https://example.com and https://another.com"
        )
    assert "message must contain exactly one CTA URL" in str(exc.value)


def test_posting_request_invalid_scheme():
    with pytest.raises(ValidationError) as exc:
        PostingRequest(message="Check ftp://files.example.com/doc")
    assert "message must contain exactly one CTA URL" in str(exc.value)


def test_posting_request_url_missing_hostname():
    with pytest.raises(ValidationError) as exc:
        PostingRequest(message="Check out https://?foo=bar")
    assert "CTA URL must be a valid HTTP or HTTPS URL" in str(exc.value)


def test_api_response_and_error_detail_models():
    err = ErrorDetail(field="message", message="Invalid message")
    assert err.field == "message"
    assert err.message == "Invalid message"

    res = ApiResponse(
        success=True,
        message="Done",
        results={"item": 1},
        errors=[err]
    )
    dumped = res.model_dump()
    assert dumped["success"] is True
    assert dumped["message"] == "Done"
    assert len(dumped["errors"]) == 1
