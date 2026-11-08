# Build progress

| Phase | Status | Last commit | Notes |
|---|---|---|---|
| 0 Safety | complete | `dc1c420` | Deterministic localized safety closings verified by 19 safety tests. |
| 1 Sources and coverage | partial | working tree | Batch 1 acquired official documents for Immunization, Malaria, Dengue, and TB; 18 sources in manifest (10 disease-specific, 8 general), 1 unreachable logged with exact error. |
| 2 Chroma and incremental ingestion | partial | working tree | Chroma has 2,167 vectors indexed incrementally from verified official sources; zero-chunk scanned PDFs diagnosed. |
| 3 Retrieval, agent and tools | partial | working tree | Structured vaccination schedule built from verified NIS 2018 table; retrieval hit-rate@4 reached 58/100 filtered. |
| 4 API | partial | `1c7b8bb` | Existing endpoints plus `/coverage` and `/diseases`; streaming remains response-at-once. |
| 5 Website | partial | `1c7b8bb` | React + Vite + TypeScript + Tailwind frontend built; Playwright/browser checks unverified, lint is tsc only, tools missing, streaming not real. |
| 6 Telegram | partial | `ba9baa7` | Env-gated dry-run adapter; live polling intentionally disabled pending token. |
| 7 Production | partial | `ba9baa7` | Dockerfile and compose path added; deployment account and monitoring remain. |
| 8 Documentation | complete | `56776e3` | Privacy, safety, data TODO, download report, evaluation, progress, and comprehensive handoff verified by file inspection. |
| 9 Tests and CI | partial | working tree | 36 tests pass in 3.92s; offline test isolation confirmed with mocked LLM and temporary databases. |
| 10 Acceptance | partial | working tree | Retrieval evaluation reached 58/100 hit-rate@4 (6/6 on dengue, malaria, chikungunya, JE, kala-azar, filariasis, TB, Hep-B, measles; 4/4 on polio). |

## Exact next step

Next step: Batch 2 official source acquisition from WHO Fact Sheet Index (`https://www.who.int/news-room/fact-sheets`) for all target diseases in `data/diseases.yaml` lacking disease-specific sources. Fetch official HTML, extract article text, update sources and lockfile, incremental index build, test suite, and commit.

## Latest verification

- `uv run pytest` -> `36 passed, 15 warnings in 3.92s`
- `uv run python scripts/build_index.py` -> `Done. Indexed 2167 chunks.`
- `uv run python scripts/evaluate_retrieval.py` -> Chroma unfiltered `29/100`, disease-filtered `58/100`; hybrid RRF `31/100` unfiltered, `58/100` filtered.
- Structured vaccination schedule -> verified against Page 1 table in `data/raw/child-immunization/national-immunization-schedule-2018.pdf`.
- `data/sources.lock.json` -> 19 tracked sources (13 downloaded, 5 skipped/deduped, 1 unreachable).
