# ADR-0045 — Shorten the Article #1 elevons to 35–90 % half-span

**Status:** 🔄 Provisional — in force for Article #1 CAD; physical closure open  
**Date:** 2026-08-18  
**Confidence:** Medium `[D]`/`[E]`/`[I]`  
**Reversible:** Yes, before tooling  
**Related gaps:** OP-06, F2, E2, E5, G7  
**Supporting research:** [I-27](../research/I-27-elevon-geometry-trade.md)

## Context

The v0.4 elevon ran from y = 195 to 585 mm. Its inner hinge termination coincided
with the removable CORE/PANEL joint even though the first 32.5 mm contributed little
roll leverage and complicated the panel-root trailing edge. The project also lacked a
documented comparison against shorter, tip-extended and different-chord alternatives.

## Alternatives considered

| Option | For | Against | Disposition |
|---|---|---|---|
| Retain 30–90 %, 0.28 c | Maximum continuity with v0.4 | Hinge begins at removable joint; unnecessary moving area | Superseded for Article #1 |
| **35–90 %, 0.28 c** | Retains 94.5 % roll derivative; closes trim; fixed root bridge and tip | Still requires physical validation | **Selected** |
| 40–90 %, 0.28 c | Lower moving area and hinge load | Greater roll-authority loss before E2 | Deferred |
| 35–95/100 %, 0.28 c | More pitch and roll authority | Tip Reynolds, damage, inertia and aeroelastic exposure; authority not needed | Deferred |
| 35–90 %, 0.24 c | Lower hinge load and mass | Ncrit-12 trim too near ±0.6° after ideal assumptions | Rejected for first prototype |
| 35–90 %, 0.32 c | More authority | Higher load, drag and mass without a demonstrated need | Rejected for first prototype |

## Decision

Article #1 shall use one separate elevon per half-wing from **y = 227.5 to 585.0 mm
(35–90 % half-span), 357.5 mm long**, with constant **0.28 c** chord and the existing
**x/c = 0.72** hinge. One DS-939MG servo remains at elevon midspan,
**y = ±406.25 mm**. The panel trailing edge is fixed from y = 195 to 227.5 mm and the
outer 65 mm tip remains fixed.

Mass balance to the measured hinge axis and zero-freeplay linkage remain mandatory.
No flap/flaperon mode, final throw or flutter credit is authorized by this ADR.

## Rationale

The connected 80×6 rigid VLM gives the selected surface 0.3275/rad differential roll
derivative, 94.5 % of the retired surface, and Ncrit-12 neutral trim of +0.500° `[D]`.
Moving area falls 10.0 % and the hinge proxy falls 11.7 %. The factored 180 km/h static
servo requirement becomes 1.643 kgf·cm, giving the 2.5 kgf·cm DS-939MG 1.52× margin
`[D]`/`[E]`. The fixed root bridge is expected to simplify the removable-joint trailing
edge `[I]`.

## Consequences

- The moving PETG estimate becomes 45 g total and the conservative balance allocation
  becomes 54 g total. Because the removed moving PETG becomes fixed panel material,
  only 6 g of balance mass is credited to AUW.
- Current analytical results are 1553.25 g CLEAN and 1615.63 g coupled V1 after the I-30 fin/packaging correction.
- The coupled V1 solver extends the forward travel 17.81 mm, adds 2.40 g of support and
  recovers exact target xCG at battery x = −386.74 mm. F2 must verify that analytical
  envelope and the measured mass/stiffness; physical closure is not claimed.
- Existing 390 mm elevon CAD, hinge strips, servo stations, balance values and drawings
  are obsolete for Article #1 and must not be mixed with this decision.
- Drawing SLM-WNG-001 remains a generated review sheet marked
  **DRAFT — NOT FOR MANUFACTURE**.

## Review conditions

Reconsider span or chord if E2 shows inadequate pitch/roll authority, unacceptable
stall behavior or hinge-gap loss; if E5/G7 shows inadequate stiffness, freeplay or
modal margin; or if F2 cannot package and balance the selected surface. Any extension
to 95/100 % span or any flap schedule requires its own aerodynamic and aeroelastic
review.
