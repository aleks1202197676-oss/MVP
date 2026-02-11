from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class FinanceCandidate:
    purchase_date: date
    projected_pnl: float
    projected_risk: float
    projected_final_value: float


def _parse_date(raw_value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise ValueError(f"finance.{field_name} must be ISO date YYYY-MM-DD, got: {raw_value!r}") from exc


def _date_range(start_date: date, end_date: date) -> list[date]:
    if end_date < start_date:
        raise ValueError("finance.purchase_window.end_date must be >= start_date")

    total_days = (end_date - start_date).days
    return [start_date + timedelta(days=offset) for offset in range(total_days + 1)]


def _simulate_candidate(purchase_date: date, params: dict) -> FinanceCandidate:
    investment_amount = float(params.get("investment_amount", 100_000))
    holding_days = int(params.get("holding_days", 30))
    expected_daily_return = float(params.get("expected_daily_return", 0.0007))
    daily_volatility = float(params.get("daily_volatility", 0.01))

    weekday_adjustments = params.get("weekday_adjustments", {})
    monthly_adjustments = params.get("monthly_adjustments", {})

    weekday_key = str(purchase_date.weekday())
    month_key = str(purchase_date.month)

    weekday_alpha = float(weekday_adjustments.get(weekday_key, 0.0))
    month_alpha = float(monthly_adjustments.get(month_key, 0.0))

    adjusted_daily_return = expected_daily_return + weekday_alpha + month_alpha
    growth_factor = (1 + adjusted_daily_return) ** holding_days
    projected_final_value = investment_amount * growth_factor
    projected_pnl = projected_final_value - investment_amount

    # Простая прокси-оценка риска: чем выше волатильность и дольше горизонт, тем выше риск.
    projected_risk = investment_amount * daily_volatility * (holding_days**0.5)

    return FinanceCandidate(
        purchase_date=purchase_date,
        projected_pnl=projected_pnl,
        projected_risk=projected_risk,
        projected_final_value=projected_final_value,
    )


def _goal_level_non_negative(candidates: list[FinanceCandidate]) -> list[FinanceCandidate]:
    non_negative = [candidate for candidate in candidates if candidate.projected_pnl >= 0]
    if non_negative:
        return non_negative

    # Если безубыточных дат нет, минимизируем абсолютный убыток.
    min_loss = min(candidates, key=lambda candidate: abs(candidate.projected_pnl)).projected_pnl
    return [candidate for candidate in candidates if candidate.projected_pnl == min_loss]


def _goal_level_max_result(candidates: list[FinanceCandidate]) -> list[FinanceCandidate]:
    max_pnl = max(candidates, key=lambda candidate: candidate.projected_pnl).projected_pnl
    return [candidate for candidate in candidates if candidate.projected_pnl == max_pnl]


def _resolve_goal_levels(candidates: list[FinanceCandidate]) -> tuple[FinanceCandidate, list[dict]]:
    levels: list[tuple[str, Callable[[list[FinanceCandidate]], list[FinanceCandidate]], str]] = [
        (
            "Уровень 1",
            _goal_level_non_negative,
            "Отбираем даты с неотрицательным результатом; если таких нет — минимизируем убыток.",
        ),
        (
            "Уровень 2",
            _goal_level_max_result,
            "Среди дат, прошедших уровень 1, выбираем максимум результата.",
        ),
    ]

    current = list(candidates)
    details: list[dict] = []
    for level_name, selector, rationale in levels:
        before = len(current)
        current = selector(current)
        details.append(
            {
                "level": level_name,
                "rationale": rationale,
                "before": before,
                "after": len(current),
                "dates": [candidate.purchase_date.isoformat() for candidate in current],
            }
        )

    best = min(current, key=lambda candidate: candidate.purchase_date)
    return best, details


def _format_money(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ")


def _write_report(
    report_path: Path,
    best: FinanceCandidate,
    candidates: list[FinanceCandidate],
    goal_details: list[dict],
    run_at: datetime,
) -> None:
    lines: list[str] = []
    lines.append("# Finance report")
    lines.append("")
    lines.append(f"Сформирован: {run_at.isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("## Выбранная дата покупки")
    lines.append("")
    lines.append(
        f"Лучшая дата: **{best.purchase_date.isoformat()}**. "
        f"Причина: дата прошла все уровни целей и дала итоговый результат "
        f"`{_format_money(best.projected_pnl)}` при риске `{_format_money(best.projected_risk)}`."
    )
    lines.append("")
    lines.append("## Результаты по уровням целей")
    lines.append("")
    for detail in goal_details:
        lines.append(f"- **{detail['level']}**: {detail['rationale']}")
        lines.append(
            f"  - Кандидатов до/после: {detail['before']} → {detail['after']}; "
            f"даты: {', '.join(detail['dates'])}"
        )
    lines.append("")
    lines.append("## Сравнение дат")
    lines.append("")
    lines.append("| Дата покупки | Итоговая стоимость | Результат (PnL) | Риск |")
    lines.append("|---|---:|---:|---:|")
    for candidate in sorted(candidates, key=lambda item: item.purchase_date):
        lines.append(
            "| "
            f"{candidate.purchase_date.isoformat()} | "
            f"{_format_money(candidate.projected_final_value)} | "
            f"{_format_money(candidate.projected_pnl)} | "
            f"{_format_money(candidate.projected_risk)} |"
        )
    lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_finance_pipeline(cfg: dict, run_id: str) -> Path:
    finance_cfg = cfg.get("pipelines", {}).get("finance", {})
    purchase_window = finance_cfg.get("purchase_window", {})

    start = _parse_date(purchase_window.get("start_date", date.today().isoformat()), "purchase_window.start_date")
    end = _parse_date(purchase_window.get("end_date", start.isoformat()), "purchase_window.end_date")

    params = finance_cfg.get("model", {})
    dates = _date_range(start, end)
    candidates = [_simulate_candidate(purchase_date=dt, params=params) for dt in dates]

    best, details = _resolve_goal_levels(candidates)

    latest_folder = Path(finance_cfg.get("outputs", {}).get("latest_folder", "data/outputs/latest/finance"))
    report_path = latest_folder / "report.md"
    _write_report(report_path=report_path, best=best, candidates=candidates, goal_details=details, run_at=datetime.utcnow())

    run_folder = Path(cfg.get("hub", {}).get("output_root", "data/outputs")) / run_id / "finance"
    run_folder.mkdir(parents=True, exist_ok=True)
    run_report_path = run_folder / "report.md"
    run_report_path.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")

    return report_path
