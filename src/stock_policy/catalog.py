"""Seeded synthetic catalogue: invented SKUs and daily demand. Not data from any company."""

from __future__ import annotations

import random
from dataclasses import dataclass
from decimal import Decimal

from .simulate import Sku


@dataclass(frozen=True)
class Item:
    sku: Sku
    daily_mean: float
    daily_sd: float


def items(n: int = 40, seed: int = 7) -> list[Item]:
    rng = random.Random(seed)
    out = []
    for i in range(n):
        cost = Decimal(rng.randrange(500, 40_000)) / 100
        mean = round(rng.uniform(2, 60), 1)
        out.append(Item(
            Sku(
                code=f"SKU-{i + 1:03d}",
                unit_cost=cost,
                price=(cost * Decimal(rng.choice(["1.25", "1.35", "1.5"]))).quantize(
                    Decimal("0.01")),
                order_cost=Decimal(rng.choice([40, 60, 90, 120])),
                holding_rate=Decimal("0.25"),
                lead_days=rng.choice([3, 5, 7, 10, 14, 21]),
            ),
            daily_mean=mean,
            daily_sd=round(mean * rng.uniform(0.2, 0.6), 1),
        ))
    return out


def demand(item: Item, days: int, seed: int) -> list[int]:
    """Normal daily demand, rounded and cut at zero."""
    rng = random.Random(f"{seed}-{item.sku.code}")
    return [max(0, round(rng.gauss(item.daily_mean, item.daily_sd))) for _ in range(days)]
