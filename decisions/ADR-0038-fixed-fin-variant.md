# ADR-0038 — Dual directional configuration: finless baseline + passive twin-fin variant (V1)

**Status:** ⬜ Superseded for the redesigned Article #1 by
[ADR-0048](ADR-0048-article-1-mission-and-configurations.md); retained as a v0.6 comparison
candidate · **Date:** 2026-08-19 · **Confidence:** Medium `[D]`/`[E]`
**Reversible:** Yes; the two fins and short root supports are additive CORE modules.
**Feeds:** I-20, I-29, I-30, G10, F2, E8, O1 and O14.

> **2026-08-21 reset:** `SALAMANDRA-6S-R` now requires a rudder-capable removable vertical
> interface for first-flight development. The passive V1a geometry below remains useful
> evidence, but is not the v2 directional release.

## Context

SALAMANDRA is a forward-swept flying wing with a centreline pusher propeller and elevons.
The analytical finless directional-stability band is negative:

| Configuration | `Cnβ` total (/deg) | Interpretation |
|---|---:|---|
| CLEAN, no fins | −0.00055 … −0.00141 | Statically unstable across the estimated band |
| V1a, twin fixed fins | −0.00029 … +0.00119; nominal +0.00050 | Marginal screening article; lower uncertainty corner remains open |
| V1b, twin fixed fins | +0.00017 … +0.00173; nominal +0.00100 | Positive independent-corner screen; mass/stall penalties remain open |

The former V1 drawing placed one centreline fin behind the pusher propeller on a notional
carrier. Visual and geometric review found that this architecture did not have a credible
load path: the carrier crossed the propeller plane, the fin root extended 84 mm behind the
body OML, and the source-product manuals had been interpreted incorrectly. Both TBS
reference aircraft integrate their fin structure ahead of, or into, the propulsion support;
neither supports a floating plate behind the propeller.

## Alternatives evaluated

1. **Centre fin ahead of the existing propeller.** The available aerodynamic-centre arm is
   too short. Holding the V1a nominal `Cnβ` target drives the required height to about
   340 mm at the selected aspect ratio. Rejected.
2. **Move the complete propulsion group aft and integrate a centre fin.** A roughly 130 mm
   propulsion translation produces a first-order battery rebalance of about 57 mm forward;
   the V1 battery solution then lies about 61 mm beyond the present forward travel bound.
   Rejected for Article 1.
3. **Wingtip fins.** NASA's X-48B demonstrates wingtip fins on an aft-swept blended wing,
   but SALAMANDRA's forward-swept tips lie forward of the CG and do not provide a robust
   stabilising yaw arm. Rejected for this planform.
4. **Split drag rudders.** They can generate control moment but provide no passive static
   directional stiffness when closed and would make the baseline FC-dependent. Deferred.
5. **Two CORE-rooted fixed fins forward of the propeller hazard.** Retains the immutable
   motor and propeller stations, separates the root loads at y = ±140 mm, and provides a
   direct wing/CORE load path. A Python sweep selects the minimum-mass candidate satisfying
   stability, 250 mm print height, 60 g mass, root support, radial clearance and at least
   8 mm axial residual beyond the inflated propeller hazard. Accepted provisionally.

## Decision

Publish two configurations:

```
SALAMANDRA-CLEAN   Finless O1 efficiency baseline. Directionally unstable by the
                   current analytical band; FC-dependent and not the first-flight default.

SALAMANDRA-V1a     Two identical passive fixed fins, no movable rudder.
                   Each fin: S_v = 3.0718 dm², span 247.9 mm,
                   root/tip chord 170.9/76.9 mm, AR 2.0, taper 0.45,
                   20° leading-edge and 15.064° quarter-chord sweep.
                   Total S_v = 6.1437 dm²; x_ac = +115.5 mm.
                   Two 18 × 14 mm aft root supports at y = ±140 mm,
                   x = +156.0…+216.6 mm; 29.4/13.4 mm nominal/residual
                   radial clearance and 8.33 mm controlling axial residual.
                   Side-view propeller overlap is zero.
                   The dorsal root fillet remains inside the credited planform.
```

The V1a planform is a conventional low-aspect-ratio swept trapezoid. The 0.45 taper avoids
the former needle-like tip, while the 20° leading edge provides a continuous external Ø3 mm
aluminium nose spar. Both trailing-edge vertices are derived from the same trapezoid; no
vertical trailing-edge constraint is imposed. These are engineering choices, not styling cues.

V1a is still a **marginal test configuration**, not a released production geometry. V1b is
the positive-corner alternative if F2 mass closure permits its larger 8.18 dm² total area.

## Consequences and gates

- V1a analytical lower assembly: **48.73 g**, including 35.61 g of LW-PLA-HT
  shells/mounts, 10.07 g of aluminium leading-edge spars and 3.04 g of carbon root
  supports. The 60.00 g allocation leaves **11.27 g**; coupon density/strength and final
  root-fillet/saddle mass remain mandatory F2 items.
- The coupled solution adds no forward support, leaves camera/VTX at −445.98/−418.00 mm,
  and moves only the battery to x = −363.27 mm. Resulting AUW is **1601.98 g** and
  analytical stall speed **44.74 km/h**.
- At 180 km/h, each V1a fin carries an estimated **47.0 N**, with **5.09 N·m** root moment.
  A 3.0 mm root screen gives analytical yield FS **2.52** without spar credit; first
  bending mode is approximately **8.2 Hz**, so structural and flutter testing remain open.
- Estimated parasite-drag increment is **ΔCD0 = +0.0034**, approximately **+23.1%** against
  the clean drag model. CLEAN alone retains the headline O1 efficiency claim.
- V1a's independent lower `Cnβ` corner is still negative. E8 yaw perturbation and decay
  testing is mandatory; the drawing must continue to say `MARGINAL`, not `STABLE`.

## Governing evidence

- `calculations/yaw_stability.py` — single source for area, planform, stability, mass,
  structural screening and validation.
- `calculations/generate_blueprints.py` — generated A3 side and fin-review SVGs.
- `research/I-29-twin-fin-architecture-correction.md` — source review and architecture trade.
- NASA X-48B/X-48C programme: <https://www.nasa.gov/aeronautics/x-48b/> and
  <https://www.nasa.gov/image-article/x-48c-hybrid-blended-wing-body-3/>.
- TBS Chupito and Mojito manuals: <https://www.team-blacksheep.com/media/files/tbs-chupito-manual.pdf>
  and <https://www.team-blacksheep.com/media/files/tbs-mojito-manual.pdf>.
