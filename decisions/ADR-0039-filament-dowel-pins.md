# ADR-0039 — Filament dowel pins in the glued segment joints

**Status:** ✅ Active · **Date:** 2026-08-06 · **Confidence:** High (strength `[D]`/`[E]`)
**Reversible:** Yes (print-time detail, no structural requirement changes)
**Research:** [joint_pin_trade.py](../calculations/joint_pin_trade.py) (context),
[filament_dowel_pins.py](../calculations/filament_dowel_pins.py) (this decision)
**Feeds:** guide §7.3/§7.4/§12, ADR-0023, ADR-0024

## Context

The glued segment joints (y = 347 and 498 mm, ADR-0024) are aligned by the tenon and
bonded per ADR-0023 (area ≥ 3× the skin section). Two assembly issues remain: the faces
can shear-slip during glue cure (a misaligned joint is a stress concentration on the
bond), and the bond is the only shear load path. Community proposal: use pieces of
3D-printer filament (Ø1.75 mm PETG/PLA scraps) as **dowel pins** in the joint faces.

> **Boundary (important):** this does NOT replace the carbon Ø6 anti-rotation pin of the
> CORE↔PANEL torque couple (ADR-0031) — that couple's function is torsional *stiffness*,
> where filament fails by ≈ 9000× (`joint_pin_trade.py`). The dowels act only in the
> **glued** segment joints, where the requirement is alignment + shear redundancy.

## Decision

**Every glued segment joint carries 2 × Ø1.75 mm filament dowels** (8 dowels per
aircraft):

| Parameter | Value |
|---|---|
| Pin | 3D-printer filament **Ø1.75 mm**, **PETG preferred** (scraps, same spool; PLA acceptable but brittle in shear) |
| Length | **20–22 mm** (embedment ≥ 10 mm per side) |
| Position on the joint face | **x/c = 0.40 and 0.60**, section mid-plane z = 0 — clear of the carbon tube (x/c 0.25 ± Ø12) and of the hinge cell (≥ 0.72 c); verified at both stations |
| Hole | **Ø1.8–1.9 mm** (sliding fit, 0.05–0.15 clearance), printed with a **solid collar Ø8 × 4 mm** (4+ perimeters) around the bore — bearing material in the 5 % gyroid infill |
| Bond | Dab of the ADR-0023 PETG adhesive on **one side**; the other side free (alignment during assembly) |
| Function | 1. **Alignment** (primary, `[I]`: prevents shear slip during glue cure — alignment IS strength); 2. **shear redundancy** (additive; the ADR-0023 bond remains the primary load path) |

The CORE↔PANEL removable joint carries **no** dowel: its alignment is the carbon
tube+pin couple, and its sockets are sliding-fit by design (ADR-0031/0032).

## Rationale `[D]` (filament_dowel_pins.py, five validation cases, ALL PASS)

| Check | Result |
|---|---|
| Shear demand at +6 g, V_NE | y = 347: ≈ 27 N `[E]` band 20–35; y = 498: ≈ 12 N `[E]` band 7–17 |
| Capacity, 2 dowels, double shear, PETG | ≈ 293 N → **FS ≈ 11** (y = 347) / **24** (y = 498) — redundancy, not primary |
| Bearing on the solid collar | 5 MPa (FS ≈ 10 vs PETG yield) |
| Mass | **2.6 g** per aircraft (pins + collars) — inside the 20 g hardware allowance; ≈ 0.15 % of AUW |
| Cost | **Zero** (filament scraps) |
| Position conflicts | None (tube, hinge cell, pitot channel clear — verified at both stations) |

The alignment benefit itself is `[I]` (standard joinery practice): a joint that cannot
slip during cure bonds at full contact area and without peel stress concentrations.

## Consequences

- Assembly (guide §12): clean the collars, dab adhesive on one side, slide the faces
  together — the dowels hold alignment until the glue cures; no clamps needed for
  alignment (clamps still recommended for pressure).
- CAD: print the two holes + collars in each segment joint face (both mating faces);
  the collars add ≈ 0.25 g and negligible print time per joint (inside O5).
- The ADR-0023 bond-area rule is **unchanged** (dowels are additive; the holes sit in
  the infill with solid collars, they do not cut the skin bond area).
- First-print verification: hole Ø1.8–1.9 sliding fit across two parts — tolerance
  check at the M3 assembly step (OP-27).
- Same practice applies to any new glued interface (e.g. the V1 fin root: 1× dowel +
  screw, guide §5.4).
