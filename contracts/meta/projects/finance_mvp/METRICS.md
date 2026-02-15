# METRICS: finance_mvp

## Outcome metrics
- Deterministic report success rate (`report.md` reproducibility across runs).
- Deterministic fingerprint presence rate in reports.

## Scale / Don’t scale metrics
- `time_to_signal_steps` — target 1–3 (PR verification must stay in rapid MTV band).
- `conflict_rate` — overlapping PR incidents per week across active tracks.
- `queue_independence` — number of disjoint allowlists that can run in parallel.
- `ci_pass_rate` — rough pass ratio for recent N CI runs.

## Agent Delta (necessity/sufficiency)
- `novelty_count` — net-new useful deltas from agent outputs.
- `actionable_tasks_count` — concrete tasks that can be executed without reinterpretation.
- `redundancy_count` — repeated or non-actionable outputs.
- `conflict_risk` — low/med/high for overlap or policy collision.
- Gate: add new agent only if novelty and actionability justify it versus redundancy/conflict risk.

## Process metrics
- Bundle publish/verify success rate for handoff artifacts.
- Governance check completion rate per PR.

## Quality metrics
- Scope-violation incidents per track.
- PR overlap/conflict incidents detected vs prevented.

## Reporting cadence
- Update on each PR for `STATUS.md` and `WORKLOG.md`.
- Review DoD progress at least once per active iteration.
