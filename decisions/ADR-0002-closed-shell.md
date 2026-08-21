# ADR-0002 — Closed three-cell shell

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** Medium `[I]` · **Reversible:** No
**Research:** [I-05](../research/I-05-divergence-flutter.md)

**Article #1 redesign:** `REOPENED` · **Gate:** `M6` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## Context

In forward sweep, torsional stiffness governs the dominant risk. The construction determines that stiffness more than the material.

## Alternatives

| Construction | Torsional stiffness | Verdict |
|---|---|---|
| Molded foam with embedded rods | Open or nearly open section. Orders of magnitude worse | **Rejected** |
| **Closed printed shell** | Torsion box by construction | **Adopted** |

## Decision

**Closed three-cell shell:** D-box at the leading edge + center cell + hinge cell.

## Rationale

A printed part is a **closed shell — a torsion box by construction**. In a closed section, `J = 4A²t/s`; the stiffness of a closed section exceeds that of an open one by orders of magnitude.

**Detail that was not obvious:** the closed cell **does not reach the trailing edge**. The elevon hinge line opens the section, and on a flying wing the elevons occupy almost the whole span. The useful box ends around 72 % of the chord.

Hence the three cells: adding a forward web (D-box) recovers enclosed area where the torque is greatest.

## Consequences

- Requires gyroid infill ([ADR-0028](ADR-0028-gyroid-infill.md)): without it the skin buckles and the closed-section hypothesis does not hold.
- Sets the elevon hinge as a structural boundary, not just an aerodynamic one.

## Associated corrections

- **C7** — it was claimed that the Eliminator evidence at 360 km/h validated printed construction in general. It validates **its** material (almost certainly PLA); with a 40 % lower G, the PETG does not inherit that endorsement.
