# LLM_RESPONSE_PROTOCOL: finance_mvp

Any chat assistant operating on `finance_mvp` MUST structure every response in this exact order:

1. **Project context snapshot** (goal + active tracks `A`, `F`, `G`)
2. **Current status spine** (`done` / `doing` / `next`)
3. **DoD progress** (what is complete vs incomplete)
4. **Remaining work checklist** (incomplete items only)
5. **Next 1–3 recommended actions + why**
6. **Risks/unknowns**

## Required content sources
- `contracts/meta/PROJECTS_INDEX.md`
- `contracts/meta/projects/finance_mvp/PROJECT_MAP.md`
- `contracts/meta/projects/finance_mvp/STATUS.md`
- `contracts/meta/projects/finance_mvp/DEFINITION_OF_DONE.md`
- `memory_pack/task_queue.md`

## Strict response rules
- Always include context + remaining work reminders, even for narrow user prompts.
- Keep track labels (`A`, `F`, `G`) explicit in recommendations.
- Do not mix finance_mvp context with other projects.

## Reasoning policy
- Never reveal private chain-of-thought.
- Instead provide:
  - **Rationale summary**: short, outcome-focused explanation.
  - **Alternatives considered**: concise bullets with trade-offs.
