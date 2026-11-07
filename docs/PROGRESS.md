# Build progress

| Phase | Status | Last commit | Notes |
|---|---|---|---|
| 0 Safety | complete | `dc1c420` | Deterministic localized safety closings verified by 19 safety tests. |
| 1 Sources and coverage | partial | `c4f6b27` | Local PDFs restored and duplicate source content collapsed by SHA-256; official HTML support added. Discovery target and OCR coverage remain incomplete. |
| 2 Chroma and incremental ingestion | partial | `c4f6b27` | Chroma has 191 unique vectors and no duplicate chunk text; scanned zero-text source still needs optional OCR validation. |
| 3 Retrieval, agent and tools | partial | `c4f6b27` | Disease-filtered retrieval and offline Chroma/FAISS comparison are implemented; structured tools (vaccination/alerts/facilities) not implemented; hybrid RRF does not improve current benchmark. |
| 4 API | partial | `1c7b8bb` | Existing endpoints plus `/coverage` and `/diseases`; streaming remains response-at-once. |
| 5 Website | partial | `1c7b8bb` | React + Vite + TypeScript + Tailwind frontend built; Playwright/browser checks unverified, lint is tsc only, tools missing, streaming not real. |
| 6 Telegram | partial | `ba9baa7` | Env-gated dry-run adapter; live polling intentionally disabled pending token. |
| 7 Production | partial | `ba9baa7` | Dockerfile and compose path added; deployment account and monitoring remain. |
| 8 Documentation | complete | `56776e3` | Privacy, safety, data TODO, download report, evaluation, progress, and comprehensive handoff verified by file inspection. |
| 9 Tests and CI | partial | `c4f6b27` | 31 tests pass in 4.62s; broader ingestion, evaluation, and browser coverage is still pending. |
| 10 Acceptance | partial | `c4f6b27` | Retrieval-only evaluation ran for 100 questions; Gemini evaluation stopped at 14/100 due HTTP 429 quota. |

## Exact next step

Next step: official source discovery starting with HTML pages (WHO fact-sheet index, NHP, *.gov.in/*.nic.in via crawl only, target 20+ diseases with 1+ disease-specific source and 10+ with 3+ sources), followed by extraction diagnostics and OCR for zero-chunk sources, covered-only retrieval evaluation, structured tools (verified schedule, DEMO alerts, SAMPLE facilities), real streaming, quota-aware evaluation, and ESLint/Playwright checks.

## Latest verification

- `uv run pytest -q` -> `31 passed, 15 warnings in 4.62s`
- `uv run pytest tests/test_safety.py` -> `19 passed, 15 warnings in 2.77s`
- `uv run python scripts/build_index.py` -> `Done. Indexed 191 chunks.`
- `uv run python scripts/evaluate_retrieval.py` -> Chroma unfiltered `18/100`, disease-filtered `58/100`; FAISS matched both; hybrid RRF was `16/100` unfiltered and `58/100` filtered.
- Chroma verification -> `chunks 191`, `unique_texts 191`, four indexed source IDs.
- `uv run python scripts/generate_eval.py` -> `wrote 100 questions`
- `uv run python scripts/evaluate.py` -> `Questions attempted: 14 / 100`; Gemini returned `429 RESOURCE_EXHAUSTED`.
- `Set-Location web; npm run build` -> Vite build succeeded; 15 modules transformed.
- `Set-Location web; npm run lint` -> TypeScript check succeeded (`tsc --noEmit`).
