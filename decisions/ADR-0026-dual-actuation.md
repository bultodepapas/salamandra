# ADR-0026 — No-freeplay linkage, one actuator per elevon

**Status:** ✅ Active · **Date:** 2026-08-18 · **Confidence:** Medium · **Reversible:** Yes
**Research:** [I-18 — Servo catalog](../research/I-18-servo-catalog.md), [ADR-0025](ADR-0025-elevon-balancing.md)

## Context

Each selected 0.28 c elevon spans y = 227.5…585 mm (357.5 mm; ADR-0045). The former baseline used two
actuators per elevon as an assumed flutter-stiffness margin even though the surface is
below the project's approximate 400 mm rule of thumb. That assumption had no measured
servo/linkage stiffness, elevon bending model or modal test. The claimed +41 % frequency
change was only `sqrt(2)` after assuming that a second actuator doubled effective hinge
stiffness.

The corrected hinge-moment calculation gives 0.876 kgf·cm ideal demand for one complete
elevon at 180 km/h. With a 1.5 torque factor and 0.80 linkage efficiency, one actuator
requires 1.643 kgf·cm `[D]`/`[E]`. The Article #1 Corona DS-939MG provides 2.5 kgf·cm
at 4.8 V `[M]`: 1.52× factored margin at 180 km/h and about 4.5× at the initial
105 km/h limit `[D]`.

## Decision

- **One digital metal-gear servo per elevon, two servos total.**
- Nominal span station **y = ±406.25 mm**, the midpoint of each elevon `[D]`; chordwise
  and vertical placement remain the section-fit/linkage solution `[D]`/`[E]`.
- Zero-freeplay linkage, high holding stiffness and hinge-line mass balance remain mandatory.
- Four-servo actuation may return only as a separately analysed variant after measured
  stiffness, freeplay and modal evidence demonstrate a necessary benefit.

## Consequences

- Servo mass falls from 50.0 to **25.0 g**. With the ADR-0045 balance update, CLEAN AUW
  is **1553.25 g** and the current V1 lower model is **1595.80 g** `[D]`.
- V1 remains about 24.1 g below the exact 45 km/h mass ceiling; CAD mass and measured
  E2 `CLmax` remain release gates.
- Two actuators remove inter-servo fighting on a shared surface and halve the linkage,
  connector and actuator counts.
- DS-939MG margin at 180 km/h remains modest. Procurement must verify torque, backlash,
  holding stiffness and current; expansion beyond 105 km/h still requires G7 testing.

## Verification

- `python calculations/servo_torque.py`
- `python calculations/mass_budget.py --config all`
- Static stiffness/freeplay bench test, E5 blackbox FFT and progressive envelope expansion.
