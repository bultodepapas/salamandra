# ADR-0022 — Carbon veil ±45° over the skin

**Status:** ❌ **CANCELLED** · **Cancellation date:** 2026-07-28

**Article #1 redesign:** `CANCELLED` · **Gate:** `—` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## What it proposed

Lay up 80 g/m² carbon fabric at ±45° over the inner 60 % of the half-span, continuous over the joints between segments.

## Why it was proposed

It solved **two problems at once**:

1. **Torsional stiffness.** A 0.12 mm layer cured at ±45° provides G·t ≈ 2.0 kN/mm versus 0.50 for 0.9 mm of PETG. It multiplied GJ by ~4 with 60–90 g.
2. **Joints.** A continuous layup over the splices turns the glued joint into a **laminated splice**: the adhesive positions, the fiber carries the torque.

## Why it is cancelled

**Project decision**, aligned with objective O5 (ease of manufacturing): wet layup introduces a manual skill, curing time and a consumable that the rest of the project does not need.

Concurrent technical reasons:

- **The veil is an RF screen.** The GPS antenna cannot sit under the layup; it forced a window in the fabric or externalizing the module.
- It prevents repair by segment reprinting (O7).

## What takes its place

| Path | Effect on V_div | Mass |
|---|---|---|
| t/c 11 % → 13.5 % | ×1.18 | +30 g |
| Gyroid infill ([ADR-0028](ADR-0028-gyroid-infill.md)) | Prevents skin buckling | +40 g |
| Second shear web (three cells) | ×1.12 | +40 g |

Net cost versus the veil: ~+35 g. Accepted.

## Consequences of the cancellation

- **ADR-0025 (elevon mass balancing) becomes non-negotiable.** Without the veil, ω_α drops and approaches the servo modes.
- **G6 rises in priority**: with less absolute margin, narrowing the sweep factor matters more.
- The GPS–carbon conflict disappears. 100 % plastic wing = RF-transparent everywhere.

## Reconsideration conditions

If E7 measured a divergence below criterion and the plastic remedy came out too heavy, the veil returns to the table as the minimum-mass solution.
