# Swasthya Setu — Limitations & Honest Operational Boundaries

In adherence to public health integrity and ethical AI principles, this document provides an honest, transparent accounting of the current boundaries, limitations, and unverified edges of Swasthya Setu.

---

## 1. Clinical Scope & Depth

### 1.1 Awareness Only — Not a Clinical Diagnostic or Triage System
- Swasthya Setu is strictly an **educational and awareness assistant**.
- It does **not** perform patient-specific clinical diagnosis, disease staging, laboratory interpretation, or differential diagnosis.
- It cannot replace in-person clinical examination, physical palpation, auscultation, or vital sign measurement (blood pressure, pulse oximetry, blood glucose).

### 1.2 Bounded Disease Scope (30 Conditions)
- The medical index covers exactly 30 high-priority public health conditions in India.
- Unindexed conditions (e.g. rare genetic disorders, specific malignancies, complex orthopedic issues, localized dermatological conditions) are intentionally refused with a referral to a certified physician or Primary Health Centre (PHC).

### 1.3 Zero Medication Prescriptions & Individual Dosing
- In compliance with Indian telemedicine ethical directives, the system refuses to prescribe medications or calculate individual dosages (e.g. mg/kg body weight calculations).
- In development set evaluation, the system achieved a **100.0% dose/prescription refusal rate** (15/15 on benchmark queries) with strictly **0 dose leaks**.
- On a fresh independent evaluation set of 30 colloquial and Hinglish prescription queries (evaluated once without tuning), lexical regex refusal was **33.3%** (10/30), highlighting the vulnerability of keyword patterns against transliterated conversational phrasing (e.g. *"kitni goli lu"*, *"konsi dawai du"*).
- While generic drug classes may be mentioned strictly in the context of official awareness (e.g. "TB is managed with a 4-to-6 month regimen of first-line antibiotics under DOTS"), specific regimens, brand names, and dose titrations are strictly prohibited.

### 1.4 Emergency Triage Detection & Best-Effort Boundaries

> [!CAUTION]
> **Do not claim emergency detection is reliable**: On a fresh set of realistic user messages (typos, slang, Hinglish), the original keyword rules caught only 45% of emergencies (18/40) and refused 33% of colloquial medicine/dose requests (10/30). While subsequent text normalisation, fuzzy matching, and an urgency/medicine flag in the existing LLM routing call scored 100% recall on a second agent-authored set, that set is development-level evidence, not independent. Real-world recall on informal phrasing is unknown, and a real-user clinical study is future work. The persistent visible "Emergency? call 108" banner on the chat page remains the primary safety guardrail.

- Emergency queries are addressed through a multi-tiered safety architecture:
  1. **Deterministic Lexicon & Normalizer:** Unicode NFC normalization, character repeat collapse, typo correction, and fuzzy token matching (rapidfuzz) over English, Hindi, and Hinglish emergency vocabularies.
  2. **Semantic LLM Urgency Routing:** Integrated into the existing single-call router (`route_rewrite_prompt`), classifying urgency (`emergency`, `urgent`, `routine`) with instructions to over-triage toward emergency when ambiguous, escalating immediately to 108 emergency cards without additional model calls.
  3. **Persistent Visible Safe Fallback:** A permanent emergency notice banner (*"Emergency? Call 108 immediately. Do not rely on this tool for life-threatening conditions."*) with direct click-to-call link is displayed prominently on the chat page at all times, ensuring users are never reliant solely on software triage.
- **Unverified Real-World Recall on Informal Phrasing:** Software pattern matching and LLM routing cannot guarantee detection of extreme dialectal slang, unprecedented transliterations, phonetic corruptions, or deeply fragmented phrases. It does not replace clinical evaluation or trained emergency dispatchers.
- Any acute signal bypasses educational intent guardrails to prevent fatal undertriage.

### 1.5 Degraded-Mode Recall (LLM Router Disabled / Upstream Outage)
- When the upstream LLM router is disabled or unavailable (e.g. total API outage, connection drops), the system operates in degraded mode, relying entirely on the deterministic rule layer (`is_emergency`).
- Across both independent Gemini hold-out emergency sets evaluated with the LLM disabled and without tuning:
  * **Hold-Out 1 (40 emergencies)**: **52.5%** (21 / 40)
  * **Hold-Out 2 (60 emergencies)**: **43.3%** (26 / 60)
  * **Combined Degraded-Mode Recall**: **47.0%** (47 / 100)
- This honest accounting confirms that keyword/regex rules alone miss 53% of realistic colloquial crisis descriptions (e.g. fragmented SMS typos, third-person narratives). The system compensates by:
  1. Retrying once with a timeout of $\le 8\text{s}$ before giving up on network glitches.
  2. Guaranteeing that any failure fallback message includes the fixed guidance: *"If this is an emergency, call 108 or 112"*.
  3. Maintaining a permanent, prominent click-to-call **108 / 112** banner on the user interface.

---

## 2. Linguistic & Vernacular Coverage

### 2.1 Standard Hindi vs. Regional Dialects
- Swasthya Setu is trained and benchmarked on **Standard Modern Hindi (मानक हिन्दी / खड़ी बोली)**.
- While the embedding model (`multilingual-e5-small`) possesses broad cross-lingual semantic capabilities, informal rural dialects (e.g., Bhojpuri, Maithili, Magahi, Bundeli, Chhattisgarhi, Marwari) have not been formally validated by clinical linguists.
- Dialectal idioms or non-standard phonological spellings of symptoms may experience lower retrieval recall compared to standard Devanagari.

### 2.2 Unreviewed Hindi Medical Terminology
- Many WHO guidelines are originally published in English and synthesized into Hindi via LLM translation.
- While factual grounding and citation mapping are strictly verified, certain complex medical translations (e.g. specific microbiological terms or pathology concepts) have not undergone formal peer-review by a panel of Hindi-medium medical doctors.

---

## 3. Data Currency & Schedule Specifics

### 3.1 National Immunization Schedule (NIS 2018 Baseline)
- The structured immunization database is built from the official MoHFW National Immunization Schedule (NIS) comprehensive guideline dated 2018.
- Recent state-specific rollouts (such as sub-district expansions of PCV or localized pilot introductions of HPV vaccines) may not be reflected in every district filter. Users are advised to verify latest local schedules with their local ASHA or ANM worker.

### 3.2 Dynamic Real-Time Outbreaks
- Outbreak alerts displayed on the `/alerts` page are based on official NCDC / IDSP weekly surveillance bulletins.
- Real-time hyper-local outbreak tracking (e.g., an acute diarrhea cluster in a specific village within the past 24 hours) requires manual ingestion of latest district surveillance reports and is not autonomously scraped from unverified news media.

---

## 4. Facility Directory Data & Geo-Routing

### 4.1 Sample / Seeded Facility Records
- The `/facilities` portal currently includes a representative directory of Primary Health Centres (PHCs), Community Health Centres (CHCs), Sub-district Hospitals, and District Hospitals across pilot districts.
- It is **not** an exhaustive national registry of all 160,000+ Ayushman Arogya Mandirs across India. Full national coverage requires live API integration with the National Health Facility Registry (HFR) under ABDM.

### 4.2 Distance Calculation
- Facility distances currently calculate approximate linear or district-centroid offsets. Real-time road routing, traffic conditions, and ambulance transit times are not modeled.

---

## 5. Deployment & Infrastructure Readiness

### 5.1 Cloud API Key Dependency (Default Configuration)
- In the default configuration, generation relies on the Google Gemini 2.5 Flash API.
- Free-tier API keys are subject to a 15 Requests Per Minute (RPM) quota and daily token quotas. Production deployment requires an enterprise Google Cloud Vertex AI project or dedicated on-premise local model inference (e.g., vLLM or Ollama serving Gemma 2 9B).

### 5.2 Accessibility & Clinical Audits
- Automated accessibility audits using axe-core report **0 critical and 0 serious violations** on standard desktop and mobile viewports.
- However, automated tools inspect only machine-testable accessibility rules. Comprehensive field usability testing with screen-reader users, elderly citizens, and assistive devices in rural settings is recommended before full production commissioning.

