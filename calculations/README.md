# Calculations — analysis tools and reproduction guide

This repository's derived quantitative claims come from scripts that are
**self-contained, validated and rerunnable**. Measured inputs retain source provenance;
estimates retain their assumptions and physical closure gates. This document explains
the tools, their versions, the data they consume and how to reproduce the published
derived results.

**Confidence rule:** every script output is tagged. Scripts compute `[D]` values from
declared `[M]`, `[E]` or `[I]` inputs; reproducibility does not raise the provenance of an
estimated input. Validation cases must pass before a modification is trusted.

---

## Tools and versions used (updated 2026-08-18)

| Tool | Version | Used for | Where to get it |
|---|---|---|---|
| Python | ≥ 3.10 | All harnesses below | python.org |
| numpy | ≥ 1.24, < 3.0 | VLM, Weissinger-L, screening harness | `pip install -r calculations/requirements.txt` |
| **XFOIL** | **6.99** (official MIT Windows console build) | Airfoil polar generation | <https://web.mit.edu/drela/Public/web/xfoil/> → `XFOIL6.99.zip` (GPL; the source ships in the zip too) |
| PowerShell 7 / cmd | Windows | Batch driving (see the Fortran stdin note below) | Built into Windows |

XFOIL is an **external GPL binary**, not bundled with this repository. Point the
scripts at it with `--xfoil <path>` or the `XFOIL_EXE` environment variable.

Data sources consumed (all `[M]`):
- **UIUC Airfoil Data Site** (<https://m-selig.ae.illinois.edu/ads/coord_database.html>)
  — E205, S5010, E387 coordinates and measured E387 polar.
- **aerodesign.de tailless-airfoil database** (Siegmann; MH data from Hepperle) — MH60
  coordinates and the published reflexed-section table (reviewed in `research/I-11`).
- Provenance of every coordinate file: `../geometry/airfoils/README.md`.

---

## The scripts

| File | What it does | Feeds | Depends on |
|---|---|---|---|
| `aero_contract.py` | **Derived aerodynamic contract** — re-derives and caches the neutral point, lift-curve slope and CG target from the planform, keeping the published values as regression anchors with a declared tolerance. Replaces the hand-copied `NP_VLM` literal (C39) | Balance, packaging, drawings, yaw | numpy |
| `drag_model.py` | **Shared drag polar** — viscous and induced terms returned separately per ADR-0009, with a declared launch-configuration transfer and band (C42) | `yaw_stability`, `launch_speed` | stdlib only |
| `contract_lint.py` | **Single-declaration lint** — fails when a physical quantity is declared in two modules, when a bare literal duplicates a contract value, or when a banded constant is frozen as a default argument | Whole system, CI | stdlib only |
| `mutation_test.py` | **Proof that the suite can fail** — seeds 20 deliberate defects (sign flips, dropped normalisations, desynchronised copies and a defeated OML containment predicate) and requires each to turn at least one contract check red (C43) | Whole system, CI | stdlib only |
| `design_config.py` | **Canonical numerical design contract** — planform, atmosphere, mission/stall/speed points, load factor and released mass targets; validates geometry and shared invariants | Guide, every coupled script | stdlib only |
| `generate_blueprints.py` | **Metric SVG drawing generator** — emits and validates the A3 general-arrangement, fuselage OML review, equipment mass-skeleton and half-wing sheets from the canonical planform, common NumPy body loft, 3D equipment ledger, calculated balance solution and released airfoil sections; visually distinguishes provisional geometry | `geometry/drawings/`, I-25/I-28, wiki drawing guide, CAD review | numpy; `fuselage_geometry.py`; `equipment_layout.py` |
| `drawing_index.py` | **Drawing publication contract** — one registry of sheet number, purpose, sheet scale, authority and reviewer note; writes `geometry/drawings/manifest.json` and the generated drawing blocks in the repository README and drawing index, and fails when any of them is stale | `README.md`, `geometry/drawings/`, wiki drawing page | stdlib only |
| `fuselage_contract.py` | **Provisional body design contract** — separates body-owned from wing-owned installation envelopes and defines three bounded, deliberately non-cylindrical OML families plus wall/clearance policy | `fuselage_geometry.py`, I-28, OP-21/F2 | stdlib only |
| `fuselage_geometry.py` | **Analytical fuselage backend** — asymmetric superelliptic sections driven by clamped cubic B-spline laws and smooth envelope maxima; emits a watertight mesh, plan/side outlines, containment margins, fairness and projected-area diagnostics | OML review drawing, trade manifest/OBJ, CAD review | numpy; `equipment_layout.py` |
| `fuselage_trade.py` | **Deterministic provisional OML trade** — seeded Latin-hypercube perturbations, feasibility-first scoring and Pareto filtering across the three family priors; writes the review manifest and OBJ without claiming aircraft closure | `geometry/fuselage/provisional/`, I-28 | numpy; fuselage contract/geometry |
| `fuselage_length_trade.py` | **I-31 flat-pack and fuselage-length screen** — compares the selected 2x2 flat 4S1P and 3x2 flat 6S1P P42A envelopes, separates physical fit from CG-compatible rail length, and quantifies first-order friction, yaw-moment, structure and pitch-inertia sensitivities without changing the OML | I-31, I-16, future fuselage trade | numpy; battery, balance and provisional fuselage geometry |
| `battery_6s_8s_trade.py` | **I-32 complete 6S1P/8S1P P42A trade** — enumerates all 18/20 rectangular layouts from manufacturer-maximum cells; compares common flat/stacked bays, mass, CG, stall, estimated cruise sensitivity, pack losses and voltage/Kv consequences without releasing a layout | I-32, I-16/I-31, future battery/propulsion/fuselage ADRs | numpy; battery, balance, drag and propulsion contracts |
| `verify_calculations.py` | **Cross-module verification** — proves geometry, mass, battery, CG, stall, power, propulsion, speed-role, airfoil, stability, control and yaw contracts agree; runs every deterministic local CLI by default (`--fast` skips them); each contract group is exception-isolated | Whole calculation system, I-23 | numpy |
| `sweep_trade.py` | **Coupled sweep selection** — full VLM + Weissinger NP, trim/twist/reflex, section-Cl margin, self-consistent balance/packaging and NASA TP-1685 divergence trend for −20…−10° candidates | I-21, ADR-0040 | numpy |
| `vlm_ala_volante.py` | Panel vortex lattice for the forward-swept wing (taper + twist). NP, CL_α, load distribution, Cm0-per-degree twist yield | I-07, G8, guide §4.3 | numpy |
| `weissinger_np.py` | **C2: independent NP check** — Weissinger-L swept lifting line (bound vortex on the c/4 line, control points at 3/4 chord). Structurally different formulation from the panel VLM | I-07, C2, G8 | numpy |
| `ventana_torsion.py` | Twist required for trim vs tip-stall margin (torsion window) | I-07, G2 | numpy |
| `flight_envelope.py` | **I-24/C33: manoeuvre and gust-load envelope** — computes the positive V-n branch and VA for CLEAN/V1, separates +6/−3 limit from +9/−4.5 ultimate loads, unit-checks the legacy Part 23 gust equation and exposes the unresolved nonlinear/dynamic gust case | I-24, ADR-0044, guide §11.2, F4/S1–S2, G11 | numpy |
| `calibra_xfoil_e387.py` | XFOIL Ncrit-grid calibration against the measured E387 (C) polar (UIUC, vol. 3) | I-06, G2 | XFOIL |
| `b3_screening.py` | **B3: corrected diagnostic screening** — changes thickness about the mean camber line, keys cached polars to geometry/settings, uses the 120k/250k/500k envelope and fits cm0 only on the pre-stall branch | B3, I-15, correction audit | numpy + XFOIL |
| `airfoil_reflex_trade.py` | **Salamandra r1 profile generator** — screens coupled root/tip reflex at the actual local Reynolds numbers, integrates section moment with c² weights, verifies trim, and writes every CAD station coordinate file | ADR-0041, guide §5, OP-02/03 | numpy + XFOIL |
| `propulsion_match.py` | **Propeller match and O1 drag boundary** — reserves avionics/FPV/BEC power, interpolates the UIUC APC E 8×8 curve, reports maximum allowable drag, and solves equilibrium only when `--drag-n` is supplied | ADR-0042/C29, guide §9, E2/D2/E3 | stdlib only |
| `balance_cg.py` | **OP-01: mass/CG balance** — pack-station solver for the CG target; planform-centroid self-check; bay sizing for the nose boom; envelope checks (AUW, V_stall) | OP-01, justification §3.1–3.2 | numpy |
| `equipment_layout.py` | **Three-dimensional equipment and mass-properties model** — one x/y/z station, oriented envelope, movement authority and uncertainty per physical component; derives total CG/inertia, fixed servo stations from the released r1 sections, cable/separation/collision gates and the battery-only CG solution for CLEAN/V1 | CAD packaging source, future SVG sheets, OP-01/P1/F1 | stdlib + released airfoil DAT files |
| `equipment_catalog.py` | **Bought-in equipment catalog** — manufacturer body dimensions and masses separated from installation abstractions; controls DJI O4 E18/E19 and their 8.95 g installed-mass closure. The 0.75 g antenna is catalogued but lumped into E19, not drawn as a third rigid body. | I-19, `equipment_layout.py`, `mass_budget.py`, SLM-EQP-001 | stdlib |
| `elevon_sizing.py` | **I-27/ADR-0045 control-surface trade** — exact surface geometry, thin-airfoil flap effectiveness, 80×6 VLM pitch/roll derivatives, connected-inertia roll response, hinge proxy and mass consequences for retained/shorter/tip/chord alternatives | I-27, ADR-0045, guide §6.6, OP-06 | numpy |
| `elevon_authority.py` | **Selected elevon pitch power** — physical-deflection ΔCm over 35–90 % half-span with ideal 0.28 c flap effectiveness and fractional panel overlap; trim closure and control margin at SM 8 % | Guide §4.3/§6.6, C6 (partial) | numpy |
| `battery_pack_layout.py` | **I-16: pack envelope** — enumerates every rectangular (n_x,n_y,n_z) layout of the 4S/6S 21700 pack, computes finished envelope (wrapper, nickel, leads) and fit-checks against the pack carrier (guide §8; the 200×70×32 bay is superseded by the cradle) | I-16, guide §8, OP-23 | stdlib only |
| `inav_fc_match.py` | **I-17: FC compatibility** — cross-checks the popular INAV boards (Matek WING, SpeedyBee, Foxeer) against the Salamandra avionics requirements (≥5 PWM, ≥2 UART, ≥1 I2C, blackbox, current, baro, 6S voltage); footprint summary + power budget | I-17, guide §10, CORE avionics | stdlib only |
| `fpv_power_budget.py` | **I-19: FPV power budget** — DJI O4 / Pro / Lite current-per-level (measured `[M]`), power at any input voltage, BEC margin vs the Matek 9V/2A and 5V/2A rails, energy impact on the 6S1P P42A pack | I-19, guide §10, O1 | stdlib only |
| `servo_torque.py` | **I-18: hinge moment** — SI hinge moment at the 180 km/h structural case, correct kgf·cm conversion, horn/linkage assumptions, safety factor and catalog margin | I-18/C30, guide §6.6, OP-06, ADR-0025 | numpy |
| `yaw_stability.py` | **I-20: directional stability** — Cnβ budget, fin sizing, rudder authority, correctly dimensionalized 2-DOF yaw modes, fin bending and mass/drag/stall cost | I-20/C31, first variant (O14), guide §4.4/§6.7, G10 | numpy |
| `joint_pin_trade.py` | **ADR-0031: pin material trade** — carbon Ø6 vs printer filament (PETG/PLA Ø1.75) in the R-JOINT torque couple: strength (FS ≥ 3 all candidates) vs stiffness (E·I: filament ≈ 9000× softer → k_joint collapses → −29 % V_div per ADR-0032) | ADR-0031/0032, guide §6.4 | numpy |
| `filament_dowel_pins.py` | **ADR-0039: dowel pins in the glued joints** — 2 × Ø1.75 filament per segment joint: shear demand at +6 g vs double-shear capacity (FS ≈ 11/24), position clearance (tube/hinge), collar bearing, mass 2.6 g | ADR-0039, guide §6.4/§6.5/§12, OP-27 | numpy |
| `mass_budget.py` | **F2: material mass variants** — per-part material policies (ALL PETG baseline / AERO-PLA wings / PLA+ / arbitrary), battery 4S–6S × P42A/50E (I-16 model), FC catalog (I-17), FPV (I-19), motor/prop/servo options, V1 fin; AUW, g/dm², V_stall, printed cost | docs/06, guide §7.1, F2 (P1/P2), OP-28 | numpy |
| `divergence.py` | **G6 revision 4: absolute divergence speed** — evaluates the released Salamandra r1 section, multicell Bredt-Batho J, explicit elastic-axis bracket, FEM cross-checked by flux-form shooting, −15° sweep-factor band, R-JOINT and tube sensitivities; auditable V_limit | docs/07, I-21/I-23, guide §11/§13, OP-29 | numpy |
| `launch_speed.py` | **I-14: hand-launch feasibility (rev. 4)** — release gate V_release ≥ V_stall, ADR-0043 V1 mass, drag-inclusive RK4 acceleration, motor-delay logic, published throw band, idle-thrust assist and torque-roll threshold | I-14/I-23, guide §4/§12, D1/D2 | numpy |
| `boom_flexion.py` | **ADR-0043 coupled nose boom Ø8/int6 aluminium + Ø3 aft spar** — imports solved mass/balance geometry; pure cantilever REJECTED (266 MPa, FS 1.04); exact multi-point two-support superposition PASS (56 MPa, FS 4.96, δ 1.7 mm, 31.4 Hz); tube+cradle 37.4 g | guide §6.7, OP-24/OP-26 | numpy |

## Reproducing the published results

Run the system contract first:

```bash
python3 -m pip install -r requirements.txt

python3 verify_calculations.py           # contracts + every deterministic script (~35 s)
python3 verify_calculations.py --fast    # interface contracts only
python3 contract_lint.py                 # one declaration per physical quantity
python3 mutation_test.py                 # prove the contract suite can actually fail
```

The default run checks cross-module equality **and** executes every deterministic local
CLI, so each module's own validation case is actually exercised; `--fast` restricts it to
the interface contracts. Every contract group is evaluated in isolation: a group that
raises is reported as a failed check carrying the exception text, never as an aborted run
with no diagnosis. XFOIL and network workflows remain explicit external gates and are
listed, never silently skipped.

`contract_lint.py` and `mutation_test.py` are the two guards on the verification itself.
The lint catches a desynchronised quantity **before** it can produce a wrong number; the
mutation test measures whether the contract suite would notice **after**. Both run in CI
(`.github/workflows/calculations.yml`) alongside the drawing gate.

### 0.1 Metric SVG drawing set (I-25)

```bash
python3 generate_blueprints.py --check
```

Running it without `--check` writes the sheets **and republishes** `geometry/drawings/manifest.json`, the repository README drawing gallery and the drawing index table through `drawing_index.py`; the wiki renders the same manifest at build time. `--check` fails when a sheet or any published block is stale, and it is the gate CI runs. Use `python3 drawing_index.py` when only the published text changed, since it needs no numerical stack.

This checks the generated A3 metric drawing set, including the equipment-only
`SLM-EQP-001` mass skeleton and `SLM-FUS-001`, the common-source OML/envelope audit.
Every sheet is explicitly marked
**not for manufacture**. Print at actual size only; responsive web display is not a scale
reference. The visual semantics and open limitations are recorded in
`geometry/drawings/README.md`.

### 0.2 Provisional fuselage OML (I-28)

```bash
python3 fuselage_contract.py
python3 fuselage_geometry.py --json
python3 fuselage_trade.py --check
python3 fuselage_trade.py --family all --samples 1 --seed 2802
```

The body is generated around the body-owned subset of the CLEAN three-dimensional
equipment skeleton. It is one analytical 3-D source for the OBJ review mesh,
`SLM-FUS-001`, and the OML projections used by GA-001/002. The default
`lifting_saddle` family is a review starting point rather than an aerodynamic optimum.
At the canonical mesh it encloses every audited central envelope and is watertight, but
the reported skin mass is only a gross 0.9 mm surface screen: overlap with the wing,
cavities, openings, local reinforcement and printed-joint mass are unresolved.

The generator deliberately keeps `geometry_feasible` separate from
`aircraft_feasible`. The latter remains false while V1 battery reach, reserve-mass
location, net union mass ownership, body-inclusive NP/trim and the wing installation
audit are open. No generated body file is manufacturing authority.

### 1. Neutral point (I-07, and C2 cross-check — guide §3)

```bash
python3 vlm_ala_volante.py      # in-house method, includes the straight-AR-6 validation
python3 weissinger_np.py        # independent method, includes the same validation
```

Published ADR-0040 result (`[D]`): VLM **x_NP = −75.8 mm** (25.72 % MAC) vs
Weissinger-L **−72.9 mm** (27.0 % MAC) — **2.9 mm method spread**, at the canonical
meshes (`VLM_NY`×`VLM_NX` = 40×6, `WEISSINGER_NY` = 100) declared in `design_config.py`.

Both numbers are **derived on every run** by `aero_contract.py` and compared against those
published anchors with a ±0.5 mm tolerance; they are no longer literals (C39). The mesh
error at the canonical resolution is bounded at 0.4 mm by an explicit convergence
assertion, and the 2.9 mm method spread is carried as a declared modelling uncertainty —
it is 16 % of the 18.0 mm static margin and 58 % of the ±5 mm CG band, so it is not
averaged away.

```bash
python3 aero_contract.py        # the derivation and its anchors
python3 vlm_ala_volante.py      # in-house method + exact linear-model identities
python3 weissinger_np.py        # independent method (C2)
```

### 2. Corrected B3 diagnostic screening (I-15 §6 and §8)

```bash
python3 b3_screening.py --xfoil /path/to/xfoil.exe
```What it does, step by step:

1. Reads the candidate coordinates from `../geometry/airfoils/` (E205, S5010, MH60 —
   provenance in `geometry/airfoils/README.md`).
2. Generates the thickness variants about the interpolated mean camber line. This
   preserves camber/reflex instead of multiplying every ordinate; the old affine-y
   rule was an implementation error.
3. Runs **42 diagnostic XFOIL cases** (7 profiles × Re 120k/250k/500k × Ncrit 10/12),
   covering the actual root/tip stall and cruise envelope.
4. Saves the raw polars in `xfoil_out/<case>.pol`; the cache metadata contains a SHA-256
   of the coordinates plus Reynolds number, Ncrit and solver settings, so changed
   geometry cannot reuse stale data.
5. Prints the summary table: cm0 (pre-stall linear fit of CM(CL) evaluated at CL=0),
   clmax, α_stall, (L/D)max, and cd at the shared V1 cruise CL (currently 0.1327).

**Incremental:** only polars whose full metadata match are reused; rerunning after a
crash recomputes missing or stale cases.

**Batch-mode notes for XFOIL 6.99 on Windows** (all baked into the script, kept here
for anyone maintaining it):
- The Ncrit command lives in the **VPAR** submenu (`OPER` → `VPAR` → `N <value>`);
  `NCRIT` does not exist in this version.
- Polar accumulation is `PACC` (prompts: save-file name, then dump-file name — blank
  to decline), then `ASEQ`; close with `PACC` (off) and `PWRT 1 <filename>`.
- The input stream must be a **CRLF file redirected as stdin** (a PowerShell pipe
  truncates it; the Fortran runtime reads until EOF and prints a harmless
  "Fortran runtime error: End of file" after QUIT — ignored).
- The script runs XFOIL from a short local working directory because its Fortran file
  handling is unreliable with long paths.

The corrected screening invalidates the old root-only trim conclusion. It is retained
as a candidate diagnostic; the coupled r1 generator below is the controlling CAD tool.

### 2.1 Salamandra r1 coupled airfoil closure (ADR-0041)

```bash
python3 airfoil_reflex_trade.py --xfoil /path/to/xfoil.exe
```

The generator uses root Re 240k/510k and tip Re 120k/255k, Ncrit 10/12, exact c²
root/tip moment weights 0.6071/0.3929, and the VLM twist/elevon yields. It selects
**MH60 mean line, 13.5 % root with +1.0° reflex and 9.0 % tip with +0.5° reflex**,
then writes the endpoint and seven intermediate station DAT files. The full-envelope
polars give neutral elevon **−0.04°/+0.41°** at the corrected V1 analytical mass and
+3.0° wash-in, inside the ±0.6° cap;
all endpoint cases have section clmax ≥1.076. These are `[D]` CAD inputs; E2 is still
the physical polar/stall acceptance.

### 3. Balance and CG reachability (OP-01, guide §8.2)

```bash
python3 balance_cg.py
```

Self-validating: it imports the canonical planform, computes the shell and carbon
stations, iterates boom mass/length with the pack solution, and solves all four P42A
pack stations at target CG **−93.8 mm** (SM 8 %).

Current aggregate screen (ADR-0043/0045, `[D]`): CLEAN mass **1553.25 g**, 6S1P pack
station **−353.7 mm**, allowable CG-band station −371.1…−336.2 mm, cradle
approximately −452.7…−254.6 mm, and support span **320.7 mm**. The component-level
packaging model below supersedes the aggregate station with **−337.74 mm CLEAN** after assigning
individual x/y/z locations. Diagnostic aggregate stations for future modules are
4S1P −473.5 / 4S2P −291.8 / 6S2P −227.7 mm; they are not Article #1.

### 3.1 Three-dimensional component layout and battery trim

```bash
python3 equipment_layout.py
python3 equipment_layout.py --variant v1
python3 equipment_layout.py --json
python3 equipment_layout.py --move receiver=5,-60,3
```

This is the pre-CAD packaging authority. Every physical item has an identifier, mass,
rectangular envelope, x/y/z centre, allowed-position box, uncertainty and evidence tag.
The coordinate system is x aft, y starboard and z up, with the root quarter-chord as
origin. It computes the three-dimensional CG, a full cuboid-plus-parallel-axis inertia
tensor, first-order CG uncertainty, AABB interference, cable length and required
equipment separation.

Movement authority is intentionally asymmetric:

- Printed frame allocations, carbon, boom, cradle and the optional **fixed** V1 fin are
  fixed masses. They are never moved to force a CG result.
- The FC reference centre is x = −93.797 mm, y = 0, directly at the longitudinal target;
  its three-dimensional distance from the solved CLEAN CG is 0.42 mm.
- Servo locations are derived once, then fixed. The solver lays one 22.5 × 24.6 ×
  11.5 mm DS-939MG body in each half-wing at y = **406.25 mm** and moves it as far aft as
  the released r1 airfoil permits while retaining 1.5 mm to both external surfaces.
  The working result is x/c = **0.5334** with a **37.1 mm** projected pushrod run to the
  x/c = 0.72 hinge.
- Low-mass avionics may be repositioned only inside their declared packaging bounds.
  The O4 camera is fixed at the foremost centreline station, looks along −x, and
  places its lens face on the forward cradle plane. Its 45.99 mm three-dimensional
  centre distance to the aft VTX is a lower-bound check against the 50 mm coax,
  not a released cable route and not a CG-ballast degree of freedom.
- The 445 g battery is the **only automatic CG-trim variable**. After an allowed manual
  equipment movement, the analytical solver recomputes only battery x; use
  `--hold-battery` solely to inspect an untrimmed candidate.

Current candidate results `[D]`: CLEAN closes **1553.25 g** at the released CG target with the
battery at x = **−337.74 mm**. V1 adds the complete fixed-fin lower model and runs the
coupled packaging solve. Existing travel is sufficient: no forward extension or added
support mass is required. Battery x = **−363.27 mm** recovers xCG = −93.784 mm in one
iteration. These values differ
from the aggregate `balance_cg.py` station because individual masses now occupy their
explicit spatial locations.

The audited E01 cradle cross-section is **68 × 25 mm**, giving 2.30 mm total lateral
and 2.40 mm total vertical clearance around the 153.0 × 65.7 × 22.6 mm maximum pack.
The 0.75 g O4 antenna is included in the released mass budget and lumped into the
E19 VTX assembly instead of being modelled as a third rigid body. Open CAD
gates remain explicit: longitudinal one-sigma CG uncertainty is about 7.8 mm versus a
5 mm half-band, V1 cannot reach the exact CG target at the current forward stop, and
92.88 g remains unresolved reserve mass. This layout is not a manufacturing release.

### 4. Elevon authority (guide §5.3/§6.1)

```bash
python3 elevon_authority.py
```

Uses the ADR-0045 35–90 % surface, ideal thin-airfoil effectiveness `tau = 0.6408` for
0.28 c and fractional span-panel overlap in the same VLM, then adds the c²-integrated
r1 root/tip moment. Results at the −15° planform: elevon yield **0.001828 Cm per
physical degree**; neutral trim is **−0.14°/+0.50°** over Ncrit 10/12. A 5° command
provides about **10×** the limiting residual. Run `elevon_sizing.py` for the span/chord
trade, roll derivatives and limitations.

### 5. Twist window (I-07)

```bash
python3 ventana_torsion.py
```

Uses the connected **1.59626 kg V1 lower model** for cruise trim and local section-Cl
screening. At 45 km/h it requires wing CL **0.58023**, below the shared CLmax 0.589;
the **1.58997 kg allocation target** requires CL 0.57794. With 3.0° wash-in the
computed peak local cl is 0.629 versus the 0.65 section limit, while the r1 profile
leaves 0.34° equivalent twist demand at SM 8 %. Five degrees has only 0.001 local-cl
margin and six degrees exceeds the section limit; the selected 3.0° remains the
controlled value. F2/E2 physical mass and CLmax verification remain open.

### 5.1 Flight-load envelope (I-24 / ADR-0044)

```bash
python3 flight_envelope.py
```

Uses the released VLM `CL_alpha = 4.2712/rad`, shared masses, `CLmax` and speed roles.
The positive manoeuvre intersections are **VA = 107.9 km/h CLEAN / 109.4 km/h V1**;
at the 105 km/h initial limit the stall boundary permits 5.68/5.53 g. It corrects C33:
**+6/−3 are provisional manoeuvre limit loads and +9/−4.5 are their 1.5× ultimate
structural cases** — +9 is not a later flight target.
At the V1 lower mass these are +94.0/−47.0 N limit and +140.9/−70.5 N ultimate
whole-aircraft normal resultants; a proof fixture must reproduce the span load rather
than apply either value at one point.

The independent legacy Part 23 gust screen gives +13.09/−11.09 g for CLEAN at
105 km/h, but its implied positive `CL = 1.36` exceeds the released `CLmax = 0.589`.
That result is deliberately reported as a nonlinear/stall flag, not adopted as a design
load. The inverse sensitivity at 105 km/h is 6.30 m/s to +6 and **5.04 m/s to −3**;
these are equivalent vertical-gust inputs, not forecast surface wind. A complete
negative branch awaits a validated negative-polar `CLmin`; dynamic gust closure is
G11/E9.

### 6. XFOIL calibration (I-06)

```bash
python3 calibra_xfoil_e387.py --xfoil /path/to/xfoil.exe
```

Downloads the E387 coordinates and the measured polar from UIUC at runtime; validates
its metric on an analytic case (Cd_calculated = 1.1 × Cd_measured → factor 1.1).

### 7. Battery pack envelope (I-16)

```bash
python3 battery_pack_layout.py
```

Self-validating by construction: it prints the full enumeration of cell
arrangements (12 envelopes for 4S, 18 for 6S) with a fit check against the
`190 × 70 × 32 mm` provisional reference bay (guide §8), plus per-cell and per-pack mass /
energy / discharge for the two reference cells (Molicel P42A, Samsung 50E) and
their average. Published results (I-16 §4–§5, §6.1):
**6S1P = 2×3 orient. A → 153.2 × 64.5 × 22.2 mm**,
**4S1P = 2×2 → 153.2 × 43.2 × 22.2 mm** — the envelopes that fit the current
provisional bay (all others are buildable with a resized bay). Pack masses:
6S1P P42A 445 g / 50E 433 g / avg 439 g; 4S1P 305 / 297 / 301 g. A change to the
fit test, assembly allowances, or cell specs must reproduce these values.

Those values are the nominal generic-21700 enumeration. CAD fit uses the separate
manufacturer-maximum P42A path: **153.0 × 65.7 × 22.6 mm** for the same 2×3 layout.
The maximum datasheet dimensions already include the cell sleeve, so the script does
not add the nominal wrapper twice; it adds only the declared pack-level wrap, nickel
and lead allowances. `equipment_layout.py` imports this maximum envelope directly.

#### I-32 extension: complete 6S1P/8S1P trade

```bash
python3 battery_6s_8s_trade.py
```

Enumerates all **18 six-cell** and **20 eight-cell** rectangular arrangements with
maximum P42A dimensions. It corrects the series-pack capacity semantics (both packs are
4.2 Ah), compares the 445 ± 5 g 6S and 585 ± 5 g 8S cases, solves their pack stations,
and prints five common-bay alternatives. Published flat-pair results: narrow
**340.5 × 44.0 × 22.6 mm** pack union, moderate **246.7 × 70.8 × 22.6 mm**, and
short/wide **235.2 × 87.4 × 22.6 mm**; rail length includes the asymmetric 12 mm aft
lead and ±10 mm centre travel. These are pre-wall screening envelopes, not CAD authority.

### 7.1 Servo hinge moment (I-18)

```bash
python3 servo_torque.py
```

Hinge moment of the 0.28 c elevon (**357.5 mm span**) at the 180 km/h structural design
speed over Ch 0.01–0.05 `[E]`: **0.175–0.876 kgf·cm per servo** with one actuator per elevon
and a 1:1 horn ratio. After 0.80 linkage efficiency and a 1.5 safety factor, the
catalog requirement is **1.643 kgf·cm**. The Article #1 DS-939MG has **1.52× factored
margin**. The former g·cm label was a factor-1000 unit
error; C30 records the correction. A change to geometry, Ch, speed or linkage must
reproduce the margin table.

### 8. INAV flight-controller compatibility (I-17)

```bash
python3 inav_fc_match.py
```

Cross-checks each candidate board (specs `[M]` from manufacturer pages) against
the Salamandra avionics requirements (guide §11). Published result (I-17 §3):
**YES** for F405-WING v1/V2, F765-WING, F722-WING, SpeedyBee F405 WING; **no** for
F411-WING/F411-WSE (no blackbox) and Foxeer F405 V2 (no current input). Also
prints the footprint summary (I-17 §4.1): min 28×28×7, avg 45×34×12, max
56×37×13 mm, recommended station cavity **64 × 45 × 21 mm**; and the power budget
(I-17 §6): 5 V rail 300–555 mA, two-servo avionics **4.39 W on the regulated rails /
4.88 W from the battery** at 90 % BEC efficiency, or 5.4 % of a 6S1P P42A pack per hour.
A change to the requirement set, board specs or BEC efficiency
must reproduce these lines.

### 9. FPV power budget (I-19)

```bash
python3 fpv_power_budget.py [input_V]
```

Per-level power of the DJI O4 Air Unit and O4 Air Unit Pro from measured currents `[M]`.
Published results (I-19 §5): O4 Pro 1200 mW = 10.4 W and Article #1 O4 Air Unit
700 mW = 6.0 W; 9 V rail utilization ≤ 58 %. Including avionics gives
**14.83 W rail / 16.48 W battery with O4 Pro**, and **10.39 W rail / 11.54 W battery
with the Article #1 O4 Air Unit**, at the shared 90 % BEC efficiency. The Pro case consumes
20.9 % of the 90.72 Wh pack per hour. A change to the current table or BEC assumptions
must reproduce these values.

### 9.1 Cruise propulsion power/drag boundary (ADR-0042/C29)

```bash
python3 propulsion_match.py
```

Starts from the O1 total battery ceiling of 109.25 W and reserves **11.54 W** for
Article #1 avionics, O4 Air Unit and BEC losses. Interpolation of the measured UIUC APC E
8×8 curve at 95 km/h gives the motor boundary **J 0.918, 8,484 rpm, maximum allowable
drag 2.12 N, ηprop 0.674, shaft power 83.1 W and motor+ESC input 97.71 W**. This is not
a unique aircraft equilibrium: use `--drag-n <measured E2 drag>` to solve one. The
boundary requires CD ≤ 0.01765 and CLEAN L/D ≥ 7.21. A 4S module needs approximately
717 Kv; the propeller has 2.21× rpm margin. The former J 0.899 point omitted hotel load
and assumed thrust equals unknown aircraft drag; C29 supersedes it.

### 10. Directional stability and the twin-fin variant (I-29)

```bash
python3 yaw_stability.py
```

Cnβ budget of the finless baseline (body + FSW wing: **−0.00055…−0.00141/deg — negative**),
twin-fin sizing for two stability tiers (swept-trapezoid V1a 6.1437 dm² total →
nominal +0.0005/deg; V1b 8.18 dm² total → +0.0010/deg), independent-corner power-on/off
bands, rudder authority vs crosswind, yaw damping and
subsidence, fin bending at the 180 km/h structural case (**root t ≥ 3.0 mm**), and the mass/drag/stall cost of
each tier. The selected architecture uses two CORE-rooted fins at y = ±140 mm, wholly
forward of the fixed propeller hazard; it does not credit slipstream. Published results (I-30, `[D]` on
`[E]` bands): correctly dimensionalized finless modes are **+8.244/−9.453 s⁻¹**
(divergence time constant about 0.12 s), while the powered nominal V1 screen gives
**−0.952 ± 5.239i s⁻¹** (decay time about 1.1 s). V1a ΔCD0 +0.0034 (+23.1 % drag);
V1b +0.0044 (+30.5 %). The selected `x_AC = +115.5 mm` is the minimum-mass feasible
result of the +80…+280 mm, 0.5 mm-grid fixed-propeller trade. A change to geometry, bands or methods must reproduce
all embedded validation cases, including planform invariants and independent-corner power states.

### 10.1 Connected aircraft scene and clearance

```bash
python3 aircraft_scene.py
```

Consumes the same equipment ledger, propeller definition, V1 packaging solution and fin
geometry used by the drawings. It validates oriented top/side/rear projections and
proves both radial and axial separation. Current V1 root-support clearance is **29.4 mm
nominal / 13.4 mm residual radially** after the explicit 16.0 mm allowance and **8.33 mm
axially** beyond the inflated forward hazard face. Side-view overlap is zero. Status is
`ANALYTICAL PASS / F2 PHYSICAL OPEN`.

### 11. R-JOINT pin material trade (ADR-0031)

```bash
python3 joint_pin_trade.py
```

Evaluates the community proposal of replacing the carbon Ø6 anti-rotation pin with
3D-printer filament (PETG/PLA Ø1.75). **Strength passes** (shear FS ≈ 4.7–6.3 at the
declared torque band), **stiffness fails decisively**: E·I carbon Ø6 = 7.63 N·m² vs
PETG filament 0.0009 N·m² (≈ 9000× softer) → k_joint ∝ E·I collapses from ≥ 5× to
≈ 0.005× the section → **−29 % V_div** (ADR-0032 penalty table) on a wing whose
dominant risk is divergence. Printed-PETG tenons need Ø17 for parity (≈ 40 g vs
6.3 g). Cost saving ≈ €0.5–1.0/aircraft, complexity unchanged (the socket is the
same). **Rejected; carbon Ø6 stands.** Five validation cases must pass.

### 12. Filament dowel pins in the glued joints (ADR-0039)

```bash
python3 filament_dowel_pins.py
```

2 × Ø1.75 mm filament per glued segment joint (y = 347/498): alignment during glue
cure (primary, `[I]`) + shear redundancy vs the +6 g V_NE demand — FS ≈ 11 (y = 347)
and 24 (y = 498) `[D]`; positions x/c 0.40/0.60 verified clear of the carbon tube and
the hinge cell; collar Ø8 × 4 mm bearing FS ≈ 10; mass 2.6 g/aircraft, zero cost.
The CORE↔PANEL torque couple is untouched (carbon Ø6 — `joint_pin_trade.py`). Six
validation cases must pass.

### 13. Material mass variants (F2 — docs/06)

```bash
python3 mass_budget.py --config all            # ALL PETG / AERO WINGS / AERO MAX / PLA+
python3 mass_budget.py --config matrix         # per-part × material matrix
python3 mass_budget.py --config aero_wings --battery 4S1P --fin
python3 mass_budget.py --config all_petg --fc F765-WING --fpv O4-Air-Unit
```

Data-driven weight budget with per-part material selection. The Article #1 default is
6S1P P42A, SpeedyBee F405 WING + mandatory PDB, DJI O4 Air Unit including its
separate antenna, two Corona DS-939MG servos,
APC E 8×8 assembly and the coupled ADR-0043 boom. Published results (docs/06 §3):
ALL PETG CLEAN **1553.25 g / 44.1 km/h**. The current V1a lower assembly model is
35.61 g for two LW-PLA-HT shells/mounts + 10.07 g for two aluminium LE spars + 3.04 g
for two carbon root supports = **48.73 g**. The coupled packaging solution requires no
forward extension or added support mass, giving **1601.98 g / 44.74 km/h** and battery
x = −363.27 mm; F2 must verify material coupons, mass, balance, O4 routing and CAD.
The AERO policies
remain rejected by divergence. Validation retains v0.2 as a historical regression and
checks both the 60.00 g complete-assembly allocation and the analytical lower model.

### 14. Absolute divergence speed (G6 revision 4 — docs/07)

```bash
python3 divergence.py
```

Revision 4 retains the explicit xEA/c = 0.30…0.45 uncertainty bracket and replaces the
stale MH60-13.5 section with the released `salamandra-root-r1.dat`. Results at −15°:
**nominal 327.2 km/h (1.36× PASS), conservative 129.6 km/h (0.54× FAIL), AERO
91.6 km/h** vs the 240 km/h criterion. GXY = 0.69 GPa gives 180.0 km/h; the combined
GXY+gyroid+1.1 mm wall case reaches 207 km/h. The computed 0.85 clearance rounds to
110 km/h, but the released initial **V_limit remains 105 km/h** conservatively;
**150 km/h** remains conditional on S3 validating GXY.

### 15. Hand-launch feasibility (I-14 executed, rev. 6 — guide §4/§12)

```bash
python3 launch_speed.py
```

Gate check of the mandatory hand throw. The current coupled packaging result is **1601.98 g V1
analytical lower mass**
and integrates `m dV/dt = T − D(V)` by RK4 with piecewise-constant phase thrust,
including the 0.2 s motor delay.
**Result: FEASIBLE — typical throw 10.5 m/s + reference idle reaches 12.8 m/s
(46.3 km/h, k = 1.04) at release and k = 1.20 in 0.35 s; firm throw reaches 16.2 m/s
(58.4 km/h, k = 1.31). Weak throw remains below stall:
technique is part of the specification.** Anchored on the Mojito configuration class
`[M]` (1800 g, higher reported stall, hand-launched in service) and published
biomechanics (van den Tillaar 2004). The worst torque-roll case is checked at the
highest thrust-to-weight end. All validation cases must pass. Autolaunch
settings table in research/I-14 §3.2.

### 16. Nose boom Ø8/int6 aluminium + Ø3 aft spar (ADR-0043 — guide §6.7)

```bash
python3 boom_flexion.py
```

User decision 2026-08-06: the battery boom is an **aluminium tube Ø8 / int Ø6
(wall 1.0 mm)** with a printed cradle, and a **Ø3 mm aluminium spar** stiffens
the V1 fin near the trailing edge; carbon optimisation deferred (ADR-0015).

- **Pure cantilever REJECTED** (`[D]`): +6 g with the 445 g pack →
  σ 266 MPa vs 276 (6061-T6), δ 34 mm.
- **Two-support arrangement ADOPTED** (`[D]`): the structural check conservatively
  retains the pack load at −359.6 mm; the current component-level balance station is
  **−337.74 mm CLEAN** between the forward
  support (x = −452.70) and CORE support (x ≈ −132), with pack, forward payload allowance
  and cradle represented as separate loads → σ **56 MPa** (FS **4.96**),
  δ **1.7 mm**, mode **31.4 Hz**. The cradle is a structural requirement, not
  packaging.
- Mass: 377 mm tube 22.4 g + cradle 15 g = **37.4 g**; tip skid = crush zone.
- Ø3 fin spar: 3.0 mm root EI ×1.60 (0.278 + 0.463 N·m²), 5.7 g.
- All structural and cross-module validation cases must pass.

---

## Validation discipline

**Any modification to a script must pass its validation case before use.** This is not a
formality: two real bugs were caught exactly this way during the 2026-08-05 session
(recorded in CHANGELOG [1.11]):
- a MAC-normalization error in the VLM (historic, C17);
- an odd `y·tanΛ` moment arm in Weissinger-L — the c/4 line sweeps forward on **both**
  halves, so the arm is `|y|·tanΛ`; the bug zeroed the sweep moment by symmetry and was
  caught by the straight-wing validation (NP must be 25.00 % MAC).

## Conventions (shared by all scripts)

- `x` positive backward, origin at the root c/4
- `Lambda_c4` negative = forward sweep
- `epsilon` positive = wash-in (tip at higher incidence)
- Outputs are `[D]` unless tagged otherwise; XFOIL polars are predictions, not
  measured data — the E387 calibration (I-06) and E2 (flight polar) define their value.
