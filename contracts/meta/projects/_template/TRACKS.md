# TRACKS: <project_id>

Define project execution lanes. This structure supports multiple tracks simultaneously.

## Track catalog
| track_id | objective | scope allowlist | denylist | completion signal |
|---|---|---|---|---|
| A | Meta/ops workstream objective | Allowed docs/scripts/paths | Forbidden paths/actions | Objective completion rule |
| F | Functional/business workstream objective | ... | ... | ... |
| G | Governance/guardrail workstream objective | ... | ... | ... |

## Track coordination rules
- How tracks interact without scope collisions.
- Escalation path for conflicts.
