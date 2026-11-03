from decimal import Decimal

import pytest

from stock_policy.simulate import ContinuousReview, MonthlyCover, Result, Sku, run

SKU = Sku("T1", Decimal("73"), Decimal("100"), Decimal("50"), Decimal("0.5"), lead_days=2)


def test_five_days_by_hand() -> None:
    # nights: 7, 4 (order 10 due day 3), 1, 8, 5 (order 10 due day 6) -> 25 unit-nights
    r = run(SKU, ContinuousReview(reorder_point=5, quantity=10), [3] * 5, start_stock=10)
    assert (r.orders, r.served, r.lost) == (2, 15, 0)
    assert r.ordering == Decimal("100.00")
    assert r.holding == Decimal("2.50")  # 73 x 0.5 / 365 = 0.10 per unit-night
    assert r.lost_margin == Decimal("0.00")
    assert r.total == Decimal("102.50")
    assert r.avg_stock == 5.0
    assert r.fill_rate == 1.0
    assert r.turnover(days=5) == pytest.approx(15 * 73 / 5)


def test_lost_sales_cost_the_margin() -> None:
    sku = Sku("T2", Decimal("10"), Decimal("15"), Decimal("1"), Decimal("0.1"), lead_days=3)
    r = run(sku, MonthlyCover(period=30, level=10), [5, 0], start_stock=2)
    assert (r.orders, r.served, r.lost) == (1, 2, 3)
    assert r.lost_margin == Decimal("15.00")
    assert r.fill_rate == 0.4
    assert r.turnover(days=2) == 0.0


def test_monthly_cover_orders_only_on_review_days() -> None:
    r = run(SKU, MonthlyCover(period=2, level=4), [1, 1, 1, 1], start_stock=0)
    # day 0: order 4 (due day 2); day 2: position 3 + 0 -> order 1 (due day 4)
    assert r.orders == 2
    assert r.served == 2


def test_position_below_s_orders_every_day() -> None:
    r = run(SKU, ContinuousReview(reorder_point=100, quantity=1), [0, 0, 0], start_stock=0)
    assert r.orders == 3


def test_empty_demand_and_zero_demand_fill_rate() -> None:
    with pytest.raises(ValueError):
        run(SKU, ContinuousReview(1, 1), [], start_stock=0)
    assert Result(0, 0, 0, 0, Decimal(0), Decimal(0), Decimal(0), 0.0).fill_rate == 1.0
