# I-23 — Calculation-system integration and physics audit

**Status:** Executed — software contracts closed; physical acceptance gates remain  
**Date:** 2026-08-17  
**Feeds:** Design Guide v0.19, C29–C32, ADR-0042/0043, OP-06/12/13/23/24/28/29,
`calculations/verify_calculations.py`

## 1. Purpose

This audit asks a different question from an isolated formula review: does the complete
analysis system represent one aircraft? The acceptance condition is that geometry,
mass, battery, balance, stall, electrical power, propulsion, launch, controls,
stability and structures consume the same released inputs and preserve their physical
identities across module boundaries.

The audit is computational. It does not promote XFOIL, material estimates or catalog
data to measured evidence. E2, E3, F2, S3 and E7 remain physical acceptance gates.

## 2. Highest-return defects found

### 2.1 C29 — total electrical power was not conserved

The former propulsion calculation treated the O1 value

```text
P_battery,total = 1.15 Wh/km × 95 km/h = 109.25 W
```

as motor+ESC input. Article #1 also powers its flight controller, receivers, sensors
and O4 Air Unit from that battery. With 4.3875 W of two-servo avionics rail load and
6.0 W of O4 Air Unit
rail load and the declared 0.90 BEC efficiency:

```text
P_hotel,battery = (4.3875 + 6.0) / 0.90 = 11.5417 W
P_motor+ESC     = 109.25 - 11.5417      = 97.7083 W
```

Interpolation of the measured UIUC APC E 8×8 data at 95 km/h and motor+ESC efficiency
0.85 then gives J = 0.91839, 8,484 rpm, thrust = 2.123 N, propeller efficiency 0.6744
and shaft power 83.05 W. The identity `T V = ηprop Pshaft` is verified numerically.

Thrust is the **maximum allowable aircraft drag** under O1, not a predicted drag. The
acceptance condition is CD ≤ 0.01765 and CLEAN L/D ≥ 7.21. A unique equilibrium is
computed only after E2 supplies drag, via `propulsion_match.py --drag-n D`.

### 2.2 C30 — servo torque carried a factor-1000 label error

The hinge-moment integration was in SI, but the report labelled a kgf·cm result as
g·cm. The correct conversion is:

```text
1 N·m = 10.197 kgf·cm
```

At 180 km/h, Ch = 0.05 and dual-servo actuation, the ideal demand is 0.489 kgf·cm per
servo. Applying 0.80 linkage efficiency and safety factor 1.5 gives a catalog
requirement of 0.917 kgf·cm. The 1.8 kgf·cm MG90S rating has 3.68× ideal margin and
1.96× factored margin. Static torque remains non-binding, but for the correct reason.

### 2.3 C31 — yaw-rate derivatives were dimensionalized incorrectly

For derivatives defined with nondimensional yaw rate `r b/(2V)`, the dimensional
terms are:

```text
Y_r = q S b C_yr / (2 V)
N_r = q S b² C_nr / (2 V)
```

The prior state matrix omitted `1/(2V)`, overstating damping. The corrected CLEAN
eigenvalues are +6.25 and −7.13 s⁻¹, so the unstable time constant is approximately
0.16 s. The V1 fixed-fin pair is −0.80 ± 3.95i s⁻¹, giving approximately 1.3 s decay.
The qualitative conclusion — CLEAN requires active stabilization/testing and V1 is the
first test variant — is strengthened rather than reversed.

### 2.4 C32 — the V1 mass chain omitted its aluminium spar

The former 36.72 g V1 row was simultaneously treated as a complete-fin lower model
and as a binding allocation. Rebuilding the bill of material shows that the current
PETG shell/mount lower estimate is already 37.31 g and the mandatory Ø3 mm aluminium
leading-edge spar adds 5.70 g:

```text
m_fin,complete,lower = 37.31 + 5.70 = 43.01 g
m_V1,lower           = 1583.50 + 43.01 = 1626.51 g
```

At the shared CLmax = 0.589 this gives 45.085 km/h, above the 45 km/h requirement.
The 1,620.22 g / 36.72 g values remain **allocation targets**, not achieved analytical
results. F2 must save or compensate at least 6.29 g, or E2 must justify a revised
CLmax. The verification suite deliberately passes only when this known requirement
failure is represented explicitly.

## 3. Shared numerical contract

`calculations/design_config.py` is now the authoritative source for values used by two
or more analyses:

| Contract family | Shared values |
|---|---|
| Geometry | span, area, taper, sweep, thickness schedule, stations, MAC and AR |
| Atmosphere | g = 9.81 m/s², ρ = 1.225 kg/m³, ν = 1.50×10⁻⁵ m²/s |
| Speeds | cruise 95, stall limit 45, initial limit 105, article VNE 160, structural case 180 km/h |
| Aerodynamics | CLmax = 0.589, static margin = 0.08 |
| Mass | CLEAN 1.5835 kg; V1 allocation 1.62022 kg / fin cap 0.03672 kg; connected V1 lower model 1.62651 kg / complete fin 0.04301 kg |
| Energy | O1 = 1.15 Wh/km, total 109.25 W at cruise, BEC efficiency 0.90 |
| Loads | positive limit load factor +6 g |

Model-specific assumptions remain local. For example, hinge coefficient belongs to the
servo model and the elastic-axis bracket belongs to divergence; neither is falsely
promoted to a global constant.

## 4. Numerical and software corrections

- Battery mass and reference envelope are generated once in
  `battery_pack_layout.py`; mass, CG and boom analyses consume those functions.
- Mass, stall and cruise lift coefficients share the same equations and distinguish
  released allocations from connected analytical masses. C32's V1 stall failure is a
  verified expected result, not silently rounded into compliance.
- INAV avionics rail power feeds the FPV budget; the battery-side hotel load feeds the
  propulsion boundary.
- Launch uses drag-inclusive RK4 integration, an explicit motor-delay state and the
  highest thrust-to-weight case for torque-roll screening.
- The nose boom uses exact simply supported multi-point-load superposition for pack,
  forward payload allowance and cradle: 56 MPa, FS 4.96, 1.7 mm and 31.4 Hz.
- The panel VLM caches the geometry influence matrix and vectorizes Biot–Savart
  evaluation. Scalar/vector parity and reference-wing validations protect the speedup.
- Divergence reads the released `salamandra-root-r1.dat`. Its conservative value is
  129.6 km/h; the initial operational limit remains 105 km/h pending S3/E7.
- Input-domain checks and non-zero failure exits were added to the revised scripts.

## 5. Verification architecture

Run from the repository root:

```bash
python calculations/verify_calculations.py
python calculations/verify_calculations.py --all-scripts
```

The fast command verifies cross-module identities, including:

1. canonical geometry and speed roles;
2. CLEAN mass/stall closure and the explicit V1 allocation/model/stall gap;
3. one 6S1P pack mass and cradle envelope;
4. shared cruise lift coefficients;
5. avionics → FPV → propulsion energy conservation;
6. propeller coefficient/dimensional power identity;
7. released airfoil consumed by divergence;
8. independent VLM/Weissinger neutral-point agreement;
9. corrected servo conversion and margin; and
10. damped V1 yaw eigenvalues.

`--all-scripts` additionally executes all 19 deterministic local command-line analyses
with individual timeouts. XFOIL and network workflows are listed explicitly rather
than silently reported as passed.

## 6. Remaining uncertainty

Passing software checks means that the calculations are internally consistent; it does
not mean that uncertain inputs are true. The dominant external closures remain:

- E2 measured aircraft drag, lift, moment and stall for the printed r1 wing;
- D2 motor/ESC/propeller bench map and E3 flight energy;
- F2 CAD mass properties and complete-aircraft weighing;
- S3 printed-section GXY/GJ and elastic-axis measurement; and
- E7/E8 flight envelope and yaw-decay testing.

No speed-limit expansion or propulsion-equilibrium claim is authorized by this audit.
Nor does it close V1 mass: F2 must eliminate the C32 gap before that variant is released
for flight under C16.
