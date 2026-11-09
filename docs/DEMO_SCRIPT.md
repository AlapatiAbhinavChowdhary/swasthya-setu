# Swasthya Setu — 5-Minute Live Demonstration Script

This script is structured for evaluators, hackathon judges, and clinical reviewers. It guides the presenter through a tightly timed 5-minute showcase demonstrating safety, bilingual comprehension, grounded RAG, immunization scheduling, and emergency triage.

---

## Pre-Demo Checklist (30 Seconds Before Starting)

1. Ensure the single-server application is active:
   ```powershell
   uv run uvicorn swasthya_setu.api.main:app --port 8000
   ```
2. Open your browser to `http://localhost:8000/`.
3. Verify that the UI loads in Light Mode (or switch to Dark Mode if preferred).
4. Have the `/chat` tab open and ready.

---

## Minute 0:00 – 1:00 | The Problem & Architectural Foundation

### Visual
Navigate to `http://localhost:8000/` (Home Page) and click on `/about`.

### Presenter Speaks:
> "Good morning, respected judges. Over 800 million citizens in rural and peri-urban India face significant barriers accessing reliable, timely health awareness. When symptoms arise, citizens either turn to unverified WhatsApp forwards or wait days to reach an overburdened Primary Health Centre.
>
> To solve this, we built **Swasthya Setu (स्वास्थ्य सेतु)**: an explainable, awareness-only public health intelligence agent.
> 
> Unlike generic chatbots that hallucinate or provide dangerous medical advice, Swasthya Setu enforces three foundational pillars:
> 1. **Authoritative Grounding**: Every fact is retrieved strictly from official Indian government (MoHFW, NCVBDC, ICMR) and WHO documents.
> 2. **Multi-Tier Clinical Safety**: Zero diagnoses, zero prescriptions, and zero numeric drug dosages.
> 3. **Bilingual Accessibility**: Full English and Hindi support across web, mobile, and messaging interfaces."

---

## Minute 1:00 – 2:00 | Grounded Clinical Information with Verifiable Citations

### Action:
1. Navigate to `http://localhost:8000/chat`.
2. Type or paste the prompt:
   ```text
   What are the symptoms of malaria?
   ```
3. Hit Send.

### Visual to Point Out:
- Point out the progressive Server-Sent Events (SSE) streaming.
- Point out the bracketed citation chips like `[1]` and `[2]`.
- Click on one of the citation chips to open the **Source Inspector Dialog**.
- Show the source details: Document Title (`WHO Malaria Fact Sheet`), Authority (`WHO`), and official URL.
- Show the explicit separation between **Early Symptoms** and **Warning Signs**.
- Highlight the mandatory closing disclaimer: *"This is health awareness information, not medical advice. In an emergency, go to the nearest hospital or call 108."*

### Presenter Speaks:
> "Notice two crucial things here:
> First, our system streams tokens in real time, but before synthesis, it executed hybrid retrieval—combining dense vector search via Multilingual-E5 with BM25 keyword matching.
> Second, see these interactive citation chips? Every single claim is directly anchored in an official guideline. Clicking the chip allows a healthcare worker or citizen to inspect the exact official source document. There are zero hallucinated citations."

---

## Minute 2:00 – 3:00 | Dual-Language & Cross-Lingual Hindi Comprehension

### Action:
1. In the chat, type or paste the Hindi prompt:
   ```text
   डेंगू के गंभीर लक्षण क्या हैं?
   ```
2. Hit Send.

### Visual to Point Out:
- The agent streams fluent, grammatically correct Devanagari Hindi.
- Highlights severe dengue warning signs (तेज पेट दर्द, लगातार उल्टी, मसूड़ों या नाक से खून आना, अत्यधिक थकान).
- Proper bracketed citations `[N]` mapped to official WHO/NCVBDC dengue guidelines.

### Presenter Speaks:
> "India's rural communities speak dozens of languages, with Hindi spoken by over half a billion citizens. Here, we asked in Hindi about severe dengue warning signs.
> Even though many source documents are published in English, our multilingual embedding space maps the Hindi query to English clinical concepts, translates them faithfully, and responds in clear Devanagari Hindi.
> Notice also our Devanagari script integrity: there are no garbled mixed-script tokens like 'सैलicylates'—our post-processor guarantees clean vernacular rendering."

---

## Minute 3:00 – 4:00 | Strict Clinical Guardrails & Refusals

### Action 1 (Prescription Attempt):
Type into chat:
```text
What medicine should I take for tuberculosis?
```
Hit Send.

### Visual:
Immediate, respectful refusal:
*"I cannot diagnose you or recommend medicines or doses. Please ask a doctor, ASHA worker or health centre."*

### Presenter Speaks:
> "Now let us test our clinical guardrails. I asked: 'What medicine should I take for TB?'
> An unsafe AI might suggest antibiotics or dosages, which can lead to drug-resistant strains or patient harm. Swasthya Setu’s deterministic intent gate catches this *before* calling the LLM and issues an unequivocal referral to a qualified doctor. In our automated evaluation across 140 adversarial tests, we achieved a strict **zero dose leak count**."

### Action 2 (Acute Emergency):
Type into chat:
```text
My child is vomiting blood
```
Hit Send.

### Visual:
Instant (<0.06s) bright red **Emergency Triage Notice**:
- 🚨 Urgent Medical Attention Required
- Direct instruction: "Go to the nearest hospital emergency department immediately."
- Prominent 108 Ambulance helpline.

### Presenter Speaks:
> "When seconds matter, you cannot afford LLM latency or hallucination. For red-flag symptoms like vomiting blood, chest pain, or infant convulsions, our deterministic triage engine identifies the emergency in under 60 milliseconds with zero LLM calls, directing the user immediately to the nearest casualty ward and the national 108 emergency service."

---

## Minute 4:00 – 5:00 | National Immunization Schedule & Health Facilities

### Action:
1. Click on the `/vaccination` tab in the navigation bar.
2. Select the **9 Months** age milestone from the timeline.
3. Show the displayed vaccines:
   - Measles & Rubella (MR-1)
   - Japanese Encephalitis (JE-1) (endemic districts)
   - PCV Booster
   - Vitamin A 1st dose (explicitly marked: *Supplement, not a vaccine*)
4. Quickly navigate to `/facilities` to show the Primary Health Centre locator and emergency contacts (108, 102, 104, 112).

### Presenter Speaks:
> "Finally, beyond chat, Swasthya Setu provides structured public health utilities.
> Here is our National Immunization Schedule portal, aligned with the MoHFW 2018 guidelines. Parents and ASHA workers can calculate exact due dates for their infants, with clear distinctions between vaccines and nutritional supplements like Vitamin A.
> Our `/facilities` portal maps health infrastructure from rural Sub-centres to District Hospitals.
>
> In summary, Swasthya Setu delivers a robust, accessible, and strictly safe public health intelligence platform designed for the real needs of rural India. Thank you, and we welcome your questions!"
