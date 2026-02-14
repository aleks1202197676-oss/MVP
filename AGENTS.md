# AGENTS.md

## Source of truth
- **Единый источник истины для агента: `latest_bundle.zip`**.
- Перед выполнением задач агент опирается на содержимое bundle и правила этого репозитория.

## Master rules
- Поддерживаемые треки: `PR-A*`, `PR-F*`, `PR-G*`.
- Трек обязателен: любые изменения вне трекового scope запрещены.
- Обязателен режим `Preflight → Implement`.
- Любой конфликт scope/denylist = fail-fast с коротким actionable сообщением.

## Two-phase protocol
1. **Preflight first**
   - Проверить ветку, `git status`, target track и фактический scope.
   - Зафиксировать allowlist/denylist, риски и команды проверки.
   - Проверить сеть, если нужны bundle/remote/PR операции.
2. **Implement second**
   - Вносить минимальные patch-изменения только в разрешённом scope.
   - Не расширять scope без явного согласования.

## Scope guard
- Перед коммитом и перед PR обязателен `git diff --name-only`.
- Если найден путь вне allowlist или denylist нарушен — работа останавливается до исправления scope.

## Stop conditions
- Неопределённый track или конфликт allowlist/denylist.
- Любые изменения вне согласованного scope.
- Невозможно подтвердить результаты проверок.

## Patch-first execution
- Предпочитать небольшие, проверяемые patch-изменения.
- Не добавлять placeholder-значения и заглушки (`...`, `TODO` без контекста).

## Operator-first preference
- Когда возможно, задачи/патчи оформлять через очередь `tools/operator` (task queue / handoff) для прозрачного handoff.

## Safety
- Не добавлять новые зависимости без явной необходимости.
- Всегда указывать команды проверки и фактический результат.
