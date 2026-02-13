# AGENTS.md

## Source of truth
- Start from repository checkout; portable context is `latest_bundle.zip`.
- If checkout and bundle differ, follow checkout and report mismatch explicitly.

## Two-phase protocol
1. **PREFLIGHT-ONLY**: scope, risks, acceptance, exact commands.
2. **IMPLEMENT**: only after preflight, only inside approved scope.

## Track discipline
- Tracks: `PR-A*`, `PR-F*`, `PR-G*`.
- Deny-first behavior: do not touch out-of-track zones.
- On scope conflict: stop and return short actionable report.

## Operator-first preference
- If `tools/operator/**` exists, prefer proposing task/patch workflow there instead of broad ad-hoc edits.

## Safety
- Patch-first, minimal diff.
- No placeholders (`...`, `TBD`, fake paths).
- No new dependencies unless explicitly required.
