# Salamandra project overview

- Open, modular, AI-assisted platform for a 3D-printed fixed-wing FPV aircraft family. Article #1 is a PETG 1,300 mm forward-swept flying wing.
- The reasoning is a primary deliverable: every quantitative claim is tagged [M] measured, [D] derived, [E] estimated, or [I] inferred. No unsourced number is accepted; [E]/[I] cannot support irreversible decisions without verification.
- Current phase: Phase 1 geometry and stability. Generated A3 SVGs are design-review sketches and remain DRAFT — NOT FOR MANUFACTURE until native CAD, tolerances, mass properties, print compensation, and physical gates close.
- Main structure: design/ controlling Design Guide; decisions/ ADRs; research/ evidence threads; gaps/ open questions; calculations/ Python numerical contract and SVG generator; geometry/ controlled airfoils and drawings; tests/ experimental program; docs/ specification/status; cad/ and stl/ community artifacts; wiki/ Astro Starlight docs.
- Canonical geometry and shared physical quantities live in calculations/design_config.py. Balance/CG, equipment layout, aero, structure, propulsion, and drawings are deterministic Python modules.
- Project runs on Windows locally and Linux in CI. Python 3.10–3.12 is the evident support range. Numeric dependency is NumPy, with the repository requirements currently declaring numpy>=2.0,<3.0.
- Coordinate convention: x positive aft from root quarter-chord; negative quarter-chord sweep is forward sweep; positive epsilon is wash-in.
