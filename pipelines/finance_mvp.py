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


def _validate_item_card_ids(items: list[PurchaseItem], cards: dict[str, Card]) -> None:
    missing_card_ids = sorted({item.card_id for item in items if item.card_id not in cards})
    if missing_card_ids:
        raise ValueError(f"finance_mvp/items.csv has unknown card_id values: {missing_card_ids}")


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


def _build_flying_logic_rows(
    cards: dict[str, Card],
    items: list[PurchaseItem],
    monthly_rows: list[dict[str, str]],
    kpi_rows: list[dict[str, str]],
    budget: dict[str, BudgetMonth],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    card_paid: dict[str, float] = {}
    card_interest: dict[str, float] = {}
    for row in monthly_rows:
        card_id = row["card_id"]
        statement_balance = float(row["statement_balance"])
        planned_payment = float(row["planned_payment"])
        card_paid[card_id] = card_paid.get(card_id, 0.0) + planned_payment
        monthly_interest = statement_balance * (cards[card_id].apr / 12.0)
        card_interest[card_id] = card_interest.get(card_id, 0.0) + monthly_interest

    total_paid = sum(card_paid.values())
    total_interest = sum(card_interest.values())
    items_purchased = len(items)
    available_budget = sum(
        max(0.0, month.income - month.fixed_expenses - month.target_savings) for _, month in sorted(budget.items())
    )

    nodes: list[dict[str, str]] = []
    for card_id in sorted(cards.keys()):
        card = cards[card_id]
        nodes.append(
            {
                "node_id": f"card:{card_id}",
                "label": card_id,
                "type": "card",
                "group": "cards",
                "weight": f"{card.credit_limit:.2f}",
                "note": f"apr={card.apr:.4f};min_payment_rate={card.min_payment_rate:.4f}",
            }
        )

    for index, item in enumerate(items, start=1):
        nodes.append(
            {
                "node_id": f"item:{index:04d}",
                "label": f"{item.category}:{item.purchase_date.isoformat()}",
                "type": "item",
                "group": "items",
                "weight": f"{item.amount:.2f}",
                "note": f"card_id={item.card_id};priority={item.priority}",
            }
        )

    for month_row in sorted(kpi_rows, key=lambda row: row["month"]):
        month = month_row["month"]
        nodes.append(
            {
                "node_id": f"kpi:ending_debt:{month}",
                "label": f"ending_debt_{month}",
                "type": "kpi",
                "group": "kpi_timeseries",
                "weight": f"{float(month_row['ending_debt']):.2f}",
                "note": "monthly ending debt",
            }
        )

    nodes.extend(
        [
            {
                "node_id": "kpi:items_purchased",
                "label": "items_purchased",
                "type": "kpi",
                "group": "kpi_summary",
                "weight": str(items_purchased),
                "note": "count of purchase items",
            },
            {
                "node_id": "kpi:total_paid",
                "label": "total_paid",
                "type": "kpi",
                "group": "kpi_summary",
                "weight": f"{total_paid:.2f}",
                "note": "sum(planned_payment)",
            },
            {
                "node_id": "kpi:total_interest",
                "label": "total_interest",
                "type": "kpi",
                "group": "kpi_summary",
                "weight": f"{total_interest:.2f}",
                "note": "sum(statement_balance * apr/12)",
            },
            {
                "node_id": "kpi:available_budget",
                "label": "available_budget",
                "type": "kpi",
                "group": "kpi_summary",
                "weight": f"{available_budget:.2f}",
                "note": "sum(max(0, income-fixed_expenses-target_savings))",
            },
        ]
    )
    nodes = sorted(nodes, key=lambda row: row["node_id"])

    edges: list[dict[str, str]] = []
    for index, item in enumerate(items, start=1):
        edges.append(
            {
                "from_id": f"item:{index:04d}",
                "to_id": f"card:{item.card_id}",
                "relation": "funded_by",
                "weight": f"{item.amount:.2f}",
                "note": f"purchase_date={item.purchase_date.isoformat()}",
            }
        )
        edges.append(
            {
                "from_id": f"item:{index:04d}",
                "to_id": "kpi:items_purchased",
                "relation": "contributes_to",
                "weight": "1.00",
                "note": "one purchased item",
            }
        )

    for card_id in sorted(cards.keys()):
        edges.append(
            {
                "from_id": f"card:{card_id}",
                "to_id": "kpi:total_paid",
                "relation": "contributes_to",
                "weight": f"{card_paid.get(card_id, 0.0):.2f}",
                "note": "sum planned payment for card",
            }
        )
        edges.append(
            {
                "from_id": f"card:{card_id}",
                "to_id": "kpi:total_interest",
                "relation": "contributes_to",
                "weight": f"{card_interest.get(card_id, 0.0):.2f}",
                "note": "estimated monthly interest contribution",
            }
        )

    edges.append(
        {
            "from_id": "kpi:available_budget",
            "to_id": "kpi:total_paid",
            "relation": "constrained_by",
            "weight": f"{available_budget:.2f}",
            "note": "payments limited by available budget",
        }
    )

    for month_row in sorted(kpi_rows, key=lambda row: row["month"]):
        month = month_row["month"]
        edges.append(
            {
                "from_id": "kpi:total_interest",
                "to_id": f"kpi:ending_debt:{month}",
                "relation": "contributes_to",
                "weight": f"{float(month_row['ending_debt']):.2f}",
                "note": "ending debt level for month",
            }
        )

    edges = sorted(edges, key=lambda row: (row["from_id"], row["to_id"], row["relation"], row["note"]))
    return nodes, edges


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
    _validate_item_card_ids(items=items, cards=cards)
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

    flying_nodes, flying_edges = _build_flying_logic_rows(
        cards=cards,
        items=items,
        monthly_rows=monthly_rows,
        kpi_rows=kpi_rows,
        budget=budget,
    )
    _write_csv(
        output_root / "flying_logic" / "nodes.csv",
        ["node_id", "label", "type", "group", "weight", "note"],
        flying_nodes,
    )
    _write_csv(
        output_root / "flying_logic" / "edges.csv",
        ["from_id", "to_id", "relation", "weight", "note"],
        flying_edges,
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
