"""Replay a year of daily demand for one SKU under a policy, with lost sales.

Order of events each day: receive what arrives, serve demand, review stock, pay holding
on what is left at night. Lead time is fixed. Unserved demand is lost and costs the margin.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from .ledger import Ledger

CENT = Decimal("0.01")
DAYS_PER_YEAR = 365


@dataclass(frozen=True)
class Sku:
    code: str
    unit_cost: Decimal
    price: Decimal
    order_cost: Decimal
    holding_rate: Decimal
    lead_days: int


@dataclass(frozen=True)
class ContinuousReview:
    """(s, Q): when position <= s, order Q."""

    reorder_point: int
    quantity: int


@dataclass(frozen=True)
class MonthlyCover:
    """Common rule: every `period` days order up to `level` (no safety stock)."""

    period: int
    level: int


Policy = ContinuousReview | MonthlyCover


@dataclass(frozen=True)
class Result:
    orders: int
    demand: int
    served: int
    lost: int
    ordering: Decimal
    holding: Decimal
    lost_margin: Decimal
    avg_stock: float

    @property
    def total(self) -> Decimal:
        return self.ordering + self.holding + self.lost_margin

    @property
    def fill_rate(self) -> float:
        return self.served / self.demand if self.demand else 1.0

    def turnover(self, days: int) -> float:
        """Units served per year over average units on the shelf (same ratio as in value)."""
        if self.avg_stock == 0:
            return 0.0
        return (self.served * DAYS_PER_YEAR / days) / self.avg_stock


def _order_qty(policy: Policy, day: int, position: int) -> int:
    if isinstance(policy, ContinuousReview):
        return policy.quantity if position <= policy.reorder_point else 0
    if day % policy.period == 0:
        return max(0, policy.level - position)
    return 0


def run(sku: Sku, policy: Policy, demand: list[int], start_stock: int) -> Result:
    if not demand:
        raise ValueError("demand is empty")
    book = Ledger()
    if start_stock:
        book.receive(-1, start_stock)
    pipeline: dict[int, int] = {}
    orders = served = 0
    night_units = 0
    for day, want in enumerate(demand):
        arriving = pipeline.pop(day, 0)
        if arriving:
            book.receive(day, arriving)
        served += book.issue(day, want)
        position = book.balance() + sum(pipeline.values())
        q = _order_qty(policy, day, position)
        if q:
            orders += 1
            pipeline[day + sku.lead_days] = pipeline.get(day + sku.lead_days, 0) + q
        night_units += book.balance()
    total_demand = sum(demand)
    lost = total_demand - served
    daily_hold = sku.unit_cost * sku.holding_rate / DAYS_PER_YEAR
    return Result(
        orders=orders,
        demand=total_demand,
        served=served,
        lost=lost,
        ordering=(sku.order_cost * orders).quantize(CENT, ROUND_HALF_UP),
        holding=(daily_hold * night_units).quantize(CENT, ROUND_HALF_UP),
        lost_margin=((sku.price - sku.unit_cost) * lost).quantize(CENT, ROUND_HALF_UP),
        avg_stock=night_units / len(demand),
    )
