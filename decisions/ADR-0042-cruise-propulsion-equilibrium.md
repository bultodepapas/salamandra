# ADR-0042 — Cruise propulsion is bounded by total power and closed by measured drag

**Status:** ✅ Active · **Date:** 2026-08-17 · **Confidence:** Medium `[D]`/`[E]` · **Reversible:** Yes
**Research:** I-03, I-22 · **Verification:** D2 bench map, E3 flight energy

> **Correction C29 (2026-08-17):** the original ADR called the O1 power-limited
> propeller point an aircraft equilibrium and assigned the complete 109.25 W battery
> budget to the motor. That was incorrect: equilibrium additionally requires E2
> aircraft drag, and the avionics/FPV/BEC battery load must be reserved first.

## Context

ADR-0007 correctly selected the APC Thin Electric 8×8 from measured UIUC data, but the
v0.2 guide incorrectly prescribed its maximum-efficiency advance ratio as the cruise
operating point. At 95 km/h that point demands about 230 W electrical and 5.46 N thrust,
so it cannot simultaneously represent the O1 ceiling of 1.15 Wh/km. Propeller efficiency
alone does not determine rpm; aircraft drag and shaft power do.

## Decision

Retain the APC E 8×8. At 95 km/h, O1 permits total battery power
`P_bat = 1.15 × 95 = 109.25 W`. The Article #1 two-servo avionics plus O4 Air Unit
consume 10.39 W at their rails and **11.54 W from the battery** at the declared BEC
efficiency 0.90. The motor+ESC therefore receives at most **97.71 W**. With
motor+ESC efficiency 0.85,
the UIUC curve gives the following acceptance boundary:

| Quantity | O1 power-limited boundary |
|---|---:|
| J | **0.918** |
| RPM | **8,484** |
| Maximum allowable aircraft drag | **2.12 N** |
| Propeller efficiency | **0.674** |
| Shaft / motor electrical power | **80.9 / 95.2 W** |
| Total battery power | **109.25 W** |
| Aerodynamic acceptance at 95 km/h | **CD ≤ 0.01765; CLEAN L/D ≥ 7.21** |

This is **not a predicted equilibrium**. For any accepted E2 drag `D`, the actual
operating point is obtained by solving `T(J) = D`; `propulsion_match.py --drag-n D`
then reports rpm, total battery power and Wh/km. The 0.80–0.88 motor-efficiency band at
the O1 boundary gives J 0.917–0.933, 8,347–8,499 rpm and 1.91–2.14 N. APC's published
18,750 rpm limit leaves 2.22× margin.

Article #1 is therefore **6S1P, 500–550 Kv, APC E 8×8**. Boundary rpm is 69–76 % of
the motor's nominal no-load rpm, a plausible loaded range. A 4S pack cannot reach this
rpm with the same 500–550 Kv motor even unloaded; a 4S variant needs approximately
**713 Kv** at an assumed 80 % loaded/no-load ratio and is a separate power module.

## Consequences

- `J_opt` remains useful for propeller comparison, but is not a commanded cruise point.
- **E2 drag is now an explicit prerequisite for claiming a unique cruise rpm or
  equilibrium.** The 2.12 N value is an upper acceptance boundary, not predicted drag.
- O1 accounting is total battery power: propulsion, avionics, FPV and conversion losses.
- O2 means a platform can host 4S and 6S modules; it no longer requires one motor and
  one cradle to accept all four historical pack configurations.
- D2 must measure motor, ESC and propeller together. E3 remains the O1 acceptance test.

## Primary data

- UIUC Propeller Database, APC E 8×8 wind-tunnel curve:
  <https://m-selig.ae.illinois.edu/props/propDB.html>
- APC Thin Electric RPM limit and 8×8E product data:
  <https://www.apcprop.com/wp-content/uploads/2022/03/APC-Propeller-RPM-Limits-rev5.pdf>
  and <https://www.apcprop.com/product/8x8e/>
