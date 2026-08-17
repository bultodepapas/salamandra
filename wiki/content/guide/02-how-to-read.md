---
title: How to read this repo
description: The repository folder map and the traceability flow that connects decisions, research, gaps, tests and calculations.
editUrl: https://github.com/bultodepapas/salmandra/edit/main/wiki/content/guide/02-how-to-read.md
---

# How to read this repository

The repository is a **reasoning repository**: its structure mirrors how a claim travels from a source, through a calculation, into a decision and finally into the design.

## Folder map

| Folder | What it contains |
|---|---|
| [`design/`](../salamandra/) | **Salamandra Design Guide v0.1** — the CAD-ready specification, its justification, and the open points |
| [`docs/`](../reference/) | Specification, status, phase plan, conventions, master plan |
| [`decisions/`](../decisions/) | **One file per decision (ADR)**: context, alternatives, consequences |
| [`research/`](../research/) | **Research threads**: what was searched, what was found, what sources |
| [`gaps/`](../gaps/) | Register of what we do **not** know and how it gets closed |
| [`tests/`](../tests/) | Experimental program and data |
| [`calculations/`](../calculations/) | Analysis scripts, with validation cases — full reproduction guide |
| `geometry/` `stl/` `cad/` | Community 3D parts and outputs |

## The traceability flow

```
[M] primary sources ──► scripts ──► [D] derived results ──► research threads (I-XX)
                                                                   │
                          design guide ◄── ADRs (decisions) ◄──────┘
                              │                    ▲
                              │                    │
                          CAD / STL (community)    gaps (G-XX) ──► tests (E-XX)
```

The folders are separated **on purpose**: an ADR says *what was decided*; a research thread says *what we know and how*. One piece of research feeds several decisions, and one decision rests on several pieces of research. Merging them forces duplication or loss of traceability.

## Where the status lives

- **Global status** — [project readme](../platform/readme/): phases, current blocker, latest results.
- **What we do not know** — [gap register](../gaps/): read it before proposing anything; it changes.
- **What is due now** — [phase-1 plan](../reference/03-phase-1-plan/).

## Conventions you will meet everywhere

- **Signs:** sweep negative forward (the project uses −15° at c/4) · positive twist = wash-in (tip at higher incidence) · in `calculations/`, `x` positive backward with origin at the root c/4.
- **Units:** SI in calculations; tables may use km/h and g/dm².
- **Drag:** never a single Oswald factor — the viscous and induced terms are always separated (ADR-0009).

Full detail in the [conventions](../reference/04-conventions/) document and the [glossary](./04-glossary/).
