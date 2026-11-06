# Build progress

| Phase | Status | Last commit | Notes |
|---|---|---|---|
| 0 Safety | complete | `dc1c420` | Deterministic localized safety closings. |
| 1 Sources and coverage | complete | `a752ba8` | Three official manifest entries; two downloaded and indexed, NCVBDC unreachable. |
| 2 Chroma and incremental ingestion | complete | working tree | Chroma is active with FAISS fallback; incremental rebuild metadata exists. |
| 3 Retrieval, agent and tools | complete | working tree | Coverage tools and existing grounded agent retained. |
| 4 API | complete | working tree | Existing API plus `/coverage` and `/diseases`. |
| 5 Website | complete | working tree | Static coverage table in `web/index.html`. |
| 6 Telegram | complete | working tree | Env-gated dry-run adapter; live polling intentionally disabled. |
| 7 Production | complete | working tree | Dockerfile and compose deployment path added. |
| 8 Documentation | in progress | working tree | Privacy, safety, data TODO, download report, and this file exist. |
| 9 Tests and CI | complete | working tree | CI workflow added; 28 tests currently pass. |
| 10 Acceptance | pending | - | Run only after phases 1-9. |

## Exact next step

Run the final acceptance checks, review generated coverage, and commit the
remaining phase completion and documentation changes.
