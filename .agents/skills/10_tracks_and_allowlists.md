# 10_tracks_and_allowlists

## Track detection
- Primary: PR title prefix (`PR-A`, `PR-F`, `PR-G`).
- Fallback: labels.

## Policy
- Minimal scope by default.
- Deny rules override assumptions.

## Deny-first rules
### `PR-F*`
- Must NOT touch: `.github/workflows/**`, `tools/operator/**`, `memory_pack/**`.

### `PR-A*`
- Must NOT touch: `pipelines/finance*`, `contracts/finance*`, `data/raw/finance*`, `outputs/latest/finance*`.

### `PR-G*`
- May touch process/gates/instructions.
- Must avoid unrelated product/data mutations.

## Enforcement
- Any deny violation => fail with concise list of offending paths.
