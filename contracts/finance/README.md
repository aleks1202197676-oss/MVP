# Finance pipeline contract

Finance pipeline включается через `config/hub.yaml`:

- `pipelines.finance.enabled` — включает расчёт.
- `pipelines.finance.purchase_window.start_date` / `end_date` — диапазон дат покупки (включительно).
- `pipelines.finance.model.*` — параметры модели расчёта результата.
- `pipelines.finance.outputs.latest_folder` — куда пишется `report.md`.

## Что делает pipeline

1. Перебирает все даты в `purchase_window`.
2. Для каждой даты считает результат модели.
3. Применяет уровни целей последовательно:
   - Уровень 1: не уходить в минус (или минимизировать убыток, если все варианты отрицательные).
   - Уровень 2: максимизировать результат среди прошедших уровень 1.
4. Пишет отчёт в `data/outputs/latest/finance/report.md`.

## Пример конфигурации

```yaml
pipelines:
  finance:
    enabled: true
    purchase_window:
      start_date: "2026-01-10"
      end_date: "2026-01-19"
    model:
      investment_amount: 100000
      holding_days: 30
      expected_daily_return: 0.0007
      daily_volatility: 0.01
      weekday_adjustments:
        "0": 0.0002
        "1": 0.0001
        "2": 0.0000
        "3": -0.0001
        "4": -0.0002
        "5": -0.0003
        "6": 0.0003
      monthly_adjustments:
        "1": 0.0002
        "2": 0.0001
        "3": 0.0000
        "4": -0.0001
    outputs:
      latest_folder: "data/outputs/latest/finance"
```
