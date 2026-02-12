from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Card:
    card_id: str
    credit_limit: float
    apr: float
    min_payment_rate: float
    cycle_day: int
    due_day: int


@dataclass(frozen=True)
class PurchaseItem:
    purchase_date: date
    card_id: str
    category: str
    amount: float
    priority: str


@dataclass(frozen=True)
class BudgetMonth:
    month: str
    income: float
    fixed_expenses: float
    target_savings: float


REQUIRED_INPUTS = ("cards.csv", "items.csv", "budget.csv")


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _parse_cards(path: Path) -> dict[str, Card]:
    cards: dict[str, Card] = {}
    for row in _read_csv_rows(path):
        card = Card(
            card_id=row["card_id"],
            credit_limit=float(row["credit_limit"]),
            apr=float(row["apr"]),
            min_payment_rate=float(row["min_payment_rate"]),
            cycle_day=int(row["cycle_day"]),
            due_day=int(row["due_day"]),
        )
        cards[card.card_id] = card
    if not cards:
        raise ValueError("finance_mvp/cards.csv must contain at least one card")
    return cards


def _parse_items(path: Path) -> list[PurchaseItem]:
    items = [
        PurchaseItem(
            purchase_date=date.fromisoformat(row["purchase_date"]),
            card_id=row["card_id"],
            category=row["category"],
            amount=float(row["amount"]),
            priority=row.get("priority", "normal"),
        )
        for row in _read_csv_rows(path)
    ]
    if not items:
        raise ValueError("finance_mvp/items.csv must contain at least one purchase")
    return sorted(items, key=lambda item: (item.purchase_date, item.card_id, item.category))


def _parse_budget(path: Path) -> dict[str, BudgetMonth]:
    budget = {
        row["month"]: BudgetMonth(
            month=row["month"],
            income=float(row["income"]),
            fixed_expenses=float(row["fixed_expenses"]),
            target_savings=float(row["target_savings"]),
        )
        for row in _read_csv_rows(path)
    }
    if not budget:
        raise ValueError("finance_mvp/budget.csv must contain at least one month")
    return budget


def _write_csv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def _due_date_for_month(month: str, due_day: int) -> str:
    yyyy, mm = month.split("-")
    clamped_day = max(1, min(28, due_day))
    return f"{yyyy}-{mm}-{clamped_day:02d}"


def run_finance_mvp_pipeline(cfg: dict, run_id: str) -> Path:
    pipeline_cfg = cfg.get("pipelines", {}).get("finance_mvp", {})
    input_root = Path(pipeline_cfg.get("input_root", "data/raw/finance_mvp"))
    output_root = Path(pipeline_cfg.get("outputs", {}).get("latest_folder", "outputs/latest/finance_mvp"))

    missing = [name for name in REQUIRED_INPUTS if not (input_root / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing finance_mvp inputs under {input_root}: {missing}")

    cards = _parse_cards(input_root / "cards.csv")
    items = _parse_items(input_root / "items.csv")
    budget = _parse_budget(input_root / "budget.csv")

    monthly_by_card: dict[tuple[str, str], float] = {}
    for item in items:
        month = item.purchase_date.strftime("%Y-%m")
        monthly_by_card[(month, item.card_id)] = monthly_by_card.get((month, item.card_id), 0.0) + item.amount

    monthly_rows: list[dict[str, str]] = []
    daily_rows: list[dict[str, str]] = []
    kpi_by_month: dict[str, dict[str, float]] = {}

    for month, month_budget in sorted(budget.items()):
        available_for_debt = max(0.0, month_budget.income - month_budget.fixed_expenses - month_budget.target_savings)
        month_card_balances = [
            (card_id, monthly_by_card.get((month, card_id), 0.0)) for card_id in sorted(cards.keys())
        ]

        for card_id, statement_balance in month_card_balances:
            card = cards[card_id]
            min_payment = round(statement_balance * card.min_payment_rate, 2)
            planned_payment = round(min(statement_balance, max(min_payment, available_for_debt)), 2)
            ending_balance = round(statement_balance - planned_payment, 2)
            available_for_debt = round(max(0.0, available_for_debt - planned_payment), 2)

            monthly_rows.append(
                {
                    "month": month,
                    "card_id": card_id,
                    "statement_balance": f"{statement_balance:.2f}",
                    "min_payment": f"{min_payment:.2f}",
                    "planned_payment": f"{planned_payment:.2f}",
                    "ending_balance": f"{ending_balance:.2f}",
                }
            )
            daily_rows.append(
                {
                    "date": _due_date_for_month(month, card.due_day),
                    "card_id": card_id,
                    "payment_type": "statement_due",
                    "amount": f"{planned_payment:.2f}",
                }
            )

            bucket = kpi_by_month.setdefault(month, {"purchase_total": 0.0, "payment_total": 0.0, "ending_debt": 0.0})
            bucket["purchase_total"] += statement_balance
            bucket["payment_total"] += planned_payment
            bucket["ending_debt"] += ending_balance

    purchase_plan_rows = [
        {
            "purchase_date": item.purchase_date.isoformat(),
            "card_id": item.card_id,
            "category": item.category,
            "amount": f"{item.amount:.2f}",
            "priority": item.priority,
            "planned_payoff_month": item.purchase_date.strftime("%Y-%m"),
            "decision_reason": "baseline_mvp_rule",
        }
        for item in items
    ]

    kpi_rows = [
        {
            "month": month,
            "purchase_total": f"{vals['purchase_total']:.2f}",
            "payment_total": f"{vals['payment_total']:.2f}",
            "ending_debt": f"{vals['ending_debt']:.2f}",
            "utilization_ratio": f"{(vals['purchase_total'] / sum(card.credit_limit for card in cards.values())):.4f}",
        }
        for month, vals in sorted(kpi_by_month.items())
    ]

    _write_csv(
        output_root / "payments_daily.csv",
        ["date", "card_id", "payment_type", "amount"],
        daily_rows,
    )
    _write_csv(
        output_root / "payments_monthly.csv",
        ["month", "card_id", "statement_balance", "min_payment", "planned_payment", "ending_balance"],
        monthly_rows,
    )
    _write_csv(
        output_root / "purchase_plan.csv",
        ["purchase_date", "card_id", "category", "amount", "priority", "planned_payoff_month", "decision_reason"],
        purchase_plan_rows,
    )
    _write_csv(
        output_root / "kpi_timeseries.csv",
        ["month", "purchase_total", "payment_total", "ending_debt", "utilization_ratio"],
        kpi_rows,
    )

    total_purchase = sum(item.amount for item in items)
    total_payment = sum(float(row["planned_payment"]) for row in monthly_rows)
    final_debt = sum(float(row["ending_balance"]) for row in monthly_rows)

    report_path = output_root / "report.md"
    report_path.write_text(
        "\n".join(
            [
                "# Finance MVP report",
                "",
                f"- run_id: `{run_id}`",
                f"- input_root: `{input_root.as_posix()}`",
                f"- purchases_count: `{len(items)}`",
                f"- total_purchase: `{total_purchase:.2f}`",
                f"- total_planned_payment: `{total_payment:.2f}`",
                f"- ending_debt: `{final_debt:.2f}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return report_path
