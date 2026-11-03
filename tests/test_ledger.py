import pytest

from stock_policy.ledger import Ledger, Move


def test_replay_gives_the_same_balance() -> None:
    a = Ledger()
    a.receive(0, 10)
    assert a.issue(1, 4) == 4
    b = Ledger(list(a.moves))
    assert a.balance() == b.balance() == 6


def test_issue_is_capped_and_zero_is_not_recorded() -> None:
    book = Ledger()
    book.receive(0, 3)
    assert book.issue(0, 5) == 3
    assert book.issue(1, 2) == 0
    assert book.moves == [Move(0, "receipt", 3), Move(0, "issue", 3)]


def test_rejects_bad_moves() -> None:
    book = Ledger()
    with pytest.raises(ValueError):
        book.receive(0, 0)
    with pytest.raises(ValueError):
        book.issue(0, -1)
