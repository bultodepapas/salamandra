# ADR-0033 — Motor and battery out of the design

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** Decided

## Context

An open project can prescribe a closed bill of materials or leave the electronics open. The first gives reproducible results; the second gives adoption.

## Decision

**The project designs the airframe and publishes recommendations. It does not prescribe motor or battery.**

## Rationale

- **The optimal KV depends on the pack.** With 4S and 6S the motor operating point changes. Prescribing a motor would force prescribing a battery, and that breaks objective O2 (4S–6S flexibility).
- **The project's contribution is the matching, not the part.** The value of [I-03](../research/I-03-propulsion-chain.md) is the **propeller–pack–speed matching table**, not a single recommendation.
- Adoption of an open project rises when people can use what they already own.

## What the project does publish

| Output | Content |
|---|---|
| Matching table | Propeller (D×P) against pack and cruise speed, with expected J and η |
| Suggested configurations | Range / Cruise / Sport with reference motor and battery |
| Hard constraints | Bay volume, admissible mass range, current limits |
| Avionics requirements | Pitot mandatory, blackbox, GPS and magnetometer out of the current path |

## Consequences

- The mass balance is published as a **range**, not a single value.
- R-CG (bay with longitudinal adjustment) moves from desirable to **mandatory**: without it, battery freedom breaks the balance.
- Contributors' test data must declare their complete configuration to be comparable.
