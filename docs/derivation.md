# Derivation

All quantities are per SKU. D = annual demand (units), S = cost of placing one order,
c = unit cost, i = holding rate per year, H = c x i = cost of keeping one unit for a year.

## 1. Order size (EOQ)

Ordering Q units at a time means D / Q orders a year, and the stock falls from Q to 0
between orders, so on average Q / 2 units sit on the shelf.

    yearly cost  C(Q) = (D / Q) S + (Q / 2) H

The first term falls as Q grows, the second rises. The lowest point is where the slope is
zero:

    dC/dQ = -D S / Q^2 + H / 2 = 0   ->   Q* = sqrt(2 D S / H)

At Q* the two costs are equal. Because of the square root, four times the demand only
doubles the order size. Hand case (tested): D = 3650, S = 50, H = 20 x 0.25 = 5 gives
Q* = sqrt(73000) = 270.19, ordered as 271.

## 2. When to order (reorder point)

An order placed today arrives after L days. If daily demand has mean m and standard
deviation sigma, and days are independent, demand over the lead time has mean m L and
standard deviation sigma sqrt(L) (variances add, so the spread grows with the square root
of time, the same law as a random walk).

    s = m L + z sigma sqrt(L)

z is chosen so the chance of not running out during one lead time equals the service level
(z = 1.645 for 95%). Hand case: m = 20, sigma = 10, L = 4, 95% gives 80 + 1.645 x 10 x 2 =
80 + 32.9, so s = 113.

## 3. Kanban cards

A card circulates once per replenishment loop. To cover demand while a card is away (L days)
with a safety margin a, using containers of C units:

    N = D_daily L (1 + a) / C

Hand case: 10 a day, 5 days, 20% margin, bins of 12 gives 60 / 12 = 5 cards.

## 4. One-shot buy (newsvendor)

For a seasonal item bought once, each unit short loses Cu = price - cost and each unit left
over loses Co = cost - salvage. Adding one more unit pays while the chance of selling it
is above Co / (Cu + Co), so the best quantity is the demand quantile at

    F(Q*) = Cu / (Cu + Co)

Hand case: price 30, cost 18, salvage 6 gives Cu = Co = 12, F = 0.5, so Q* = mean demand.

## 5. The replay

Formulas assume things (steady demand, normal noise). The replay checks them against a year
of daily demand. Each day: receive arrivals, serve demand (unserved demand is lost and costs
Cu), review the stock position (on hand + on order), pay holding of H / 365 per unit left at
night. Stock is never stored, only rebuilt from an append-only ledger of receipts and
issues. Hand case (tested): lead time 2, s = 5, Q = 10, start 10, demand 3 a day for 5 days
gives night stock 7, 4, 1, 8, 5, two orders and 25 unit-nights.
