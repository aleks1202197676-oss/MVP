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

Печать шаблона задачи (web → queue):

```bash
python -m tools.operator.operator --print-task-template
```

Windows:

```cmd
tools\operator\START_OPERATOR.cmd
```

## Формат задачи

Рекомендуемый формат (массив `patches`):

```json
{
  "task_id": "task-001",
  "repo": "owner/repo",
  "base_branch": "main",
  "branch_name": "operator/task-001",
  "patches": [
    "tools/operator/queue/patches/task-001.patch"
  ],
  "commands": [
    "python -m py_compile tools/operator/operator.py"
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

Совместимость: одиночное поле `patch_file` тоже поддерживается.

## Web → operator queue за 60 секунд

1. Сгенерируйте заготовку:
   ```bash
   python -m tools.operator.operator --print-task-template
   ```
2. Вставьте JSON в файл `tools/operator/queue/inbox/<task_id>.json`.
3. Положите patch-файл(ы) в `tools/operator/queue/patches/`.
4. Проверьте `allowlist_globs` (только разрешённые пути).
5. Запустите оператор:
   ```bash
   python -m tools.operator.operator --once
   ```
6. Если `gh` недоступен, оператор автоматически уйдёт в `push_only` и запишет `compare_url` + `next_action` в `tools/operator/logs/operator_events.jsonl`.

## Безопасность

- По умолчанию запрещены изменения в `.github/workflows/**`.
- Любой путь в патче и staged-изменениях должен соответствовать `allowlist_globs`.
- Все patch-файлы должны находиться строго в `tools/operator/queue/patches/`.

## Поведение

1. Проверяет `tools/operator/STOP`; если файл существует — безопасно завершает работу.
2. Создает/пересоздает рабочую ветку от `base_branch`.
3. Применяет patch-файлы через `git apply --3way --index`.
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
