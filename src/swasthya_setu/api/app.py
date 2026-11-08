"""FastAPI backend for the Swasthya Setu awareness agent."""

from __future__ import annotations

import json
import logging
import re
import secrets
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

from swasthya_setu.api.db import Database
from swasthya_setu.api.models import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    FeedbackResponse,
    SourceResponse,
)
from swasthya_setu.config import check_llm_configured, get_settings, settings
from swasthya_setu.coverage import get_coverage
from swasthya_setu.generation.agent import run_agent
from swasthya_setu.generation.chain import _store

logger = logging.getLogger(__name__)
_cache: dict[tuple[str, str | None], tuple[float, ChatResponse]] = {}
_requests: defaultdict[str, deque[float]] = defaultdict(deque)
CACHE_TTL_SECONDS = 300
_PAGE_RESIDUE = re.compile(r"(?m)^\s*(?:page\s+)?\d+\s*$", re.IGNORECASE)
_INFOGRAPHIC_MARKS = re.compile(r"(?m)^\s*[•▪◦■□]+\s*$")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database = Database(settings.feedback_database)
    is_configured, missing_var = check_llm_configured()
    app.state.llm_configured = is_configured
    app.state.llm_missing_var = missing_var
    if not is_configured:
        logger.warning(
            "Required LLM setting '%s' is missing or set to a placeholder.",
            missing_var,
        )
    try:
        app.state.vectorstore = _store()
    except Exception as exc:
        logger.warning("Vectorstore initialization skipped: %s", exc)
        app.state.vectorstore = None
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


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, _exc: RequestValidationError):
    language = request.headers.get("accept-language", "").lower()
    if language.startswith("hi"):
        message = "कृपया सही संदेश और अनुरोध विवरण भेजें।"
    else:
        message = "Please provide a valid message and request."
    return JSONResponse(status_code=422, content={"detail": message})


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
    sources = []
    for number, source in zip(state.get("citations", []), response["sources"]):
        snippet = _PAGE_RESIDUE.sub("", source["snippet"])
        snippet = _INFOGRAPHIC_MARKS.sub("", snippet).strip()
        snippet = re.sub(r"\s+", " ", snippet).strip()
        if len(snippet) > 240:
            snippet = snippet[:240].rsplit(" ", 1)[0].rstrip(" .,;:") + "..."
        sources.append(SourceResponse(
            number=number,
            source=source["source"],
            page=source["page"],
            snippet=snippet,
            publisher=source.get("publisher"),
            year=source.get("year"),
            url=source.get("url"),
        ))
    return ChatResponse(
        answer=response["answer"],
        citations=state.get("citations", []),
        sources=sources,
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
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "llm_configured": getattr(app.state, "llm_configured", False),
    }


@app.get("/sources")
def sources() -> dict[str, str]:
    path = Path("data/SOURCES.md")
    return {"content": path.read_text(encoding="utf-8") if path.exists() else ""}


@app.get("/coverage")
def coverage() -> dict:
    return get_coverage()


@app.get("/diseases")
def diseases() -> dict:
    return get_coverage()


@app.get("/vaccination")
def get_vaccination(age_months: int | None = None) -> dict[str, Any]:
    from swasthya_setu.tools import vaccination_schedule
    return vaccination_schedule(age_months=age_months)


@app.get("/alerts")
def get_alerts(
    district: str | None = None,
    state: str | None = None,
    disease: str | None = None,
    language: str = "en",
) -> dict[str, Any]:
    from swasthya_setu.tools import outbreak_alerts
    return outbreak_alerts(district=district, state=state, disease=disease, language=language)


@app.get("/facilities")
def get_facilities(
    district: str | None = None,
    state: str | None = None,
    language: str = "en",
) -> dict[str, Any]:
    from swasthya_setu.tools import find_hospital
    return find_hospital(district=district, state=state, language=language)


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    return _run_chat(request, payload)


def split_into_sentence_chunks(text: str) -> list[str]:
    """Split verified text into sentence or paragraph chunks, strictly preserving all whitespace."""
    if not text:
        return []
    pattern = re.compile(r"([^.!?।\n]+(?:[.!?।]+(?:\s*|$)|(?:\n+|$))|[\n]+)")
    chunks = pattern.findall(text)
    if not chunks or "".join(chunks) != text:
        return [text]
    return chunks


@app.post("/chat/stream")
def chat_stream(payload: ChatRequest, request: Request) -> StreamingResponse:
    # 1. Run the FULL pipeline first (safety, intent, retrieval, verification, dose filter, closing safety line)
    response = _run_chat(request, payload)

    def events():
        # 2. Stream verified sentence chunks as multiple SSE message events
        chunks = split_into_sentence_chunks(response.answer)
        for chunk in chunks:
            data = json.dumps({"chunk": chunk}, separators=(",", ":"))
            yield f"event: message\ndata: {data}\n\n"

        # 3. Final event with sources, intent, and flags
        meta = {
            "sources": [s.model_dump() for s in response.sources],
            "intent": response.intent,
            "emergency": response.emergency,
            "language": response.language,
            "language_consistent": response.language_consistent,
            "request_id": response.request_id,
        }
        yield f"event: metadata\ndata: {json.dumps(meta, separators=(',', ':'))}\n\n"

        # 4. Terminal done event
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@app.get("/languages")
def get_languages() -> dict[str, Any]:
    return {
        "languages": [
            {"code": "en", "name": "English", "native_name": "English", "status": "supported"},
            {"code": "hi", "name": "Hindi", "native_name": "हिन्दी", "status": "supported"},
            {"code": "or", "name": "Odia", "native_name": "ଓଡ଼ିଆ", "status": "draft"},
            {"code": "pa", "name": "Punjabi", "native_name": "ਪੰਜਾਬੀ", "status": "draft"},
        ]
    }


@app.get("/admin/feedback")
def get_admin_feedback(
    request: Request,
    authorization: str | None = Header(default=None),
    x_admin_token: str | None = Header(default=None),
) -> dict[str, Any]:
    current_settings = get_settings()
    if not current_settings.admin_token:
        raise HTTPException(status_code=404, detail="Admin feedback route is disabled.")

    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_admin_token:
        token = x_admin_token.strip()

    if not token or not secrets.compare_digest(token, current_settings.admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    records = app.state.database.list_feedback()
    return {"feedback": records, "count": len(records)}


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


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    current_settings = get_settings()
    if not getattr(current_settings, "enable_frontend", False):
        raise HTTPException(status_code=404, detail="Not Found")
    dist_dir = Path(__file__).resolve().parents[3] / "web" / "dist"
    if not dist_dir.exists():
        raise HTTPException(status_code=404, detail="Frontend build directory not found.")
    target = dist_dir / full_path
    if full_path and target.is_file():
        return FileResponse(target)
    index_file = dist_dir / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Frontend index.html not found.")
