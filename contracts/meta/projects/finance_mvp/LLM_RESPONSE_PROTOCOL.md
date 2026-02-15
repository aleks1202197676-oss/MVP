# LLM_RESPONSE_PROTOCOL: finance_mvp

Any chat assistant operating on `finance_mvp` MUST structure every response in this exact order:

1. **Project context snapshot** (goal + active tracks `A`, `F`, `G`)
2. **Current status spine** (`done` / `doing` / `next`)
3. **DoD progress** (what is complete vs incomplete)
4. **Rapid MTV** (short “How to verify” with real signal in <=3 actions)
5. **Scale decision** (`scale` / `don’t scale` + metrics: `time_to_signal_steps`, `conflict_rate`, `queue_independence`, `ci_pass_rate`)
6. **Agent delta** (`novelty_count`, `actionable_tasks_count`, `redundancy_count`, `conflict_risk` + gate decision)
7. **Next Codex TASK** (single scoped next task)
8. **Risks + rationale/alternatives** (no chain-of-thought)

## Required content sources
- `contracts/meta/PROJECTS_INDEX.md`
- `contracts/meta/projects/finance_mvp/PROJECT_MAP.md`
- `contracts/meta/projects/finance_mvp/STATUS.md`
- `contracts/meta/projects/finance_mvp/DEFINITION_OF_DONE.md`
- `memory_pack/task_queue.md`

## Strict response rules
- Always include context + MTV + explicit next task, even for narrow user prompts.
- Keep track labels (`A`, `F`, `G`) explicit in recommendations.
- Do not mix finance_mvp context with other projects.

## Known governance state anchor
- Use known facts: A12/A13/F5/F6 done; A14/A15/A16 done; A14 required-check enabling may still be pending.

## Reasoning policy
- Never reveal private chain-of-thought.
- Instead provide:
  - **Rationale summary**: short, outcome-focused explanation.
  - **Alternatives considered**: concise bullets with trade-offs.
