# Salamandra — Release v0.5.0: Verification Integrity and the Connected Design Contract

**Date:** 2026-08-18 · **Tag:** `v0.5.0` · **Status:** RELEASED

**Controlling specification:**
[Salamandra Design Guide v0.23](../design/Salamandra-Design-Guide-v0.1.md)

Release v0.4.0 published a *connected* calculation baseline. A full senior-level audit of
the 33 modules in `calculations/` — [`docs/12`](12-calculation-system-audit-and-remediation.md),
every finding measured by executing the code — then established that the connection was
partly nominal: twelve physical quantities were declared in two or more places, the
published neutral point was a hand-copied literal, two modules disagreed by a factor 1.76
on the same yaw inertia, several validation checks could not turn red, and the
documentation CI aborted at install time so no gate was actually enforcing anything.

**Release v0.5.0 closes that class of defect.** It also releases the Article #1 elevon
geometry decision (ADR-0045) and the generated technical drawing set that had accumulated
as post-v0.4.0 working changes.

The engineering delta is deliberately small and it is stated exactly, in §3.4. What
changed at scale is not the numbers — it is that the numbers are now re-derived on every
run, own exactly one declaration site, and are guarded by checks that have been **proven
able to fail**.

This release does **not** claim flight qualification. E2 aerodynamic acceptance, F2 mass
verification, S3 printed-structure properties, G7 flutter, G10 yaw identification and
G11 dynamic gust response all remain physical acceptance gates. The 105 km/h operational
cap stands.

---

## 1. Authority and migration rule

Use the released documents in this order:

1. **Design Guide v0.23** controls CAD geometry, interfaces, operating limits and
   structural load definitions.
2. `calculations/design_config.py` owns chosen design inputs; `calculations/aero_contract.py`
   owns derived aerodynamics; `calculations/drag_model.py` owns the polar. **No other
   module may declare any of them** — [ADR-0046](../decisions/ADR-0046-single-declaration-contract.md).
3. ADR-0041…ADR-0046 record the adopted decisions.
4. I-22…I-27 and `docs/12` record the audits and evidence; the open-points register
   controls unresolved physical gates.

Do not average conflicting values and do not combine historical inputs with the current
baseline. Release v0.4.0 remains the immutable v0.21 snapshot and an audit record.

## 2. Highest-ROI changes

| Priority | Defect closed | Return |
|---:|---|---|
| 1 | A published, safety-critical quantity — the neutral point that sets the CG target — was a frozen literal no test compared against its solver | The project's most repeated failure mode (#3, re-derivation) is removed from the source of its most consequential number |
| 2 | Three validation checks compared two literals, or reduced algebraically to an identity, or asserted that a problem still exists | The verification can now fail; 19 seeded defects prove it, and three of them survived the first run |
| 3 | `npm ci` aborted before any documentation gate ran, and the calculation suite was never in CI at all | The gates run instead of failing at install time; a desynchronising change is blocked by CI, not found by audit |
| 4 | One yaw inertia declared twice, with a factor 1.76 between the two values | A published dynamic result was 33 % low; it is corrected and its band is now actually propagated |
| 5 | Five speeds with five roles and nothing asserting their order; `V_A` sitting above the speed used as `V_C` | Ladder inversion is impossible; the 105 km/h cap is declared an operational limit, not a Part 23 `V_C` |
| 6 | Drag treated three incompatible ways, one of them the single lumped coefficient ADR-0009 forbids | ADR-0009 is honoured by construction: every consumer receives viscous and induced terms separately |

## 3. Released engineering values

### 3.1 The design contract

| Quantity | Owner | Released value |
|---|---|---:|
| Neutral point, VLM 40×6 | `aero_contract.py`, re-derived | **−75.79 mm · 25.72 % MAC** `[D]` |
| Neutral point, Weissinger-L ny=100 | `aero_contract.py`, re-derived | **−72.90 mm** `[D]` |
| Declared method spread | — | 2.9 mm |
| Bounded mesh error | asserted | ≤ 0.4 mm |
| CG target, 8 % static margin | derived, not copied | **−93.784 mm** `[D]` |
| Yaw inertia `I_zz` | `equipment_layout` 3-D mass model | **0.1587 kg·m²** `[D]`, band 0.1349–0.1825 `[E]` |
| V1a reduced 2-DOF yaw pair | `yaw_stability.py` | **λ = −1.233 ± 5.205j 1/s** (ω_n 5.35 rad/s, ζ 0.231) `[D]` |
| Cruise polar | `drag_model.py` | CD = CD_visc + CD_ind, **returned separately**; best glide L/D 17.15 at CL 0.4665 `[D on E inputs]` |
| Launch drag | banded, not lumped | **0.0346** attached decomposition … **0.0798** separated-flow allowance `[E]`; the gate is judged on the conservative end |

The published literals survive only as **regression anchors with a declared tolerance**
(±0.5 mm on the neutral point). Re-derivation reproduces them.

### 3.2 Article #1 elevon geometry (ADR-0045 / I-27)

| Quantity | v0.4.0 release | v0.5.0 released value |
|---|---:|---:|
| Elevon span, each side | y 195…585 mm · 390 mm | **y 227.5…585.0 mm · 357.5 mm** (35–90 % half-span) |
| Elevon chord | 0.28 c | 0.28 c (unchanged; 0.24 and 0.32 c evaluated and rejected) |
| Moving area | 221.1 cm² | **199.0 cm²** (−10.0 %) |
| Fixed PANEL-root trailing-edge bridge | none | **32.5 mm**, y 195…227.5 |
| Fixed tip | 65 mm | 65 mm (unchanged) |
| Servo station | y ±390 mm | **y ±406.25 mm** |
| Rigid-VLM roll derivative retained | 1.000 | **0.945** |
| Roll damping `Cl_p` | — | **−0.4160 /rad** `[D]` |
| Hinge-moment proxy | 1.000 | **0.883** (−11.7 %) |
| DS-939MG factored static margin at 180 km/h | 1.36× | **1.52×** |
| Limiting Ncrit-12 neutral trim | +0.50° | +0.500°, inside the ±0.6° cap |

Actuation is **two servos, one per elevon** (C35, ADR-0026). The former `sqrt(2)`
flutter-frequency credit assumed an unmeasured doubling of effective hinge stiffness and
is withdrawn pending G7 evidence. No flap mode, throw improvement or flutter-speed credit
is claimed.

### 3.3 Mass, stall and load envelope

| Configuration | AUW | Predicted stall | Margin to the 1,620.4 g exact stall-mass limit |
|---|---:|---:|---:|
| SALAMANDRA-CLEAN | **1,553.25 g** | 44.1 km/h | 67.2 g |
| SALAMANDRA-V1 lower model | **1,596.26 g** | **44.66 km/h** | **24.1 g** |

The load definitions released in v0.4.0 are unchanged — **+6/−3 g manoeuvre limit,
+9/−4.5 g ultimate** — and are now recomputed at the two-servo masses:

| Quantity | CLEAN | V1 lower model |
|---|---:|---:|
| Manoeuvring speed `V_A` | 107.9 km/h | 109.4 km/h |
| Positive manoeuvre boundary at the 105 km/h cap | 5.68 g | 5.53 g |
| Inverse reference gust reaching +6 g | 6.30 m/s | 6.41 m/s |
| Inverse reference gust reaching −3 g | 5.04 m/s | 5.13 m/s |

`V_A` sits **above** the 105 km/h cap for every released mass. That is not an error and it
is no longer hidden: 105 km/h is an **operational cap**, not a Part 23 design cruising
speed `V_C`, and `design_config.validate_geometry` now asserts the relationship instead of
leaving it silent (C41). The full 15.24 m/s reference gust remains a **screen only** — it
implies CL ≈ 1.36, more than twice the released wing `CLmax` 0.589 — reported under G11 as
a diagnostic, never asserted as a design load.

### 3.4 Exact engineering delta from guide v0.22

A late finding, recorded as **C44**: C40 corrected the yaw inertia in the code but four
documents kept quoting the pre-C40 modes — including the **E8 acceptance criterion**, the
number a flight test would have been compared against. Corrected here to finless
divergence τ **0.16 → 0.12 s** and V1a decay τ **1.3 → 0.8 s**. The lesson is worth
stating plainly: the lint and the mutation suite guard the *code*; a number transcribed
into prose is still a manual re-derivation obligation.

| Moved | Did not move |
|---|---|
| V1a yaw mode: ω_n 4.03 → **5.35 rad/s**, ζ 0.197 → **0.231** (C40); quoted decay τ 1.3 → **0.8 s** and finless divergence τ 0.16 → **0.12 s** (C44) | Planform, airfoil coordinates, +3.0° wash-in, materials |
| Launch drag: single lumped 0.08 → **declared band 0.0346…0.0798** (C42) | Published launch conclusion: typical throw 12.9 m/s vs V_stall 12.4 m/s |
| CG target: **+0.017 mm**; battery station **+0.04 mm**, against ±5 mm (C39) | Component masses, CG band, propulsion boundary |
| `docs/09` neutral point: −75.9/−75.8 mm inconsistency → **−75.79 mm** (C39) | 105 km/h operational cap, 160 km/h article `V_NE` |
| `V_NE` split into `V_ARTICLE_NE` (160) and `V_STRUCTURAL` (180) (C41) | Every speed **value** in the ladder |

Nothing physical moved except the yaw mode. What moved is that the numbers are re-derived,
singly declared and defended by checks that can fail.

### 3.5 Published drawing set

Four A3 sheets are generated, manifest-verified and published automatically (C37):

| Sheet | Content | Scale |
|---|---|---|
| `SLM-GA-001` | General arrangement — planform, modular stations, CG/NP, provisional fuselage OML | A3 · 1:4 |
| `SLM-GA-002` | Side elevations | A3 · 1:4 |
| `SLM-EQP-001` | Equipment mass skeleton | A3 · top 1:6.5 / side 1:4 |
| `SLM-WNG-001` | Right half-wing layout | A3 · plan 1:2 |

All four carry `DRAFT — NOT FOR MANUFACTURE`. `calculations/drawing_index.py` holds the
single registry; `geometry/drawings/manifest.json` records each sheet's SHA-256, and the
README gallery, the folder index and the wiki are all published from it. The wiki refuses
to build when a served sheet does not match its recorded digest.

## 4. v0.4.0 → v0.5.0 migration

| Driver | v0.4.0 | v0.5.0 |
|---|---|---|
| Shared-quantity ownership | Prose rule in `CLAUDE.md` | **ADR-0046**: `design_config` / `aero_contract` / `drag_model`, enforced by `contract_lint.py` |
| Neutral point | Hand-copied literal | Re-derived and cached; literal retained as ±0.5 mm anchor |
| Verification | 51 contracts, 20 CLIs, unproven | **112 contracts, 28 CLIs, 19 seeded defects all caught** |
| CI | `docs.yml` only, `npm ci` broken | `docs.yml` repaired **+ `calculations.yml`** on a Python × numpy matrix |
| Elevons | 390 mm, four servos assumed in earlier text | **357.5 mm, two servos** |
| Drawings | Not published from the generator | Four manifest-verified A3 sheets in README, folder index and wiki |
| Yaw inertia | 0.28 kg·m² `[E]` and 0.1587 `[D]`, both accepted | **0.1587 kg·m² `[D]`**, ≤10 % cross-check, band propagated |
| Suite runtime | `divergence.py` 33 s | **1.7 s**; full cross-module suite **36.5 s** `[M]` |

**CAD impact.** Existing 390 mm elevon solids, hinge strips, pockets, balance values and
servo stations are obsolete for Article #1 and must be regenerated at 227.5…585.0 mm with
the servo at y ±406.25 mm. The planform, r1 airfoil coordinates, twist, materials,
stations and speed limits are unchanged; nothing else requires rework.

## 5. Released package

| Artifact | Release role |
|---|---|
| [`design/Salamandra-Design-Guide-v0.1.md`](../design/Salamandra-Design-Guide-v0.1.md) | **v0.23 controlling CAD and engineering specification** |
| [`design/Design-Guide-Justification-v0.1.md`](../design/Design-Guide-Justification-v0.1.md) | v0.18 evidence and derivations |
| [`design/Design-Guide-Open-Points-v0.1.md`](../design/Design-Guide-Open-Points-v0.1.md) | v0.18 unresolved gates and triggers |
| [`decisions/ADR-0045-article-1-elevon-geometry.md`](../decisions/ADR-0045-article-1-elevon-geometry.md) | Article #1 control-surface geometry |
| [`decisions/ADR-0046-single-declaration-contract.md`](../decisions/ADR-0046-single-declaration-contract.md) | **Single-declaration architecture rule and its enforcement** |
| [`docs/12-calculation-system-audit-and-remediation.md`](12-calculation-system-audit-and-remediation.md) | The measured audit and the remediation programme it drove |
| [`research/I-27-elevon-geometry-trade.md`](../research/I-27-elevon-geometry-trade.md) | Elevon span/chord/tip trade evidence |
| [`research/I-20-yaw-stability-centerline-fin.md`](../research/I-20-yaw-stability-centerline-fin.md) | Yaw stability, re-derived at the single-source inertia (C44) |
| [`research/I-25-svg-technical-drawing-workflow.md`](../research/I-25-svg-technical-drawing-workflow.md) | Drawing workflow and validation |
| [`calculations/aero_contract.py`](../calculations/aero_contract.py) | Derived neutral point, CG target, lift slope, canonical meshes |
| [`calculations/drag_model.py`](../calculations/drag_model.py) | The single polar, viscous and induced terms separated |
| [`calculations/contract_lint.py`](../calculations/contract_lint.py) | Single-declaration enforcement |
| [`calculations/mutation_test.py`](../calculations/mutation_test.py) | 19 seeded defects; proof the suite can fail |
| [`calculations/elevon_sizing.py`](../calculations/elevon_sizing.py) | Elevon geometry trade |
| [`calculations/generate_blueprints.py`](../calculations/generate_blueprints.py) | Drawing set, manifest and published index blocks |
| [`geometry/drawings/manifest.json`](../geometry/drawings/manifest.json) | Sheet registry with SHA-256 per sheet |
| `.github/workflows/calculations.yml` | Required calculation gate |

## 6. Reproduction and release verification

```bash
python3 calculations/verify_calculations.py
python3 calculations/contract_lint.py
python3 calculations/mutation_test.py
python3 calculations/generate_blueprints.py --check
python3 -m compileall -q calculations
cd wiki
node scripts/gen-site.mjs --strict
npm run check:refs
npm run build
```

Measured on the release commit (Python 3.12.3, numpy 1.26.4, Linux x86-64):

| Gate | Result |
|---|---|
| Cross-module interface contracts | **112 / 112 PASS** |
| Deterministic script validations | **28 / 28 PASS** |
| Contract lint | ALL PASS — no physical quantity declared twice |
| Mutation test | **19 / 19 seeded defects caught** |
| Drawing set `--check` | ALL PASS — sheets, manifest and published blocks current |
| Wiki strict generation / reference check / production build | PASS — 115 markdown files, 108 pages, no broken local links |
| `git diff --check` | clean |
| Full cross-module suite runtime | 36.5 s (mutation suite 108 s) |

External workflows not run in the harness and unchanged by this release: XFOIL-dependent
`airfoil_reflex_trade.py`, `b3_screening.py` and `calibra_xfoil_e387.py`.

## 7. Gates that remain open

| Gate | Released state | Closure required |
|---|---|---|
| **E2 / G2 — aerodynamic acceptance** | Salamandra r1 computational baseline; polars are `[D]`, never `[M]` | Printed-section or aircraft lift, drag, moment and stall measurements |
| **F2 / OP-24 — V1 mass** | V1 lower model 1,596.26 g, 24.1 g below the exact stall-mass limit | CAD mass verification and complete-aircraft scale measurement |
| **S3 / OP-29–30 — printed structure** | 105 km/h operational cap retained; conservative `V_div` 129.6 km/h still short of the 240 km/h criterion (G6 open, reported not asserted) | Measured GXY/GJ, elastic axis and complete-wing torsion |
| **G7 — flutter** | Two-servo actuation released **without** the withdrawn `sqrt(2)` stiffness credit | Hinge stiffness and modal evidence, E5 |
| **G10 / E8 — yaw** | V1a mode damped across the whole declared inertia band; E8 acceptance predictions re-derived at the single-source inertia (C44) | CAD side-area check and flight yaw-decay identification |
| **G11 / E9 — dynamic gust and negative lift** | Rigid reference screen reported as a diagnostic, not adopted; no defensible `CLmin` | Nonlinear unsteady model, negative-polar evidence, E9 correlation |
| **D2 / E3 — propulsion and energy** | Power/drag boundary connected; equilibrium open | Motor/ESC/prop bench map, E2 aircraft drag, 95 km/h flight Wh/km |
| **OP-21 / F2 — fuselage OML** | Continuous OML concept on the drawings is `[I]`, amber and provisional | Native parametric CAD freeze |

Release v0.5.0 is suitable for continued CAD and analysis within these gates. It does not
authorize flight above 105 km/h, use of the reference gust screen as a design load, or
treating calculated aerodynamic and printed-material values as measured evidence.
