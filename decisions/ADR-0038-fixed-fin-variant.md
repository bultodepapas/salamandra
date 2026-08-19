# ADR-0038 — Dual directional configuration: finless baseline + fixed-fin variant (V1)

**Status:** 🔄 Provisional · **Date:** 2026-08-06 · **Confidence:** Medium `[D]`/`[E]` bands
**Reversible:** Yes (the fin is an additive CORE component — removable without touching
panels, elevons, balance or avionics) · **Feeds:** I-20, gap G10, O1, O14, guide §7.6

## Context

The Salamandra (forward-swept flying wing, nose boom, pusher, elevons only) is specified
finless. The yaw axis was never analysed — the same failure mode that C6 corrected for
pitch (docs/03). The directional budget (I-20, `yaw_stability.py`, 12 validation cases)
shows:

| Configuration | Cnβ total (/deg) | Verdict |
|---|---|---|
| **Finless baseline** | **−0.0006 … −0.0014** `[E]` | **Negative across the band — statically unstable in yaw**; corrected 2-DOF worst case λ = +6.25/−7.13 s⁻¹ (τ ≈ 0.16 s); FC recovery is unproven and there is no physical yaw effector |
| **V1a — fixed fin, S_v 2.1025 dm²** | powered −0.00029 … +0.00119; motor-off −0.00057 … +0.00087 (powered nominal +0.0005) | Marginal; independent lower corners remain negative |
| **V1b — fixed fin, S_v 2.80 dm²** | powered +0.00017 … +0.00173; motor-off −0.00020 … +0.00130 (powered nominal +0.0010) | Higher powered margin; not robust at the motor-off lower corner |

In-service precedent `[M]`: the TBS Mojito — the same FSW + nose + pusher class — carries
a **fixed** vertical stabilizer on the motor mount and **no rudder servo** (product page,
manual, official INAV CLI: two elevon servos only, bank-to-turn).

## Alternatives considered

1. **Movable rudder.** Rejected by calculation: |Cnδr| ≈ 0.00043/deg cannot hold a steady
   20 km/h crosswind slip at stall (δr ≈ 24° > ±20° available); differential elevons give
   one fifth of a rudder's authority; no mission need exists (INAV coordinates turns
   through roll); cost +1 servo/linkage/mass (I-18 class) with no justified return.
2. **Dorsal fin on the wing (ahead of the prop).** Rejected on drag: needs ≈ 1.7× the
   area of the rear fin for equal Cnβ (shorter arm, no slipstream η).
3. **Single finless configuration.** Rejected as the *only* configuration: it forces the
   first flights of a new airframe onto an FC-dependent yaw axis with no effector, and
   it contaminates E2/E3 pitch data with roll–yaw coupling.
4. **Fin as a CORE variant.** Accepted (this ADR).

## Decision

**Two published configurations:**

```
SALAMANDRA-CLEAN   Finless baseline — O1 efficiency build (≤ 1.15 Wh/km target).
                   Directionally unstable yaw [E]; FC-dependent; documented risk (G10).

SALAMANDRA-V1      Fixed centreline fin, NO rudder — first platform variant (O14),
                   recommended build for the Article #1 test programme after F2 mass closure.
                   Spec (I-20 §6, yaw_stability.py [D]):
                     S_v 2.1025 dm² (V1a) · b_v 251.1 mm · c_r 104.6 / c_t 62.8 mm · AR_v 3.0
                     vertical TE · derived Λc/4 7.125° · root LE/TE x +244.4/+349.1 mm
                     root t ≥ 3.0 mm solid (FS 1.67 at V_NE, no spar credit) · swept tip
                     carrier extension 84.1 mm aft of x +265 · fin AC +285 mm
                     l_v = 379 mm from CG · slipstream η ≈ 1.25
                     complete mass 42.55–67.11 g [E] incl. 5.70 g spar; carrier mass OPEN
                     allocation target 36.72 g OPEN (C32) · ΔCD0 ≈ +0.0015 (+10.2 % energy [E])
```

The fin is a **CORE component** (ADR-0032): panels, elevons, mass balance, servos and FC
are unchanged. V1a is the nominal build; V1b (2.80 dm², +0.0010/deg powered nominal) is a
budget-permitting trade, not a robust motor-off closure. The movable rudder remains documented as a *future* variant,
reopened only if the E-flight programme demonstrates a yaw-handling failure mode.

## Consequences

- **C16 (stall), corrected by C32 and ADR-0045:** the 36.72 g fin allocation omitted
  the mandatory 5.70 g aluminium spar. The connected fin lower assembly is 42.55 g
  and still misses that internal allocation by 5.83 g; however, the current aircraft
  lower model is **1595.80 g / 44.7 km/h**, 24.6 g below the exact C16 mass ceiling.
  V1 remains the preferred test configuration subject to F2 measured mass and battery
  travel closure.
- **O1 (≤ 1.15 Wh/km):** only SALAMANDRA-CLEAN can carry the headline claim; V1 costs
  ≈ +10 % energy `[E]` — still better than the market reference (Mojito 1.40 Wh/km `[M]`).
- **Test programme:** V1 is the instrumented article — doubled nominal Cnr and a damped
  powered nominal reduced mode, but lower independent/motor-off corners remain open;
  E8 must establish the real modal behaviour before release.
- **G10** is bounded by calculation but **closed only by flight test**: yaw-perturbation
  and Dutch-roll-decay runs in the E-series, plus the CORE side-area check at OP-21.
- CAD: the CORE rear pod gains an optional fin mount (screw pattern on the pod end,
  Mojito pattern `[M]`); the fin is a separate printable component.

## Governing data

`calculations/yaw_stability.py` (validation cases: Helmbold, fin reference, Raymer body,
tier consistency, mass/stall and damping) · `research/I-20-yaw-stability-centerline-fin.md` · TBS Mojito
primary sources `[M]` (product page, manual, INAV CLI) · G10.
