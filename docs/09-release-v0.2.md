# Salamandra — Release v0.2.0: Safety-Corrected CAD Baseline

**Date:** 2026-08-17 · **Tag:** `v0.2.0` · **Status:** RELEASED

**Controlling specification:**
[Salamandra Design Guide v0.17](../design/Salamandra-Design-Guide-v0.1.md)

Release v0.2.0 freezes the highest-ROI design audit as a new CAD baseline. It is a
breaking release because the quarter-chord sweep, planform stations, neutral point,
target CG, battery cradle and initial flight limit changed together. The Design Guide is
the primary deliverable: CAD work must begin with it, not with these notes or with a
legacy solid.

This remains a **design package**, not a flight-qualified aircraft. Airfoil closure,
measured mass properties, printed-wing stiffness and elastic-axis tests remain mandatory
before the corresponding CAD and flight gates can close.

---

## 1. Design Guide authority

The released document set is intentionally hierarchical:

1. **Design Guide v0.17** controls CAD dimensions, interfaces, materials, stations and
   assembly requirements.
2. `calculations/design_config.py` is the single numerical source for planform geometry.
3. ADR-0040 and I-21 record why −15° was selected and what would force review.
4. The justification records evidence and derivations; the open-points register records
   everything that is still provisional.

If the guide and generated geometry disagree, stop and report the conflict. Do not
average values. The filename `Salamandra-Design-Guide-v0.1.md` is retained for stable
repository links; its internal released revision is **0.17**.

## 2. Breaking migration from v0.1.0

Do **not** mix v0.1.0 wing sketches, printed panels, CORE wing interfaces or cradle
coordinates with v0.2.0. Regenerate the wing and re-project dependent features.

| Driver | v0.1.0 | v0.2.0 |
|---|---:|---:|
| Quarter-chord sweep | −20° | **−15°** |
| Tip trailing-edge coordinate | contradictory legacy values | **−65.7 mm** |
| VLM neutral point | legacy −20° solution | **−75.8 mm** from root c/4 |
| Target CG | −119 mm | **−93.8 mm** |
| 6S1P P42A station | legacy forward cradle | **−372.7 mm** |
| Cradle limits | legacy geometry | **−473.3…−272.2 mm** |
| Boom + cradle | ≈41 g budget | **38.2 g**, 342 mm extension |
| Initial V_limit | 110 km/h | **105 km/h** |
| V1a fin root | under-sized prior check | **3.0 mm solid minimum** |

Unchanged architectural drivers: span 1300 mm, area 0.282 m², taper 0.50, root/tip
thickness 13.5/9 %, CORE + three segments per half-wing, three-cell section, PETG shell,
panel carbon arrangement and the 6S1P reference configuration.

## 3. Engineering changes released

### 3.1 Coupled sweep selection

`sweep_trade.py --full` evaluates −20/−16/−15/−12/−10° with a 32×5 VLM,
100-station Weissinger cross-check, provisional trim moment, section-Cl screen,
self-consistent balance and a literature-anchored divergence trend. **−15°** is the
least-negative candidate that closes the declared favourable-polar trim cap; −12° needs
1.54° equivalent reflex and is rejected.

The selected case gives VLM/Weissinger neutral points −75.8/−72.9 mm, 0.638 peak
section Cl at the 1.620 kg O1 design target, a −373.1 mm full-trade pack station and an
estimated 15 % relative divergence-speed improvement over −20°.

### 3.2 Aeroelastic safety correction

The previous model incorrectly called the enclosed-cell-area centroid a shear centre.
Revision 3 treats it only as a geometric diagnostic and brackets the unmeasured elastic
axis at xEA/c = 0.30…0.45. Results are 325.3 km/h nominal, **128.8 km/h conservative**
and 91.1 km/h for AERO-PLA wings. The conservative case fails the 240 km/h structural
criterion; first-flight clearance is therefore **105 km/h**, rising to 150 km/h only if
the GXY stiffness model is measured and validated.

### 3.3 Geometry, balance and structure consistency

- `design_config.py` owns span, area, taper, sweep, thickness schedule and stations.
- Target CG is −93.8 mm; only the current one-layer 6S1P arrangement closes the cradle.
- The hybrid aluminium boom is fixed at 38.2 g across printed-material policies.
- Fin calculations now use their calculated 2.16 dm² area throughout. A 2.5 mm root is
  rejected at FS 1.15; the released V1a minimum is 3.0 mm, FS 1.65 without spar credit.
- Elevon trim now uses the computed +0.00249 Cm/° wash-in yield. The favourable polar
  needs ≈0.6° reflex; the adverse Ncrit-12 polar needs ≈1.9° and fails the permanent
  trim cap. Control travel is adequate, but the final airfoil remains a CAD gate.

## 4. Released package

| Artifact | Release version / role |
|---|---|
| [`design/Salamandra-Design-Guide-v0.1.md`](../design/Salamandra-Design-Guide-v0.1.md) | **v0.17 — controlling CAD specification** |
| [`design/Design-Guide-Justification-v0.1.md`](../design/Design-Guide-Justification-v0.1.md) | v0.12 — evidence and derivations |
| [`design/Design-Guide-Open-Points-v0.1.md`](../design/Design-Guide-Open-Points-v0.1.md) | v0.12 — unresolved gates and triggers |
| [`decisions/ADR-0040-quarter-chord-sweep.md`](../decisions/ADR-0040-quarter-chord-sweep.md) | Sweep decision and review conditions |
| [`research/I-21-sweep-trade-and-elastic-axis-correction.md`](../research/I-21-sweep-trade-and-elastic-axis-correction.md) | Primary audit evidence |
| [`calculations/design_config.py`](../calculations/design_config.py) | Canonical geometry source |
| [`calculations/sweep_trade.py`](../calculations/sweep_trade.py) | Reproducible coupled selection |
| [`docs/07-divergence-margin.md`](07-divergence-margin.md) | Divergence revision 3 and operating limit |
| [`CHANGELOG.md`](../CHANGELOG.md) | Complete correction history through 1.29 |

## 5. Verification record

The release audit completed the following checks on 2026-08-17:

- all Python files compile;
- full 32×5 VLM / 100-station Weissinger sweep trade: **ALL PASS**;
- VLM NP −75.8 mm and independent Weissinger NP −72.9 mm: 2.9 mm agreement;
- canonical geometry, balance, mass budget, boom, fin, divergence, launch and dowel
  validation suites: **ALL PASS**;
- divergence FEM/shooting and closed-section reference checks: **ALL PASS**;
- elevon-authority consistency and adverse-polar detection: **ALL PASS**;
- `git diff --check`: clean.

The external XFOIL/B3 campaign was not rerun for this release. Its existing polar band
is deliberately carried as an unresolved input, not promoted to measured evidence.

## 6. Gates that remain open

| Gate | Released state | Closure required |
|---|---|---|
| **Airfoil / trim (OP-02)** | Favourable provisional polar just meets 0.6° reflex; adverse case needs 1.9° | Final calibrated B3 polar and accepted coordinates |
| **Mass / stall (OP-24)** | Current AUW 1685.2 g gives 45.9 km/h, above the 45 km/h requirement | CAD mass properties and verified reduction or requirement change |
| **Divergence (OP-29/30)** | Conservative Vdiv 128.8 km/h; Vlimit 105 km/h | GXY/GJ coupon, complete-wing torsion and elastic-axis measurement |
| **Yaw (OP-26)** | CLEAN estimated unstable; V1a marginal at uncertainty corner | CAD body area, fin coupon/modal check and E8 flight test |
| **CORE outer mold (OP-21)** | Interfaces and envelopes fixed; exterior shape open | CAD integration and mass-property review |

## 7. CAD hand-off checklist

Before editing or accepting a part for v0.2.0:

1. Regenerate the planform from the guide v0.17 station table or `design_config.py`.
2. Confirm the tip trailing edge is −65.7 mm and the local c/4 tip is −174.2 mm in the
   guide coordinate system.
3. Rebuild or re-project every spanwise interface affected by sweep; do not mate a
   v0.1.0 panel to a v0.2.0 CORE.
4. Use target CG −93.8 mm and the released cradle limits; verify the physical 6S1P pack.
5. Keep twist and airfoil externally parametric. Do not freeze the adverse 1.9° reflex
   case into geometry.
6. Enforce the 3.0 mm V1a fin-root minimum if the fixed-fin variant is built.
7. Mark drawings, exports and slicer projects `SALAMANDRA-v0.2.0`; reject unversioned
   geometry at review.

Release v0.2.0 is ready for CAD work within these gates. It is not authorization to fly
above 105 km/h or to treat estimated printed-material properties as measured values.
