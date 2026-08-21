---
title: Glossary and notation
description: Provenance tags, record identifiers, configurations, speed and load definitions, coordinate signs and key aerodynamic terms.
editUrl: https://github.com/bultodepapas/salamandra/edit/main/wiki/content/guide/04-glossary.md
---

Use this page to decode a table or claim. Formal sign and unit definitions remain in the
[project conventions](../reference/04-conventions/).

## Provenance tags

| Tag | Meaning | Required context |
|---|---|---|
| `[M]` | Measured and published by a primary source, or measured by this project | Source, configuration, method and applicable uncertainty |
| `[D]` | Derived by calculation from declared inputs | Equation or script, input provenance and validation case |
| `[E]` | Estimated on declared assumptions | Assumptions, range or sensitivity, and closure trigger |
| `[I]` | Reasoned inference not yet verified | Reasoning and the evidence that would confirm or reject it |

The tags classify **provenance**, not truth. A `[D]` result based partly on `[E]` inputs
remains limited by those estimates. No `[E]` or `[I]` datum may support an irreversible
decision without prior verification.

## Record identifiers

| Pattern | Record |
|---|---|
| `ADR-XXXX` | Architecture/design decision: choice, alternatives, consequences and reversal trigger |
| `I-XX` | Research thread: question, method, sources, findings and limitations |
| `GX` | Gap: missing knowledge and closure condition |
| `EX` | Experimental or flight test |
| `FX`, `SX`, `DX` | Manufacturing/mass, structural and bench/system work items used by the plans |
| `OX` | Objective |
| `R-…` | Requirement or interface rule |
| `CX` | Correction in the changelog |
| `OP-XX` | Open point tied directly to the Design Guide |
| `MP-XX` | Master Plan work package with an explicit dependency and exit state |
| `H01`–`H22` | MP-04 physical hardware-characterisation gates |

## Configurations and modules

- **Article #1** — the first instrumented Salamandra prototype produced by the Master
  Plan. Its final span, sweep and OML have not been selected.
- **SALAMANDRA-6S-R** — first-flight configuration: 6S1P, front camera, single pusher and
  a removable rudder-capable directional module. Exact surface sizing remains M5 work.
- **SALAMANDRA-6S-CLEAN** — post-baseline experiment with the vertical module removed.
  It does not fly before 6S-R establishes a safe baseline.
- **SALAMANDRA-8S-STUDY** — separate voltage, mass, packaging and propulsion architecture
  study. It has no current first-flight or procurement authority.
- **CORE / PANEL** — historical v0.6 modular architecture. It remains a candidate method,
  not a binding interface for the redesign.
- **CLEAN / V1** — historical v0.6 finless and passive twin-fin comparison labels. Do not
  substitute them for the active 6S-R / 6S-CLEAN configuration contract.

## Coordinates, signs and units

| Quantity | Convention |
|---|---|
| Origin | Candidate-specific aircraft datum; the v0.6 reference uses the root quarter-chord point |
| `x` | Positive aft, toward the trailing edge |
| `y` | Positive starboard; v0.6 half-span is 0 to +650 mm |
| `z` | Positive up |
| Sweep | Negative is forward; v0.6 uses −15° at quarter chord, while redesign sweep is open |
| Twist | Positive is wash-in; v0.6 prints wash-in, while redesign twist is open |
| Dihedral | Positive puts the tips up |
| Calculation units | SI; presentation may use mm, g, km/h and g/dm² |

## Speeds and loads

- **E0–E3** — redesign efficiency states: candidate best range, 65 km/h report point,
  nominal 80 km/h FPV cruise and historical 95 km/h continuity comparison.
- **Cruise speed** — candidate-dependent in the redesign; 95 km/h is a historical v0.6
  comparator, not the sole objective.
- **`V_limit`** — current operational cap for the initial flight programme: 105 km/h.
  It is governed by unmeasured aeroelastic properties.
- **Article `V_NE`** — 160 km/h never-exceed value for Article #1. It is not authorized
  during initial testing merely because it appears in the design envelope.
- **Structural design speed** — 180 km/h sizing case. It is neither `V_limit` nor a
  flight target.
- **`VA`** — positive manoeuvring corner, calculated as `Vs sqrt(n_limit)`:
  approximately 109.0 km/h CLEAN and 110.4 km/h for the current V1 lower model.
- **Limit load** — maximum provisional manoeuvre load for operation: +6/−3 g.
- **Ultimate load** — structural proof/design case after the 1.5 safety factor:
  +9/−4.5 g. It is not an operational target.
- **Gust-reference screen** — legacy rigid-aircraft calculation retained as a warning.
  Its current result leaves the valid lift range, so it is not an adopted design load.

## Aerodynamics and stability

- **FSW** — forward-swept wing. It is redesign candidate A: visually preferred and
  technically interesting, but not selected before the equal-requirements trade.
- **MAC** — mean aerodynamic chord; 224.9 mm for the historical v0.6 candidate.
- **Neutral point (NP)** — longitudinal aerodynamic neutral point. The v0.6 panel-VLM
  result is −75.8 mm / 25.72 % MAC; the Weissinger-L check is −72.9 mm / 27.0 % MAC.
- **Center of gravity (CG)** — mass-balance location. The historical v0.6 target is −93.8 mm,
  ahead of the neutral point in the project's positive-aft coordinate system.
- **Static margin (SM)** — NP minus CG expressed as a fraction of MAC; the target is 8 %.
- **`cl` versus `CL`** — lowercase denotes a two-dimensional section coefficient;
  uppercase denotes the three-dimensional wing or aircraft quantity. The current local
  section `clmax` screen is 0.65; the released wing `CLmax` is 0.589.
- **`Cm0`** — pitching-moment coefficient at zero lift. The obsolete single-section
  `Cm0 ≥ +0.008` requirement was replaced by a coupled root/tip moment, twist and neutral
  elevon trim criterion in ADR-0041.
- **Reflex** — upward curvature near the airfoil trailing edge that contributes positive
  pitching moment for tailless trim.
- **Wash-in** — increasing incidence toward the tip. Article #1 prints +3.0° and retains
  the parameter for measured refinement.
- **Elevon** — surface combining pitch and roll control. Article #1 retains a two-servo
  working baseline; final geometry follows the selected wing and M5 evidence.
- **`Cnβ`** — directional static-stability derivative. Positive is stabilizing under the
  project's convention.

## Structures and propulsion

- **Divergence** — static aeroelastic instability in which load twists a forward-swept
  wing toward higher incidence, increasing load again.
- **`GXY`** — in-plane printed shear modulus. It remains a measured gate because filament
  orientation and process materially affect the value.
- **`GJ`** — torsional rigidity: shear modulus multiplied by the section torsion constant.
- **Elastic axis** — spanwise line through which aerodynamic loading produces no first-
  order twist. The current location is a bracket, not a measured shear center.
- **R-JOINT** — stiffness rule for the removable CORE↔PANEL joint; the connection must
  remain stiff enough that modularity does not consume the divergence margin.
- **O1 boundary** — historical 95 km/h APC E 8×8 comparison after avionics power is
  reserved: `J = 0.918`, 8,484 rpm and 2.12 N maximum allowable drag. It is not a
  predicted aircraft equilibrium until E2 supplies drag.
- **Wh/km** — battery-terminal energy per air distance, including propulsion, conversion,
  avionics and FPV. The former 1.15 Wh/km at 95 km/h is retained only as the E3 comparator.

## Tools

- **VLM** — vortex-lattice method used for the full planform neutral point, loads and
  control derivatives.
- **Weissinger-L** — independent swept lifting-line formulation used to cross-check the
  neutral point.
- **XFOIL 6.99** — external airfoil-analysis program used for section-polar generation;
  it is calibrated and screened, not treated as measured evidence.
- **System verifier** — `verify_calculations.py`, which checks cross-module contracts and
  can run all deterministic local analyses.
- **Pagefind** — static full-text search generated by the wiki build.
