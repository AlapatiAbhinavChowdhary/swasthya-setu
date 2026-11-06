# Source download report

Generated from `data/sources.lock.json` after running:

```powershell
uv run python scripts/download_data.py --retry-unreachable
```

| Source | Status | Bytes | Fallback | Reason |
|---|---|---:|---|---|
| dengue-guidelines-2023 | unreachable | 0 | Python, curl | NCVBDC timed out after retries |
| who-vector-borne-fact-sheets-2014 | downloaded | 283187 | Python | WHO IRIS returned `%PDF` |
| national-immunization-schedule | downloaded | 94522 | Python | NHM returned `%PDF` |

Only downloaded or valid pre-existing files in the lockfile are eligible for
indexing. The existing root-level files in `data/raw/` are intentionally not
used by the rebuild because they are not tied to this verified manifest.
