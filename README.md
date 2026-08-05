# Forward-swept FPV flying wing — modular 3D-printed platform

PETG forward-swept flying wing, **modular and configurable**: a standard center module and interchangeable wing panels. Efficient FPV cruise flight, with electronics chosen by the builder.

**Revision 1.5** · 28 July 2026 · **Phase 0 closed · Phase 1 in progress**

---

## What this project is

There are dozens of open-source printed wings. Almost none of them publish **why** they have the geometry they have.

This project's contribution is not the STL: it is that **every decision carries its rationale, its source, and its confidence level**, and that **the mistakes made along the way are recorded instead of erased**.

It is an **evolutionary** repository. Right now it defines the foundations; the geometry will come later. What never changes is the criterion: **no decision without a declared rationale.**

## Measurable objective

| | Value |
|---|---|
| Market reference | **TBS Mojito** — 1.40 Wh/km measured, USD 189.95 |
| **Target** | **≤ 1.15 Wh/km** at 95 km/h |
| Where it comes from | **Propeller matching**, +20 % demonstrated on UIUC data `[D]` |

The initial analysis showed that the Mojito is **not energy-efficient** — it consumes 0.74 Wh/(km·kg), the same as a USD 40 foam wing; its achievement is sustaining that at 2–3× the speed. This project's efficiency does not come from optimistic aerodynamics: it comes from the propulsion chain, which is where the data say the gap is.

**It is falsifiable.** It is measured with [E2](tests/) and [E3](tests/).

---

## How to navigate this repository

| Folder | What it contains |
|---|---|
| [`docs/`](docs/) | Specification, status, phase plan, conventions, [master plan up to the first prototype](docs/05-master-plan.md) |
| [`decisions/`](decisions/) | **One file per decision (ADR)**: context, alternatives, consequences |
| [`research/`](research/) | **Research threads**: what was searched, what was found, what sources |
| [`gaps/`](gaps/) | Register of what we do **not** know and how it gets closed |
| [`tests/`](tests/) | Experimental program and data |
| [`calculations/`](calculations/) | Analysis scripts, with validation cases |
| `geometry/` `stl/` `cad/` | Phase 1 outputs and beyond |

**Start with:** [`docs/00-objectives-and-requirements.md`](docs/00-objectives-and-requirements.md) → [`decisions/README.md`](decisions/README.md) → [`gaps/README.md`](gaps/README.md)

---

## Confidence convention

This is the project's central rule. Every quantitative claim carries a tag:

| Tag | Meaning |
|---|---|
| `[M]` | Measured and published by a primary source |
| `[D]` | Derived by calculation from `[M]` data |
| `[E]` | Estimated on declared assumptions |
| `[I]` | Reasoned inference, not verified |

> **Hard rule:** no `[E]` or `[I]` datum supports an irreversible decision without prior verification.
>
> **Corollary:** when better data overturn a conclusion, it is recorded in the [CHANGELOG](CHANGELOG.md) with a correction number. There are 21 so far.

---

## Article #1 — Cruise configuration

| Parameter | Value | Decision |
|---|---|---|
| Wingspan | 1300 mm | [ADR-0010](decisions/ADR-0010-mission-branch.md) |
| Aspect ratio | 6.0 · S = 0.282 m² `[E]` | [ADR-0004](decisions/ADR-0004-aspect-ratio.md) |
| **t/c** | **13.5 % root / 9 % tip** | [ADR-0027](decisions/ADR-0027-relative-thickness.md) |
| Material | **Conventional PETG**, light color | [ADR-0021](decisions/ADR-0021-base-material.md) |
| Perimeters / infill | 2 (0.9 mm) / **gyroid 5 %** | [ADR-0028](decisions/ADR-0028-gyroid-infill.md) |
| Section | Three cells: D-box + center + hinge | [ADR-0002](decisions/ADR-0002-closed-shell.md) |
| Carbon | Bending tube + pin. **Not torsional** | [ADR-0015](decisions/ADR-0015-carbon-non-torsional.md) |
| AUW (6S1P) | ~1620 g · 57 g/dm² | — |
| V_NE article #1 | **160 km/h** (design 180) | — |
| Avionics | INAV 9.1+ or ArduPlane · **pitot mandatory** | — |

---

## Modular architecture

```
CORE-1          Center module. Wing joiners up to ~30 % of half-span,
                battery bay with longitudinal adjustment, avionics, motor mount.

PANEL-xxxx-y    xxxx = resulting total wingspan · y = airfoil family
```

| Config | Panels | Suggested battery | Use | Status |
|---|---|---|---|---|
| **Range** | 1600 | 4S2P Li-Ion 21700 | Maximum range | Design |
| **Cruise** | 1300 | 6S1P Li-Ion 21700 | **Article #1** | Design |
| **Sport** | 1100 | 6S LiPo | Fast flight | Design |

⚠️ See [ADR-0032](decisions/ADR-0032-modularity.md): the panels **are not arbitrary**. Each set is designed against a common neutral point.

---

## Status

| Phase | Status |
|---|---|
| 0 — Specification | ✅ **Closed** |
| **1 — Geometry and stability** | 🔄 In progress · see [`docs/03-phase-1-plan.md`](docs/03-phase-1-plan.md) |
| 2 — Weights and balancing | ⬜ |
| 3 — Performance | ⬜ |
| 4 — Loads and structure | ⬜ |
| 5 — Systems and propulsion | ⬜ |
| 6 — Manufacturing and release | ⬜ |

**Current blocker: [G2](gaps/README.md) — airfoil selection.**

G8 (neutral point) partially closed: **NP = 26.7 % MAC**, target CG 18.7 % MAC. See [I-07](research/I-07-neutral-point-torsion-window.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: contributions that **raise the confidence level of a datum** are accepted. Numbers without a source are not accepted, even if they are correct.

## License

Pending. Candidates: CERN-OHL-S (hardware, strong copyleft) or CC BY-SA 4.0 for documentation.
