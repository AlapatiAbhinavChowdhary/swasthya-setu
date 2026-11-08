# Retrieval-only evaluation

| Backend | Disease filter | Hybrid BM25+RRF | Hit-rate@4 |
|---|---:|---:|---:|
| Chroma | false | false | 0.290 (29/100) |
| Chroma | true | false | 0.580 (58/100) |
| Chroma | false | true | 0.310 (31/100) |
| Chroma | true | true | 0.580 (58/100) |
| FAISS | false | false | 0.290 (29/100) |
| FAISS | true | false | 0.580 (58/100) |
