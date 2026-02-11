from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipelines.finance.simulate_finance import FinanceSimulationResult


def _monthly_agg(df: pd.DataFrame, date_col: str, group_cols: list[str], value_col: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["month", *group_cols, value_col])
    out = df.copy()
    out["month"] = pd.to_datetime(out[date_col]).dt.to_period("M").dt.to_timestamp()
    return out.groupby(["month", *group_cols], as_index=False)[value_col].sum()


def _build_report(result: FinanceSimulationResult) -> str:
    purchases_lines = ["## Покупки"]
    if result.purchases_plan.empty:
        purchases_lines.append("- Нет покупок")
    else:
        for _, row in result.purchases_plan.iterrows():
            purchases_lines.append(
                f"- {row['item_id']}: {row['chosen_purchase_date'].date()} через {row['chosen_source']} "
                f"на {row['chosen_price']:.2f}, дедлайн {row['deadline_date'].date()}"
            )

    payments_lines = ["## Платежи"]
    if result.payments_plan_daily.empty:
        payments_lines.append("- Нет платежей")
    else:
        grouped = result.payments_plan_daily.groupby("date", as_index=False)["amount"].sum()
        for _, row in grouped.iterrows():
            payments_lines.append(f"- {row['date'].date()}: {row['amount']:.2f}")

    warn_lines = ["## Предупреждения"]
    if result.violations.empty:
        warn_lines.append("- Нарушений не обнаружено")
    else:
        for _, row in result.violations.drop_duplicates().iterrows():
            warn_lines.append(f"- {row['date'].date()}: {row['violation_type']} -> {row['details']}")

    return "\n".join(["# Finance MVP report", *purchases_lines, *payments_lines, *warn_lines])


def export_finance_outputs(result: FinanceSimulationResult, out_dir: str = "data/outputs/latest/finance") -> list[str]:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)

    result.purchases_plan.to_csv(output / "purchases_plan.csv", index=False)
    result.payments_plan_daily.to_csv(output / "payments_plan_daily.csv", index=False)
    result.item_balance_daily.to_csv(output / "item_balance_daily.csv", index=False)
    result.card_balance_daily.to_csv(output / "card_balance_daily.csv", index=False)
    result.kpi_daily.to_csv(output / "kpi_daily.csv", index=False)
    result.violations.to_csv(output / "violations.csv", index=False)

    payments_monthly = _monthly_agg(result.payments_plan_daily, "date", ["target"], "amount")
    payments_monthly.to_csv(output / "payments_monthly.csv", index=False)

    kpi_monthly = _monthly_agg(result.kpi_daily, "date", ["kpi_name"], "value")
    kpi_monthly.to_csv(output / "kpi_monthly.csv", index=False)

    report = _build_report(result)
    (output / "report.md").write_text(report, encoding="utf-8")

    return [str(x) for x in sorted(output.glob("*"))]
