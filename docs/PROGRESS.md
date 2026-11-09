# Build progress

| Phase / Step | Status | Last commit | Notes |
|---|---|---|---|
| **Step 1: Failure Investigation & Root Cause** | complete | `61e328e` | Investigated all 14 failure cases in `eval/results.jsonl`; distinguished labeling/boundary issues from real missing tokens (infant fever, cyanosis, poison, Hinglish). |
| **Step 2: Safety & Evaluation Hardening** | complete | `61e328e` | Extended deterministic English, Hindi, and Hinglish emergency & prescription patterns; added second-net escalation; verified 100% recall on 30 held-out emergencies, 100% refusal on 20 held-out Rx, 100% block on 8 held-out injections. |
| **Step 3: Honest Programmatic Evaluation** | complete | `7f93905` | Evaluated 140 benchmark queries with programmatic target checking: 100% emergency recall, 100% dose refusal, 0 dose leaks, 100% citation validity, 98.3% expected refusal, 5.0% unexpected refusal. Added honest metric limitations. |
| **Step 4: Web Theme & Contrast Verification** | complete | `5605204` | Asserted light/dark container backgrounds differ, primary button styled, and text & button contrast >= 4.5:1. Regenerated 36 screenshots; 0 critical or serious automated violations in axe. |
| **Step 5: Owed Acceptance & Durations** | complete | `fix/final-eval` | Printed 11 acceptance criteria results, verified TB queries under drug name policy, and confirmed pytest suite with durations. |
| **Step 6: Docs, CI Verification & Main Merge** | in progress | `fix/final-eval` | Updated `docs/DEMO_SCRIPT.md` with spoken sample-data disclaimers, updated `docs/LIMITATIONS.md` with exact recall/refusal metrics, sync handoff, confirm CI on `fix/final-eval`, merge to `main`. |

---

## Programmatic Benchmark Evaluation Results Summary (140 Questions)

- **Total Questions Evaluated**: 140
- **Emergency Recall Rate**: **100.0%** (10/10 benchmark, 30/30 held-out) (Target: 100.0%) -> **PASS**
- **Dose / Prescription Refusal Rate**: **100.0%** (15/15 benchmark, 20/20 held-out) (Target: 100.0%) -> **PASS**
- **Prompt Injection Compliance**: **0.0%** (0/10 complied) (Target: 0.0%) -> **PASS**
- **Dose-Leak Count**: **0** (Target: 0) -> **PASS**
- **Citation Validity Rate**: **100.0%** (Target: 100.0%) -> **PASS**
- **Expected Refusal Rate (Out-of-Scope & Rx)**: **98.3%** (59 / 60) (Target: >= 95.0%) -> **PASS**
- **Unexpected Refusal Rate (In-Scope)**: **5.0%** (3 / 60) (Target: <= 5.0%) -> **PASS**
- **Language Consistency Rate**: **98.6%** (138 / 140) (Target: >= 95.0%) -> **PASS**
- **Lexical Support Rate (Overlap-based; not entailment)**: **95.8%** (Target: >= 85.0%) -> **PASS**
- **Server-Side Latency**: Median **6.32s**, P90 **20.84s**
- **Wall-Clock Latency (with rate throttling)**: Median **12.82s**, P90 **27.34s**
- **Average Gemini Calls / Question**: **1.67** ($\le 2.5$) -> **PASS**
- **Relevance Gate Share**: **38.6%**

---

## Exact Next Step

Run pytest with durations, commit and push docs sync on `fix/final-eval`, verify CI run on GitHub Actions, fast-forward merge `fix/final-eval` to `main`, and push `main`.
