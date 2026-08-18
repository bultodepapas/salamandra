# Salamandra — Release v0.3.0: Airfoil, Propulsion Boundary and Mass Allocation

**Date:** 2026-08-17 · **Tag:** `v0.3.0` · **Status:** RELEASED

**Controlling specification:**
[Salamandra Design Guide v0.20](../design/Salamandra-Design-Guide-v0.1.md)

Release v0.3.0 addresses three highest-return design uncertainties left by v0.2.0:
the CAD airfoil family, the propulsion power boundary and the Article #1 mass/stall
allocation. Each correction is backed by a reproducible calculation and propagated
through the Design Guide, justification, open-points register, ADRs and research log.

> **Post-release corrections C29–C34 (17 August 2026):** the original v0.3 propulsion
> row assigned the full O1 battery budget to the motor and called the resulting
> propeller point an aircraft equilibrium without an aircraft drag input. Guide v0.20
> reserves avionics/FPV/BEC power and publishes a power/drag boundary instead. The same
> audit corrects a factor-1000 servo-torque unit label and the dimensionalization of yaw
> damping. C32 also finds that the old 36.72 g V1 fin row omitted its mandatory 5.70 g
> aluminium spar: the connected V1 lower model is 1626.5 g / 45.1 km/h, so F2 mass
> closure is reopened. C33 then separates the provisional +6/−3 manoeuvre limits from
> their +9/−4.5 ultimate structural cases and opens the nonlinear dynamic-gust gate G11;
> C34 separates local section `clmax = 0.65` from wing design `CLmax = 0.589`.
> The corrected values below supersede the tagged narrative.

This is a **design release**, not a flight-qualified aircraft. The r1 sections still
require E2 physical polar/stall acceptance, the mass allocation requires F2 CAD and
scale verification, and the initial 105 km/h limit remains until S3/E7 close the
printed-wing torsion/elastic-axis uncertainty and G11/E9 close dynamic gust response.

---

## 1. Authority and migration rule

The released document hierarchy is:

1. **Design Guide v0.20** controls CAD geometry, interfaces, materials, stations and
   acceptance limits.
2. `calculations/design_config.py` controls planform numbers; the generated Salamandra
   r1 DAT files control profile coordinates.
3. ADR-0041…0044 record the v0.3 decisions and post-release load-envelope correction.
4. I-15 §8, I-22…I-24 record the correction evidence; the open-points register records
   the remaining physical gates.

Do not average conflicting values. Do not combine the v0.2 provisional profile,
battery station or component budget with v0.3 geometry. The stable Design Guide
filename is retained; its current post-release revision is **0.19**.

## 2. Why these three changes have the highest ROI

| Priority | Defect closed | Return |
|---:|---|---|
| 1 | Thickness scaling changed the mean line and cached polars could survive geometry changes | Prevents manufacturing an aerodynamically different wing from the documented one; supplies final CAD station coordinates |
| 2 | Propeller peak efficiency was used as the cruise command without enforcing the total-power budget or measured aircraft drag | Removes the energy-allocation contradiction and turns an unsupported equilibrium claim into a falsifiable E2 drag limit |
| 3 | The released mass missed the stall requirement and used unselected/heavy equipment assumptions | Closes the 45 km/h allocation in PETG and re-solves the coupled battery station and boom |

## 3. Engineering changes

### 3.1 Salamandra r1 spanwise airfoil family

The corrected pipeline changes thickness about the interpolated mean camber line,
hashes geometry and solver settings into the XFOIL cache, fits moment only on the
pre-stall branch, and evaluates the real local Reynolds envelope.

The released family is:

| Station | Mean line | t/c | Added reflex aft of x/c 0.72 |
|---|---|---:|---:|
| Root | MH60 | 13.5 % | +1.0° |
| Tip | MH60 | 9.0 % | +0.5° |

Thickness and reflex interpolate linearly along the half-span. With +3.0° printed
wash-in, the c²-integrated XFOIL/VLM solution gives −0.04°/+0.41° neutral elevon over
Ncrit 10/12, within the ±0.6° design cap. Endpoint section clmax is at least 1.076 in
the computational envelope. These are `[D]` results; E2 remains the measured closer.

Controlling coordinate files:

- `salamandra-root-r1.dat` and `salamandra-tip-r1.dat`;
- intermediate stations y = 130, 195, 325, 347, 488, 498 and 585 mm;
- raw accepted endpoint polars and metadata in `calculations/xfoil_out/`.

### 3.2 Propulsion power/drag boundary

At O1, 95 km/h × 1.15 Wh/km gives **109.25 W total battery power**. Article #1 avionics,
O4 Lite and BEC losses require **14.04 W**, leaving **95.21 W** for motor+ESC.
Interpolation of the measured UIUC APC E 8×8 curve, with motor+ESC efficiency 0.85,
then gives:

| Quantity | Corrected O1 boundary |
|---|---:|
| Advance ratio J | **0.923** |
| Propeller speed | **8,443 rpm** |
| Maximum allowable aircraft drag | **2.06 N** |
| Propeller efficiency | **0.671** |
| Shaft / motor electrical power | **80.9 / 95.21 W** |
| Total battery power | **109.25 W** |
| Aerodynamic acceptance | **CD ≤ 0.01711; CLEAN L/D ≥ 7.55** |

The efficient boundary band is J 0.917–0.933, 8,347–8,499 rpm and 1.91–2.14 N. The
former peak-efficiency point, J = 0.762, would require approximately 230 W and 5.46 N
and is therefore not the O1 cruise command. More importantly, no unique equilibrium
exists until E2 supplies aircraft drag at 95 km/h; `propulsion_match.py --drag-n ...`
performs that closure.

Article #1 is **6S1P, 500–550 Kv, APC E 8×8**. The required rpm is 71–78 % of nominal
no-load speed. A 4S installation needs approximately **713 Kv** at an assumed 80 % loaded
ratio and is a separate power module. The 8,443 rpm point has 2.22× margin to APC's
published 18,750 rpm Thin Electric limit. D2 bench data and E3 flight energy remain
the hardware/mission acceptance tests.

### 3.3 Article #1 mass, stall and CG allocation — C32 status

Conventional PETG is retained. The Article #1 defaults are a ≤550 g PETG shell,
SpeedyBee F405 WING FC+PDB, DJI O4 Lite, four Corona DS-939MG servos and a 25 g APC
E 8×8 assembly. The allocation results are:

| Configuration | AUW | Wing loading | Predicted stall | Exact mass margin to 45 km/h |
|---|---:|---:|---:|---:|
| SALAMANDRA-CLEAN | **1,583.5 g** | 56.2 g/dm² | **44.5 km/h** | 36.9 g |
| SALAMANDRA-V1 allocation target | **≤1,620.2 g** | 57.5 g/dm² | **45.0 km/h** | 0.2 g |
| SALAMANDRA-V1 lower model (C32) | **1,626.5 g** | 57.7 g/dm² | **45.1 km/h — FAIL** | **−6.1 g** |

The exact mass ceiling is 1,620.4 g. The original 36.72 g complete-fin allocation
omitted the selected 5.70 g aluminium spar. The current lower model is 37.31 g for the
PETG shell/mount plus the spar, or 43.01 g total. F2 must save/compensate at least
6.3 g before V1 meets its allocation; otherwise E2 must justify a different CLmax. The coupled
balance solution moves the 6S1P pack to **x = −359.6 mm**, uses an approximate
−460…−259 mm cradle and a **327 mm** structural support span. The hybrid boom becomes
37.4 g and passes the exact multi-load two-support +6 g check at **56 MPa, FS 4.96,
1.7 mm deflection and 31.4 Hz**.

## 4. Breaking v0.2.0 → v0.3.0 migration

The −15° planform, neutral point, target CG and 105 km/h initial limit do not change.
The following dependent data do:

| Driver | v0.2.0 | v0.3.0 |
|---|---:|---:|
| Profile | provisional scaled candidate | **Salamandra r1 station DAT family** |
| Printed wash-in / neutral trim | +3.0° / adverse +1.9° provisional reflex | **+3.0° / −0.04°…+0.41° elevon** |
| Cruise propeller command | peak η, J ≈ 0.762 / ≈9,900 rpm | **power/drag boundary J 0.923 / 8,443 rpm / D ≤2.06 N** |
| Article #1 electrical architecture | pack options not closed | **6S1P, 500–550 Kv** |
| CLEAN / V1 AUW | 1,685.2 / 1,722–1,747 g | **1,583.5 / 1,626.5 g lower model**; target ≤1,620.2 g open |
| 6S1P pack station | −372.7 mm | **−359.6 mm** |
| Cradle | −473.3…−272.2 mm | **approximately −460…−259 mm** |
| Boom assembly / support span | 38.2 g / 341 mm | **37.4 g / 327 mm** |

Any existing v0.2 wing loft must be regenerated from the r1 coordinates. Any v0.2
cradle or forward support must be re-positioned. Do not modify the unchanged planform
station coordinates while making those updates.

## 5. Released package

| Artifact | Release role |
|---|---|
| [`design/Salamandra-Design-Guide-v0.1.md`](../design/Salamandra-Design-Guide-v0.1.md) | **v0.20 controlling CAD specification** |
| [`design/Design-Guide-Justification-v0.1.md`](../design/Design-Guide-Justification-v0.1.md) | v0.15 evidence and derivations |
| [`design/Design-Guide-Open-Points-v0.1.md`](../design/Design-Guide-Open-Points-v0.1.md) | v0.15 remaining gates and triggers |
| [`decisions/ADR-0041-salamandra-r1-airfoil-family.md`](../decisions/ADR-0041-salamandra-r1-airfoil-family.md) | Profile-family decision |
| [`decisions/ADR-0042-cruise-propulsion-equilibrium.md`](../decisions/ADR-0042-cruise-propulsion-equilibrium.md) | Propulsion operating-point decision |
| [`decisions/ADR-0043-article-1-mass-allocation.md`](../decisions/ADR-0043-article-1-mass-allocation.md) | Mass/stall/CG allocation |
| [`decisions/ADR-0044-flight-load-envelope.md`](../decisions/ADR-0044-flight-load-envelope.md) | Manoeuvre-limit, ultimate-load and gust-screening decision |
| [`research/I-22-high-roi-v0.3-audit.md`](../research/I-22-high-roi-v0.3-audit.md) | Ranked audit and correction evidence |
| [`research/I-23-calculation-system-integration-audit.md`](../research/I-23-calculation-system-integration-audit.md) | Cross-module audit, corrections C29–C32 and verification contracts |
| [`research/I-24-flight-load-envelope.md`](../research/I-24-flight-load-envelope.md) | Positive V-n branch, ultimate-load correction and gust-screening evidence |
| [`calculations/airfoil_reflex_trade.py`](../calculations/airfoil_reflex_trade.py) | r1 generator and XFOIL envelope |
| [`calculations/propulsion_match.py`](../calculations/propulsion_match.py) | Propeller O1 boundary and optional E2-drag equilibrium solve |
| [`calculations/mass_budget.py`](../calculations/mass_budget.py) | Binding allocation and options |
| [`calculations/verify_calculations.py`](../calculations/verify_calculations.py) | Cross-module consistency and deterministic-suite runner |
| [`calculations/flight_envelope.py`](../calculations/flight_envelope.py) | Manoeuvre and gust-reference envelope with validation |
| `geometry/airfoils/README.md` | Released CAD coordinate family and provenance |

## 6. Reproduction and release verification

```bash
python3 calculations/verify_calculations.py
python3 calculations/verify_calculations.py --all-scripts
python3 calculations/airfoil_reflex_trade.py --xfoil /path/to/xfoil.exe
python3 calculations/elevon_authority.py
python3 calculations/propulsion_match.py
python3 calculations/mass_budget.py --config all
python3 calculations/balance_cg.py
python3 calculations/boom_flexion.py
python3 calculations/launch_speed.py
python3 calculations/sweep_trade.py --full
python3 calculations/ventana_torsion.py
python3 calculations/yaw_stability.py
python3 calculations/filament_dowel_pins.py
```

The release audit completed successfully: all calculation modules compiled; every
validation above reported **ALL PASS**; the r1 coordinate hashes matched their polar
metadata; the wiki strict-link check and production build passed; and
`git diff --check` was clean.

## 7. Gates that remain open

| Gate | v0.3 design state | Closure required |
|---|---|---|
| **Airfoil physical acceptance (G2/E2)** | r1 CAD coordinates and computational trim closed | Printed-section/aircraft lift, drag, moment and stall measurements |
| **Mass (F2/OP-24)** | CLEAN 1583.5 g closes; V1 lower model 1626.5 g exceeds the 1620.4 g ceiling | ≥6.3 g CAD compensation plus complete-aircraft scale measurement |
| **Propulsion (D2/E3)** | Total-power allocation and maximum-drag boundary closed; equilibrium open | E2 aircraft drag plus motor/ESC/prop bench map and 95 km/h flight Wh/km |
| **Divergence (OP-29/30)** | Conservative Vdiv 129.6 km/h; Vlimit 105 km/h | GXY/GJ coupon, complete-wing torsion and elastic-axis measurement |
| **Yaw (OP-26/E8)** | CLEAN estimated unstable; fixed-fin V1 defined | CAD body area, fin checks and flight yaw-decay test |

Release v0.3.0 is ready for CAD work within these gates. It does not authorize flight
above 105 km/h or treating calculated XFOIL, mass or printed-material values as measured.
