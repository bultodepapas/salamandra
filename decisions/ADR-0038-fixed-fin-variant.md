# ADR-0038 — Dual directional configuration: finless baseline + fixed-fin variant (V1)

**Status:** 🔄 Provisional · **Date:** 2026-08-06 · **Confidence:** Medium `[D]`/`[E]` bands
**Reversible:** Yes (the fin is an additive CORE component — removable without touching
panels, elevons, balance or avionics) · **Feeds:** I-20, gap G10, O1, O14, guide §7.6

## Context

The Salamandra (forward-swept flying wing, nose boom, pusher, elevons only) is specified
finless. The yaw axis was never analysed — the same failure mode that C6 corrected for
pitch (docs/03). The directional budget (I-20, `yaw_stability.py`, six validation cases)
shows:

| Configuration | Cnβ total (/deg) | Verdict |
|---|---|---|
| **Finless baseline** | **−0.0006 … −0.0015** `[E]` | **Negative across the band — statically unstable in yaw**; divergence τ ≈ 0.7 s; flies only FC-stabilized bank-to-turn, with no physical yaw effector |
| **V1a — fixed fin, S_v 2.16 dm²** | −0.00006 … +0.00096 (nominal +0.0005) | Marginal; lower uncertainty corner remains slightly negative |
| **V1b — fixed fin, S_v 2.86 dm²** | +0.00048 … +0.00142 (nominal +0.0010) | Stable across the declared band |

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
                   recommended build for the Article #1 test programme.
                   Spec (I-20 §6, yaw_stability.py [D]):
                     S_v 2.16 dm² (V1a) · b_v ≈ 254 mm · c_r 106 / c_t 64 mm · AR_v 3.0
                     root t ≥ 3.0 mm solid (FS 1.65 at V_NE, no spar credit) · swept tip
                     rear-pod extension ≈ 30 mm aft of x ≈ +265 · fin AC ≈ +285 mm
                     l_v = 379 mm from CG · slipstream η ≈ 1.25
                     mass 37–62 g [E] · ΔCD0 ≈ +0.0015 (+9.9 % energy [E])
```

The fin is a **CORE component** (ADR-0032): panels, elevons, mass balance, servos and FC
are unchanged. V1a is the nominal build; V1b (2.86 dm², +0.0010/deg nominal) is the
budget-permitting upgrade. The movable rudder remains documented as a *future* variant,
reopened only if the E-flight programme demonstrates a yaw-handling failure mode.

## Consequences

- **C16 (stall):** both fin tiers push V_stall past 45 km/h at the current mass budget
  (V1a +50 g → 46.6 km/h); the declared OP-24 lever (shell 550 g, boom ≤ 40 g, servos
  48 g) absorbs V1a to ≈ 45.7 km/h — **arbitrated in F2**.
- **O1 (≤ 1.15 Wh/km):** only SALAMANDRA-CLEAN can carry the headline claim; V1 costs
  ≈ +10 % energy `[E]` — still better than the market reference (Mojito 1.40 Wh/km `[M]`).
- **Test programme:** V1 is the instrumented article — doubled Cnr, no yaw divergence,
  cleaner E2/E3 polars.
- **G10** is bounded by calculation but **closed only by flight test**: yaw-perturbation
  and Dutch-roll-decay runs in the E-series, plus the CORE side-area check at OP-21.
- CAD: the CORE rear pod gains an optional fin mount (screw pattern on the pod end,
  Mojito pattern `[M]`); the fin is a separate printable component.

## Governing data

`calculations/yaw_stability.py` (validation cases: Helmbold, fin reference, Raymer body,
tier consistency, damping) · `research/I-20-yaw-stability-centerline-fin.md` · TBS Mojito
primary sources `[M]` (product page, manual, INAV CLI) · G10.
