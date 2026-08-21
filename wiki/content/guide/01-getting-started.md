---
title: Getting started
description: A five-minute path through Salamandra's Master Plan, active MP-04 hardware campaign, evidence model and historical v0.6 baseline.
editUrl: https://github.com/bultodepapas/salamandra/edit/main/wiki/content/guide/01-getting-started.md
---

This page gives you a working model of Salamandra in about five minutes. The most
important habit is now: **identify which programme gate and configuration owns a value
before using it**.

## 1. Know what is being designed

Salamandra Article #1 is a single-motor, front-camera, predominantly PETG tailless FPV
aircraft. Its first priority is safe, controllable testing; its performance objective is
the lowest practicable total battery-terminal Wh/km while retaining useful handling and
field durability.

The current configurations are:

- **SALAMANDRA-6S-R** — first-flight baseline with a removable rudder-capable directional
  module;
- **SALAMANDRA-6S-CLEAN** — later comparison without the vertical module; and
- **SALAMANDRA-8S-STUDY** — separate architecture study, not a first-flight build.

Forward sweep, the old `CORE`/`PANEL` architecture and the v0.6 fuselage are candidates,
not requirements. Production CAD is held.

## 2. Follow the active authority stack

When documents appear to disagree, use this order:

1. [Master Design Plan v2.4](../reference/05-master-plan/) — programme intent, sequence,
   gate status and authorization.
2. [Article #1 requirements](../reference/00-objectives-and-requirements/) and
   `mission_contract.py` — product objective, configurations, mission states and scoring.
3. [Hardware and power manifest](../reference/17-article-1-hardware-manifest/) — candidate
   6S-R/CLEAN equipment, separate 8S study overlay and H01–H22 ownership.
4. [I-33 MP-04 campaign](../research/i-33-mp04-propulsion-procurement-and-hardware-characterisation/)
   plus the [measurement protocol](../tests/mp04-hardware-characterisation/) — procurement
   specimens, test method and physical evidence schema.
5. [ADR redesign disposition](../decisions/redesign-disposition/) — whether each historical
   decision is retained, method-only, candidate-only, reopened, superseded or cancelled.
6. [Historical release notes]({{CURRENT_RELEASE_URL}}), Design Guide and `design_config.py`
   — v0.6 comparison baseline only until a later gate explicitly reselects a value.

Never combine an active mission value with a historical geometry value and call the result
the redesigned aircraft.

## 3. Understand the current work

M0 is closed. MP-01 through MP-03 established the mission, reset the ADR authority and
published the candidate hardware/power manifest. **MP-04 is active.** Its digital
infrastructure is ready, but physical evidence is still open.

| Ready now | Still required |
|---|---|
| 6S/8S voltage and Kv/RPM screen | Traceable procured specimens |
| MN3110 KV470 / MN4010 KV475 shortlist | Measured motor constants and thermal map |
| APD 80F3[X]v2 6S reference | Installed capacitor/leads, protocol and fault proof |
| APC 8x8E / 8x6E / conditional 9x7.5E articles | Guarded thrust, RPM, power and temperature map |
| H01–H22 JSON schema | Accepted measurements with evidence files and UTC timestamps |
| OpenSCAD envelope shells | Printed, ballasted and measured packaging dummies |

The next action is Tranche A packaging work followed by the guarded Tranche B 6S bench
chain. 8S Tranche C remains held until a quantified benefit justifies it.

## 4. Choose the shortest route

| Your task | First page | Follow with |
|---|---|---|
| Direct programme work | [Master Plan](../reference/05-master-plan/) | The current gate's exit evidence |
| Buy or test hardware | [I-33](../research/i-33-mp04-propulsion-procurement-and-hardware-characterisation/) | [H01–H22 protocol](../tests/mp04-hardware-characterisation/) |
| Review candidate equipment | [Hardware manifest](../reference/17-article-1-hardware-manifest/) | Candidate calculator and source notes |
| Reproduce a result | [Calculation index](../calculations/) | [Reproduction guide](../calculations/reproduction-guide/) |
| Interpret prior CAD | [Historical Design Guide](../salamandra/design-guide/) | [ADR disposition](../decisions/redesign-disposition/) |
| Add evidence or a fixture | [Contributing](./05-contributing/) | The affected H-gate, research thread and raw data |

## 5. Read provenance tags correctly

| Tag | Meaning | What it permits |
|---|---|---|
| `[M]` | Measured, with source and conditions | Use only inside the stated configuration and uncertainty |
| `[D]` | Derived from declared inputs by calculation | Rerun the method and inspect input provenance |
| `[E]` | Estimated on explicit assumptions | Reversible planning only; verify before commitment |
| `[I]` | Reasoned inference not yet verified | Hypothesis, trade input or research direction |

A manufacturer mass is `[M]` for the catalog specimen but does not become Salamandra's
installed mass. H01–H22 must include the actual component, shortened leads, connectors,
mounts and service loops.

## 6. Reproduce the active state

Run these commands from the repository root:

```bash
python3 calculations/hardware_manifest.py
python3 calculations/hardware_candidate_trade.py
python3 calculations/hardware_measurements.py --check
python3 calculations/generate_hardware_dummies.py --check
python3 calculations/verify_calculations.py
python3 calculations/mutation_test.py
```

The default verifier runs both the cross-module contracts and every deterministic local
CLI. XFOIL and physical tests remain explicit external gates; they are never silently
reported as complete.

Next: [How to read the record](./02-how-to-read/) explains document roles;
[Architecture](./03-architecture/) shows how mission, hardware, models and evidence
connect.
