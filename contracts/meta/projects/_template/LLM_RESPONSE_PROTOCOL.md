# LLM_RESPONSE_PROTOCOL: <project_id>

Any chat assistant operating on this project MUST structure every response in this exact order:

1. **Project context snapshot** (goal, active tracks, scope boundaries)
2. **Current status spine** (`done` / `doing` / `next` from project status docs)
3. **DoD progress** (completed vs incomplete checklist items)
4. **Remaining work checklist** (explicit incomplete items only)
5. **Next 1–3 recommended actions + why**
6. **Risks/unknowns**

## Required source documents
- `contracts/meta/PROJECTS_INDEX.md`
- `contracts/meta/projects/<project_id>/PROJECT_MAP.md`
- `contracts/meta/projects/<project_id>/STATUS.md`
- `contracts/meta/projects/<project_id>/DEFINITION_OF_DONE.md`
- `memory_pack/task_queue.md` (for cross-project prioritization)

## Strict response rules
- Always remind context and remaining work, even if user asks a narrow question.
- Never mix data between different `project_id` values.
- If project context is missing or conflicting, stop and request clarification before proposing actions.

## Reasoning policy
- Do not reveal private chain-of-thought.
- Provide a short **Rationale summary** section.
- Provide **Alternatives considered** as concise bullets.
