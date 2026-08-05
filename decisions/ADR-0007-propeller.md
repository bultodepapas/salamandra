# ADR-0007 — Propeller P/D 0.8–1.0 matched by advance ratio

**Status:** ✅ Active · **Date:** 2026-07-27 · **Confidence:** High · **Reversible:** Yes
**Research:** [I-03 — Propulsion chain](../research/I-03-propulsion-chain.md)

## Context

The propulsion chain is the term of the range equation with the largest margin for immediate improvement, and the one that sustains objective O1 (≤ 1.15 Wh/km).

## Decision

**Propeller with pitch/diameter 0.8–1.0, matched by advance ratio J at cruise speed, operating at high rpm.**

## Rationale `[D]` — own extraction from the UIUC database

Efficiency peak at ~6000 rpm:

| Propeller | P/D | η max | Optimal J | V @6000 rpm | V @16000 rpm |
|---|---|---|---|---|---|
| APC-E 8×4 | 0.50 | 0.600 | 0.481 | 35 km/h | 94 km/h |
| APC-E 8×6 | 0.75 | 0.678 | 0.689 | 50 km/h | 134 km/h |
| **APC-E 8×8** | **1.00** | **0.731** | 0.784 | 57 km/h | 153 km/h |
| APC-E 9×6 | 0.67 | 0.683 | 0.583 | 48 km/h | 128 km/h |
| APC-E 10×7 | 0.70 | 0.705 | 0.576 | 53 km/h | 140 km/h |

Three readings:

1. **Pitch dominates.** From 8×4 to 8×8, same diameter: **+22 % of peak efficiency**.
2. **The optimal speed is a propeller × rpm product**, not a propeller property. The same 8×8 peaks at 57 km/h at 6000 rpm and at 153 km/h at 16000.
3. **Raising rpm improves efficiency** via the blade Reynolds effect `[M]` (Brandt & Selig).

## The gap that justifies O1

| Component | Range |
|---|---|
| Propeller at its optimal J | 0.65 – 0.73 |
| Well-sized motor + ESC | ≈ 0.85 |
| **Theoretical product** | **0.55 – 0.62** |
| **Real value solved from the Mojito flight** | **≈ 0.50** |

**Moving from 0.50 to 0.60 is +20 % range without touching the aerodynamics.** It is the project's central claim.

## Consequences

- The motor must be chosen so the propeller falls at its optimal J at cruise speed, not by static thrust.
- The matching table per pack is a publishable output ([ADR-0033](ADR-0033-electronics-out.md)).
- Realized and verified with test E3.
