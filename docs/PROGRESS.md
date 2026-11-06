# Build progress

| Phase | Status | Last commit | Notes |
|---|---|---|---|
| 0 Safety | complete | `dc1c420` | Deterministic localized safety closings. |
| 1 Sources and coverage | complete | `a752ba8` | Three official manifest entries; two downloaded and indexed, NCVBDC unreachable. |
| 2 Chroma and incremental ingestion | complete | `6233708` | Chroma is active with FAISS fallback; incremental rebuild metadata exists. |
| 3 Retrieval, agent and tools | complete | `ba9baa7` | Coverage tools and existing grounded agent retained. |
| 4 API | complete | `ba9baa7` | Existing API plus `/coverage` and `/diseases`. |
| 5 Website | complete | `ba9baa7` | Static coverage table in `web/index.html`. |
| 6 Telegram | complete | `ba9baa7` | Env-gated dry-run adapter; live polling intentionally disabled. |
| 7 Production | complete | `ba9baa7` | Dockerfile and compose deployment path added. |
| 8 Documentation | complete | `ba9baa7` | Privacy, safety, data TODO, download report, and this file exist. |
| 9 Tests and CI | complete | `ba9baa7` | CI workflow added; 28 tests currently pass. |
| 10 Acceptance | complete | `ba9baa7` | Full tests, Chroma retrieval, coverage, compose config, and hygiene checks passed. |

## Exact next step

For future work, retry unreachable official sources with
`uv run python scripts/download_data.py --retry-unreachable`, then rebuild
incrementally with `uv run python scripts/build_index.py`.
