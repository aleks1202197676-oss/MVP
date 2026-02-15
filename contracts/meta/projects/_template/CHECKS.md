# CHECKS: <project_id>

List all required verification checks. Multiple verification methods are supported.

## Rapid MTV (mandatory per PR)
- Every PR MUST include a short **How to verify** section that gives real signal in <=3 actions.
- Accepted signal format: UI scenario in <=3 clicks/steps OR CLI/hash check in <=3 commands.
- If signal cannot be produced in <=3 actions, split scope or explain why PR is not ready.

## Required CLI checks
- `command_here` — expected output/signal.

## Required UI checks
- Page/view + scenario + expected result.

## Required hash/integrity checks
- Artifact/path + hashing command + expected matching rule.

## Optional checks
- Non-blocking checks and when to run them.

## Check evidence format
- Where to store command output, screenshots, and hash logs.
