# ADR-0043 — Article #1 mass allocation targets the 45 km/h stall requirement

**Status:** ✅ CLEAN and V1 analytically closed; physical F2 open · **Date:** 2026-08-18 · **Confidence:** Medium `[M]`/`[D]`/`[E]` · **Reversible:** Yes
**Research:** I-16…I-19, I-22/I-23, I-27 · **Verification:** F2 CAD mass properties and weighed assembly

> **2026-08-18 amendment — ADR-0045:** the selected 35–90 % half-span elevons
> reduce moving PETG by 5 g and balance mass by 6 g while retaining the 550 g total
> shell cap. Current connected totals and torque margin below supersede the original
> figures preserved in repository history.

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
| FPV | DJI O4 Air Unit **8.95 g installed** | E18 camera 3.10 g + E19 VTX/attached-antenna assembly 5.85 g `[M]`/`[D]`; I-19 |
| Servos | 2× Corona DS-939MG **25.0 g** | one per elevon, 12.5 g each `[M]`; 1.52× factored torque margin at 180 km/h |
| Propeller assembly | **25 g** | APC blade 15 g `[M]` + adapter/collet allowance 10 g `[E]` |
| V1a complete fin | **≤36.72 g target** | Current vertical-TE lower model: 36.85 g shell/mount + 5.70 g mandatory spar = **42.55 g**; 5.83 g gap, corrected carrier mass still open `[E]` |

All other v0.2 rows remain unchanged. The reproducible totals are:

| Configuration | AUW | Wing loading | Predicted stall |
|---|---:|---:|---:|
| SALAMANDRA-CLEAN | **1,553.25 g** | 55.1 g/dm² | **44.1 km/h** |
| SALAMANDRA-V1 allocation target | **1,589.97 g** | 56.4 g/dm² | **44.6 km/h** |
| SALAMANDRA-V1 current lower model | **1,596.26 g** | 56.6 g/dm² | **44.7 km/h — analytical PASS** |

The formula's exact 45 km/h mass ceiling is 1,620.4 g. CLEAN carries 67.2 g of margin
and the connected V1 lower model carries about 24.1 g. C32 remains the correction that
connected the mandatory fin spar; ADR-0026 removes two unsupported baseline actuators.
The aggregate ledger gives x = −353.7 mm; the component-level layout that controls the
drawing solves x = −337.74 mm after placing E18/E19 explicitly. Both calculations expose
their assumptions instead of retaining the v0.2 station.

## Consequences

- OP-24 is analytically closed for CLEAN and V1. F2 CAD mass properties and the complete
  aircraft scale measurement remain mandatory; V1 is rejected above 1,620.4 g unless
  measured E2 `CLmax` supports a re-derivation.
- The released v0.2 1,685.2 g case remains in `mass_budget.py` as a regression test.
- AERO/LW-PLA remains prohibited for the flight wing until the divergence gate closes.
- The O4 Pro and heavier servos remain supported options, but not Article #1 defaults.
