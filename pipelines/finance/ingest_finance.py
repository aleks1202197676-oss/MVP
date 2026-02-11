from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd
import yaml
from pydantic import BaseModel, Field, field_validator


class FinanceConfig(BaseModel):
    horizon_days: int = Field(gt=0)
    start_date: str
    time_step: Literal["day"]
    allocation_policy: Literal["fifo_deadline", "highest_rate", "highest_value"]
    allow_pay_ahead: bool
    objective_mode: dict
    price_mode: Literal["fixed", "range", "optimize_under_constraints"]

    @field_validator("start_date", mode="before")
    @classmethod
    def validate_date(cls, value: str) -> str:
        parsed = pd.Timestamp(value)
        return parsed.strftime("%Y-%m-%d")


@dataclass
class FinanceInputs:
    config: FinanceConfig
    cards: pd.DataFrame
    items: pd.DataFrame
    budget_daily: pd.DataFrame
    manual_payments: pd.DataFrame


def _load_csv(path: Path, required: bool = True) -> pd.DataFrame:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Missing required input: {path}")
        return pd.DataFrame()
    return pd.read_csv(path)


def _normalize_items(items: pd.DataFrame) -> pd.DataFrame:
    date_cols = [
        "purchase_date_fixed",
        "purchase_date_earliest",
        "purchase_date_latest",
        "item_deadline_override",
    ]
    for col in date_cols:
        if col in items.columns:
            items[col] = pd.to_datetime(items[col], errors="coerce")

    bool_cols = ["split_allowed", "installment_allowed"]
    for col in bool_cols:
        if col in items.columns:
            items[col] = items[col].fillna(False).astype(bool)

    items["split_terms"] = pd.to_numeric(items.get("split_terms"), errors="coerce")
    items["installment_terms"] = pd.to_numeric(items.get("installment_terms"), errors="coerce")
    items["allowed_sources_list"] = items["allowed_sources"].fillna("").apply(
        lambda x: [token.strip() for token in str(x).split(",") if token.strip()]
    )
    return items


def _validate_frames(cards: pd.DataFrame, items: pd.DataFrame, budget_daily: pd.DataFrame) -> None:
    required_cards = {
        "card_id",
        "credit_limit",
        "grace_days",
        "apr_outside_grace",
        "min_payment_rule",
    }
    required_items = {
        "item_id",
        "name",
        "price_value",
        "price_min",
        "price_max",
        "value_score",
        "priority",
        "allowed_sources",
        "purchase_date_mode",
        "purchase_date_earliest",
        "purchase_date_latest",
    }
    required_budget = {"date", "amount_in"}

    for name, frame, required in [
        ("cards", cards, required_cards),
        ("items", items, required_items),
        ("budget_daily", budget_daily, required_budget),
    ]:
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"{name}: missing columns {sorted(missing)}")


def read_finance_inputs(
    config_path: str = "config/finance_config.yml", data_root: str = "data/raw/finance"
) -> FinanceInputs:
    with open(config_path, "r", encoding="utf-8") as f:
        config = FinanceConfig(**yaml.safe_load(f))

    root = Path(data_root)
    cards = _load_csv(root / "cards.csv")
    items = _normalize_items(_load_csv(root / "items.csv"))
    budget_daily = _load_csv(root / "budget_daily.csv")
    manual_payments = _load_csv(root / "manual_payments.csv", required=False)

    cards["credit_limit"] = pd.to_numeric(cards["credit_limit"], errors="coerce")
    cards["grace_days"] = pd.to_numeric(cards["grace_days"], errors="coerce").astype(int)
    cards["apr_outside_grace"] = pd.to_numeric(cards["apr_outside_grace"], errors="coerce")
    cards["min_payment_rule"] = pd.to_numeric(cards["min_payment_rule"], errors="coerce")

    budget_daily["date"] = pd.to_datetime(budget_daily["date"], errors="coerce")
    budget_daily["amount_in"] = pd.to_numeric(budget_daily["amount_in"], errors="coerce").fillna(0.0)
    budget_daily["amount_out_fixed"] = pd.to_numeric(
        budget_daily.get("amount_out_fixed"), errors="coerce"
    ).fillna(0.0)

    if not manual_payments.empty:
        manual_payments["date"] = pd.to_datetime(manual_payments["date"], errors="coerce")
        manual_payments["amount"] = pd.to_numeric(manual_payments["amount"], errors="coerce")

    _validate_frames(cards, items, budget_daily)
    return FinanceInputs(
        config=config,
        cards=cards,
        items=items,
        budget_daily=budget_daily,
        manual_payments=manual_payments,
    )
