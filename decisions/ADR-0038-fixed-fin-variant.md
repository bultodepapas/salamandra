# ADR-0038 — Dual directional configuration: finless baseline + passive twin-fin variant (V1)

**Status:** 🔄 Provisional · **Date:** 2026-08-19 · **Confidence:** Medium `[D]`/`[E]`
**Reversible:** Yes; the two fins and aft booms are additive CORE modules.
**Feeds:** I-20, I-29, G10, F2, E8, O1 and O14.

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
5. **Two aft CORE booms with fixed fins outside the propeller disk.** Retains the existing
   propeller station, separates the fin root loads, and provides a direct wing/CORE load
   path. A Python station sweep selects the first mass-feasible knee at `x_ac = +280 mm`;
   the resulting mass then drives the coupled CG and forward-packaging solve. Accepted
   provisionally.

## Decision

Publish two configurations:

```
SALAMANDRA-CLEAN   Finless O1 efficiency baseline. Directionally unstable by the
                   current analytical band; FC-dependent and not the first-flight default.

SALAMANDRA-V1a     Two identical passive fixed fins, no movable rudder.
                   Each fin: S_v = 1.7368 dm², span 186.4 mm,
                   root/tip chord 128.5/57.8 mm, AR 2.0, taper 0.45,
                   25° leading-edge and 20.379° quarter-chord sweep.
                   Total S_v = 3.4737 dm²; x_ac = +280 mm.
                   Two 18 × 14 mm aft boom envelopes at y = ±140 mm,
                   x = +156…+372.4 mm; 29.4 mm nominal / 13.4 mm residual
                   propeller radial clearance after a 16.0 mm allowance.
                   The dorsal root fillet remains inside the credited planform.
```

The V1a planform is a conventional low-aspect-ratio swept trapezoid. The 0.45 taper avoids
the former needle-like tip, while the 25° leading edge provides a continuous external Ø3 mm
aluminium nose spar. Both trailing-edge vertices are derived from the same trapezoid; no
vertical trailing-edge constraint is imposed. These are engineering choices, not styling cues.

V1a is still a **marginal test configuration**, not a released production geometry. V1b is
the positive-corner alternative if F2 mass closure permits its larger 4.63 dm² total area.

## Consequences and gates

- V1a analytical lower assembly: **59.97 g**, including both fin shells/mounts, both
  leading-edge spars and both carbon booms. The 60.00 g allocation leaves **0.03 g**, so
  measured F2 mass and final root-fillet/saddle mass are mandatory closure items.
- The coupled solution adds **2.40 g** of forward boom/cradle support, moves the battery to
  x = −386.74 mm, camera to x = −463.79 mm and VTX to x = −429.61 mm, and extends the nose
  **17.81 mm**. Resulting AUW is **1615.63 g** and analytical stall speed **44.93 km/h**.
- At 180 km/h, each V1a fin carries an estimated **26.6 N**, with **2.17 N·m** root moment.
  A 3.0 mm solid PETG root gives analytical yield FS **4.45** without spar credit; first
  bending mode is approximately **14.6 Hz**, so structural and flutter testing remain open.
- Estimated parasite-drag increment is **ΔCD0 = +0.0019**, approximately **+13.3%** against
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
