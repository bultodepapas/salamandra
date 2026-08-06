# ADR-0016 — Reject PLA+

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** High `[M]` · **Reversible:** —
**Research:** [I-04 — Printing materials](../research/I-04-printing-materials.md)

## Context

Paired test on the same bench, same manufacturer (Polymaker PolyLite vs PolyMax, I-04):
**PLA+ is softer, not stiffer** — E 2.20 GPa `[M]` vs 3.00 GPa for normal PLA (−27 %),
sitting at the level of PETG and ABS, with **no thermal gain** (it fails at 65 °C like
normal PLA).

## Decision

**Reject PLA+** as a candidate structural material.

## Rationale

PLA+ is an intermediate point that solves no constraint: it gives up the best stiffness
of the family (G/ρ 0.53 vs 0.73) without gaining the thermal margin that PETG provides.
If the project needed PLA-family stiffness it would take normal PLA; if it needed
temperature it takes PETG (ADR-0021).

## Consequences

- The material set reduces to: PETG (base, ADR-0021), normal PLA (technical fallback per
  ADR-0021 review conditions), LW-PLA (reference-article benchmark only, I-04).
- Limitation declared: a couple of brands, not the whole PLA+ universe (I-04 §limits).
