# ADR-0012 — Light color mandatory

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** High · **Reversible:** Yes
**Research:** [I-04 — Printing materials](../research/I-04-printing-materials.md), [ADR-0021](ADR-0021-base-material.md)

## Context

The primary structure is PETG (ADR-0021). A wing lives outdoors, on the ground and in the
sun for most of its life. Dark colors absorb solar radiation and raise part temperature;
PETG's thermal margin (HDT ≈ 70 °C) is its selling point, and absorbed solar load would
erode exactly that margin on the hottest days. Color is also the cheapest way to reduce
UV degradation of the surface.

## Decision

**Light color mandatory** for the printed parts (guide §7.4; renders: light gray).

## Consequences

- Reduces solar load and surface temperature growth on the ground and in the air.
- Part of the PETG acceptance argument of ADR-0021 (thermal margin preserved).
- Purely cosmetic dark accents (e.g. the FPV camera cowl) are allowed; structural parts
  stay light.
