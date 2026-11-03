"""Draw docs/img/hero.png, cost_curve.png and sawtooth.png from the seeded synthetic run.

Every number is computed by the library on the default run (40 SKUs, seed 7, 95% service).
"""

from decimal import Decimal

import matplotlib.pyplot as plt
from _style import BG, GOLD, GOLD_DIM, IMG, MUTED, SERIF, TEXT, style, title

from stock_policy.__main__ import table
from stock_policy.compare import monthly_cover
from stock_policy.policy import eoq
from stock_policy.simulate import DAYS_PER_YEAR

ROWS = table(40, 7, 0.95)
PARTS = ("ordering", "holding", "lost_margin")
NAMES = {"ordering": "Ordering", "holding": "Holding", "lost_margin": "Lost margin"}
SHADE = {"ordering": GOLD_DIM, "holding": GOLD, "lost_margin": "#E8D27A"}


def sums(kind: str) -> dict[str, float]:
    return {p: float(sum((getattr(getattr(r, kind), p) for r in ROWS), Decimal(0)))
            for p in PARTS}


def hero() -> None:
    base, new = sums("baseline"), sums("proposed")
    tb, tn = sum(base.values()), sum(new.values())
    fig = plt.figure(figsize=(16, 6.4), dpi=100)
    fig.text(0.05, 0.78, "stock-policy", fontfamily=SERIF, fontsize=50, color=TEXT)
    fig.text(0.05, 0.69, "When to reorder and how much, per item,", fontsize=17, color=TEXT)
    fig.text(0.05, 0.635, "proved by replaying a year of demand.", fontsize=17, color=MUTED)
    fig.add_artist(plt.Line2D([0.05, 0.12], [0.57, 0.57], color=GOLD, lw=2))
    fig.text(0.95, 0.80, f"{(tb - tn) / tb:.0%} lower", fontfamily=SERIF, fontsize=40,
             color=GOLD, ha="right")
    fig.text(0.95, 0.72, "yearly stock cost, 40 synthetic SKUs, seed 7", fontsize=13,
             color=MUTED, ha="right")
    ax = fig.add_axes((0.05, 0.1, 0.9, 0.38))
    ax.set_axis_off()
    ax.set_xlim(0, tb * 1.02)
    ax.set_ylim(-0.7, 1.9)
    for y, label, part, tot in ((1.2, "Monthly cover", base, tb), (0.2, "(s, Q)", new, tn)):
        x = 0.0
        for p in PARTS:
            ax.barh(y, part[p], left=x, height=0.55, color=SHADE[p], edgecolor=BG, lw=1.5)
            x += part[p]
        ax.text(0, y + 0.38, f"{label}   {tot:,.0f}", fontsize=13, color=TEXT)
    for k, p in enumerate(PARTS):
        ax.barh(-0.45, tb * 0.015, left=tb * (0.62 + k * 0.13), height=0.18, color=SHADE[p])
        ax.text(tb * (0.64 + k * 0.13), -0.45, NAMES[p], va="center", fontsize=11, color=MUTED)
    fig.savefig(IMG / "hero.png")
    plt.close(fig)


def cost_curve() -> None:
    item = ROWS[0].item
    s = item.sku
    d = item.daily_mean * DAYS_PER_YEAR
    h = float(s.unit_cost * s.holding_rate)
    qs = list(range(20, 800, 5))
    order = [d / q * float(s.order_cost) for q in qs]
    hold = [q / 2 * h for q in qs]
    q_star = eoq(round(d + 0.5), s.order_cost, s.unit_cost, s.holding_rate)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(qs, order, color=GOLD_DIM, lw=1.5, label="Ordering  D / Q x S")
    ax.plot(qs, hold, color=MUTED, lw=1.5, label="Holding  Q / 2 x H")
    ax.plot(qs, [a + b for a, b in zip(order, hold, strict=True)], color=GOLD, lw=2.5,
            label="Total")
    ax.axvline(q_star, color=TEXT, lw=0.8, ls=":")
    ax.text(q_star + 8, max(order) * 0.8, f"Q* = {q_star}", color=TEXT)
    ax.set_xlabel("Order size Q (units)")
    ax.set_ylabel("Cost per year")
    ax.legend(frameon=False)
    title(ax, f"Where the two costs cross: {s.code}", "Synthetic item, seed 7.")
    fig.tight_layout()
    fig.savefig(IMG / "cost_curve.png")
    plt.close(fig)


def sawtooth() -> None:
    row = ROWS[3]
    days = 150
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(row.baseline.nights[:days], color=MUTED, lw=1.3,
            label=f"Monthly cover, up to {monthly_cover(row.item).level}")
    ax.plot(row.proposed.nights[:days], color=GOLD, lw=1.8,
            label=f"(s, Q): s = {row.rule.reorder_point}, Q = {row.rule.quantity}")
    ax.set_ylim(0, max(row.baseline.nights[:days]) * 1.3)
    ax.set_xlabel("Day")
    ax.set_ylabel("Units on the shelf at night")
    ax.legend(frameon=False)
    title(ax, f"Same demand, two rules: {row.item.sku.code}",
          f"Synthetic item, seed 7, lead time {row.item.sku.lead_days} days.")
    fig.tight_layout()
    fig.savefig(IMG / "sawtooth.png")
    plt.close(fig)


if __name__ == "__main__":
    style()
    IMG.mkdir(parents=True, exist_ok=True)
    hero()
    cost_curve()
    sawtooth()
