---
title: How to read the engineering record
description: How authority, evidence, decisions, calculations, gaps and tests fit together without mixing releases or confidence classes.
editUrl: https://github.com/bultodepapas/salmandra/edit/main/wiki/content/guide/02-how-to-read.md
---

This is not a conventional product manual. It is a **controlled reasoning record**: the
repository preserves the design, the evidence behind it, the unknowns that remain and
the corrections that changed earlier conclusions.

## Ask the document the question it owns

| Question | Owning record | What it does not own |
|---|---|---|
| What must CAD implement now? | [Design guide](../salamandra/design-guide/) | Full derivations or historical alternatives |
| Why was this option selected? | [ADR](../decisions/) | New research or raw test data |
| What does the evidence show? | [Research thread](../research/) | The final project decision |
| Which value is still provisional? | [Open points](../salamandra/design-guide-open-points/) | The test procedure itself |
| What is unknown and why does it matter? | [Gap register](../gaps/) | A claim that the gap is closed |
| How will the gap be measured? | [Test programme](../tests/) | A result before the test is run |
| How is a derived value reproduced? | [Calculations](../calculations/) | Measured truth beyond the model's inputs |
| What changed between releases? | [Release notes]({{CURRENT_RELEASE_URL}}) and [changelog](../platform/changelog/) | Silent replacement of history |

Keeping these roles separate prevents a common failure: a calculated estimate being
repeated until it sounds measured, or a historical decision being mistaken for the
current baseline.

## Repository map

| Path | Role |
|---|---|
| `design/` | Controlling guide, justification and open-point companion |
| `docs/` | Objectives, conventions, plans, technical notes and release records |
| `decisions/` | One architecture/design decision record per adopted or rejected choice |
| `research/` | Investigation threads, source review, methods and limitations |
| `gaps/` | Unknowns, impact, owner and closure condition |
| `tests/` | Experimental procedures and configuration requirements |
| `calculations/` | Shared numerical contract, model scripts and verification harness |
| `geometry/`, `cad/`, `stl/` | Geometry inputs and community design outputs |
| `wiki/` | Generated publication layer; canonical engineering files remain elsewhere |

## Trace one claim end to end

For a current design value, follow this sequence:

```text
source or declared assumption
        ↓
calculation and validation case
        ↓
research finding and limitations
        ↓
ADR decision and reversal trigger
        ↓
Design Guide control value
        ↓
CAD / test article
        ↓
measured result → gap closure or correction
```

Example: the current neutral-point result comes from the −15° planform in
`design_config.py`, is calculated by the panel VLM, independently checked by
Weissinger-L, reviewed in I-21, adopted by ADR-0040 and published in the guide as
**−75.8 mm / 25.72 % MAC**, with a **2.9 mm** method-to-method difference. The
central-body effect and flight identification remain explicit limitations.

## Recognize the three kinds of “current”

- **Current release:** {{RELEASE_TAG}} defines the package that may be used together.
- **Current guide:** v{{GUIDE_VERSION}} is the controlling human-readable CAD and
  engineering specification.
- **Current numerical contract:** `calculations/design_config.py` owns shared constants.

If any of these disagree, stop. The release notes define migration; no document should
be “fixed” by averaging values.

## Interpret status language precisely

- **Released** means controlled and internally checked within stated assumptions.
- **Closed for CAD** means geometry may proceed; it does not imply measured acceptance.
- **Provisional** means a current working value with a named trigger.
- **Measured gate open** means the computational or documentary work is complete but
  physical evidence is still required.
- **Superseded** means preserved for audit only.
- **Cancelled or rejected** means considered and deliberately not adopted.

## Conventions that prevent expensive mistakes

- Coordinates use `x` positive aft, `y` starboard and `z` up; the origin is the root
  quarter-chord point.
- Negative sweep is forward sweep; positive twist is wash-in.
- Calculations use SI. Presentation tables may use millimetres, grams, km/h and g/dm².
- Lowercase `cl` is a two-dimensional section coefficient; uppercase `CL` is a
  three-dimensional wing or aircraft coefficient.
- `V_limit`, article `V_NE` and structural design speed are different quantities.
- Manoeuvre **limit** loads and structural **ultimate** loads differ by the released 1.5
  safety factor.

See [Conventions](../reference/04-conventions/) for the formal notation and
[Glossary](./04-glossary/) for operational definitions.
