# Task Queue (cross-project)

Single queue for planned and active tasks across all projects.

## Record format (required fields)
- `project_id`: unique project key from `contracts/meta/PROJECTS_INDEX.md`
- `task_id`: stable task key (for example `PR-A16`)
- `track`: one track label (for example `A`, `F`, `G`)
- `allowlist`: explicit file/path scope that is allowed
- `denylist`: explicit forbidden paths
- `acceptance`: Definition of Done for this task
- `status`: one of `todo`, `in_progress`, `blocked`, `done`

## Queue

| project_id | task_id | track | allowlist | denylist | acceptance | status |
|---|---|---|---|---|---|---|
| finance_mvp | PR-A14 | A | governance/process docs and checks only | `.github/**`, pipeline runtime code | overlap guard policy implemented and documented end-to-end | done |
| finance_mvp | PR-A15 | A | `contracts/meta/**`, `memory_pack/**` | `.github/**`, pipeline runtime code | multi-project project-map and templates are stable | done |
| finance_mvp | PR-A16 | A | `contracts/meta/**`, `memory_pack/**` | `.github/**`, pipeline runtime code | stable status spine is present in bundle and handoff points are explicit | done |
| finance_mvp | PR-A14-MANUAL | A | repository Settings branch protection required checks | source code and runtime pipelines | required check for A14 is enabled in branch protection and confirmation is recorded | todo |
