# Build progress

| Phase | Status | Last commit | Notes |
|---|---|---|---|
| 0 Safety | complete | `dc1c420` | Deterministic localized safety closings. |
| 1 Sources and coverage | complete | `1c7b8bb` | Local PDFs restored, official HTML support added, 561 vectors indexed. |
| 2 Chroma and incremental ingestion | complete | `1c7b8bb` | Chroma is active with FAISS fallback; per-source chunk manifest exists. |
| 3 Retrieval, agent and tools | complete | `ba9baa7` | Coverage tools and existing grounded agent retained. |
| 4 API | complete | `ba9baa7` | Existing API plus `/coverage` and `/diseases`. |
| 5 Website | complete | `1c7b8bb` | React + Vite + TypeScript + Tailwind frontend with coverage, chat and safety UI. |
| 6 Telegram | complete | `ba9baa7` | Env-gated dry-run adapter; live polling intentionally disabled. |
| 7 Production | complete | `ba9baa7` | Dockerfile and compose deployment path added. |
| 8 Documentation | complete | `ba9baa7` | Privacy, safety, data TODO, download report, and this file exist. |
| 9 Tests and CI | complete | `1c7b8bb` | CI workflow added; 31 tests pass in 5.78s. |
| 10 Acceptance | partial | `1c7b8bb` | Build/index/frontend checks pass; Gemini evaluation stopped at 14/100 due HTTP 429 quota. |

## Exact next step

For future work, retry unreachable official sources with
`uv run python scripts/download_data.py --retry-unreachable`, then rebuild
incrementally with `uv run python scripts/build_index.py`.

## Latest verification

- `uv run pytest -q` -> `31 passed, 15 warnings in 5.78s`
- `uv run python scripts/build_index.py` -> `Done. Indexed 561 chunks.`
- `uv run python scripts/generate_eval.py` -> `wrote 100 questions`
- `uv run python scripts/evaluate.py` -> `Questions attempted: 14 / 100`; Gemini returned `429 RESOURCE_EXHAUSTED`.
- `Set-Location web; npm run build` -> Vite build succeeded; 15 modules transformed.
- `Set-Location web; npm run lint` -> TypeScript check succeeded.
