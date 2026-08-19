# Completion checklist

For calculation or geometry changes:
1. Run the directly affected module and its validation case.
2. Run python calculations/verify_calculations.py --all-scripts.
3. Run python calculations/contract_lint.py and python calculations/mutation_test.py when shared quantities/contracts change.
4. If drawings can change, regenerate with python calculations/generate_blueprints.py, then run --check and python calculations/drawing_index.py --check.
5. Run git diff --check and inspect the exact generated-file diff; unexpected sibling drawing changes are defects.
6. Visually review final SVGs at full A3 and dense zoom, including grayscale, labels, leaders, intersections, and provisional styling.
7. Report input authority, files changed, validation results, visual findings, and all unresolved/provisional items.
8. Do not claim manufacturing authority until native CAD, tolerances, print compensation, mass properties, fit/structural tests, and relevant physical gates close.
