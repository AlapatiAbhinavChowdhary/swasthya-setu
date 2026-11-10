# Build progress

| Phase / Step | Status | Last commit | Notes |
|---|---|---|---|
| **Step 1: Dev Set Baseline & Leak Analysis** | complete | `fix/triage` | Analyzed all 22 missed emergencies and 20 unrefused prescriptions from fresh evaluation set (now dev set). Verified leak count across all 20 unrefused prescription answers: strictly 0 dose leaks, 0 frequency leaks, 0 personal drug choices, 0 self-medication advice. Cached in `eval/fresh_failures_baseline.jsonl`. |
| **Step 2 & 3: Triage Normalizer, Fuzzy Matching & Merged Router** | complete | `fix/triage` | Created `triage_normalizer.py` with Unicode NFC normalization, 3+ repeat collapsing, SMS typo dictionary, and rapidfuzz Levenshtein matching on high-urgency tokens. Added acute emergency overrides in `safety.py`. Upgraded `agent.py` to single-call `route_rewrite_prompt` (INTENT, URGENCY, ASKS_MEDICINE_OR_DOSE, QUERY). Refined prescription regexes with awareness exemptions (dengue paracetamol awareness, TB 6 months, NIS vaccine schedule, ORS fluid dilution). Added post-generation dose verification net. |
| **Step 4: ORS & Liquid Volume Safety + Official Discovery** | complete | `fix/triage` | Extended `_NUMERIC_DOSE_PATTERN` negative lookahead to permit ORS/water preparation volumes (1000 ml, 1 litre, 500 ml) without triggering dose refusal. Discovered and downloaded 4 official PDFs (*.gov.in / who.int): NCDC Heat Illness Plan (8.3MB), NDMA Heat Wave Guidelines (7.6MB), WHO SEAR Snakebite Guidelines (26.0MB), WHO Diarrhoea Treatment Manual (1.1MB). Rebuilt Chroma index: 3,633 -> 4,632 chunks (+999 chunks). Verified heat and snakebite grounding. |
| **Step 5: Unseen Independent Evaluation Set** | complete | `fix/triage` | Created independent 110-query unseen set (40 emergencies, 40 look-alikes, 30 prescriptions with typos, Hinglish, acute crises). Evaluated once: Emergency Recall 100.0% (40/40, target >= 90%), Look-alike FP Rate 0.0% (0/40, target <= 5%), Prescription Refusal 100.0% (30/30, target >= 95%), Leaks 0 (target 0). |
| **Step 6: Safe Fallbacks & Persistent Notice** | complete | `fix/triage` | Added persistent visible 108 emergency notice banner with click-to-call link on Chat page (`web/src/pages/Chat.tsx`). Added Playwright e2e assertion in `web/e2e/app.spec.ts`. Updated `docs/LIMITATIONS.md` explaining best-effort colloquial triage and persistent banner fallback. |
| **Step 7: Verification, Offline Tests & CI** | complete | `fix/triage` | All 78 pytest unit/integration tests pass in 5.3s offline. Web frontend builds cleanly (`tsc -b && vite build`). Playwright e2e suite passes all 24 specs (2 skipped for live LLM key). Merge `fix/triage` to `main`. |

---

## Exact Resume Point

All 7 triage hardening steps verified and complete. Ready to commit on `fix/triage`, push branch, merge fast-forward to `main`, and push `main`.
