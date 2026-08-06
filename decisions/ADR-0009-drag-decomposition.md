# ADR-0009 — Separate drag decomposition; never a single Oswald factor

**Status:** ✅ Active · **Date:** 2026-07-27 · **Confidence:** High · **Reversible:** No
**Research:** [I-01 — Aspect-ratio / Reynolds frontier](../research/I-01-aspect-ratio-reynolds.md), first_investigation §4.2 (D9)

## Context

**Correction C1:** it was claimed that the Oswald factor collapses with aspect ratio for
physical reasons, invalidating higher AR. It is largely a **definition artifact**: e_v
decreases with AR by algebraic construction (e_v = 1/(1+δ+kπAR)). Raising AR does work;
the real effects are saturation and the chord→Re coupling.

The parabolic polar with a **single Oswald factor is only valid above Re ≈ 5×10⁶**
(Spedding & McArthur, 2010). The project's regime is **three orders of magnitude below**
(Re 3–5×10⁵).

## Decision

**Always separate the viscous term from the induced term; never use a single Oswald
factor** for drag. The decomposition of first_investigation §4.2 is mandatory
(CLAUDE.md hard rule; docs/04 conventions). The Oswald factor appears only as a
reporting figure (e.g. e = 0.85 `[E]` in `yaw_stability.py`), never as the drag model.

## Consequences

- Drag targets (O1, ≤ 1.15 Wh/km) are decomposed: propeller chain vs C_D0 vs induced —
  the C_D0 term is the object of the G3 register and of E2.
- Prevents the repeat of C1-type reasoning in every future trade (AR, winglet, fin —
  including the V1-fin drag estimate of I-20, computed as ΔCD0, not as Δe).
