# ADR-0004 — Aspect ratio 6.0

**Status:** 🔄 Provisional · **Date:** 2026-07-28 · **Confidence:** Medium `[E]` · **Reversible:** No
**Gaps:** G1, G6 · **Research:** [I-01](../research/I-01-aspect-ratio-reynolds.md), [I-05](../research/I-05-divergence-flutter.md)

**Article #1 redesign:** `CANDIDATE-ONLY` · **Gate:** `M3` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## Context

Intuition says "more aspect ratio, less induced drag". At low Reynolds numbers that stops being true past a certain point, and in forward sweep there is a second reason not to raise it.

## Decision history

- **Rev 1.0:** AR 6–8, by saturation of the benefit and the chord→Reynolds coupling.
- **Rev 1.1:** tightened to **6.0** when the divergence term appeared.

## Decision

**Aspect ratio 6.0** → with b = 1300 mm, S = 0.282 m², mean chord 217 mm.

## Rationale

**Argument 1 — Reynolds (I-01).** The correct causal chain:

1. The induced term still falls as 1/(π·AR·e_i) — raising AR **does work**.
2. The viscous term k·C_L² **does not depend on aspect ratio**.
3. Therefore the benefit **saturates**.
4. At constant area, raising AR shortens the chord → lowers Re → raises k and C_D0.

Point 4 generates the optimum; point 3 makes it flat.

**Argument 2 — Divergence (I-05).** The divergence speed scales as:

```text
V_div ∝ AR^(−3/4)
```

Raising from 6 to 8 costs ~19 % of V_div, in addition to the chord penalty.

**Contrast `[M]`:** the Peregrine 840 mm, which flies, has AR ≈ 5.05.

## Consequences

- Sets S = 0.282 m² for b = 1300 mm.
- Wing loading 57 g/dm² with 6S1P → stall speed ~43 km/h (see correction C16).
- The alternative panels (1100 / 1600) change the AR and therefore the neutral point. See [ADR-0032](ADR-0032-modularity.md) and R-NP.

## Review conditions

Close G1 with the real reference planform. If the stability analysis (Phase 1) requires more area to lower the stall speed, AR will fall before the wingspan rises.
