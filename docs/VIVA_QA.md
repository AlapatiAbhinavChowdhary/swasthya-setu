# Swasthya Setu — Viva Voce & Defense Q&A Guide

This guide prepares students and developers for comprehensive project viva and technical defense across 7 core dimensions: Data Provenance, Retrieval Engineering, Generation & Prompting, Clinical Safety & Ethics, System Architecture, Scalability & Performance, and Real-World Deployment.

---

## Dimension 1: Data Provenance & Ingestion (Questions 1–5)

### Q1: Where does your health data come from, and why did you choose these sources?
**Answer**: Our corpus comes strictly from official, non-commercial health authorities: the Ministry of Health and Family Welfare (MoHFW), National Health Mission (NHM), National Center for Vector Borne Diseases Control (NCVBDC), Indian Council of Medical Research (ICMR), and the World Health Organization (WHO). We chose these because public health information requires clinical authority; commercial health blogs often carry unverified claims or sponsor biases.

### Q2: How do you guarantee the integrity of downloaded health guidelines?
**Answer**: Every document download is cryptographically verified. We maintain a `data/sources.lock.json` manifest recording the canonical URL, download timestamp, and SHA-256 cryptographic checksum. If an upstream document changes or is tampered with, the hash mismatch fails the ingestion pipeline.

### Q3: What document formats do you support, and how do you handle unstructured noise?
**Answer**: We ingest official PDF clinical manuals and WHO HTML fact sheets. For PDFs, we extract text page-by-page preserving section titles. For HTML, we use BeautifulSoup to strip navigation banners, scripts (Google Tag Manager, dataLayer), footers, and cookie banners, keeping only the semantic article body.

### Q4: Why did you choose a chunk size of 800 characters with 150-character overlap?
**Answer**: 800 characters (~120–150 words) comfortably encapsulates a coherent clinical concept—such as a symptom cluster, vector transmission cycle, or vaccination milestone—without diluting semantic embedding density. The 150-character overlap prevents sentences and diagnostic criteria from being fractured at chunk boundaries.

### Q5: How many diseases are indexed in Swasthya Setu?
**Answer**: Exactly 30 high-burden public health conditions in India are indexed across 5 major categories: Vector-borne (malaria, dengue, chikungunya, kala-azar, lymphatic filariasis, Japanese encephalitis), Infectious/Communicable (TB, leprosy, cholera, typhoid, viral hepatitis, rabies), Maternal & Child Health (immunization schedule, anaemia, diarrhoeal disease, pneumonia), Non-Communicable Diseases (diabetes, hypertension, cardiovascular, stroke, COPD, oral cancer), and Environmental/Occupational (heat-related illness, snakebite, fluorosis, silicosis).

---

## Dimension 2: Embeddings & Retrieval Engineering (Questions 6–10)

### Q6: Which embedding model did you choose and why?
**Answer**: We use `intfloat/multilingual-e5-small`. It produces 384-dimensional dense vectors and was trained on massive multilingual sentence pairs. It handles both English and Devanagari Hindi seamlessly within a shared vector space, essential for bilingual Indian healthcare.

### Q7: What is the asymmetric prefix rule in E5 models, and why does it matter?
**Answer**: E5 was trained using asymmetric contrastive prefixes: passages must be prefixed with `"passage: "` during vectorstore indexing, and user questions must be prefixed with `"query: "` during search. Failing to prepend these prefixes degrades retrieval recall by up to 18% because the cross-attention geometry expects distinct query and passage representations.

### Q8: Why did you pick Chroma instead of FAISS or Pinecone?
**Answer**: Chroma is an embedded vector database backed by SQLite and Parquet. It requires zero external server setup, runs entirely in-process on consumer hardware, and natively supports rich metadata filtering on disease IDs. FAISS requires manual metadata mapping wrappers, while cloud vector databases like Pinecone require network roundtrips and subscription costs.

### Q9: What is Hybrid Search and why is it necessary for medical RAG?
**Answer**: Hybrid search combines dense vector search (semantic similarity via cosine distance) with sparse lexical search (BM25 keyword matching) using Reciprocal Rank Fusion (RRF). Semantic vectors capture conceptual meaning (e.g., "शिशु को टीका कब लगेगा" $\rightarrow$ infant immunization), while BM25 ensures exact acronyms and proper names (e.g., "PCV", "JE-1", "DOTS") are never missed.

### Q10: How does your retrieval pipeline achieve 96.1% Hit-Rate@4?
**Answer**: By coupling query-time intent classification with metadata filtering. When a user asks about "malaria prevention", the intent router tags `disease_ids: ["malaria"]`, restricting Chroma's candidate pool to verified malaria guidelines before ranking top-4 chunks.

---

## Dimension 3: Agentic Architecture & Reasoning (Questions 11–15)

### Q11: Why did you use LangGraph instead of a standard linear LangChain pipeline?
**Answer**: LangGraph models the assistant as an explicit state machine with conditional branching and deterministic safeguards. It allows us to bypass the LLM entirely for emergencies and prescription inquiries, verify citations in post-processing loops, and maintain stateful conversational memory across turns.

### Q12: How does your intent classification router work?
**Answer**: User queries are classified by a lightweight Gemini prompt into categories: `disease_info`, `prevention_tips`, `vaccination_schedule`, `emergency`, `find_hospital`, or `out_of_scope`. If an out-of-scope query is detected, the agent immediately issues a grounded refusal without performing unnecessary vector searches.

### Q13: How is conversational memory handled without token bloat?
**Answer**: We enforce a rolling window of the last 6 turns (3 user questions, 3 assistant responses). Older turns are pruned. This preserves immediate conversational context (e.g., answering "What are its complications?" following a question on dengue) while bounding prompt token consumption.

### Q14: How does the agent answer vaccination schedule queries?
**Answer**: Vaccination queries route to a specialized structured handler backed by the National Immunization Schedule (NIS 2018). It extracts exact milestones (at birth, 6 weeks, 10 weeks, 14 weeks, 9–12 months, 16–24 months, 5–6 years, 10 & 16 years) with official notes on non-vaccine supplements like Vitamin A.

### Q15: How does real-time streaming work in your system?
**Answer**: FastAPI streams tokens using Server-Sent Events (SSE) via `text/event-stream`. The client receives four distinct event types: `metadata` (language, intent, source documents), `delta` (incremental generated tokens), `done` (completion signal), and `error` (user-friendly error messages).

---

## Dimension 4: Clinical Safety & Guardrails (Questions 16–20)

### Q16: How do you prevent the LLM from diagnosing patients or prescribing drugs?
**Answer**: We use a two-tier defense:
1. *Pre-LLM Regex & Keyword Gating*: Patterns like "what medicine should I take" or "prescribe dose" immediately trigger a hard refusal without calling the LLM.
2. *Post-LLM Dose Filtering*: `filter_dose_patterns` scans generated text for numeric dosages (e.g. "500 mg", "2 tablets/day"). If detected, the response is wiped and replaced with the safe refusal notice.

### Q17: What happens when a user describes a life-threatening medical emergency?
**Answer**: The deterministic `is_emergency` classifier identifies high-acuity triggers (e.g. "vomiting blood", "crushing chest pain", "infant not breathing") within 0.05 seconds. It bypasses the LLM completely ($0$ LLM calls) and immediately presents the Emergency Notice: advising immediate transit to the nearest hospital and calling the 108 ambulance helpline.

### Q18: What is your policy on drug names in responses?
**Answer**: Drug names (e.g., "paracetamol", "rifampicin") are permitted strictly for general disease awareness when supported by official text (e.g., "fever may be managed with paracetamol"). They are strictly forbidden from being combined with personalized dosage, frequencies, or tablet counts.

### Q19: How do you eliminate hallucinated citations?
**Answer**: Generation is constrained so that every bracketed citation `[N]` must correspond to an index in the retrieved context documents. The `verify_citations` post-processor verifies that $1 \le N \le \text{len(documents)}$. If any citation is out-of-bounds or unsupported, it is stripped or replaced with safe refusal.

### Q20: Why is the safety disclaimer non-negotiable?
**Answer**: Every informational response appends a standardized awareness disclaimer: *"This is health awareness information, not medical advice. In an emergency, go to the nearest hospital or call 108."* This ensures clear legal and ethical boundaries under Indian telemedicine guidelines.

---

## Dimension 5: Multilingual & Indic Language Support (Questions 21–25)

### Q21: How do you handle Hindi queries when source documents are in English?
**Answer**: Multilingual-E5 maps Hindi queries and English source passages into a common conceptual vector space. The LLM is then prompted in Hindi with the retrieved English facts, translating and synthesizing culturally aligned Hindi responses with bracketed citations.

### Q22: What is the "mixed-script token bug" in Devanagari LLM output?
**Answer**: Sub-word tokenizers often fail on rare Latin medical terms in Hindi sentences, creating chimera tokens like `सैलicylates` (Devanagari "सैल" + Latin "icylates"). Our `normalize_mixed_script_tokens` regex detects and cleanly standardizes these into readable terms.

### Q23: How do you evaluate language consistency?
**Answer**: We verify that a Hindi query produces an answer with at least 20 Devanagari Unicode characters (`\u0900-\u097f`) and an English query produces Latin characters. Our benchmark achieves 100% language consistency.

### Q24: Can Swasthya Setu be extended to other Indian languages like Bengali, Tamil, or Odia?
**Answer**: Yes. Multilingual-E5 natively supports 100+ languages including 10+ Indic scripts. To support Odia or Tamil, we simply add localized refusal messages in `FIXED_MESSAGES` and language detection rules.

### Q25: How do vernacular health terms like "लू" or "शुगर" get handled?
**Answer**: Our domain query expansion dictionary maps common colloquial terms ("लू" $\rightarrow$ heatstroke, "शुगर" $\rightarrow$ diabetes, "खून की कमी" $\rightarrow$ anaemia) before vector search, ensuring rural phrasing reaches the correct clinical guidelines.

---

## Dimension 6: System Performance & Scalability (Questions 26–28)

### Q26: How did you optimize your automated test suite to run in under 6 seconds?
**Answer**: We isolated tests from disk I/O in `tests/conftest.py` by mocking the Chroma SQLite vectorstore with an in-memory document mock. This dropped test suite execution from 30.2 seconds down to 5.78 seconds for 66 unit tests.

### Q27: How do you stay within free-tier API rate limits during large batch evaluations?
**Answer**: We built a token-bucket rate limiter into our evaluation runner (`scripts/evaluate_answers.py`) enforcing $\ge 6.5\text{s}$ spacing between calls ($<10\text{ RPM}$ against the 15 RPM free limit), combined with automatic 55s backoff on HTTP 429 and incremental checkpointing in `eval/results.jsonl`.

### Q28: Can this system run completely offline in rural primary health centres?
**Answer**: Yes. Chroma runs locally without internet. If paired with an on-premise quantized small language model (such as Llama 3 8B or Gemma 2 9B via Ollama), the entire pipeline can operate on a local sub-centre laptop without any internet connectivity.

---

## Dimension 7: Ethics, Limitations & Future Scope (Questions 29–30)

### Q29: What are the primary clinical limitations of this system?
**Answer**: Swasthya Setu is awareness-only. It cannot physically examine a patient, order blood investigations, interpret lab reports, or account for individual comorbidities (e.g., renal failure, pregnancy). It directs any patient needing clinical decision-making to a certified healthcare practitioner.

### Q30: How would you scale this to nationwide deployment under Ayushman Bharat Digital Mission (ABDM)?
**Answer**:
1. Integration with ABDM ABHA (Ayushman Bharat Health Account) for verified citizen login.
2. WhatsApp and IVR/telephony voice interfaces for illiterate or feature-phone populations.
3. Geo-location integration with PM-JAY and NHM health facility registries to route patients to the nearest active Primary Health Centre (PHC) with available drug stock.
