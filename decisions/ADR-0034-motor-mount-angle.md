# ADR-0034 — Motor mount angle as a design parameter

**Status:** 🔄 Provisional · **Date:** 2026-07-28 · **Confidence:** Medium · **Reversible:** Yes
**Research:** [docs/02 — Peregrine measured references](../docs/02-measured-references.md) (`[M]`)

## Context

The thrust line geometry couples power with pitch: a misaligned thrust line adds a
pitching moment that changes with throttle, contaminating trim and the E2/E7
measurements. The only in-service datum of this configuration class is the Peregrine
datasheet: **motor mount tilt 0.8° up** `[M]` (docs/02 §1.1).

## Decision

- **Motor mount angle is a design parameter** (not a fixed value), provisionally
  **0.8° upthrust** (guide §10.2) — Peregrine precedent `[M]`.
- Thrust line through the CG plane (z = 0) to minimize pitch coupling with throttle.

## Consequences

- The angle is adjustable at the mount; final value set at trimming (OP-15, first
  flights, E7). Any change to the mount angle must be re-checked against the CG band
  (guide §8.2) — the thrust line passes through the CG plane by construction.
