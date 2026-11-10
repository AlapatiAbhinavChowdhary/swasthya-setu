# Build progress

| Phase / Step | Status | Last commit | Notes |
|---|---|---|---|
| **Step 1: Index Discrepancy & Shrink Guard** | complete | `fix/index-and-tb` | Diagnosed Chroma index (3,633 chunks, 75 raw files: 40 PDFs, 35 WHO HTMLs across 30 diseases); fixed outdated counts in `docs/FINAL_ACCEPTANCE.md`; added `--allow-shrink` guard to `scripts/build_index.py` with unit tests. |
| **Step 2: TB Answer & Cross-Disease Retrieval Filter** | complete | `fix/index-and-tb` | Added `disease_filter.py` with multi-lingual patterns; filtered cross-disease documents in `_retrieve` and `verify_citations`; verified plain-language simple-words answers for TB in English and Hindi citing WHO fact sheet with zero cross-disease leakage; 4 tests pass. |
| **Step 3: Fresh Evaluation Set & Independence** | complete | `fix/index-and-tb` | Labeled 140 benchmark as development set in `docs/EVALUATION.md`; generated fresh realistic 110-query set and ran once without tuning (45% emergency recall on colloquial/typos, 0% FP, 33.3% Rx refusal); verified 100/100 ordinary awareness questions passed in false-positive audit across all 30 diseases; reconciled 3 in-scope refusals and 1 triaged query in dev set. |
| **Step 4: Wrap-Up, CI Verification & Main Merge** | in progress | `fix/index-and-tb` | Sync `docs/HANDOFF.md`, `docs/FINAL_ACCEPTANCE.md`, push branch, verify CI green on GitHub Actions, merge `fix/index-and-tb` to `main`, push `main`. |

---

## Exact Next Step

Sync `docs/HANDOFF.md` and `docs/FINAL_ACCEPTANCE.md`, run pytest with durations, commit and push `fix/index-and-tb`, verify CI run passes on GitHub Actions, merge fast-forward to `main`, push `main`, and verify CI green on `main`.
