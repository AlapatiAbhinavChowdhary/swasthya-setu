# Swasthya Setu

[![CI](https://github.com/AlapatiAbhinavChowdhary/swasthya-setu/actions/workflows/ci.yml/badge.svg)](https://github.com/AlapatiAbhinavChowdhary/swasthya-setu/actions/workflows/ci.yml)

Swasthya Setu is a multilingual public-health awareness RAG assistant for
rural and semi-urban India. It uses local multilingual embeddings, FAISS, and
Gemini configured through the environment. It is **not a diagnostic or
treatment system**.

## Current agent flow

The agent is implemented as a LangGraph state graph:

1. A deterministic multilingual emergency check runs before any model call.
2. The intent router separates awareness questions from greetings and
   diagnosis/medication requests.
3. RAG questions are rewritten, retrieved from the local FAISS index, and
   answered from numbered context.
4. Citation verification removes citations that do not refer to retrieved
   passages and refuses unsupported answers.
5. Session memory retains the last six user/assistant turns.
6. Retrieval uses `scripts/calibrate_threshold.py` for score diagnostics. The
   current in-scope/out-of-scope distributions overlap, so embedding scores
   alone are not trusted; a relevance gate filters the retrieved passages.

See [docs/SAFETY.md](docs/SAFETY.md) for the safety flow and limitations.

## Setup (PowerShell)

```powershell
uv sync
Copy-Item .env.example .env
# Edit .env and set GEMINI_API_KEY and GEMINI_MODEL.
uv run python scripts/build_index.py
uv run python scripts/ask.py "What are the warning signs of severe dengue?"
```

`GEMINI_MODEL` is always used as supplied; no model name is hardcoded. Do not
commit `.env`, source PDFs, or `vectorstore/`.

To inspect retrieval score distributions:

```powershell
uv run python scripts/calibrate_threshold.py
```

## Safety behavior

Emergency messages such as heavy bleeding, difficulty breathing, unconsciousness,
convulsions, or a very sick child immediately return: go to the nearest
hospital or call 108. The assistant does not diagnose, prescribe medicines, or
provide doses. If retrieved sources do not support an answer, it directs the
user to a doctor, ASHA worker, or health centre.

The current repository contains the RAG core and CLI. API, frontend, structured
health tools, and deployment surfaces are intentionally separate follow-up
phases; no sample medical facts are presented as verified data.

## API (Phase 4)

Run the backend in PowerShell:

```powershell
uv run uvicorn swasthya_setu.api.app:app --reload
```

Endpoints are `GET /health`, `GET /sources`, `POST /chat`,
`POST /chat/stream` (SSE), and `POST /feedback`. The API keeps only hashed
session/message identifiers and feedback records in SQLite; do not include
personal medical details in feedback. Configure CORS, rate limits, cache
behavior, and the SQLite path through `.env`.