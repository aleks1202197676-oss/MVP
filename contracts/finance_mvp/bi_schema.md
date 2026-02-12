# Finance MVP BI schema

## Purpose

This document describes BI-facing tables produced by `finance_mvp` and a deterministic graph export for Flying Logic.

## Canonical input root

- `data/raw/finance_mvp/`

## Core output tables

### 1) `payments_daily`

- Physical file: `outputs/latest/finance_mvp/payments_daily.csv`
- Grain: one payment event per `date` + `card_id` + `payment_type`.
- Primary key (logical): (`date`, `card_id`, `payment_type`).
- Columns (stable order):
  1. `date` (date, ISO `YYYY-MM-DD`)
  2. `card_id` (string)
  3. `payment_type` (string)
  4. `amount` (decimal(18,2))

### 2) `payments_monthly`

- Physical file: `outputs/latest/finance_mvp/payments_monthly.csv`
- Grain: one row per `month` + `card_id`.
- Primary key (logical): (`month`, `card_id`).
- Columns (stable order):
  1. `month` (string, `YYYY-MM`)
  2. `card_id` (string)
  3. `statement_balance` (decimal(18,2))
  4. `min_payment` (decimal(18,2))
  5. `planned_payment` (decimal(18,2))
  6. `ending_balance` (decimal(18,2))

### 3) `purchase_plan`

- Physical file: `outputs/latest/finance_mvp/purchase_plan.csv`
- Grain: one purchase item.
- Primary key (logical): (`purchase_date`, `card_id`, `category`, `amount`).
- Columns (stable order):
  1. `purchase_date` (date, ISO `YYYY-MM-DD`)
  2. `card_id` (string)
  3. `category` (string)
  4. `amount` (decimal(18,2))
  5. `priority` (string)
  6. `planned_payoff_month` (string, `YYYY-MM`)
  7. `decision_reason` (string)

### 4) `kpi_timeseries`

- Physical file: `outputs/latest/finance_mvp/kpi_timeseries.csv`
- Grain: one row per `month`.
- Primary key (logical): (`month`).
- Columns (stable order):
  1. `month` (string, `YYYY-MM`)
  2. `purchase_total` (decimal(18,2))
  3. `payment_total` (decimal(18,2))
  4. `ending_debt` (decimal(18,2))
  5. `utilization_ratio` (decimal(10,4))

## Flying Logic graph export (deterministic)

- Folder: `outputs/latest/finance_mvp/flying_logic/`
- Files:
  - `nodes.csv`
  - `edges.csv`
- Determinism rules:
  - stable column order,
  - stable sorting by ids,
  - stable numeric formatting (`.2f` for money-like values).

### `nodes.csv` schema

Columns (stable order):
1. `node_id` (string, unique id)
2. `label` (string)
3. `type` (enum-like string: `card` | `item` | `kpi`)
4. `group` (string; e.g. `cards`, `items`, `kpi_summary`, `kpi_timeseries`)
5. `weight` (string-encoded numeric)
6. `note` (string)

Contains nodes for:
- cards,
- purchase items,
- KPI summary (`total_interest`, `total_paid`, `items_purchased`, `available_budget`),
- KPI monthly ending debt points.

### `edges.csv` schema

Columns (stable order):
1. `from_id` (string, FK → `nodes.node_id`)
2. `to_id` (string, FK → `nodes.node_id`)
3. `relation` (enum-like string: `funded_by` | `contributes_to` | `constrained_by`)
4. `weight` (string-encoded numeric)
5. `note` (string)

Examples of relations:
- item → card (`funded_by`),
- item/card/KPI → KPI (`contributes_to`),
- `available_budget` → `total_paid` (`constrained_by`).

## Relationships for BI model

Recommended joins:
- `payments_daily.card_id` → `dim_card.card_id`
- `payments_monthly.card_id` → `dim_card.card_id`
- `purchase_plan.card_id` → `dim_card.card_id`
- `purchase_plan.category` → `dim_item.category`
- month/date fields connect through a dedicated Date table.

Suggested relationship style in Power BI:
- star schema,
- single-direction filters from dimensions to facts,
- avoid bidirectional filters unless explicitly required.

## Power BI-friendly guidance

1. **Date table**
   - Build a conformed Date dimension with daily grain.
   - Add derived attributes: Year, Quarter, Month Number, Month Name, Year-Month.
   - Link:
     - Date[Date] ↔ `payments_daily.date`,
     - Date[Year-Month] ↔ monthly facts (`payments_monthly.month`, `kpi_timeseries.month`, `purchase_plan.planned_payoff_month`).

2. **`dim_card` suggestion**
   - Source: canonical cards input (`data/raw/finance_mvp/cards.csv`).
   - Columns: `card_id`, `credit_limit`, `apr`, `min_payment_rate`, `cycle_day`, `due_day`.

3. **`dim_item` suggestion**
   - Create small dimension from `purchase_plan` distinct values:
     - `category`,
     - optional `priority` bucket,
     - optional semantic grouping (essential/optional).

4. **Measures**
   - Recompute monetary measures as numeric in BI layer.
   - Keep CSV value parsing explicit to avoid locale issues.

5. **Graph usage in BI / Flying Logic**
   - Import `nodes.csv` and `edges.csv` as two tables.
   - Use `node_id` as entity key.
   - Use `relation` + `group/type` to drive visual encoding.
