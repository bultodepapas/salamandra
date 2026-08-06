---
title: Glossary
description: The vocabulary of the project — confidence tags, identifiers, signs, units and key aerodynamic terms.
editUrl: https://github.com/bultodepapas/salmandra/edit/main/wiki/content/guide/04-glossary.md
---

# Glossary

The vocabulary you will meet in every document of this repository.

## Confidence tags

Every quantitative claim carries one of these:

| Tag | Meaning |
|---|---|
| `[M]` | **Measured** and published by a primary source |
| `[D]` | **Derived** by calculation from `[M]` data |
| `[E]` | **Estimated** on declared assumptions |
| `[I]` | **Reasoned inference**, not verified |

> **Hard rule:** no `[E]` or `[I]` datum supports an irreversible decision without prior verification.
>
> **Operational corollary:** before writing a number, decide its tag. If you cannot assign one, do not write it yet.

## Identifiers

| Prefix | Meaning |
|---|---|
| `ADR-XXXX` | Decision record (one file per decision) |
| `I-XX` | Research thread (what we searched and found) |
| `GX` | Gap (an unknown that prevents or degrades a decision) |
| `EX` | Experimental test |
| `OX` | Objective |
| `R-XXXX` | Requirement |
| `CX` | Correction (recorded in the changelog) |
| `OP-XX` | Open point |

## Signs and units

| Convention | Value |
|---|---|
| Sweep | **Negative forward** — the project uses ≈ −20° at c/4 |
| Twist | **Positive = wash-in** (tip at higher incidence) |
| `x` axis in `calculations/` | **Positive backward**, origin at the root c/4 |
| Units | SI in calculations; tables may use **km/h** and **g/dm²** |

## Key terms

- **FSW** — forward-swept wing. The reason Salamandra is unusual: efficient trim and root-first stall, at the cost of aeroelastic divergence risk.
- **MAC** — mean aerodynamic chord. The reference chord of the wing; the neutral point and CG are expressed as a percentage of it (e.g. NP = 26.7 % MAC).
- **Neutral point (NP)** — the aerodynamic center of the whole aircraft. The CG must sit ahead of it.
- **Static margin (SM)** — distance CG→NP as % of MAC. Salamandra targets **8 %**.
- **Wing loading** — mass per unit area (e.g. 57 g/dm²). Drives stall speed.
- **Aspect ratio (AR)** — span²/area. Salamandra cruise configuration: **6.0**.
- **Reflexed airfoil** — a section with positive pitching moment coefficient (`Cm0`) that can trim a tailless aircraft.
- **Cm0** — section pitching-moment coefficient at zero lift. The project needs **Cm0 ≥ +0.008** (R-AIRFOIL).
- **Wash-in** — tip at higher incidence than root (positive twist here). Provides part of the tailless trim.
- **Divergence** — aeroelastic instability at high speed on forward-swept wings; the project's dominant risk.
- **Elevon** — combined elevator+aileron control surface, the only control on a flying wing.
- **Torsion window** — the allowed range of wash-in between trim (lower limit) and tip stall (upper limit).
- **Southwell test (E7)** — in-flight extrapolation of divergence speed from trim deflection vs dynamic pressure.
- **Wh/km** — specific energy per distance, the efficiency metric of the mission (target ≤ 1.15).
