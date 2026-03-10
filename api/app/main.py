import logging
import os
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from api.app.routes import router

app = FastAPI(title="EthosGuard API", version="0.1.0")
logger = logging.getLogger("ethosguard.api")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def _truncate(value: str, limit: int = 1200) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "...<truncated>"


def _allowed_origins() -> list[str]:
    raw = os.environ.get(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or ["http://localhost:3000", "http://127.0.0.1:3000"]


@app.middleware("http")
async def log_request_response(request: Request, call_next):
    started = time.perf_counter()
    raw_body = await request.body()
    request_payload = _truncate(raw_body.decode("utf-8", errors="ignore")) if raw_body else ""

    async def receive():
        return {"type": "http.request", "body": raw_body, "more_body": False}

    request = Request(request.scope, receive)
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started) * 1000, 2)

    chunks = []
    async for chunk in response.body_iterator:
        chunks.append(chunk)
    response_body = b"".join(chunks)
    response_payload = _truncate(response_body.decode("utf-8", errors="ignore")) if response_body else ""

    logger.info(
        "request_complete method=%s path=%s status=%s duration_ms=%s request=%s response=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_payload,
        response_payload,
    )

    headers = dict(response.headers)
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=headers,
        media_type=response.media_type,
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
