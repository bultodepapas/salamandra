# ADR-0021 — PETG as the base structural material

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** High · **Reversible:** Partial
**Research:** [I-04 — Printing materials](../research/I-04-printing-materials.md)

## Context

The primary structure is a printed shell. The material governs torsional stiffness, which is the project's dominant risk ([ADR-0001](ADR-0001-inverted-sweep.md)).

Five materials were evaluated with paired test data.

## Alternatives considered

| Material | E printed | G_eff | ρ | **G/ρ** | Verdict |
|---|---|---|---|---|---|
| Normal PLA | 3.00 GPa `[M]` | 0.90 | 1.24 | **0.73** | Best stiffness. Fails at 65 °C. Brittle |
| PLA+ | 2.20 GPa `[M]` | 0.66 | 1.24 | 0.53 | **Rejected** — ADR-0016 |
| ASA | 1.9–2.2 GPa `[E]` | 0.58 | 1.07 | 0.53 | Best thermal and weldable, but warps |
| **PETG** | **1.94 GPa** `[M]` | **0.55** | **1.27** | **0.43** | **Adopted** |
| LW-PLA | ~1.0 GPa `[E]` | 0.35 | 0.68 | 0.51 | Light but soft and expensive |

## Decision

**Conventional spool PETG**, light color, as the single structural material.

## Rationale

**PETG is the worst of the thermoplastics in specific torsional stiffness.** It is adopted anyway because, with gyroid infill and a three-cell section, the divergence criterion is met — and then the choice is decided by secondary criteria where PETG wins:

| Criterion | PETG | Alternative |
|---|---|---|
| Thermal margin | HDT ≈ 70 °C | PLA/PLA+ fail at 65 °C `[M]` |
| Toughness in belly landing | Yields, does not break | PLA shatters |
| Repeatability without active chamber | Good | ASA warps |
| Price and availability | Best | LW-PLA ~3× |

**Geometric twist is a trim parameter** ([ADR-0003](README.md)). A material that deforms in a poorly repeatable way corrupts the variable that governs the balance. That discarded ASA despite its advantages.

## Consequences

- Forces mission **branch A** ([ADR-0010](ADR-0010-mission-branch.md)).
- Requires **light color** (ADR-0012).
- Joints need a specific adhesive (ADR-0023): 3D-Gloop PETG or 30-min epoxy. Not E6000.
- Requires gyroid infill ([ADR-0028](ADR-0028-gyroid-infill.md)) so the closed section works.

## Associated corrections

- **C8** — it was claimed that PETG has better layer adhesion than PLA. **False**: Z retention, PLA 55 %, PETG 46 %, ASA 29 % `[M]`.
- **C9** — it was claimed that PETG cannot be glued. Too categorical.

## Review conditions

If test E7 measured a divergence below criterion and the plastic remedy came out too heavy, normal PLA (G/ρ 0.73) is the technical alternative, at the cost of losing the thermal margin.
