# ADR-0027 — Relative thickness 13.5 % root / 9 % tip

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** High `[M]` · **Reversible:** No
**Replaces:** ADR-0005 ("thin" airfoil)
**Data:** [02-measured-references](../docs/02-measured-references.md)

**Article #1 redesign:** `CANDIDATE-ONLY` · **Gate:** `M3/M4/M6` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## Context

The original decision (ADR-0005) asked for a **thin** airfoil, on a parasitic-drag argument. Three later analyses reversed it.

## Decision

**t/c = 13.5 % at the root, 9 % at the tip.**

## Rationale — three independent paths to the same number

**1. Divergence.** In a closed section, `J = 4A²t/s`. Since the enclosed area scales with thickness, t/c enters **linearly in the divergence speed**:

    V_div ∝ (h/c) · AR^(−3/4) · S^(−1/4) · √(G·t_wall)

Raising from 11 % to 13 % gives ×1.18 of V_div for ~30 g. It is the cheapest lever in the project.

**2. Cell housing.** The 21700 cells are 21 mm in diameter and **do not stack**. With skin, clearance and structure, ~28 mm useful are needed.

| t/c | Root thickness (c = 260 mm) | Margin over cell |
|---|---|---|
| 11 % | 28.6 mm | 6 mm — very tight |
| **13.5 %** | **35.1 mm** | **Room to spare** |

**3. Convergence with a flying article `[M]`.** Measurement on the Peregrine 840 mm:

| Station | Chord | Thickness | t/c |
|---|---|---|---|
| 0.15 | 125.6 mm | 17.0 mm | 13.5 % |
| 0.55 | 140.6 mm | 19.3 mm | 13.8 % |
| 0.90 | 160.1 mm | 21.3 mm | 13.3 % |

**An in-service printed forward-swept wing uses 13.5 %.** Three different arguments, same result.

## Consequences

- Restricts airfoil selection (gap G2) to 13–14 % thickness families.
- Penalizes C_D0 relative to a thin airfoil. Accepted: stiffness rules.
- Eases the battery bay and therefore R-CG.

## Evidence register (2026-08-05 — does not reopen the decision)

The airfoil evidence campaign (I-15) located the aerodynamic review material for the
13.5 % root, to be used at B3 time when the section is **designed** (no published
reflexed section reaches 13.5 %, I-11):

- **NASA-CR-4096 / AIAA 87-1268** — Barnett & Carter: as thickness increases, the flow
  evolves from local to massive separation — the stall-character risk of the root.
- **NACA-SR-83** — Jacobs (1938): the classic thickness-vs-profile-drag evidence.
- **NACA-RM-L8L08** — Loftin & Smith: 34 sections at Re 3–9×10⁶ (high-Re reference).

These support the divergence/cell arguments above (they do not contradict them) and
define the aerodynamic constraints the designed root section must meet (stall
character, drag, C_Lmax ≥ 0.65). Full campaign: `research/I-15-airfoil-evidence-campaign.md`.

## Review conditions

None foreseen. It is one of the best-supported decisions in the project.
