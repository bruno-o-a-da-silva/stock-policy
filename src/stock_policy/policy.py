"""Order size and order timing for one SKU.

Money is Decimal. Quantities are whole units, always rounded up so the policy never
orders less than the formula asks for.
"""

from __future__ import annotations

import math
from decimal import Decimal
from statistics import NormalDist


def eoq(annual_demand: int, order_cost: Decimal, unit_cost: Decimal, holding_rate: Decimal) -> int:
    """Economic order quantity Q = sqrt(2 D S / H), with H = unit cost x holding rate."""
    if annual_demand <= 0 or order_cost <= 0 or unit_cost <= 0 or holding_rate <= 0:
        raise ValueError("demand and costs must be positive")
    h = unit_cost * holding_rate
    q = (Decimal(2) * annual_demand * order_cost / h).sqrt()
    return math.ceil(q)


def safety_stock(daily_sd: float, lead_days: int, service: float) -> int:
    """z x sigma_daily x sqrt(L): demand noise over the lead time, for a cycle service level."""
    if daily_sd < 0 or lead_days < 0 or not 0.5 <= service < 1:
        raise ValueError("sd and lead time >= 0, service in [0.5, 1)")
    z = NormalDist().inv_cdf(service)
    return math.ceil(z * daily_sd * math.sqrt(lead_days) - 1e-9)


def reorder_point(daily_mean: float, daily_sd: float, lead_days: int, service: float) -> int:
    """Order when stock on hand plus on order falls to demand over lead time + safety stock."""
    if daily_mean < 0:
        raise ValueError("mean demand must be >= 0")
    return math.ceil(daily_mean * lead_days - 1e-9) + safety_stock(daily_sd, lead_days, service)


def kanban_cards(daily_mean: float, lead_days: int, container: int, safety: float) -> int:
    """Toyota card count N = D x L x (1 + safety) / container size."""
    if daily_mean <= 0 or lead_days <= 0 or container <= 0 or safety < 0:
        raise ValueError("positive demand, lead time and container; safety >= 0")
    return math.ceil(daily_mean * lead_days * (1 + safety) / container - 1e-9)


def critical_fractile(price: Decimal, cost: Decimal, salvage: Decimal) -> float:
    """Cu / (Cu + Co): the chance of selling the last unit that still pays to stock."""
    if not salvage < cost < price:
        raise ValueError("need salvage < cost < price")
    under = price - cost
    over = cost - salvage
    return float(under / (under + over))


def newsvendor(mean: float, sd: float, price: Decimal, cost: Decimal, salvage: Decimal) -> int:
    """One-shot buy for normal demand: mean + z(fractile) x sd."""
    if mean < 0 or sd < 0:
        raise ValueError("mean and sd must be >= 0")
    z = NormalDist().inv_cdf(critical_fractile(price, cost, salvage))
    return max(0, math.ceil(mean + z * sd - 1e-9))
