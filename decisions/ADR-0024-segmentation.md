# ADR-0024 — Three segments per wing half, 45° roll on the bed

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** High · **Reversible:** Yes
**Feeds:** guide §7.4 (printability, O3/O5)

## Context

Printer class: 256 mm bed (Bambu P1S, O3). The 1300 mm wing must be segmented to fit.
The orientation on the bed decides whether the segments fit at all.

> **Correction C24:** the v0.1 figure "segments of ≈ 118 mm span" was wrong — actual
> segment spans are 152/151/152 mm; and "span axis at 45° in the bed plane" does **not**
> fit (segment 1 would need ≈ 281 mm).

## Decision

- **3 segments per wing half** (plus the CORE), cuts at **y = 347 mm and 498 mm**
  (53.3 % / 76.7 % of the half-span) (guide §7.4).
- **Print orientation: 45° roll of the airfoil plane about the spanwise axis** (airfoil
  at 45° to the bed, leading edge low). Footprint: span 152 mm × chord·cos 45° ≈ 174 mm
  at the panel root — fits the 256 mm bed.
- Print budget ≤ 20 h per wing half (O5).

## Consequences

- Segmentation defines the joint positions that ADR-0023 and ADR-0032 apply to; the
  joints at y = 347/498 coincide with the dihedral kinks (guide §5.3, C22).
- The 45° roll is the reason the elevon hinge at 0.72 c and the servo cavities (§7.5)
  must be modeled with the build orientation in mind (overhangs).
