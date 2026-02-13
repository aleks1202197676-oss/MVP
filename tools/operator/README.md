# Local Operator (gh-based)

Минимальный локальный оператор для автоматизации PR-потока без ручных кликов в веб-интерфейсе.

## Требования

- `git`
- `python` 3.10+
- `gh` (GitHub CLI) + `gh auth login` **опционально** (только для `mode=gh` и авто-режима с PR через CLI)

## Структура

- `tools/operator/operator.py` — основной цикл обработки задач
- `tools/operator/queue/inbox/*.json` — входящие задачи
- `tools/operator/queue/patches/*.patch` — unified diff патчи
- `tools/operator/queue/archive/` — архив обработанных задач (`*.done.json`, `*.failed.json`, `*.skipped.json`)
- `tools/operator/logs/operator_events.jsonl` — append-only события
- `tools/operator/logs/processed_tasks.json` — idempotency state
- `tools/operator/STOP` — аварийная остановка (если файл существует, цикл завершается)

## Запуск

Linux/macOS:

```bash
python -m tools.operator.operator
```

Однократный прогон:

```bash
python -m tools.operator.operator --once
```

Windows:

```cmd
tools\operator\START_OPERATOR.cmd
```

## Формат задачи

Сохраните JSON в `tools/operator/queue/inbox/<task>.json`:

```json
{
  "task_id": "task-001",
  "repo": "owner/repo",
  "base_branch": "main",
  "branch_name": "operator/task-001",
  "patch_file": "tools/operator/queue/patches/task-001.patch",
  "commands": [
    "python -m pytest -q"
  ],
  "allowlist_globs": [
    "tools/operator/**",
    "docs/**"
  ],
  "pr_title": "Operator task-001",
  "pr_body": "Automated patch apply",
  "mode": "auto"
}
```

## Безопасность

- По умолчанию запрещены изменения в `.github/workflows/**`.
- Любой путь в патче и staged-изменениях должен соответствовать `allowlist_globs`.
- Патч должен находиться строго в `tools/operator/queue/patches/`.

## Поведение

1. Проверяет `tools/operator/STOP`; если файл существует — безопасно завершает работу.
2. Создает/пересоздает рабочую ветку от `base_branch`.
3. Применяет патч через `git apply --3way --index`.
4. Запускает команды в порядке из `commands`.
5. Делает commit/push.
6. Режимы публикации:
   - `mode=gh`: создает PR через `gh pr create` и включает `gh pr merge --auto --squash --delete-branch`.
   - `mode=push_only`: только push ветки, записывает `compare_url` и безопасные следующие шаги для ручного PR.
   - `mode=auto` (по умолчанию): если `gh` установлен и авторизован — ведет себя как `gh`, иначе как `push_only`.

## Экстренная остановка

Создайте файл:

```bash
touch tools/operator/STOP
```

Чтобы возобновить работу, удалите файл:

```bash
rm tools/operator/STOP
```
