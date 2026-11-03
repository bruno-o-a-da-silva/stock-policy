from decimal import Decimal

import pytest

from stock_policy.policy import (
    critical_fractile,
    eoq,
    kanban_cards,
    newsvendor,
    reorder_point,
    safety_stock,
)


def test_eoq_hand_case() -> None:
    # D = 3650, S = 50, H = 20 x 0.25 = 5 -> sqrt(73000) = 270.19 -> 271
    assert eoq(3650, Decimal("50"), Decimal("20"), Decimal("0.25")) == 271


def test_eoq_exact_square_is_not_rounded_up() -> None:
    # 2 x 1000 x 10 / 2 = 10000 -> 100
    assert eoq(1000, Decimal("10"), Decimal("8"), Decimal("0.25")) == 100


@pytest.mark.parametrize(
    "args", [(0, "1", "1", "1"), (1, "0", "1", "1"), (1, "1", "0", "1"), (1, "1", "1", "0")]
)
def test_eoq_rejects_non_positive(args: tuple[int, str, str, str]) -> None:
    d, s, c, h = args
    with pytest.raises(ValueError):
        eoq(d, Decimal(s), Decimal(c), Decimal(h))


def test_safety_stock_hand_case() -> None:
    # z(0.95) = 1.6449, sd 10, L 4 -> 1.6449 x 10 x 2 = 32.9 -> 33
    assert safety_stock(10, 4, 0.95) == 33
    assert safety_stock(10, 4, 0.5) == 0
    assert safety_stock(0, 9, 0.99) == 0


@pytest.mark.parametrize("args", [(-1, 1, 0.9), (1, -1, 0.9), (1, 1, 0.4), (1, 1, 1.0)])
def test_safety_stock_rejects(args: tuple[float, int, float]) -> None:
    with pytest.raises(ValueError):
        safety_stock(*args)


def test_reorder_point() -> None:
    assert reorder_point(20, 10, 4, 0.95) == 80 + 33
    with pytest.raises(ValueError):
        reorder_point(-1, 1, 1, 0.9)


def test_kanban_hand_case() -> None:
    # 10 per day x 5 days x 1.2 / 12 per bin = 5 cards
    assert kanban_cards(10, 5, 12, 0.2) == 5
    assert kanban_cards(10, 5, 12, 0.21) == 6


@pytest.mark.parametrize("args", [(0, 1, 1, 0), (1, 0, 1, 0), (1, 1, 0, 0), (1, 1, 1, -0.1)])
def test_kanban_rejects(args: tuple[float, int, int, float]) -> None:
    with pytest.raises(ValueError):
        kanban_cards(*args)


def test_newsvendor_symmetric_costs_buys_the_mean() -> None:
    # Cu = 30 - 18 = 12, Co = 18 - 6 = 12 -> fractile 0.5 -> q = mean
    assert critical_fractile(Decimal(30), Decimal(18), Decimal(6)) == 0.5
    assert newsvendor(100, 20, Decimal(30), Decimal(18), Decimal(6)) == 100


def test_newsvendor_cheap_leftover_buys_more() -> None:
    # Cu = 20, Co = 2 -> 0.909 -> z = 1.335 -> 100 + 26.7 -> 127
    assert newsvendor(100, 20, Decimal(40), Decimal(20), Decimal(18)) == 127


def test_newsvendor_never_negative() -> None:
    assert newsvendor(1, 50, Decimal(11), Decimal(10), Decimal(0)) == 0


def test_newsvendor_rejects() -> None:
    with pytest.raises(ValueError):
        critical_fractile(Decimal(10), Decimal(10), Decimal(1))
    with pytest.raises(ValueError):
        newsvendor(-1, 1, Decimal(3), Decimal(2), Decimal(1))
