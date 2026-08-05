# ADR-0028 — Gyroid 5 % infill

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** Medium `[M]` · **Reversible:** Yes
**Associated correction:** C12
**Research:** [I-05](../research/I-05-divergence-flutter.md)

## Context

The original specification said **infill 0 %, only perimeters**, inherited from LW-PLA vase-mode practice, where the goal is minimum mass.

**It was an error**, and the mechanism is not what it seems.

## The error

The Bredt-Batho formulation assumes **the skin does not buckle**. A 0.4–0.9 mm skin over an unsupported span of 100 mm or more, under shear, **buckles locally well below the material limit**. Once it buckles, the effective GJ does not degrade progressively: **it collapses**.

That is: **without infill, the GJ calculation was overestimated, not underestimated.** The error ran in the opposite direction to what was assumed.

## Decision

**Gyroid 5 % infill** throughout the shell, instead of a third perimeter.

## Rationale

- **The gyroid's contribution is not directly torsional** — it sits near the shear center and contributes little to `J`. Its function is to **stabilize the skin** so the closed cell actually works.
- **More stiffness per gram than an additional perimeter**, because it attacks the mode that actually fails.
- **Precedent `[M]`:** the Peregrine 840 mm print profile specifies **4 % gyroid** with **a single perimeter**, and it flies.

5 % is adopted and not 8 % (a value initially proposed with no basis) because 4 % is proven in flight and 8 % was an unsupported own estimate.

## Consequences

- Replaces the third perimeter: **2 perimeters (0.9 mm) + gyroid 5 %**.
- Saves ~135 g versus the three-perimeter path.
- Complicates the layup: gyroid in thin-walled parts can come out discontinuous. Verify on the first real part.

## Associated corrections

- **C12** — 0 % infill was wrong for a PETG shell.
- **C15** — it was claimed that one perimeter fails the criterion. **Falsified by flying hardware**: the Peregrine uses 1 perimeter of 0.42 mm.
