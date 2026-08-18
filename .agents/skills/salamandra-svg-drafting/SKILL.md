---
name: salamandra-svg-drafting
description: Create, revise, validate, or visually review Salamandra aircraft technical sketches in generated SVG. Use for drawing sheets, blueprint drafts, fuselage or OML silhouettes, packaging envelopes, SVG geometry, drawing annotations, line hierarchy, and Codex or VS Code drawing workflows in this repository.
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
- Prefer established aerospace/drafting symbols over invented icons. Use the conventional
  alternating black/white quartered circle for CG; keep component mass-centre dots and
  neutral-point targets visually distinct from it.
- Make meaning survive monochrome printing: line type, weight, label, and status must
  remain sufficient without colour.
- Keep visual encodings orthogonal. Colour may identify system function, but line type and
  explicit status must identify authority/maturity. Define any project palette in the
  sheet legend and `geometry/drawings/README.md`; never imply that it is an external
  standard unless a cited standard actually defines it.
- Use real text, unique IDs, same-document references, `<title>`, `<desc>`, provenance
  metadata, drawing number, revision, scale, and an explicit authority warning.
- Keep provisional geometry amber, dashed, and text-labelled. Do not imply tolerance or
  precision that the evidence does not support.
- Separate the outer mould line (OML), internal equipment envelopes, and structural
  interfaces into distinct visual layers; do not substitute one for another.
- Give every physical component its own reference and schedule row. When repeated items
  encode a design decision—dual actuation, redundancy, symmetry—state the count, location,
  and rationale on the sheet or in its controlling document instead of leaving the reader
  to infer that the duplication is accidental.
- For fuselage, pod, or fairing silhouette work, read
  [`references/oml-continuity.md`](references/oml-continuity.md) before editing.
- Scope drawing-specific styles to the affected sheet or element. After regeneration,
  confirm that unrelated canonical drawings remain unchanged.
- A new sheet is not finished until it is published: add its `SheetSpec` (number, file,
  heading, purpose, sheet scale, authority, reviewer note) to `calculations/drawing_index.py`.
  The generator refuses to pass while a rendered sheet has no entry, and the manifest it
  writes is what the README gallery, the drawing index table and the wiki page render.
  Never hand-edit inside a `BEGIN GENERATED: drawing-index` block.

## Verify and review

Run from the repository root:

```bash
python calculations/generate_blueprints.py
python calculations/generate_blueprints.py --check
```

The second command is read-only and must fail if a generated artifact is missing, stale,
unsafe, inaccessible, or inconsistent with the numerical contract.

Inspect `git diff --check` and the generated-file diff after regeneration. Treat an
unexpected change to a sibling drawing as a generator fan-out defect, even when both SVGs
remain valid.

Then open each standalone SVG in a browser and apply
[`references/review-checklist.md`](references/review-checklist.md). Inspect the full A3
sheet and dense regions at higher zoom. Where labels have stable IDs, use DOM bounding
boxes to check label-to-label and label-to-text collisions, then inspect leader crossings
visually. Review colour and grayscale. Perform this review after the final regeneration;
a successful XML check or an earlier screenshot is not visual acceptance.

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
