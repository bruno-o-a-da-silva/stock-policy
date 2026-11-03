from decimal import Decimal

from stock_policy.__main__ import main, table
from stock_policy.catalog import demand, items
from stock_policy.compare import monthly_cover, set_policy


def test_catalogue_is_seeded_and_repeatable() -> None:
    a, b = items(5, seed=3), items(5, seed=3)
    assert a == b
    assert demand(a[0], 30, 3) == demand(b[0], 30, 3)
    assert all(x >= 0 for x in demand(a[0], 365, 3))
    assert a != items(5, seed=4)


def test_policies_for_one_item() -> None:
    item = items(1, seed=7)[0]
    rule = set_policy(item, 0.95)
    assert rule.reorder_point > item.daily_mean * item.sku.lead_days
    cover = monthly_cover(item)
    assert cover.period == 30
    assert cover.level >= item.daily_mean * (30 + item.sku.lead_days)


def test_headline_run_is_stable() -> None:
    out = main(["--items", "40", "--seed", "7"])
    assert "monthly cover  total cost   1,390,683.76" in out
    assert "(s, Q) policy  total cost     459,279.12" in out
    rows = table(3, 1, 0.9)
    assert all(r.proposed.total > Decimal(0) for r in rows)
