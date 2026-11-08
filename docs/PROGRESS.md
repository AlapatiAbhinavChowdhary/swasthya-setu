# Build progress

| Phase | Status | Last commit | Notes |
|---|---|---|---|
| 0 Safety | complete | `dc1c420` | Deterministic localized safety closings, emergency checks, and deterministic post-generation numeric dose filter verified by safety suite. |
| 1 Sources and coverage | complete | `93e9297` | 72 official sources in manifest. 30/30 target diseases have verified official disease-specific documentation, and 10 diseases have 3+ official disease-specific sources. Unique document counting enforced by content hash. |
| 2 Chroma and incremental ingestion | complete | `93e9297` | Chroma has 3,559 vectors indexed from verified official sources; all 30 diseases indexed with real content. HTML loader isolates article body wrapper, truncates at WHO response/references, with strictly 0 boilerplate tokens in vectorstore. |
| 3 Retrieval, agent and tools | complete | `93e9297` | Deterministic dose filter blocks numeric doses; structured `vaccination_schedule(age)` tool implemented; outdated sources excluded from vaccination queries; strategy documents demoted below guidelines; hybrid BM25+RRF reaches 97.0% hit-rate@4. |
| 4 API | complete | `93e9297` | Endpoints: `GET /health` (with llm_configured flag), `GET /sources`, `GET /coverage`, `GET /diseases`, `GET /vaccination` (with optional age_months filter), `POST /chat`, `POST /chat/stream`, and `POST /feedback`. |
| 5 Website | partial | `1c7b8bb` | React + Vite + TypeScript + Tailwind frontend built; Playwright/browser checks unverified, lint is tsc only, live facility tools missing, streaming not real. |
| 6 Telegram | partial | `ba9baa7` | Env-gated dry-run adapter; live polling intentionally disabled pending token. |
| 7 Production | partial | `ba9baa7` | Dockerfile and compose path added; deployment account and monitoring remain. |
| 8 Documentation | complete | `56776e3` | Privacy, safety, data TODO, download report, retrieval evaluation, progress, and comprehensive handoff verified. |
| 9 Tests and CI | complete | `93e9297` | 45 tests pass in 4.10s; offline test isolation confirmed with mocked LLM and temporary databases; GitHub Actions CI workflow green for both python and web jobs (Run 42458655523). |
| 10 Acceptance | partial | `93e9297` | Retrieval-only evaluation reached 97.0% hit-rate@4 across covered diseases (100% on 15 of 17 evaluated diseases). Gemini end-to-end evaluation remaining. |

## Exact next step

Next step: Step 5: Dose Filter Edge Cases (verify no damage to ORS litres, vaccine age ranges, timing rules; test mocked LLM + painkiller awareness/refusal).

## Latest verification

- `uv run pytest` -> `47 passed, 15 warnings in 4.16s`
- Step 4 Hindi Checks verified (`scripts/run_hindi_checks.py`):
  - Q1 "डेंगू के गंभीर लक्षण क्या हैं?": Cited [1, 8] (WHO Symptoms + NCVBDC p56); symptoms and warning signs separated cleanly into distinct lists; closing safety line in own paragraph.
  - Q2 "मलेरिया के लक्षण क्या हैं?": Cited [1, 10] (WHO Symptoms + Overview); common symptoms (बुखार, सिरदर्द, ठंड लगना) separated from severe warning signs (सांस लेने में कठिनाई, दौरे, आदि); closing safety line in own paragraph.
  - Q3 "टीबी का इलाज कैसे होता है, आसान भाषा में?": Cited [1, 2] (WHO TB Treatment + Immunization Handbook); plain-language explanation with antibiotics combination, completion of full course, DOTS; closing safety line in own paragraph.
  - Q4 "9 महीने के बच्चे को कौन से टीके लगते हैं?": Cited [1, 4, 6, 7] (NIS + NHM FAQ); MR-1, JE-1, PCV booster, Vitamin A; closing safety line in own paragraph.
  - Q5 "मेरे बच्चे को उल्टी में खून आ रहा है": Deterministic emergency triggered (`emergency: true`, citations: [], "यह आपातकाल हो सकता है। तुरंत नजदीकी अस्पताल जाएँ या 108 पर कॉल करें।", no LLM call).
- Step 1 Answer Quality verified:
  - Closing safety line sits in its own paragraph (`\n\n`) preceding fixed message, never glued to bullets (verified by `test_closing_safety_line_sits_in_own_paragraph`).
  - TB plain-words answer backed sentence-by-sentence by chunk lexical support check; ungrounded RNTCP claim dropped; curable and course duration cited.
  - Malaria symptoms answer capped at ~3 common symptoms (Fever, Headache, Chills) with warning signs in separate list.
  - WHO HTML sections segmented by `<h2>`/`<h3>` with informative `page_label` (e.g. `Malaria > Symptoms`, `Tuberculosis > Treatment`), and API returning `publisher`, `year`, `url`.
- Step 2 Honest Depth & OCR verified:
  - Depth tier calculation updated: `deep` strictly requires `specific_docs_count >= 2` and `specific_chunks >= 50`. Diseases supported primarily by broad immunization/hepatitis handbooks (`measles`, `polio`, `child-immunization`, `hepatitis-a`, `hepatitis-b`, `hepatitis-e`, `diphtheria-pertussis-tetanus`) now honestly report `good`, never `deep`.
  - Low-chunk audit complete (`scripts/audit_low_chunk_sources.py`).
  - Optional OCR fallback implemented via `rapidocr-onnxruntime` behind `enable_ocr` config flag, tagging chunks with `ocr=true`.
  - Chunk count difference accounted for across index build iterations (3,669 -> 3,559 -> 3,633 granular section chunks).
- Step 3 Calibration and Evaluation Honesty verified:
  - 45 hard out-of-scope questions benchmarked against 30 in-scope questions in `scripts/calibrate_threshold.py`. Ambiguous score band (0.70 - 0.82) identified and explicitly routed to LLM relevance gate (`_relevance_filter`) and upgraded prompt intent classification.
  - Retrieval evaluation expanded to all 30 diseases with 180 questions (3 EN + 3 HI per disease) in `eval/questions.jsonl`.
  - Overall Hit-rate@4 is 96.1% (173/180) across all 30 diseases, with 26/30 diseases achieving 100% Hit-rate@4 (`docs/RETRIEVAL_EVALUATION.md`).
  - Accounted for why 13 diseases were previously skipped (Batch 1 evaluation set only contained initial infectious disease questions; non-communicable, maternal, and environmental topics added subsequently).
- `npm --prefix web run build && npm --prefix web run lint` -> `Build and lint clean (0 errors)`
- `Forbidden boilerplate check over 3,559 chunks` -> `Newsroom: 0, Select language: 0, Emergencies: 0, Disease Outbreak News: 0, Member States: 0, cookie: 0`
- `Red-team safety evaluation` -> 7/7 questions passed: 5 personal dose/regimen requests refused; 1 dengue painkiller awareness question warning against aspirin/ibuprofen; 1 simple TB treatment question without numeric doses.
- `Threshold calibration` -> `in_scope min=0.7610`, `out_of_scope max=0.7492` (threshold 0.75 cleanly separates in-scope vs out-of-scope).
- `Retrieval evaluation (covered)` -> 97.0% hit-rate@4 for Chroma Hybrid Filtered (90.0% dense unfiltered, 96.0% dense filtered).
- `Coverage check` -> 30/30 target diseases have indexed documents; `specific` <= `documents` strictly guaranteed by content hash deduplication.
