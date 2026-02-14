# Track Skill: Allowlists / Deny Rules

## Track detection
- По префиксу PR: `PR-A`, `PR-F`, `PR-G`.
- Если префикс отсутствует — использовать labels.

## Philosophy
- По умолчанию минимальный scope.
- Явные deny-правила сильнее неявных допущений.
- Scope-check выполняется через `git diff --name-only`.

## Deny examples
### PR-F* (finance-only)
- Нельзя менять:
  - `.github/workflows/**`
  - `tools/operator/**`
  - `memory_pack/**`

### PR-A*
- Нельзя менять:
  - `pipelines/finance*`
  - `contracts/finance*`
  - `data/raw/finance*`
  - `outputs/latest/finance*`

### PR-G*
- Разрешены process/gates/infrastructure изменения.
- Запрещены несвязанные продуктовые изменения в данных/доменных артефактах.

## Operational rule
- Любое нарушение deny-правил = мгновенный fail с коротким списком нарушивших путей.
- Перед commit и перед PR scope-check обязателен.
