# ADR-0043 — Article #1 mass allocation targets the 45 km/h stall requirement

**Status:** ✅ CLEAN and V1 analytically closed; physical F2 open · **Date:** 2026-08-18 · **Confidence:** Medium `[M]`/`[D]`/`[E]` · **Reversible:** Yes
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
| Servos | 2× Corona DS-939MG **25.0 g** | one per elevon, 12.5 g each `[M]`; 1.36× factored torque margin at 180 km/h |
| Propeller assembly | **25 g** | APC blade 15 g `[M]` + adapter/collet allowance 10 g `[E]` |
| V1a complete fin | **≤36.72 g target** | C32 current lower model: 37.31 g shell/mount + 5.70 g mandatory spar = **43.01 g**; 6.29 g gap `[E]` |

All other v0.2 rows remain unchanged. The reproducible totals are:

| Configuration | AUW | Wing loading | Predicted stall |
|---|---:|---:|---:|
| SALAMANDRA-CLEAN | **1,558.5 g** | 55.3 g/dm² | **44.1 km/h** |
| SALAMANDRA-V1 allocation target | **1,595.2 g** | 56.6 g/dm² | **44.7 km/h** |
| SALAMANDRA-V1 current lower model | **1,601.5 g** | 56.8 g/dm² | **44.7 km/h — analytical PASS** |

The formula's exact 45 km/h mass ceiling is 1,620.4 g. CLEAN carries 61.9 g of margin
and the connected V1 lower model carries about 18.9 g. C32 remains the correction that
connected the mandatory fin spar; ADR-0026 removes two unsupported baseline actuators.
The lighter component moments move the 6S1P pack to approximately x = −355.1 mm;
`balance_cg.py` solves this coupling rather than retaining the v0.2 station.

## Consequences

- OP-24 is analytically closed for CLEAN and V1. F2 CAD mass properties and the complete
  aircraft scale measurement remain mandatory; V1 is rejected above 1,620.4 g unless
  measured E2 `CLmax` supports a re-derivation.
- The released v0.2 1,685.2 g case remains in `mass_budget.py` as a regression test.
- AERO/LW-PLA remains prohibited for the flight wing until the divergence gate closes.
- The O4 Pro and heavier servos remain supported options, but not Article #1 defaults.
