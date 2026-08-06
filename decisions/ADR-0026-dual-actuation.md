# ADR-0026 — No-freeplay linkage, dual actuation per elevon

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** High · **Reversible:** Yes
**Research:** [I-18 — Servo catalog](../research/I-18-servo-catalog.md), [ADR-0025](ADR-0025-elevon-balancing.md)

## Context

The elevon (0.28 c, hinge at 0.72 c, span y = 195…585 mm = 390 mm) is the only control
surface, and its flutter mode is **inertial, not stiff** (ADR-0025). Freeplay in the
linkage couples with the servo stiffness and can feed the flutter mode; a single
actuation point on a 390 mm surface leaves the outer part elastically free.

## Decision

- **Zero-freeplay linkage**, digital servos (guide §7.5, §11).
- **Dual actuation (2 points per elevon), 4 servos total** — retained even though
  390 mm is below the ≈ 400 mm rule-of-thumb, as **flutter margin** (ADR-0025;
  dual actuation doubles K_hinge → **+41 % ω_β** `[D]`).

## Consequences

- Servo rail current: avg 1.2–2.8 A, peaks 5–9 A on simultaneous reversal `[M]` (I-18 §5)
  → FC Vx BEC ≥ 4.5 A avg + capacitance near the servos; dual-actuation balance must be
  **current-measured** (two fighting servos draw ≈ 150 mA extra each, silent).
- Servo class 12–15 g digital metal-gear (I-18) — 48–60 g in the mass budget; hinge
  moment is NOT the binding constraint (≥ 3.7× margin, `servo_torque.py`).
- The sub-400 mm dual-actuation need is to be confirmed (OP-06/C6).
