# Salamandra — Release v0.6.0: Twin-Fin Architecture and the Parametric Fuselage Programme

**Date:** 2026-08-19 · **Tag:** `v0.6.0` · **Status:** RELEASED

**Controlling specification:**
[Salamandra Design Guide v0.24](../design/Salamandra-Design-Guide-v0.1.md) (concise, CAD
execution) and
[Advanced Design Guide v0.24](../design/Salamandra-Design-Guide-Advanced-v0.1.md)
(engineering context). Both describe the same released baseline.

Release v0.5.0 made every number own exactly one declaration site and proved the
verification suite could fail. It left two shapes undefined: **where the directional
surfaces go**, and **what the body actually is**. Both were carried as `[I]` sketches on
the drawings — a single fin floating behind the propeller, and a fuselage outline that
existed only as hand-placed Bézier control points in the drawing generator.

**Release v0.6.0 replaces both sketches with derivations.** The centreline fin is rejected
and superseded by two CORE-rooted fins whose station is the output of a propeller-clearance
and mass/CG trade, not an assumption. The body becomes a reproducible parametric surface
generated around the equipment skeleton, with a containment audit that a candidate can
fail.

This is a **minor increment** under [`docs/15`](15-how-to-publish-a-release.md) §1.1: the
V1 CAD baseline changes architecture, and a new verified capability (automatic OML
generation and audit) enters the repository. It does **not** claim flight qualification.
E2, F2, S3, G7, G10 and G11 remain physical acceptance gates and the 105 km/h operational
cap stands.

---

## 1. Authority and migration rule

1. The **concise Design Guide v0.24** is the CAD execution authority.
2. The **Advanced Design Guide v0.24** carries the derivations behind it. Where the two
   appear to disagree, the release is blocked until they are reconciled — they do not
   disagree in this release.
3. Generated artifacts (`geometry/drawings/`, `geometry/fuselage/provisional/`) are
   **review data**, not manufacturing authority. Every sheet retains
   `DRAFT — NOT FOR MANUFACTURE`.
4. Anything marked `[I]` — including the entire fuselage outer mould line — may change
   without a release. It must not be cut, printed or committed to tooling.

**Corrections packaged:** C45–C48 from the pre-release work, plus **C49** (one numpy
support window), **C50** (the released fin geometry the changelog had not re-derived) and
**C51** (the wiki link rewrite that broke the audit's evidence links and a required CI
step). All three were found while cutting this release, which is what the procedure in
[`docs/15`](15-how-to-publish-a-release.md) is for.

## 2. Highest-ROI changes

| # | Change | Why it matters |
|---|---|---|
| 1 | **Twin CORE-rooted fins replace the centreline fin** (C47, I-29) | The rejected architecture put a load path and a fin root across the x = +235 mm propeller plane. The replacement is clear of the disc by construction. |
| 2 | **Fin station is derived, not assumed** (C48, I-30) | `x_AC = +285 mm` was an assumption. A +225…+325 mm station trade, coupled to clearance, mass and CG, selects the feasible minimum-score station. |
| 3 | **The fuselage becomes a generated surface** (I-28 Revision 3) | `fuselage_geometry.py` lofts a superelliptic body around the equipment skeleton and audits containment; `fuselage_trade.py` scores candidate families. The body can now fail a check. |
| 4 | **Design Guide split into concise + advanced** | The CAD executor gets an execution document; the engineering context keeps its full traceability. |
| 5 | **A written release procedure** ([`docs/15`](15-how-to-publish-a-release.md)) | Releases stop depending on one person's memory of what must be refreshed. |
| 6 | **The numeric-stack support window is one window again** (C49) | The declared floor, the enforced floor and the CI matrix floor disagreed; CI was still testing a numpy the code cannot run on. |
| 7 | **The documentation CI is green again** (C51) | The wiki link rewrite carried source line anchors onto a generated page, breaking 14 evidence links of `docs/12` and failing a required workflow step on `main`. |

## 3. Released engineering values

### 3.1 V1a directional architecture (ADR-0038, I-29, I-30)

| Item | Released value | Authority |
|---|---|---|
| Configuration | Two identical fixed fins rooted in the aft CORE at y = ±140 mm; **no rudder** | `FIXED [D]` |
| Total fin area | **S_v = 6.1437 dm²** (two surfaces) | `[D]` |
| Fin planform, each | b_v **247.9 mm**, c_r **170.9 mm**, c_t **76.9 mm**, AR_v 2.0, taper 0.45, LE 20°, Λc/4 **15.064°**, MAC 129.9 mm | `[D]` |
| Fin aerodynamic centre | **x = +115.5 mm**, arm l_v = **209.3 mm** | `[D]` |
| Fin root LE / TE | x = **+43.6 / +214.6 mm**; tip LE / TE x = +133.8 / +210.8 mm | `[D]` |
| Root supports | 18 × 14 mm booms, x = +156.0…+216.6 mm at y = ±140 mm | `[D]`/`[E]` |
| Propeller clearance | **29.4 mm nominal** radial, **13.4 mm residual** after the declared 16.0 mm allowance; controlling **axial residual 8.33 mm**; projected side overlap zero | `[D]` on `[E]` |
| Directional stability | Fin Cnβ **+0.00151 /deg**; V1a total nominal **≈ +0.00050 /deg** (band −0.00029…+0.00119) | `[D]` on `[E]` bands |
| Fin volume coefficient | V_v = 0.035 (tailless practice ≈ 0.02–0.05 `[I]`) | `[D]` |
| Drag cost | ΔCD0 **+0.0034** → **+23.1 %** against the CLEAN polar; ≈ 1.42 Wh/km | `[E]` |
| Mass | Lower analytical assembly **48.73 g** = 35.61 g shells/mounts + 10.07 g spars + 3.04 g supports, against the **60.00 g** allocation → **+11.27 g** margin | `[D]` on `[E]` |
| Fin section | Symmetric biconvex plate, 3.0 mm root → 1.5 mm tip, external Ø3 mm aluminium LE nose | `PROVISIONAL [E]` |

### 3.2 Fuselage OML programme (I-28 Revision 3)

The body is no longer a drawing. `fuselage_contract.py` declares the skeleton and the
acceptance thresholds, `fuselage_geometry.py` generates a globally smooth superelliptic
loft and audits it against the equipment envelopes, and `fuselage_trade.py` scores three
candidate families on a seeded Latin hypercube with a Pareto filter.

| Item | Released state |
|---|---|
| Review selection | **`integrated_spindle-000`**, mesh SHA-256 `0b3d79a2…`, 72 × 81 mesh, seed 2801 |
| Status | **Geometry feasible: true · Aircraft feasible: false** — the open gates are visible, not hidden |
| Area distribution | Maximum **9300 mm² at x = −22.6 mm**, inside the root band, one dominant peak, no payload-to-root neck, no long parallel sides |
| Nose | Outer nose x = **−474.7 mm**; camera lens face x = −452.7 mm; **22 mm aperture reserved, not cut** |
| Containment | Every audited envelope passes with margin — camera **+11.53 mm**, VTX **+9.48 mm**, battery inside its travel in both variants |
| Battery station | CLEAN **x = −337.74 mm**, V1 **x = −363.27 mm**; travel −371.20…−336.10 mm, both reachable |
| Authority | **All OML dimensions and transitions are `[I]`.** The surface takes no structural credit and is not CAD. |

The rejected Revision 2 `lifting_saddle` surface is retained in
`geometry/fuselage/provisional/` as trade history, exactly as a cancelled ADR is retained.

### 3.3 Mass, stall and balance

| Configuration | AUW | Wing loading | V_stall | Limit |
|---|---:|---:|---:|---|
| CLEAN (finless) | **1553.25 g** | 55.1 g/dm² | **44.1 km/h** | 45 km/h |
| V1 (twin fin, analytical lower assembly) | **1601.98 g** | — | **44.74 km/h** | 45 km/h |
| V1 at the full 60 g allocation | 1613.2 g | — | 44.9 km/h | 45 km/h |

The V1 margin to the stall requirement is **analytical and small**. It is an F2/OP-24 gate,
not a closed result.

### 3.4 Exact delta from release v0.5.0

**Changed:** directional architecture and all fin geometry; V1 mass, CG solution and
battery station; the fuselage OML from `[I]` styling curves to a generated, audited
surface; the drawing set from four sheets to six; the Design Guide from one document to a
concise/advanced pair; the numeric-stack support window (C49).

**Unchanged:** planform (b 1300 mm, S 0.282 m², AR 5.99, taper 0.50, MAC 225.0 mm, Λc/4
−15°), Salamandra r1 airfoil coordinates and 3.0° wash-in, elevon geometry released by
ADR-0045 (357.5 mm surfaces, two servos at y ±406.25 mm), materials, load envelope
(+6/−3 limit, 1.5 ultimate), CG target −93.8 mm at 8 % static margin, the 105 km/h
operational cap and the 160 km/h article `V_NE`.

### 3.5 Published drawing set

Six manifest-verified A3 sheets, each with a SHA-256 in
[`geometry/drawings/manifest.json`](../geometry/drawings/manifest.json):

| Sheet | Role |
|---|---|
| `SLM-GA-001` | General arrangement, top view |
| `SLM-FUS-001` | **New** — fuselage OML review: plan, side and transverse sections with containment margins and mesh diagnostics |
| `SLM-GA-002` | Side elevations, CLEAN and V1a twin fin, with connected electronics and rear clearance proof |
| `SLM-FIN-001` | **New** — twin-fin review with the top-view propeller-clearance proof |
| `SLM-EQP-001` | Equipment mass skeleton |
| `SLM-WNG-001` | Right half-wing structural layout |

## 4. v0.5.0 → v0.6.0 migration

| Driver | v0.5.0 | v0.6.0 |
|---|---|---|
| Directional surface | One centreline fin on a carrier behind the propeller | **Two CORE-rooted fins at y = ±140 mm, clear of the disc** |
| Fin station | Assumed `x_AC = +285 mm` | **Derived +115.5 mm** from a coupled clearance/mass/CG trade |
| Fuselage | ~50 hand-placed Bézier control points inside the drawing generator | **Generated superelliptic loft with a containment audit and a trade** |
| Body evidence | A silhouette | Two candidate OBJ meshes, a manifest with hashes, and a review sheet |
| Design Guide | One 67 kB document | **Concise execution guide + Advanced reference, same baseline** |
| Release process | Undocumented | [`docs/15-how-to-publish-a-release.md`](15-how-to-publish-a-release.md) |
| numpy window | Declared `>=2.0`, enforced `>=1.24`, CI tested `1.24.4` | **One window: `>=2.0,<3.0` in all three places (C49)** |
| Drawing set | Four sheets | **Six sheets** |

**CAD impact.** Any V1 fin solid, carrier or mount modelled from v0.5.0 is **obsolete**:
the architecture, station, area, planform and attachment all changed. The CLEAN
configuration, the wing, the elevons and the equipment stations are unaffected except for
the V1 battery station (x = −363.27 mm). The fuselage surface is `[I]` review geometry —
it may inform CAD but must not be treated as released.

## 5. Released package

| Artifact | Release role |
|---|---|
| [`design/Salamandra-Design-Guide-v0.1.md`](../design/Salamandra-Design-Guide-v0.1.md) | **v0.24 concise, controlling CAD execution specification** |
| [`design/Salamandra-Design-Guide-Advanced-v0.1.md`](../design/Salamandra-Design-Guide-Advanced-v0.1.md) | **v0.24 canonical advanced engineering reference** |
| [`design/Design-Guide-Justification-v0.1.md`](../design/Design-Guide-Justification-v0.1.md) | Evidence and derivations behind the released values |
| [`design/Design-Guide-Open-Points-v0.1.md`](../design/Design-Guide-Open-Points-v0.1.md) | Unresolved gates and their triggers |
| [`decisions/ADR-0038-fixed-fin-variant.md`](../decisions/ADR-0038-fixed-fin-variant.md) | **Twin fixed-fin variant, re-derived** |
| [`research/I-28-coupled-parametric-fuselage-oml.md`](../research/I-28-coupled-parametric-fuselage-oml.md) | Fuselage programme master plan, Revision 3 |
| [`research/I-29-twin-fin-architecture-correction.md`](../research/I-29-twin-fin-architecture-correction.md) | Architecture correction and its rejected trade history |
| [`research/I-30-fin-station-mass-cg-and-connected-scene-closure.md`](../research/I-30-fin-station-mass-cg-and-connected-scene-closure.md) | **Controlling fin station, mass, CG and clearance closure** |
| [`docs/14-fin-placement-electronics-and-svg-coupling-remediation-plan.md`](14-fin-placement-electronics-and-svg-coupling-remediation-plan.md) | The remediation plan this release executes |
| [`docs/15-how-to-publish-a-release.md`](15-how-to-publish-a-release.md) | Maintainer release procedure |
| [`calculations/fuselage_contract.py`](../calculations/fuselage_contract.py) | Skeleton, corridors and acceptance thresholds |
| [`calculations/fuselage_geometry.py`](../calculations/fuselage_geometry.py) | OML loft, containment audit and mesh export |
| [`calculations/fuselage_trade.py`](../calculations/fuselage_trade.py) | Candidate families, Pareto filter and review selection |
| [`calculations/aircraft_scene.py`](../calculations/aircraft_scene.py) | Shared 3-D scene and propeller hazard |
| [`geometry/fuselage/provisional/oml-manifest.json`](../geometry/fuselage/provisional/oml-manifest.json) | Candidate registry with mesh hashes and audits |
| [`geometry/drawings/manifest.json`](../geometry/drawings/manifest.json) | Six-sheet registry with SHA-256 per sheet |
| `.github/workflows/calculations.yml` | Required calculation gate, matrix corrected by C49 |

## 6. Reproduction and release verification

```bash
python3 -m pip install -r calculations/requirements.txt   # numpy>=2.0,<3.0
python3 calculations/verify_calculations.py
python3 calculations/contract_lint.py
python3 calculations/mutation_test.py
python3 calculations/generate_blueprints.py --check
python3 calculations/drawing_index.py --check
cd wiki && node scripts/gen-site.mjs --strict && npm run check:refs && npm run build
```

Measured on the release commit (Python 3.12.3, numpy 2.5.2, Linux x86-64):

| Gate | Result |
|---|---|
| Cross-module contracts and deterministic scripts | **182 / 182 PASS**, 0 FAIL (32 script CLIs), 58.2 s |
| Contract lint | ALL PASS — no physical quantity declared twice |
| Mutation test | **21 / 21 seeded defects caught** |
| Drawing set `--check` and drawing index `--check` | ALL PASS — six sheets, manifest and published blocks current |
| Wiki reference check / lint / strict generation / build | PASS — 127 markdown files, 115 pages, no unresolved internal links |
| Built-site integrity (`check:site`) | **PASS — 18,187 internal links across 115 pages** (was 14 failures before C51) |
| `git diff --check` | clean |

The same suite on **numpy 1.26.4** now fails with one named contract error
(`unsupported numpy 1.26.4: this repository requires >=2.0,<3.0`) instead of an
`AttributeError` raised three modules deep. That is C49 working.

External workflows not run in the harness and unchanged by this release: the
XFOIL-dependent `airfoil_reflex_trade.py`, `b3_screening.py` and `calibra_xfoil_e387.py`.

## 7. Gates that remain open

| Gate | Released state | Closure required |
|---|---|---|
| **E2 / G2 — aerodynamic acceptance** | r1 computational baseline; polars are `[D]`, never `[M]` | Measured lift, drag, moment and stall |
| **F2 / OP-24 — V1 mass and stall margin** | 1601.98 g analytical, 44.74 km/h against a 45 km/h limit | CAD mass verification and a weighed aircraft |
| **F2 — fuselage OML** | `aircraft_feasible: false`; surface is `[I]` review geometry with no structural credit | Native parametric CAD freeze and the coupled aircraft gates in I-28 §§ gates |
| **S3 / OP-29–30 — printed structure** | 105 km/h cap retained; conservative V_div 129.6 km/h | Measured GXY/GJ, elastic axis, complete-wing torsion |
| **G7 / E5 — flutter** | Unverified | Hinge stiffness and modal evidence |
| **G10 / E8 — yaw** | Twin-fin nominal Cnβ ≈ +0.00050 /deg with a band that crosses zero on its pessimistic end | Flight yaw-decay identification |
| **G11 / E9 — dynamic gust, CLmin** | Reference screen reported, not adopted | Nonlinear unsteady model and flight correlation |
| **G3 — CD0 by component** | Still one lumped `CD_PROFILE_CRUISE = 0.0136` `[E]`; the fin ΔCD0 is the only component term | Component build-up validated against E2 |
| **D2 / E3 — propulsion energy** | Boundary connected, equilibrium open | Bench map and 95 km/h flight Wh/km |

## 8. Known limitations and explicit non-claims

- The fuselage surface is **not** released geometry. `aircraft_feasible` is **false**, and
  the release says so on purpose rather than presenting a shape that looks finished.
- The twin-fin Cnβ band still crosses zero at its pessimistic end. V1a is a **test
  variant**, not a proof of directional stability.
- The V1 stall margin is analytical and under one km/h. No mass has been weighed.
- No flight above the 105 km/h operational cap is authorized, and the gust screen is not
  a design load.
- Nothing in this release has been measured on hardware. Every `[E]` and `[I]` value keeps
  its tag for exactly that reason.
- `geometry/fuselage/provisional/oml-manifest.json` is written with full float precision
  and is **not bit-reproducible across numpy builds**: rerunning `fuselage_trade.py` on a
  different numpy moves last digits (≈1e-15) and dirties the working tree. It has no
  `--check` staleness gate of the kind the drawing set has. Recorded here rather than
  papered over; closing it belongs to the fuselage programme, not to release packaging.
