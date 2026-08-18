# SVG drawing review checklist

## Numerical and semantic review

- The generator imports the authoritative geometry instead of repeating constants.
- Dimensions, labels, datum direction, scale, drawing number, revision, and source line
  agree with the current design contract.
- Controlled, evidence-backed, and provisional geometry are distinguishable without
  colour.
- Every provisional feature is dashed and explicitly labelled.
- No feature can reasonably be mistaken for a manufacturing tolerance, cutting path, or
  released interface.

## Structural review

- XML parses; the root is SVG; physical size and viewBox match the sheet contract.
- IDs are unique; `aria-labelledby`, markers, patterns, and fragment links resolve.
- The file contains no scripts, event handlers, embedded active content, or external
  resources.
- Title, description, generator provenance, warning, and drawing number are present.
- `python calculations/generate_blueprints.py --check` leaves the working tree unchanged.

## Visual review

- The entire sheet fits the A3 frame and title block.
- No text, dimension, leader, arrowhead, or callout is clipped or unintentionally
  overlapped.
- Text remains readable at whole-sheet view and at the stated print scale.
- Line-weight hierarchy is evident; dashed patterns survive normal zoom and printing.
- Forward direction, handedness, sweep, station order, CG/NP relationship, and local
  coordinate conventions are visually plausible.
- Dense regions are inspected separately at higher zoom.
- The sheet is checked in monochrome or grayscale as well as colour.
