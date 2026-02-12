# Finance MVP input schema

Canonical input root: `data/raw/finance_mvp/`

## cards.csv
Required columns:
- `card_id` (string, unique)
- `credit_limit` (float, > 0)
- `apr` (float, annual percentage rate)
- `min_payment_rate` (float in range 0..1)
- `cycle_day` (int 1..31)
- `due_day` (int 1..31)

## items.csv
Required columns:
- `purchase_date` (ISO date `YYYY-MM-DD`)
- `card_id` (string, must exist in `cards.csv`)
- `category` (string)
- `amount` (float, > 0)
- `priority` (string, e.g. `essential`, `normal`, `low`)

## budget.csv
Required columns:
- `month` (string `YYYY-MM`)
- `income` (float)
- `fixed_expenses` (float)
- `target_savings` (float)
