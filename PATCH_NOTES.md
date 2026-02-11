# PATCH NOTES

## Что сделано
- Добавлен минимальный Finance MVP pipeline с детерминированной эвристикой распределения покупок по картам.
- Добавлены шаблоны входных данных в `inputs/finance/*`, чтобы запуск работал на чистом клоне.
- Обновлён `pipelines/run_all.py`: при `pipelines.finance.enabled: true` сначала запускается finance pipeline, затем собирается meta + bundle.
- В `config/hub.yaml` и `hub.yaml` включён флаг `pipelines.finance.enabled: true` по умолчанию для локального MVP-прогона.

## Выходные артефакты Finance
Pipeline пишет в `data/outputs/latest/finance/`:
- `payment_schedule.csv`
- `cashflow_daily.csv`
- `summary_metrics.json`
- `constraint_violations.csv`
- `report.md`

## Детерминизм
- Явные сортировки входов/выходов.
- Фиксированное форматирование денежных значений (2 знака).
- Стабильные схемы CSV/JSON (порядок колонок и `sort_keys=True` в JSON).
