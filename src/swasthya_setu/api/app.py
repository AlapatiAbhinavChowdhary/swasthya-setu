"""FastAPI backend for the Swasthya Setu awareness agent."""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

from swasthya_setu.api.db import Database
from swasthya_setu.api.models import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    FeedbackResponse,
    SourceResponse,
)
from swasthya_setu.config import settings
from swasthya_setu.generation.agent import run_agent
from swasthya_setu.generation.chain import _store

logger = logging.getLogger(__name__)
_cache: dict[tuple[str, str | None], tuple[float, ChatResponse]] = {}
_requests: defaultdict[str, deque[float]] = defaultdict(deque)
CACHE_TTL_SECONDS = 300


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database = Database(settings.feedback_database)
    app.state.vectorstore = _store()
    yield


app = FastAPI(
    title="Swasthya Setu API",
    version="0.1.0",
    description="Verified public-health awareness API. Not for diagnosis or prescriptions.",
    lifespan=lifespan,
)
origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = uuid4().hex
    request.state.request_id = request_id
    started = time.perf_counter()
    response = await call_next(request)
    logger.info(json.dumps({
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "latency_ms": round((time.perf_counter() - started) * 1000),
    }))
    response.headers["X-Request-ID"] = request_id
    return response


def _request_key(request: Request, session_id: str | None) -> str:
    return f"{request.client.host if request.client else 'unknown'}:{session_id or ''}"


def _check_rate_limit(request: Request, session_id: str | None) -> None:
    key = _request_key(request, session_id)
    now = time.monotonic()
    bucket = _requests[key]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    bucket.append(now)


def _response_from_state(state: dict, request_id: str) -> ChatResponse:
    response = state["response"]
    return ChatResponse(
        answer=response["answer"],
        citations=state.get("citations", []),
        sources=[SourceResponse(**source) for source in response["sources"]],
        intent=response["intent"],
        language=response["language"],
        emergency=response["emergency"],
        language_consistent=response["language_consistent"],
        request_id=request_id,
    )


def _run_chat(request: Request, payload: ChatRequest) -> ChatResponse:
    _check_rate_limit(request, payload.session_id)
    session_id = payload.session_id or uuid4().hex
    cache_key = (payload.message, payload.language)
    cached = _cache.get(cache_key)
    if cached and time.monotonic() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1].model_copy(update={"request_id": request.state.request_id})
    try:
        state = run_agent(payload.message, session_id, payload.language)
    except (TimeoutError, ConnectionError, ChatGoogleGenerativeAIError) as exc:
        logger.warning("request_id=%s upstream_error=%s", request.state.request_id, type(exc).__name__)
        raise HTTPException(status_code=503, detail="The health assistant is temporarily unavailable.") from exc
    response = _response_from_state(state, request.state.request_id)
    app.state.database.record_message(session_id, "user", payload.message)
    app.state.database.record_message(session_id, "assistant", response.answer)
    _cache[cache_key] = (time.monotonic(), response)
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/sources")
def sources() -> dict[str, str]:
    path = Path("data/SOURCES.md")
    return {"content": path.read_text(encoding="utf-8") if path.exists() else ""}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    return _run_chat(request, payload)


@app.post("/chat/stream")
def chat_stream(payload: ChatRequest, request: Request) -> StreamingResponse:
    response = _run_chat(request, payload)
    data = response.model_dump_json()

    def events():
        yield f"event: message\ndata: {data}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@app.post("/feedback", response_model=FeedbackResponse)
def feedback(payload: FeedbackRequest, request: Request) -> FeedbackResponse:
    _check_rate_limit(request, payload.session_id)
    app.state.database.record_feedback(
        payload.session_id,
        payload.rating == "up",
        payload.comment,
        request.state.request_id,
    )
    return FeedbackResponse(accepted=True, request_id=request.state.request_id)
