"""Set both policies for each item and replay the same demand under each."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .catalog import Item
from .policy import eoq, reorder_point
from .simulate import DAYS_PER_YEAR, ContinuousReview, MonthlyCover, Result, run


@dataclass(frozen=True)
class Row:
    item: Item
    rule: ContinuousReview
    baseline: Result
    proposed: Result


def set_policy(item: Item, service: float) -> ContinuousReview:
    s = item.sku
    annual = math.ceil(item.daily_mean * DAYS_PER_YEAR)
    q = eoq(annual, s.order_cost, s.unit_cost, s.holding_rate)
    return ContinuousReview(reorder_point(item.daily_mean, item.daily_sd, s.lead_days, service), q)


def monthly_cover(item: Item, period: int = 30) -> MonthlyCover:
    return MonthlyCover(period, math.ceil(item.daily_mean * (period + item.sku.lead_days)))


def compare(item: Item, demand: list[int], service: float = 0.95) -> Row:
    rule = set_policy(item, service)
    start = math.ceil(item.daily_mean * item.sku.lead_days) + rule.quantity
    return Row(
        item,
        rule,
        run(item.sku, monthly_cover(item), demand, start),
        run(item.sku, rule, demand, start),
    )
