# AGENT_RULES

- Portable source of truth: `latest_bundle.zip`; active source during work: repository checkout.
- Mandatory order: PREFLIGHT -> IMPLEMENT -> VERIFY.
- Track discipline is required: `PR-A*`, `PR-F*`, `PR-G*` with deny-first behavior.
- Keep patches minimal, deterministic, and placeholder-free.
- Prefer operator-first workflow when applicable.
