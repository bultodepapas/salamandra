---
title: Open aircraft engineering you can audit
description: Salamandra is an open 3D-printed FPV aircraft platform with a traceable design record, reproducible analyses and explicit physical acceptance gates.
template: splash
editUrl: https://github.com/bultodepapas/salmandra/edit/main/wiki/content/home.md
hero:
  title: Salamandra
  tagline: Open aircraft engineering you can audit. Derived values are rerunnable, measured inputs retain provenance, and unresolved assumptions stay visible.
  image:
    file: ../../assets/salamandra-planform.svg
    alt: Technical top-view diagram of Salamandra's 1,300 mm forward-swept wing, showing the quarter-chord line, center module, neutral point and target center of gravity.
  actions:
    - text: Read the current release
      link: '{{CURRENT_RELEASE_URL}}'
      icon: right-arrow
      variant: primary
    - text: Start in five minutes
      link: guide/01-getting-started/
      icon: open-book
      variant: minimal
---

## Current engineering baseline

**{{RELEASE_TAG}} · Design Guide v{{GUIDE_VERSION}} · Phase 1 in progress.** The current
release connects the Article #1 geometry, mass, propulsion and flight-load definitions
to one numerical contract. It is suitable for continued CAD and analysis within the
published gates; it is **not flight qualification**.

| Control item | Released value | Authority |
|---|---|---|
| Planform | 1,300 mm span · 0.282 m² · AR 6.0 · −15° quarter-chord sweep | [Design guide](salamandra/design-guide/) · ADR-0040 |
| Article #1 mass | 1,583.5 g CLEAN · 1,626.5 g V1 lower model | ADR-0043 · correction C32 |
| Operating speeds | 95 km/h cruise · 105 km/h initial limit · 160 km/h article V_NE | [Current release]({{CURRENT_RELEASE_URL}}) |
| Structural cases | +6/−3 g manoeuvre limit · +9/−4.5 g ultimate | ADR-0044 · I-24 |

The gates that matter now are physical: E2 aerodynamic acceptance, F2 CAD and measured
mass, S3 printed-wing torsion and elastic axis, G11/E9 dynamic gust response, and D2/E3
propulsion and energy measurement. See the [open-points register](salamandra/design-guide-open-points/)
before using a provisional value.

## Choose your route

| If you are… | Start here | Then verify with… |
|---|---|---|
| Building CAD | [Design Guide v{{GUIDE_VERSION}}](salamandra/design-guide/) | [Open points](salamandra/design-guide-open-points/) and the current release migration rules |
| Reviewing a decision | [ADR index](decisions/) | The linked research thread, calculation and reversal trigger |
| Reproducing a number | [Calculation index](calculations/) | The [reproduction guide](calculations/reproduction-guide/) and system verifier |
| Planning a test | [Gap register](gaps/) | The [experimental programme](tests/) and required configuration metadata |
| Contributing a part or correction | [Contribution path](guide/05-contributing/) | The affected ADR, gap and confidence tag |

## How the record works

1. **Inputs keep their provenance.** Published or project measurements are `[M]`;
   estimates and inferences remain visibly `[E]` or `[I]`.
2. **Derived results are rerunnable.** Python analyses turn declared inputs into `[D]`
   results and validate internal invariants.
3. **Research and decisions stay separate.** Research threads document what the evidence
   says; ADRs record what the project chose and what would reverse that choice.
4. **Unknowns have owners.** Gaps name the missing evidence, and tests define how it will
   be measured.
5. **Corrections are never hidden.** The [changelog](platform/changelog/) records the
   correction chain through C{{LATEST_CORRECTION}}.

## The governing rule

> No `[E]` or `[I]` datum supports an irreversible decision without prior verification.

The tags describe **provenance**, not a cosmetic confidence score. Read
[How to read this repository](guide/02-how-to-read/) before combining values from
different documents or releases.
