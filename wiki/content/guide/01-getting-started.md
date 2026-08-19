---
title: Getting started
description: A five-minute path to the current Salamandra baseline, its evidence model, its tools and the physical gates that remain open.
editUrl: https://github.com/bultodepapas/salmandra/edit/main/wiki/content/guide/01-getting-started.md
---

This page gives you a working model of Salamandra in about five minutes. The most
important habit is simple: **identify the release before using a number**.

## 1. Know what you are reading

Salamandra is an open platform for 3D-printed fixed-wing FPV aircraft. Its first
reference design is a modular PETG forward-swept flying wing:

- **CORE** — common center module, battery cradle, avionics and pusher mount.
- **PANEL** — removable wing panels designed against a common neutral-point rule.
- **SALAMANDRA-CLEAN** — finless efficiency configuration.
- **SALAMANDRA-V1** — fixed-fin test configuration, conditional on closing its mass gate.

The current controlled baseline is **{{RELEASE_TAG}} / Design Guide v{{GUIDE_VERSION}}**.
It supports continued CAD and analysis within explicit limits; it does not claim flight
qualification.

## 2. Follow the authority stack

When two documents appear to disagree, use this order:

1. [Current release notes]({{CURRENT_RELEASE_URL}}) — scope, migration rules and released
   limitations.
2. [Design Guide v{{GUIDE_VERSION}}](../salamandra/design-guide/) — controlling geometry,
   interfaces, mass targets, operating limits and load definitions.
3. `calculations/design_config.py` — numerical source of truth for values shared by
   multiple analyses.
4. [Advanced Design Guide](../salamandra/design-guide-advanced/) — calculations,
   release migration and detailed engineering boundaries.
5. [ADRs](../decisions/) — decisions and reversal triggers.
6. [Research threads](../research/) — evidence, methods, sources and limitations.
7. [Open points](../salamandra/design-guide-open-points/) — provisional values and the
   event that may change each one.

Never average conflicting releases or combine a historical input with the current
baseline. Raise the conflict instead.

## 3. Choose the shortest route

| Your task | First page | Follow with |
|---|---|---|
| Model the aircraft | [Concise Design Guide](../salamandra/design-guide/) | [Advanced Design Guide](../salamandra/design-guide-advanced/) only when a requirement needs interpretation |
| Understand a design choice | [ADR index](../decisions/) | The ADR's linked research and calculation |
| Check what remains unknown | [Gap register](../gaps/) | [Test programme](../tests/) |
| Reproduce a result | [Calculation index](../calculations/) | [Reproduction guide](../calculations/reproduction-guide/) |
| Add a part, test or correction | [Contributing](./05-contributing/) | The affected ADR and gap |

## 4. Read provenance tags correctly

| Tag | Meaning | What it permits |
|---|---|---|
| `[M]` | Measured, with a published or project source | Use within the stated test conditions and uncertainty |
| `[D]` | Derived from declared inputs by calculation | Rerun the method and inspect input provenance |
| `[E]` | Estimated on explicit assumptions | Use for reversible work; verify before an irreversible choice |
| `[I]` | Reasoned inference not yet verified | Treat as a hypothesis or design direction |

These are **provenance classes**, not a four-step ranking. A derived result can still be
limited by an estimated input. The [glossary](./04-glossary/) explains the notation and
the difference between section, wing and aircraft quantities.

## 5. Verify a derived number

Run the cross-module contract before an individual analysis:

```bash
python calculations/verify_calculations.py
python calculations/verify_calculations.py --all-scripts
```

Then run the owning model. For the released planform and shared invariants:

```bash
python calculations/design_config.py
```

For the Article #1 manoeuvre and gust-reference screen:

```bash
python calculations/flight_envelope.py
```

The verifier checks that geometry, mass, battery, CG, stall, power, propulsion, controls,
stability and structural models describe the same aircraft. XFOIL workflows and physical
tests remain explicit external gates; they are never silently reported as complete.

## 6. Know what remains open

The current high-value physical gates are:

- **E2 / G2:** measured lift, drag, moment and stall acceptance for Salamandra r1.
- **F2 / OP-24:** CAD mass properties and complete-aircraft scale measurement; the V1
  lower model exceeds its 45 km/h stall allocation by about 6.3 g.
- **S3 / OP-29–30:** printed `GXY`, wing torsional stiffness and elastic-axis measurement
  before expanding the 105 km/h initial speed limit.
- **G11 / E9:** nonlinear dynamic gust response and a defensible negative-lift branch.
- **D2 / E3:** motor–ESC–propeller bench map and measured 95 km/h energy consumption.

Next: [How to read this repository](./02-how-to-read/) explains the record structure;
[Architecture](./03-architecture/) explains how the tools and evidence connect.
