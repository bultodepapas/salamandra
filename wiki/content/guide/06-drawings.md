---
title: Drawings and SVG workflow
description: How Salamandra turns the numerical design contract into printable, reviewable SVG sketches without confusing provisional geometry with manufacturing authority.
editUrl: https://github.com/bultodepapas/salmandra/edit/main/wiki/content/guide/06-drawings.md
---

The drawing set is a bridge between analysis and native CAD. It gives designers a
dimensioned, reviewable starting point while keeping every unresolved shape visibly
provisional. These are **technical sketches, not manufacturing drawings**.

## Current drawing set

### General arrangement · SLM-GA-001

[![A3 general-arrangement drawing of the Salamandra Article #1 planform, balance datums and provisional equipment.]({{BASE}}drawings/SLM-GA-001-general-arrangement.svg)]({{BASE}}drawings/SLM-GA-001-general-arrangement.svg)

Use this sheet to review the whole-aircraft relationship: 1,300 mm controlled planform,
modular stations, quarter-chord sweep, CG/NP, nose-boom battery station and rear-pusher
envelope. The equipment outlines are amber and provisional.

### Right half-wing · SLM-WNG-001

[![A3 right-half-wing drawing showing printed segments, cells, spar, pin, elevon, airfoil section and polyhedral inset.]({{BASE}}drawings/SLM-WNG-001-half-wing-layout.svg)]({{BASE}}drawings/SLM-WNG-001-half-wing-layout.svg)

Use this sheet to review PANEL segmentation and interfaces. It shows the exact y195
Salamandra r1 coordinate section, but the spar/channel, servo zones, D-box web and
polyhedral construction retain their provisional status.

## Read the linework before the colour

| Graphic treatment | Engineering meaning |
|---|---|
| Heavy dark continuous line | Visible controlled outline |
| Thin dark or blue line | Derived feature, datum or dimension |
| Long-short line | Centreline |
| Short dashed grey line | Hidden feature or station/cut boundary |
| Amber dashed line or fill | Provisional item awaiting CAD or physical closure |

Colour is redundant: line type and labels preserve the distinction on a monochrome
print. An attractive amber envelope is still an estimate, not authority.

## Reproduce and verify

From the repository root:

```bash
python calculations/generate_blueprints.py --check
```

The script imports the canonical planform, calculated balance solution and released y195
airfoil coordinates. It then checks the shared geometry, segment lengths, elevon span,
NP agreement, static margin, A3 metric viewport, XML structure, accessible description,
drawing identifiers and manufacturing warning.

For a scale check, print the standalone SVG on A3 at **100 % / actual size**. Do not use
“fit to page”. Browser and wiki display sizes are responsive and therefore not physical
scale references.

## Authority boundary

The SVGs are suitable for design review, discussion and tracing CAD inputs. They do not
contain tolerances, print compensation, feature history, mass properties or assembly
constraints. Do not derive a cutting, drilling or printable part directly from them.

The research and rationale are in [I-25](../research/i-25-svg-technical-drawing-workflow/);
the complete source/print contract is in the
[drawing-set README](https://github.com/bultodepapas/salmandra/blob/main/geometry/drawings/README.md).
Native CAD plus F2/S3 evidence remains the release path.
