# Salamandra — Design Guide: Open Points and Evolution

**Version 0.9** · 6 August 2026 · Companion to
[`Salamandra-Design-Guide-v0.1.md`](Salamandra-Design-Guide-v0.1.md) (v0.9)

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
| **OP-01** | **CG reachability** | **Resolution adopted (v0.3–v0.5):** nose boom carrying the battery bay (forward end x ≈ −516, 200×70×32, pack 6S1P 153.2 mm I-16, FPV camera at the boom front), 6S1P pack at ≈ −415 mm for CG −119 mm; pack stations −568/−415/−342/−267 (4S1P/6S1P/4S2P/6S2P, `balance_cg.py` `[D]`) | Real components (F2/P1–P3), central-body NP margin, boom mass | F2 mass model; OP-23/OP-24; boom structure validation at first print |
| **OP-02** | Airfoil profile | Provisional: reflexed section scaled to 13.5 % root (MH 60-12 % as closest family member, **not MH 45 — C28/I-11**) / reflexed 9 % tip with camber compensation; criteria fixed (t/c 13.5/9, Cm0 ≥ +0.008, C_Lmax ≥ 0.65, **gentle root-first stall — guide §6.1**). **Screening executed (I-15 §6):** E205 discarded (cm0 ≈ −0.07); MH60→13.5 % cm0 = +0.0016 (Re 5e5, Ncrit 10); no off-the-shelf candidate closes trim inside R-TWIST at SM 8 % — residual ≤ 0.6° permanent elevon reflex (v0.3, `elevon_authority.py`) | Final coordinates from the calibrated B3 screening; R-AIRFOIL feasibility at 13.5 % is an explicit B3 question — the root is expected to be a **designed section** (evidence campaign I-15) | G2 closure (I-06 + I-11 + I-15 + B3 + E2) |

### Geometry and stability

| # | Item | v0.2 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-03 | Twist ε | +0.5° wash-in | Re-derived from the final airfoil Cm0 (0.17–0.76° band for SM 8 %) | C5 (torsion window closure) |
| OP-04 | Dihedral Γ | 2.0° total, piecewise-polyhedral (kinks at y = 195/347/498; 0 / 1.07 / 1.53 / 2.0°) | Roll-stability verification; may be revised by the stability analysis | Phase 1 stability (C-series), first flights |
| OP-05 | Neutral point | 26.7 % MAC `[D]` (VLM only) | Independent method + central body | **C2 partial (I-15 §6.3):** Weissinger-L cross-check agrees within 3 mm (−98.3 mm / 28.0 % MAC); central-body effect remains unquantified | C2 (body model, I-07 §7.4) |
| OP-06 | Elevon span / travel | 195–585 mm (30–90 % half-span, panel component), ±20°, dual actuation retained. **Partial closure (I-18, v0.5):** hinge moment 10–48 mN·m/servo is NOT the binding constraint (≥ 3.7× margin on the most modest catalog servo, `servo_torque.py`); trim authority verified (`elevon_authority.py`); remaining: gust/extreme-CG envelope and the sub-400 mm dual-actuation need | Authority verification across the envelope (gust, extreme CG); confirm dual-actuation need below 400 mm | C6 — never done before; thread I-10 |
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
| OP-16 | Battery bay 200×70×32 mm | Provisional; v0.5 fixes the forward end at x ≈ −516 (nose boom); pack envelope per I-16 | R-CG verification in CAD with real packs | F2/P3 |
| OP-17 | Pitot probe position | y ≈ 260 mm LE; lines cross the CORE↔PANEL joint (dedicated channel) | Install/test convenience | D1/D2 |
| OP-18 | FC pitot input | SpeedyBee F405 WING (not MINI) must be verified. **I-17 catalog check (v0.5):** the F405-WING-V2 and SpeedyBee F405 WING meet the full requirement set (I2C for the MS4525 pitot included); H7A3-WING excluded (no INAV target) | Bench check before buying | D1 |
| OP-19 | Bay position (nose) | CORE nose boom, forward end at x ≈ −516 (guide §7.6) | OP-01 final validation | F2 |
| **OP-23** | **R-CG four-config requirement** | docs/00 §3.3 requires CG ±5 mm in all four pack configs; with the boom, pack stations span −568…−267 mm, **and the pack envelope (I-16) sharpens the conflict: 4S2P/6S2P fit no single-layer arrangement of the 200×70×32 bay at all; 4S1P fits but needs x ≈ −568 (outside the bay)** — the v0.5 bay serves the reference 6S1P only | Re-derivation of the requirement (per-configuration CG acceptance, or per-mission bay inserts, or a taller/stacked bay violating the single-layer rule) | F2 (P1–P3) with real packs |
| **OP-24** | **Boom mass / stall compliance** | Boom structure ≤ 40 g target; with the FPV unit (37 g, I-19) AUW 1697 g → V_stall ≈ 46.1 km/h vs ≤ 45 required; declared levers: shell 550 g + boom ≤ 40 g + servos 48 g (I-18 class) → AUW ≈ 1625 g → ≈ 45.1 km/h — **borderline; F2 must arbitrate the mass budget against C16** | Real boom CAD mass; final shell mass; F2 budget | F2/P3; first print of the CORE |
| **OP-25** | **FPV system selection / integration** | DJI O4 series reference (I-19 `[M]`): camera in the nose boom (2× M2, 16 mm, O4 25.55×20×23.3 mm), VTX in the CORE with airflow (33.5×33.5×13, 20×20/25.5×25.5 M2), antennas ≥ 5 cm at 90°; power: Pro on the 9 V/2 A rail (≥ 13.5 W), Lite on 5 V; energy impact 18.8 %/h (Pro) vs 11.5 % (Lite). **Legacy O3 Air Unit (I-19 §2.4 `[M]`)** fits the mounts (module 32.5×30.5×14.5, camera 21.2×20×19.5); camera hole spacing and measured current pending | Model choice (O4 vs Pro vs Lite; O3 legacy accepted with verifications), camera FOV/lens for the mission, CE legal power, real current measurement | D-series bench; O1 energy re-check |
| **OP-26** | **Fin variant V1 verification (ADR-0038, I-20)** | Fixed centreline fin: S_v 2.1 dm² (V1a) / 2.8 dm² (V1b), b_v 250–290 mm, root t ≥ 2.5 mm, rear-pod extension ≈ 30 mm (fin AC ≈ +285). Open items: (a) real Mojito fin dimensions — photos downloaded, measurement pending human verification; (b) CORE/boom exact side area S_fs from the CAD (band midpoint); (c) fin strength/flutter at the ≈ 9 Hz mode and wake buffeting; (d) C16 stall compliance with the fin mass at the OP-24 lever; (e) **E8 flight test (yaw perturbation, Dutch-roll decay) — the only `[M]` closure of G10** | Fin flutter (F2/F4-S8), CAD S_fs (OP-21), E-flight yaw test (E8), first print | F2 mass arbitration; E-series |

### Added in v0.2

| # | Item | v0.2 value | What changes it | Trigger |
|---|---|---|---|---|
| **OP-20** | Wing tips | Flat end caps at y = ±650, no winglet | Winglet option (drag/recovery); not required for the O1 cruise claim | First flights, F3 polar |
| **OP-21** | CORE outer mold | Nose boom to x ≈ −516 (bay 200×70×32), FPV camera mount at the boom front, rear pod to x ≈ +265 with belly ≤ −111.6 mm at the prop plane, avionics stations (guide §7.6) — binding constraints given, body shape open | Real CORE geometry + mass (the pods add mass not in the §8.1 estimate) | F2 (P1–P3) |
| **OP-22** | Missing ADR files | **RESOLVED (2026-08-06):** all 14 pending ADR files (0003, 0006, 0008, 0009, 0012, 0016, 0018, 0023, 0024, 0026, 0030, 0031, 0034, 0035) published from their guide/justification values; index updated | — | ✅ Closed |
| **OP-27** | **Dowel-pin fit tolerance (ADR-0039)** | Holes Ø1.8–1.9 mm printed in both mating faces (solid collar Ø8×4); sliding fit across two parts depends on printer tolerance (±0.1–0.2 mm) | First-print verification: dowel must slide into both faces with light friction after glue application | M3 assembly step (F6), first print of the segments |
| **OP-28** | **Printed-part mass fractions and material variants (docs/06)** | `mass_budget.py` uses `[E]` fractions of the 600 g shell (core 30 % / wings 62 % / tips 8 %; elevons `[D]` 2×25 g) and ρ per material (I-04); **AERO WINGS / AERO MAX** (−179/−230 g, stall-compliant) are conditional on the **divergence re-verification of the LW wing** (E ≈ 0.5× PETG — G4/G6/S3–S4) and the elevon-flutter chain for aero_max (G7) | CAD mass properties (Fusion 360, P2); measured AERO coupon E/G; flight | F2 (P1/P2); F4 (S3/S4/S7); first material experiment |

---

## 2. What is NOT expected to change

- Wingspan 1300 mm, S = 0.282 m², AR 6.0 (ADR-0004, ADR-0010 — branch A is material-forced)
- t/c 13.5 % / 9 % (ADR-0027 — one of the best-supported decisions)
- Sweep Λ_c/4 = −20° (I-07 family alignment; ±2–4° adjustment is the compensation knob)
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
| 0.9 | 2026-08-06 | **OP-28 added** (material mass variants: `[E]` printed fractions → CAD; AERO divergence re-check; `docs/06-material-mass-variants.md`, `mass_budget.py`). |
| 0.8 | 2026-08-06 | **OP-27 added** (dowel-pin fit tolerance, ADR-0039 — verification at the first print/M3 assembly). |
| 0.7 | 2026-08-06 | **OP-22 closed** — all 14 missing ADR files published (0003, 0006, 0008, 0009, 0012, 0016, 0018, 0023, 0024, 0026, 0030, 0031, 0034, 0035) from their guide/justification values; OP-25 extended with the legacy DJI O3 Air Unit compatibility row (I-19 §2.4 `[M]`). |
| 0.6 | 2026-08-06 | **Dual directional configuration (ADR-0038, I-20):** OP-26 (fin variant verification) added — Mojito fin measurement, CORE S_fs from CAD, fin flutter/strength at ≈ 9 Hz (F4/S8), C16 with the fin mass at the OP-24 lever, E8 flight closure of G10; OP-24/OP-21 cross-referenced. Guide §5.4 defines the two published configurations (CLEAN / V1). |
| 0.5 | 2026-08-05 | Component catalogs integrated: OP-01/OP-19 numbers re-derived with FPV in the balance (pack ≈ −415, bay −516); OP-06 partial closure (hinge moment not binding, I-18); OP-18 catalog check (I-17); OP-24 updated (AUW 1697 → 46.1 km/h, three levers); OP-25 (FPV selection/integration) added; OP-16/OP-21/OP-23 refreshed. |
| 0.4 | 2026-08-05 | Bay re-derived with the I-16 pack envelope (6S1P 153.2 mm): 200×70×32, forward end ≈ −521, boom ≈ 390 mm; fit verdict: only 6S1P in the bay and in band; 4S1P outside (station); 4S2P/6S2P do not fit (I-16) — OP-23 sharpened; OP-01/OP-16/OP-19/OP-21 updated. |
| 0.3 | 2026-08-05 | OP-01 resolved by decision: nose boom adopted (bay x ≈ −493…−304, 6S1P pack ≈ −421 mm; `balance_cg.py`); pack-station map per config; OP-19/OP-16 updated to the boom; OP-23 (R-CG four-config tension) and OP-24 (boom mass/stall compliance) added; OP-02 updated with the elevon-reflex closure (≤ 0.6°) and R-TWIST 3.0°. |
| 0.2 | 2026-08-05 | OP-01 re-derived with corrected motor station (band ≈ −24…+9 mm, bay-limited); OP-04 defined piecewise (C22); OP-06 elevon span corrected to 30–90 % (C23); OP-19 fixed by the new CORE spec (§7.6 of the guide); OP-20 (wingtips), OP-21 (CORE outer mold), OP-22 (missing ADR files) added. I-09 additions: OP-10 hinge alternative (mylar). I-10…I-14 threads opened; OP-02 updated per C28 (MH 45 → MH 60-12 %); OP-06/OP-14 cross-referenced to I-10/I-13. |
| 0.1 | 2026-08-05 | First release. OP-01 (CG reachability) identified from a preliminary moment balance; all other open points carried from Phase 1 plan. |
