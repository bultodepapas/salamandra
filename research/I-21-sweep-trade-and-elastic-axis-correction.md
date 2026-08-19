# I-21 — Sweep trade and elastic-axis correction

**Status:** 🔄 **Executed — design selection complete; material tests remain open**
**Date:** 2026-08-17
**Feeds:** ADR-0040, ADR-0003, guide §§3/5/9, OP-01, OP-03, OP-23, OP-29
**Calculation:** [sweep_trade.py](../calculations/sweep_trade.py),
[divergence.py](../calculations/divergence.py),
[balance_cg.py](../calculations/balance_cg.py)

> **v0.3 supersession note:** the −15° sweep and aeroelastic conclusions remain
> controlling. ADR-0041/0043 replace this trade's provisional profile moment, mass and
> battery station with Salamandra r1. Those mass-layout inputs were superseded by
> ADR-0045: the current CLEAN mass is 1553.25 g and the component-layout pack station
> is −337.74 mm. The aerodynamic sweep conclusions are unchanged.

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
The section-Cl screen now uses the **1.59626 kg V1 analytical lower model** at 45 km/h.
Rerunning the full trade after ADR-0045 lowers the selected-case peak section Cl to
0.629 and does not change the sweep selection. V1 analytically closes C16; physical
mass, CLmax and battery travel remain open (OP-24/OP-16).
The full-resolution result is:

| Λc/4 | NP VLM / Weissinger (mm) | Twist / reflex | Peak Cl | 6S1P station (mm) | Extension from tip (mm) | Result |
|---:|---:|---:|---:|---:|---:|---|
| −20° | −101.5 / −98.3 | 2.45° / 0.00° | 0.624 | −399.5 | 367 | Pass |
| −16° | −80.9 / −77.9 | 3.11° / 0.11° | 0.628 | −363.3 | 330 | Pass |
| **−15°** | **−75.9 / −72.9** | **3.33° / 0.33°** | **0.629** | **−354.4** | **321** | **Pass; selected** |
| −12° | −60.9 / −58.1 | 4.22° / 1.22° | 0.632 | −327.7 | 295 | Reject: trim |
| −10° | −51.0 / −48.3 | 5.11° / 2.11° | 0.634 | −309.9 | 277 | Reject: trim |

The selection rule is declared before evaluation: choose the least-negative sweep that
passes all constraints. The result is −15°, not the locally attractive −12° candidate.

## 5. Revised balance and divergence results

At −15°, `balance_cg.py` gives a VLM target CG of −93.8 mm. After ADR-0045, the Article
#1 6S1P P42A component layout balances CLEAN at −337.74 mm inside physical travel.
CLEAN AUW is 1.55325 kg and calculated stall speed is 44.1 km/h. The V1 allocation is
1.58997 kg / 44.6 km/h and C32's connected lower model is 1.59626 kg / 44.7 km/h.
The exact V1 target pack station is 2.72 mm ahead of current travel, although achieved
CG remains inside R-CG; F2 physical closure therefore remains open. Other packs are
future power modules, not Article #1 options.

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
