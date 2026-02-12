# Finance variables dictionary

## Inputs
- `card_id`: card identifier used for joins.
- `statement_day`: statement day of month.
- `apr`: annual percentage rate (informational in v1).
- `min_payment_rate`: minimum payment percentage applied to each purchase.
- `item_id`: purchase identifier.
- `purchase_date`: purchase date in ISO format.
- `amount`: purchase amount.
- `category`: purchase category label.
- `month`: budget month key (`YYYY-MM`).
- `payment_budget`: planned payment capacity for month.

## Derived fields
- `due_date`: `purchase_date + 25 days`.
- `budget_month`: `due_date` month (`YYYY-MM`).
- `required_payment`: `amount * min_payment_rate / 100`.
- `paid_payment`: allocated from monthly budget.
- `unfunded_payment`: `required_payment - paid_payment`.

## Outputs
- `payments_daily.csv`: daily aggregation by `payment_date`.
- `payments_monthly.csv`: month aggregation by `month`.
- `purchase_plan.csv`: row-level deterministic payment allocation plan.
- `report.md`: assumptions and KPIs.
