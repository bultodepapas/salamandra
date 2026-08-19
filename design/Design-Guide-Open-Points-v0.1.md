# Salamandra — Design Guide: Open Points and Evolution

**Version 0.18** · 18 August 2026 · **released with v0.5.0**, companion to
[`Salamandra-Design-Guide-v0.1.md`](Salamandra-Design-Guide-v0.1.md) (v0.23)

This document lists everything in the Design Guide that is **not yet fixed**: assumptions
that need verification, values that will change when the corresponding research closes,
and the revision process. It is the "what to watch" map for the designer and for Phase 1.

Every open point names the trigger that resolves it. Until a trigger fires, the released
v0.23 value stands; v0.4.0 remains the historical release snapshot.

---

## 1. Open points

### Critical

| # | Item | v0.4 value | What changes it | Trigger |
|---|---|---|---|---|
| **OP-01** | **CG reachability** | **Re-derived with the forward-centreline camera installation:** target CG −93.8 mm. CLEAN E01 solution −337.74 mm is inside travel −371.20…−336.10 mm. V1 requires −373.73 mm and clamps 2.53 mm short; xCG −93.08 mm remains inside band. Cradle inner section 68×25 mm; overall length 201 mm. | Real mass properties and central-body NP; recover or accept V1 station | F2/P1–P3; first-print balance |
| **OP-02** | **Measured airfoil acceptance** | **CAD coordinate closure complete (ADR-0041):** Salamandra r1, 13.5/9 % t/c, +1.0°/+0.5° added reflex. With ADR-0045 physical-surface effectiveness, neutral elevon is −0.14°/+0.50° at Ncrit 10/12 and 3.0° wash-in. | Printed-section/flight polar, hinge-gap loss, drag and stall progression may revise exposed profile/twist/control parameters | **E2**; computational/CAD part closed |

### Geometry and stability

| # | Item | v0.4 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-03 | Twist ε | **CLOSED FOR CAD:** +3.0° printed wash-in; selected r1/elevon model needs −0.14°…+0.50° neutral elevon over Ncrit 10–12 at the V1 lower mass | E2 may refine the exposed parameter before production | ADR-0041/0045 / E2 |
| OP-04 | Dihedral Γ | 2.0° total, piecewise-polyhedral (kinks at y = 195/347/498; 0 / 1.07 / 1.53 / 2.0°) | Roll-stability verification; may be revised by the stability analysis | Phase 1 stability (C-series), first flights |
| OP-05 | Neutral point | **25.72 % MAC / −75.8 mm** `[D]` (32×5 VLM); Weissinger-L **27.0 % / −72.9 mm**, 2.9 mm difference (I-21) | Central-body model and measured balance/flight NP | C2 body model; E-series |
| OP-06 | Elevon span / travel | **ADR-0045 CAD baseline:** 227.5–585 mm (35–90 %), 357.5 mm, 0.28 c, servo y ±406.25. Rigid VLM retains 94.5 % roll derivative, gives +0.001828 Cm/physical deg and +0.500° limiting trim. Hinge proxy −11.7 %; DS-939MG factored margin 1.52× at 180 km/h. ±20° is only a mechanical envelope; no flap mode/final throw is released. | Measured authority/stall, hinge-gap loss, servo stiffness/freeplay and G7 modal response | I-27; E2 / E5 / G7 |
| OP-07 | Hinge line x/c | 0.72 | Fixed by structure (ADR-0002); keep unless section is redesigned | — |

### Structure and materials

| # | Item | v0.4 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-08 | Carbon tube Ø12×1.0 | Provisional (bending only) | Real GJ/EI verification on the section; final sizing | S3/F4 (G4 closure) |
| OP-09 | D-box web at x/c 0.30 | Provisional | Section optimization (cell layout) | S3 |
| OP-10 | TPU hinge stiffness | TPU-printed (baseline) or mylar tape 25×30 (I-09); characterized later | K_hinge enters ω_β (flutter); can be off by factor 3 | C7/S6 (G7) |
| OP-11 | Printing temperatures | 240–250 °C nozzle / 70–80 °C bed | First test prints | First real part |

### Propulsion

| # | Item | v0.4 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-12 | Motor | 28-class 500–550 Kv, **6S only**; two-servo O1-boundary 8,484 rpm is 69–76 % of no-load. 4S needs a separate ~717 Kv module. | D2 measured efficiency/current/thermal map | ADR-0042; D2/E3 |
| OP-13 | Propeller / aircraft match | APC-E 8×8 O1 boundary **J 0.918 / 8,484 rpm / maximum drag 2.12 N**, not J_opt and not a predicted equilibrium. E2 must supply aircraft drag. | E2 drag polar; D2 thrust/RPM map; E3 energy | ADR-0042/C29; D2/E3 |
| OP-14 | Pusher vs twin tractor | Single pusher (disputed ADR-0006) | Comparative wake data at Re 4×10⁵; literature bounds | G5; thread I-13 |
| OP-15 | Thrust angle | 0.8° up (Peregrine precedent) | Flight trimming | First flights, E7 |

### Systems and integration

| # | Item | v0.4 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-16 | Battery carrier (cradle) | Printed 2 halves, **201 mm overall**, inner cross-section **68×25 mm**, 6S1P P42A E01 envelope 153.0×65.7×22.6 mm; CLEAN centre −337.74 mm, V1 required −373.73 mm versus −371.20 mm stop; Ø8.2 channel gripping the boom | R-CG verification and V1 travel recovery in CAD with real packs | F2/P3 |
| OP-17 | Pitot probe position | y ≈ 260 mm LE; lines cross the CORE↔PANEL joint (dedicated channel) | Install/test convenience | D1/D2 |
| OP-18 | FC pitot input | SpeedyBee F405 WING (not MINI) must be verified. **I-17 catalog check (v0.5):** the F405-WING-V2 and SpeedyBee F405 WING meet the full requirement set (I2C for the MS4525 pitot included); H7A3-WING excluded (no INAV target) | Bench check before buying | D1 |
| OP-19 | Cradle position (nose) | Forward plane x = **−452.70 mm**, CORE support x ≈ −132, 320.7 mm span + 50 mm insertion; pack between supports; E18 lens face is flush with the forward plane | OP-01 final validation | F2 |
| **OP-23** | **Battery variants** | **CLOSED for Article #1:** 6S1P only. O2 now means separate 4S/6S platform power modules; 4S needs ~713 Kv at the current boundary and a different carrier/CG solution; 2P needs another outer carrier. | Each future module must close its own propulsion, fit and CG chain | ADR-0042; future variant ADR |
| **OP-24** | **Measured mass acceptance** | ADR-0045 baseline: CLEAN **1553.25 g / 44.1 km/h**; V1 allocation 1589.97 g and connected lower model **1596.05 g / 44.7 km/h** including the complete 42.80 g fin. Analytical margin to the exact C16 ceiling is about 24.4 g. Only 6 g balance saving is credited; fixed bridge PETG remains in the shell. | CAD mass properties and complete-aircraft scale measurement; reject V1 >1620.4 g unless E2 re-derives CLmax | F2/P3; first complete assembly |
| **OP-25** | **FPV system selection / integration** | DJI O4 series reference (I-19 `[M]`): Article #1 camera 13.44×12.36×16.50 in the nose boom; 30×30×6 VTX in the CORE with airflow; attached antenna mass lumped into E19 and 80 mm route retained. Power: Pro on the 9 V/2 A rail (≥13.5 W), Article #1 O4 Air Unit on 5 V. Including two-servo avionics and 90 % BEC: Pro **16.48 W battery / 18.2 % pack·h⁻¹**; Article #1 **11.54 W / 12.7 % pack·h⁻¹**. **Legacy O3 Air Unit (I-19 §2.4 `[M]`)** requires its own camera-mount and power checks. | Camera FOV/lens for the mission, CE legal power, real current measurement | D-series bench; O1 energy re-check |
| **OP-26** | **Fin variant V1 verification (ADR-0038, I-20)** | V1a **2.12 dm²**, 252/105/63 mm; V1b **2.82 dm²**, 291/121/73 mm. Root **3.0 mm solid** gives FS 1.68 without spar credit; mode ≈8.0 Hz. Ø3 mm Al LE spar retained. C32 complete lower mass 42.80 g exceeds its 36.72 g allocation by 6.08 g. V1a lower uncertainty corner is slightly negative; V1b stays positive. | CAD side area, fin flutter/wake test, **mass reduction/compensation**, E8 yaw perturbation/full modal identification | F2/F4-S8; E8 |

### Added in v0.2

| # | Item | v0.4 value | What changes it | Trigger |
|---|---|---|---|---|
| **OP-20** | Wing tips | Flat end caps at y = ±650, no winglet | Winglet option (drag/recovery); not required for the O1 cruise claim | First flights, F3 polar |
| **OP-21** | CORE outer mold | Nose/lens plane x = **−452.70**, E18 camera centre x = −445.98 on y = 0 and looking along −x, cradle envelope controlled by E01, rear pod to +265 with belly ≤ −111.6 at the prop plane; body shape and coax connector routing remain open | Real CORE geometry + mass | F2 (P1–P3) |
| **OP-22** | Missing ADR files | **RESOLVED (2026-08-06):** all 14 pending ADR files (0003, 0006, 0008, 0009, 0012, 0016, 0018, 0023, 0024, 0026, 0030, 0031, 0034, 0035) published from their guide/justification values; index updated | — | ✅ Closed |
| **OP-27** | **Dowel-pin fit tolerance (ADR-0039)** | Holes Ø1.8–1.9 mm printed in both mating faces (solid collar Ø8×4); sliding fit across two parts depends on printer tolerance (±0.1–0.2 mm) | First-print verification: dowel must slide into both faces with light friction after glue application | M3 assembly step (F6), first print of the segments |
| **OP-28** | **Printed-part mass fractions and material variants (docs/06)** | Article #1 binding PETG shell cap **550 g**; hybrid boom correctly fixed outside material scaling. AERO WINGS saves 162.6 g but released-r1 conservative **Vdiv = 91.6 km/h**, below 95 km/h cruise: **not cleared for flight**. | CAD mass properties; measured AERO E/G; new structural concept if pursued | F2 P1/P2; F4 S3/S4/S7 |
| **OP-29** | **Absolute divergence margin (docs/07 rev. 4, G6)** | At −15° with released r1 root: nominal **327.2 km/h** (1.36× PASS), conservative unmeasured **129.6 km/h** (0.54× FAIL), AERO **91.6 km/h**. GXY-plane case 180.0; GXY+gyroid+1.1 mm wall 207, still below 240. Initial **Vlimit remains 105 km/h**; **150** only after S3 validates GXY. | Real GJ, elastic axis, printed GXY and E7 Southwell | F4 S3/S4; I-21; E7 |
| **OP-30** | **Elastic-axis location** | xEA/c bracket **0.30…0.45 `[E]`**, nominal 0.35. The old x/c = 0.353 enclosed-area centroid is a geometry diagnostic, **not a shear centre**. | Representative-section no-twist load test or validated shell FE model including wall stiffness and cells | S3 before raising Vlimit; E7 correlation |
| **OP-31** | **Dynamic gust envelope and negative CLmin** | C33/I-24 closes terminology and the positive manoeuvre branch: +6/−3 g limit, +9/−4.5 ultimate, VA 109.0/110.4 km/h CLEAN/V1. The legacy rigid gust result exceeds the linear/stall domain and is retained only as a screen; inverse −3 threshold at 105 km/h is 5.10/5.19 m/s. | Nonlinear unsteady model with plunge/flexibility/spanwise gust plus validated negative-polar `CLmin` and measured `n_z(V)` | G11; B3 negative-polar extension/E9; F4/S1–S3 |

---

## 2. What is NOT expected to change

- Wingspan 1300 mm, S = 0.282 m², AR 6.0 (ADR-0004, ADR-0010 — branch A is material-forced)
- t/c 13.5 % / 9 % (ADR-0027 — one of the best-supported decisions)
- Forward-swept configuration (ADR-0001); current Λ_c/4 = **−15°** per ADR-0040 and is reviewed only on its declared trim/NP/GJ triggers
- Skin 0.9 mm / gyroid 5 % (ADR-0028), three-cell section (ADR-0002)
- Elevon mass balancing (ADR-0025 — non-negotiable), one actuator per elevon (ADR-0026)
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
| 0.18 | 2026-08-18 | **Released with v0.5.0 / guide v0.23.** The open-gate state is unchanged by the release: the ADR-0046 declaration contract, the C39–C43 corrections and the drawing set are traceability and verification work, not new evidence. OP-06 elevon geometry is now released rather than working; G7 flutter remains open **without** the withdrawn `sqrt(2)` two-servo stiffness credit; G10 yaw is republished at the single-source inertia (ω_n 5.35 rad/s, ζ 0.231) and stays damped across the whole declared band; E2, F2, S3, G6, G11, D2/E3 and OP-21 are untouched. |
| 0.17 | 2026-08-18 | Guide v0.22/I-27/ADR-0045 propagated: OP-06 adopts the 35–90 % elevon as the working CAD baseline while retaining E2/E5/G7; OP-01/16 expose the 2.72 mm V1 battery-station shortfall; OP-24 credits only the 6 g balance reduction. No flap mode, final throw or flutter closure is claimed. |
| 0.16 | 2026-08-17 | **Released with v0.4.0 / guide v0.21.** The open-gate state is intentionally unchanged: OP-31/G11/E9 still require dynamic gust and negative-`CLmin` evidence, while F2, E2 and S3 retain the mass, aerodynamic and structural physical acceptance work. |
| 0.15 | 2026-08-17 | Guide v0.20/I-24 propagated: C33 separates manoeuvre limit from ultimate load, adds positive V-n/VA results and OP-31 for the dynamic gust and negative-CL closure; C34 distinguishes local section `clmax` from wing `CLmax`. No false gust load or CAD change is adopted. |
| 0.14 | 2026-08-17 | Guide v0.19/I-23 propagated: C29–C32 correct power, servo, yaw and complete-fin mass chains; OP-24 reopens V1 because its 1626.5 g lower model exceeds the 1620.2 g allocation target. |
| 0.13 | 2026-08-17 | **Released with v0.3.0 / guide v0.18.** OP-02/03 close computationally on Salamandra r1; OP-12/13 use the aircraft-equilibrium propeller point; OP-23 closes Article #1 at 6S1P; OP-24 becomes a measured acceptance gate against the 1583.5/1620.2 g allocation. |
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
