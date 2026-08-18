# Salamandra — Release v0.4.0: Flight-Load Envelope

**Date:** 2026-08-17 · **Tag:** `v0.4.0` · **Status:** RELEASED

**Controlling specification:**
[Salamandra Design Guide v0.21](../design/Salamandra-Design-Guide-v0.1.md)

Release v0.4.0 promotes the corrected, connected calculation system and the Article #1
flight-load definitions into one controlled engineering baseline. It resolves the
highest-risk ambiguity left after v0.3.0: manoeuvre limit, structural ultimate and gust
screening loads can no longer be mistaken for one another.

This release does **not** claim flight qualification. Dynamic gust response, negative
lift, printed-structure properties, complete-aircraft mass and measured aerodynamic
performance remain physical acceptance gates.

---

## 1. Authority and migration rule

Use the released documents in this order:

1. Design Guide v0.21 controls CAD geometry, interfaces, operating limits and structural
   load definitions.
2. `calculations/design_config.py` owns shared design inputs;
   `calculations/flight_envelope.py` owns the reproducible manoeuvre and gust-reference
   calculations.
3. ADR-0041…ADR-0044 record the adopted decisions.
4. I-22…I-24 record the audits and evidence; the open-points register controls unresolved
   physical gates.

Do not average conflicting values or combine historical inputs with the current
baseline. Existing v0.3.0 CAD remains geometrically current, but all structural checks
must use the v0.4.0 load definitions.

## 2. Highest-ROI changes

| Priority | Defect closed | Released result | Return |
|---:|---|---|---|
| 1 | `+6/−3 g, later +9` mixed limit and ultimate loads | **+6/−3 g manoeuvre limit; +9/−4.5 g ultimate** | Prevents a missing or duplicated safety factor in structural sizing |
| 2 | No connected V-n calculation existed | **VA 109.0/110.4 km/h CLEAN/V1; 5.57/5.42 g at 105 km/h** | Supplies auditable positive manoeuvre loads at the actual released masses |
| 3 | `gust-dominated` was asserted without a valid nonlinear model | Legacy Part 23 result is a **screen only**; G11/E9 remain open | Prevents a rigid linear result outside `CLmax` from becoming a false CAD load |

Correction C34 is part of the same chain: `clmax = 0.65` is the local section screen,
whereas `CLmax = 0.589` is the released three-dimensional wing coefficient used for
stall, mass acceptance and V-n calculations.

## 3. Released engineering values

### 3.1 Manoeuvre and structural loads

| Quantity | SALAMANDRA-CLEAN | SALAMANDRA-V1 lower model |
|---|---:|---:|
| Connected mass | 1,583.5 g | 1,626.5 g |
| Wing loading | 55.09 N/m² | 56.58 N/m² |
| Stall speed, `CLmax = 0.589` | 44.48 km/h | 45.08 km/h |
| `VA = Vs sqrt(6)` | 108.96 km/h | 110.43 km/h |
| Positive manoeuvre boundary at 105 km/h | 5.57 g | 5.42 g |
| Limit normal-force resultants, +6/−3 g | +93.2/−46.6 N | +95.7/−47.9 N |
| Ultimate resultants, +9/−4.5 g | +139.8/−69.9 N | +143.6/−71.8 N |

The negative aerodynamic stall branch is deliberately absent because the repository has
no defensible negative-polar `CLmin`. The `−3 g` operational limit remains a provisional
load case, not a claimed negative-stall boundary.

### 3.2 Gust-reference screen

The official archived Part 23 discrete-gust equation is implemented in SI and checked
independently against its published imperial form. At 105 km/h:

| Quantity | CLEAN | V1 lower model |
|---|---:|---:|
| Full 15.24 m/s reference screen | +12.94/−10.94 g | +12.74/−10.74 g |
| Implied positive `CL` | 1.37 | 1.38 |
| Equivalent gust reaching +6 g | 6.38 m/s | 6.49 m/s |
| Equivalent gust reaching −3 g | 5.10 m/s | 5.19 m/s |

The implied positive lift is more than twice the released wing `CLmax`. The full result
therefore exposes a rigid, linear-model mismatch; it is **not** an adopted design load.
The same screen at 160 km/h also does not authorize flight at that speed. The released
initial limit remains 105 km/h.

## 4. v0.3.0 → v0.4.0 migration

| Driver | Historical v0.3.0 state | v0.4.0 authority |
|---|---|---|
| Calculation integration | Corrected through post-release C29–C32 | One shared-input contract, verified as a release unit |
| Manoeuvre load | Ambiguous `+6/−3`, with `+9` described as later | +6/−3 g limit; +9/−4.5 g ultimate |
| Positive V-n branch | Not published | Connected to actual CLEAN/V1 masses and wing `CLmax` |
| Negative V-n branch | Implicit/undefined | Explicitly open until validated `CLmin` exists |
| Gust load | Called dominant without a dynamic model | Regulatory-reference screen only; G11/E9 control adoption |
| Maximum lift | Section and wing coefficients mixed | `clmax = 0.65` section; `CLmax = 0.589` wing |

There is no CAD rework solely because of this release. The planform, Salamandra r1
coordinates, +3.0° wash-in, materials, component masses, CG station, battery cradle,
propulsion boundary and speed limits are unchanged from the corrected guide v0.20 state.

## 5. Released package

| Artifact | Release role |
|---|---|
| [`design/Salamandra-Design-Guide-v0.1.md`](../design/Salamandra-Design-Guide-v0.1.md) | **v0.21 controlling CAD and engineering specification** |
| [`design/Design-Guide-Justification-v0.1.md`](../design/Design-Guide-Justification-v0.1.md) | v0.16 evidence and derivations |
| [`design/Design-Guide-Open-Points-v0.1.md`](../design/Design-Guide-Open-Points-v0.1.md) | v0.16 unresolved gates and triggers |
| [`decisions/ADR-0044-flight-load-envelope.md`](../decisions/ADR-0044-flight-load-envelope.md) | Load-definition and gust-screening decision |
| [`research/I-24-flight-load-envelope.md`](../research/I-24-flight-load-envelope.md) | Source basis, derivation and scope limits |
| [`calculations/design_config.py`](../calculations/design_config.py) | Shared masses, speeds, load factors and safety factor |
| [`calculations/flight_envelope.py`](../calculations/flight_envelope.py) | V-n and regulatory-reference gust implementation |
| [`calculations/verify_calculations.py`](../calculations/verify_calculations.py) | Cross-module contracts and deterministic-suite runner |

The complete package also includes the v0.3.0 Salamandra r1 geometry and the C29–C32
propulsion, servo, yaw and V1-mass corrections recorded in I-23 and CHANGELOG entries
1.30–1.32.

## 6. Reproduction and release verification

```bash
python calculations/flight_envelope.py
python calculations/verify_calculations.py --all-scripts
python -m ruff check calculations
python -m compileall -q calculations
cd wiki
node scripts/gen-site.mjs --strict
npm run check:refs
npm run check
npm run build
```

Release acceptance requires:

- 51 cross-module contracts passing;
- all 20 deterministic calculation CLIs passing;
- Python lint and compilation passing;
- strict wiki generation, internal-reference checking, Astro type checking and the
  production build passing;
- `git diff --check` reporting no whitespace errors.

## 7. Gates that remain open

| Gate | Released state | Closure required |
|---|---|---|
| **G11 / E9 — dynamic gust** | Rigid regulatory-reference screen implemented and rejected as a final load | Nonlinear unsteady model with plunge/flexibility/spanwise gust, then low-amplitude flight correlation |
| **B3 extension / OP-31 — negative lift** | No negative aerodynamic branch published | Traceable negative-polar analysis or section test supplying `CLmin` |
| **F2 / OP-24 — V1 mass** | CLEAN closes; V1 lower model is 1,626.5 g, 6.3 g above allocation | CAD mass compensation and complete-aircraft scale measurement |
| **E2 / G2 — aerodynamic acceptance** | Salamandra r1 computational baseline released | Printed-section or aircraft lift, drag, moment and stall measurements |
| **S3 / OP-29–30 — printed structure** | 105 km/h initial limit retained | Measured GXY/GJ, elastic axis and complete-wing torsion |
| **D2 / E3 — propulsion and energy** | Power/drag boundary connected | Motor/ESC/prop bench map, aircraft drag and 95 km/h flight Wh/km |

Release v0.4.0 is suitable for continued CAD and analysis within these gates. It does
not authorize flight above 105 km/h, use of the legacy gust screen as a design load, or
treating calculated aerodynamic and printed-material properties as measured evidence.
