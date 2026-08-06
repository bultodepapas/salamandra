# I-20 — Directional (yaw) stability and the centreline-fin variant

**Status:** 🔄 New — quantitative budget `[D]`, band inputs `[E]`; flight-test closure pending (E-series)
**Date:** 2026-08-05
**Feeds:** First platform variant (O14, ADR-0032), CORE rear-pod design (guide §7.6), OP-21, gap G10, in-service Mojito comparison (docs/02, I-02)
**Does not close:** G8 (pitch NP) — this is the lateral-directional axis, Phase 1's declared task (I-10 §7)

---

# 1. Question

Does the Salamandra (forward-swept flying wing, nose boom, pusher, elevons only) need a
vertical stabilizer — fixed fin and/or movable rudder — and if so, at what size, mass and
drag cost? What does the closest in-service configuration (TBS Mojito, same FSW + nose +
pusher layout) actually do, and what does the engineering budget say about copying it?

**Primary finding (in-service, `[M]`):** the Mojito carries a **fixed** vertical stabilizer
on the motor mount and **no rudder servo** — its official INAV CLI configures exactly two
servos (elevons) and flies bank-to-turn. A movable rudder is *not* the Mojito's answer; a
fixed fin is. This thread reproduces that choice with numbers for the Salamandra.

# 2. Why it matters

1. **The configuration is directionally handicapped by construction:**
   - **Forward sweep** is the *destabilizing* yaw contribution (opposite of the aft-swept
     planks that dominate flying-wing FPV practice) — I-02 documents this family's known
     compensation (extremely forward CG, short elevon throws).
   - **The nose boom** (OP-01, x ≈ −516…−132) is a long fuselage ahead of the CG: the
     body contribution to Cnβ is negative, and the boom adds yaw inertia
     (I_z ≈ 0.28 kg·m², of which ≈ 0.08 from the 6S1P pack at ≈ −0.42 m).
   - **There is no yaw effector.** INAV yaw PIDs (fw_p_yaw) need a surface or
     differential thrust; with elevons only, yaw is open-loop and the aircraft is
     bank-to-turn by necessity.
2. **Baseline claim was never checked.** The guide's "no tail, no vertical stabilizer, no
   rudder" (render prompt v0.1-01) is an assumption, not a calculation — exactly the
   failure mode C6 corrected for pitch (docs/03).
3. **The efficiency target is at stake.** O1 (≤ 1.15 Wh/km at 95 km/h) lives at the clean
   end of the drag budget; any fin adds parasitic drag in the prop wake. The trade must
   be quantified, not assumed.

# 3. What was searched (2026-08-05)

| Source | What | Result | Grade |
|---|---|---|---|
| team-blacksheep.com, TBS Mojito product page (kit) | Configuration: FSW 1300 mm, 1800 g, 6S–8S; **"plastic leading edge covers for the wings and vertical stabilizer"**; kit contents: **2 servos for elevons** only | Fin exists, fixed; no rudder servo anywhere in the product | `[M]` |
| TBS Mojito manual (PDF, official) | Assembly: stabilizer installed on the motor mount; "the longer screw … mainly holding the vertical stabilizer"; ESC bay **under the stabilizer**; receiver/antenna compartment **inside the vertical stabilizer**; elevon throws 15 mm pitch / 20 mm roll; motor 1000 KV, 14 poles | Fin is a hollow rear part on the motor mount, behind the pusher prop; serves as antenna/ESC housing | `[M]` |
| TBS Mojito official INAV CLI file | `servo 1/2` only (elevons, one reversed); `fw_p_yaw = 7`; `fw_ff_roll = 93` (feed-forward roll = bank-to-turn); `fw_level_pitch_trim = 1.996`; launch/loiter settings | **No rudder channel, no rudder mixing.** Bank-to-turn confirmed | `[M]` |
| mh-aerotools.de flying-wing pages | Attempted fetch of tailless sizing articles | 404 (not found) — logged as failed attempt | — |
| aerodesign.de "Faszination Nurflügel" (Unverferth) | Attempted fetch of the directional-stability chapter | 404 (not found) — logged as failed attempt | — |
| TBS Mojito gallery photos (5) | Fin geometry measurement from images | **Downloaded, but the analysis model cannot process images** — measurement pending human verification (OP) | pending |
| Published methods | Textbook stability & control methodology (below, §Sources) | Used for all formulas | `[M]`-method |

> Tool note: AGENTS.md prescribes Firecrawl MCP for search; it was **not available in this
> session** — direct fetches (webfetch/Invoke-WebRequest) were used and logged above.

# 4. Method (all reproducible in `calculations/yaw_stability.py`)

Cnβ budget, per-degree, band inputs `[E]`:

```
Cnβ_total = Cnβ_fin(η, sidewash, S_v, l_v, CLα_v) + Cnβ_body(−k_f·S_fs·l_f/(S·b)) + Cnβ_wing(FSW)
```

| Term | Formula | Source |
|---|---|---|
| Fin | Cnβ_v = η·(1+dσ/dβ)·(S_v/S)·(l_v/b)·CLα_v | DATCOM/Roskam |
| CLα_v | Helmbold-Diederich: 2πA/(2+√(A²(1+tan²Λ)/η²+4)) × low-Re factor 0.85–1.00 `[E]` | DATCOM form |
| Body | Cnβ_f = −k_f·(S_fs·l_f)/(S·b), k_f = 0.40…0.96 (slender boom → full-body Raymer) | Raymer/DATCOM; Munk lower bound |
| Wing | Small at AR 6 (|Cnβ_w| ≤ 1e-4/deg); **negative** for forward sweep | band `[E]` |
| Rudder | Cnδr = −η_r·CLα_v·τ·(S_v/S)·(l_v/b), τ = 0.25…0.40 (30 % chord, low Re) | DATCOM |
| Damping | Cnr_v = −2·η·CLα_v·(S_v/S)·(l_v/b)²; Cnr_w ≈ −CL/4 | DATCOM |
| Dynamics | 2-DOF (β, r) eigenvalues; I_z ≈ 0.28 kg·m² `[E]` | simplified, declared |
| Structure | Cantilever bending at V_NE, CN = 1.0, slipstream q-ratio 1.25 | `[D]` |
| Drag | ΔCD0 = η·k_int·Cf·(2S_v/S), Cf turbulent flat plate, k_int 1.35 | Hoerner |

Fin installation (V1): centreline, on a **rear-pod extension** behind the prop disk
(fin AC ≈ +285 mm from root c/4; l_v = 0.404 m from the CG at −119 mm). The dorsal
alternative (on the wing, ahead of the prop) needs ≈ 1.7× the area for the same Cnβ
(shorter arm, no slipstream η) — rejected on drag before running it.

**Validation cases (all PASS):** Helmbold AR 4 η 0.95 → 3.7729/rad; fin reference
0.10·0.30·0.06 → +0.00180/deg; Raymer C172-like body → −0.00141/deg (published band
−0.0012…−0.0016); V1b nominal ≥ +0.0010/deg; finless nominal < 0; Cnδr reference
0.00062/deg.

# 5. Results `[D]` on `[E]` bands (yaw_stability.py)

## 5.1 Finless baseline — statically unstable in yaw

| Term | Value (/deg) |
|---|---|
| Body (k 0.40 … 0.96, S_fs 0.040 m²) | **−0.00059 … −0.00143** |
| Wing, FSW (band) | −0.00010 … 0.00000 |
| **Total, no fin** | **−0.00059 … −0.00153** — negative across the whole band |
| Worst-case yaw mode | λ ≈ +1.5 1/s → **divergence τ ≈ 0.7 s** `[E]` |

The finless Salamandra is **directionally unstable in the classical sense**. It would fly
only because INAV holds heading through roll (bank-to-turn) and the time constant is long
enough for the FC — but there is no physical yaw effector, no restoring moment, and the
boom's yaw inertia (≈ 0.07 kg·m² from the pack alone) delays any correction. This is
exactly why the Mojito — the closest in-service FSW + nose + pusher — carries a fin.

## 5.2 Fin sizing (centreline, rear-pod, l_v = 404 mm, AR_v = 3.0)

| | **V1a — marginal** | **V1b — robust** |
|---|---|---|
| S_v | **2.1 dm²** | **2.8 dm²** |
| b_v / c_r / c_t | 250 / 105 / 63 mm | 290 / 120 / 72 mm |
| Cnβ_total band | −0.0001 … +0.0010 (nominal **+0.0005**) | +0.0005 … +0.0015 (nominal **+0.0010**) |
| V_v = S_v·l_v/(S·b) | 0.023 | 0.030 (tailless practice ≈ 0.02–0.05 `[I]`) |
| Mass (solid 1.2–2.0 mm) | **36–60 g** | **47–79 g** |
| ΔCD0 | +0.0014 | +0.0018 |
| Drag / Wh/km impact | **+9.6 % → ≈ 1.26** `[E]` | +12.6 % → ≈ 1.29 `[E]` |
| AUW & V_stall | +48 g → 46.7 km/h | +63 g → 47.0 km/h |

C16 tension: both options push V_stall above the 45 km/h requirement at the current
budget; the guide's declared lever (shell 550 g, boom ≤ 40 g, servos 48 g → ≈ 1625 g)
absorbs V1a with ≈ 45.7 km/h at the lever — **flagged to F2/OP-24**.

## 5.3 Structure (V1a at V_NE 180 km/h, cantilever)

- Side load F ≈ 38 N at the centroid (110 mm) → M ≈ 4.2 N·m.
- Root thickness: 1.5 mm → σ ≈ 108 MPa (**fails**, FS 0.46); **2.5 mm → σ ≈ 39 MPa,
  FS 1.29**; 3.0 mm → FS 1.86.
- **Spec: root t ≥ 2.5 mm solid (or 2 mm + carbon strip), trapezoidal, swept tip.**
- First bending mode ≈ 9 Hz — flutter/strength verification in F2 (G7 discipline).

## 5.4 Movable rudder — quantified rejection

- Authority |Cnδr| ≈ **0.00043/deg** (τ 0.32).
- To hold a steady sideslip in a 20 km/h crosswind at stall (β ≈ 24°): **δr ≈ 24° —
  beyond ±20° available. Cannot hold.** At cruise (β ≈ 12°): δr ≈ 12° — feasible but
  unnecessary (crab + bank is standard).
- Differential elevons (the only no-fin yaw control) ≈ **0.00008/deg — one fifth of a
  rudder's authority** `[E]`, and it costs lift and drag.

The rudder cannot deliver what it would be bought for (crosswind landing authority), and
the mission does not need it: INAV/ArduPilot coordinate turns through roll. **A movable
rudder is not justified in this analysis.** The Mojito agrees `[M]`.

## 5.5 Yaw damping

Cnr: wing −0.033 → with V1a fin **−0.089 /rad (doubled)**; yaw subsidence with V1a:
λ ≈ −0.65 1/s (stable, τ ≈ 1.5 s) `[E]` vs +1.5 1/s finless. The fin converts a
divergence into a damped subsidence.

# 6. Recommendation (engineering)

1. **V1 = fixed centreline fin, no rudder — first platform variant (O14), recommended
   build for the Article #1 test programme.** Size V1a (S_v ≈ 2.1 dm², b_v ≈ 250 mm,
   c_r ≈ 105 / c_t ≈ 63 mm, AR_v ≈ 3.0, root t ≥ 2.5 mm) on a ≈ 30 mm rear-pod extension
   behind the prop disk, fin AC ≈ +285 mm, slipstream-mounted (η ≈ 1.25 — the fin is
   *most* effective at low speed, exactly where launch and stall handling need it).
   Mass 36–60 g, ΔCD0 ≈ +0.0014. V1b (+0.0010/deg nominal) if the F2 mass lever allows.
2. **The finless configuration remains the O1-efficiency baseline** (≤ 1.15 Wh/km needs
   the cleanest build; the fin costs ≈ +10 % energy `[E]`). It is documented here as
   directionally unstable and FC-dependent — a declared risk, not a silent assumption.
3. **No rudder.** Revisit only if the E-flight programme shows a yaw-handling failure
   mode that a surface would fix (currently none identified).
4. **Benefit to the test programme:** the fin doubles Cnr and removes the slow yaw
   divergence — cleaner E2/E3 polar data (less roll–yaw contamination of the pitch
   measurements), which is worth more than the drag it costs on the instrumented article.

# 7. Consequences for the platform

- The fin is a **CORE component** (ADR-0032): panels, elevons, mass balance and the
  flight controller are untouched. It is a pure additive variant — the platform's first.
- Rear-pod geometry: extension +30 mm aft of x ≈ +265, motor-mount screw pattern
  (Mojito precedent `[M]`), optional antenna/ESC housing (Mojito practice `[M]`).
- INAV/ArduPilot: no config change required (passive surface); fw_p_yaw is already
  present for the finless case.
- The Mojito pattern is confirmed as *engineering-copyable* for this exact configuration
  class (FSW + nose + pusher): fixed fin, bank-to-turn, no rudder.

# 8. Open items

| Item | Closes with |
|---|---|
| Real Mojito fin dimensions (photos downloaded, model cannot process images) | Human measurement of the 5 gallery files in session cache |
| Exact CORE/boom side area S_fs from the CAD (affects the band midpoint) | OP-21 (CORE outer mold) |
| Fin flutter/strength at the 9 Hz mode, wake buffeting | F2 (loads and structure) |
| **E-flight falsification:** yaw perturbation test (rudder-kick analog via aileron impulse, Dutch roll decay in blackbox) | E-series — the only `[M]` closure of §5 |
| C16 (stall) with the fin mass at the declared lever | F2 mass arbitration (OP-24 extension) |

# 9. Transfer limits

- All magnitudes carry `[E]` bands on: S_fs and the body factor k_f (the two methods,
  Munk-slim vs Raymer-full, differ ≈ 3× — the band brackets both), low-Re CLα of a
  printed surface, slipstream η, yaw inertia, and the simplified 2-DOF dynamics. The
  *sign* conclusions (finless negative; fin restores stability; rudder not needed) are
  robust to the band; the *sizes* (2.1 vs 2.8 dm²) are not — hence the two tiers.
- The 2-DOF (β, r) model is a subsidence check, not a Dutch-roll analysis (4-DOF with
  p, φ needed) — declared `[E]`, flight data to close.
- Mojito practice is one data point from a single manufacturer `[M]` (same limitation
  class as I-08/I-09): configuration-class evidence, not replication.

# 10. Sources

- TBS Mojito product page (kit) — `team-blacksheep.com/products/prod:tbs_mojito_kit`
  (accessed 2026-08-05) `[M]`
- TBS Mojito manual — `team-blacksheep.com/media/files/tbs-mojito-manual.pdf` `[M]`
- TBS Mojito official INAV CLI — `team-blacksheep.com/media/files/tbs-mojito-inav-cli.txt` `[M]`
- TBS Mojito gallery photos (5 files, session cache) — pending human measurement
- USAF Stability and Control DATCOM (Hoak et al.), 1978 — fin/body/derivative methods
- Roskam, J. — *Airplane Flight Dynamics and Automatic Flight Controls*, 2nd ed. — fin
  contribution, Cnβ criteria
- Raymer, D. — *Aircraft Design: A Conceptual Approach* — body contribution, V_v practice
- Etkin, B. & Reid, L. — *Dynamics of Flight: Stability and Control* — Cnβ criteria
- Helmbold, H. — low-AR lift-curve (as used in DATCOM form)
- Hoerner, S. — *Fluid-Dynamic Drag* — fin drag, interference
- Repo: design guide v0.5 §5/§7.6/§8, OP-01/OP-24, I-02, I-10, docs/00 O1/O14, docs/03
