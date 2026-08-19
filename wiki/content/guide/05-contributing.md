---
title: Contributing to Salamandra
description: Contribution paths for measurements, corrections, analyses, CAD parts and documentation, with the evidence and verification each path requires.
editUrl: https://github.com/bultodepapas/salamandra/edit/main/wiki/content/guide/05-contributing.md
---

Salamandra welcomes measurements, corrections, analyses, CAD, printed parts, adapters,
new configurations and documentation. Start from the contribution's effect on the
engineering record, not from its file type.

## Highest-value work now

| Priority | Contribution | Current example |
|---:|---|---|
| 1 | Measurement that replaces an estimate or inference | Printed-wing `GXY`/`GJ`, elastic axis, lift/drag/moment or complete-aircraft mass |
| 2 | Correction with stronger evidence | A source or calculation that overturns a controlling value |
| 3 | Independent replication | Second implementation, build or flight log with complete configuration |
| 4 | CAD and integration | CORE, PANEL, mounts, cradles or tooling that obey current interfaces |
| 5 | New variant or creative part | Alternative panel, body, equipment adapter or visual modification |

All five are welcome. The ordering reflects how directly the contribution raises the
confidence of the platform.

## Pick a contribution path

### Measurement or test data

1. Link the gap or open point the test addresses.
2. Use the published procedure where one exists; declare deviations before interpreting
   the result.
3. Record the full configuration: airframe variant, material, slicer settings, mass,
   battery, motor, propeller, electronics, firmware and environmental conditions.
4. Preserve raw data and units. Put analysis in a rerunnable script when practical.
5. State what changed: a confidence tag, a gap state, an ADR trigger or none.

Data without configuration metadata cannot be compared across builders.

### Calculation or research

1. Open or update an `I-XX` thread with the question, search method and primary sources.
2. Separate measured inputs, derived outputs, estimates and inference.
3. Add a validation case independent of the project result.
4. If the value is shared by more than one model, update `design_config.py` and the
   cross-module verifier instead of copying a new constant.
5. Run:

```bash
python calculations/verify_calculations.py
python calculations/verify_calculations.py --all-scripts
python -m ruff check calculations
python -m compileall -q calculations
```

XFOIL and network-dependent work must remain explicit; do not silently substitute a
cached or skipped result.

### CAD, printed part or configuration

1. Identify the target configuration and Design Guide version.
2. Reference every controlling interface and any affected ADR or open point.
3. Include native CAD when possible, plus exchange and printable outputs.
4. Report mass properties, material, slicer assumptions, tolerances and assembly method.
5. Do not present a part as a released replacement until its fit, mass and relevant
   structural or flight gates pass.

A creative or decorative part may be submitted “as is”; label it clearly when no
engineering claim is intended.

### Documentation or correction

Canonical engineering content lives outside `wiki/src/content/docs/`, which is generated.
Edit the owning Markdown file or a committed onboarding page under `wiki/content/`.

If new evidence invalidates an existing conclusion:

1. correct the current authority;
2. add a numbered entry to the [changelog](../platform/changelog/);
3. update affected ADR, research, gap and guide references;
4. preserve the historical release note;
5. run the wiki verification pipeline.

The correction record currently runs through **C{{LATEST_CORRECTION}}**. Corrections are
evidence of review, not defects to hide.

## Writing a decision or research record

Use the [ADR template](../decisions/template/) for a design decision. A strong ADR answers:

- What forced the decision?
- Which alternatives were evaluated and why were they rejected?
- What downstream work or constraint follows?
- What evidence would reverse the decision?

A research thread answers a different set of questions: what was asked, how sources were
searched, what was found, what remains uncertain and which decisions consume the result.

## Source and language standard

- Prefer primary measurements, peer-reviewed work, experimental databases, official
  manufacturer data and controlled project tests.
- Cite the source next to the claim it supports; do not use a bibliography as a substitute
  for claim-level traceability.
- Use precise technical English, SI in calculations and defined project units in tables.
- Distinguish section (`cl`) from wing/aircraft (`CL`) quantities, limit from ultimate
  loads, and current from historical values.
- State uncertainty or sensitivity when the available evidence supports it.

## Before opening a pull request

```bash
cd wiki
npm run check:refs
node scripts/gen-site.mjs --strict
npm run check
npm run lint
npm run build
```

Then complete the full checklist in [CONTRIBUTING](../platform/contributing/), including
the affected decision, gap and provenance tag for every new quantitative claim.
