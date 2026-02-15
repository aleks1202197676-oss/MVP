# LLM_RESPONSE_PROTOCOL: finance_mvp

Any chat assistant operating on `finance_mvp` MUST structure every response in this order:

1. **Project context snapshot** (goal + active tracks)
2. **Current status** (`done` / `doing` / `next`)
3. **Remaining work checklist** (all incomplete DoD items)
4. **Next 1–3 recommended actions + why**
5. **Risks/unknowns**

## Required content sources
- Use `PROJECT_MAP.md`, `STATUS.md`, and `DEFINITION_OF_DONE.md` as primary references.
- Keep track labels (`A`, `F`, `G`) explicit in recommendations.

## Reasoning policy
- Never reveal private chain-of-thought.
- Instead provide:
  - **Rationale summary**: short, outcome-focused explanation.
  - **Alternatives considered**: concise bullets with trade-offs.
