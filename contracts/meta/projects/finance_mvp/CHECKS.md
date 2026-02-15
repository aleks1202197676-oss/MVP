# CHECKS: finance_mvp

## Rapid MTV (mandatory per PR)
- Every finance_mvp PR MUST include **How to verify** with real signal in <=3 actions.
- Prefer deterministic CLI/hash signal in <=3 commands; use UI path only when UI surface changed.
- If <=3-step signal is not possible, split PR scope before merge.

## Required CLI checks
- Verify deterministic report generation command(s) produce stable `report.md` output.
- Verify deterministic input fingerprint exists in generated report.

## Required UI checks
- Not required by default for finance_mvp unless UI artifacts are added.

## Required hash/integrity checks
- Compare hashes/fingerprints for expected deterministic inputs and resulting report artifacts.

## Governance checks
- Confirm CI publish/verify flow for `latest_bundle` is active (A12).
- Confirm manual `workflow_dispatch` permission on `main` publish path is preserved (A13).
- Confirm PR overlap guard behavior is documented/detected (A14/A15/A16), and note that required-check enabling from A14 may still be pending.

## Evidence format
- Store command output, hash output, and CI run references in PR notes and `WORKLOG.md`.
