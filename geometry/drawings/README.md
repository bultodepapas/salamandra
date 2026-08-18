# Salamandra drawing set

This directory contains **generated technical sketches**, not released manufacturing
drawings. They translate the current numerical and Design Guide contracts into reviewable
metric SVG sheets while the native parametric CAD and F2 physical verification remain
open.

## Current sheets

<!-- BEGIN GENERATED: drawing-index · calculations/drawing_index.py · do not edit by hand -->

| Drawing | Purpose | Sheet | Authority |
|---|---|---:|---|
| [`SLM-GA-001`](SLM-GA-001-general-arrangement.svg) | Article #1 top-view arrangement: controlled planform, modular stations, CG/NP and continuous provisional fuselage/equipment envelopes | A3 · 1:4 | Planform `[D]`; equipment `[D]`/`[E]`; OML `[I]` |
| [`SLM-GA-002`](SLM-GA-002-side-elevations.svg) | Comparative side elevations: CLEAN finless baseline and V1a fixed-fin test variant, with common root section, packaging, motor/propeller and keel clearance | A3 · 1:4 | Root/fin `[D]`/`[E]`; side OML/install `[I]` |
| [`SLM-EQP-001`](SLM-EQP-001-equipment-mass-skeleton.svg) | Top and side mass skeleton: component envelopes, true mass centres, x/y/z schedule, CLEAN CG and V1 battery-stop overlay. The top view includes the controlled exterior wing planform as spatial context but no wing construction, fuselage or OML. | A3 · top 1:6.5 / side 1:4 | Planform `[D]`; mass/position ledger `[D]`/`[E]`; open installations `[M]`; no OML authority |
| [`SLM-WNG-001`](SLM-WNG-001-half-wing-layout.svg) | Right half-wing: printed segments, cells, spar/pin, ADR-0045 elevon/fixed-root bridge, exact y195 profile and polyhedral inset | A3 · plan 1:2 | Planform/profile/elevon bounds `[D]`; structure/polyhedral `[E]`/`[I]` |

<!-- END GENERATED: drawing-index -->

The table, the repository README gallery, the wiki drawing page and
[`manifest.json`](manifest.json) are all published by
[`calculations/drawing_index.py`](../../calculations/drawing_index.py) from one sheet
registry. Do not hand-edit anything between the generated markers: it is overwritten on the
next run and `--check` fails while it disagrees.

All sheets state **DRAFT — NOT FOR MANUFACTURE**. Amber dashed geometry is provisional
and must not be reverse-engineered into a released part. The black/blue planform is
traceable, but a printed part still requires native CAD, tolerances, mass properties and
the applicable fit/structural test.

The general-arrangement fuselage is a smooth **top-view OML concept `[I]`**. Its battery,
support and propulsion stations are sourced, but the Bézier transitions are packaging
geometry only. OP-21 and F2 must freeze the native CAD surface before it can become an
interface or manufacturing reference.

The side-elevation sheet repeats the same authority boundary in the vertical plane. It
compares **SALAMANDRA-CLEAN** with **SALAMANDRA-V1a**; V1a has a passive fixed fin and
explicitly **no movable rudder**. The root airfoil and calculated fin size are traceable,
while equipment height placement, keel transitions and the fin-to-pod interface remain
`[I]`. The sheet exposes a CAD item that must be reconciled: the 105 mm fin root footprint
versus the rear-pod extension ending near x = +295 mm.

## Reproduce

From the repository root:

```bash
python calculations/generate_blueprints.py
python calculations/generate_blueprints.py --check
```

The first command deliberately writes the deterministic artifacts. The second command is
read-only: it fails if any artifact is missing, stale, structurally unsafe or
inconsistent with the numerical contract. In VS Code, run **Tasks: Run Task** and choose
`Drawings: regenerate`, `Drawings: verify`, or `Drawings: verify all calculations`.

The generator imports:

- planform, chord and sweep from `calculations/design_config.py`;
- Article #1 elevon bounds, hinge fraction and servo midspan from
  `calculations/design_config.py` (ADR-0045/I-27);
- CG, VLM NP, independent Weissinger NP and solved pack station from
  `calculations/balance_cg.py`;
- component masses, oriented envelopes, x/y/z stations, installation status and
  battery-only CG trim from `calculations/equipment_layout.py`;
- the released local section from
  `geometry/airfoils/salamandra-r1-y195.dat`;
- the released root section from `geometry/airfoils/salamandra-root-r1.dat` and the
  V1a fin solution from `calculations/yaw_stability.py`;
- explicitly named provisional dimensions from the Design Guide §§3–6.

No geometry is traced from an illustration. Changing a shared planform or balance input
changes the SVG on regeneration. The script validates the numerical contract, XML,
physical page size, unique and resolved identifiers, same-document references,
accessibility metadata, generator provenance, absence of active/embedded content, warning
text and drawing identifiers.

Use the installed SVG extension only for live preview and symbol navigation. Do not run
its minimiser or any automatic SVG optimiser on the controlled masters. Browser rendering
is a visual review gate, not a source of geometry.

## Graphic contract

| Appearance | Meaning |
|---|---|
| Heavy dark continuous line | Visible controlled outline |
| Thin dark/blue line | Derived feature, datum or dimension |
| Long-short line | Centreline |
| Short dashed grey line | hidden feature or station/cut boundary |
| Amber dashed line/fill | provisional geometry awaiting CAD or physical closure |
| Quartered black/white circle | Calculated centre of gravity (conventional CG symbol) |

On `SLM-EQP-001`, envelope **fill colour identifies system function** while outline
style continues to identify maturity. A solid system-colour outline is measured or
controlled; an amber dashed outline remains estimated, reserved or otherwise open.
Labels and line styles preserve the meaning in monochrome.

| Equipment fill | System |
|---|---|
| Violet | Stored energy / battery |
| Red | Propulsion train |
| Amber | Electrical power conversion/distribution |
| Blue | Flight control and avionics |
| Teal | Navigation and air-data sensors |
| Green | Control actuators |
| Magenta | FPV and RF equipment |
| Grey | Unresolved installation reserve |

The files use `width="420mm"`, `height="297mm"` and `viewBox="0 0 420 297"`.
Consequently one SVG user unit maps to one millimetre on an A3 sheet when printed at
**100 % / actual size**. Browser “fit to page” scaling invalidates the stated scale.

## Method basis

The workflow is documented in
[`research/I-25-svg-technical-drawing-workflow.md`](../../research/I-25-svg-technical-drawing-workflow.md).
It follows the representation/dimensioning scope of ISO 128/129, the FAA aircraft-drawing
line hierarchy and orthographic conventions, NASA's three-view geometry practice, and
W3C SVG viewport/accessibility requirements. The repository does not reproduce
copyrighted standard text; it records only the project rules derived from public primary
sources.

Codex, VS Code, MCP, renderer, validator, library and skill choices are evaluated in
[`research/I-26-codex-svg-agent-toolchain.md`](../../research/I-26-codex-svg-agent-toolchain.md).
The executable agent procedure is
[`salmandra-svg-drafting`](../../.agents/skills/salamandra-svg-drafting/SKILL.md).

## Next useful sheets

1. `SLM-CORE-001`: CORE interface-control envelope after its outer mould is frozen.
2. `SLM-ASM-001`: exploded assembly and fastener/joiner schedule.
3. `SLM-WNG-002`: station/profile schedule with twist and local reference frames.
4. `SLM-FIN-001`: optional V1 fin, after F2 closes root, spar and mass geometry.
5. 1:1 tiled templates only after tolerances and print compensation are measured.
