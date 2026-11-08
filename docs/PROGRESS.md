# Build progress

| Phase | Status | Last commit | Notes |
|---|---|---|---|
| 0 Safety | complete | `dc1c420` | Deterministic localized safety closings verified by 19 safety tests. |
| 1 Sources and coverage | complete | working tree | All 3 Batches complete: 73 sources in manifest (65 disease-specific, 8 general). 30/30 target diseases have verified official disease-specific documentation (target was 20+), and 10 diseases have 3+ official disease-specific sources (target was 10+). |
| 2 Chroma and incremental ingestion | complete | working tree | Chroma has 3,669 vectors indexed incrementally from verified official sources; all 30 diseases indexed with real content. |
| 3 Retrieval, agent and tools | partial | `c3a3d5a` | Structured vaccination schedule built from verified NIS 2018 table; retrieval hit-rate@4 reached 58/100 filtered. |
| 4 API | partial | `1c7b8bb` | Existing endpoints plus `/coverage` and `/diseases`; streaming remains response-at-once. |
| 5 Website | partial | `1c7b8bb` | React + Vite + TypeScript + Tailwind frontend built; Playwright/browser checks unverified, lint is tsc only, tools missing, streaming not real. |
| 6 Telegram | partial | `ba9baa7` | Env-gated dry-run adapter; live polling intentionally disabled pending token. |
| 7 Production | partial | `ba9baa7` | Dockerfile and compose path added; deployment account and monitoring remain. |
| 8 Documentation | complete | `56776e3` | Privacy, safety, data TODO, download report, evaluation, progress, and comprehensive handoff verified by file inspection. |
| 9 Tests and CI | complete | working tree | 36 tests pass in 4.21s; offline test isolation confirmed with mocked LLM and temporary databases. |
| 10 Acceptance | partial | `c3a3d5a` | Retrieval evaluation reached 58/100 hit-rate@4 (6/6 on dengue, malaria, chikungunya, JE, kala-azar, filariasis, TB, Hep-B, measles; 4/4 on polio). |

## Exact next step

Next step: extraction diagnostics and OCR validation for zero-chunk sources, covered-only retrieval evaluation across all 30 indexed diseases, structured tools (vaccination schedule tool, DEMO alerts, SAMPLE facilities), real incremental SSE streaming, and frontend Playwright integration tests.

## Latest verification

- `uv run pytest -q` -> `36 passed, 15 warnings in 4.21s`
- `uv run python scripts/build_index.py` -> `Done. Indexed 3669 chunks.`
- `Coverage check` -> 30/30 target diseases have indexed documents; 10 diseases have 3+ disease-specific sources.
- `data/sources.lock.json` -> 74 tracked sources (all official *.gov.in, *.nic.in, who.int).
- Structured vaccination schedule -> verified against Page 1 table in `data/raw/child-immunization/national-immunization-schedule-2018.pdf`.
