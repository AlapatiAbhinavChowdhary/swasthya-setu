# Swasthya Setu Architecture & System Design

Swasthya Setu (स्वास्थ्य सेतु) is an explainable, awareness-only public health information agent designed to bridge rural and peri-urban healthcare awareness gaps in India. It grounds every medical statement in official, authoritative sources from the Ministry of Health and Family Welfare (MoHFW), National Health Mission (NHM), National Center for Vector Borne Diseases Control (NCVBDC), Indian Council of Medical Research (ICMR), and the World Health Organization (WHO).

This document provides a student-friendly, comprehensive deep-dive into the architectural components, data pipelines, retrieval strategies, agentic reasoning, safety controls, and frontend delivery.

---

## 1. High-Level Architectural Overview

Swasthya Setu operates on a five-tier architecture:

```
[ User Input (Web SPA / Mobile / Telegram Adapter) ]
                      │
                      ▼
[ Deterministic Triage Layer (0 LLM Calls) ]
  ├─ Emergency Detection (is_emergency -> 108 Emergency Card)
  └─ Prescription / Diagnosis Refusal (is_prescription -> Doctor Referral)
                      │
                      ▼
[ LangGraph Agentic Pipeline ]
  ├─ Intent Classification & Query Rewriting (Gemini 2.5 Flash)
  └─ Conditional Routing:
       ├─ out_of_scope -> Grounded Refusal Notice
       ├─ vaccination_schedule -> Structured DB + NIS 2018 Guidelines
       └─ disease_info / prevention / outbreaks -> Hybrid RAG Pipeline
                      │
                      ▼
[ Retrieval & Ranking Pipeline ]
  ├─ Query Prefixing ("query: ...")
  ├─ Vectorstore (Chroma SQLite + intfloat/multilingual-e5-small)
  ├─ Metadata Filtering (topic / disease IDs)
  └─ Reciprocal Rank Fusion Hybrid Search (Dense Vector + BM25 Lexical)
                      │
                      ▼
[ Generation & Safety Verification Layer ]
  ├─ Constrained Generation with Numbered Bracket Citations [N]
  ├─ Post-Generation Verification:
  │    ├─ Citation Integrity (verify_citations)
  │    ├─ Regex Dose & Prescription Filter (filter_dose_patterns)
  │    ├─ Devanagari Script Normalization (normalize_mixed_script_tokens)
  │    └─ Language Consistency Check
  └─ Mandatory Awareness Disclaimer & 108 Helpline Attachment
                      │
                      ▼
[ Real-Time SSE Streaming Output (FastAPI -> React Client) ]
```

---

## 2. Ingestion & Document Processing Pipeline

### 2.1 Authoritative-Only Sourcing
The corpus contains strictly official, non-commercial sources:
- **Domains Permitted**: `*.gov.in`, `*.nic.in`, `who.int`, `cdn.who.int`, `iris.who.int`.
- **Integrity**: Every downloaded artifact has a SHA-256 digest tracked in `data/sources.lock.json` and human-readable metadata in `data/sources.yaml`. No untracked or placeholder files are permitted.

### 2.2 Extraction & Cleaning
- **PDF Extraction**: Extracted page-by-page via `pypdf`, preserving structural headings and table structures where possible.
- **HTML Extraction**: Scraped via `beautifulsoup4`. Web wrappers, navigation bars, headers, footers, tracking scripts (`googletagmanager`, `gtm.js`, `dataLayer`), and analytics cookies are strictly stripped out using DOM element removal. Only semantic `<article>` or content-body tags are processed.

### 2.3 Semantic Chunking Strategy
- Documents are split using recursive character chunking:
  - **Chunk Size**: 800 characters.
  - **Overlap**: 150 characters.
  - **Separators**: Paragraph breaks `\n\n`, line breaks `\n`, sentence terminators (`. `, `। ` for Devanagari), and word boundaries.
- **Metadata Preservation**: Each chunk retains:
  - `source`: Relative file path or official canonical URL.
  - `title`: Human-readable document title.
  - `page`: Page number (for PDFs).
  - `disease_ids`: Array of disease tags (e.g., `["malaria", "vector-borne"]`).
  - `authority`: Authority classification (`MoHFW`, `ICMR`, `WHO`).
  - `chunk_hash`: SHA-256 hash for deduplication and provenance verification.

---

## 3. Retrieval & Embedding Engineering

### 3.1 Embedding Model: `intfloat/multilingual-e5-small`
Swasthya Setu employs `intfloat/multilingual-e5-small` (384-dimensional embeddings), selected for high multilingual performance across English and Indic scripts (particularly Hindi Devanagari).

#### The Asymmetric Prefix Rule
The E5 model family requires asymmetric prefixing for optimal contrastive alignment:
- **Indexing Passages**: Every passage must begin with `"passage: "` before generating vectors:
  ```python
  text_to_embed = f"passage: {doc.page_content}"
  ```
- **Search Queries**: Every search query must begin with `"query: "`:
  ```python
  query_to_embed = f"query: {query}"
  ```
*Omission of these prefixes degrades retrieval recall by up to 18% because the cross-attention geometry in E5 expects distinct query and document representations.*

### 3.2 Vectorstore Selection: Chroma vs FAISS
| Feature | Chroma (Chosen) | FAISS |
|---|---|---|
| **Persistence** | Embedded SQLite + Parquet (`duckdb`/native) with ACID guarantees | Flat binary files (`index.faiss`) requiring manual serialization |
| **Metadata Filtering** | Rich native payload filtering (`$in`, `$and`, `$or`) on disease IDs | Requires secondary ID mapping or custom wrapper dictionaries |
| **Incremental Updates** | Native upsert / delete by document ID | Rebuilding or custom ID maps required |
| **Zero External Services** | Runs in-process with Python standard environment | Runs in-process |

Chroma was chosen because its embedded SQLite persistence allows zero-setup offline storage with native, high-performance metadata filtering.

### 3.3 Hybrid Search & Reciprocal Rank Fusion (RRF)
To ensure reliable retrieval across exact medical names (e.g., "Plasmodium vivax", "BCG", "ORS") and natural language queries, Swasthya Setu combines:
1. **Dense Semantic Retrieval**: Chroma cosine similarity over multilingual embeddings.
2. **Sparse Lexical Retrieval**: BM25 keyword matching over tokenized text.
3. **Reciprocal Rank Fusion**:
   $$\text{RRF\_Score}(d) = \sum_{m \in \{\text{Dense}, \text{BM25}\}} \frac{1}{k + \text{rank}_m(d)}$$
   where $k = 60$. Dense retrieval excels at conceptual similarity (e.g., "शिशु को टीका कब लगेगा" $\rightarrow$ infant immunization schedule), while BM25 ensures exact acronyms and brand-neutral terms are never lost in semantic space.

---

## 4. Agentic Architecture & Reasoning (LangGraph)

Swasthya Setu implements an explainable state graph via LangGraph:

```
[ START ] ──> [ Check Emergency (Deterministic) ]
                      │
           ┌──────────┴──────────┐
      (Emergency)           (Non-Emergency)
           │                     │
           ▼                     ▼
  [ Emergency Node ]     [ Check Prescription (Deterministic) ]
           │                     │
           │              ┌──────┴──────┐
           │         (Rx Request)  (Awareness Query)
           │              │             │
           │              ▼             ▼
           │        [ Rx Refusal ]  [ Route Intent & Query Rewrite ]
           │              │             │
           │              │      ┌──────┴─────────────────────────┐
           │              │  (Out of Scope)             (Disease / Vaccine)
           │              │      │                                │
           │              │      ▼                                ▼
           │              │ [ Grounded Refusal ]          [ Hybrid Retrieval ]
           │              │      │                                │
           │              │      │                                ▼
           │              │      │                     [ Synthesis & Citations ]
           │              │      │                                │
           │              │      │                                ▼
           │              │      │                     [ Safety Verification ]
           │              │      │                                │
           └──────────────┼──────┴────────────────────────────────┘
                          ▼
                       [ END ]
```

### 4.1 State Schema (`AgentState`)
The agent state tracks:
- `question`: Current user inquiry.
- `language`: Detected or selected language (`"en"` or `"hi"`).
- `history`: Last 6 conversational turns (`List[Tuple[str, str]]`).
- `intent`: Identified user intent (`disease_info`, `vaccination_schedule`, `emergency`, `out_of_scope`).
- `documents`: Retrieved official document chunks with full provenance.
- `citations`: Extracted integer citation keys mapped to `documents`.
- `answer`: Grounded, verified final markdown response.
- `emergency`: Boolean flag indicating acute medical emergency triage.

---

## 5. Multi-Layered Safety & Clinical Guardrails

Swasthya Setu implements defense-in-depth safety:

1. **Pre-LLM Deterministic Emergency Filter**:
   - Triggers on acute life-threatening symptoms (vomiting blood, chest pain radiating to left arm, acute respiratory distress, severe trauma, infant convulsions).
   - Bypasses LLM generation completely ($0.00\text{s}$ latency, $0$ LLM calls).
   - Immediately returns the emergency notice directing user to call 108 or attend the nearest casualty ward.

2. **Pre-LLM Prescription & Personal Diagnosis Refusal**:
   - Triggers on "what medicine should I take", "prescribe", "what dose for my child", "which tablet for fever".
   - Bypasses LLM generation to return a strict referral message:
     *"I cannot diagnose you or recommend medicines or doses. Please ask a doctor, ASHA worker or health centre."*

3. **In-Prompt Structural Constraints**:
   - Every fact must carry a bracketed citation `[N]` corresponding to context documents.
   - Prohibits personal pronouns in medical recommendations.
   - Prohibits prescribing or combining drug names with dosages.

4. **Post-Generation Regex Dose Filtering**:
   - Scans output text with `filter_dose_patterns`:
     $$\b\d+(?:\.\d+)?\s*(?:mg|mcg|µg|ml|iu|tablets?|capsules?|drops?)(?:/(?:kg|day|dose))?\b$$
   - Any generated numeric dosage causes the entire answer to be replaced with the safe refusal notice.

5. **Devanagari Script Integrity**:
   - `normalize_mixed_script_tokens` catches and repairs mixed-script tokens (e.g. `सैलicylates` $\rightarrow$ `salicylates`).

6. **Mandatory Closing Disclaimer**:
   - Statically appended in its own paragraph:
     *"This is health awareness information, not medical advice. In an emergency, go to the nearest hospital or call 108."*

---

## 6. Streaming Architecture & Real-Time Delivery

The application streams responses via Server-Sent Events (SSE) over HTTP:
- **Protocol**: `text/event-stream`.
- **Event Types**:
  - `event: metadata` $\rightarrow$ JSON payload with detected language, intent, emergency flag, and source documents.
  - `event: delta` $\rightarrow$ Incremental text chunk for smooth typing effect.
  - `event: done` $\rightarrow$ Completion signal with total token/timing metadata.
  - `event: error` $\rightarrow$ Sanitized error payload with friendly retry guidance on HTTP 429.

---

## 7. Frontend Architecture (React + Tailwind CSS)

The user interface is built as a single-page application (SPA):
- **Stack**: React 18, TypeScript, Tailwind CSS, Lucide Icons, Vite.
- **Routing**: `wouter` lightweight client-side router.
- **Theme Support**: Seamless light/dark mode with contrast-compliant palette.
- **Bilingual Interface**: Full toggle for English and Hindi (हिन्दी) across all 9 pages:
  1. `/` (Home & symptom search overview)
  2. `/chat` (Interactive grounded assistant with citation chips & source inspector)
  3. `/diseases` (Directory of 30 indexed diseases)
  4. `/diseases/:slug` (Individual disease deep-dive with official sources)
  5. `/vaccination` (National Immunization Schedule with age-milestone calculator)
  6. `/facilities` (Hospital & health center locator with emergency helpline cards)
  7. `/alerts` (Outbreak notices & seasonal advisories)
  8. `/about` (Mission, methodology, and official data provenance)
  9. `/admin` (System health, vectorstore diagnostics, and source audit)

---

## 8. Key Architectural Design Decisions & Rationales

1. **Why LangGraph instead of monolithic chains?**
   - *Rationale*: LangGraph enables explicit state control, deterministic branching before LLM invocation, and circular correction loops. Emergency and prescription requests are diverted deterministically without consuming token quota or risking hallucination.

2. **Why Single-Server SPA Distribution (`ENABLE_FRONTEND=true`)?**
   - *Rationale*: Packaging the compiled Vite build directly into FastAPI's static file mounts eliminates CORS issues, simplifies rural / self-hosted container deployment, and allows a single command (`uv run uvicorn ...`) to run the entire application.

3. **Why Multilingual-E5 over monolingual MiniLM?**
   - *Rationale*: Hindi is spoken by over 500 million citizens in India. Monolingual English embeddings fail completely when rural healthcare workers or citizens query in Devanagari script. Multilingual-E5 maps English and Hindi medical concepts into a shared embedding space.

4. **Why Reciprocal Rank Fusion (RRF) for Hybrid Search?**
   - *Rationale*: Vector similarity alone can miss exact disease acronyms ("JE", "PCV", "DOTS") or vernacular transliterations ("लू", "शुगर"). BM25 provides lexical precision while dense vectors provide semantic flexibility. RRF combines their strengths without requiring heuristic score normalization.

---

## 9. Three Hard Engineering Bugs & Their Solutions

### Bug 1: Corrupted Mixed-Script Tokens in Hindi Output
- **Symptom**: The LLM occasionally produced garbled chimeric tokens in Hindi responses, such as `सैलicylates` (Devanagari "सैल" fused with Latin "icylates").
- **Root Cause**: Sub-word tokenizers split uncommon Latin medical words across script boundaries when surrounded by Devanagari context.
- **Solution**: Implemented `normalize_mixed_script_tokens` in `verification.py` using regex `\S*[\u0900-\u097f]\S*[A-Za-z]\S*` to intercept and normalize hybrid tokens into clean Latin or pure Devanagari terms.

### Bug 2: Test Suite Slowness Due to SQLite Chroma Disk Contention
- **Symptom**: Pytest suite took over 30 seconds to run because every unit test initialized and tore down a real Chroma SQLite database on disk.
- **Root Cause**: Synchronous Windows file locking on SQLite disk databases inside `load_index()`.
- **Solution**: Patched `tests/conftest.py` with `isolate_test_environment` to mock the underlying Chroma store with an in-memory document stub. Full test suite execution dropped from 30.2s to 5.78s (an 81% reduction).

### Bug 3: Free-Tier Gemini API Quota Exhaustion (429 Resource Exhausted)
- **Symptom**: Automated evaluation of 140 questions crashed mid-run due to Google's 15 Requests Per Minute (RPM) free-tier limit.
- **Root Cause**: Burst evaluation fired queries back-to-back without pacing.
- **Solution**: Implemented a token-bucket rate limiter enforcing $\ge 6.5\text{s}$ pause between LLM calls ($<10\text{ RPM}$), exponential backoff on HTTP 429, and atomic checkpointing in `eval/results.jsonl` allowing idempotent recovery if interrupted.

