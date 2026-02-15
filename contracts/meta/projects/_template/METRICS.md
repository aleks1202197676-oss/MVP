# METRICS: <project_id>

## Outcome metrics
- Metric, target, and measurement source.

## Scale / Don’t scale metrics
- `time_to_signal_steps` — target: 1–3 steps to get real PR signal.
- `conflict_rate` — PR overlaps per week.
- `queue_independence` — count of disjoint allowlists/parallel queues.
- `ci_pass_rate` — rough pass ratio for last N runs.

## Agent Delta (necessity/sufficiency)
- `novelty_count` — number of net-new useful contributions.
- `actionable_tasks_count` — number of concrete, executable tasks produced.
- `redundancy_count` — duplicate/low-value outputs.
- `conflict_risk` — `low` / `med` / `high`.
- Gate: add new agent only if novelty and actionability justify it relative to redundancy and conflict risk.

## Process metrics
- Throughput/lead-time/rework indicators.

## Quality metrics
- Defect rate, determinism rate, drift checks, etc.

## Reporting cadence
- Daily/weekly/release cadence and owner.
