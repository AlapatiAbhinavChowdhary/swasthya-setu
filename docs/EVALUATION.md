# Evaluation

Questions attempted: 14 / 100

| Group | Count | Refusal rate | Citation validity | Language consistency | Median latency (s) |
|---|---:|---:|---:|---:|---:|
| awareness | 5 | 0.60 | 1.00 | 1.00 | 6.064 |
| prevention | 5 | 0.60 | 1.00 | 0.80 | 3.296 |
| warning | 4 | 0.75 | 1.00 | 1.00 | 3.261 |

Configuration comparison:

| Backend | Filter | Hybrid | Result |
|---|---|---|---|
| Chroma | on | off | measured above |
| FAISS | on | off | compatibility path available; not run in this Gemini pass |
| Chroma | off | off | not run; requires a separate controlled API experiment |
| Chroma | on | on | not implemented |
