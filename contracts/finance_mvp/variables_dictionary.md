# Finance MVP variable dictionary

## Input variables
- `card_id`: card identifier used for joins between cards and purchases.
- `credit_limit`: total limit for utilization KPI denominator.
- `apr`: annual rate retained for future amortization extensions.
- `min_payment_rate`: baseline payment policy by card.
- `cycle_day`: statement cycle day (currently informational in MVP).
- `due_day`: due day used to build deterministic `payments_daily.csv` dates.
- `purchase_date`: transaction date.
- `category`: transaction category tag.
- `amount`: transaction amount.
- `priority`: transaction priority for planning metadata.
- `month`: budget month key in `YYYY-MM` format.
- `income`, `fixed_expenses`, `target_savings`: derive debt service envelope.

## Output variables
- `statement_balance`: monthly per-card sum of purchases.
- `min_payment`: `statement_balance * min_payment_rate`.
- `planned_payment`: deterministic payment allocation capped by available budget.
- `ending_balance`: `statement_balance - planned_payment`.
- `purchase_total`: monthly sum of statement balances.
- `payment_total`: monthly sum of planned payments.
- `ending_debt`: monthly residual debt.
- `utilization_ratio`: `purchase_total / sum(credit_limit)`.
