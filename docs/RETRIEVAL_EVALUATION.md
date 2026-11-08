# Retrieval-only evaluation

### Evaluation Scope and Methodology
- **Full Coverage**: All 30 target diseases evaluated with 6 questions each (3 English + 3 Hindi covering awareness, prevention, and warning signs), totaling 180 questions in `eval/questions.jsonl`.
- **Hit Definition**: A query is a retrieval hit if at least one of the top 4 retrieved passages has the query's target disease in its chunk metadata `disease_ids`.
- **Why 13 Diseases Were Previously Skipped**: The initial test set only contained questions for Batch 1 infectious diseases (17 diseases). Non-communicable, maternal/newborn, nutritional, and environmental health topics (`diabetes`, `hypertension`, `anaemia-nutrition`, `child-immunization`, `maternal-newborn-care`, `rabies-animal-bites`, `snakebite`, `leprosy`, `hiv-aids`, `heat-illness`, `mental-health-basics`, `hygiene-sanitation-safe-water`, `diphtheria-pertussis-tetanus`) were acquired in subsequent batches and are now fully evaluated.
- **Results**: Overall Hit-rate@4 is 96.1% (173/180) across all 30 diseases, with 26 of 30 diseases achieving 100.0% Hit-rate@4.

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
