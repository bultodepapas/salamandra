# ADR-0010 — Mission branch: fast cruise

**Status:** ⬜ Superseded by
[ADR-0048](ADR-0048-article-1-mission-and-configurations.md) · **Date:** 2026-07-28 ·
**Confidence:** Decided for v0.6 · **Reversible:** Yes under M0/M2
**Research:** [I-01](../research/I-01-aspect-ratio-reynolds.md), [I-03](../research/I-03-propulsion-chain.md)

> **2026-08-21 reset:** Wh/km remains the performance metric, but a single fast-cruise
> branch no longer governs. Revision 2 compares total Wh/km over E0–E3 and treats range and
> endurance as outcomes.

**Article #1 redesign:** `SUPERSEDED` · **Gate:** `M0` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## Context

There were two mutually exclusive objective functions. **They are not a continuous trade-off: they diverge from the first stroke.**

| Branch | Metric | Planform |
|---|---|---|
| **A — Fast cruise** | Wh/km at 90–120 km/h | AR 5–7, wing loading 55–70 g/dm² |
| **B — Endurance** | Minutes of flight | AR 8–12, wing loading 25–35 g/dm² |

This decision blocked the whole project during the research phase.

## Decision

**Branch A — fast cruise.**

## Rationale

The choice of PETG forces it. Branch B requires 25–35 g/dm²; at S = 0.282 m² that is 700–990 g of AUW. Only the PETG shell weighs 550–650 g `[E]`; with battery and motor the budget is exceeded before starting.

**It is not a preference, it is a material constraint.** And it is coherent: branch A *wants* high wing loading, so the PETG density stops being a penalty.

## Consequences

- Efficiency objective expressed as **Wh/km**, not minutes.
- The aspect ratio is set low (ADR-0004), which also helps divergence.
- **Declared non-goal:** this project is not a thermal glider.

## Note on "efficient"

The initial analysis showed that the TBS Mojito **is not energy-efficient** — 0.74 Wh/(km·kg), the same as a cheap foam wing. This project's efficiency is sought where the data say the gap is: **the propulsion chain** ([I-03](../research/I-03-propulsion-chain.md)), not the aerodynamics.
