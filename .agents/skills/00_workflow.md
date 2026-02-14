# Workflow Skill: Preflight → Implement

## Purpose
Единый операционный протокол выполнения PR.

## Steps
1. **Preflight**
   - Зафиксировать track (`PR-A*` / `PR-F*` / `PR-G*`) и границы scope.
   - Проверить состояние репозитория: `branch`, `git status`, `git diff --name-only`.
   - Описать риски (top-5 failure modes) и mitigation.
   - Определить acceptance и команды проверки.
   - Проверить сеть, если нужны remote/bundle/PR операции.
2. **Implement**
   - Вносить минимальные изменения только в согласованном scope.
   - Сохранять детерминизм (порядок, формат, отсутствие плавающих значений).
3. **Verify**
   - Выполнить проверки из acceptance.
   - Перед commit и PR повторить scope-check: `git diff --name-only`.
4. **Deliver**
   - Дать короткий summary и фактические результаты проверок.

## Mandatory quality rules
- Fail-fast диагностика вместо длинных логов.
- Никаких placeholder-путей/значений.
- Никаких необоснованных расширений scope.
