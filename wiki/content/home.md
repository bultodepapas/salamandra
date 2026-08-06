---
title: Salamandra
description: Open 3D-printed FPV aircraft platform — the reasoning is the product. Design guide, ADRs, research threads, gaps and reproducible calculations.
template: splash
hero:
  title: Salamandra
  tagline: An open, community-driven 3D-printed FPV aircraft platform. Every decision carries its rationale, its source and its confidence level — and every number can be reproduced from a script.
  actions:
    - text: Start here
      link: guide/01-getting-started/
      icon: right-arrow
      variant: primary
    - text: GitHub
      link: https://github.com/bultodepapas/salmandra
      icon: external
---

## The reasoning is the product

There are dozens of open-source printed wings. Almost none of them publish **why** they have the geometry they have — and most are a single, finished design. This project is different in two ways:

1. **Reasoning-first.** Every decision carries its rationale, its source and its confidence tag (`[M]`, `[D]`, `[E]`, `[I]`), and the mistakes made along the way are recorded instead of erased. Anyone can trace where each number and shape comes from.
2. **A platform, not a part.** The goal is a continuously evolving, community-driven library of airframes, parts, adapters and experiments. The current reference design — the PETG forward-swept flying wing **Salamandra** — is only the first member.

## Where to go

| I want to ... | Go to |
|---|---|
| Understand the project in 5 minutes | [Getting started](guide/01-getting-started/) |
| Read the design as a CAD-ready spec | [Design guide v0.1](salamandra/design-guide/) |
| See what was decided and why | [Decisions (ADR)](decisions/) |
| See what we researched and the sources | [Research threads](research/) |
| See what we do **not** know yet | [Gap register](gaps/) |
| Reproduce any published number | [Calculations](calculations/) |
| Know the experimental program | [Tests](tests/) |

## Current status

- **Phase 0 (specification): closed.** Phase 1 (geometry and stability) in progress — see the [phase-1 plan](reference/03-phase-1-plan/).
- **Current blocker:** airfoil selection (gap [G2](gaps/)). The root section must be **designed, not selected**.
- Neutral point (G8) is largely closed: **NP = 26.7 % MAC** by in-house VLM, cross-checked by an independent Weissinger-L method (28.0 % MAC, 3 mm agreement).

## The hard rule

> Every quantitative claim carries a confidence tag. **No `[E]` or `[I]` datum supports an irreversible decision without prior verification.** Numbers without a source are not accepted, even if correct.

This is the project's central rule — see the [glossary](guide/04-glossary/).
