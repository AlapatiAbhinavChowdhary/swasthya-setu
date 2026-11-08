# Build progress

| Phase | Status | Last commit | Notes |
|---|---|---|---|
| 0 Safety | complete | `dc1c420` | Deterministic localized safety closings, emergency checks, and deterministic post-generation numeric dose filter verified by safety suite. |
| 1 Sources and coverage | complete | `93e9297` | 72 official sources in manifest. 30/30 target diseases have verified official disease-specific documentation, and 10 diseases have 3+ official disease-specific sources. Unique document counting enforced by content hash. |
| 2 Chroma and incremental ingestion | complete | `93e9297` | Chroma has 3,559 vectors indexed from verified official sources; all 30 diseases indexed with real content. HTML loader isolates article body wrapper, truncates at WHO response/references, with strictly 0 boilerplate tokens in vectorstore. |
| 3 Retrieval, agent and tools | complete | `93e9297` | Deterministic dose filter blocks numeric doses; structured `vaccination_schedule(age)` tool implemented; outdated sources excluded from vaccination queries; strategy documents demoted below guidelines; hybrid BM25+RRF reaches 97.0% hit-rate@4. |
| 4 API | complete | `93e9297` | Endpoints: `GET /health` (with llm_configured flag), `GET /sources`, `GET /coverage`, `GET /diseases`, `GET /vaccination` (with optional age_months filter), `POST /chat`, `POST /chat/stream`, and `POST /feedback`. |
| 5 Website | partial | `1c7b8bb` | React + Vite + TypeScript + Tailwind frontend built; Playwright/browser checks unverified, lint is tsc only, live facility tools missing, streaming not real. |
| 6 Telegram | partial | `ba9baa7` | Env-gated dry-run adapter; live polling intentionally disabled pending token. |
| 7 Production | partial | `ba9baa7` | Dockerfile and compose path added; deployment account and monitoring remain. |
| 8 Documentation | complete | `56776e3` | Privacy, safety, data TODO, download report, retrieval evaluation, progress, and comprehensive handoff verified. |
| 9 Tests and CI | complete | `93e9297` | 45 tests pass in 4.10s; offline test isolation confirmed with mocked LLM and temporary databases; GitHub Actions CI workflow green for both python and web jobs (Run 42458655523). |
| 10 Acceptance | partial | `93e9297` | Retrieval-only evaluation reached 97.0% hit-rate@4 across covered diseases (100% on 15 of 17 evaluated diseases). Gemini end-to-end evaluation remaining. |

## Exact next step

Next step: Step 2: Honest Depth and OCR (low-chunk audit table, OCR fallback behind config flag, and chunk count difference accounting).

## Latest verification

- `uv run pytest` -> `46 passed, 15 warnings in 4.13s`
- Step 1 Answer Quality verified:
  - Closing safety line sits in its own paragraph (`\n\n`) preceding fixed message, never glued to bullets (verified by `test_closing_safety_line_sits_in_own_paragraph`).
  - TB plain-words answer backed sentence-by-sentence by chunk lexical support check; ungrounded RNTCP claim dropped; curable and course duration cited.
  - Malaria symptoms answer capped at ~3 common symptoms (Fever, Headache, Chills) with warning signs in separate list.
  - WHO HTML sections segmented by `<h2>`/`<h3>` with informative `page_label` (e.g. `Malaria > Symptoms`, `Tuberculosis > Treatment`), and API returning `publisher`, `year`, `url`.
- `npm --prefix web run build && npm --prefix web run lint` -> `Build and lint clean (0 errors)`
- `Forbidden boilerplate check over 3,559 chunks` -> `Newsroom: 0, Select language: 0, Emergencies: 0, Disease Outbreak News: 0, Member States: 0, cookie: 0`
- `Red-team safety evaluation` -> 7/7 questions passed: 5 personal dose/regimen requests refused; 1 dengue painkiller awareness question warning against aspirin/ibuprofen; 1 simple TB treatment question without numeric doses.
- `Threshold calibration` -> `in_scope min=0.7610`, `out_of_scope max=0.7492` (threshold 0.75 cleanly separates in-scope vs out-of-scope).
- `Retrieval evaluation (covered)` -> 97.0% hit-rate@4 for Chroma Hybrid Filtered (90.0% dense unfiltered, 96.0% dense filtered).
- `Coverage check` -> 30/30 target diseases have indexed documents; `specific` <= `documents` strictly guaranteed by content hash deduplication.
