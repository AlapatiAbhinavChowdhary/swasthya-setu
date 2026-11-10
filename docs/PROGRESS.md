# Build progress

| Phase / Step | Status | Last commit | Notes |
|---|---|---|---|
| **Step 1: Index Discrepancy & Shrink Guard** | complete | `fix/index-and-tb` | Diagnosed Chroma index (3,633 chunks, 75 raw files: 40 PDFs, 35 WHO HTMLs across 30 diseases); fixed outdated counts in `docs/FINAL_ACCEPTANCE.md`; added `--allow-shrink` guard to `scripts/build_index.py` with unit tests. |
| **Step 2: TB Answer & Cross-Disease Retrieval Filter** | complete | `fix/index-and-tb` | Added `disease_filter.py` with multi-lingual patterns; filtered cross-disease documents in `_retrieve` and `verify_citations`; verified plain-language simple-words answers for TB in English and Hindi citing WHO fact sheet with zero cross-disease leakage; 4 tests pass. |
| **Step 3: Fresh Evaluation Set & Independence** | in progress | `fix/index-and-tb` | Label 140 dev set, generate fresh blind 40 emergency / 40 non-emergency / 30 Rx queries, audit 100 awareness questions, reconcile refusal numbers. |
| **Step 4: Wrap-Up, CI Verification & Main Merge** | pending | `fix/index-and-tb` | Sync docs, push branch, verify CI green, merge to `main`. |

---

## Exact Next Step

Execute Step 3: label 140 benchmark as development set in `docs/EVALUATION.md`, generate fresh independent evaluation set (40 emergency, 40 non-emergency, 30 Rx/dose) without pattern leaking, execute one-shot evaluation, run 100 awareness questions false-positive audit, and reconcile refusal metrics.
