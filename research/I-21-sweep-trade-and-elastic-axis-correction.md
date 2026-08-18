# I-21 — Sweep trade and elastic-axis correction

**Status:** 🔄 **Executed — design selection complete; material tests remain open**
**Date:** 2026-08-17
**Feeds:** ADR-0040, ADR-0003, guide §§3/5/9, OP-01, OP-03, OP-23, OP-29
**Calculation:** [sweep_trade.py](../calculations/sweep_trade.py),
[divergence.py](../calculations/divergence.py),
[balance_cg.py](../calculations/balance_cg.py)

> **v0.3 supersession note:** the −15° sweep and aeroelastic conclusions remain
> controlling. ADR-0041/0043 replace this trade's provisional profile moment, mass and
> battery station with Salamandra r1, 1559.25 g CLEAN and component-layout x_pack = −341.3 mm.

## 1. Questions

1. What quarter-chord forward sweep gives the best aeroelastic and packaging return
   without exhausting the tailless wing's trim authority?
2. Does the previous section calculation actually locate the elastic/shear axis?
3. What operational speed follows from the conservative unmeasured structure?

## 2. Audit correction: enclosed-area centroid is not a shear centre

The previous script calculated the centroid of the three enclosed cell areas and called
it the shear centre. That is not a valid shear-centre solution for a closed multicell
section. The elastic axis depends on wall-by-wall geometry and shear stiffness, cell
compatibility and the bending/torsion coupling of the actual laminate/printed shell.

The script now reports that point only as a **geometric cell-area-centroid diagnostic**:
`x/c = 0.353`. It brackets the elastic axis explicitly as:

| Case | xEA/c | Aerodynamic-arm e/c = 0.25 − xEA/c |
|---|---:|---:|
| Optimistic | 0.30 | −0.05 |
| Nominal | 0.35 | −0.10 |
| Conservative | 0.45 | −0.20 |

These remain `[E]`; a torsion test and a load/deflection elastic-axis measurement are
required. No design claim now identifies the area centroid with the shear centre.

## 3. Primary aeroelastic evidence

NASA TP-1685, *Subsonic aerodynamic characteristics of several forward-swept-wing
configurations* (NASA Langley, 1980), tested and calculated forward-swept wings at aspect
ratios 4 and 8 and sweep magnitudes from 0° to 30°. Its figures 7 and 8 show the same
robust trend for both aspect ratios: reducing the magnitude of forward sweep increases
divergence dynamic pressure/speed. The report is available from
[NASA NTRS](https://ntrs.nasa.gov/citations/19800020786).

This source justifies the **ranking**, not direct numerical scaling. Geometry, stiffness,
material anisotropy, Reynolds number and construction differ. The trade therefore marks
the relative speed factors (1.00 at −20°, 1.15 at −15°, 1.23 at −12°) as `[E]` digitised
engineering bounds and keeps E7 as the closing experiment.

## 4. Reproducible coupled trade

Run from `calculations/`:

```powershell
python sweep_trade.py --full
```

Fixed inputs: span 1.300 m, area 0.282 m², taper 0.50, 3.0° printed-twist cap,
0.6° permanent-reflex cap, target static margin 8 % MAC and section-Cl ceiling 0.65.
The section-Cl screen originally used the **1.620 kg O1 allocation target** at 45 km/h.
The connected C32 V1 lower model is now 1.62651 kg; rerunning the selected case changes
peak section Cl only to 0.639 and does not change the sweep selection. V1 nevertheless
remains non-compliant with its mass/stall requirement (OP-24).
The full-resolution result is:

| Λc/4 | NP VLM / Weissinger (mm) | Twist / reflex | Peak Cl | 6S1P station (mm) | Extension from tip (mm) | Result |
|---:|---:|---:|---:|---:|---:|---|
| −20° | −101.5 / −98.3 | 2.64° / 0.00° | 0.633 | −420.9 | 389 | Pass |
| −16° | −80.9 / −77.9 | 3.35° / 0.35° | 0.637 | −382.5 | 351 | Pass |
| **−15°** | **−75.9 / −72.9** | **3.59° / 0.59°** | **0.638** | **−373.1** | **342** | **Pass; selected** |
| −12° | −60.9 / −58.1 | 4.54° / 1.54° | 0.641 | −344.8 | 313 | Reject: trim |
| −10° | −51.0 / −48.3 | 5.50° / 2.50° | 0.643 | −326.0 | 294 | Reject: trim |

The selection rule is declared before evaluation: choose the least-negative sweep that
passes all constraints. The result is −15°, not the locally attractive −12° candidate.

## 5. Revised balance and divergence results

At −15°, `balance_cg.py` gives a VLM target CG of −93.8 mm. After ADR-0043, the Article
#1 6S1P P42A pack balances at −341.3 mm inside its −372.8 to −337.6 mm travel.
CLEAN AUW is 1.55925 kg and calculated stall speed is 44.1 km/h. The
V1 allocation is 1.6202 kg / 45.0 km/h, while C32's connected lower model is
1.6265 kg / 45.1 km/h and remains open at F2. Other packs are future power modules,
not Article #1 options.

`divergence.py` revision 4, using the released r1 section, gives:

| Case | Divergence speed | Interpretation |
|---|---:|---|
| Nominal | 327.2 km/h | Sensitivity reference only |
| Conservative, unmeasured baseline | 129.6 km/h | Governing pre-test case |
| Optimistic | 852 km/h | Non-design case |
| Conservative + Gxy plane | 180.0 km/h | Conditional on coupon validation |
| Conservative + Gxy + gyroid + 1.1 mm wall | 207 km/h | Still below the 240 km/h structural target |

The computed clearance is 0.85 × 129.6 = 110.2 km/h, rounded downward to 110 km/h.
The released initial limit remains **105 km/h** conservatively. If the Gxy-plane coupon
validates that stiffness model, 0.85 × 180.0 = 153.0 km/h, rounded down to **150 km/h**.

## 6. What is decided and what remains open

**Decided:** canonical −15° quarter-chord sweep; one geometry source; VLM balance target;
105 km/h initial speed gate; no shear-centre claim from cell-area geometry.

**Open:** final airfoil moment and stall polars, printed coupon Gxy, complete-wing GJ,
elastic-axis measurement, mass-property measurement and flight Southwell expansion.
The 240 km/h divergence criterion remains unmet in the conservative model; CAD detail
must not erase that result by choosing a favourable uncertainty case.
