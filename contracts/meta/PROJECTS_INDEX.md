# PROJECTS_INDEX

Single entry point for all project-level documentation included in `latest_bundle.zip`.

## Projects table

| project_id | purpose | entry doc path | current status doc path | DoD path | last updated date |
|---|---|---|---|---|---|
| finance_mvp | Deterministic finance MVP reporting flow and delivery governance. | `contracts/meta/projects/finance_mvp/PROJECT_MAP.md` | `contracts/meta/projects/finance_mvp/STATUS.md` | `contracts/meta/projects/finance_mvp/DEFINITION_OF_DONE.md` | 2026-02-15 |

## How to add a new project

1. Copy `contracts/meta/projects/_template/` to `contracts/meta/projects/<new_project_id>/`.
2. Update all required docs in the new folder (`PROJECT_MAP.md`, `STATUS.md`, `TRACKS.md`, `CHECKS.md`, `METRICS.md`, `DEFINITION_OF_DONE.md`, `WORKLOG.md`, `DECISION_LOG.md`, `LLM_RESPONSE_PROTOCOL.md`).
3. Add one row for the new project in the table above.
4. Ensure paths are valid and point to the new folder only (no cross-project mixing).
5. Rebuild/publish `latest_bundle.zip` so handoff agents receive the new project context.
