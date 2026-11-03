"""Append-only stock ledger. Stock is never stored, only replayed from the moves.

A receipt adds units, an issue removes them and is refused if it would go below zero.
Replaying the same moves always gives the same balance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Kind = Literal["receipt", "issue"]


@dataclass(frozen=True)
class Move:
    day: int
    kind: Kind
    units: int


@dataclass
class Ledger:
    moves: list[Move] = field(default_factory=list)

    def balance(self) -> int:
        return sum(m.units if m.kind == "receipt" else -m.units for m in self.moves)

    def receive(self, day: int, units: int) -> None:
        if units <= 0:
            raise ValueError("receipt must be positive")
        self.moves.append(Move(day, "receipt", units))

    def issue(self, day: int, wanted: int) -> int:
        """Issue up to `wanted`; return what was really issued (the rest is a lost sale)."""
        if wanted < 0:
            raise ValueError("issue must be >= 0")
        got = min(wanted, self.balance())
        if got:
            self.moves.append(Move(day, "issue", got))
        return got
