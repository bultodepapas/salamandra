# ADR-0015 — Carbon is a bending and alignment element, not torsion

**Status:** ✅ Active (corrected) · **Date:** 2026-07-28 · **Confidence:** High `[D]`
**Associated correction:** C11

## Context

Modeling intuition says that "adding carbon" solves any structural problem. In wing torsion that is false in the common case and true in a specific one — and the difference matters.

## Original (incorrect) version

A 10/8 mm tube was calculated, 2.3 N·m² came out versus ~70 from the skin, and it was concluded: **"the tubes are not for torsion"**.

## The correction (C11)

In a thin-wall tube:

    J = π·D³·t / 4

**It scales with the cube of the diameter.** Going from 10 to 18 mm is not 80 % more: it is almost **6 times** more.

| Element | GJ | Note |
|---|---|---|
| Solid 6 mm rod | ~0.5 N·m² | Nothing |
| 10/8 tube | 2.3 N·m² | The case that was calculated |
| 18/16 pultruded tube | ~18 N·m² | +26 % over the skin |
| **18/16 braided ±45° tube** | **~69 N·m²** | **Doubles the wing's GJ** |

## Decision

**Carbon is used as a bending spar and joint-alignment pin. Not as the primary torsional element.**

The braided torsion tube stays documented as **option B** (ADR-0030), not discarded.

## Rationale for rejecting it as the primary path

Three conditions, all three elimination rounds:

1. **Diameter ≥ 16 mm.** Below that it does not pay for its mass.
2. **Braided ±45°, not pultruded.** A pultruded tube has the fiber on the axis: in torsion the matrix works and G falls to 3–4 GPa versus 15. **It is a factor 4 in the result** — and **almost no modeling vendor declares the layup**. You can buy a tube, get +26 % instead of +100 %, and never find out.
3. **Continuous bonding, not housed.** A tube floating in a sleeve contributes **zero**. It requires transfer ribs along the whole run.

**It is rejected as the primary path because it introduces two new uncertainties — unknown layup and bonding quality — in the parameter that is already the dominant risk and is only known to ±35 %.**

## Reference

The Peregrine 840 mm uses an Ø8 × 654 mm tube — a **bending spar**, with a torsional contribution of ~1 N·m². Confirms the criterion.
