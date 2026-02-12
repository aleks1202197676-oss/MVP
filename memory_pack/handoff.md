# Handoff: MVP

Вставь этот блок в новый чат и продолжай работу с актуальным контекстом.

## Скачать latest_bundle.zip
- One-click: https://github.com/aleks1202197676-oss/MVP/releases/download/latest-bundle/latest_bundle.zip
- Fallback (страница релиза): https://github.com/aleks1202197676-oss/MVP/releases/tag/latest-bundle

## Быстрый запуск (локально/CI)
```bash
python -m pipelines.run_all
```
После запуска обновится `data/ai_contract/latest/latest_bundle.zip`.

## Что держать актуальным
- `memory_pack/handoff.md` — краткий статус и ссылки.
- `memory_pack/chats/` — ключевые заметки из чатов (не полный архив).

## Правила PR
- База PR всегда `main`.
- 1 задача → 1 ветка → 1 PR → merge → удалить ветку.
- Публикация release asset только после проверки содержимого zip.
