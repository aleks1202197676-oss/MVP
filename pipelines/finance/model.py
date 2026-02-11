from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class FinanceConfig:
    start_date: str
    horizon_days: int
    strategy: str


@dataclass(frozen=True)
class Item:
    item_id: str
    title: str
    cost: Decimal
    priority: int


@dataclass(frozen=True)
class Card:
    card_id: str
    limit: Decimal


@dataclass(frozen=True)
class Assignment:
    date: str
    amount: Decimal
    source: str
    card_id: str
    item_id: str


@dataclass(frozen=True)
class Violation:
    date: str
    violation_type: str
    details: str


@dataclass(frozen=True)
class FinanceResult:
    assignments: list[Assignment]
    violations: list[Violation]
    total_spend: Decimal
    unpurchasable_count: int
    max_card_utilization: Decimal


def _sorted_items(items: list[Item]) -> list[Item]:
    return sorted(items, key=lambda x: (-x.priority, x.cost, x.item_id))


def assign_items(config: FinanceConfig, items: list[Item], cards: list[Card]) -> FinanceResult:
    ordered_cards = sorted(cards, key=lambda c: c.card_id)
    remaining = {card.card_id: card.limit for card in ordered_cards}
    assignments: list[Assignment] = []
    violations: list[Violation] = []

    total_spend = Decimal("0.00")

    for item in _sorted_items(items):
        assigned_card_id = ""
        for card in ordered_cards:
            if remaining[card.card_id] >= item.cost:
                assigned_card_id = card.card_id
                break

        if assigned_card_id:
            remaining[assigned_card_id] -= item.cost
            total_spend += item.cost
            assignments.append(
                Assignment(
                    date=config.start_date,
                    amount=item.cost,
                    source="card",
                    card_id=assigned_card_id,
                    item_id=item.item_id,
                )
            )
            continue

        violations.append(
            Violation(
                date=config.start_date,
                violation_type="over_limit",
                details=f"item_id={item.item_id};cost={item.cost:.2f}",
            )
        )

    utilizations: list[Decimal] = []
    for card in ordered_cards:
        spent = card.limit - remaining[card.card_id]
        if card.limit == Decimal("0"):
            utilizations.append(Decimal("0"))
        else:
            utilizations.append(spent / card.limit)

    max_card_utilization = max(utilizations, default=Decimal("0"))

    return FinanceResult(
        assignments=sorted(assignments, key=lambda a: (a.date, a.card_id, a.item_id)),
        violations=sorted(violations, key=lambda v: (v.date, v.violation_type, v.details)),
        total_spend=total_spend,
        unpurchasable_count=len(violations),
        max_card_utilization=max_card_utilization,
    )
