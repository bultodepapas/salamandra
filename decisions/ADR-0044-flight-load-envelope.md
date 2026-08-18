# ADR-0044 — Separate manoeuvre limits, ultimate loads and gust screening

**Status:** 🔄 Partial — manoeuvre/ultimate basis adopted; dynamic gust closure open  
**Date:** 2026-08-17  
**Confidence:** Medium `[D]`/`[E]`  
**Reversible:** Yes  
**Research:** I-24  
**Verification:** `calculations/flight_envelope.py`, B3 negative-polar extension, E9, F4/S3

## Context

The specification said `+6/−3 g, later +9, gust-dominated` without distinguishing
manoeuvre limit, ultimate structural and gust loads. That ambiguity could make a CAD
designer apply a safety factor twice, omit it entirely, or size the aircraft to a linear
gust result outside the airfoil's usable lift range.

## Decision

1. Retain `+6.0/−3.0 g` provisionally as the Article #1 **manoeuvre limit** loads.
2. Apply a structural ultimate factor of 1.5. The corresponding **ultimate** cases are
   `+9.0/−4.5 g`; `+9 g` is not a future manoeuvre target.
3. Use the calculated positive V-n boundary. `VA` is 109.0 km/h CLEAN and 110.4 km/h
   for the current V1 lower model; at the 105 km/h first-flight limit, positive manoeuvre
   capability is 5.57/5.42 g respectively.
4. Do not publish a negative aerodynamic stall branch until a validated negative-polar
   analysis or section test supplies defensible `CLmin` data; the normal E2 glide polar
   cannot provide it.
5. Treat the legacy Part 23 discrete-gust calculation as a **screen only**. Its full
   reference input exceeds both declared limits and produces a positive linear-lift
   result above `CLmax` at 105 km/h. It is neither an adopted Salamandra design load nor
   a certification claim.
6. A component checked at a limit load must retain at least 1.5 margin to its applicable
   failure value. Printed material/process uncertainty can require an additional special
   factor after coupon and section testing; it is not hidden inside the 1.5 factor.
7. Preserve the C34 coefficient distinction in every envelope calculation: **0.65 is
   the local section `clmax` screen; 0.589 is the released 3-D wing `CLmax`** used for
   aircraft stall, mass acceptance and the manoeuvre boundary.

## Consequences

- Corrections C33/C34 remove the ambiguous phrases `later +9` and global
  `CLmax >= 0.65` throughout the controlling specification.
- F4/S1 is closed for terminology and manoeuvre/ultimate values, but remains open for a
  Salamandra-specific dynamic gust basis.
- F4/S2 is closed only on the positive manoeuvre branch; `CLmin` and the gust envelope
  remain explicit open gates G11/B3-extension/E9.
- Existing +6 g component calculations are now interpretable: the boom (FS 4.96), V1
  fin root (FS 1.67 without spar credit) and filament dowels (FS >10) exceed the base
  1.5 ultimate requirement in their static models. This does not validate the complete
  printed shell, joints, fatigue, flutter or dynamic gust response.
- No geometry, material, 105 km/h first-flight limit or 160 km/h Article #1 V_NE changes.
