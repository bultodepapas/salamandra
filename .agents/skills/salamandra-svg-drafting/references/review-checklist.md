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
- An OML encloses every controlling equipment envelope at the cited stations; required
  wall, clearance, or offset values remain traceable and are not aesthetic guesses.
- Bézier control points and fairing transitions are marked `[I]` unless a calculation or
  released surface controls them.

## Structural review

- XML parses; the root is SVG; physical size and viewBox match the sheet contract.
- IDs are unique; `aria-labelledby`, markers, patterns, and fragment links resolve.
- The file contains no scripts, event handlers, embedded active content, or external
  resources.
- Title, description, generator provenance, warning, and drawing number are present.
- `python calculations/generate_blueprints.py --check` leaves the working tree unchanged.
- Regeneration changes only the intended canonical sheets; sheet-specific styles do not
  leak into sibling drawings through the shared renderer.

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
- The OML reads as one closed silhouette without disconnected islands, self-intersections,
  accidental flat spots, or visible tangent kinks.
- Internal equipment and structural interfaces remain identifiable inside the OML instead
  of being hidden by the fairing fill.
