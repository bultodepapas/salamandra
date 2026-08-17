# Salamandra — Release v0.3.0: Airfoil, Propulsion and Mass Closure

**Date:** 2026-08-17 · **Tag:** `v0.3.0` · **Status:** RELEASED

**Controlling specification:**
[Salamandra Design Guide v0.18](../design/Salamandra-Design-Guide-v0.1.md)

Release v0.3.0 closes the three highest-return design uncertainties left by v0.2.0:
the CAD airfoil family, the propulsion operating point and the Article #1 mass/stall
allocation. Each correction is backed by a reproducible calculation and propagated
through the Design Guide, justification, open-points register, ADRs and research log.

This is a **design release**, not a flight-qualified aircraft. The r1 sections still
require E2 physical polar/stall acceptance, the mass allocation requires F2 CAD and
scale verification, and the initial 105 km/h limit remains until S3/E7 close the
printed-wing torsion and elastic-axis uncertainty.

---

## 1. Authority and migration rule

The released document hierarchy is:

1. **Design Guide v0.18** controls CAD geometry, interfaces, materials, stations and
   acceptance limits.
2. `calculations/design_config.py` controls planform numbers; the generated Salamandra
   r1 DAT files control profile coordinates.
3. ADR-0041…0043 record the three v0.3 decisions and their review conditions.
4. I-15 §8 and I-22 record the correction evidence; the open-points register records
   the remaining physical gates.

Do not average conflicting values. Do not combine the v0.2 provisional profile,
battery station or component budget with v0.3 geometry. The stable Design Guide
filename is retained; its internal released revision is **0.18**.

## 2. Why these three changes have the highest ROI

| Priority | Defect closed | Return |
|---:|---|---|
| 1 | Thickness scaling changed the mean line and cached polars could survive geometry changes | Prevents manufacturing an aerodynamically different wing from the documented one; supplies final CAD station coordinates |
| 2 | Propeller peak efficiency was used as the cruise command without enforcing aircraft power/thrust equilibrium | Removes a 230 W versus 109 W contradiction and makes motor Kv/pack selection physically consistent |
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
wash-in, the c²-integrated XFOIL/VLM solution gives −0.06°/+0.39° neutral elevon over
Ncrit 10/12, within the ±0.6° design cap. Endpoint section clmax is at least 1.076 in
the computational envelope. These are `[D]` results; E2 remains the measured closer.

Controlling coordinate files:

- `salamandra-root-r1.dat` and `salamandra-tip-r1.dat`;
- intermediate stations y = 130, 195, 325, 347, 488, 498 and 585 mm;
- raw accepted endpoint polars and metadata in `calculations/xfoil_out/`.

### 3.2 Propulsion at aircraft equilibrium

At O1, 95 km/h × 1.15 Wh/km gives 109.25 W electrical. Interpolation of the measured
UIUC APC E 8×8 curve, with motor+ESC efficiency 0.85, gives:

| Quantity | v0.3 operating point |
|---|---:|
| Advance ratio J | **0.899** |
| Propeller speed | **8,667 rpm** |
| Thrust = aircraft drag | **2.42 N** |
| Propeller efficiency | **0.688** |
| Shaft / electrical power | **92.9 / 109.3 W** |

The 0.80–0.88 motor-efficiency sensitivity gives 8,568–8,722 rpm and 2.25–2.52 N.
The former peak-efficiency point, J = 0.762, would require approximately 230 W and
5.46 N and is therefore not the O1 cruise point.

Article #1 is **6S1P, 500–550 Kv, APC E 8×8**. The required rpm is 71–78 % of nominal
no-load speed. A 4S installation needs approximately 730 Kv at an assumed 80 % loaded
ratio and is a separate power module. The 8,667 rpm point has 2.16× margin to APC's
published 18,750 rpm Thin Electric limit. D2 bench data and E3 flight energy remain
the hardware/mission acceptance tests.

### 3.3 Binding Article #1 mass, stall and CG allocation

Conventional PETG is retained. The Article #1 defaults are a ≤550 g PETG shell,
SpeedyBee F405 WING FC+PDB, DJI O4 Lite, four Corona DS-939MG servos and a 25 g APC
E 8×8 assembly. The allocation results are:

| Configuration | AUW | Wing loading | Predicted stall | Exact mass margin to 45 km/h |
|---|---:|---:|---:|---:|
| SALAMANDRA-CLEAN | **1,583.5 g** | 56.2 g/dm² | **44.5 km/h** | 36.9 g |
| SALAMANDRA-V1 | **≤1,620.2 g** | 57.5 g/dm² | **45.0 km/h** | 0.2 g |

The exact mass ceiling under the declared model is 1,620.4 g. V1 therefore requires
strict CAD mass properties and a complete-aircraft scale measurement. Its 36.72 g fin
cap matches the calculated V1a lower mass bound. The coupled
balance solution moves the 6S1P pack to **x = −359.6 mm**, uses an approximate
−460…−259 mm cradle and a **327 mm** structural support span. The hybrid boom becomes
37.4 g and passes the two-support +6 g check at 54 MPa, FS 5.08 and 1.4 mm deflection.

## 4. Breaking v0.2.0 → v0.3.0 migration

The −15° planform, neutral point, target CG and 105 km/h initial limit do not change.
The following dependent data do:

| Driver | v0.2.0 | v0.3.0 |
|---|---:|---:|
| Profile | provisional scaled candidate | **Salamandra r1 station DAT family** |
| Printed wash-in / neutral trim | +3.0° / adverse +1.9° provisional reflex | **+3.0° / −0.06°…+0.39° elevon** |
| Cruise propeller command | peak η, J ≈ 0.762 / ≈9,900 rpm | **equilibrium J 0.899 / 8,667 rpm** |
| Article #1 electrical architecture | pack options not closed | **6S1P, 500–550 Kv** |
| CLEAN / V1 AUW | 1,685.2 / 1,722–1,747 g | **1,583.5 / ≤1,620.2 g** |
| 6S1P pack station | −372.7 mm | **−359.6 mm** |
| Cradle | −473.3…−272.2 mm | **approximately −460…−259 mm** |
| Boom assembly / support span | 38.2 g / 341 mm | **37.4 g / 327 mm** |

Any existing v0.2 wing loft must be regenerated from the r1 coordinates. Any v0.2
cradle or forward support must be re-positioned. Do not modify the unchanged planform
station coordinates while making those updates.

## 5. Released package

| Artifact | Release role |
|---|---|
| [`design/Salamandra-Design-Guide-v0.1.md`](../design/Salamandra-Design-Guide-v0.1.md) | **v0.18 controlling CAD specification** |
| [`design/Design-Guide-Justification-v0.1.md`](../design/Design-Guide-Justification-v0.1.md) | v0.13 evidence and derivations |
| [`design/Design-Guide-Open-Points-v0.1.md`](../design/Design-Guide-Open-Points-v0.1.md) | v0.13 remaining gates and triggers |
| [`decisions/ADR-0041-salamandra-r1-airfoil-family.md`](../decisions/ADR-0041-salamandra-r1-airfoil-family.md) | Profile-family decision |
| [`decisions/ADR-0042-cruise-propulsion-equilibrium.md`](../decisions/ADR-0042-cruise-propulsion-equilibrium.md) | Propulsion operating-point decision |
| [`decisions/ADR-0043-article-1-mass-allocation.md`](../decisions/ADR-0043-article-1-mass-allocation.md) | Mass/stall/CG allocation |
| [`research/I-22-high-roi-v0.3-audit.md`](../research/I-22-high-roi-v0.3-audit.md) | Ranked audit and correction evidence |
| [`calculations/airfoil_reflex_trade.py`](../calculations/airfoil_reflex_trade.py) | r1 generator and XFOIL envelope |
| [`calculations/propulsion_match.py`](../calculations/propulsion_match.py) | Propeller/aircraft equilibrium |
| [`calculations/mass_budget.py`](../calculations/mass_budget.py) | Binding allocation and options |
| `geometry/airfoils/README.md` | Released CAD coordinate family and provenance |

## 6. Reproduction and release verification

```bash
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
| **Mass (F2/OP-24)** | 1583.5/1620.2 g allocation closes the model | CAD mass properties and complete-aircraft scale measurement |
| **Propulsion (D2/E3)** | Equilibrium and power-module architecture closed | Motor/ESC/prop bench map and 95 km/h flight Wh/km |
| **Divergence (OP-29/30)** | Conservative Vdiv 128.8 km/h; Vlimit 105 km/h | GXY/GJ coupon, complete-wing torsion and elastic-axis measurement |
| **Yaw (OP-26/E8)** | CLEAN estimated unstable; fixed-fin V1 defined | CAD body area, fin checks and flight yaw-decay test |

Release v0.3.0 is ready for CAD work within these gates. It does not authorize flight
above 105 km/h or treating calculated XFOIL, mass or printed-material values as measured.
