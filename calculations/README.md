# Calculations — analysis tools and reproduction guide

This repository's quantitative claims come from scripts that are **self-contained,
validated, and rerunnable by anyone**. This document explains the tools, their versions,
the data they consume, and exactly how to reproduce the published results.

**Confidence rule:** every script output is tagged. The scripts compute `[D]` values
(derived by calculation from `[M]` data). They never invent inputs, and their validation
cases must pass before a modification is trusted.

---

## Tools and versions used (updated 2026-08-17)

| Tool | Version | Used for | Where to get it |
|---|---|---|---|
| Python | 3.11 (Windows) | All harnesses below | python.org (any ≥ 3.8 works) |
| numpy | 1.2x | VLM, Weissinger-L, screening harness | `pip install numpy` |
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
| `design_config.py` | **Canonical numerical planform** — span, area, taper, −15° c/4 sweep, thickness schedule and every design station; validates area, chord closure and edge directions | ADR-0040, guide §4, every geometry-dependent script | stdlib only |
| `sweep_trade.py` | **Coupled sweep selection** — full VLM + Weissinger NP, trim/twist/reflex, section-Cl margin, self-consistent balance/packaging and NASA TP-1685 divergence trend for −20…−10° candidates | I-21, ADR-0040 | numpy |
| `vlm_ala_volante.py` | Panel vortex lattice for the forward-swept wing (taper + twist). NP, CL_α, load distribution, Cm0-per-degree twist yield | I-07, G8, guide §4.3 | numpy |
| `weissinger_np.py` | **C2: independent NP check** — Weissinger-L swept lifting line (bound vortex on the c/4 line, control points at 3/4 chord). Structurally different formulation from the panel VLM | I-07, C2, G8 | numpy |
| `ventana_torsion.py` | Twist required for trim vs tip-stall margin (torsion window) | I-07, G2 | numpy |
| `calibra_xfoil_e387.py` | XFOIL Ncrit-grid calibration against the measured E387 (C) polar (UIUC, vol. 3) | I-06, G2 | XFOIL |
| `b3_screening.py` | **B3: airfoil screening** — batch XFOIL polars (Re 3e5/5e5 × Ncrit 10/12) for the shortlist in `../geometry/airfoils/`; generates the scaled variants; parses cm0/clmax/α_stall/L/D/cd@cruise | B3, G2, OP-02 | numpy + XFOIL |
| `balance_cg.py` | **OP-01: mass/CG balance** — pack-station solver for the CG target; planform-centroid self-check; bay sizing for the nose boom; envelope checks (AUW, V_stall) | OP-01, justification §3.1–3.2 | numpy |
| `elevon_authority.py` | **Elevon control power** — ΔCm per degree of elevon deflection (step incidence over 30–90 % half-span) via the VLM; trim closure and control margin at SM 8 % | Guide §5.3/§6.1, C6 (partial) | numpy |
| `battery_pack_layout.py` | **I-16: pack envelope** — enumerates every rectangular (n_x,n_y,n_z) layout of the 4S/6S 21700 pack, computes finished envelope (wrapper, nickel, leads) and fit-checks against the pack carrier (guide §8; the 200×70×32 bay is superseded by the cradle) | I-16, guide §8, OP-23 | stdlib only |
| `inav_fc_match.py` | **I-17: FC compatibility** — cross-checks the popular INAV boards (Matek WING, SpeedyBee, Foxeer) against the Salamandra avionics requirements (≥5 PWM, ≥2 UART, ≥1 I2C, blackbox, current, baro, 6S voltage); footprint summary + power budget | I-17, guide §10, CORE avionics | stdlib only |
| `fpv_power_budget.py` | **I-19: FPV power budget** — DJI O4 / Pro / Lite current-per-level (measured `[M]`), power at any input voltage, BEC margin vs the Matek 9V/2A and 5V/2A rails, energy impact on the 6S1P P42A pack | I-19, guide §10, O1 | stdlib only |
| `servo_torque.py` | **I-18: hinge moment** — elevon hinge moment (Ch 0.01–0.05 `[E]`) at V_NE, per-servo with dual actuation, margin vs the catalog | I-18, guide §6.6, OP-06, ADR-0025 | stdlib only |
| `yaw_stability.py` | **I-20: directional stability** — Cnβ budget (finless baseline vs centreline fin), fin sizing tiers V1a/V1b, rudder-authority vs crosswind, yaw damping/subsidence, fin bending at V_NE, mass/drag/stall cost | I-20, first variant (O14), guide §4.4/§6.7, G10 | numpy |
| `joint_pin_trade.py` | **ADR-0031: pin material trade** — carbon Ø6 vs printer filament (PETG/PLA Ø1.75) in the R-JOINT torque couple: strength (FS ≥ 3 all candidates) vs stiffness (E·I: filament ≈ 9000× softer → k_joint collapses → −29 % V_div per ADR-0032) | ADR-0031/0032, guide §6.4 | numpy |
| `filament_dowel_pins.py` | **ADR-0039: dowel pins in the glued joints** — 2 × Ø1.75 filament per segment joint: shear demand at +6 g vs double-shear capacity (FS ≈ 11/24), position clearance (tube/hinge), collar bearing, mass 2.6 g | ADR-0039, guide §6.4/§6.5/§12, OP-27 | numpy |
| `mass_budget.py` | **F2: material mass variants** — per-part material policies (ALL PETG baseline / AERO-PLA wings / PLA+ / arbitrary), battery 4S–6S × P42A/50E (I-16 model), FC catalog (I-17), FPV (I-19), motor/prop/servo options, V1 fin; AUW, g/dm², V_stall, printed cost | docs/06, guide §7.1, F2 (P1/P2), OP-28 | numpy |
| `divergence.py` | **G6 revision 3: absolute divergence speed** — multicell Bredt-Batho J, explicit elastic-axis bracket (no false shear-centre claim), FEM cross-checked by flux-form shooting, −15° sweep-factor band, R-JOINT and tube sensitivities; auditable V_limit | docs/07, I-21, guide §11/§13, OP-29 | numpy |
| `launch_speed.py` | **I-14: hand-launch feasibility (rev. 2)** — release gate V_suelta ≥ V_stall (corrected: k_safe applies post-release, built by acceleration); V_hand band from published biomechanics (van den Tillaar 2004), idle-thrust assist (INAV hover rule T/W ≈ 1.0, idle 0.5–0.67×), Mojito configuration-class anchor `[M]`, torque-roll threshold; INAV/ArduPlane autolaunch settings | I-14 executed, guide §4/§12, D1/D2 | numpy |
| `boom_flexion.py` | **ADR-0040 nose boom Ø8/int6 aluminium + Ø3 aft spar** — imports solved balance geometry; pure cantilever REJECTED (278 MPa, FS 0.99); **two-support PASS** (56 MPa, FS 4.96, δ 1.6 mm, 25.3 Hz); tube+cradle 38.2 g; Ø3 spar gives total 3 mm fin-root EI 1.60× | guide §6.7, OP-24/OP-26 | numpy |

## Reproducing the published results

### 1. Neutral point (I-07, and C2 cross-check — guide §3)

```bash
python3 vlm_ala_volante.py      # in-house method, includes the straight-AR-6 validation
python3 weissinger_np.py        # independent method, includes the same validation
```

Published ADR-0040 result (`[D]`): VLM **x_NP = −75.8 mm** (25.72 % MAC) vs
Weissinger-L **−72.9 mm** (27.0 % MAC) — **2.9 mm agreement**. Both validations must
reproduce: straight AR 6 wing → NP at 25.00 % MAC; CL_α within ~7 % of the Helmbold
formula (the classical 1-D/2-D difference).

### 2. B3 airfoil screening (I-15 §6)

```bash
python3 b3_screening.py --xfoil /path/to/xfoil.exe
```What it does, step by step:

1. Reads the candidate coordinates from `../geometry/airfoils/` (E205, S5010, MH60 —
   provenance in `geometry/airfoils/README.md`).
2. Generates the thickness variants `mh60-12.dat`, `mh60-135.dat`, `e205-9.dat`
   (affine y-scaling — the declared provisional scaling rule of the design guide §6.3).
3. Runs **24 XFOIL cases** (6 airfoils × Re 3e5/5e5 × Ncrit 10/12), alpha sweep
   0–16° step 0.5°, ITER 300, in the calibrated band of I-06.
4. Saves the raw polars in `xfoil_out/<case>.pol` and **verifies each header** carries
   the requested `Re` and `Ncrit` (a polar whose Ncrit failed to apply is regenerated).
5. Prints the summary table: cm0 (linear fit of CM(CL) evaluated at CL=0, about c/4),
   clmax, α_stall, (L/D)max, cd at cruise CL 0.132.

**Incremental:** polars whose header already matches are reused — rerunning after a
crash only recomputes the missing cases.

**Batch-mode notes for XFOIL 6.99 on Windows** (all baked into the script, kept here
for anyone maintaining it):
- The Ncrit command lives in the **VPAR** submenu (`OPER` → `VPAR` → `N <value>`);
  `NCRIT` does not exist in this version.
- Polar accumulation is `PACC` (prompts: save-file name, then dump-file name — blank
  to decline), then `ASEQ`; close with `PACC` (off) and `PWRT 1 <filename>`.
- The input stream must be a **CRLF file redirected as stdin** (a PowerShell pipe
  truncates it; the Fortran runtime reads until EOF and prints a harmless
  "Fortran runtime error: End of file" after QUIT — ignored).
- Full paths in the polar filenames are fine.

Published result highlights (I-15 §6.2, `[D]`):
- E205 **discarded**: cm0 ≈ −0.07 (fails R-AIRFOIL by ~0.08).
- MH60→13.5 %: cm0 = +0.0016 (Re 5e5, Ncrit 10); published cm0 values are not
  achieved at project Re.
- At SM 8 % no off-the-shelf candidate closes trim inside R-TWIST ≤ 3.0° unaided.
  The favourable provisional polar closes at about 0.6° permanent reflex, but the
  adverse Ncrit-12 polar requires about 1.9° and fails that cap
  (`elevon_authority.py`); final B3 polars are a CAD gate.

### 3. Balance and CG reachability (OP-01, guide §8.2)

```bash
python3 balance_cg.py
```

Self-validating: it imports the canonical planform, computes the shell and carbon
stations, iterates boom mass/length with the pack solution, and solves all four P42A
pack stations at target CG **−93.8 mm** (SM 8 %).

Published results (I-21/ADR-0040, `[D]`): pack stations 4S1P **−501** / 6S1P
**−373** / 4S2P **−306** / 6S2P **−237 mm**; 6S1P band −392…−354; cradle
−473…−272; support span 341 mm; AUW 1685 g → V_stall 45.9 km/h.

### 4. Elevon authority (guide §5.3/§6.1)

```bash
python3 elevon_authority.py
```

Models the elevon as step incidence over 30–90 % half-span in the same VLM (no section
Cm0 — the section cm0 is added as the B3 screening datum). Results at the −15° planform:
elevon yield 0.00256 Cm/° vs 0.00249 Cm/° full-span wash-in; 5° elevon gives 2.6×
the limiting trim deficit. The favourable provisional polar needs ≈ 0.6° permanent
reflex; the adverse Ncrit-12 polar needs ≈ 1.9°, outside the cap.

### 5. Twist window (I-07)

```bash
python3 ventana_torsion.py
```

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
`200 × 70 × 32 mm` reference bay (guide §9), plus per-cell and per-pack mass /
energy / discharge for the two reference cells (Molicel P42A, Samsung 50E) and
their average. Published results (I-16 §4–§5, §6.1):
**6S1P = 2×3 orient. A → 153.2 × 64.5 × 22.2 mm**,
**4S1P = 2×2 → 153.2 × 43.2 × 22.2 mm** — the envelopes that fit the current
provisional bay (all others are buildable with a resized bay). Pack masses:
6S1P P42A 445 g / 50E 433 g / avg 439 g; 4S1P 305 / 297 / 301 g. A change to the
fit test, assembly allowances, or cell specs must reproduce these values.

### 7.1 Servo hinge moment (I-18)

```bash
python3 servo_torque.py
```

Hinge moment of the 0.28 c elevon (390 mm span) at V_NE 180 km/h over Ch
0.01–0.05 `[E]`: **19–96 mN·m per elevon → 10–48 mN·m per servo** (dual
actuation). The most modest catalog servo (MG90S ≈ 180 g·cm) has ≥ 3.7× margin —
**static torque is not the binding constraint** (I-18 §2). A change to the
geometry, Ch band, or V_NE must reproduce the margin table.

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
(I-17 §6): 5 V rail 300–555 mA, avionics ≈ 6.6 W ≈ 6 % of cruise, ≈ 7.3 % of a
6S1P P42A pack per flight-hour. A change to the requirement set or board specs
must reproduce these lines.

### 9. FPV power budget (I-19)

```bash
python3 fpv_power_budget.py [input_V]
```

Per-level power of the DJI O4 / Pro / Lite from measured currents `[M]`.
Published results (I-19 §5): O4 Pro 1200 mW = 10.4 W, O4 standard max 9.5 W
(700 mW cap), O4 Lite 6.0 W; 9 V rail utilization ≤ 58 %; total electronics
avionics+FPV = 17.0 W (15.5 % of cruise) and 18.8 % of the 6S1P P42A pack per
flight-hour with the Pro. A change to the current table or BEC assumptions must
reproduce these values.

### 10. Directional stability and the fin variant (I-20)

```bash
python3 yaw_stability.py
```

Cnβ budget of the finless baseline (body + FSW wing: **−0.0006…−0.0015/deg — negative**),
centreline-fin sizing for the two stability tiers (V1a 2.16 dm² → nominal +0.0005/deg;
V1b 2.86 dm² → +0.0010/deg), rudder authority vs crosswind, yaw damping and
subsidence, fin bending at V_NE (**root t ≥ 3.0 mm**), and the mass/drag/stall cost of
each tier. In-service datum `[M]`: the TBS Mojito (same
FSW + nose + pusher layout) flies a **fixed** stabilizer with elevons only — no rudder
servo (product page, manual, official INAV CLI). Published results (I-20 §5, `[D]` on
`[E]` bands): finless yaw divergence τ ≈ 0.7 s; V1a ΔCD0 +0.0015 (+9.9 % drag);
V1b +13.0 %; both tiers push V_stall past 45 km/h at the current budget (OP-24 lever
applies). A change to geometry, bands or methods must reproduce the seven validation
cases (Helmbold, fin reference, Raymer body, tier consistency, damping reference).

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
python3 mass_budget.py --config all_petg --fc F765-WING --fpv O4-Lite
```

Data-driven weight budget with per-part material selection. Reproduces the guide §8.1
baseline with the I-16 `[D]` P42A pack and the ADR-0040 hybrid boom assembly.
Published results (docs/06 §3): ALL PETG **1685.2 g / 45.9**; **AERO WINGS
1506.3 g / 43.4** (stall-compliant but fails the conservative divergence model);
AERO MAX 1455.2 g / 42.6; PLA+ 1669.6 g
(ADR-0016 rejected material). Twelve validation cases — a change to materials, parts,
packs or options must reproduce them.

### 14. Absolute divergence speed (G6 revision 3 — docs/07)

```bash
python3 divergence.py
```

Revision 3 removes the invalid enclosed-area-centroid/shear-centre identification and
uses an explicit xEA/c = 0.30…0.45 uncertainty bracket. Results at −15° sweep:
**nominal 325.3 km/h (1.36× PASS), conservative 128.8 km/h (0.54× FAIL), AERO
91.1 km/h** vs the 240 km/h criterion. GXY = 0.69 GPa gives 179.0 km/h; the combined
GXY+gyroid+1.1 mm wall case reaches only 206 km/h. Initial V_limit is **105 km/h**
(0.85× conservative, rounded down); **150 km/h** only after S3 validates GXY.

### 15. Hand-launch feasibility (I-14 executed, rev. 2 — guide §4/§12)

```bash
python3 launch_speed.py
```

Gate check of the mandatory hand throw, rev. 2 (the first revision wrongly demanded
k_safe = 1.20 at the release instant; the correct gate is V_suelta ≥ V_stall — the
margin is built by motor acceleration in 0.2–0.4 s). **Result: FEASIBLE — typical
throw 10.5 m/s + ref idle → 13.4 m/s (48.4 km/h) at release (k = 1.05), k = 1.20 in
0.39 s; firm throw → 17.3 m/s (62.4 km/h, k = 1.36). Weak throw stays below stall:
technique is part of the specification.** Anchored on the Mojito configuration class
`[M]` (1800 g, higher reported stall, hand-launched in service) and published
biomechanics (van den Tillaar 2004). Nine validation cases must pass. Autolaunch
settings table in research/I-14 §3.2.

### 16. Nose boom Ø8/int6 aluminium + Ø3 aft spar (ADR-0040 — guide §6.7)

```bash
python3 boom_flexion.py
```

User decision 2026-08-06: the battery boom is an **aluminium tube Ø8 / int Ø6
(wall 1.0 mm)** with a printed cradle, and a **Ø3 mm aluminium spar** stiffens
the V1 fin near the trailing edge; carbon optimisation deferred (ADR-0015).

- **Pure cantilever REJECTED** (`[D]`): +6 g with the 445 g pack →
  σ 278 MPa vs 276 (6061-T6), δ 39 mm, first mode 6.2 Hz.
- **Two-support arrangement ADOPTED** (`[D]`): pack at −373 mm between the forward
  support (x ≈ −473) and CORE support (x ≈ −132) → σ 56 MPa (FS 4.96),
  δ 1.6 mm, mode 25.3 Hz. The cradle is a structural requirement, not
  packaging.
- Mass: 391 mm tube 23.2 g + cradle 15 g = **38.2 g**; tip skid = crush zone.
- Ø3 fin spar: 3.0 mm root EI ×1.60 (0.278 + 0.463 N·m²), 5.7 g.
- Twelve validation cases must pass.

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
