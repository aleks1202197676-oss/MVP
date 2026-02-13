# 20_auto_task_format

## AUTO-TASK (no placeholders)

### TASK
- ID/Track: `PR-<TRACK><N>`
- Goal: one measurable outcome.

### HARD RULES
- Exact allowlist scope.
- Explicit deny paths.
- No new deps unless approved.

### PREFLIGHT
A) Entrypoints + code path.
B) Non-determinism / risk sources.
C) Exact files to create/modify.
D) Acceptance criteria + commands.
E) Top-5 failure modes + mitigations.

### IMPLEMENT
- 3–7 concrete patch steps.

### ACCEPTANCE
- Executable pass/fail checks.

## Constraints
- Do not output `...`, `TBD`, or fake paths.
- Infer real paths from repository tree.
- Build task card from actual repo state, not assumptions.
