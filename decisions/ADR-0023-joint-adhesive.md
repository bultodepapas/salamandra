# ADR-0023 — Segment joints: tenon + PETG adhesive, area ≥ 3× the skin section

**Status:** 🔄 Provisional · **Date:** 2026-07-28 · **Confidence:** Medium · **Reversible:** Yes
**Research:** [I-04 — Printing materials](../research/I-04-printing-materials.md), [ADR-0032](ADR-0032-modularity.md)

**Article #1 redesign:** `REOPENED` · **Gate:** `M6` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## Context

The wing halves print in segments (ADR-0024) and the panels join the CORE with a
removable joint (ADR-0032). The glued segment joints must transmit bending and torsion
between printed sections; the removable CORE↔PANEL joint must not be glued (panels swap).

## Decision

- **Segment joints (within a panel):** tenon + specific PETG adhesive, bond area
  **≥ 3× the skin section** (guide §7.3). Adhesive: **3D-Gloop PETG or 30-min epoxy**;
  **not E6000** (I-04; correction C9: PETG can be glued — categorical claims rejected).
- **CORE↔PANEL joint:** removable, no adhesive (socket + protruding tube/pin, ADR-0031).

## Consequences

- Bond area rule is the joint's load path: below 3× the skin section, the joint is the
  weak point of the closed shell (G4 discipline).
- The removable joint keeps its R-JOINT ≥ 5× requirement (ADR-0032) via the pin couple,
  not via adhesive.
- Assumption `[I]`: bond area rule derived from structural practice, to be verified in
  F4 (S3/GJ test) and by the first flight.
