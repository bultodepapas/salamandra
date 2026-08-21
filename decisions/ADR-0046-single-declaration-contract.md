# ADR-0046 — One declaration site per physical quantity, enforced by lint and mutation

**Status:** ✅ Active — architectural rule for `calculations/`  
**Date:** 2026-08-18  
**Confidence:** High `[M]` — every claim below is measured by executing this repository  
**Reversible:** Yes, but reverting reopens the defect class it closes  
**Related gaps:** G8, G10, G11 (all three were mis-served by duplicated declarations)  
**Supporting research:** [`docs/12-calculation-system-audit-and-remediation.md`](../docs/12-calculation-system-audit-and-remediation.md), [I-23](../research/I-23-calculation-system-integration-audit.md)

**Article #1 redesign:** `RETAINED` · **Gate:** `All` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## Context

The `calculations/` tree grew to 33 modules with a clean acyclic import graph, and still
carried **twelve** physical quantities declared in two or more places. The audit measured
the consequences rather than asserting them:

- the published neutral point that sets the CG target was a **hand-copied literal**
  (`NP_VLM = -75.8e-3`) that no check compared against the solver that produced it — so a
  change to span, area, taper or sweep would have moved the real neutral point and left
  the target untouched (C39);
- two modules held the same yaw inertia with a factor **1.76** between them, and the
  harness accepted both in the same run (C40);
- one speed name, `V_NE`, meant 160 km/h in `divergence.py` and 180 km/h in
  `yaw_stability.py` (C41);
- drag was computed three incompatible ways, one of them the single lumped coefficient
  that [ADR-0009](ADR-0009-drag-decomposition.md) forbids and that already caused C1 (C42).

This is failure mode #3 — *failing to re-derive downstream* — written into the source of
the project's most consequential numbers. The project's own rule existed in prose in
`CLAUDE.md`; nothing executed it.

A second, compounding finding: several validation checks **could not fail**. Two literals
were compared to each other; one assertion reduced algebraically to `abs(STATIC_MARGIN -
0.08)`; one demanded that a problem still exist (C43). A duplicate-declaration rule is
worth nothing if the suite guarding it is a tautology.

## Alternatives considered

| Option | For | Against | Disposition |
|---|---|---|---|
| Keep the prose rule in `CLAUDE.md` | Zero tooling | It is the state that produced C39–C42; unexecuted prose caught nothing in four releases | Rejected |
| Human review checklist at release | Cheap | Reviewers cannot diff twelve constants across 33 modules reliably; the audit found them only by executing the code | Rejected |
| One god-module holding every constant | Simple to lint | Collapses *chosen inputs* and *derived results* into one namespace; a derived quantity would become editable as if it were an input | Rejected |
| **Layered ownership + executable lint + mutation proof** | Each quantity has one owner and one derivation; the lint fails a PR; the mutation test proves the lint can fail | Costs a lint pass and ~110 s of mutation runtime | **Selected** |

## Decision

**A physical quantity is declared exactly once.** A module may *compute* it or *import*
it; it may never *declare* one that another module also declares. Ownership is layered:

| Owner | Owns |
|---|---|
| `design_config.py` | Chosen design inputs — geometry, masses, the speed ladder, load factors, material properties |
| `aero_contract.py` | Derived aerodynamics — the neutral point (re-derived and cached), the CG target, lift slope, canonical mesh constants |
| `drag_model.py` | The polar, returned as **separate viscous and induced terms**, per ADR-0009 |

Enforcement is executable, not editorial:

- `calculations/contract_lint.py` fails when any quantity is declared twice, and when a
  banded constant is frozen as a default argument;
- `calculations/mutation_test.py` seeds **19** deliberate defects — sign flips, dropped
  normalisations, desynchronised copies — and requires each to turn at least one check
  red;
- `.github/workflows/calculations.yml` runs the contracts, every deterministic script, the
  lint and the mutation test on a Python × numpy matrix, as a required check.

The published literals survive only as **regression anchors with a declared tolerance**
(neutral point ±0.5 mm), never as the source of the value.

## Rationale

The rule is justified by what it catches, measured on this repository:

- Re-derivation reproduces the published pair — VLM **−75.79 mm**, Weissinger-L
  **−72.90 mm** `[D]` — so adopting it cost no engineering change while removing the
  drift path. The CG target moved **0.017 mm** and the battery station **0.04 mm** against
  a ±5 mm tolerance.
- The mesh study behind those numbers is now published rather than implied: the VLM
  neutral point runs −76.895 mm (12×3) → −75.482 mm (120×14), Richardson limit ≈ −75.43
  mm; Weissinger runs −73.966 mm (ny=20) → −72.718 mm (ny=300), limit ≈ −72.65 mm `[D]`.
  The former literals therefore carried ≈ 0.36 mm and ≈ 0.25 mm of undeclared
  discretisation error, quoted to 0.1 mm on a 2.9 mm method spread — failure mode #2.
- Reconciling the yaw inertia in favour of the traceable `[D]` derivation
  (0.1587 kg·m² from the 3-D mass model, not 0.28 `[E]`) moved a **published** result: the
  V1a reduced 2-DOF pair goes from λ = −0.794 ± 3.948j to **λ = −1.233 ± 5.205j**
  (ω_n 5.35 rad/s, ζ 0.231) `[D]`. The conclusion is unchanged and slightly strengthened.
- Three of the 19 seeded defects **survived the first mutation run**. They were real holes
  in the verification, not test-suite noise, and each is now caught. That is the evidence
  that the enforcement discriminates.

The cost is bounded and measured: the full cross-module suite runs in **36.5 s** (112
contracts, 28 deterministic CLIs) and the mutation suite in **108 s** `[M]`.

## Consequences

**Closes.** The duplicate-declaration class, the unexecuted-CI class (C38) and the
tautological-check class (C43). A desynchronising change is now blocked by CI rather than
found by audit four releases later.

**Requires downstream.**

- Any new module must import shared quantities from their owner. Adding a second
  declaration fails `contract_lint.py`.
- Any new check must be accompanied by the question *what result would make this fail?*
  A check that no seeded defect can turn red is a hole, not a pass.
- A banded quantity must be a parameter, never a module constant bound as a default
  argument — defaults are evaluated once at definition time, so a sensitivity sweep
  written the obvious way silently returns the unmutated answer.
- Adding a quantity to `design_config.py` obliges declaring its confidence tag and, when
  banded, propagating the band to every consumer.

**Opens.** The mutation catalogue is a floor, not a proof of completeness: 19 defects are
caught, and the population of possible defects is unbounded. Growing the catalogue when a
new class of error is found is part of the rule.

## Review conditions

Reconsider this decision if:

- the lint blocks a legitimate physical distinction — two quantities that share a name but
  are genuinely different — in which case the fix is to name them apart, not to relax the
  rule (this is exactly how `V_ARTICLE_NE` and `V_STRUCTURAL` were separated);
- the mutation suite runtime stops contributors running it before pushing, in which case
  it moves to CI-only with a fast subset locally — measured, not assumed;
- a measured `[M]` value ever contradicts a derived quantity, in which case the derivation
  yields to the measurement and the anchor becomes the measured value with its own band.
