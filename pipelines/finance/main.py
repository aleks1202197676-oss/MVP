from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from .io import format_money, read_cards, read_finance_config, read_items, write_csv, write_summary
from .model import FinanceResult, assign_items


def _cashflow_rows(start_date: str, total_spend: Decimal, horizon_days: int) -> list[dict[str, str]]:
    start = date.fromisoformat(start_date)
    rows: list[dict[str, str]] = []
    for offset in range(max(horizon_days, 1)):
        current = start + timedelta(days=offset)
        outflow = total_spend if offset == 0 else Decimal("0.00")
        cumulative = total_spend
        rows.append(
            {
                "date": current.isoformat(),
                "total_outflow": format_money(outflow),
                "cumulative_debt": format_money(cumulative),
            }
        )
    return rows


def _write_report(path: Path, result: FinanceResult) -> None:
    lines = [
        "# Finance MVP Report",
        "",
        f"- Total spend: {format_money(result.total_spend)}",
        f"- Unpurchasable items: {result.unpurchasable_count}",
        f"- Max card utilization: {result.max_card_utilization:.4f}",
        "",
        "## Constraint violations",
    ]
    if not result.violations:
        lines.append("- None")
    else:
        for violation in result.violations:
            lines.append(f"- {violation.date}: {violation.violation_type} ({violation.details})")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_finance_pipeline(output_dir: str = "data/outputs/latest/finance") -> dict[str, str]:
    config = read_finance_config("inputs/finance/config.yml")
    items = read_items("inputs/finance/items.csv")
    cards = read_cards("inputs/finance/cards.csv")

    result = assign_items(config=config, items=items, cards=cards)

    output_root = Path(output_dir)
    payment_schedule_path = output_root / "payment_schedule.csv"
    cashflow_path = output_root / "cashflow_daily.csv"
    summary_path = output_root / "summary_metrics.json"
    violations_path = output_root / "constraint_violations.csv"
    report_path = output_root / "report.md"

    payment_rows = [
        {
            "date": assignment.date,
            "amount": format_money(assignment.amount),
            "source": assignment.source,
            "card_id": assignment.card_id,
            "item_id": assignment.item_id,
        }
        for assignment in result.assignments
    ]
    write_csv(
        payment_schedule_path,
        fieldnames=["date", "amount", "source", "card_id", "item_id"],
        rows=payment_rows,
    )

    write_csv(
        cashflow_path,
        fieldnames=["date", "total_outflow", "cumulative_debt"],
        rows=_cashflow_rows(config.start_date, result.total_spend, config.horizon_days),
    )

    summary_payload = {
        "max_card_utilization": f"{result.max_card_utilization:.6f}",
        "total_spend": format_money(result.total_spend),
        "unpurchasable_count": result.unpurchasable_count,
    }
    write_summary(summary_path, summary_payload)

    violation_rows = [
        {"date": v.date, "violation_type": v.violation_type, "details": v.details}
        for v in result.violations
    ]
    write_csv(
        violations_path,
        fieldnames=["date", "violation_type", "details"],
        rows=violation_rows,
    )

    _write_report(report_path, result)

    return {
        "payment_schedule": str(payment_schedule_path),
        "cashflow_daily": str(cashflow_path),
        "summary_metrics": str(summary_path),
        "constraint_violations": str(violations_path),
        "report": str(report_path),
    }
