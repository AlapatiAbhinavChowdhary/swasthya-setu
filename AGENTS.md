# Agent rules

Read `docs/HANDOFF.md` first.

- Awareness only: never diagnose, prescribe, give doses, or invent medical facts.
- Use official Indian government/WHO sources only.
- Run deterministic emergency handling before any LLM call.
- Keep missing coverage honest; never create placeholder medical content.
- The owner runs nothing manually; the agent performs discovery and verification.
- Verify with real commands and printed output before claiming completion.
- Use one branch per phase and small conventional commits.
- Do not commit secrets, `.env`, PDFs, vectorstores, databases, or caches.
