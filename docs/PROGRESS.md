# Build progress

| Phase | Status | Last commit | Notes |
|---|---|---|---|
| 0 Safety | complete | `dc1c420` | Deterministic localized safety closings. |
| 1 Sources and coverage | partial | working tree | Local PDFs restored and duplicate source content collapsed by SHA-256; official HTML support added. Discovery target and OCR coverage remain incomplete. |
| 2 Chroma and incremental ingestion | partial | working tree | Chroma has 191 unique vectors and no duplicate chunk text; scanned zero-text source still needs optional OCR validation. |
| 3 Retrieval, agent and tools | partial | working tree | Disease-filtered retrieval and offline Chroma/FAISS comparison are implemented; hybrid RRF is available but does not improve the current benchmark. |
| 4 API | partial | `1c7b8bb` | Existing endpoints plus `/coverage` and `/diseases`; streaming remains response-at-once. |
| 5 Website | complete | `1c7b8bb` | React + Vite + TypeScript + Tailwind frontend with coverage, chat and safety UI. |
| 6 Telegram | partial | `ba9baa7` | Env-gated dry-run adapter; live polling intentionally disabled pending token. |
| 7 Production | partial | `ba9baa7` | Dockerfile and compose path added; deployment account and monitoring remain. |
| 8 Documentation | complete | `1c7b8bb` | Privacy, safety, data TODO, download, evaluation, and progress docs exist. |
| 9 Tests and CI | partial | working tree | 31 tests pass in 5.05s; broader ingestion, evaluation, and browser coverage is still pending. |
| 10 Acceptance | partial | working tree | Retrieval-only evaluation ran for 100 questions; Gemini evaluation stopped at 14/100 due HTTP 429 quota. |

## Exact next step

Next step: add extraction diagnostics/optional OCR reporting for zero-chunk documents,
then complete the official-source discovery pass and browser validation. Gemini
evaluation can resume with `uv run python scripts/evaluate.py`.

## Latest verification

- `uv run pytest -q` -> `31 passed, 15 warnings in 5.05s`
- `uv run python scripts/build_index.py` -> `Done. Indexed 191 chunks.`
- `uv run python scripts/evaluate_retrieval.py` -> Chroma unfiltered `18/100`, disease-filtered `58/100`; FAISS matched both; hybrid RRF was `16/100` unfiltered and `58/100` filtered.
- Chroma verification -> `chunks 191`, `unique_texts 191`, four indexed source IDs.
- `uv run python scripts/generate_eval.py` -> `wrote 100 questions`
- `uv run python scripts/evaluate.py` -> `Questions attempted: 14 / 100`; Gemini returned `429 RESOURCE_EXHAUSTED`.
- `Set-Location web; npm run build` -> Vite build succeeded; 15 modules transformed.
- `Set-Location web; npm run lint` -> TypeScript check succeeded.
