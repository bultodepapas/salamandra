# Salamandra — Design Guide: Open Points and Evolution

**Version 0.12** · 17 August 2026 · **v0.2.0 release companion** to
[`Salamandra-Design-Guide-v0.1.md`](Salamandra-Design-Guide-v0.1.md) (v0.17)

This document lists everything in the Design Guide that is **not yet fixed**: assumptions
that need verification, values that will change when the corresponding research closes,
and the revision process. It is the "what to watch" map for the designer and for Phase 1.

Every open point names the trigger that resolves it. Until a trigger fires, the v0.2
value stands.

---

## 1. Open points

### Critical

| # | Item | v0.2 value | What changes it | Trigger |
|---|---|---|---|---|
| **OP-01** | **CG reachability** | **Re-derived for ADR-0040:** target CG −93.8 mm; 6S1P P42A at −372.7 mm in a 155×66×24 cradle from −473 to −272 mm; pack stations −501/−373/−306/−237. Only 6S1P closes the present one-layer envelope. | Real mass properties, central-body NP, final boom/cradle mass | F2/P1–P3; OP-23/OP-24; first-print balance |
| **OP-02** | Airfoil profile | Provisional: reflexed section scaled to 13.5 % root (MH 60-12 % as closest family member, **not MH 45 — C28/I-11**) / reflexed 9 % tip with camber compensation; criteria fixed (t/c 13.5/9, Cm0 ≥ +0.008, C_Lmax ≥ 0.65, **gentle root-first stall — guide §5.1**). **Screening executed (I-15 §6):** E205 discarded (cm0 ≈ −0.07); MH60→13.5 % cm0 = +0.0016 (Re 5e5, Ncrit 10). At −15°, that favourable polar needs ≈ 0.6° permanent reflex after 3.0° wash-in; the adverse cm0 −0.0018 result needs ≈ 1.9° and fails the cap (`elevon_authority.py`). | Final coordinates from the calibrated B3 screening; demonstrate ≤ 0.6° reflex over the accepted polar band. R-AIRFOIL feasibility at 13.5 % is explicit — the root is expected to be a **designed section** (I-15). | G2 closure (I-06 + I-11 + I-15 + B3 + E2) |

### Geometry and stability

| # | Item | v0.2 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-03 | Twist ε | **+3.0° printed wash-in cap + 0.59° equivalent permanent reflex** at −15° for the provisional profile (`sweep_trade.py --full`); this trim cap rejects −12° | Re-derived from final airfoil Cm0/polars; ADR-0040 review if reflex > 0.6° | C5 / OP-02 closure |
| OP-04 | Dihedral Γ | 2.0° total, piecewise-polyhedral (kinks at y = 195/347/498; 0 / 1.07 / 1.53 / 2.0°) | Roll-stability verification; may be revised by the stability analysis | Phase 1 stability (C-series), first flights |
| OP-05 | Neutral point | **25.72 % MAC / −75.8 mm** `[D]` (32×5 VLM); Weissinger-L **27.0 % / −72.9 mm**, 2.9 mm difference (I-21) | Central-body model and measured balance/flight NP | C2 body model; E-series |
| OP-06 | Elevon span / travel | 195–585 mm (30–90 % half-span, panel component), ±20°, dual actuation retained. **Partial closure:** hinge moment 10–48 mN·m/servo is not binding (≥ 3.7× margin, I-18); VLM gives +0.00256 Cm/° and 5° provides 2.6× the limiting trim deficit (`elevon_authority.py`). Remaining: low-Re effectiveness, gust/extreme-CG envelope and sub-400 mm dual-actuation need. | Measured/validated authority across the envelope; confirm dual-actuation need below 400 mm | C6 partial; thread I-10 |
| OP-07 | Hinge line x/c | 0.72 | Fixed by structure (ADR-0002); keep unless section is redesigned | — |

### Structure and materials

| # | Item | v0.2 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-08 | Carbon tube Ø12×1.0 | Provisional (bending only) | Real GJ/EI verification on the section; final sizing | S3/F4 (G4 closure) |
| OP-09 | D-box web at x/c 0.30 | Provisional | Section optimization (cell layout) | S3 |
| OP-10 | TPU hinge stiffness | TPU-printed (baseline) or mylar tape 25×30 (I-09); characterized later | K_hinge enters ω_β (flutter); can be off by factor 3 | C7/S6 (G7) |
| OP-11 | Printing temperatures | 240–250 °C nozzle / 70–80 °C bed | First test prints | First real part |

### Propulsion

| # | Item | v0.2 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-12 | Motor | 28-class, 500–550 KV (reference only) | Matching table (prop–pack–speed) | D3/D4; E3 |
| OP-13 | Propeller | APC-E 8×8 reference | Matching sweep against UIUC J | D3/E3 |
| OP-14 | Pusher vs twin tractor | Single pusher (disputed ADR-0006) | Comparative wake data at Re 4×10⁵; literature bounds | G5; thread I-13 |
| OP-15 | Thrust angle | 0.8° up (Peregrine precedent) | Flight trimming | First flights, E7 |

### Systems and integration

| # | Item | v0.2 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-16 | Battery carrier (cradle) | Printed 2 halves, inner 155×66×24 mm, x ≈ **−473…−272**, 6S1P P42A center −372.7; Ø8.2 channel gripping the boom | R-CG verification in CAD with real packs | F2/P3 |
| OP-17 | Pitot probe position | y ≈ 260 mm LE; lines cross the CORE↔PANEL joint (dedicated channel) | Install/test convenience | D1/D2 |
| OP-18 | FC pitot input | SpeedyBee F405 WING (not MINI) must be verified. **I-17 catalog check (v0.5):** the F405-WING-V2 and SpeedyBee F405 WING meet the full requirement set (I2C for the MS4525 pitot included); H7A3-WING excluded (no INAV target) | Bench check before buying | D1 |
| OP-19 | Cradle position (nose) | Forward support x ≈ **−473**, CORE support x ≈ −132, 341 mm span + 50 mm insertion; pack between supports | OP-01 final validation | F2 |
| **OP-23** | **R-CG four-config requirement** | Required stations now span **−501…−237 mm**. 4S1P fits physically but needs x ≈ −501 outside the cradle; 4S2P/6S2P have no one-layer 155×66×24 arrangement. Present carrier serves 6S1P only. | Re-derive the requirement: per-mission inserts, alternate carrier or explicitly limit the reference aircraft to 6S1P | F2 (P1–P3) with real packs |
| **OP-24** | **Boom mass / stall compliance** | ADR-0040 geometry gives a **38.2 g** hybrid assembly and current AUW **1685.2 g → Vstall 45.9 km/h**. Updated two-support check: σ 56 MPa, FS 4.96, δ 1.6 mm, 25.3 Hz; pure cantilever fails at 278 MPa. Final CAD mass and dimensions remain open. | Real boom CAD mass; final shell mass | F2/P3; first print of CORE |
| **OP-25** | **FPV system selection / integration** | DJI O4 series reference (I-19 `[M]`): camera in the nose boom (2× M2, 16 mm, O4 25.55×20×23.3 mm), VTX in the CORE with airflow (33.5×33.5×13, 20×20/25.5×25.5 M2), antennas ≥ 5 cm at 90°; power: Pro on the 9 V/2 A rail (≥ 13.5 W), Lite on 5 V; energy impact 18.8 %/h (Pro) vs 11.5 % (Lite). **Legacy O3 Air Unit (I-19 §2.4 `[M]`)** fits the mounts (module 32.5×30.5×14.5, camera 21.2×20×19.5); camera hole spacing and measured current pending | Model choice (O4 vs Pro vs Lite; O3 legacy accepted with verifications), camera FOV/lens for the mission, CE legal power, real current measurement | D-series bench; O1 energy re-check |
| **OP-26** | **Fin variant V1 verification (ADR-0038, I-20)** | Re-derived on ADR-0040 geometry: V1a **2.16 dm²**, 254/106/64 mm; V1b **2.86 dm²**, 293/122/73 mm. Root **3.0 mm solid** gives FS 1.65 without spar credit; mode ≈ 7.9 Hz. Ø3 mm Al LE spar retained. V1a lower uncertainty corner is slightly negative (−0.00006/deg); V1b stays positive. | CAD side area, fin flutter/wake test, mass arbitration, E8 yaw perturbation/Dutch-roll decay | F2/F4-S8; E8 |

### Added in v0.2

| # | Item | v0.2 value | What changes it | Trigger |
|---|---|---|---|---|
| **OP-20** | Wing tips | Flat end caps at y = ±650, no winglet | Winglet option (drag/recovery); not required for the O1 cruise claim | First flights, F3 polar |
| **OP-21** | CORE outer mold | Nose support to x ≈ **−473**, cradle 155×66×24, camera x ≈ −407, rear pod to +265 with belly ≤ −111.6 at the prop plane; body shape remains open | Real CORE geometry + mass | F2 (P1–P3) |
| **OP-22** | Missing ADR files | **RESOLVED (2026-08-06):** all 14 pending ADR files (0003, 0006, 0008, 0009, 0012, 0016, 0018, 0023, 0024, 0026, 0030, 0031, 0034, 0035) published from their guide/justification values; index updated | — | ✅ Closed |
| **OP-27** | **Dowel-pin fit tolerance (ADR-0039)** | Holes Ø1.8–1.9 mm printed in both mating faces (solid collar Ø8×4); sliding fit across two parts depends on printer tolerance (±0.1–0.2 mm) | First-print verification: dowel must slide into both faces with light friction after glue application | M3 assembly step (F6), first print of the segments |
| **OP-28** | **Printed-part mass fractions and material variants (docs/06)** | Baseline 600 g printed structure; hybrid boom correctly fixed outside material scaling. AERO WINGS saves 179 g but revision-3 conservative **Vdiv = 91.1 km/h**, below 95 km/h cruise: **not cleared for flight**. | CAD mass properties; measured AERO E/G; new structural concept if pursued | F2 P1/P2; F4 S3/S4/S7 |
| **OP-29** | **Absolute divergence margin (docs/07 rev. 3, G6)** | At −15°: nominal **325.3 km/h** (1.36× PASS), conservative unmeasured **128.8 km/h** (0.54× FAIL), AERO **91.1 km/h**. GXY-plane case 179.0; GXY+gyroid+1.1 mm wall 206, still below 240. Initial **Vlimit 105 km/h**; **150** only after S3 validates GXY. | Real GJ, elastic axis, printed GXY and E7 Southwell | F4 S3/S4; I-21; E7 |
| **OP-30** | **Elastic-axis location** | xEA/c bracket **0.30…0.45 `[E]`**, nominal 0.35. The old x/c = 0.353 enclosed-area centroid is a geometry diagnostic, **not a shear centre**. | Representative-section no-twist load test or validated shell FE model including wall stiffness and cells | S3 before raising Vlimit; E7 correlation |

---

## 2. What is NOT expected to change

- Wingspan 1300 mm, S = 0.282 m², AR 6.0 (ADR-0004, ADR-0010 — branch A is material-forced)
- t/c 13.5 % / 9 % (ADR-0027 — one of the best-supported decisions)
- Forward-swept configuration (ADR-0001); current Λ_c/4 = **−15°** per ADR-0040 and is reviewed only on its declared trim/NP/GJ triggers
- Skin 0.9 mm / gyroid 5 % (ADR-0028), three-cell section (ADR-0002)
- Elevon mass balancing (ADR-0025 — non-negotiable), dual actuation (ADR-0026)
- Joint at 30 % half-span, R-JOINT ≥ 5×, R-NP (ADR-0032)
- Confidence convention, traceability rules (docs/04)

---

## 3. How this guide evolves

1. Each resolved open point produces a **new version** of the Design Guide (0.1 → 0.2 → …)
   with the value updated and the justification annotated.
2. Version bumps are recorded in the guide's §14 and in the [CHANGELOG](../CHANGELOG.md).
3. The designer works from the latest version; the repository always keeps the history
   (no silent edits — project rule).
4. **v1.0** = the configuration actually built as Article #1 (printed, assembled, balanced,
   flying with valid blackbox data; per `docs/05-master-plan.md` §0).

Suggested workflow: the designer raises issues against this document for any value that
cannot be realized in CAD (clearance, printability, servo fit, balance), and the open
point that forced the change is closed with the resolution.

---

## 4. Revision log

| Version | Date | Change |
|---|---|---|
| 0.12 | 2026-08-17 | **Released with v0.2.0 / guide v0.17.** No engineering closure was invented for release: OP-02 airfoil/trim, OP-24 mass, OP-29 divergence and OP-30 elastic-axis measurement remain explicit gates. |
| 0.11 | 2026-08-17 | ADR-0040/I-21 propagated: −15° sweep, NP/CG and cradle rebalanced; OP-28/29 updated to divergence revision 3; **OP-30 added** because the old enclosed-area centroid was not a valid shear-centre solution. |
| 0.10 | 2026-08-06 | **Guide v0.14 reorganization absorbed:** OP-01/OP-16/OP-19/OP-21/OP-23 reworded to the battery cradle (supersedes the 200×70×32 bay — guide §8, CAD question Q1); OP-02/OP-03 refreshed to the twist working value (+3.0° parametric, C5); OP-29 refreshed to docs/07 rev. 2 numbers (275.6/151.5/107.1, V_limit 110). |
| 0.9 | 2026-08-06 | **OP-28 added** (material mass variants: `[E]` printed fractions → CAD; AERO divergence re-check; `docs/06-material-mass-variants.md`, `mass_budget.py`). |
| 0.8 | 2026-08-06 | **OP-27 added** (dowel-pin fit tolerance, ADR-0039 — verification at the first print/M3 assembly). |
| 0.7 | 2026-08-06 | **OP-22 closed** — all 14 missing ADR files published (0003, 0006, 0008, 0009, 0012, 0016, 0018, 0023, 0024, 0026, 0030, 0031, 0034, 0035) from their guide/justification values; OP-25 extended with the legacy DJI O3 Air Unit compatibility row (I-19 §2.4 `[M]`). |
| 0.6 | 2026-08-06 | **Dual directional configuration (ADR-0038, I-20):** OP-26 (fin variant verification) added — Mojito fin measurement, CORE S_fs from CAD, fin flutter/strength at ≈ 9 Hz (F4/S8), C16 with the fin mass at the OP-24 lever, E8 flight closure of G10; OP-24/OP-21 cross-referenced. Guide §5.4 defines the two published configurations (CLEAN / V1). |
| 0.5 | 2026-08-05 | Component catalogs integrated: OP-01/OP-19 numbers re-derived with FPV in the balance (pack ≈ −415, bay −516); OP-06 partial closure (hinge moment not binding, I-18); OP-18 catalog check (I-17); OP-24 updated (AUW 1697 → 46.1 km/h, three levers); OP-25 (FPV selection/integration) added; OP-16/OP-21/OP-23 refreshed. |
| 0.4 | 2026-08-05 | Bay re-derived with the I-16 pack envelope (6S1P 153.2 mm): 200×70×32, forward end ≈ −521, boom ≈ 390 mm; fit verdict: only 6S1P in the bay and in band; 4S1P outside (station); 4S2P/6S2P do not fit (I-16) — OP-23 sharpened; OP-01/OP-16/OP-19/OP-21 updated. |
| 0.3 | 2026-08-05 | OP-01 resolved by decision: nose boom adopted (bay x ≈ −493…−304, 6S1P pack ≈ −421 mm; `balance_cg.py`); pack-station map per config; OP-19/OP-16 updated to the boom; OP-23 (R-CG four-config tension) and OP-24 (boom mass/stall compliance) added; OP-02 updated with the elevon-reflex closure (≤ 0.6°) and R-TWIST 3.0°. |
| 0.2 | 2026-08-05 | OP-01 re-derived with corrected motor station (band ≈ −24…+9 mm, bay-limited); OP-04 defined piecewise (C22); OP-06 elevon span corrected to 30–90 % (C23); OP-19 fixed by the new CORE spec (§7.6 of the guide); OP-20 (wingtips), OP-21 (CORE outer mold), OP-22 (missing ADR files) added. I-09 additions: OP-10 hinge alternative (mylar). I-10…I-14 threads opened; OP-02 updated per C28 (MH 45 → MH 60-12 %); OP-06/OP-14 cross-referenced to I-10/I-13. |
| 0.1 | 2026-08-05 | First release. OP-01 (CG reachability) identified from a preliminary moment balance; all other open points carried from Phase 1 plan. |
