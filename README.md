# Unified Hub Starter (Avito + Health + Models)

Это **каркас** для единой системы моделирования/планирования/прогнозирования/визуализации.
Он специально сделан так, чтобы:
- быть **модульным** (плагин-пайплайны: avito / health / models / tasks),
- иметь **единый run_id + latest/history**,
- собирать **LLM-bundle.zip** для анализа в ChatGPT/Gemini без ручной подготовки,
- легко расширяться новыми входами/выходами/логикой.

## Быстрый старт
1) Открой папку `00__CLICK_HERE` и запусти `00__RUN_ALL.cmd`
2) Открой `data/outputs/latest` и смотри результаты
3) Если хочешь прогнать только одну подсистему:
   - `python -m pipelines.health.import_samsung_health`
   - `python -m pipelines.models.solve_equation_model`

## Где что лежит
- `config/hub.yaml` — главный конфиг (что включено, где входы, горизонты, где БД).
- `contracts/` — формальные контракты входов/выходов (JSON/YAML).
- `pipelines/` — пайплайны по доменам (Avito/Health/Models).
- `core/` — общие утилиты: run_id, упаковка LLM-bundle, валидация, логирование.
- `data/raw` — «как пришло».
- `data/staged` — «приведённые форматы» (нормализация).
- `data/mart` — агрегаты/фичи для BI и моделей.
- `data/outputs/latest` — последние отчёты/таблицы/графики.
- `data/outputs/history/<run_id>` — история прогонов.

## Как расширять
Добавляешь новый пайплайн:
1) `pipelines/<new_domain>/...`
2) `contracts/<new_domain>_contract.json`
3) Регистрируешь в `config/hub.yaml` и в `pipelines/run_all.py`

