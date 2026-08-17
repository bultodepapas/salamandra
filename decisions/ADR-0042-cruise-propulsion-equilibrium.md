# ADR-0042 — Cruise propulsion is matched at aircraft equilibrium

**Status:** ✅ Active · **Date:** 2026-08-17 · **Confidence:** Medium `[D]`/`[E]` · **Reversible:** Yes
**Research:** I-03, I-22 · **Verification:** D2 bench map, E3 flight energy

## Context

ADR-0007 correctly selected the APC Thin Electric 8×8 from measured UIUC data, but the
v0.2 guide incorrectly prescribed its maximum-efficiency advance ratio as the cruise
operating point. At 95 km/h that point demands about 230 W electrical and 5.46 N thrust,
so it cannot simultaneously represent the O1 ceiling of 1.15 Wh/km. Propeller efficiency
alone does not determine rpm; aircraft drag and shaft power do.

## Decision

Retain the APC E 8×8 and solve its measured UIUC coefficient curve at fixed airspeed and
the O1 electrical-power ceiling. At 95 km/h, `P_e = 1.15 × 95 = 109.25 W`. With the
declared motor+ESC efficiency estimate of 0.85:

| Quantity | Equilibrium value |
|---|---:|
| J | 0.899 |
| RPM | 8,667 |
| Thrust = aircraft drag | 2.42 N |
| Propeller efficiency | 0.688 |
| Shaft / electrical power | 92.9 / 109.3 W |

The 0.80–0.88 motor-efficiency band gives J 0.893–0.909, 8,568–8,722 rpm and
2.25–2.52 N. APC's published 18,750 rpm limit for an 8-inch Thin Electric propeller
leaves 2.16× margin.

Article #1 is therefore **6S1P, 500–550 Kv, APC E 8×8**. Required rpm is 71–78 % of
the motor's nominal no-load rpm, a plausible loaded range. A 4S pack cannot reach this
rpm with the same 500–550 Kv motor even unloaded; a 4S variant needs approximately
**730 Kv** at an assumed 80 % loaded/no-load ratio and is a separate power module.

## Consequences

- `J_opt` remains useful for propeller comparison, but is not a commanded cruise point.
- O2 means a platform can host 4S and 6S modules; it no longer requires one motor and
  one cradle to accept all four historical pack configurations.
- D2 must measure motor, ESC and propeller together. E3 remains the O1 acceptance test.

## Primary data

- UIUC Propeller Database, APC E 8×8 wind-tunnel curve:
  <https://m-selig.ae.illinois.edu/props/propDB.html>
- APC Thin Electric RPM limit and 8×8E product data:
  <https://www.apcprop.com/wp-content/uploads/2022/03/APC-Propeller-RPM-Limits-rev5.pdf>
  and <https://www.apcprop.com/product/8x8e/>
