# Build progress

| Phase / Step | Status | Last commit | Notes |
|---|---|---|---|
| **Step 1: Index Discrepancy & Shrink Guard** | complete | `fix/index-and-tb` | Diagnosed Chroma index (3,633 chunks, 75 raw files: 40 PDFs, 35 WHO HTMLs across 30 diseases); fixed outdated counts in `docs/FINAL_ACCEPTANCE.md`; added `--allow-shrink` guard to `scripts/build_index.py` with unit tests. |
| **Step 2: TB Answer & Cross-Disease Retrieval Filter** | in progress | `fix/index-and-tb` | Filter cross-disease contamination in retrieval; plain-language simple-words synthesis without unexplained acronyms; support check. |
| **Step 3: Fresh Evaluation Set & Independence** | pending | `fix/index-and-tb` | Label 140 dev set, generate fresh blind 40 emergency / 40 non-emergency / 30 Rx queries, audit 100 awareness questions, reconcile refusal numbers. |
| **Step 4: Wrap-Up, CI Verification & Main Merge** | pending | `fix/index-and-tb` | Sync docs, push branch, verify CI green, merge to `main`. |

---

## Exact Next Step

Implement disease-filtered retrieval to prevent irrelevant cross-disease documents (e.g. JE STG) from leaking into TB answers; implement plain-language answer rules for 'simple words' queries.
