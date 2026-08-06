---
title: Getting started
description: The shortest path to understanding Salamandra — what it is, how the wiki is organized, and how to verify any number.
editUrl: https://github.com/bultodepapas/salmandra/edit/main/wiki/content/guide/01-getting-started.md
---

# Getting started

Welcome. This page is the shortest path from zero to a working mental model of the project. It takes about five minutes.

## What this project is

**Salamandra** is an open, community-driven platform for 3D-printed fixed-wing FPV aircraft — not a single finished design. Its current reference design is a PETG **forward-swept flying wing**, modular and configurable: a standard center module (CORE) and interchangeable wing panels (PANEL).

The platform's defining trait is that **the reasoning is the product**:

- Every decision carries its rationale, its source and its confidence level.
- Every number is backed by a calculation or a source.
- Mistakes are recorded (in the changelog) instead of erased.

## The wiki map

| Section | Contains | Read it when ... |
|---|---|---|
| [Salamandra](../salamandra/) | The design guide v0.1 (the CAD-ready spec), its justification and open points | You want the design itself |
| [Decisions (ADR)](../decisions/) | One file per decision: context, alternatives, consequences | You ask "why?" about any design choice |
| [Research](../research/) | What was searched, what was found, with what sources | You want the evidence behind a decision |
| [Gaps](../gaps/) | What we do **not** know, and how it gets closed | You want the honest limitations |
| [Tests](../tests/) | The experimental program that closes gaps | You want to know how claims get measured |
| [Calculations](../calculations/) | Validated, rerunnable analysis scripts | You want to verify a number yourself |

## A 3-click path

1. **Read this page** and the [current status](../platform/readme/).
2. **Skim the [design guide v0.1](../salamandra/design-guide/)** — it is the specification that a designer turns into CAD.
3. **Open the [ADR index](../decisions/)** and follow any decision that caught your attention.

From there, the [architecture page](./03-architecture/) explains how all these pieces feed each other.

## The confidence convention

Every quantitative claim carries a tag:

| Tag | Meaning |
|---|---|
| `[M]` | Measured and published by a primary source |
| `[D]` | Derived by calculation from `[M]` data |
| `[E]` | Estimated on declared assumptions |
| `[I]` | Reasoned inference, not verified |

**Hard rule:** no `[E]` or `[I]` datum supports an irreversible decision without prior verification.

The tone of a claim must carry its tag: an `[E]` is not communicated like an `[M]`. See the [glossary](./04-glossary/).

## How to verify any number

1. Find the claim and its tag — e.g. **NP = 26.7 % MAC `[D]`**.
2. The `[D]` traces to a script in [`calculations/`](../calculations/) (`vlm_ala_volante.py` in this case).
3. Run it. Every script ships its **validation case** and must pass it before it is trusted:

```bash
python3 calculations/vlm_ala_volante.py
```

A modification that breaks the validation is not accepted.

## Next steps

- [How to read this repo](./02-how-to-read/) — the folder map and the traceability flow.
- [Architecture](./03-architecture/) — how research, decisions, gaps, tests and calculations feed each other.
- [Contributing](./05-contributing/) — how to help, and what is worth most.
