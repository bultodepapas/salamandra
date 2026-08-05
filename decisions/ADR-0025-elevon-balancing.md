# ADR-0025 — Elevon mass balancing

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** High · **Reversible:** No
**Gaps:** G7 · **Research:** [I-05](../research/I-05-divergence-flutter.md)

## Context

Preliminary flutter analysis `[E]`:

| Mode | Estimated frequency |
|---|---|
| Bending ω_h | ~25 Hz |
| Torsion ω_α | ~106 Hz |
| **Elevon ω_β** | **~82 Hz** |

**ω_h/ω_α = 0.23** — widely separated modes: classic bending-torsion flutter **is not critical**.

**ω_β/ω_α = 0.77** — inside the coupling band.

## The finding that forces the decision

**The frequency separation is not achievable by stiffness.** No value of GJ solves the problem: if it drops, ω_α crosses below ω_β; if it rises, it crosses above. **It is an inertial problem, not a stiffness one.**

## Decision

**Elevon mass balancing, with the surface CG on the hinge line. Non-negotiable.**

Budget: ~60 g in total (~3.5 % of the AUW).

## Rationale

With the elevon CG on the hinge, the inertial coupling disappears and the mode stops being fed. It is the standard solution and attacks the dominant mechanism instead of going around it.

A 25 g elevon with its CG ~24 mm behind the hinge → moment 0.60 g·m. With a 20 mm forward compensation horn: **m_b ≈ 30 g per elevon**.

## Concurrent mandatory measures

- **Zero freeplay in the linkage** (ADR-0026). Freeplay is a nonlinearity that triggers a limit cycle **below** the linear critical speed. It is the number-one cause of flutter in models.
- **Dual actuation point** if the elevon exceeds ~400 mm: doubles K_hinge and raises ω_β by 41 %.
- Digital servos with high holding stiffness. Static torque matters less than stiffness.

## Raised to non-negotiable

After cancelling the carbon veil ([ADR-0022](ADR-0022-carbon-veil-cancelled.md)), ω_α drops and the margin narrows. What was prudence became a requirement.

## Declared uncertainty

⚠️ **K_hinge is an estimate that can be off by a factor 3**, and ω_β scales with its root. In addition, printed TPU hinges (ADR-0035) add poorly characterized stiffness. **Characterizing it is a Phase 1 task.**

It closes with **E5** — FFT of blackbox gyro traces.
