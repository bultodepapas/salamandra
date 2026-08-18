# Salamandra drawing set

This directory contains **generated technical sketches**, not released manufacturing
drawings. They translate the current numerical and Design Guide contracts into reviewable
metric SVG sheets while the native parametric CAD and F2 physical verification remain
open.

## Current sheets

| Drawing | Purpose | Scale | Authority |
|---|---|---:|---|
| [`SLM-GA-001-general-arrangement.svg`](SLM-GA-001-general-arrangement.svg) | Article #1 top-view arrangement: controlled planform, modular stations, CG/NP and provisional equipment envelopes | A3 · 1:4 | Planform `[D]`; equipment `[D]`/`[E]` |
| [`SLM-WNG-001-half-wing-layout.svg`](SLM-WNG-001-half-wing-layout.svg) | Right half-wing: printed segments, cells, spar/pin, elevon, exact y195 profile and polyhedral inset | A3 · plan 1:2 | Planform/profile `[D]`; structure/polyhedral `[E]`/`[I]` |

Both sheets state **DRAFT — NOT FOR MANUFACTURE**. Amber dashed geometry is provisional
and must not be reverse-engineered into a released part. The black/blue planform is
traceable, but a printed part still requires native CAD, tolerances, mass properties and
the applicable fit/structural test.

## Reproduce

From the repository root:

```bash
python calculations/generate_blueprints.py
python calculations/generate_blueprints.py --check
```

The first command deliberately writes the deterministic artifacts. The second command is
read-only: it fails if either artifact is missing, stale, structurally unsafe or
inconsistent with the numerical contract. In VS Code, run **Tasks: Run Task** and choose
`Drawings: regenerate`, `Drawings: verify`, or `Drawings: verify all calculations`.

The generator imports:

- planform, chord and sweep from `calculations/design_config.py`;
- CG, VLM NP, independent Weissinger NP and solved pack station from
  `calculations/balance_cg.py`;
- the released local section from
  `geometry/airfoils/salamandra-r1-y195.dat`;
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
