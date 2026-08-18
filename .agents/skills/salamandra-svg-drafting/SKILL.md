---
name: salamandra-svg-drafting
description: Create, revise, validate, or visually review Salamandra aircraft technical sketches in generated SVG. Use for drawing sheets, blueprint drafts, SVG geometry, drawing annotations, line hierarchy, and Codex or VS Code drawing workflows in this repository.
---

# Salamandra SVG drafting

Produce reviewable engineering communication without promoting a sketch to
manufacturing authority.

## Establish authority

1. Read `geometry/drawings/README.md` for the drawing contract.
2. Read only the calculation modules, ADRs, Design Guide sections, and research threads
   that control the requested geometry.
3. Mark every geometric statement as controlled/derived `[D]`, evidence-backed `[E]`,
   or provisional/inferred `[I]`. If its source is unclear, treat it as provisional.
4. Keep `DRAFT — NOT FOR MANUFACTURE` until native CAD, tolerances, print compensation,
   mass properties, and the relevant physical gates are closed.

## Author the drawing

- Edit `calculations/generate_blueprints.py` or its authoritative input, never a
  generated SVG directly.
- Keep the A3 metric mapping: `width="420mm"`, `height="297mm"`, and
  `viewBox="0 0 420 297"`.
- Derive coordinates from `design_config.py`, analysis results, or released coordinate
  files. Do not trace screenshots or conceptual illustrations.
- Make meaning survive monochrome printing: line type, weight, label, and status must
  remain sufficient without colour.
- Use real text, unique IDs, same-document references, `<title>`, `<desc>`, provenance
  metadata, drawing number, revision, scale, and an explicit authority warning.
- Keep provisional geometry amber, dashed, and text-labelled. Do not imply tolerance or
  precision that the evidence does not support.

## Verify and review

Run from the repository root:

```bash
python calculations/generate_blueprints.py
python calculations/generate_blueprints.py --check
```

The second command is read-only and must fail if a generated artifact is missing, stale,
unsafe, inaccessible, or inconsistent with the numerical contract.

Then open each standalone SVG in a browser and apply
[`references/review-checklist.md`](references/review-checklist.md). Inspect the full A3
sheet and dense regions at higher zoom. A successful XML check is not visual acceptance.

For changes to geometry or status, also run:

```bash
python calculations/verify_calculations.py --all-scripts
```

Report the input authority, files changed, validation results, visual findings, and every
remaining provisional item.

## Guardrails

- Do not use raster image generation as the geometric master.
- Do not run SVGO, an editor's optimiser, or path conversion on controlled masters
  without reviewing the exact transformation and re-running every check.
- Do not let Figma, Inkscape, or a VS Code extension become the authority for calculated
  coordinates. They may preview, inspect, annotate, or export review copies.
- Do not add a dependency unless it removes a demonstrated failure mode and works in the
  repository's Windows verification path.
