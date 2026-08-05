# 3D-printed FPV aircraft platform — open, modular, AI-assisted

A completely free, community-driven platform for 3D-printed fixed-wing FPV aircraft.
The core design principles are developed largely through **AI-assisted research**, while the
**final aircraft and its 3D models are created collaboratively by humans and AI**.

This is an **evolving platform**, not a single aircraft. It currently targets a PETG
forward-swept flying wing, but that is only the first design. The repository is meant to
grow into a whole family of airframes, parts, adapters and experiments — contributed by
the community.

**Revision 1.11** · 5 August 2026 · **Phase 0 closed · Phase 1 in progress**

---

## What this project is

There are dozens of open-source printed wings. Almost none of them publish **why** they
have the geometry they have. And most of them are a single, finished design.

This project is different in two ways:

1. **The reasoning is the product.** Every decision carries its rationale, its source and
   its confidence level, and the mistakes made along the way are recorded instead of
   erased. Anyone can trace where each number and each shape comes from.
2. **It is a platform, not a part.** The goal is a continuously evolving, community-driven
   library of aircraft, components, variants and experiments — with this repository as the
   central archive.

**It is fully free and as open as possible.** Contributors are encouraged to open pull
requests with modifications, improvements and new variants.

---

## The AI–human workflow

AI and the community have complementary roles:

| | What AI does best | What humans do best |
|---|---|---|
| **AI-assisted research** | Aerodynamic analysis, theoretical research, data cross-validation (XFOIL, VLM, propeller matching), design exploration and trade studies | Experimentation, practical judgment, manufacturing experience, engineering intuition, ground/bench/flight testing |
| **Design** | Parametric reasoning, sizing trades, geometric constraints, documentation | Creating the actual 3D parts (Fusion 360 / CAD), CAD detail, and translating research into reliable native models |

Today, AI is still not particularly effective at directly creating reliable, parametric
Fusion 360 models or native CAD files. That is intentional and expected: **the community
creates the actual 3D parts** based on our AI-assisted research, on their own engineering
knowledge, or on a combination of both.

The repository is built so the two can meet: the research and analysis tell *what* and
*why*; the community provides the *how* — the parts that realize it.

---

## Why it is open

- **Free.** No paywall, no locked files, no licensing fees. The project is meant to be
  used, built and shared.
- **Community-driven.** PRs with modifications, improvements and new variants are welcome
  and expected. The platform grows through its contributors.
- **Broad contributions.** Human expertise is especially valuable in experimentation,
  practical judgment, manufacturing and engineering intuition — but contributions are not
  limited to aerodynamics or structures. Decorative parts, visual improvements, equipment
  mounts and other creative modifications are welcome too.
- **Reciprocal.** Under the project's licences, derivatives stay open, so the whole
  community benefits from every contribution. See [Licence](#licence).

---

## Modular platform and extensibility

The aircraft is designed as a **modular platform**:

- **Replaceable wings.** Larger or differently shaped wings can be swapped onto the common
  center module.
- **Body variants.** Contributors can create complete fuselage variations, larger
  fuselages, different wingtips, alternative rudders and control surfaces.
- **Different configurations.** The platform is not limited to the current forward-swept
  flying wing. Future directions may include conventional fuselage designs, V-tail
  configurations, tractor or pusher propulsion systems, and many other aircraft layouts.
- **Hardware archive.** This repository is also the central archive for adapters and
  mounting systems for different FPV equipment, electronics, propulsion systems and
  related hardware.

---

## Initial design: Salamandra, the forward-swept flying wing

This is the first, reference design on the platform, named **Salamandra**. Its current
specification for the designer is the
[**Salamandra Design Guide v0.1**](design/Salamandra-Design-Guide-v0.1.md), with the
justification in [`design/`](design/). The baseline is a PETG forward-swept flying wing,
**modular and configurable**: a standard center module and interchangeable wing panels.
Efficient FPV cruise flight, with electronics chosen by the builder.

### Measurable objective

| | Value |
|---|---|
| Market reference | **TBS Mojito** — 1.40 Wh/km measured, USD 189.95 |
| **Target** | **≤ 1.15 Wh/km** at 95 km/h |
| Where it comes from | **Propeller matching**, +20 % demonstrated on UIUC data `[D]` |

The initial analysis showed that the Mojito **is not energy-efficient** — it consumes
0.74 Wh/(km·kg), the same as a USD 40 foam wing; its achievement is sustaining that at
2–3× the speed. This design's efficiency does not come from optimistic aerodynamics: it
comes from the propulsion chain, which is where the data say the gap is.

**It is falsifiable.** It is measured with [E2](tests/) and [E3](tests/).

### Article #1 — Cruise configuration

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

### Modular architecture

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

⚠️ See [ADR-0032](decisions/ADR-0032-modularity.md): the panels **are not arbitrary**. Each
set is designed against a common neutral point. The same discipline applies to every new
configuration contributed to the platform.

---

## How to navigate this repository

| Folder | What it contains |
|---|---|
| [`design/`](design/) | **Salamandra Design Guide v0.1** — the CAD-ready specification handed to the designer, its justification, and the open points |
| [`docs/`](docs/) | Specification, status, phase plan, conventions, [master plan up to the first prototype](docs/05-master-plan.md) |
| [`decisions/`](decisions/) | **One file per decision (ADR)**: context, alternatives, consequences |
| [`research/`](research/) | **Research threads**: what was searched, what was found, what sources |
| [`gaps/`](gaps/) | Register of what we do **not** know and how it gets closed |
| [`tests/`](tests/) | Experimental program and data |
| [`calculations/`](calculations/) | Analysis scripts, with validation cases — **full reproduction guide in its README** |
| `geometry/` `stl/` `cad/` | Community 3D parts and outputs; `geometry/airfoils/` holds the screening coordinate files with provenance |

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

Phase-1 status (2026-08-05):

- **G8 (neutral point) — largely closed.** NP = 26.7 % MAC by the in-house panel VLM,
  **cross-checked by an independent Weissinger-L lifting line: 28.0 % MAC, 3 mm
  agreement** ([I-15 §6.3](research/I-15-airfoil-evidence-campaign.md)). The
  central-body effect remains unquantified and moves the NP forward.
- **G2 (airfoil) — screening executed.** The B3 XFOIL screening (24 polars,
  Re 3e5/5e5 × Ncrit 10/12) discarded E205 (cm0 ≈ −0.07) and showed that **no
  off-the-shelf reflexed section satisfies R-AIRFOIL at 13.5 % t/c nor closes the
  trim inside the torsion window at SM 8 %** — the root section must be **designed,
  not selected** ([I-15 §6](research/I-15-airfoil-evidence-campaign.md)).

---

## Reproducible analysis — tools used

Every quantitative claim in this repository comes from scripts that anyone can rerun.
The full guide (versions, commands, batch quirks, validation discipline) is in
[`calculations/README.md`](calculations/README.md). Summary:

| Tool | Version | Role |
|---|---|---|
| Python + numpy | 3.11 / 1.2x | In-house panel VLM, Weissinger-L NP check, screening harness |
| **XFOIL** | **6.99** (official MIT build, GPL) | Airfoil polar generation for the B3 screening and the E387 calibration |
| UIUC Airfoil Data Site, aerodesign.de | — | Measured/published input data (`[M]`), coordinates in `geometry/airfoils/` |

Reproduction in three commands:

```bash
python3 calculations/vlm_ala_volante.py       # NP (I-07)
python3 calculations/weissinger_np.py         # C2 independent NP check (I-15 §6.3)
python3 calculations/b3_screening.py --xfoil /path/to/xfoil.exe   # B3 screening (I-15 §6)
```

Each script ships its validation case; a modification that breaks the validation is
not accepted.

---

## Contributing

This is a community project. Contributions of all kinds are welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md). In short:

- Contributions that **raise the confidence level of a datum** (measurements, corrections,
  replications) are the highest value.
- **Any new part, variant or configuration** — wings, fuselages, wingtips, rudders,
  control surfaces, mounts, adapters, decorative or creative pieces — is welcome.
- Numbers without a source are not accepted in the technical record, even if they are
  correct.

## Licence

This is free and open hardware.

- **Hardware design and 3D models** (CAD/STL), geometry, and the analysis/design scripts
  are licensed under the **CERN Open Hardware Licence Version 2 — Strongly Reciprocal**
  (CERN-OHL-S-2.0). See [`LICENSE`](LICENSE).
- **Documentation** (the `.md` files) is licensed under
  **Creative Commons Attribution-ShareAlike 4.0** (CC BY-SA 4.0). See
  [`LICENSE-docs.md`](LICENSE-docs.md).

Both licences are reciprocal: derivatives of the community's work stay open, so the whole
platform benefits from every contribution.
