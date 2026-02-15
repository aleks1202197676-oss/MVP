# Handoff: MVP

Вставь этот блок в новый чат и продолжай работу с актуальным контекстом.

## Start here (stable entrypoint)
1. Open `contracts/meta/PROJECTS_INDEX.md`.
2. Pick target `project_id`.
3. Follow that project's `LLM_RESPONSE_PROTOCOL.md` + `STATUS.md` + `DEFINITION_OF_DONE.md`.

## Скачать latest_bundle.zip
- One-click: https://github.com/aleks1202197676-oss/MVP/releases/download/latest-bundle/latest_bundle.zip
- Fallback (страница релиза): https://github.com/aleks1202197676-oss/MVP/releases/tag/latest-bundle

## Быстрый запуск (локально/CI)
```bash
python -m pipelines.run_all
```
После запуска обновится `data/ai_contract/latest/latest_bundle.zip`.

## How to work with Codex safely
- 1 задача → 1 ветка `codex/*` → 1 PR → merge → удалить ветку.
- Перед коммитом и перед PR запускать scope-guard: `git diff --name-only`.
- Работать только в allowlist; denylist всегда приоритетнее.
- Не вести параллельные пересекающиеся PR по одному и тому же scope.

## Definition of Done (current version)
- Finance MVP DoD source: `contracts/meta/projects/finance_mvp/DEFINITION_OF_DONE.md`.
- Confirmed completed items: `A12`, `A13`, `F5`, `F6`.
- Planned/in-flight governance items tracked here: `A14`, `A15`, `A16`.

## Next tasks
- Primary queue: `memory_pack/task_queue.md`.
- Keep status transitions explicit (`todo` → `in_progress` → `blocked` / `done`).

## Что держать актуальным
- `memory_pack/handoff.md` — краткий статус и ссылки.
- `memory_pack/task_queue.md` — единая очередь задач по проектам.
- `memory_pack/chats/` — ключевые заметки из чатов (без смешения проектов).
