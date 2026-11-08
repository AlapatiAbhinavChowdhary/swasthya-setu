# Build progress

| Phase | Status | Last commit | Notes |
|---|---|---|---|
| 0 Safety | complete | `dc1c420` | Deterministic localized safety closings verified by 19 safety tests. |
| 1 Sources and coverage | partial | working tree | Batch 1 & 2 complete: 53 sources in manifest (45 disease-specific, 8 general). 30/30 target diseases now have verified official disease-specific documentation. |
| 2 Chroma and incremental ingestion | partial | working tree | Chroma has 2,623 vectors indexed incrementally from verified official sources; 35 official WHO fact sheets embedded. |
| 3 Retrieval, agent and tools | partial | `c3a3d5a` | Structured vaccination schedule built from verified NIS 2018 table; retrieval hit-rate@4 reached 58/100 filtered. |
| 4 API | partial | `1c7b8bb` | Existing endpoints plus `/coverage` and `/diseases`; streaming remains response-at-once. |
| 5 Website | partial | `1c7b8bb` | React + Vite + TypeScript + Tailwind frontend built; Playwright/browser checks unverified, lint is tsc only, tools missing, streaming not real. |
| 6 Telegram | partial | `ba9baa7` | Env-gated dry-run adapter; live polling intentionally disabled pending token. |
| 7 Production | partial | `ba9baa7` | Dockerfile and compose path added; deployment account and monitoring remain. |
| 8 Documentation | complete | `56776e3` | Privacy, safety, data TODO, download report, evaluation, progress, and comprehensive handoff verified by file inspection. |
| 9 Tests and CI | partial | working tree | 36 tests pass in 4.21s; offline test isolation confirmed with mocked LLM and temporary databases. |
| 10 Acceptance | partial | `c3a3d5a` | Retrieval evaluation reached 58/100 hit-rate@4 (6/6 on dengue, malaria, chikungunya, JE, kala-azar, filariasis, TB, Hep-B, measles; 4/4 on polio). |

## Exact next step

Next step: Batch 3 official source acquisition from Indian government domains (*.gov.in / *.nic.in) such as NCVBDC, NCDC, NHM, NTEP, NACO, ICMR for target diseases with under 3 official sources, aiming for 3+ sources on 10+ diseases. Rebuild index, verify with pytest, commit and push.

## Latest verification

- `uv run pytest` -> `36 passed, 15 warnings in 4.21s`
- `uv run python scripts/build_index.py` -> `Done. Indexed 2623 chunks.` (Kept 35 of 35 pages, Created 456 chunks).
- `Coverage check` -> 30/30 target diseases have indexed documents.
- `data/sources.lock.json` -> 54 tracked sources.
- Structured vaccination schedule -> verified against Page 1 table in `data/raw/child-immunization/national-immunization-schedule-2018.pdf`.
