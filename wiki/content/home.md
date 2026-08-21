---
title: Design the aircraft from evidence outward
description: Salamandra is an open 3D-printed FPV aircraft programme currently measuring its hardware and power architecture before selecting final geometry or authorizing CAD.
template: splash
editUrl: https://github.com/bultodepapas/salamandra/edit/main/wiki/content/home.md
hero:
  title: Salamandra
  tagline: Mission first. Hardware measured before geometry. CAD only after the evidence closes.
  actions:
    - text: Read the Master Plan
      link: reference/05-master-plan/
      icon: right-arrow
      variant: primary
    - text: Execute MP-04
      link: research/i-33-mp04-propulsion-procurement-and-hardware-characterisation/
      icon: open-book
      variant: minimal
---

## Current programme focus

**Master Plan v2.4 · M0 closed · M1 open · MP-04 active.** Salamandra Article #1 is not
being drawn from an assumed outer shape. The programme defines the mission, measures the
bought-in systems, solves the mass/CG skeleton and only then selects the aircraft
architecture and shapes the fuselage around it.

| Control item | Current state | Authority |
|---|---|---|
| Product objective | Minimize measured total battery-terminal Wh/km after safety and controllability gates; no arbitrary range or roll-rate target | [Article #1 requirements](reference/00-objectives-and-requirements/) |
| First prototype | **SALAMANDRA-6S-R**: one pusher motor, front DJI O4 camera, 6S1P P42A and a removable rudder-capable directional module | [Master Plan](reference/05-master-plan/) |
| Controlled comparison | **6S-CLEAN** follows the safe R baseline; **8S-STUDY** remains a separate, non-flight study | ADR-0048 · mission contract |
| Current work | Procure/mock hardware, execute H01–H22 and produce the guarded 6S propulsion map | [I-33 MP-04 campaign](research/i-33-mp04-propulsion-procurement-and-hardware-characterisation/) |
| Explicit hold | No production wing, fuselage or OML CAD before measured hardware, mass skeleton and architecture selection | Master Plan M1–M7 |

## MP-04 is ready to execute

The digital preparation is complete; the remaining evidence is physical:

- the [22-row hardware and power manifest](reference/17-article-1-hardware-manifest/)
  owns configuration membership, planning mass, envelopes and rail loads;
- the [MP-04 protocol](tests/mp04-hardware-characterisation/) owns specimen identity,
  instruments, UTC timestamps, raw evidence and every required H01–H22 value;
- the generated OpenSCAD shells provide external-envelope dummies with ballast cavities,
  never flight hardware;
- the procurement screen keeps catalog data separate from measured selection; and
- the blank record is correctly **0/22 accepted**, so M1 remains open.

| Bench article | Controlled screen |
|---|---|
| Battery | P42A 6S1P: 21.6 V nominal / 25.2 V full; at least 20 mm total longitudinal adjustment remains a separate requirement |
| 6S motors | T-Motor MN3110 KV470 primary and MN4010 KV475 robust alternate |
| 6S ESC | APD 80F3[X]v2 reference; Hobbywing FlyFun 60A V5 protocol/thermal fallback |
| Propellers | APC 8x8E datum, 8x6E pitch sensitivity and clearance-conditional 9x7.5E diameter sensitivity |
| 8S | MN4010 KV370 / MN4012 KV400 and APD 120F3[X]v2 remain study-only; no current purchase authority |

## Choose your route

| If you are… | Start here | Then verify with… |
|---|---|---|
| Directing the programme | [Master Plan v2.4](reference/05-master-plan/) | [Active requirements](reference/00-objectives-and-requirements/) and gate status |
| Buying or measuring hardware | [I-33](research/i-33-mp04-propulsion-procurement-and-hardware-characterisation/) | [H01–H22 protocol](tests/mp04-hardware-characterisation/) and hardware manifest |
| Reproducing a number | [Calculation index](calculations/) | [Reproduction guide](calculations/reproduction-guide/) and system verifier |
| Reviewing prior work | [ADR disposition](decisions/redesign-disposition/) | The linked research, calculation and historical release |
| Inspecting v0.6 geometry | [Historical Design Guide](salamandra/design-guide/) | [Drawings](guide/06-drawings/) and the explicit engineering hold |
| Contributing now | [Contribution path](guide/05-contributing/) | A measured H-gate, fixture, replication or correction |

## Historical release boundary

The tagged **{{RELEASE_TAG}} / Design Guide v{{GUIDE_VERSION}}** package remains a
reproducible comparison baseline. Its 1,300 mm forward-swept planform, airfoils, passive
twin-fin variant and inferred fuselage are not the selected redesign. Use them to recover
methods and compare candidates, never to bypass the Master Plan or start production CAD.

## How the record works

1. **Inputs keep their provenance.** Measurements are `[M]`; estimates and inferences
   remain visibly `[E]` or `[I]`.
2. **Derived results are rerunnable.** Python analyses produce `[D]` results and validate
   their internal and cross-module contracts.
3. **Research and decisions stay separate.** Research says what the evidence supports;
   ADRs state what was chosen and what would reverse it.
4. **Unknowns have closure records.** A blank schema is a method, not a measurement.
5. **Corrections remain visible.** The [changelog](platform/changelog/) records the chain
   through C{{LATEST_CORRECTION}}.

> No `[E]` or `[I]` datum supports an irreversible decision without prior verification.
