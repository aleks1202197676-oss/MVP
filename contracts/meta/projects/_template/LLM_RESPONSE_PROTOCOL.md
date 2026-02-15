# LLM_RESPONSE_PROTOCOL: <project_id>

Any chat assistant operating on this project MUST structure every response in this order:

1. **Project context snapshot** (goal + active tracks)
2. **Current status** (`done` / `doing` / `next`)
3. **Remaining work checklist** (all incomplete DoD items)
4. **Next 1–3 recommended actions + why**
5. **Risks/unknowns**

## Reasoning policy
- Do not reveal private chain-of-thought.
- Provide a short **Rationale summary** section.
- Provide **Alternatives considered** as concise bullets.
