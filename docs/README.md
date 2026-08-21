# Documents

This is an **open, community-driven, modular 3D-printed FPV aircraft platform**. The core
design principles are developed largely through **AI-assisted research**, while the final
aircraft and its 3D models are created collaboratively by humans and AI. The files here
define the reference design and the platform's conventions. See the
[README](../README.md) for the full positioning and the licence.

| File | Content |
|---|---|
| [`00-objectives-and-requirements.md`](00-objectives-and-requirements.md) | **Inherited v0.6 specification.** Reopened for Master Plan Gate M0 reissue |
| [`02-measured-references.md`](02-measured-references.md) | Primary `[M]` data measured by the project |
| [`03-phase-1-plan.md`](03-phase-1-plan.md) | Historical v0.6 geometry/stability workstream; superseded for programme sequence |
| [`04-conventions.md`](04-conventions.md) | Tags, identifiers, symbols, signs |
| [`05-master-plan.md`](05-master-plan.md) | **Canonical Master Design Plan.** Mission → hardware → mass skeleton → equal-requirements architecture trade → evidence → human CAD → prototype |
| [`06-material-mass-variants.md`](06-material-mass-variants.md) | **Mass budget tool and results** — PETG / AERO-PLA wings / PLA+ policies, per-part materials, battery/FC/FPV options (`calculations/mass_budget.py`) |
| [`07-divergence-margin.md`](07-divergence-margin.md) | **Absolute divergence speed (G6, rev. 4)** — released r1 section and elastic-axis uncertainty at −15°: nominal 327.2 km/h, conservative 129.6 (**FAIL**), AERO 91.6; combined GXY+gyroid+1.1 mm wall 207; released initial **V_limit 105 km/h**, 150 only after S3 validates GXY (`calculations/divergence.py`) |
| [`08-release-v0.1.md`](08-release-v0.1.md) | **First release (tag v0.1.0)** — the design package (CAD baseline): contents, verification status, frozen vs open items, binding constraints |
| [`09-release-v0.2.md`](09-release-v0.2.md) | **Historical release (tag v0.2.0)** — safety-corrected −15° CAD baseline and audit record |
| [`10-release-v0.3.md`](10-release-v0.3.md) | **Historical release (tag v0.3.0)** — Salamandra r1 coordinates and Article #1 allocation; its post-release corrections are packaged by v0.4.0 |
| [`11-release-v0.4.md`](11-release-v0.4.md) | **Historical release (tag v0.4.0)** — connected calculation baseline and Article #1 manoeuvre/ultimate-load envelope |
| [`12-calculation-system-audit-and-remediation.md`](12-calculation-system-audit-and-remediation.md) | **Calculation-system audit `[M]`** — the measured findings (S1–S5) and the WP1–WP6 remediation programme that drove corrections C39–C43 |
| [`13-release-v0.5.md`](13-release-v0.5.md) | **Historical release (tag v0.5.0)** — single-declaration design contract ([ADR-0046](../decisions/ADR-0046-single-declaration-contract.md)), verification proven falsifiable, released elevon geometry and drawing set; E2/F2/S3/G7/G10/G11 remain open |
| [`16-release-v0.6.md`](16-release-v0.6.md) | **Current release (tag v0.6.0)** — twin-fin directional architecture ([ADR-0038](../decisions/ADR-0038-fixed-fin-variant.md), I-29/I-30) and the parametric fuselage programme (I-28 Revision 3); the OML remains `[I]` review geometry with `aircraft_feasible: false`; E2/F2/S3/G7/G10/G11 remain open |
| [`15-how-to-publish-a-release.md`](15-how-to-publish-a-release.md) | **Maintainer release procedure** — scope freeze, version ownership, release document, CI-equivalent gates, PR, annotated tag and post-release checks |
| `first_investigation.md` | Rev. 1.0, initial research *(add manually)* |

**Decisions** live in [`../decisions/`](../decisions/), the **why** in [`../research/`](../research/), what we do **not know** in [`../gaps/`](../gaps/).

The history lives in [`../CHANGELOG.md`](../CHANGELOG.md) and in the git log.
