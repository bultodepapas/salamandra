# ADR-0041 — Salamandra r1 spanwise airfoil family

**Status:** ⬜ Held for flight-wing CAD by ADR-0047; retained as reference/coupon geometry · **Date:** 2026-08-17 · **Confidence:** Medium `[D]` · **Reversible:** Yes, before tooling
**Gaps:** G2 / E2 measured acceptance · **Research:** I-15 §8, I-22

## Context

The v0.2 root candidate was not a valid CAD release profile. Its thickness routine
multiplied every ordinate, which scaled camber and reflex as well as thickness, while
the documentation claimed that the mean line was unchanged. The polar cache also did
not identify the geometry, so a regenerated section could reuse a stale polar. Finally,
the screening used 300k/500k at both stations instead of the actual root/tip Reynolds
envelope. Those errors made the root-only `Cm0` value unsuitable for wing trim.

## Decision

Adopt the generated **Salamandra r1** family as the controlling CAD profile:

| Station | Base mean line | t/c | Additional geometric reflex aft of x/c 0.72 |
|---|---|---:|---:|
| Root | MH60 | 13.5 % | +1.0° |
| Tip | MH60 | 9.0 % | +0.5° |

Thickness is changed about the interpolated mean camber line. Both thickness and reflex
vary linearly between root and tip. The controlling coordinate files are
`geometry/airfoils/salamandra-root-r1.dat`, `salamandra-tip-r1.dat`, and the generated
intermediate station files. Printed twist remains **+3.0° wash-in**.

At the real cruise Reynolds numbers (root 510k, tip 255k), the c²-integrated profile
moment is +0.00326 at Ncrit 10 and +0.00209 at Ncrit 12. At the C32 V1 lower mass,
VLM twist and elevon yields give neutral trim **−0.04° to +0.41°**, inside the ±0.6° cap. Every endpoint
XFOIL case exceeds section `clmax = 1.07`; this is computational evidence, not a
measured stall guarantee.

## Consequences

- OP-02 closes for coordinate generation and CAD; E2 remains the physical acceptance
  gate for lift, drag, moment and stall character.
- OP-03 closes at +3.0° printed wash-in. The old provisional +1.9° adverse elevon
  offset is deleted.
- The root and tip cannot be replaced independently: trim uses their c²-weighted
  moment integral.
- `airfoil_reflex_trade.py` is the only generator. Direct ordinate scaling is forbidden.

## 2026-08-21 review-trigger disposition

The E2/low-speed review condition fired before tooling. The cruise-only `Cm0`
selection does not close the 45 km/h/full-CG trim envelope when section moment
is evaluated at operating `CL` and deflected-section `Cm` is included. ADR-0047
therefore blocks r1 from new flight-wing CAD and selects r2a only for physical
coupon testing. The r1 files remain controlled historical evidence; they are
not silently regenerated or deleted.
