# Style and conventions

- All technical documentation uses precise professional English.
- Every quantitative technical claim must identify its source/confidence: [M], [D], [E], or [I]. Record corrections in CHANGELOG instead of silently rewriting history.
- Prefer a single owner for every physical quantity (ADR-0046). Import shared quantities from calculations/design_config.py rather than redeclaring them.
- Python modules are deterministic calculation scripts with validation cases; functions and constants use conventional snake_case and UPPER_CASE. Keep calculations reproducible and state assumptions/units.
- Use symbol-aware code inspection/editing when practical. Generated SVG files are never hand-edited; edit calculations/generate_blueprints.py or its authoritative inputs.
- Drawings are A3 metric (420 x 297 mm, matching viewBox), with controlled/derived, evidence-backed, and provisional geometry visually and textually distinct. Preserve DRAFT — NOT FOR MANUFACTURE while physical/CAD gates remain open.
- Separate OML, equipment envelopes, and structural interfaces. Do not promote a view-specific silhouette into complete 3D authority.
- Source preference: peer-reviewed research, experimental databases, controlled tests, manufacturer data, patents, then own measurements.
