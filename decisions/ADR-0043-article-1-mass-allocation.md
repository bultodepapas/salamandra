# ADR-0043 — Article #1 mass allocation targets the 45 km/h stall requirement

**Status:** ⚠️ CLEAN closed; V1 allocation reopened by C32 · **Date:** 2026-08-17 · **Confidence:** Medium `[M]`/`[D]`/`[E]` · **Reversible:** Yes
**Research:** I-16…I-19, I-22/I-23 · **Verification:** F2 CAD mass properties and weighed assembly

## Context

The released v0.2 estimate was 1,685.2 g and predicted 45.9 km/h stall, missing C16.
It also budgeted 40 g for the APC 8×8 propeller assembly although APC publishes a
15 g blade mass, and it did not select the lighter already-catalogued electronics.
Switching the wing to LW-PLA saves mass but fails the current conservative divergence
model, so it is not an acceptable closure.

## Decision

Keep conventional PETG and make the following masses binding CAD/procurement limits:

| Item | Article #1 allocation | Basis |
|---|---:|---|
| PETG shell, excluding V1 fin | **≤ 550 g** | low end of established 550–650 g estimate `[E]`; CAD acceptance cap |
| FC/PDB | SpeedyBee F405 WING **20.3 g** | 8.9 g FC + mandatory 11.4 g PDB/current board `[M]`; wireless board omitted |
| FPV | DJI O4 Lite **8.2 g** | `[M]` I-19 |
| Servos | 4× Corona DS-939MG **50.0 g** | 12.5 g each `[M]`; torque is non-binding |
| Propeller assembly | **25 g** | APC blade 15 g `[M]` + adapter/collet allowance 10 g `[E]` |
| V1a complete fin | **≤36.72 g target** | C32 current lower model: 37.31 g shell/mount + 5.70 g mandatory spar = **43.01 g**; 6.29 g gap `[E]` |

All other v0.2 rows remain unchanged. The reproducible totals are:

| Configuration | AUW | Wing loading | Predicted stall |
|---|---:|---:|---:|
| SALAMANDRA-CLEAN | **1,583.5 g** | 56.2 g/dm² | **44.5 km/h** |
| SALAMANDRA-V1 allocation target | **1,620.2 g** | 57.5 g/dm² | **45.0 km/h** |
| SALAMANDRA-V1 current lower model | **1,626.5 g** | 57.7 g/dm² | **45.1 km/h — FAIL** |

The formula's exact 45 km/h mass ceiling is 1,620.4 g. CLEAN therefore carries 36.9 g
of allocation margin. C32 found that the original V1 row omitted its mandatory spar;
the current lower model exceeds the ceiling by about 6.1 g. The lighter component
moments move the 6S1P pack to x = −359.6 mm and shorten the boom assembly to 37.4 g;
`balance_cg.py` solves this coupling rather than retaining the v0.2 station.

## Consequences

- OP-24 closes for CLEAN but reopens for V1. F2 must remove or compensate at least
  6.3 g relative to the current lower assembly model; otherwise V1 is rejected or must
  be re-derived against measured E2 `CLmax`.
- The released v0.2 1,685.2 g case remains in `mass_budget.py` as a regression test.
- AERO/LW-PLA remains prohibited for the flight wing until the divergence gate closes.
- The O4 Pro and heavier servos remain supported options, but not Article #1 defaults.
