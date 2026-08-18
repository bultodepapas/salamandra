# I-25 — Reproducible SVG technical-drawing workflow

**Status:** Executed — two-sheet proof of concept generated and visually reviewed;
manufacturing release remains blocked by native CAD and F2/S3 evidence  
**Date:** 2026-08-18  
**Feeds:** `calculations/generate_blueprints.py`, `geometry/drawings/`, wiki drawing guide,
future CAD interface-control documents

## 1. Question

How can the project publish useful plan sketches before native parametric CAD exists,
without allowing an attractive illustration to masquerade as manufacturing authority or
drift away from the calculations?

The required output must be human-readable, printable, diffable, accessible and
regenerated from the same numerical contract as the analyses.

## 2. Search method and source basis

Firecrawl MCP was requested by the repository instructions but was not available in this
session. The investigation therefore searched and checked only primary, official
documentation:

- [ISO 128-1:2020](https://www.iso.org/standard/65296.html) defines the general scope and
  requirements for computer- or manually executed 2D/3D technical drawings. ISO confirms
  this edition as current in 2026.
- [ISO 129-1:2018](https://www.iso.org/standard/64007.html) defines general presentation
  principles for dimensions and associated tolerances. ISO marked it “to be revised” in
  June 2026, so this project uses only its stable high-level dimension-presentation scope;
  it does not claim a complete ISO-conforming tolerance system.
- The FAA's 2023
  [*Aviation Maintenance Technician Handbook — General*, Chapter 4](https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/amtg_handbook.pdf)
  explains aircraft drawings, orthographic projections, dimension/centre/hidden lines and
  the need for distinguishable thin, medium and thick line intensities.
- NASA Glenn's [wing-geometry reference](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/wing-geometry/)
  presents wing geometry in top, front and side views; NASA's
  [OpenVSP modelling introduction](https://www.nasa.gov/reference/openvsp-modeling-introduction/)
  uses three-view drawings and dimensions as modelling references.
- W3C SVG 2 defines the
  [`viewBox`, viewport and units mapping](https://www.w3.org/TR/SVG/coords.html), while
  W3C's [SVG accessibility note](https://www.w3.org/TR/SVG-access/) documents structured
  `title` and `desc` alternatives for meaningful graphics.

No secondary drafting blog, AI-generated example or aesthetic “blueprint” image is used
as geometric evidence.

## 3. Requirements derived for Salamandra

1. **Source geometry, do not redraw it.** Planform coordinates come from
   `design_config.py`; calculated balance points come from `balance_cg.py`; the section
   inset comes from the released coordinate file.
2. **Use a physical sheet.** A3 landscape uses a 420 × 297 SVG viewBox and matching
   millimetre width/height, so the page coordinate system is metric at 100 % print scale.
3. **Use line semantics before colour.** Visible outlines, dimensions, centrelines,
   station cuts and provisional items remain distinguishable in monochrome. Amber adds a
   redundant warning for assumptions.
4. **Separate authority.** Every sheet carries a drawing number, revision, source,
   scale and “DRAFT — NOT FOR MANUFACTURE”. Provisional equipment/structure is dashed and
   labelled rather than implied by a polished outline.
5. **Make accessibility intrinsic.** Each standalone SVG is an image with an accessible
   title and long description; labels are real text, not paths.
6. **Validate and inspect.** XML and numerical checks are necessary but insufficient.
   Every generated sheet must also be rendered at A3 aspect ratio and visually checked
   for overlap, sweep direction, hierarchy and legibility.

## 4. Implemented system

`calculations/generate_blueprints.py` is a standard-library SVG writer around the current
calculation modules. It emits:

- `SLM-GA-001`, a full top-view arrangement at 1:4; and
- `SLM-WNG-001`, a right half-wing structural layout at 1:2, including the exact y195
  Salamandra r1 section and a clearly exaggerated polyhedral front inset.

The first visual render exposed issues that XML checks did not: arrowheads were too
large, title text crossed its title-block cell and the span-chain caption competed with
dimension text. Revision P0 corrects those layout failures. The planform direction,
stations, CG/NP separation and provisional/controlled distinction were visually correct.

## 5. What these sheets do not close

- The CORE outer mould, rear pod, motor envelope, cradle, servo pockets, spar/channel and
  polyhedral construction remain provisional where the Design Guide says so.
- An SVG drawing has no parametric feature history, assembly constraints, tolerance stack
  or mass properties. Native CAD remains the design implementation authority.
- The 1:2/1:4 scale is valid only on an A3 print at actual size. Web display is explicitly
  not to scale.
- No 1:1 cutting or drilling template will be published until print shrinkage, fit and
  hole compensation are measured.

## 6. Acceptance and next step

The proof of concept is accepted as a **communication and design-review layer**. It is not
accepted as manufacturing data. The next drawing should be the CORE interface-control
sheet only after F2 freezes the outer mould and mass properties; otherwise a new sheet
would add false precision rather than useful information.

