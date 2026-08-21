# ADR-0018 — Reject ABS (UV degradation)

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** High `[M]` · **Reversible:** —
**Research:** [I-04 — Printing materials](../research/I-04-printing-materials.md)

**Article #1 redesign:** `CANDIDATE-ONLY` · **Gate:** `M6` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## Context

ABS **yellows and embrittles in the sun in a few months** `[M]` (I-04). A wing lives
outdoors — on the ground between flights and in the sun during operation. Its surface is
a load-bearing shell (ADR-0002): UV embrittlement attacks the structure itself, not just
the finish.

## Decision

**Reject ABS** as a candidate structural material.

## Consequences

- ASA (the UV-resistant ABS-family alternative) is also rejected in ADR-0021: it warps
  without an active chamber (O3: no active chamber on the P1S class) and its layer
  adhesion is the worst of the family (Z retention 29 % `[M]`, correction C8).
- The base material is PETG (ADR-0021), which combines acceptable UV behaviour with the
  thermal margin the structure needs.
