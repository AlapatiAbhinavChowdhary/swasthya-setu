# Security Policy & Secret Management

Swasthya Setu adheres to strict public-health safety, privacy, and secret hygiene practices.

## Secret Management

1. **Zero Secret Tracking:** Real API credentials, environment files (`.env`), tokens, vector stores, and raw databases are strictly git-ignored and never committed to version control.
2. **Automated CI Secret Scanning:** The CI pipeline runs `scripts/scan_secrets.py` on every push and pull request, scanning all commits and working-tree tracked files for Google API key patterns (`AIza...`, `AQ...`) and ensuring zero secret leakage.
3. **Lazy Settings & Startup Validation:** The backend uses lazy settings resolution (`get_settings()`). Importing modules never requires live API keys. When live keys are missing or placeholders, endpoints fail safely and clearly report `llm_configured: false` on `GET /health` without exposing key values.
4. **Bearer Token Authentication:** Operator endpoints (`/admin/feedback`) are protected with constant-time token comparison (`secrets.compare_digest`) using `ADMIN_TOKEN`. Tokens are never stored on disk or logged.

## Privacy & Safety

1. **Zero PII Storage:** No user names, IP addresses, phone numbers, or personally identifiable information are logged or stored. Session identifiers are cryptographically hashed using SHA-256 before storage.
2. **Deterministic Emergency Interception:** Critical acute emergency signs (e.g. chest pain, severe breathlessness, profuse bleeding, poisoning, snakebite) trigger instant deterministic routing to national medical helplines (**108**) before any LLM inference or vector search.
3. **Dose & Prescription Refusal:** The application strictly provides verified public-health awareness. It deterministically refuses requests for drug dosages, personal prescriptions, and self-treatment regimens.
