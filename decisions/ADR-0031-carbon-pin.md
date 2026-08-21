# ADR-0031 — Carbon pin in the CORE↔PANEL joints

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** High · **Reversible:** Yes
**Feeds:** guide §7.2/§7.3, [ADR-0032](ADR-0032-modularity.md) (R-JOINT)

**Article #1 redesign:** `CANDIDATE-ONLY` · **Gate:** `M6` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## Context

A single tube transmits bending but leaves torsion to the sleeve fit of the removable
CORE↔PANEL joint. R-JOINT (ADR-0032) requires joint torsional stiffness ≥ 5× the
adjacent section; a sliding-fit sleeve cannot guarantee that.

## Decision

**Two pins per joint, acting as a force couple** (guide §7.2/§7.3):

- Main spar tube: pultruded carbon **Ø12 × 1.0 mm**, at x/c = 0.25 (the c/4 line);
- **Anti-rotation pin: solid carbon Ø6 mm, 65 mm aft of the tube axis** (arm 65 mm —
  the mid-value of the 60–80 mm band, ADR-0032);
- Socket bores Ø12.2–12.4 / Ø6.1–6.2 mm (sliding fit), depth ≈ 70 mm;
- Tube and pin bonded **inside the PANEL** (continuous adhesive, ADR-0015 §3.3),
  protruding ≈ 70 mm into the CORE sockets **without adhesive** (removable joint).

## Consequences

- The couple's arm enters the stiffness linearly: a 65 mm arm at y = 195 (30 %
  half-span, where the torque has already fallen to half) delivers the R-JOINT ≥ 5×
  requirement with a removable joint.
- Physical lengths: tube ≈ 485 mm, pin ≈ 140 mm (C27; cut lengths confirmed on CAD).
- The pin is the modularity enabler: panels swap without touching the torsion path.

## Trade study 2026-08-06 — printer filament as pin material (rejected)

Proposal evaluated (community/user): replace the carbon Ø6 pin with a piece of
3D-printing filament (PETG/PLA, Ø1.75). Reproduction: `joint_pin_trade.py` (five
validation cases, ALL PASS).

| Check | Result |
|---|---|
| **Strength** (F = T/arm = 2.3–15.4 N `[E]`) | Filament passes: shear FS ≈ 4.7 (PETG) / 6.3 (PLA); bearing ≈ 5 MPa on the printed socket |
| **Stiffness** (the binding requirement) | E·I: carbon Ø6 = **7.63 N·m²** vs PETG filament = **0.0009 N·m²** → **≈ 9000× softer**. With identical sockets/arm/loads, k_joint ∝ E·I |
| **R-JOINT consequence** | k_joint drops from ≥ 5× to ≈ 0.005× section → the joint becomes the torsion weak point → **−29 % V_div** (ADR-0032 penalty table), on a forward-swept wing whose dominant risk is aeroelastic divergence (I-05) |
| **Printed-PETG alternatives** | Tenon Ø8 → 5 % of the carbon stiffness; Ø10 → 12 %; **Ø17 needed for parity** (≈ 40 g vs 6.3 g) — worse than carbon on every axis |
| **Cost/complexity** | Carbon Ø6 × 140 mm ≈ €0.25–0.50 and 6.3 g per pin; the socket (bore, embedment, sliding fit) is identical for any pin — **filament saves ≈ €1 per aircraft and changes no complexity** |

**Conclusion: rejected with numbers.** Strength was never the binding requirement; the
couple's function is torsional *stiffness*, and filament delivers 0.01 % of the carbon's
flexural stiffness. Losing 29 % of the divergence margin is not purchasable for ≈ €0.5.
The Ø6 carbon pin stands (this ADR).
