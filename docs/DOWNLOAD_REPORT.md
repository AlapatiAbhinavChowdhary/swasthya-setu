# Source download report

Generated from `data/sources.lock.json` after running:

```powershell
uv run python scripts/download_data.py --retry-unreachable
```

| Source | Status | Bytes | Fallback | Reason |
|---|---|---:|---|---|
| who-india-health-topics | downloaded | 67874 | Python | WHO HTML page returned HTTP 200 |
| dengue-guidelines-2023 | downloaded | 4917466 | Python | NCVBDC PDF returned `%PDF` |
| who-vector-borne-fact-sheets-2014 | skipped | 283187 | Existing file | WHO IRIS PDF is valid |
| local-who-vector-borne-fact-sheets-2014 | downloaded | 5062009 | Python | WHO CDN PDF returned `%PDF` |
| national-immunization-schedule | skipped | 94522 | Existing file | NHM PDF is valid |

The two root-level legacy files were registered as `local_file` sources and
are indexed directly; they are never discarded when a network URL is
unreachable.

Only downloaded or valid pre-existing files in the lockfile are eligible for
indexing. The existing root-level files in `data/raw/` are intentionally not
used by the rebuild because they are not tied to this verified manifest.
