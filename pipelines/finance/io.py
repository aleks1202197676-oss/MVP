from __future__ import annotations

import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import yaml

from .model import Card, FinanceConfig, Item


def _money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"


def read_finance_config(path: str) -> FinanceConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return FinanceConfig(
        start_date=str(raw.get("start_date", "1970-01-01")),
        horizon_days=int(raw.get("horizon_days", 0)),
        strategy=str(raw.get("strategy", "priority_first")),
    )


def read_items(path: str) -> list[Item]:
    items: list[Item] = []
    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            items.append(
                Item(
                    item_id=str(row["item_id"]),
                    title=str(row["title"]),
                    cost=Decimal(str(row["cost"])),
                    priority=int(row["priority"]),
                )
            )
    return sorted(items, key=lambda i: i.item_id)


def read_cards(path: str) -> list[Card]:
    cards: list[Card] = []
    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            cards.append(Card(card_id=str(row["card_id"]), limit=Decimal(str(row["limit"]))))
    return sorted(cards, key=lambda c: c.card_id)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered_rows = sorted(rows, key=lambda row: tuple(str(row.get(k, "")) for k in fieldnames))
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in ordered_rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def write_summary(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def format_money(value: Decimal) -> str:
    return _money(value)
