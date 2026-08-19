# ADR-0043 — Article #1 mass allocation targets the 45 km/h stall requirement

**Status:** ✅ CLEAN and V1 analytically closed; physical F2 open · **Date:** 2026-08-18 · **Confidence:** Medium `[M]`/`[D]`/`[E]` · **Reversible:** Yes
**Research:** I-16…I-19, I-22/I-23, I-27, I-29 · **Verification:** F2 CAD mass properties and weighed assembly

> **2026-08-18 amendment — ADR-0045:** the selected 35–90 % half-span elevons
> reduce moving PETG by 5 g and balance mass by 6 g while retaining the 550 g total
> shell cap. Current connected totals and torque margin below supersede the original
> figures preserved in repository history.

> **2026-08-19 amendment — ADR-0038/I-29:** the invalid centreline-fin carrier is
> replaced by two fins on aft CORE booms. The 60.00 g complete-assembly allocation and
> connected totals below supersede the former 36.72 g fin-only target.

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
| V1a complete twin-fin/boom assembly | **≤60.00 g** | Current lower model: 41.25 g two shells/mounts + 7.85 g two LE spars + 10.88 g two aft booms = **59.97 g**; 0.03 g allocation margin `[E]` |

All other v0.2 rows remain unchanged. The reproducible totals are:

| Configuration | AUW | Wing loading | Predicted stall |
|---|---:|---:|---:|
| SALAMANDRA-CLEAN | **1,553.25 g** | 55.1 g/dm² | **44.1 km/h** |
| SALAMANDRA-V1 allocation target | **1,613.25 g** | 57.2 g/dm² | **44.9 km/h** |
| SALAMANDRA-V1 fin-only lower model | **1,613.22 g** | 57.2 g/dm² | **44.9 km/h — intermediate only** |
| SALAMANDRA-V1 coupled packaging result | **1,615.63 g** | 57.3 g/dm² | **44.93 km/h — analytical PASS** |

The formula's exact 45 km/h mass ceiling is 1,620.4 g. CLEAN carries 67.2 g of margin
and the connected V1 lower model carries only about 7.9 g. C32 remains the correction that
connected mandatory fin structure; I-29 additionally connects both aft booms.
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
