# I-20 — Directional (yaw) stability and the centreline-fin variant

**Status:** 🔄 Updated for ADR-0040 — quantitative budget `[D]`, band inputs `[E]`; flight-test closure pending
**Date:** 2026-08-17
**Feeds:** First platform variant (O14, ADR-0032), CORE rear-pod design (guide §7.6), OP-21, gap G10, in-service Mojito comparison (docs/02, I-02)
**Does not close:** G8 (pitch NP) — this is the lateral-directional axis, Phase 1's declared task (I-10 §7)

> **C31/C32 update:** `yaw_stability.py` consumes the −15° geometry and solved
> −93.8 mm CG. It also corrects an internal inconsistency: structure/rudder/damping now
> use the calculated fin area instead of a stale fixed 2.0 dm². With the v0.3 boom,
> current V1a is 2.13 dm² with a 3.0 mm solid root; V1b is 2.83 dm². C32 adds the
> mandatory 5.70 g spar to both complete-fin mass bands.

> **ADR-0045 mass update (2026-08-18):** the selected elevon/balance allocation makes
> current CLEAN 1553.25 g and V1a lower model 1596.26 g / 44.7 km/h. The 43.01 g fin
> still exceeds its internal 36.72 g allocation by 6.29 g, but no longer causes an
> analytical C16 stall-speed failure. Physical F2 mass and E2 CLmax remain gates.

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
   - **The nose boom** (OP-01, supports x ≈ −459…−132) is a long fuselage ahead of the CG: the
     body contribution to Cnβ is negative, and the boom adds yaw inertia
     (I_z ≈ 0.28 kg·m², with the 6S1P pack at ≈ −0.373 m).
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
(fin AC ≈ +285 mm from root c/4; l_v = 0.379 m from the CG at −93.8 mm). The dorsal
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
| Body (k 0.40 … 0.96, S_fs 0.040 m²) | **−0.00056 … −0.00135** |
| Wing, FSW (band) | −0.00010 … 0.00000 |
| **Total, no fin** | **−0.00056 … −0.00145** — negative across the whole band |
| Worst-case yaw mode | Corrected 2-DOF λ ≈ +6.25/−7.13 s⁻¹ → **divergence τ ≈ 0.16 s** `[E]` |

The finless Salamandra is **directionally unstable in the classical sense**. The
corrected 0.16 s divergence is too fast to claim that bank-to-turn stabilization will
recover it, especially because there is no physical yaw effector or restoring moment.
Finless flight therefore requires its own E8 build-up evidence; it is not the first-test
configuration. This is exactly why the Mojito — the closest in-service FSW + nose +
pusher — carries a fin.

## 5.2 Fin sizing (centreline, rear-pod, l_v = 379 mm, AR_v = 3.0)

| | **V1a — marginal** | **V1b — robust** |
|---|---|---|
| S_v | **2.13 dm²** | **2.83 dm²** |
| b_v / c_r / c_t | 253 / 105 / 63 mm | 291 / 121 / 73 mm |
| Cnβ_total band | −0.00006 … +0.00096 (nominal **+0.0005**) | +0.00048 … +0.00142 (nominal **+0.0010**) |
| V_v = S_v·l_v/(S·b) | 0.022 | 0.030 (tailless practice ≈ 0.02–0.05 `[I]`) |
| Complete mass (distributed thickness + mount + spar) | **43.01–67.88 g** | **55.32–88.39 g** |
| ΔCD0 | +0.0014 | +0.0019 |
| Drag / Wh/km impact | **+9.8 % → ≈ 1.26** `[E]` | +12.9 % → ≈ 1.30 `[E]` |
| AUW & V_stall | Lower model **1596.26 g / 44.7 km/h analytical PASS**; allocation target 1589.97 g / 44.6 km/h | Heavier option; recompute after V1b CAD mass |

C16 is analytically closed for the V1a lower model with 24.1 g margin to the exact
45 km/h mass ceiling. The former 36.72 g V1a value is still an internal allocation
target, not a physical lower bound; C32's connected fin model misses it by 6.29 g and
the V1 battery target is 2.72 mm beyond travel — both are **flagged to F2/OP-24**.

## 5.3 Structure (V1a at V_NE 180 km/h, cantilever)

- Side load F = 40.7 N at the centroid (116 mm) → M = 4.72 N·m.
- Root thickness: 1.5 mm → σ ≈ 121 MPa (**fails**); 2.5 mm → σ ≈ 43.6 MPa,
  **FS 1.16 (rejected)**; **3.0 mm → σ 29.9 MPa, FS 1.67** without spar credit.
- **Spec: root t ≥ 3.0 mm solid, trapezoidal, swept tip.**
- First bending mode ≈ 7.9 Hz — flutter/strength verification in F2 (G7 discipline).

## 5.4 Movable rudder — quantified rejection

- Authority |Cnδr| ≈ **0.00043/deg** (τ 0.32).
- To hold a steady sideslip in a 20 km/h crosswind at stall (β ≈ 24°): **δr ≈ 28° —
  beyond ±20° available. Cannot hold.** At cruise (β ≈ 12°): δr ≈ 12° — feasible but
  unnecessary (crab + bank is standard).
- Differential elevons (the only no-fin yaw control) ≈ **0.00008/deg — one fifth of a
  rudder's authority** `[E]`, and it costs lift and drag.

The rudder cannot deliver what it would be bought for (crosswind landing authority), and
the mission does not need it: INAV/ArduPilot coordinate turns through roll. **A movable
rudder is not justified in this analysis.** The Mojito agrees `[M]`.

## 5.5 Yaw damping

Cnr: wing −0.032 → with V1a fin **−0.084 /rad (doubled)**. With the corrected C31
dimensionalization, CLEAN gives +6.25/−7.13 s⁻¹ and V1a gives the damped reduced pair
−0.796 ± 3.947i s⁻¹ (decay τ ≈ 1.3 s) `[E]`. The fin converts a divergence into a
damped lateral-directional oscillation in this reduced model.

# 6. Recommendation (engineering)

1. **V1 = fixed centreline fin, no rudder — first platform variant (O14), recommended
   build for the Article #1 test programme.** Size V1a (S_v = 2.13 dm², b_v ≈ 253 mm,
   c_r ≈ 105 / c_t ≈ 63 mm, AR_v ≈ 3.0, root t ≥ 3.0 mm) on a ≈ 30 mm rear-pod extension
   behind the prop disk, fin AC ≈ +285 mm, slipstream-mounted (η ≈ 1.25 — the fin is
   *most* effective at low speed, exactly where launch and stall handling need it).
   Complete lower mass 43.01 g against a 36.72 g allocation target, ΔCD0 ≈ +0.0014.
   V1b (+0.0010/deg nominal) if F2 allows its 55.32–88.39 g complete mass.
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
| Fin flutter/strength at the 8.0 Hz mode, wake buffeting | F2 (loads and structure) |
| **E-flight falsification:** yaw perturbation test (rudder-kick analog via aileron impulse, Dutch roll decay in blackbox) | E-series — the only `[M]` closure of §5 |
| C16 (stall) with the fin mass at the declared lever | F2 mass arbitration (OP-24 extension) |

# 9. Transfer limits

- All magnitudes carry `[E]` bands on: S_fs and the body factor k_f (the two methods,
  Munk-slim vs Raymer-full, differ ≈ 3× — the band brackets both), low-Re CLα of a
  printed surface, slipstream η, yaw inertia, and the simplified 2-DOF dynamics. The
  *sign* conclusions (finless negative; fin restores stability; rudder not needed) are
  robust to the band; the *sizes* (2.13 vs 2.83 dm²) are not — hence the two tiers.
- The 2-DOF (β, r) model estimates reduced lateral-directional modes, not a full
  Dutch-roll identification (p and φ are omitted) — declared `[E]`, flight data to close.
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
