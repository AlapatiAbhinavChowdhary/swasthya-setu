# Retrieval-only evaluation

### Evaluation Scope and Methodology
- **Full Coverage**: All 30 target diseases evaluated with 6 questions each (3 English + 3 Hindi covering awareness, prevention, and warning signs), totaling 180 questions in `eval/questions.jsonl`.
- **Hit Definition**: A query is a retrieval hit if at least one of the top 4 retrieved passages has the query's target disease in its chunk metadata `disease_ids`.
- **Why 13 Diseases Were Previously Skipped**: The initial test set only contained questions for Batch 1 infectious diseases (17 diseases). Non-communicable, maternal/newborn, nutritional, and environmental health topics (`diabetes`, `hypertension`, `anaemia-nutrition`, `child-immunization`, `maternal-newborn-care`, `rabies-animal-bites`, `snakebite`, `leprosy`, `hiv-aids`, `heat-illness`, `mental-health-basics`, `hygiene-sanitation-safe-water`, `diphtheria-pertussis-tetanus`) were acquired in subsequent batches and are now fully evaluated.
- **Results**: Overall Hit-rate@4 is 96.1% (173/180) across all 30 diseases, with 25 of 30 diseases achieving 100.0% Hit-rate@4. Exactly 5 topics have questions below 100%: `heat-illness` (4/6), `leprosy` (4/6), `cholera` (5/6), `diabetes` (5/6), and `hygiene-sanitation-safe-water` (5/6).

| Configuration | Disease filter | Hybrid BM25+RRF | Hit-rate@4 | Overall Accuracy |
|---|---:|---:|---:|---:|
| Chroma Dense (Unfiltered) | false | false | 164/180 | 91.1% |
| Chroma Dense (Filtered) | true | false | 173/180 | 96.1% |
| Chroma Hybrid BM25+RRF (Unfiltered) | false | true | 158/180 | 87.8% |
| Chroma Hybrid BM25+RRF (Filtered) | true | true | 173/180 | 96.1% |

### Hit-rate@4 per disease (Chroma Hybrid Filtered):

| Disease | Hits / Questions | Hit-rate@4 |
|---|---:|---:|
| anaemia-nutrition | 6/6 | 100.0% |
| chikungunya | 6/6 | 100.0% |
| child-immunization | 6/6 | 100.0% |
| cholera | 5/6 | 83.3% |
| covid-19 | 6/6 | 100.0% |
| dengue | 6/6 | 100.0% |
| diabetes | 5/6 | 83.3% |
| diarrhoeal-disease | 6/6 | 100.0% |
| diphtheria-pertussis-tetanus | 6/6 | 100.0% |
| heat-illness | 4/6 | 66.7% |
| hepatitis-a | 6/6 | 100.0% |
| hepatitis-b | 6/6 | 100.0% |
| hepatitis-e | 6/6 | 100.0% |
| hiv-aids | 6/6 | 100.0% |
| hygiene-sanitation-safe-water | 5/6 | 83.3% |
| hypertension | 6/6 | 100.0% |
| japanese-encephalitis | 6/6 | 100.0% |
| kala-azar | 6/6 | 100.0% |
| leprosy | 4/6 | 66.7% |
| lymphatic-filariasis | 6/6 | 100.0% |
| malaria | 6/6 | 100.0% |
| maternal-newborn-care | 6/6 | 100.0% |
| measles | 6/6 | 100.0% |
| mental-health-basics | 6/6 | 100.0% |
| polio | 6/6 | 100.0% |
| rabies-animal-bites | 6/6 | 100.0% |
| seasonal-influenza | 6/6 | 100.0% |
| snakebite | 6/6 | 100.0% |
| tuberculosis | 6/6 | 100.0% |
| typhoid | 6/6 | 100.0% |

### Missed Queries Analysis (7 Misses across 5 Topics)

All 7 missed queries were inspected against their top 4 retrieved chunks:

1. **`cholera` (5/6)**: *"हैजा में पानी की कमी होने पर तुरंत ओआरएस कैसे दें?"*
   - *Top retrieved chunks*: `diarrhoeal-disease/who-diarrhoeal-disease.html` (ORS rehydration), `diarrhoeal-disease/icmr-stw-acute-diarrhea.pdf`.
   - *Verified cause*: Cross-topic overlap. The query asks specifically about giving ORS for severe dehydration; the dense index retrieves acute diarrhoea guidelines that contain extensive ORS preparation instructions rather than the cholera fact sheet.

2. **`diabetes` (5/6)**: *"शुगर के मरीजों को पैरों की देखभाल क्यों करनी चाहिए?"*
   - *Top retrieved chunks*: `anaemia-nutrition/icmr-stw-haemolytic-anaemia.pdf`, `tuberculosis/national-guidance-differential-tb-care-2025.pdf`.
   - *Verified cause*: Vernacular vocabulary mismatch. Colloquial Hindi *"शुगर"* (sugar) has weaker dense alignment with official English ICMR/WHO diabetes monographs without query rewriting to *"diabetes foot care"*.

3. **`heat-illness` (4/6)**:
   - Query 1: *"लू (हीट स्ट्रोक) लगने के शुरुआती और गंभीर लक्षण क्या हैं?"*
   - Query 2: *"लू लगने पर मरीज को तुरंत क्या प्राथमिक उपचार देना चाहिए?"*
   - *Top retrieved chunks*: `diarrhoeal-disease`, `tuberculosis`, `dengue`.
   - *Verified cause*: Colloquial Hindi term *"लू"* (*loo*) is not present in English-native WHO heat guidance. In end-to-end agent execution, the LLM query rewriter translates *"लू"* to *"heat stroke / heat illness symptoms"*, resolving this gap.

4. **`leprosy` (4/6)**:
   - Query 1: *"How to prevent nerve damage and disability in leprosy patients?"*
   - Query 2: *"कुष्ठ रोग में हाथों-पैरों की नसों को नुकसान से कैसे बचाएं?"*
   - *Top retrieved chunks*: `dengue`, `malaria`, `tuberculosis`.
   - *Verified cause*: The phrase *"nerve damage and disability"* without query expansion misses WHO clinical terminology (*"multidrug therapy"*, *"Grade 2 disability"*, *"peripheral neuropathy"*).

5. **`hygiene-sanitation-safe-water` (5/6)**: *"बीमारियों से बचने के लिए साबुन से हाथ धोना कब-कब जरूरी है?"*
   - *Top retrieved chunks*: `rabies-animal-bites/mohfw-stg-rabies-prophylaxis.pdf` (washing with soap), `seasonal-influenza/who-influenza-seasonal.html`, `hepatitis-b/who-hepatitis-b.html`.
   - *Verified cause*: Cross-cutting infection control guidance. Specific infectious disease guidelines that mandate soap handwashing score higher on lexical and semantic overlap than general WASH circulars.
