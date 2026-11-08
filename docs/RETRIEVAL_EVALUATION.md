# Retrieval-only evaluation

| Configuration | Disease filter | Hybrid BM25+RRF | Hit-rate@4 | Overall Accuracy |
|---|---:|---:|---:|---:|
| Chroma Dense (Unfiltered) | false | false | 90/100 | 90.0% |
| Chroma Dense (Filtered) | true | false | 96/100 | 96.0% |
| Chroma Hybrid BM25+RRF (Unfiltered) | false | true | 93/100 | 93.0% |
| Chroma Hybrid BM25+RRF (Filtered) | true | true | 97/100 | 97.0% |

### Hit-rate@4 per disease (Chroma Hybrid Filtered):

| Disease | Hits / Questions | Hit-rate@4 |
|---|---:|---:|
| chikungunya | 6/6 | 100.0% |
| cholera | 4/6 | 66.7% |
| covid-19 | 6/6 | 100.0% |
| dengue | 6/6 | 100.0% |
| diarrhoeal-disease | 5/6 | 83.3% |
| hepatitis-a | 6/6 | 100.0% |
| hepatitis-b | 6/6 | 100.0% |
| hepatitis-e | 6/6 | 100.0% |
| japanese-encephalitis | 6/6 | 100.0% |
| kala-azar | 6/6 | 100.0% |
| lymphatic-filariasis | 6/6 | 100.0% |
| malaria | 6/6 | 100.0% |
| measles | 6/6 | 100.0% |
| polio | 4/4 | 100.0% |
| seasonal-influenza | 6/6 | 100.0% |
| tuberculosis | 6/6 | 100.0% |
| typhoid | 6/6 | 100.0% |
