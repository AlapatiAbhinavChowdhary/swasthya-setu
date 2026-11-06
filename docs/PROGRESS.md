# Build progress

| Phase | Status | Last commit | Notes |
|---|---|---|---|
| 0 Safety | complete | `dc1c420` | Deterministic localized safety closings. |
| 1 Sources and coverage | complete | `a752ba8` | Three official manifest entries; two downloaded and indexed, NCVBDC unreachable. |
| 2 Chroma and incremental ingestion | in progress | working tree | Chroma is active with FAISS fallback; incremental rebuild metadata exists. |
| 3 Retrieval, agent and tools | pending | - | Existing agent is retained until Phase 2 migration is complete. |
| 4 API | in progress | working tree | Existing API plus `/coverage`; full API expansion remains. |
| 5 Website | pending | - | No frontend exists yet. |
| 6 Telegram | pending | - | No token required for mock/dry-run adapter. |
| 7 Production | pending | - | Deployment and observability files remain. |
| 8 Documentation | in progress | working tree | Privacy, safety, data TODO, download report, and this file exist. |
| 9 Tests and CI | pending | - | 26 tests currently pass; CI remains. |
| 10 Acceptance | pending | - | Run only after phases 1-9. |

## Exact next step

Commit the Chroma changes, merge Phase 1 into local `main`, then create
`feat/phase-2-chroma` from that merged main and continue retrieval evaluation.
