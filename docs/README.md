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
| [`07-divergence-margin.md`](07-divergence-margin.md) | **Absolute divergence speed (G6, rev. 3)** — corrected elastic-axis uncertainty at −15°: nominal 325.3 km/h, conservative 128.8 (**FAIL**), AERO 91.1; combined GXY+gyroid+1.1 mm wall 206; initial **V_limit 105 km/h**, 150 only after S3 validates GXY (`calculations/divergence.py`) |
| [`08-release-v0.1.md`](08-release-v0.1.md) | **First release (tag v0.1.0)** — the design package (CAD baseline): contents, verification status, frozen vs open items, binding constraints |
| `first_investigation.md` | Rev. 1.0, initial research *(add manually)* |

**Decisions** live in [`../decisions/`](../decisions/), the **why** in [`../research/`](../research/), what we do **not know** in [`../gaps/`](../gaps/).

The history lives in [`../CHANGELOG.md`](../CHANGELOG.md) and in the git log.
