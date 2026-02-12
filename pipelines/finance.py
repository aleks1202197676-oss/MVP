from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


@dataclass(frozen=True)
class Card:
    card_id: str
    statement_day: int
    apr: float
    min_payment_rate: float


@dataclass(frozen=True)
class Item:
    item_id: str
    card_id: str
    purchase_date: date
    amount: float
    category: str


@dataclass(frozen=True)
class PlannedPayment:
    payment_date: date
    budget_month: str
    card_id: str
    item_id: str
    purchase_date: date
    due_date: date
    amount: float
    required_payment: float
    paid_payment: float
    unfunded_payment: float


def _parse_date(raw_value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise ValueError(f"finance.{field_name} must be ISO date YYYY-MM-DD, got: {raw_value!r}") from exc


def _read_cards(path: Path) -> dict[str, Card]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        cards: dict[str, Card] = {}
        for row in reader:
            card = Card(
                card_id=str(row["card_id"]).strip(),
                statement_day=int(row["statement_day"]),
                apr=float(row["apr"]),
                min_payment_rate=float(row["min_payment_rate"]),
            )
            cards[card.card_id] = card
    return cards


def _read_items(path: Path) -> list[Item]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        items = [
            Item(
                item_id=str(row["item_id"]).strip(),
                card_id=str(row["card_id"]).strip(),
                purchase_date=_parse_date(str(row["purchase_date"]).strip(), "raw.items.purchase_date"),
                amount=float(row["amount"]),
                category=str(row.get("category", "")).strip(),
            )
            for row in reader
        ]
    return sorted(items, key=lambda item: (item.purchase_date, item.card_id, item.item_id))


def _read_budget(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        budget = {str(row["month"]).strip(): float(row["payment_budget"]) for row in reader}
    return dict(sorted(budget.items(), key=lambda item: item[0]))


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _to_money(value: float) -> str:
    return f"{value:.2f}"


def _build_payment_plan(cards: dict[str, Card], items: list[Item], budget_by_month: dict[str, float]) -> list[PlannedPayment]:
    remaining_budget = dict(budget_by_month)
    plan: list[PlannedPayment] = []

    for item in items:
        card = cards.get(item.card_id)
        if card is None:
            raise ValueError(f"Unknown card_id in items.csv: {item.card_id!r}")

        due_date = item.purchase_date + timedelta(days=25)
        budget_month = due_date.strftime("%Y-%m")
        required_payment = round(item.amount * (card.min_payment_rate / 100.0), 2)

        month_left = remaining_budget.get(budget_month, 0.0)
        paid_payment = round(min(required_payment, month_left), 2)
        remaining_budget[budget_month] = round(month_left - paid_payment, 2)
        unfunded_payment = round(required_payment - paid_payment, 2)

        plan.append(
            PlannedPayment(
                payment_date=due_date,
                budget_month=budget_month,
                card_id=item.card_id,
                item_id=item.item_id,
                purchase_date=item.purchase_date,
                due_date=due_date,
                amount=item.amount,
                required_payment=required_payment,
                paid_payment=paid_payment,
                unfunded_payment=unfunded_payment,
            )
        )

    return sorted(plan, key=lambda row: (row.payment_date, row.card_id, row.item_id))


def _write_outputs(latest_folder: Path, plan: list[PlannedPayment]) -> Path:
    daily_rows: list[dict[str, str]] = []
    monthly_rows: list[dict[str, str]] = []

    daily_acc: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    monthly_acc: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for row in plan:
        payment_day = row.payment_date.isoformat()
        daily_acc[payment_day]["required"] += row.required_payment
        daily_acc[payment_day]["paid"] += row.paid_payment
        daily_acc[payment_day]["unfunded"] += row.unfunded_payment
        daily_acc[payment_day]["count"] += 1

        month = row.budget_month
        monthly_acc[month]["required"] += row.required_payment
        monthly_acc[month]["paid"] += row.paid_payment
        monthly_acc[month]["unfunded"] += row.unfunded_payment
        monthly_acc[month]["count"] += 1

    for payment_date in sorted(daily_acc.keys()):
        values = daily_acc[payment_date]
        daily_rows.append(
            {
                "payment_date": payment_date,
                "purchase_count": str(int(values["count"])),
                "required_payment": _to_money(values["required"]),
                "paid_payment": _to_money(values["paid"]),
                "unfunded_payment": _to_money(values["unfunded"]),
            }
        )

    for month in sorted(monthly_acc.keys()):
        values = monthly_acc[month]
        monthly_rows.append(
            {
                "month": month,
                "purchase_count": str(int(values["count"])),
                "required_payment": _to_money(values["required"]),
                "paid_payment": _to_money(values["paid"]),
                "unfunded_payment": _to_money(values["unfunded"]),
            }
        )

    plan_rows = [
        {
            "payment_date": row.payment_date.isoformat(),
            "budget_month": row.budget_month,
            "card_id": row.card_id,
            "item_id": row.item_id,
            "purchase_date": row.purchase_date.isoformat(),
            "due_date": row.due_date.isoformat(),
            "amount": _to_money(row.amount),
            "required_payment": _to_money(row.required_payment),
            "paid_payment": _to_money(row.paid_payment),
            "unfunded_payment": _to_money(row.unfunded_payment),
        }
        for row in plan
    ]

    _write_csv(
        latest_folder / "payments_daily.csv",
        ["payment_date", "purchase_count", "required_payment", "paid_payment", "unfunded_payment"],
        daily_rows,
    )
    _write_csv(
        latest_folder / "payments_monthly.csv",
        ["month", "purchase_count", "required_payment", "paid_payment", "unfunded_payment"],
        monthly_rows,
    )
    _write_csv(
        latest_folder / "purchase_plan.csv",
        [
            "payment_date",
            "budget_month",
            "card_id",
            "item_id",
            "purchase_date",
            "due_date",
            "amount",
            "required_payment",
            "paid_payment",
            "unfunded_payment",
        ],
        plan_rows,
    )

    required_total = sum(row.required_payment for row in plan)
    paid_total = sum(row.paid_payment for row in plan)
    unfunded_total = sum(row.unfunded_payment for row in plan)

    lines = [
        "# Finance report",
        "",
        "## Assumptions",
        "- Input root: `data/raw/finance/`.",
        "- Due date = purchase_date + 25 days.",
        "- Required payment = amount * min_payment_rate / 100.",
        "- Monthly budget is allocated in deterministic sorted order: date, card_id, item_id.",
        "",
        "## KPI",
        f"- Purchases in plan: **{len(plan)}**.",
        f"- Total required payment: **{_to_money(required_total)}**.",
        f"- Total paid payment: **{_to_money(paid_total)}**.",
        f"- Total unfunded payment: **{_to_money(unfunded_total)}**.",
    ]

    report_path = latest_folder / "report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def run_finance_pipeline(cfg: dict, run_id: str) -> Path:
    finance_cfg = cfg.get("pipelines", {}).get("finance", {})
    raw_root = Path(finance_cfg.get("inputs", {}).get("raw_root", "data/raw/finance"))

    cards = _read_cards(raw_root / "cards.csv")
    items = _read_items(raw_root / "items.csv")
    budget_by_month = _read_budget(raw_root / "budget.csv")

    plan = _build_payment_plan(cards=cards, items=items, budget_by_month=budget_by_month)

    latest_folder = Path(finance_cfg.get("outputs", {}).get("latest_folder", "data/outputs/latest/finance"))
    report_path = _write_outputs(latest_folder=latest_folder, plan=plan)

    run_folder = Path(cfg.get("hub", {}).get("output_root", "data/outputs")) / run_id / "finance"
    run_folder.mkdir(parents=True, exist_ok=True)

    for filename in ["payments_daily.csv", "payments_monthly.csv", "purchase_plan.csv", "report.md"]:
        source = latest_folder / filename
        (run_folder / filename).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    return report_path
