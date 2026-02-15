# TRACKS: finance_mvp

## Track catalog
| track_id | objective | scope allowlist | denylist | completion signal |
|---|---|---|---|---|
| A | Meta/ops governance for bundle + handoff + docs | `contracts/meta/**`, release/bundle process docs | Functional finance logic changes without track approval | Required governance docs and bundle process controls documented and active |
| F | Deterministic finance MVP reporting outputs | `contracts/finance_mvp/**`, deterministic report artifacts | Unrelated product domains or governance-only changes | Deterministic `report.md` and fingerprint checks pass |
| G | Cross-PR/process guardrails | Governance policies/checks for conflict prevention | Scope expansion beyond approved guardrail plan | Overlap guard checks enforced and evidenced |

## Track coordination rules
- Each PR must declare one track and stay within that track scope.
- Cross-track dependencies must be noted in `STATUS.md` and `WORKLOG.md`.
- Governance (`G`) can block merge when overlap or safety checks fail.
