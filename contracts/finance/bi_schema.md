# Finance BI schema (v1)

## fact_purchase_plan
Grain: one row per purchase (`item_id`).

Columns:
- `payment_date` DATE
- `budget_month` STRING (`YYYY-MM`)
- `card_id` STRING (FK -> dim_card.card_id)
- `item_id` STRING (PK)
- `purchase_date` DATE
- `due_date` DATE
- `amount` DECIMAL(12,2)
- `required_payment` DECIMAL(12,2)
- `paid_payment` DECIMAL(12,2)
- `unfunded_payment` DECIMAL(12,2)

## agg_payments_daily
Grain: one row per day (`payment_date`).

Columns:
- `payment_date` DATE (PK)
- `purchase_count` INT
- `required_payment` DECIMAL(12,2)
- `paid_payment` DECIMAL(12,2)
- `unfunded_payment` DECIMAL(12,2)

## agg_payments_monthly
Grain: one row per month (`month`).

Columns:
- `month` STRING (`YYYY-MM`, PK)
- `purchase_count` INT
- `required_payment` DECIMAL(12,2)
- `paid_payment` DECIMAL(12,2)
- `unfunded_payment` DECIMAL(12,2)

## Keys and joins
- `fact_purchase_plan.card_id` -> `cards.csv.card_id`.
- `fact_purchase_plan.item_id` is unique in input.
