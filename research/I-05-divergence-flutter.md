# I-05 — Aeroelastic divergence and flutter

**Status:** **Open** · **Feeds:** ADR-0002, ADR-0025, ADR-0028 · **Gaps:** G4, G6, G7

It is the **project's dominant risk**. No other research thread reorders so many priorities.

## Mechanism

In forward sweep the aerodynamic center lies **ahead of** the torsional stiffness center. The load produces nose-up twist → more angle of attack → more lift → more twist. **Positive feedback up to structural failure** `[M]`.

Known remedies: increase stiffness (mass penalty) or **aeroelastic tailoring of the layup** (the X-29 solution) `[M]`.

## Formulation

Thin-wall closed section (Bredt-Batho):

    J = 4·A²·t / s

Uniform wing divergence:

    q_D = π²·GJ / (4·L²·c·e·a)

With e ∝ c and AR = b²/S, the scaling law results:

    V_div ∝ (h/c) · AR^(−3/4) · S^(−1/4) · √(G·t_wall)

**Relative thickness enters linearly. It is the most powerful lever available** → [ADR-0027](../decisions/ADR-0027-relative-thickness.md).

### Constant-wall scaling law

With `t` fixed (same nozzle, same perimeters) and geometrically similar shape of factor λ:

    GJ ∝ λ³ ,  q_D ∝ 1/λ ,  **V_div ∝ λ^(−1/2)**

A larger wing printed with the same wall is **inherently worse**. Explains why an 840 mm design does not transfer to 1300 mm without correction.

## The error that ran in the opposite direction

The original specification said **infill 0 %**, inherited from LW-PLA vase-mode practice.

**Bredt-Batho assumes the skin does not buckle.** A 0.4–0.9 mm skin over an unsupported span of 100 mm or more, under shear, **buckles locally well below the material limit**, and once it buckles the effective GJ **collapses**.

> **Correction C12.** Without infill, the GJ calculation was **overestimated, not underestimated**.

The 4–5 % gyroid **does not add direct torsion** — it sits near the shear center — but **stabilizes the skin** so the closed cell works → [ADR-0028](../decisions/ADR-0028-gyroid-infill.md).

## Anchoring to an in-service article

The **Peregrine 840 mm** is a flying printed forward-swept flying wing. See [measured data](../docs/02-measured-references.md).

| | Peregrine | Project | Ratio |
|---|---|---|---|
| Reference chord | ~180 mm | 260 mm | 1.44 |
| Half-span | 420 mm | 650 mm | 1.55 |
| Wall | 0.42 mm (1 perimeter) | 0.90 mm (2) | 2.14 |
| t/c | 13.5 % `[M]` | 13.5 % | 1.00 |
| **GJ** (∝ c³·t) | — | — | **6.45×** |
| **V_div** | — | — | **1.14×** |

**The project design is 14 % better in divergence speed than the reference, despite being 55 % larger.**

⚠️ This **anchors** the comparison in measured geometry. **It does not give the absolute value.**

> **Correction C13.** Calibrating the model against the Peregrine was proposed (test E6). **Withdrawn:** the Peregrine is at a factor ~3 from the prediction. A test that passes with that margin **does not falsify the model but does not validate it either**.

> **Correction C15.** It was claimed that a single perimeter fails the criterion. **Falsified by flying hardware.**

> **Correction C14.** The risk was overestimated and communicated with more certainty than `[E]` ±35 % data supported.

## Flutter — preliminary analysis `[E]`

| Mode | Frequency |
|---|---|
| Bending ω_h | ~25 Hz |
| Torsion ω_α | ~106 Hz |
| **Elevon ω_β** | **~82 Hz** |

- **ω_h/ω_α = 0.23** — widely separated modes: **classic bending-torsion flutter is not critical.**
- **ω_β/ω_α = 0.77** — inside the coupling band.

**Key finding: the separation is not achievable by stiffness.** No value of GJ solves the problem; if it drops, ω_α crosses below, if it rises, it crosses above. **It is inertial** → [ADR-0025](../decisions/ADR-0025-elevon-balancing.md).

⚠️ K_hinge is an estimate that can be off by a factor 3, and ω_β scales with its root. TPU hinges add poorly characterized stiffness.

## How it closes: E7, Southwell plot

As divergence is approached the elastic twist amplifies as **1/(1 − q/q_D)**: the elevon deflection needed to compensate **shoots up hyperbolically well before reaching it**.

**Method:**
1. Stabilized Cruise flight at 90, 110, 130 and 150 km/h.
2. From the blackbox: elevon trim deflection against pitot dynamic pressure.
3. **Plot 1/Δtrim against q: it gives a straight line that intercepts the axis at q_D.**

A standard technique for extrapolating the critical speed **without ever reaching it**. It turns G6 from a literature gap into a measurement on the first afternoon of flight.

⚠️ **Identified threat (G9):** the Peregrine documentation reports *porpoising* in INAV's RTH / Cruise / Loiter modes. **If the aircraft oscillates in altitude, the trim-against-q data are noise and Southwell does not come out.** The altitude loop must be stabilized before attempting E7.

## Thread state

**Open.** It closes when E7 gives a measured q_D.
