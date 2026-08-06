# Documents

This is an **open, community-driven, modular 3D-printed FPV aircraft platform**. The core
design principles are developed largely through **AI-assisted research**, while the final
aircraft and its 3D models are created collaboratively by humans and AI. The files here
define the reference design and the platform's conventions. See the
[README](../README.md) for the full positioning and the licence.

| File | Content |
|---|---|
| [`00-objectives-and-requirements.md`](00-objectives-and-requirements.md) | **Specification (Phase 0).** Objectives, requirements, non-goals |
| [`02-measured-references.md`](02-measured-references.md) | Primary `[M]` data measured by the project |
| [`03-phase-1-plan.md`](03-phase-1-plan.md) | Phase 1 execution plan |
| [`04-conventions.md`](04-conventions.md) | Tags, identifiers, symbols, signs |
| [`05-master-plan.md`](05-master-plan.md) | Roadmap F1→F6 to the first prototype, integrating the CAD flow |
| [`06-material-mass-variants.md`](06-material-mass-variants.md) | **Mass budget tool and results** — PETG / AERO-PLA wings / PLA+ policies, per-part materials, battery/FC/FPV options (`calculations/mass_budget.py`) |
| [`07-divergence-margin.md`](07-divergence-margin.md) | **Absolute divergence speed (G6, rev. 2)** — nominal 275.6 km/h (1.15×, barely PASS), conservative end 151.5 km/h (0.63×, **FAIL — below V_NE 160**): the ADR-0030 "criterion met" claim is falsified; real-print sensitivity (G_XY in-plane 0.69–0.72 GPa → 210.5 km/h; combined best 242); AERO 107.1 km/h not airworthy; **V_limit 110 km/h** until S3/I-12/E7 (`calculations/divergence.py`, 14 validations) |
| [`08-release-v0.1.md`](08-release-v0.1.md) | **First release (tag v0.1.0)** — the design package (CAD baseline): contents, verification status, frozen vs open items, binding constraints |
| `first_investigation.md` | Rev. 1.0, initial research *(add manually)* |

**Decisions** live in [`../decisions/`](../decisions/), the **why** in [`../research/`](../research/), what we do **not know** in [`../gaps/`](../gaps/).

The history lives in [`../CHANGELOG.md`](../CHANGELOG.md) and in the git log.
