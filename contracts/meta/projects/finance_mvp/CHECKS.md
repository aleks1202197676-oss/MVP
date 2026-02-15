# CHECKS: finance_mvp

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
- Track PR overlap guard checks as planned/next until fully enforced (A14).

## Evidence format
- Store command output, hash output, and CI run references in PR notes and `WORKLOG.md`.
