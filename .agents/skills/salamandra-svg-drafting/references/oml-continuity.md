# OML continuity workflow

Use this workflow when a fuselage, pod, nacelle, or fairing looks absent, fragmented, or
mechanically boxy in a technical sketch.

## Diagnose before styling

1. Identify whether the drawing shows only equipment boxes, structural members, or several
   disconnected provisional primitives. Do not call those objects a fuselage OML.
2. Collect the controlled longitudinal stations, minimum equipment widths, wall thicknesses,
   clearances, support interfaces, and propulsion limits.
3. Assign `[D]`, `[E]`, or `[I]` independently to stations, widths, and curve transitions.
   A sourced station does not make an unsourced curve controlled.

## Construct the silhouette

1. Compute packaging minima before shaping. For a symmetric enclosure, use relationships
   such as `outer_width = inner_width + 2 × wall + 2 × clearance`.
2. Build one closed, symmetric planform path around the centreline when the configuration is
   symmetric. Join the nose, equipment bay, structural neck, core, and aft pod continuously.
3. Use cubic Bézier segments for smooth transitions, but keep their control points `[I]`
   until released CAD or analysis defines the surface. Preserve at least positional
   continuity and visually inspect tangent continuity at every join.
4. Keep equipment envelopes, boom or spar geometry, and hard-interface stations visible as
   separate internal layers. Do not distort them to improve the silhouette.
5. Do not infer vertical sections, wetted area, cooling flow, drag, or printability from a
   top-view OML alone.

## Validate the result

- Check the OML half-width against the required envelope at each controlling station.
- Inspect the complete sheet, a tight OML detail, and grayscale output. A shape can look
  continuous in detail yet disappear at plotted scale.
- Reject self-intersections, pinched necks without structural justification, abrupt slope
  reversals, and curves that cross the propeller or other exclusion envelopes.
- Inspect computed SVG style and bounding box when browser tools are available; confirm the
  provisional dash pattern and fill survive rendering.
- Regenerate all sheets and compare their diffs. If a new style belongs to one drawing,
  keep it element-local or sheet-local so shared CSS does not modify unrelated artifacts.

Report the result as a **plan-view OML concept**, not as a complete fuselage or manufacturing
surface, until the required CAD and physical gates are closed.
