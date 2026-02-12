# Finance input schema

Canonical input root: `data/raw/finance/`.

## cards.csv
Required columns (stable header order):
1. `card_id` (string, primary key)
2. `statement_day` (int, 1..28)
3. `apr` (float, annual percentage rate)
4. `min_payment_rate` (float, percent of purchase amount)

## items.csv
Required columns (stable header order):
1. `item_id` (string, primary key)
2. `card_id` (string, FK -> cards.card_id)
3. `purchase_date` (date, `YYYY-MM-DD`)
4. `amount` (float, >= 0)
5. `category` (string)

## budget.csv
Required columns (stable header order):
1. `month` (string, `YYYY-MM`)
2. `payment_budget` (float, >= 0)
