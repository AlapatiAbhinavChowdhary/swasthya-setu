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
- While generic drug classes may be mentioned strictly in the context of official awareness (e.g. "TB is managed with a 4-to-6 month regimen of first-line antibiotics under DOTS"), specific regimens, brand names, and dose titrations are strictly prohibited.

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
