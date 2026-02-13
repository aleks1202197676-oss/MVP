# Track Skill: Allowlists / Deny Rules

## Track detection
- По префиксу в названии PR: `PR-A`, `PR-F`, `PR-G`.
- Если префикс отсутствует — использовать labels.

## Philosophy
- По умолчанию минимальный scope.
- Явные deny-правила важнее неявных допущений.

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
- Можно менять процесс/гейты/инфраструктуру.
- Нельзя вносить несвязанные продуктовые изменения в данные/доменные артефакты.

## Operational rule
- Любое нарушение deny-правил = мгновенный fail с коротким списком нарушивших путей.
