"""python -m stock_policy [--items N] [--seed S] [--service P]: print the yearly comparison."""

from __future__ import annotations

import argparse
from decimal import Decimal

from .catalog import demand as daily_demand
from .catalog import items
from .compare import Row, compare
from .simulate import DAYS_PER_YEAR


def table(n: int, seed: int, service: float) -> list[Row]:
    return [compare(i, daily_demand(i, DAYS_PER_YEAR, seed), service) for i in items(n, seed)]


def main(argv: list[str] | None = None) -> str:
    ap = argparse.ArgumentParser(prog="stock_policy")
    ap.add_argument("--items", type=int, default=40)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--service", type=float, default=0.95)
    a = ap.parse_args(argv)
    rows = table(a.items, a.seed, a.service)
    base = sum((r.baseline.total for r in rows), Decimal(0))
    new = sum((r.proposed.total for r in rows), Decimal(0))
    demand = sum(r.baseline.demand for r in rows)

    def fill(k: str) -> float:
        served: int = sum(getattr(r, k).served for r in rows)
        return served / demand

    lines = [
        f"synthetic catalogue: {a.items} SKUs, seed {a.seed}, {DAYS_PER_YEAR} days",
        f"monthly cover  total cost {base:>14,.2f}  fill rate {fill('baseline'):.1%}",
        f"(s, Q) policy  total cost {new:>14,.2f}  fill rate {fill('proposed'):.1%}",
        f"difference                {base - new:>14,.2f}  ({(base - new) / base:.1%})",
    ]
    out = "\n".join(lines)
    print(out)
    return out


if __name__ == "__main__":  # pragma: no cover
    main()
