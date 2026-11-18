# Automated Multi-Platform Posting Service

A backend service built with **FastAPI** that automatically and concurrently publishes messages across multiple third-party social media and developer blogging platforms with built-in fault tolerance.

Supported Platforms:
- **Telegram** (Telegram Bot API)
- **Discord** (Webhook API)
- **Bluesky** (`atproto` SDK)
- **Dev.to** (Forem API)
- **Mastodon** (Mastodon REST API)

---

## Table of Contents
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Environment Variables Configuration](#environment-variables-configuration)
- [Running the Application](#running-the-application)
- [Running the Test Suite](#running-the-test-suite)
- [Sample API Requests & Responses](#sample-api-requests--responses)
  - [1. Health Check (`GET /health`)](#1-health-check-get-health)
  - [2. Publish Post Success (`POST /posting`)](#2-publish-post-success-post-posting)
  - [3. Validation Error 422 (`POST /posting`)](#3-validation-error-422-post-posting)
- [Execution Logs & Implementation Evidence](#execution-logs--implementation-evidence)
- [Security & Credentials](#security--credentials)

---

## Key Features
1. **Concurrent Multi-Platform Dispatch**: Publishes posts across all platforms simultaneously using `asyncio.gather`.
2. **Fault Tolerance**: A failure on any single platform (e.g., invalid token or rate limit) does not halt or cancel posting to the remaining platforms.
3. **Integrated CTA URL Validation**: Enforces that every message contains exactly one valid Call-to-Action (CTA) link with an `http` or `https` scheme, and a maximum length of 200 characters.
4. **Standardized Response Contract**: Returns a uniform response structure (`ApiResponse` and `PlatformResult`) including status, published content URL, posting timestamp (UTC), and error details if a platform fails.

---

## Project Structure

```text
automated-posting/
├── app/
│   ├── main.py                  # FastAPI entry point & custom exception handler
│   ├── config.py                # Environment configuration via Pydantic BaseSettings
│   ├── schemas.py               # Pydantic request/response models & validators
│   ├── platforms/               # Platform integration adapters
│   │   ├── base.py              # BasePlatform abstract class & utilities
│   │   ├── telegram.py
│   │   ├── discord.py
│   │   ├── bluesky.py
│   │   ├── devto.py
│   │   └── mastodon.py
│   └── services/
│       └── posting_service.py   # Service orchestrator (async dispatch)
├── tests/                       # Comprehensive test suite (38 test cases)
│   ├── platforms/               # Mocked unit tests for each platform
│   ├── test_api.py              # FastAPI HTTP route tests
│   ├── test_base.py             # Utility and base class tests
│   ├── test_posting.py          # Service layer & fault tolerance tests
│   └── test_schemas.py          # Schema & Pydantic validation tests
├── .env.example                 # Environment configuration template
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Project dependencies
└── README.md
```

---

## Prerequisites
- **Python**: Version 3.12 or newer
- **Virtualenv** / **pip**

---

## Setup & Installation

### 1. Clone Repository & Navigate to Directory
```bash
git clone <repository-url>
cd automated-posting
```

### 2. Create & Activate Virtual Environment
- **macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **Windows (Command Prompt / PowerShell):**
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Environment Variables Configuration

Copy the `.env.example` template to `.env`:
```bash
cp .env.example .env
```

Open `.env` and fill in the configuration values with your credentials:

```ini
HTTP_TIMEOUT_SECONDS=60

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=@your_channel_or_chat_id

# Discord Configuration
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your/webhook/url

# Dev.to Configuration
DEVTO_API_KEY=your_devto_api_key_here

# Mastodon Configuration
MASTODON_ACCESS_TOKEN=your_mastodon_access_token_here
MASTODON_VISIBILITY=public

# Bluesky Configuration
BLUESKY_HANDLE=your_handle.bsky.social
BLUESKY_APP_PASSWORD=your_app_password_here
```

> **Note:** Never commit the `.env` file to your Git repository. Ensure `.env` is listed in `.gitignore`.

---

## Running the Application

Start the development server with Uvicorn on port `4000`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

The application will run on `http://localhost:4000`. You can explore and test the interactive API documentation at:
- **Swagger UI**: [http://localhost:4000/docs](http://localhost:4000/docs)
- **ReDoc**: [http://localhost:4000/redoc](http://localhost:4000/redoc)

---

## Running the Test Suite

This project includes 38 automated test cases covering schema validation, API routes, service fault tolerance, and isolated mocked platform integrations.

Run the test suite using pytest:
```bash
pytest -v
```

---

## Sample API Requests & Responses

### 1. Health Check (`GET /health`)

#### Request:
```bash
curl -X GET "http://localhost:4000/health" \
  -H "Accept: application/json"
```

#### Response (HTTP 200 OK):
```json
{
  "success": true,
  "results": null,
  "errors": null
}
```

---

### 2. Publish Post Success (`POST /posting`)

The message must be between 1 and 200 characters long and contain exactly **one valid CTA link** using an `http` or `https` scheme.

#### Request:
```bash
curl -X POST "http://localhost:4000/posting" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Check out our latest business platform and grow your online visibility. https://example.com"
  }'
```

#### Response (HTTP 200 OK):
```json
{
  "success": true,
  "results": [
    {
      "platform": "Telegram",
      "status": "success",
      "posted_url": "https://t.me/examplechannel/105",
      "public_access": true,
      "date": "2026-11-18",
      "time": "03:45:12",
      "error": null
    },
    {
      "platform": "Discord",
      "status": "success",
      "posted_url": "https://discord.com/channels/123456789/987654321/1122334455",
      "public_access": false,
      "date": "2026-11-18",
      "time": "03:45:12",
      "error": null
    },
    {
      "platform": "Bluesky",
      "status": "success",
      "posted_url": "https://bsky.app/profile/example.bsky.social/post/3lbt7wxgxrs2x",
      "public_access": true,
      "date": "2026-11-18",
      "time": "03:45:13",
      "error": null
    },
    {
      "platform": "Devto",
      "status": "success",
      "posted_url": "https://dev.to/example/check-out-our-latest-platform-123",
      "public_access": true,
      "date": "2026-11-18",
      "time": "03:45:14",
      "error": null
    },
    {
      "platform": "Mastodon",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "MASTODON_ACCESS_TOKEN or MASTODON_VISIBILITY is required"
    }
  ],
  "errors": null
}
```

> **Note on Live vs Unconfigured Posting:**
> - If you test this request **before configuring real credentials** in `.env`, the service will safely return HTTP 200 with `"success": false` and each platform will report `"status": "failed"` explaining which credential is missing (e.g., `"TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is required"`).
> - Once you configure valid credentials for one or more platforms in `.env`, those platforms will return `"status": "success"` with their live published URLs, and the root `"success"` flag will become `true`. Even if one platform fails, posting to the remaining platforms continues unaffected.

---

### 3. Validation Error 422 (`POST /posting`)

If the message does not contain a CTA link or includes more than one link, the request is rejected before contacting any platform.

#### Example Request (Missing CTA URL):
```bash
curl -X POST "http://localhost:4000/posting" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Release announcement without any link"
  }'
```

#### Response (HTTP 422 Unprocessable Entity):
```json
{
  "success": false,
  "results": null,
  "errors": [
    {
      "field": "message",
      "message": "Value error, message must contain exactly one CTA URL"
    }
  ]
}
```

#### Example Request (More Than One URL):
```bash
curl -X POST "http://localhost:4000/posting" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Visit https://site1.com and also https://site2.com"
  }'
```

#### Response (HTTP 422 Unprocessable Entity):
```json
{
  "success": false,
  "results": null,
  "errors": [
    {
      "field": "message",
      "message": "Value error, message must contain exactly one CTA URL"
    }
  ]
}
```

---

## Execution Logs & Implementation Evidence

### 1. Test Suite Execution Log (`pytest -v`)
```text
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-9.2.0, pluggy-1.7.0 -- /Users/.../.venv/bin/python3.12
rootdir: /Users/mochamadrizki/Documents/Dxora/Sources/automated-posting
configfile: pytest.ini
plugins: anyio-4.16.0, asyncio-1.5.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 38 items

tests/platforms/test_bluesky.py::test_bluesky_missing_credentials PASSED [  2%]
tests/platforms/test_bluesky.py::test_bluesky_publish_success PASSED     [  5%]
tests/platforms/test_bluesky.py::test_bluesky_publish_no_uri PASSED      [  7%]
tests/platforms/test_devto.py::test_devto_missing_api_key PASSED         [ 10%]
tests/platforms/test_devto.py::test_devto_publish_success PASSED         [ 13%]
tests/platforms/test_discord.py::test_discord_missing_webhook PASSED     [ 15%]
tests/platforms/test_discord.py::test_discord_publish_success PASSED     [ 18%]
tests/platforms/test_discord.py::test_discord_publish_without_ids PASSED [ 21%]
tests/platforms/test_mastodon.py::test_mastodon_missing_credentials PASSED [ 23%]
tests/platforms/test_mastodon.py::test_mastodon_invalid_visibility PASSED [ 26%]
tests/platforms/test_mastodon.py::test_mastodon_publish_public_success PASSED [ 28%]
tests/platforms/test_mastodon.py::test_mastodon_publish_private_success PASSED [ 31%]
tests/platforms/test_telegram.py::test_telegram_missing_credentials PASSED [ 34%]
tests/platforms/test_telegram.py::test_telegram_public_channel_success PASSED [ 36%]
tests/platforms/test_telegram.py::test_telegram_private_chat_success PASSED [ 39%]
tests/platforms/test_telegram.py::test_telegram_api_rejected PASSED      [ 42%]
tests/test_api.py::test_health_endpoint PASSED                           [ 44%]
tests/test_api.py::test_posting_endpoint_success PASSED                  [ 47%]
tests/test_api.py::test_posting_endpoint_validation_error_no_url PASSED  [ 50%]
tests/test_api.py::test_posting_endpoint_empty_body PASSED               [ 52%]
tests/test_base.py::test_now_default PASSED                              [ 55%]
tests/test_base.py::test_now_with_custom_timestamp PASSED                [ 57%]
tests/test_base.py::test_base_platform_failure PASSED                    [ 60%]
tests/test_posting.py::test_one_failure_does_not_stop_other_platforms PASSED [ 63%]
tests/test_posting.py::test_all_platforms_succeed PASSED                 [ 65%]
tests/test_posting.py::test_all_platforms_fail PASSED                    [ 68%]
tests/test_posting.py::test_empty_platforms_list PASSED                  [ 71%]
tests/test_posting.py::test_unexpected_exception_captured_as_failure PASSED [ 73%]
tests/test_schemas.py::test_extract_url_single_and_multiple PASSED       [ 76%]
tests/test_schemas.py::test_extract_url_strips_trailing_punctuation PASSED [ 78%]
tests/test_schemas.py::test_posting_request_valid PASSED                 [ 81%]
tests/test_schemas.py::test_posting_request_empty_or_whitespace PASSED   [ 84%]
tests/test_schemas.py::test_posting_request_exceeds_max_length PASSED    [ 86%]
tests/test_schemas.py::test_posting_request_missing_url PASSED           [ 89%]
tests/test_schemas.py::test_posting_request_multiple_urls PASSED         [ 92%]
tests/test_schemas.py::test_posting_request_invalid_scheme PASSED        [ 94%]
tests/test_schemas.py::test_posting_request_url_missing_hostname PASSED  [ 97%]
tests/test_schemas.py::test_api_response_and_error_detail_models PASSED  [100%]

============================== 38 passed in 0.83s ==============================
```

### 2. Server Startup Log (`uvicorn`)
```text
INFO:     Will watch for changes in: ['/Users/.../automated-posting']
INFO:     Uvicorn running on http://0.0.0.0:4000 (Press CTRL+C to quit)
INFO:     Started reloader process [14820] using WatchFiles
INFO:     Started server process [14822]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Security & Credentials

- **Zero Plaintext Secrets Principle**: All secrets and credentials (API tokens, app passwords, webhook URLs) must be managed exclusively through environment variables or the `.env` file.
- **Git Ignore**: The `.gitignore` file includes `.env` to prevent accidental commits of sensitive configuration:
  ```gitignore
  .env
  .venv
  __pycache__/
  .pytest_cache/
  ```
- **Placeholders Only**: All examples in this documentation use generic placeholders (`your_token_here`). Never commit or publish live credentials.
