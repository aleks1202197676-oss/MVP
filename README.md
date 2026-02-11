# Unified Hub Starter (Avito + Health + Models)

Канонический каркас Unified Hub с модульной структурой папок и единым запуском через `pipelines.run_all`.

## Быстрый старт
1. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Запусти полный прогон:
   ```bash
   python -m pipelines.run_all
   ```
3. Проверь результаты:
   - `data/outputs/latest/`
   - `data/ai_contract/latest/run_manifest.json`
   - `data/ai_contract/latest/latest_bundle.zip`

Для Windows можно запускать `.cmd`-файлы из папки `00__CLICK_HERE/`.

## Структура
- `config/hub.yaml` — главный конфиг Unified Hub.
- `core/` — общие утилиты (`run_registry.py`, `llm_bundle.py`).
- `pipelines/` — orchestration и доменные пайплайны:
  - `pipelines/run_all.py`
  - `pipelines/health/import_samsung_health.py`
  - `pipelines/models/solve_equation_model.py`
- `contracts/` — контракты и модельные спецификации (`model_spec.yaml`).
- `data/`
  - `raw/`, `staged/`, `mart/`
  - `outputs/latest/`, `outputs/history/`
  - `ai_contract/latest/`
- `00__CLICK_HERE/` — Windows-скрипты быстрого запуска.

## Примечание
Сейчас это каркас без добавления финмодельной логики: запускаются безопасные заглушки пайплайнов, формируется run manifest и bundle артефактов.
