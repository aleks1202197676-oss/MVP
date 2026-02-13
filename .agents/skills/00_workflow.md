# 00_workflow

## Execution flow
1. **PREFLIGHT**
   - Find entrypoints and exact files.
   - List risks, acceptance criteria, and copy-paste checks.
2. **IMPLEMENT**
   - Apply smallest patch in approved scope only.
3. **VERIFY**
   - Run required checks and verify changed-file scope.
4. **DELIVER**
   - Provide Summary / Testing / Risks-Rollback.

## Guardrails
- Fail fast on scope mismatch.
- Keep diagnostics short and actionable.
- Never emit placeholder content.
