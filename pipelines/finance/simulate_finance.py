from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import pandas as pd

from pipelines.finance.ingest_finance import FinanceInputs


@dataclass
class FinanceSimulationResult:
    purchases_plan: pd.DataFrame
    payments_plan_daily: pd.DataFrame
    item_balance_daily: pd.DataFrame
    card_balance_daily: pd.DataFrame
    kpi_daily: pd.DataFrame
    violations: pd.DataFrame


def _choose_price(item: pd.Series, price_mode: str) -> float:
    if price_mode == "fixed":
        return float(item["price_value"])
    return float(item["price_max"] if pd.notna(item["price_max"]) else item["price_value"])


def _pick_card(allowed: list[str], cards: pd.DataFrame) -> str:
    candidates = cards[cards["card_id"].isin([x for x in allowed if x.startswith("card")])]
    if candidates.empty:
        return "cash"
    candidates = candidates.sort_values(["grace_days", "apr_outside_grace"], ascending=[False, True])
    return str(candidates.iloc[0]["card_id"])


def _choose_purchase_date(item: pd.Series, config_start: pd.Timestamp) -> pd.Timestamp:
    if item["purchase_date_mode"] == "fixed" and pd.notna(item.get("purchase_date_fixed")):
        return pd.Timestamp(item["purchase_date_fixed"])
    earliest = item.get("purchase_date_earliest")
    latest = item.get("purchase_date_latest")
    if pd.isna(earliest):
        earliest = config_start
    if pd.isna(latest):
        latest = earliest
    return pd.Timestamp(latest)


def _build_item_schedule(item: dict[str, Any]) -> list[tuple[pd.Timestamp, float]]:
    terms = None
    if item["chosen_source"] == "split" and item.get("split_terms"):
        terms = int(item["split_terms"])
    elif item["chosen_source"] == "installment" and item.get("installment_terms"):
        terms = int(item["installment_terms"])

    if not terms or terms <= 1:
        return [(item["deadline_date"], item["chosen_price"])]

    chunk = round(item["chosen_price"] / terms, 2)
    schedule: list[tuple[pd.Timestamp, float]] = []
    paid = 0.0
    for i in range(terms):
        due = pd.Timestamp(item["chosen_purchase_date"]) + pd.Timedelta(days=30 * (i + 1))
        amt = chunk if i < terms - 1 else round(item["chosen_price"] - paid, 2)
        paid += amt
        schedule.append((due, amt))
    return schedule


def _allocate_payment(
    obligations: list[dict[str, Any]], amount: float, policy: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if policy == "highest_rate":
        order = sorted(obligations, key=lambda x: (-x["apr"], x["deadline"]))
    elif policy == "highest_value":
        order = sorted(obligations, key=lambda x: (-x["value_score"], x["deadline"]))
    else:
        order = sorted(obligations, key=lambda x: (x["deadline"], x["created_at"]))

    allocations: list[dict[str, Any]] = []
    remaining = amount
    for ob in order:
        if remaining <= 0:
            break
        if ob["remaining"] <= 0:
            continue
        pay = min(ob["remaining"], remaining)
        ob["remaining"] -= pay
        remaining -= pay
        allocations.append({"item_id": ob["item_id"], "amount": round(pay, 2), "deadline": str(ob["deadline"].date())})
    return obligations, allocations


def run_simulation(fin: FinanceInputs) -> FinanceSimulationResult:
    start = pd.Timestamp(fin.config.start_date).normalize()
    horizon = int(fin.config.horizon_days)
    dates = pd.date_range(start=start, periods=horizon, freq="D")

    cards = fin.cards.set_index("card_id").to_dict("index")
    purchases: list[dict[str, Any]] = []
    obligations_by_card: dict[str, list[dict[str, Any]]] = defaultdict(list)
    schedule_by_date: dict[pd.Timestamp, list[dict[str, Any]]] = defaultdict(list)

    items_sorted = fin.items.sort_values(["priority", "value_score"], ascending=[True, False])
    for _, item in items_sorted.iterrows():
        chosen_date = _choose_purchase_date(item, start)
        chosen_price = _choose_price(item, fin.config.price_mode)
        chosen_source = _pick_card(item["allowed_sources_list"], fin.cards)
        grace = int(cards[chosen_source]["grace_days"]) if chosen_source in cards else 0
        deadline = item["item_deadline_override"] if pd.notna(item.get("item_deadline_override")) else chosen_date + pd.Timedelta(days=grace)

        purchase = {
            "item_id": item["item_id"],
            "chosen_purchase_date": chosen_date,
            "chosen_source": chosen_source,
            "chosen_price": chosen_price,
            "deadline_date": pd.Timestamp(deadline),
            "flags": "optimized_date" if item["purchase_date_mode"] == "optimize" else "fixed_date",
            "value_score": float(item["value_score"]),
            "split_terms": item.get("split_terms"),
            "installment_terms": item.get("installment_terms"),
        }
        purchases.append(purchase)

        if chosen_source.startswith("card"):
            parts = _build_item_schedule(purchase)
            for due_date, due_amount in parts:
                obligations_by_card[chosen_source].append(
                    {
                        "item_id": item["item_id"],
                        "remaining": float(due_amount),
                        "deadline": pd.Timestamp(due_date),
                        "created_at": chosen_date,
                        "apr": float(cards[chosen_source]["apr_outside_grace"]),
                        "value_score": float(item["value_score"]),
                    }
                )
            schedule_by_date[chosen_date].append(
                {"kind": "purchase", "source": chosen_source, "item_id": item["item_id"], "amount": chosen_price}
            )

    budget = fin.budget_daily.groupby(fin.budget_daily["date"].dt.normalize()).agg(
        amount_in=("amount_in", "sum"), amount_out_fixed=("amount_out_fixed", "sum")
    )
    manual = pd.DataFrame()
    if not fin.manual_payments.empty:
        manual = fin.manual_payments.copy()
        manual["date"] = manual["date"].dt.normalize()

    card_balances = {cid: 0.0 for cid in cards}
    cash_balance = 0.0

    payments_rows: list[dict[str, Any]] = []
    item_balance_rows: list[dict[str, Any]] = []
    card_balance_rows: list[dict[str, Any]] = []
    kpi_rows: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []

    for dt_day in dates:
        day = dt_day.normalize()
        b = budget.loc[day] if day in budget.index else {"amount_in": 0.0, "amount_out_fixed": 0.0}
        cash_balance += float(b["amount_in"]) - float(b["amount_out_fixed"])

        for event in schedule_by_date.get(day, []):
            card_balances[event["source"]] += float(event["amount"])

        # обязательные платежи по дедлайнам
        for card_id, obs in obligations_by_card.items():
            due_today = sum(ob["remaining"] for ob in obs if ob["deadline"] <= day and ob["remaining"] > 0)
            min_pay = card_balances[card_id] * float(cards[card_id]["min_payment_rule"])
            target_payment = max(due_today, min_pay)
            pay = min(target_payment, cash_balance) if fin.config.allow_pay_ahead else min(due_today, cash_balance)
            if pay > 0:
                obligations_by_card[card_id], alloc = _allocate_payment(obs, round(pay, 2), fin.config.allocation_policy)
                card_balances[card_id] = round(max(card_balances[card_id] - pay, 0.0), 2)
                cash_balance = round(cash_balance - pay, 2)
                payments_rows.append(
                    {
                        "date": day,
                        "source_account": "cash",
                        "target": card_id,
                        "amount": round(pay, 2),
                        "allocation_json_or_columns": str(alloc),
                    }
                )

        if not manual.empty:
            for _, row in manual[manual["date"] == day].iterrows():
                card_id = row["target_card"]
                pay = float(row["amount"])
                obligations_by_card[card_id], alloc = _allocate_payment(
                    obligations_by_card[card_id], pay, fin.config.allocation_policy
                )
                card_balances[card_id] = round(max(card_balances[card_id] - pay, 0.0), 2)
                cash_balance = round(cash_balance - pay, 2)
                payments_rows.append(
                    {
                        "date": day,
                        "source_account": row.get("source_account", "cash"),
                        "target": card_id,
                        "amount": pay,
                        "allocation_json_or_columns": str(alloc),
                    }
                )

        for card_id, bal in card_balances.items():
            limit = float(cards[card_id]["credit_limit"])
            if bal > limit:
                violations.append(
                    {
                        "date": day,
                        "violation_type": "card_limit",
                        "details": f"{card_id} balance {bal} exceeds {limit}",
                    }
                )
            overdue = [ob for ob in obligations_by_card[card_id] if ob["remaining"] > 0 and ob["deadline"] < day]
            if overdue:
                violations.append(
                    {
                        "date": day,
                        "violation_type": "overdue",
                        "details": f"{card_id} overdue items: {','.join(sorted({x['item_id'] for x in overdue}))}",
                    }
                )

            next_deadline = min((ob["deadline"] for ob in obligations_by_card[card_id] if ob["remaining"] > 0), default=pd.NaT)
            card_balance_rows.append(
                {
                    "date": day,
                    "card_id": card_id,
                    "balance": round(bal, 2),
                    "available_limit": round(limit - bal, 2),
                    "in_grace_bool": bool(pd.notna(next_deadline) and day <= next_deadline),
                    "next_deadline": next_deadline,
                }
            )

        for purchase in purchases:
            card_id = purchase["chosen_source"]
            relevant = [
                ob
                for ob in obligations_by_card.get(card_id, [])
                if ob["item_id"] == purchase["item_id"]
            ]
            remain = round(sum(ob["remaining"] for ob in relevant), 2)
            status = "paid" if remain <= 0 else ("overdue" if day > purchase["deadline_date"] else "open")
            item_balance_rows.append(
                {
                    "date": day,
                    "item_id": purchase["item_id"],
                    "remaining_balance": remain,
                    "deadline_date": purchase["deadline_date"],
                    "status": status,
                }
            )

        kpi_rows.extend(
            [
                {"date": day, "kpi_name": "cash_balance", "value": round(cash_balance, 2)},
                {"date": day, "kpi_name": "total_card_debt", "value": round(sum(card_balances.values()), 2)},
                {"date": day, "kpi_name": "violations_count", "value": len([v for v in violations if v['date'] == day])},
            ]
        )

    purchases_df = pd.DataFrame(purchases)
    payments_df = pd.DataFrame(payments_rows)
    item_bal_df = pd.DataFrame(item_balance_rows)
    card_bal_df = pd.DataFrame(card_balance_rows)
    kpi_df = pd.DataFrame(kpi_rows)
    violations_df = pd.DataFrame(violations)

    for frame, cols in [
        (purchases_df, ["chosen_purchase_date", "deadline_date"]),
        (payments_df, ["date"]),
        (item_bal_df, ["date", "deadline_date"]),
        (card_bal_df, ["date", "next_deadline"]),
        (kpi_df, ["date"]),
        (violations_df, ["date"]),
    ]:
        for col in cols:
            if col in frame.columns:
                frame[col] = pd.to_datetime(frame[col], errors="coerce")

    return FinanceSimulationResult(
        purchases_plan=purchases_df,
        payments_plan_daily=payments_df,
        item_balance_daily=item_bal_df,
        card_balance_daily=card_bal_df,
        kpi_daily=kpi_df,
        violations=violations_df,
    )
