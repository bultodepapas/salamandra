# ADR-0035 — TPU-printed elevon hinges

**Status:** 🔄 Provisional · **Date:** 2026-07-28 · **Confidence:** Medium · **Reversible:** Yes
**Research:** [I-09 — Flightory practice](../research/I-09-flightory-inspiration.md), [ADR-0025](ADR-0025-elevon-balancing.md)

## Context

The elevon hinge line at x/c = 0.72 (ADR-0002) is a structural joint of the control
surface: its stiffness K_hinge enters the flutter frequency ω_β, and the elevon flutter
mode is inertial (ADR-0025). Two hinge technologies are available: TPU-printed hinges
(glued or live-hinge, project pattern) and polyester (mylar) tape hinges 25×30 mm glued
in slots — flight-proven on 900–1340 mm printed FPV aircraft (Pico Talon, Stallion;
I-09).

## Decision

- **TPU-printed hinges as the baseline** (guide §7.5) — ADR-0035.
- **Mylar tape hinges as the documented alternative**: acceptable if TPU results
  disappoint; stiffness to be characterized in both cases (OP-10).

## Consequences

- K_hinge is uncharacterized for both technologies (can be off by a factor 3) — it is
  the input of the flutter analysis (C7/S6, G7) and the mass balance (ADR-0025: hinge
  mass sits forward of the hinge line).
- The hinge decision is reversible at build time without changing the geometry (both
  mount at 0.72 c).
