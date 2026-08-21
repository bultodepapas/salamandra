---
title: How to read the engineering record
description: How authority, evidence, decisions, calculations, gaps and tests fit together without mixing releases or confidence classes.
editUrl: https://github.com/bultodepapas/salamandra/edit/main/wiki/content/guide/02-how-to-read.md
---

This is not a conventional product manual. It is a **controlled reasoning record**: the
repository preserves the design, the evidence behind it, the unknowns that remain and
the corrections that changed earlier conclusions.

## Ask the document the question it owns

| Question | Owning record | What it does not own |
|---|---|---|
| What may the programme do next? | [Master Plan](../reference/05-master-plan/) | A claim that an open gate is already closed |
| What aircraft are we trying to build? | [Article #1 requirements](../reference/00-objectives-and-requirements/) | Final geometry or an unmeasured component release |
| What hardware is currently bounded? | [Hardware manifest](../reference/17-article-1-hardware-manifest/) | Physical acceptance or final placement |
| How is MP-04 executed? | [I-33](../research/i-33-mp04-propulsion-procurement-and-hardware-characterisation/) and [H01–H22](../tests/mp04-hardware-characterisation/) | Measurements before specimens and raw evidence exist |
| What must CAD implement now? | Nothing for production; the [historical Design Guide](../salamandra/design-guide/) is review authority only | Permission to bypass M1–M7 |
| Why was this option selected? | [ADR](../decisions/) | New research or raw test data |
| What does the evidence show? | [Research thread](../research/) | The final project decision |
| Which active value is still provisional? | Owning contract plus Master Plan exit evidence | Permission to treat catalog or estimated input as measured |
| Which v0.6 value was provisional? | [Historical Open Points](../salamandra/design-guide-open-points/) | Active redesign authority |
| What is unknown and why does it matter? | [Gap register](../gaps/) | A claim that the gap is closed |
| How will the gap be measured? | [Test programme](../tests/) | A result before the test is run |
| How is a derived value reproduced? | [Calculations](../calculations/) | Measured truth beyond the model's inputs |
| What changed between releases? | [Release notes]({{CURRENT_RELEASE_URL}}) and [changelog](../platform/changelog/) | Silent replacement of history |

Keeping these roles separate prevents a common failure: a calculated estimate being
repeated until it sounds measured, or a historical decision being mistaken for the
active redesign authority.

## Repository map

| Path | Role |
|---|---|
| `design/` | Historical v0.6 guides, method audits and future CAD-handoff evidence |
| `docs/` | Active requirements and Master Plan plus conventions, technical notes and release records |
| `decisions/` | One architecture/design decision record per adopted or rejected choice |
| `research/` | Investigation threads, source review, methods and limitations |
| `gaps/` | Unknowns, impact, owner and closure condition |
| `tests/` | Experimental procedures and configuration requirements |
| `calculations/` | Shared numerical contract, model scripts and verification harness |
| `geometry/`, `cad/`, `stl/` | Geometry inputs and community design outputs |
| `wiki/` | Generated publication layer; canonical engineering files remain elsewhere |

## Trace one claim end to end

For an active redesign value, follow this sequence:

```text
source or declared assumption
        ↓
calculation and validation case
        ↓
research finding and limitations
        ↓
programme gate and, when selected, ADR decision
        ↓
measured mass skeleton and released CAD brief
        ↓
CAD / test article
        ↓
measured result → gap closure or correction
```

Example: the P42A source establishes 3.6 V nominal and 4.2 V full charge per cell. The
battery contract derives 21.6/25.2 V for 6S; I-33 uses that bus to screen motor Kv,
full-charge RPM and ESC voltage headroom. The manifest then bounds procurement mass and
envelopes, while H04/H06 require the actual specimens, wiring, efficiency and thermal map.
Only accepted measurements may enter the MP-06 mass skeleton. The chain names products
without pretending they are selected flight hardware.

## Recognize the four kinds of “current”

- **Current programme authority:** Master Plan v2.4 owns sequence, gate status and what
  work is authorized.
- **Current product contract:** requirements v2.0 and `mission_contract.py` own Article #1
  intent, configurations and scoring.
- **Current M1 interface:** the hardware manifest, I-33 and H01–H22 own candidate systems
  and their physical closure method.
- **Current tagged release:** {{RELEASE_TAG}} / Design Guide v{{GUIDE_VERSION}} is the
  internally reproducible **historical v0.6 comparison baseline**.

If these appear to disagree, the first three govern the redesign. Preserve the tagged
release as history; never repair a conflict by averaging values.

## Interpret status language precisely

- **Released** means controlled and internally checked within stated assumptions.
- **Authorized** means the Master Plan permits that scope of work at the current gate.
- **Closed for CAD** means geometry may proceed; it does not imply measured acceptance.
- **Provisional** means a current working value with a named trigger.
- **Measured gate open** means the computational or documentary work is complete but
  physical evidence is still required.
- **Superseded** means preserved for audit only.
- **Historical comparison** means reproducible prior work with no automatic redesign
  authority.
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
