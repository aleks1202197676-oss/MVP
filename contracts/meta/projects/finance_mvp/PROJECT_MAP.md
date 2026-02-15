# PROJECT_MAP: finance_mvp

## Mission
- Deliver deterministic finance MVP reporting artifacts with reliable LLM handoff context.

## Goals
- Maintain deterministic `report.md` output for finance_mvp runs.
- Preserve deterministic input fingerprint in report output.
- Keep handoff docs structured for multi-track operations (`A`, `F`, `G`).

## Non-goals
- No expansion into unrelated pipelines or product domains.
- No cross-project status mixing.

## Tracks
- `A` (meta/ops): bundle/handoff governance and process guardrails.
- `F` (finance functionality): deterministic reporting behavior.
- `G` (governance): overlap and safety controls.

## Deliverables
- Deterministic `report.md` artifact.
- Project documentation set in `contracts/meta/projects/finance_mvp/`.

## Required checks
- See `CHECKS.md`.

## Metrics
- See `METRICS.md`.

## Definition of done
- See `DEFINITION_OF_DONE.md`.

## Known risks
- PR scope overlap can still occur without strict guard enforcement.
- Bundle publishing drift can reduce handoff quality.
