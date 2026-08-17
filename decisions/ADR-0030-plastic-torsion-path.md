# ADR-0030 — Plastic torsion path as base; carbon torsion tube as option B

**Status:** 🔄 Provisional · **Date:** 2026-07-28 · **Confidence:** Medium · **Reversible:** Yes
**Research:** [I-05 — Divergence and flutter](../research/I-05-divergence-flutter.md),
[I-21 — sweep/elastic-axis correction](../research/I-21-sweep-trade-and-elastic-axis-correction.md),
[ADR-0015](ADR-0015-carbon-non-torsional.md)

## Context

Torsional stiffness is the project's dominant risk (divergence, G4/G6). ADR-0015 assigns
torsion to the **closed printed shell**, not to the carbon. Two structural paths exist:
the plastic path (closed three-cell shell, ADR-0002/ADR-0028) and a braided carbon
torsion tube added to the bending tube.

## Decision

- **Base path: the plastic closed shell carries torsion** (guide §7.2: torsion carried by
  the closed shell, not the carbon — ADR-0015, C11).
- **Option B (documented, not used in v0.2):** braided torsion tube — kept as the remedy
  if the shell's real GJ under-delivers (G4 is `[E]` ±35 %, anchored to a measured
  reference).

## Consequences

- **Correction (2026-08-17): the shell-alone criterion is not demonstrated.** Revision 3
  gives 325.3 km/h nominal but only 128.8 km/h at the conservative unmeasured end versus
  240 km/h required. The base structural architecture remains provisional; it is not a
  speed-clearance claim. Option B must be sized if S3 confirms insufficient GJ.
- G4/G6 remain the declared weakest links; validation: E5 (FFT) and E7 (Southwell in
  flight), plus the S3 GJ/EI verification on the real section (docs/05).
