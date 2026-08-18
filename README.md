# 3D-printed FPV aircraft platform — open, modular, AI-assisted

A completely free, community-driven platform for 3D-printed fixed-wing FPV aircraft.
The core design principles are developed largely through **AI-assisted research**, while the
**final aircraft and its 3D models are created collaboratively by humans and AI**.

This is an **evolving platform**, not a single aircraft. It currently targets a PETG
forward-swept flying wing, but that is only the first design. The repository is meant to
grow into a whole family of airframes, parts, adapters and experiments — contributed by
the community.

**Revision 1.17** · 17 August 2026 · **Release v0.4.0 · Phase 1 in progress**

> 📖 **Read this project as a website:** <https://bultodepapas.github.io/salmandra/>
> — searchable, with auto-generated indexes and an onboarding guide.

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
[**Salamandra Design Guide v0.21**](design/Salamandra-Design-Guide-v0.1.md), with the
justification in [`design/`](design/). The baseline is a PETG forward-swept flying wing,
**modular and configurable**: a standard center module and interchangeable wing panels.
Efficient FPV cruise flight, with electronics chosen by the builder.

**📦 Current release — `v0.4.0`: Article #1 flight-load envelope.** The Design Guide
is the authoritative entry point. This release promotes C29–C34 into one controlled
baseline and fixes the structural meaning of the load cases: +6/−3 g are provisional
manoeuvre limits, while +9/−4.5 g are their ultimate structural cases. It also publishes
the positive V-n branch and keeps the nonlinear dynamic-gust response explicitly open.
Read the [**v0.4.0 release notes**](docs/11-release-v0.4.md) before structural sizing.
Historical v0.1.0–v0.3.0 notes remain audit records.
The wiki renders the package at
<https://bultodepapas.github.io/salmandra/>.

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
| Quarter-chord sweep | **−15°** | [ADR-0040](decisions/ADR-0040-quarter-chord-sweep.md) |
| **t/c** | **13.5 % root / 9 % tip** | [ADR-0027](decisions/ADR-0027-relative-thickness.md) |
| Airfoil | **Salamandra r1:** MH60 mean line, +1.0°/+0.5° root/tip reflex | [ADR-0041](decisions/ADR-0041-salamandra-r1-airfoil-family.md) |
| Printed wash-in | **+3.0°**; neutral elevon −0.04°…+0.41° at the corrected V1 mass `[D]` | [ADR-0041](decisions/ADR-0041-salamandra-r1-airfoil-family.md) |
| Material | **Conventional PETG**, light color | [ADR-0021](decisions/ADR-0021-base-material.md) |
| Perimeters / infill | 2 (0.9 mm) / **gyroid 5 %** | [ADR-0028](decisions/ADR-0028-gyroid-infill.md) |
| Section | Three cells: D-box + center + hinge | [ADR-0002](decisions/ADR-0002-closed-shell.md) |
| Carbon | Bending tube + pin. **Not torsional** | [ADR-0015](decisions/ADR-0015-carbon-non-torsional.md) |
| AUW (6S1P) | **1559.25 g CLEAN / 44.1 km/h; V1 lower model 1602.26 g / 44.7 km/h** | [ADR-0043](decisions/ADR-0043-article-1-mass-allocation.md) |
| Propulsion | **APC E 8×8, 6S1P, 500–550 Kv; two-servo O1 boundary J 0.918 / 8,484 rpm / drag ≤2.12 N** | [ADR-0042](decisions/ADR-0042-cruise-propulsion-equilibrium.md) |
| Target CG | **−93.8 mm** from root c/4 | [ADR-0040](decisions/ADR-0040-quarter-chord-sweep.md) |
| V_NE article #1 | **160 km/h** (design 180) | — |
| Initial V_limit | **105 km/h**; 150 only after GXY validation | [`docs/07`](docs/07-divergence-margin.md) |
| Avionics | INAV 9.1+ or ArduPlane · **pitot mandatory** | — |
| **Directional** | **CLEAN (finless, O1 build) / V1 (fixed fin, first variant)** | [ADR-0038](decisions/ADR-0038-fixed-fin-variant.md) |

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

**Directional variants (ADR-0038):** `SALAMANDRA-CLEAN` (finless, O1 efficiency build)
and `SALAMANDRA-V1` (fixed centreline fin, no rudder — first platform variant, I-20,
recommended for the test programme). The fin is a CORE component; panels are untouched.

⚠️ See [ADR-0032](decisions/ADR-0032-modularity.md): the panels **are not arbitrary**. Each
set is designed against a common neutral point. The same discipline applies to every new
configuration contributed to the platform.

---

## How to navigate this repository

| Folder | What it contains |
|---|---|
| [`design/`](design/) | **Salamandra Design Guide v0.21** — the authoritative v0.4.0 CAD and engineering specification, its justification, and the open points |
| [`docs/`](docs/) | Specification, status, phase plan, conventions, [master plan up to the first prototype](docs/05-master-plan.md) |
| [`decisions/`](decisions/) | **One file per decision (ADR)**: context, alternatives, consequences |
| [`research/`](research/) | **Research threads**: what was searched, what was found, what sources |
| [`gaps/`](gaps/) | Register of what we do **not** know and how it gets closed |
| [`tests/`](tests/) | Experimental program and data |
| [`calculations/`](calculations/) | Analysis scripts, with validation cases — **full reproduction guide in its README** |
| `geometry/` `stl/` `cad/` | Community 3D parts and outputs; `geometry/airfoils/` holds controlled section coordinates and `geometry/drawings/` holds generated A3 SVG design-review sheets |
| [`wiki/`](wiki/) | **The served documentation site** (Astro Starlight): onboarding guide, auto-generated indexes, search. Deployed to GitHub Pages via `.github/workflows/docs.yml` |

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
> **Corollary:** when better data overturn a conclusion, it is recorded in the [CHANGELOG](CHANGELOG.md) with a correction number.

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

**Current physical gates:** E2 measured r1 polar/stall acceptance, F2 CAD/weighed mass,
OP-29 measured torsional stiffness/elastic axis and G11 dynamic gust closure before the
speed envelope can expand beyond 105 km/h. Airfoil coordinate generation is no longer a
CAD blocker.

Phase-1 status (2026-08-17):

- **G8 (neutral point) — largely closed.** On the ADR-0040 −15° planform, NP =
  **25.72 % MAC / −75.8 mm** by the full panel VLM, cross-checked by Weissinger-L at
  **27.0 % / −72.9 mm (2.9 mm agreement)** ([I-21](research/I-21-sweep-trade-and-elastic-axis-correction.md)). The
  central-body effect remains unquantified and moves the NP forward.
- **G2 (airfoil) — closed for CAD, open for measured acceptance.** The corrected B3
  pipeline preserves the mean line, invalidates stale polar caches and uses the local
  Reynolds envelope. The released Salamandra r1 family integrates root/tip moments with
  c² weights and trims at **−0.04°…+0.41° neutral elevon** with +3.0° wash-in
  ([ADR-0041](decisions/ADR-0041-salamandra-r1-airfoil-family.md)); E2 remains mandatory.
- **ADR-0040/0043 — coupled planform, mass and balance resolved.** The −15° planform
  and target CG **−93.8 mm** remain. With Article #1 hardware and the 550 g PETG-shell
  cap and two-servo baseline, CLEAN is **1558.5 g** and the 6S1P P42A pack balances at
  approximately **−355.1 mm** in a 327 mm two-support nose boom. Current stations and acceptance gates in the
  [guide §7.2](design/Salamandra-Design-Guide-v0.1.md) and
  [justification §3.2](design/Design-Guide-Justification-v0.1.md); tools in
  `calculations/balance_cg.py` and `calculations/elevon_authority.py`.
- **Two-servo correction closes the analytical V1 mass gap.** The complete fin remains
  **43.01 g**, including its mandatory 5.7 g aluminium spar. With 25 g removed from
  actuation, V1 is **1601.5 g / 44.7 km/h**, about 18.9 g below the exact 45 km/h
  mass ceiling. CAD and scale mass verification remain mandatory.
- **OP-29 (divergence) — operationally bounded, structurally open.** Revision 4 uses
  the released r1 profile. Nominal Vdiv is 327.2 km/h, but the conservative unmeasured
  case is **129.6 km/h**; initial **Vlimit = 105 km/h**. S3 GJ,
  GXY and elastic-axis measurements plus E7 Southwell expansion are mandatory.
- **C33/G11 — load meanings fixed; dynamic gust remains open.** +6/−3 g are
  provisional manoeuvre limit loads; +9/−4.5 g are the corresponding 1.5× ultimate
  structural cases, not flight targets. The positive V-n branch gives VA **109.0 km/h
  CLEAN / 110.4 km/h V1**. A unit-checked regulatory-reference gust transfer leaves the
  linear CL range, so it is a screening flag rather than an adopted design load
  ([I-24](research/I-24-flight-load-envelope.md), [ADR-0044](decisions/ADR-0044-flight-load-envelope.md)).
- **G10 (directional stability) — bounded by calculation (I-20, ADR-0038).** The
  finless baseline is estimated **directionally unstable** (Cnβ −0.0006…−0.0014/deg
  `[E]`, FSW + nose boom); the platform now publishes two configurations:
  **SALAMANDRA-CLEAN** (finless, O1 efficiency build) and **SALAMANDRA-V1** (fixed
  centreline fin, no rudder — first platform variant, recommended for the test
  programme after F2 mass closure): S_v 2.13–2.83 dm², **43–88 g complete**, ΔCD0
  +0.0014–0.0019 `[D]`/`[E]`
  (`calculations/yaw_stability.py`). A movable rudder is **rejected with numbers**
  (I-20 §5.4; Mojito `[M]` flies a fixed stabilizer with elevons only). Closure by
  flight test **E8** (yaw perturbation).

---

## Tools and workflow

The project runs on an explicit toolchain — every tool is named, versioned, and used for
a defined job, from research to flight:

| Stage | Tool | Role |
|---|---|---|
| **Research** | Web search via **Firecrawl MCP** | Primary-source search; every query and source logged in [`research/`](research/) |
| **Analysis** | Python 3.11 + numpy | In-house panel VLM, Weissinger-L independent check, sizing, balance and screening harnesses |
| **Aerodynamics** | **XFOIL** 6.99 (official MIT build, GPL) | Airfoil polar generation for the B3 screening and the E387 calibration |
| **Input data** | UIUC Airfoil Data Site, aerodesign.de | Measured/published data (`[M]`); coordinates in `geometry/airfoils/` |
| **Design** | **Fusion 360** (connected via an MCP server) | Community parametric CAD; STL/STEP export for printing and sharing |
| **Manufacturing** | Bambu Studio · 256 mm printer (P1S class) · **PETG** | Printability is a hard requirement (O3/O4), not an afterthought |
| **Avionics** | INAV 9.1+ / ArduPlane · pitot + blackbox | Flight control and the measuring instruments of the whole test program |

Every **derived** quantitative claim is tied to a rerunnable analysis. Measured inputs
retain their source and test conditions; estimates and inferences retain their declared
assumptions and closure gates. The full guide (versions, commands, batch quirks and
validation discipline) is in [`calculations/README.md`](calculations/README.md).

The current high-value results reproduce with:

```bash
python3 calculations/verify_calculations.py        # fast cross-module contracts
python3 calculations/verify_calculations.py --all-scripts  # deterministic local suite
python3 calculations/vlm_ala_volante.py       # NP (I-07)
python3 calculations/weissinger_np.py         # C2 independent NP check (I-15 §6.3)
python3 calculations/airfoil_reflex_trade.py --xfoil /path/to/xfoil.exe  # r1 coordinates/trim
python3 calculations/propulsion_match.py      # APC E 8x8 O1 power/drag boundary
python3 calculations/mass_budget.py --config all  # Article #1 allocation and variants
python3 calculations/balance_cg.py            # coupled 6S1P station / nose-boom sizing
```

Each script ships validation cases. The system verifier also checks that geometry,
mass, battery, CG, stall, power, propulsion, stability and structural modules use the
same design contract; a modification that breaks either level is not accepted.

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
