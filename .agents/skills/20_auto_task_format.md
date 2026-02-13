# Skill: AUTO-TASK Card Output Format

## Rule
Агент генерирует task card без плейсхолдеров и с реальными путями из репозитория.

## Output template

### TASK
- **ID/Track**: `PR-<TRACK><N>`
- **Goal**: одно измеримое предложение.

### HARD RULES
- Scope: точный allowlist директорий/файлов.
- Запреты: явные deny-paths.
- No new deps (если не согласовано отдельно).

### PREFLIGHT
A) Где меняется логика (entrypoints + code path).
B) Источники риска/недетерминизма.
C) Exact file list to modify/create.
D) Acceptance criteria + commands.
E) Top-5 failure modes + mitigations.

### IMPLEMENT
- Шаги patch-плана в 3–7 пунктах.

### ACCEPTANCE
- Набор проверок с ожидаемыми сигналами pass/fail.

## Constraints
- Нельзя использовать заглушки вида `...`, `<path/to/file>`, `TBD`.
- Пути должны браться из фактического дерева репозитория.
- Команды должны быть исполнимы в текущем окружении.
