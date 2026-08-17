# Changelog

Continues the project's correction log. **Errors are documented because they affected intermediate conclusions.** The error history is part of the product: it is what allows trust in what remains standing.

---

## [1.28] — 2026-08-17

**Highest-ROI design audit — coupled sweep selection, canonical geometry and corrected
elastic-axis uncertainty.**

- **ADR-0040 / I-21:** full −20/−16/−15/−12/−10° trade using 32×5 VLM,
  100-station Weissinger, trim/reflex, section-Cl, self-consistent balance and the NASA
  TP-1685 divergence trend. **−15° selected**; −12° rejected because it requires 4.54°
  equivalent trim against the 3.0° twist + 0.6° reflex cap.
- **Single geometry source:** `calculations/design_config.py` now owns b, S, taper,
  sweep, thickness and stations. Guide v0.16 receives the generated −15° station table.
  **Correction:** v0.15 gave mutually inconsistent tip trailing-edge values (−128.1 in
  the station table and +108.5 in the CAD controls); the correct −15° value is −65.7 mm.
- **Aeroelastic correction:** the enclosed-area centroid x/c = 0.353 was incorrectly
  called the shear centre in revision 2. It is only a geometric diagnostic. Revision 3
  brackets xEA/c = 0.30…0.45 `[E]`: Vdiv 325.3 nominal / **128.8 conservative** /
  91.1 AERO; initial **Vlimit 105 km/h**, 150 only after GXY validation. The shell-alone
  240 km/h claim in ADR-0030 remains unproven.
- **Balance/mass correction:** target CG −93.8 mm; 6S1P P42A at −372.7 mm; cradle
  −473.3…−272.2; hybrid boom 38.2 g; AUW 1685.2 g. The aluminium boom is now a fixed
  hybrid row in `mass_budget.py`, so printed-material policies no longer scale its mass.
- **Yaw/structure correction:** the fin sizing block calculated 2.16 dm² but downstream
  checks still used a stale fixed 2.0 dm². All blocks now consume the calculated area;
  the 2.5 mm solid root is rejected at FS 1.15 and the baseline becomes **3.0 mm**
  (FS 1.65). The Ø3 mm spar is retained for stiffness but receives no strength credit.
- **Elevon-authority correction:** the script reported the current VLM wash-in yield
  (+0.00249/°) but still calculated trim with a stale +0.00338/°. It now uses its own
  computed yield: the favourable provisional polar closes at about **0.6°** reflex,
  while the adverse Ncrit-12 polar needs about **1.9°** and therefore fails the
  permanent-reflex cap. Control authority passes; the final B3 polar is a CAD gate.
- Documents updated: guide v0.16, justification v0.11, open points v0.11 (OP-30 added),
  docs/06 rev. 1.1, docs/07 rev. 3, README and calculation index.

---

## [1.27] — 2026-08-06

**First release — tag `v0.1.0`: Salamandra Design Package (CAD baseline).**

- Guide **v0.15** released (status RELEASED, tag v0.1.0): segment spans added (§6.5,
  C24); new §6.9 bought-in items and consumables table; open items named with their
  triggers (OP-02 airfoil, OP-21 CORE shape).
- **`docs/08-release-v0.1.md`** (new): release notes — package contents, verification
  status (all 16 scripts ALL PASS), frozen vs open items, binding constraints for the
  designer and the build, working and feedback flow.
- Indexes: `docs/README.md` row for docs/08; README release pointer.
- **Corrections:** none — release of the v0.14/v0.15 state with documentation only.

---

## [1.26] — 2026-08-06

**Design guide reorganized as a CAD designer's guide — v0.14 (structure only, no engineering change).**

- **Guide structure** re-ordered for the designer's workflow: §4 reference planform →
  §5 airfoil → §6 structure and parts (with a new **component map** listing the 11 parts
  to model: CORE, 6 segments, 2 elevons, fin, cradle, skid, balance tabs) → §7 mass/CG →
  §8 battery and cradle → §9 propulsion → §10 avionics → §11 flight envelope (stall,
  divergence/V_limit, launch consolidated from old §4) → §12 assembly → §13 references →
  §14 log. CAD method promoted to §6.8.
- **Analysis moved out, nothing lost:** long blockquotes compressed to one-line flags;
  the full rationale remains in `Design-Guide-Justification-v0.1.md` (v0.10: twist
  working-value row, cradle row §9, boom row §6, straight-channel row §5, divergence row
  §8) and the CHANGELOG. Historical bay sizing kept in justification §9 as the
  fit-analysis basis.
- **Values reconciled to the canonical scripts** (no silent changes, corrections listed):
  twist working value **+0.5° → +3.0°** (parametric, C5; target 0.5° with the designed
  section); divergence numbers updated to docs/07 rev. 2 (**275.6 / 151.5 / 107.1**,
  V_limit 110 — the guide's v0.10-era 267.7/121.9 were stale); battery **bay → cradle**
  throughout (§8, assembly step 8 verifies 6S1P only); AUW summary row reconciled
  (1697 current / 1620 design ref.); guide §14 log compacted with CHANGELOG mapping.
- Documents: guide **v0.14**, justification **v0.10**, open-points **v0.10** (OP-01/03/16/
  19/21/23 reworded to the cradle). **Corrections:** stale divergence numbers; stale
  twist value; bay-vs-cradle contradiction; 4S2P balance-verification step.

---

## [1.25] — 2026-08-06

**CAD questions Q1–Q5 answered — guide v0.13 (modelable as-is).**

The 5 questions a CAD designer would raise are now resolved in the guide:

- **Q1 — Cradle replaces the battery bay:** printed cradle (2 halves, 155×66×24 mm inner, ≤ 15 g, Ø8.2 channel gripping the tube, 2× velcro + spring-lock hatch) replaces the internal 200×70×32 bay; pack centred at x ≈ −415 between the two supports; CORE has no bay; boom socket Ø8.2 at z = 0 with a 4-perimeter collar (§7.6).
- **Q2 — Tube/pin channels vs dihedral kinks (`[D]`, `boom_flexion.py` §6):** straight bores Ø12.4–12.6 / Ø6.3–6.5 per flat segment; the kinks (max 1.07°) deviate the tube ≤ 0.19 mm across the joint face — inside the 0.30 mm radial clearance; even forced, the elastic bend is σ 34 MPa (CFRP ~1600) (§7.3).
- **Q3 — Elevon as a separate part:** TPU hinge strip 4×6 mm × 390 mm glued in a 4.2×6.2 groove; balance pocket 40×14×12 mm at x/c 0.74, lid 1× M2, 40 g capacity; the lead amount (not the geometry) closes the ADR-0025 balance in CAD (§7.5).
- **Q4 — Fin section:** symmetric biconvex plate, 2.5 → 1.5 mm, LE r 1.5 / TE 0.8 mm, Ø3 spar in a Ø3.2 LE channel, slot + dowel + M2 mount (§5.4).
- **Q5 — CAD method declared:** solid bodies; slicer makes skin 0.9 + gyroid 5 %; web, channels, collars, cavities, sockets modelled explicitly; CORE torsion box closed to the TE; print orientation is a slicer task.
- Documents: guide **v0.13** (§5.4/§7.2/§7.3/§7.5/§7.6 + CAD-method note), `boom_flexion.py` §6 (kink check, 13 validations ALL PASS). **Corrections:** the internal battery bay is superseded by the cradle (prototype decision, no analysis depended on it).

---

## [1.24] — 2026-08-06

**PROTOTYPE 0.1 materials decided (user): aluminium nose boom Ø8/int6 + Ø3 aft spar — `boom_flexion.py`.**

- **Nose boom = aluminium tube Ø8 / int Ø6 (wall 1.0 mm, measured) + printed cradle (15 g):** the structural analysis found and resolved the governing trap — the tube **cannot cantilever** the 455 g pack (+6 g: σ 322 MPa > 276 yield, δ 57 mm, 5.2 Hz), but the existing geometry (pack centred x −415 between the tip support −516 and the CORE −132) is exactly a **two-support beam: σ 60 MPa (FS 4.6), δ 2.0 mm, mode 21 Hz — PASS** (`boom_flexion.py`, 11 validations ALL PASS). The cradle is a structural requirement; the tip skid is the crush zone.
- **Boom mass ≈ 41 g** (tube 25.8 + cradle 15) — OP-24 target 40 + 2 absorbed (V_stall +0.03 km/h).
- **Ø3 mm aluminium spar along the V1 fin leading edge** (aft, near the TE): root stiffness ×2.05 (EI 0.278 + 0.265 N·m²), 5.7 g, load path vs slipstream buffeting (OP-26).
- **Carbon optimisation deferred** (documented pending, ADR-0015 revision).
- Documents: guide **v0.12** (§7.6 nose boom, §7.2 fin mount, §8.1 table), OP-24/OP-26 updated, mass_budget boom 41 g, calculations/README §16. **Corrections:** none.

---

## [1.23] — 2026-08-06

**Divergence model refined: real profile geometry + literature sensitivity (docs/07 rev. 2).**

Designer's empirical report (printed PETG thin-wall/low-infill parts feel stiffer than
simple calculations) investigated and quantified:

- **Real geometry:** `divergence.py` now computes the torsion box from the actual
  profile coordinates (`geometry/airfoils/mh60-135.dat`): A1 = 0.0310c², A2 = 0.0415c²,
  real arc perimeters, shear centre x/c = 0.353 (e = 0.103c). The k_h = 0.8 rectangle
  idealization validates within 0.4 % (validated as a check). 14 validations ALL PASS,
  C2 cross-check 0.07 %.
- **Results (real geometry):** nominal 275.6 km/h (1.15×), conservative end 151.5 km/h
  (0.63× — FAIL, below V_NE 160), optimistic 521 km/h, AERO 107.1 km/h (not airworthy).
- **Literature sensitivity (docs/07 §4):** in-plane G_XY ≈ 0.69–0.72 GPa from E–ν
  (Özen 2021, CNC Kitchen E 1.9 GPa; Sadaghian 2022's ~0.24 GPa applies to across-layer
  loading, not the wing's in-plane skin path) moves the conservative end to 210 km/h
  (+39 %); gyroid 5 % and real wall 1.0–1.1 mm add ~5–10 % each. **Combined best case:
  242 km/h — touches the criterion but does not guarantee it.** The dominant unresolved
  term remains the sweep factor 0.50–0.70 `[E]` (I-12).
- **S3 expectation declared:** printed torsion coupon should measure G_XY ≈ 0.65–0.72
  GPa → V_div ≈ 200–240 km/h; V_limit 110 km/h for the first flights, raisable to
  ≈ 160 km/h if the coupon confirms the in-plane G.
- Documents: docs/07 rev. 2 (model table, results, §4 sensitivity, S3 expectation).
  **Corrections:** none — the verdict is unchanged, its band is now quantified with
  real geometry and literature.

---

## [1.22] — 2026-08-06

**Launch verdict CORRECTED (I-14 rev. 2) — hand launch IS feasible.**

Designer review challenged the rev-1 verdict ("cannot leave the hand"): the model was
too strict in two respects, now corrected with data:

- **(a) Release gate corrected:** rev. 1 demanded k_safe = 1.20 at the release instant
  (15.3 m/s). The correct gate is **V_suelta ≥ V_stall (12.8 m/s)** — the margin is
  built by motor acceleration at T/W ≈ 1.0 in 0.2–0.4 s.
- **(b) Thrust/throw data corrected:** published throwing biomechanics (van den
  Tillaar, JSSM 2004: 0.409 kg → 21.5 m/s, significant negative linear mass–velocity
  relation → 1.6–1.7 kg band 8–13 m/s, ref 10.5) and the full throw gesture (0.4–0.6 s)
  with the motor at wing-throw idle (0.5–0.67 × hover) add 2–4 m/s.
- **Configuration-class anchor `[M]`:** the TBS Mojito — 1300 mm, ≈ 1800 g, higher
  reported stall (~60 km/h) — is hand-launched in service (TBS manual + community:
  idle 1300 + launch 1850, over-head technique). The Salamandra is the easier case.
- **New verdict:** typical throw = **13.4 m/s (48.4 km/h, k = 1.05) at release, k = 1.20
  in 0.39 s; firm throw = 17.3 m/s (62.4 km/h, k = 1.36)**; weak throw stays below
  stall → technique rule (firm throw ≥ 10 m/s, 0–5° pitch) is part of the spec.
  Torque-roll check: launch T/W ≈ 1.0 inside the community 1.5 threshold.
- Documents: I-14 rev. 2 (correction record), guide **v0.11** (§4/§12), calculations
  README §15. **Corrections:** rev-1 launch verdict (too strict gate + low thrust
  estimate); the divergence findings (docs/07) are untouched.

---

## [1.21] — 2026-08-06

**I-14 executed — hand-launch feasibility quantified (`launch_speed.py`, guide v0.10 §4/§12).**

The open thread that had zero data now closes with the quantitative envelope:

- **A typical throw releases the aircraft BELOW its own stall speed: 44.5 km/h vs 45.9 km/h (1687 g).** Best case (hard throw 12 m/s + high idle throttle) = 14.9 m/s — **0.4 m/s short of k_safe = 1.20** (55.1 km/h). Danger window ≈ 0.8 s (200 ms motor delay + acceleration at hover throttle).
- **Official autolaunch data integrated `[D]`:** INAV guide (Hoffmann): `nav_fw_launch_thr` = hover throttle (T/W ≈ 1.0 → 16.5 N), idle 0.5–0.67 ×, motor delay 200 ms, spinup 200 ms (8-in prop), climb 18–25°; ArduPlane: `TKOFF_THR_MINACC` 15 m/s², delay ≥ 0.2 s, minspd 4 m/s, **release at 0–5° pitch** (higher → stall).
- **Envelope declared:** release ≥ 1.20 × V_stall at 0–5° pitch, hard throw + high idle; launch lever: CL_max chain (R-AIRFOIL) is now double-critical (lowers V_stall AND raises the release margin).
- Documents: research/I-14 executed, guide **v0.10** (§4 launch envelope, §12 autolaunch settings, §13 refs), calculations/README §15, I-14 §3.2 settings table for D1/D2. **Corrections:** none.

---

## [1.20] — 2026-08-06

**Absolute divergence speed computed (G6 first pass) — `calculations/divergence.py` + `docs/07`. Criterion FALSIFIED at nominal and conservative ends.**

The ADR-0030 claim "V_div ≥ 1.5 × V_NE met with the shell alone" had no calculation behind it (I-05 gave only the relative Peregrine anchor, 1.14×). New absolute estimate:

- **Nominal: 267.7 km/h — margin 1.12× (barely PASS). Conservative end (G −35 %, a 11.2, k_sweep 0.50): 121.9 km/h — 0.51× — FAIL, below V_NE 160 km/h.** Optimistic end: 664 km/h.
- **AERO LW-PLA wings: 86.2 km/h — below the 95 km/h design cruise: NOT airworthy under this model** (OP-28 confirmed with numbers).
- R-JOINT penalty at 5× = **−12 %** on the real wing (lumped table −9 % slightly optimistic); tube Ø12 fully bonded = **+7 % max** ("bending only" quantified, holds).
- **Method bug caught by C2:** a first shooting implementation (θ′ continuity) converged to the WRONG equation (drops GJ′·θ′; 3× error on the tapered wing). Flux-form shooting agrees with the FEM weak form to **0.06 %**. Recorded in the validation discipline.
- **Action:** declared **V_limit 110 km/h** for the first test flights; S3 (real section GJ in Fusion 360) + I-12 (sweep factor) + E7 (Southwell) are the closers; 3 perimeters (+22 % V_div, +200 g) is the structural option.
- Documents: `docs/07-divergence-margin.md` (new), open points **OP-29 added**, OP-28 updated with numbers, calculations/README §14, docs/README index. **Corrections:** none — a falsified claim replaced by a calculated band.

---

## [1.19] — 2026-08-06

**Material mass variants tool (F2-class) — `mass_budget.py` + `docs/06`.**

New data-driven weight calculator with per-part material selection: **ALL PETG**
(baseline), **AERO WINGS / AERO MAX** (LW-PLA wings/tips ± elevons), **PLA+** (rejected
material, computed for completeness), or arbitrary per-part assignment. Options:
battery 4S1P/6S1P/4S2P/6S2P × Molicel P42A/Samsung 50E (I-16 `[D]` model), FC catalog
(I-17 `[M]`, 8.4–26 g), FPV O4/Pro/Lite/O3 (I-19 `[M]`), motor/prop/servo class, V1 fin
(ADR-0038). Twelve validation cases, ALL PASS.

- **Baseline refinement (−10 g):** the script uses the I-16 `[D]` pack mass 445 g
  (validated vs the measured packs) instead of the guide §8.1 `[E]` 455 g → 1687 g /
  45.9 km/h vs 1697 / 46.1. The OP-24 stall tension holds in both; the guide's figures
  remain the conservative published values.
- **Results (6S1P P42A, O4 Pro, CLEAN):** ALL PETG 1687 g / 45.9 km/h · **AERO WINGS
  1508 g / 43.4 (stall-compliant, −179 g)** · AERO MAX 1457 g / 42.7 · PLA+ 1670 g.
- **Engineering flags:** AERO wings are E ≈ 0.5× PETG → divergence/torsion re-check
  required before airworthiness (OP-28, F4/S3–S4); AERO needs flow 0.60 (never 0.95);
  elevon balance mass derived from elevon mass (ADR-0025); PLA+ stays rejected
  (ADR-0016).
- Documents: `docs/06-material-mass-variants.md` (new), guide **v0.9** (§8.1 note),
  open-points v0.9 (OP-28), calculations/README §13, docs/README index.
  **Corrections:** none (refinement, not overturn).

---

## [1.18] — 2026-08-06

**Filament dowel pins adopted in the glued segment joints (ADR-0039).**

Community proposal (refined after the §1.17 trade): filament pins are NOT a carbon
replacement — they are **alignment/shear dowels in the glued joints**. New tool
`filament_dowel_pins.py` (six validation cases, ALL PASS):

- **Spec:** 2 × Ø1.75 mm filament (PETG scraps preferred) per glued segment joint
  (y = 347/498, 8 dowels/aircraft); holes Ø1.8–1.9 mm at x/c 0.40/0.60 with solid
  collars Ø8 × 4 mm; adhesive dab on one side; length 20–22 mm.
- **Shear redundancy:** demand at +6 g V_NE ≈ 27 N (y=347) / 12 N (y=498) `[E]` vs
  2-dowel double-shear capacity ≈ 293 N → **FS ≈ 11 / 24** `[D]`.
- **Alignment** (primary function, `[I]`): prevents shear slip during glue cure —
  alignment IS strength; zero cost (scraps), 2.6 g/aircraft.
- **Boundary declared:** the CORE↔PANEL torque couple keeps the carbon Ø6 pin
  (§1.17); the ADR-0023 bond-area rule is unchanged (dowels are additive).

Documents: ADR-0039 (new), guide **v0.8** (§7.3 spec, §7.4 print row, §5.4 fin-root
dowel, §12 assembly, §13, §14), justification/open-points v0.8 (OP-27: first-print fit
verification), calculations/README §12, decisions index. **Corrections:** none.

---

**R-JOINT pin material trade — filament proposal evaluated and rejected with numbers.**

Community proposal: replace the carbon Ø6 anti-rotation pin with pieces of 3D-printer
filament (PETG/PLA Ø1.75). New tool `joint_pin_trade.py` (five validation cases, ALL
PASS) shows:

- **Strength passes** (not the binding requirement): couple force F = T/arm =
  2.3–15.4 N `[E]` → shear FS ≈ 4.7 (PETG) / 6.3 (PLA); bearing ≈ 5 MPa.
- **Stiffness fails by ≈ 9000×**: E·I carbon Ø6 = 7.63 N·m² vs PETG filament
  Ø1.75 = 0.0009 N·m². With identical sockets/arm/loads, k_joint ∝ E·I → R-JOINT
  collapses from ≥ 5× to ≈ 0.005× the section → **−29 % V_div** (ADR-0032 table) on a
  forward-swept wing whose dominant risk is aeroelastic divergence (I-05).
- Printed-PETG alternatives: tenon Ø8 → 5 %, Ø10 → 12 %, Ø17 → parity (≈ 40 g vs
  6.3 g) — worse than carbon on every axis.
- Cost/complexity: carbon ≈ €0.25–0.50 per pin, 6.3 g; the socket (bore, embedment,
  sliding fit) is identical for any pin — filament saves ≈ €1/aircraft, no complexity
  change. **Verdict: −29 % divergence margin is not purchasable for €0.5.**

Documents: ADR-0031 (trade-study section added), guide §7.3 (pin material fixed,
with reference), calculations/README §11. **Corrections:** none (proposal evaluated,
no datum overturned).

---

**Catalog audit — everything integrated, two gaps closed (O3 + 14 missing ADR files).**

### Audit result (batteries / FC / servos / FPV)
Verified in the design guide: **batteries** (I-16: bay 200×70×32 mm, pack 6S1P
153.2×64.5×22.2 mm, energy 90.7/108 Wh — §7.6/§8.1/§9/§10.1), **FC** (I-17: station
cavity 64×45×21 mm, 30.5×30.5 boss, F405-WING-V2/SpeedyBee reference, exclusions —
§7.6/§11), **servos** (I-18: class 12–15 g, cavity 34×16×39 mm, current 1.2–2.8/5–9 A —
§7.5/§8.1/§11), **FPV O4 series** (I-19: camera 25.55×20×23.30 / Lite 13.44×12.36×16.50,
VTX 33.5×33.5×13 / Lite 30×30×6, power rails — §7.6/§8.1/§11). **All integrated.**

### Gap closed 1 — DJI O3 Air Unit (legacy) `[M]`
Not previously cataloged. Added to **I-19 §2.4** with DJI official data (module
32.5×30.5×14.5 mm, camera 21.2×20×19.5 mm, 36.4 g, 7.4–26.4 V, coax 115 mm): fits the
Salamandra mounts (camera inside the O4 cavity, module on the O4 tray); declared
verifications pending (camera hole spacing, measured current). Guide §7.6/§8.1/§11 and
OP-25 updated. O4 series remains the reference.

### Gap closed 2 — OP-22: all 14 missing ADR files published
ADR-0003 (wash-in twist), 0006 (single pusher, ⚠️ dispute), 0008 (reject 7×12), 0009
(drag decomposition), 0012 (light color), 0016 (reject PLA+), 0018 (reject ABS), 0023
(joint adhesive), 0024 (segmentation), 0026 (dual actuation), 0030 (plastic torsion
path), 0031 (carbon pin), 0034 (motor mount angle), 0035 (TPU hinges) — written from
their guide/justification values with tags; decisions index linked; OP-22 **closed**;
guide §13 note updated (all ADRs published).

### Versioning
Design guide **v0.7** (O3 + ADR publication; §14), justification/open-points v0.7.

### Corrections
None (catalog extension and file publication; no overturned datum).

---

## [1.17] — 2026-08-06

**R-JOINT pin material trade — filament proposal evaluated and rejected with numbers.**

Community proposal: replace the carbon Ø6 anti-rotation pin with pieces of 3D-printer
filament (PETG/PLA Ø1.75). New tool `joint_pin_trade.py` (five validation cases, ALL
PASS) shows:

- **Strength passes** (not the binding requirement): couple force F = T/arm =
  2.3–15.4 N `[E]` → shear FS ≈ 4.7 (PETG) / 6.3 (PLA); bearing ≈ 5 MPa.
- **Stiffness fails by ≈ 9000×**: E·I carbon Ø6 = 7.63 N·m² vs PETG filament
  Ø1.75 = 0.0009 N·m². With identical sockets/arm/loads, k_joint ∝ E·I → R-JOINT
  collapses from ≥ 5× to ≈ 0.005× the section → **−29 % V_div** (ADR-0032 table) on a
  forward-swept wing whose dominant risk is aeroelastic divergence (I-05).
- Printed-PETG alternatives: tenon Ø8 → 5 %, Ø10 → 12 %, Ø17 → parity (≈ 40 g vs
  6.3 g) — worse than carbon on every axis.
- Cost/complexity: carbon ≈ €0.25–0.50 per pin, 6.3 g; the socket (bore, embedment,
  sliding fit) is identical for any pin — filament saves ≈ €1/aircraft, no complexity
  change. **Verdict: −29 % divergence margin is not purchasable for €0.5.**

Documents: ADR-0031 (trade-study section added), guide §7.3 (pin material fixed,
with reference), calculations/README §11. **Corrections:** none (proposal evaluated,
no datum overturned).

---

## [1.16] — 2026-08-06

**Catalog audit — everything integrated, two gaps closed (O3 + 14 missing ADR files).**## [1.15] — 2026-08-06

**Directional (yaw) stability quantified — dual configuration adopted (I-20, ADR-0038).**

### New analysis
- **`calculations/yaw_stability.py`** — Cnβ budget, fin sizing, rudder authority, yaw
  damping/subsidence, fin bending, drag/mass/stall cost. Six validation cases (Helmbold,
  fin reference, Raymer body, tier consistency, damping) — **all PASS**.
- **I-20 — directional stability thread** with primary-source evidence: the TBS Mojito
  (same FSW + nose + pusher class) carries a **fixed** vertical stabilizer and **no
  rudder servo** (product page, manual, official INAV CLI: `servo 1/2` elevons only,
  `fw_ff_roll 93` bank-to-turn) — `[M]`, new.

### Findings (honest, not silent)
- **The finless baseline is directionally unstable:** Cnβ = −0.0006…−0.0015/deg `[E]`
  (negative across the band — FSW wing sign + nose boom); yaw divergence τ ≈ 0.7 s.
  The guide's "no tail, no vertical stabilizer, no rudder" was an **assumption, not a
  calculation** — the same failure mode C6 corrected for pitch. Now quantified.
- **A movable rudder is rejected with numbers:** |Cnδr| ≈ 0.00043/deg cannot hold a
  20 km/h crosswind slip at stall (δr ≈ 24° > ±20°); differential elevons ≈ 1/5 of a
  rudder's authority; no mission need (bank-to-turn); no in-service precedent.
- **Cost of the fin:** V1a (2.1 dm²) 36–60 g, ΔCD0 +0.0014 → +9.6 % energy `[E]`
  (Wh/km ≈ 1.26 — still < the Mojito's 1.40 `[M]`); V_stall +0.6 km/h (OP-24 lever).

### Decisions and documents
- **ADR-0038 — dual directional configuration:** `SALAMANDRA-CLEAN` (finless, O1
  efficiency build) and `SALAMANDRA-V1` (fixed centreline fin — **first platform
  variant**, recommended for the Article #1 test programme). Fin = CORE component:
  no servo, no linkage, no FC change; panels untouched.
- **Design guide v0.6:** §5.4 (full variant spec: S_v 2.1/2.8 dm², b_v 250–290 mm,
  root t ≥ 2.5 mm, rear-pod extension ≈ 30 mm, fin AC ≈ +285), §7.6 fin-mount row,
  §4/§8.1 stall flags, §12 assembly step, §13 references.
- **Justification v0.6** (§11) and **Open Points v0.6** (OP-26 added).
- **docs/00 §3.6**, **docs/02 §3 (Mojito `[M]` register + R5 pending)**, **docs/03 C8**
  (directional budget + exit criterion), **docs/05 S8** (fin loads/flutter in F4),
  **tests/README E8** (yaw perturbation — the `[M]` closure of G10), **gaps G10**,
  **README** (status + article table + variants).
- **Corrections:** none (new analysis, no overturned datum). Mojito fin dimensions
  (R5) pending human measurement — the analysis model cannot process images.

---

## [1.14] — 2026-08-05

**Component catalogs integrated: batteries (I-16), FC (I-17), servos (I-18), FPV DJI O4 (I-19).**

### Integration
- **Mass balance re-run with the FPV unit** (`balance_cg.py` `[D]`): DJI O4/Pro
  (camera 16.4 g at the boom front ≈ −450, VTX 16.6 g at the avionics station, 2×
  antennas 4.2 g) → AUW **1697 g**; 6S1P pack station **−415 mm** (was −421), bay
  **−516…−315** (200 mm, was −521), boom ≈ 385 mm. The FPV camera in the boom helps the
  balance (≈ 4 mm forward).
- **Guide v0.5:** §7.5 servo class 12–15 g metal-gear (I-18), cavity 34×16×39 mm,
  hinge moment 10–48 mN·m/servo NOT binding (≥ 3.7× margin, `servo_torque.py`), current
  avg 1.2–2.8 A / peaks 5–9 A with capacitance guidance; §7.6 avionics station cavity
  64×45×21 + 30.5×30.5 boss (I-17), FPV camera mount (2× M2, 16 mm) and VTX tray with
  airflow (I-19); §8.1 FPV row 37 g `[M]`; §11 FC reference class (F405-WING-V2 /
  SpeedyBee; F411 no blackbox, Foxeer no current, H7A3 no INAV target), avionics
  6.6 W ≈ 6 % of cruise ≈ 7.3 % of pack per flight-hour, FPV power (Pro on the 9 V/2 A
  rail ≥ 13.5 W, NOT the 5 V rail; total electronics 17.0 W Pro = 18.8 %/h); §10.1
  battery energy reference 90.7 Wh P42A / 108 Wh 50E (I-16); §4 stall flag updated.
- **Open points v0.5:** OP-06 partial closure (torque not binding); OP-18 catalog check;
  OP-24 (three mass levers, AUW 1697 → 46.1 km/h, borderline); OP-25 (FPV selection)
  added.
- **I-18 collision fixed:** the DJI O4 catalog was numbered I-18 twice — the FPV system
  is now **I-19** (`git mv`, references updated in `research/README.md`,
  `calculations/README.md`, `fpv_power_budget.py`).

### Stall flag (honest, not silent)
AUW 1697 g → V_stall ≈ **46.1 km/h** vs ≤ 45 required. Levers: shell 550 g + boom
≤ 40 g + servos 48 g → ≈ 45.1 km/h — **borderline; F2 must arbitrate the mass budget
against C16 (OP-24).**
---

## [1.13] — 2026-08-05

**Bay re-derived with the real pack envelope (I-16).**

### Context
The parallel battery-pack analysis (I-16, `battery_pack_layout.py`) established the
finished pack envelopes with datasheet `[M]` + assembly allowances `[E]`: **6S1P =
153.2 × 64.5 × 22.2 mm** (2×3 cells, orientation A, leads included) and 4S1P =
153.2 × 43.2 × 22.2. The v0.3 bay sizing assumed an 84 mm pack — **corrected**.

### Corrected (`balance_cg.py`, all `[D]`)
- Bay: **200 × 70 × 32 mm**, forward end **x ≈ −521**, boom ≈ **390 mm** (was 190 mm /
  −493 / 360 mm). The 6S1P pack (153.2 mm) + 36.5 mm R-CG slide + 5 mm clearances
  require the 200 mm length.
- Fit verdict: **only 6S1P fits the single-layer bay and reaches its band
  (−439.5…−403)**; 4S1P fits physically but needs x ≈ −577 (outside the bay);
  **4S2P/6S2P fit no n_z = 1 arrangement of 8/12 cells (I-16)** — the earlier
  "also covers 4S2P" claim is withdrawn.
- OP-23 sharpened accordingly; the v0.4 bay serves the reference 6S1P only.

### Changed
- Design guide v0.4: §7.6 boom/bay rows, §8.2 OP-01 blockquote, §9 bay/configs rows,
  §14 log; justification §3.2 (table + adopted geometry + flag 1); open points v0.4
  (OP-01, OP-16, OP-19, OP-21, OP-23).

---

## [1.12] — 2026-08-05

**OP-01 resolved by decision (nose boom), R-TWIST raised to 3.0°, elevon authority verified.**

### New tools (both validated, all `[D]`)
- **`calculations/balance_cg.py`** — mass/CG balance with the pack-station solver.
  Self-consistency validation: numerical planform area centroid −48.9 mm vs the
  −49 mm assumed in the mass table (OK).
- **`calculations/elevon_authority.py`** — elevon control power via the VLM
  (step incidence over 30–90 % half-span): yield **0.00348 °/°**; 10° elevon
  ≈ 4.8× the SM-8 % trim requirement.

### Resolution (guide v0.3, justification §3.2)
- **OP-01 (CG reachability):** target CG −119 mm needs the 6S1P pack CG at
  **x ≈ −421 mm** — the v0.2 nose pod could only reach ≈ −100 (band −24…+9 mm).
  **Adopted: nose boom** carrying the battery bay (forward end x ≈ −493, 190×70×32,
  slide ≈ 36 mm covers R-CG ±5 mm), ≈ 360 mm forward of the nose pod tip, skid at the
  tip — Mojito pattern (I-02). Pack stations: 4S1P −577 / **6S1P −421** / 4S2P −346 /
  6S2P −270.
- **OP-23 (new):** the R-CG four-config requirement is not satisfiable with one bay
  (stations span 307 mm); the bay covers 6S1P (reference) + 4S2P; requirement
  re-derived in F2.
- **OP-24 (new):** boom structure ≤ 40 g target; AUW 1660 g → V_stall ≈ 45.6 km/h vs
  ≤ 45 required; declared lever: shell at 550 g (low end) + boom ≤ 40 g → ≈ 44.7 km/h.
- **R-TWIST 2.5° → 3.0°:** at 3.0° the stall criterion holds (load peak 56 % b/2,
  margin +0.017 — same as 0°; at 4° it drops to +0.009). Trim closure at SM 8 %:
  worst-case residual ≈ 0.6° permanent elevon reflex (authority verified).
- Central-body effect (I-07 §6): direction known (NP forward), margin applied in F2;
  does not reverse the solution.

### Changed
- Design guide v0.3: §4 stall flag (45.6 km/h + mass lever); §5.3 twist note
  (R-TWIST 3.0° + reflex closure); §6.1 trim-closure blockquote; §7.6 CORE nose
  boom + bay 190×70×32; §8.1 mass budget (boom 40 g, AUW 1660 g); §8.2 NP row
  (Weissinger-L) + OP-01 resolution blockquote; §9 bay; §12 step 7; §14 log.
- Justification §3.2 (resolution with pack-station table and honest flags); Open
  Points v0.3 (OP-01 resolved by decision, OP-02 updated, OP-16/OP-19 updated,
  OP-23/OP-24 added).

## [1.11] — 2026-08-05

**B3 screening executed (XFOIL 6.99, 24 cases) and C2 NP cross-check executed.**

### Executed
- **`calculations/b3_screening.py`** — batch XFOIL screening of the shortlist
  (E205, E205→9 %, S5010, MH60, MH60→12 %, MH60→13.5 %) at Re 3e5/5e5 × Ncrit 10/12
  (the I-06 calibrated band). Coordinates in `geometry/airfoils/`; 24 polars in
  `calculations/xfoil_out/`; all `[D]`.
- **`calculations/weissinger_np.py`** — independent NP check (Weissinger-L swept
  lifting line), validated on a straight AR 6 wing (NP 25.00 % MAC).

### Results (I-15 §6, all `[D]`)
- **E205 DISCARDED**: cm0 ≈ −0.07 at project Re (fails R-AIRFOIL by ≈ 0.08;
  ≈ 22° wash-in needed). In-service evidence does not imply Cm0 — confirmed.
- **Thinning quantified**: E205→9 % loses ≈ 0.1 clmax and 3–4° stall angle.
- **Published cm0 not achieved at project Re** (S5010: +0.0080 → −0.011…−0.016);
  **thickening a reflexed section improves cm0** (MH60: −0.0136 → +0.0016 at 13.5 %,
  Re 5e5, Ncrit 10).
- **Trim closure at SM 8 %: no off-the-shelf candidate fits R-TWIST ≤ 2.5°**
  (MH60→13.5 % needs 2.6–3.7° wash-in). Closure paths: designed section
  (cm0 ≥ +0.008), reduced SM target, or elevon reflex.
- **C2: NP verified by two methods** — VLM −101.3 mm (26.7 % MAC) vs Weissinger-L
  −98.3 mm (28.0 % MAC): **3 mm agreement**. The "least-verified number in the chain"
  claim (justification §3.1) is superseded; the central-body effect remains
  unquantified (moves NP forward).

### Changed
- Design guide: §3 NP row (C2 cross-check); §5.3 twist note (parametric; 2.6–3.7°
  preview with current candidates); §6.1 trim-closure blockquote; §6.2 E205 →
  discarded, MH60→13.5 % cm0 +0.0016; §14 log.
- Justification §3.1 (NP note), §4 airfoil rows; Open Points OP-02 (screening
  executed), OP-05 (cross-check done); gaps G8; calculations README.

### Engineering notes
- XFOIL 6.99 batch-mode quirks solved and baked into the script: Ncrit lives in the
  VPAR submenu (command `N`), polar via PACC/PWRT, CRLF input file, Fortran stdin EOF
  noise tolerated; the script is incremental (reuses valid polars).
- Two implementation bugs were found and fixed by validation: a wrong validation
  harness (b for S) and an odd `y·tanΛ` moment arm in Weissinger-L (the c/4 line
  sweeps forward on **both** halves, `|y|·tanΛ`).
- **Reproducibility packaging:** XFOIL path is now configurable (`--xfoil` / `XFOIL_EXE`);
  full reproduction guide in `calculations/README.md` (tools, versions, commands,
  batch quirks, validation discipline); coordinate provenance in
  `geometry/airfoils/README.md`; root README documents the toolchain and the current
  Phase-1 status (G8 largely closed, G2 screening executed).

---

## [1.10] — 2026-08-05

**Airfoil evidence campaign (I-15) opened — 11 investigations, 6 partially executed.**

### Added
- **[I-15](research/I-15-airfoil-evidence-campaign.md)** — analysis of the airfoil
  criterion (the guide's weakest, matrix score 60/100) and an evidence campaign with
  11 investigations (A1–A11) on the root/tip problem.
- Executed evidence (all NTRS, public fulltext where noted): E387 LSB measurements
  (NASA-CR-186263 — the project's calibration airfoil), Carmichael low-Re survey
  (NASA-CR-165803-VOL-1), thickness-induced separation crossover (NASA-CR-4096,
  Barnett & Carter), NACA-SR-83 (thickness vs drag), Notre Dame LSB series covering
  Re 40k–400k (AIAA 80-1440, 86-1065, 83-1671), flap-deflection LSB data (AIAA
  79-0004), Prandtl-D/Horten minimum-induced-drag line (DFRC-E-DAA-TN2041/3811/4103).
- Negative results recorded: PW51 not in UIUC (A3); airfoiltools unreachable from this
  environment (E205 XFOIL polar deferred to the local calibrated run); NTRS has **zero**
  reflexed-section records — the reflexed evidence base is the RC/glider world + LSB
  physics, not NASA.

### Changed
- Design guide §6.1 — R-AIRFOIL note: the root section is to be **designed, not
  selected**; **new binding criterion: gentle root-first stall character**; **declared
  confidence basis of the polar** (no measured reflexed polar at Re 3–5×10⁵; XFOIL
  `[D]` anchored on the E387 LSB measurements; printed-skin transition runs earlier;
  E2 closes); §1/§13 research set extended to I-01…I-15; §14 log updated.
- Justification §4 — provisional recipe row rewritten (MH 60-12 % family, designed
  root); stall-character row added with its `[M]` evidence; references extended.
- Open Points OP-02 — trigger now includes I-15; criteria now include the stall
  character.
- **Knowledge integration into the owning documents:**
  - I-06 — measured LSB anchors for the Ncrit calibration (NASA-CR-186263 E387, Notre
    Dame series at Re 40k–400k, Schmidt & Mueller, Carmichael survey); B1 closing list
    now includes the E387 bubble-level comparison.
  - I-01 — Carmichael fulltext source added; measured bridge to Re 4×10⁵ declared.
  - I-02 — Prandtl-D/Horten line added as supplementary evidence (does not reopen the
    closure), with its transfer limits.
  - I-08 — PW51 availability gap recorded (not in UIUC, 404).
  - ADR-0027 — evidence register added (thickness/separation sources) without reopening
    the decision; review conditions unchanged.

### Declared (not a correction)
- The airfoil criterion analysis concludes: no published reflexed section satisfies
  R-AIRFOIL at 13.5 % t/c; B3's central deliverable is a **designed section**, with
  R-AIRFOIL re-derivation against the twist window as the declared alternative.

---

## [1.9] — 2026-08-05

**Five new investigation threads (I-10…I-14) and correction C28.**

### Added
- **[I-10](research/I-10-control-authority-static-margin.md)** — tailless pitch control
  authority and minimum static margin (feeds C6/S5 — never done before — OP-01, OP-06).
- **[I-11](research/I-11-reflexed-airfoil-database.md)** — reflexed-airfoil database for
  the B3 shortlist (aerodesign.de tailless database reviewed; E205/UIUC availability
  checked). Partial: database values extracted, measured polars still to be compiled.
- **[I-12](research/I-12-x29-divergence-sweep-factor.md)** — X-29 divergence flight
  data and sweep-factor bounds (NASA-TM-86025 located on NTRS; feeds G6 — the declared
  weakest link — and G4).
- **[I-13](research/I-13-pusher-tractor-slipstream.md)** — pusher vs tractor slipstream
  at Re 3–5×10⁵ (feeds the disputed ADR-0006 and G5).
- **[I-14](research/I-14-hand-launch-stall-margin.md)** — hand-launch and stall-margin
  practice (feeds the O1 stall requirement with its 0.4 km/h margin and the launch
  method).

### Changed
- Design guide §6.2/§6.3 — provisional airfoil candidates corrected (C28); §1/§13
  research set extended to I-01…I-14.

### Corrections

| # | Error | Correction |
|---|---|---|
| **C28** | The design guide listed the provisional root airfoil as "MH 45 (t/c ≈ 13 %)". The aerodesign.de tailless-airfoil database (reviewed in I-11) lists **MH 45 at 9.85 % thickness, cm0 +0.0070**, documented for 15–40 g/dm² — below the project's 57 g/dm², and below R-AIRFOIL's +0.008 | Provisional root candidate moved to **MH 60-12 %** (12.0 %, cm0 +0.0030) scaled to 13.5 %; the guide now declares that **no off-the-shelf reflexed section reaches 13.5 %**, making R-AIRFOIL feasibility at 13.5 % an explicit B3 question; the 9 % tip must use camber compensation, not pure thickness scaling (MH 45-8 % precedent warns of clmax loss and harsh stall) |

---

## [1.8] — 2026-08-05

**Salamandra Design Guide v0.2 — designer-review release.**

The three `design/` documents were reviewed as a CAD specification (Fusion 360): every
value was re-derived and cross-checked (planform, stations, NP/CG/SM, speeds, balance).
All planform and stability numbers verified. Six inconsistencies were corrected; the
guide is now fully self-consistent and complete enough to model the v0.2 geometry.

### Changed
- **Design Guide v0.2** — new §7.6 "CORE (center module)": nose pod (60 mm forward of the
  root LE, battery reach x ≈ −100), rear pod (motor mount, prop disk at x ≈ +235), prop
  ground-clearance constraint (belly ≤ −111.6 mm at the prop plane), joint sockets with
  centerlines and clearances, avionics stations. Carbon tube/pin physical lengths.
  Provisional airfoil coordinate recipe (§6.3). Wing tips declared (flat caps, no winglet).
- **Justification v0.2** — moment balance re-derived with corrected motor station and the
  v0.2 bay limits; band ≈ −24…+9 mm (6S1P; ≈ −36…+9 across the packs, was −27…+29).
  Battery for target CG ≈ −439 mm (was −428).
- **Open Points v0.2** — OP-01/04/06/19 updated; OP-20 (wingtips), OP-21 (CORE outer
  mold), OP-22 (missing ADR files) added.

### Corrections

| # | Error | Correction |
|---|---|---|
| **C22** | The guide stated dihedral as both "polyhedral segment rotations" (0 / 1.07 / 0.46 / 0.47°) and a "linear schedule Γ(y) = 2.0°·y/650" — two different surfaces (tip rise 11.35 vs 12.18 mm), with ambiguous kink locations | Defined unambiguously: **piecewise-linear polyhedral, flat segments, kinks at every segment joint** (y = 195/347/498), cumulative values 0 / 1.07 / 1.53 / 2.0°, tip rise ≈ 12 mm; the linear schedule remains only as the generator of the joint values |
| **C23** | Elevon inner end at 20 % half-span (y = 130) crossed the removable CORE↔PANEL joint at 30 % (y = 195), placing a control surface on the shared, non-reprinted CORE with no servo for it | Elevon is a **panel component**: y = 195 → 585 (30–90 %), length 390 mm; CORE trailing edge fixed (torsion box may run to the TE inboard of the joint). Dual actuation retained as flutter margin pending C6 |
| **C24** | Print-fit statement inconsistent: "segments of ≈ 118 mm span" (actual: 152/151/152 mm), and span-at-45°-in-bed-plane does not fit the 256 mm bed (≈ 281 mm footprint for segment 1) | 45° defined as **roll of the airfoil plane about the span axis** (LE low): footprint 152 × 174 mm — fits; orientation constraints added to §7.4 |
| **C25** | Motor+prop station at x = +190 in the OP-01 balance — inside the planform (root TE at +216.9), impossible for a pusher with the prop disk aft of the TE | Prop disk at x ≈ +235 (≥ 10 mm aft of root TE), mount face +230, motor+prop centroid ≈ +217. OP-01 band re-derived with the v0.2 bay limits: ≈ **−24…+9 mm** (6S1P; ≈ −36…+9 across the packs, was −27…+29); battery for the target ≈ −439 mm |
| **C26** | "Prop with ≥ 10 mm ground clearance" at z = 0 with the 8×8 prop (radius 101.6 mm): the lowest blade tip falls ≈ 82 mm below the wing lower surface — the constraint was physically unsatisfiable with an airfoil-shaped CORE | CORE rear pod defined: **lower surface ≤ z = −111.6 mm at the prop plane** (≈ 92 mm below the wing lower surface). Thrust line stays at z = 0 (no pitch coupling) |
| **C27** | Tube "~390 mm per panel" is the spanwise extent; the physical tube is longer along the swept c/4 line (≈ 415 mm) plus ≈ 70 mm socket insertion | Tube ≈ **485 mm** total; pin ≈ 140 mm (70 + 70, matching the socket depth); socket bores Ø12.2–12.4 / Ø6.1–6.2, depth ≈ 70 mm — added to §7.2/§7.3 |

### Identified
- **OP-22** — ADR files 0003, 0006, 0008, 0009, 0012, 0016, 0018, 0023, 0024, 0026,
  0030, 0031, 0034, 0035 exist in the decisions **index** but were never published as
  files; several are referenced by the guide. Must be published before v1.0.

---

## [1.7] — 2026-08-05

**Salamandra Design Guide v0.1 released.**

### Added
- **`design/Salamandra-Design-Guide-v0.1.md`** — first release of the CAD-ready
  specification for the designer: reference planform (b 1300 mm, S 0.282 m², AR 6.0,
  λ 0.50, Λ_c/4 −20°, t/c 13.5/9 %), provisional airfoil (B3 pending), structure,
  mass budget, propulsion, bay and avionics.
- **`design/Design-Guide-Justification-v0.1.md`** — per-value rationale with confidence
  tags and derivations.
- **`design/Design-Guide-Open-Points-v0.1.md`** — open points and evolution process.

### Identified
- **OP-01 (critical)** — preliminary moment balance shows the target CG (18.7 % MAC,
  47 mm forward of the root LE) is not reachable with the current mass layout; the
  neutral point must be re-verified with an independent method (C2) before the bay
  position is finalized.

---

## [1.6] — 2026-08-05

**Project reframed as an open, community-driven aircraft platform.**

### Added
- **ADR-0036** — the repository is an open, community-driven, modular 3D-printed FPV
  aircraft platform: AI performs the aerodynamic/theoretical research and design
  exploration; the community creates the actual 3D parts, experiments and manufacturing
  know-how.
- **ADR-0037** — licence selected: **CERN-OHL-S-2.0** for hardware/design/scripts and
  **CC BY-SA 4.0** for documentation.
- `LICENSE` (CERN-OHL-S v2) and `LICENSE-docs.md` (CC BY-SA 4.0).

### Changed
- `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `docs/00-...` and `docs/05-...` updated to
  communicate the platform purpose, the AI–human division of labour, the modular and
  extensible nature (beyond the forward-swept flying wing), and the importance of community
  participation.
- PR template updated to welcome diverse contributions and declare the licence.

---

## [1.5] — 2026-07-28

**A4 started with primary sources from the StuntDouble family.**

### Added
- **[I-08](research/I-08-stuntdouble-family.md)** — base comparison of Nemesis,
  Stinger V2 and Stormbird.
- **[I-06](research/I-06-reflexed-airfoils.md)** and
  **`calculations/calibra_xfoil_e387.py`** — first reproducible XFOIL calibration against
  the measured E387 (C) polar.
- Primary Stinger V2 and Stormbird files for the later reconstruction of planform,
  airfoil and twist.

### Results
- The three published designs converge on **AR = 6.05–6.55** `[D]`.
- Nemesis and Stinger keep twin tractor and comparable wing loading, but switch from
  PW51 to PW75; Stormbird additionally switches to a single pusher.
- Nemesis publishes 2 mm of reflex and Stormbird 1–2 mm `[M]`; the local chord is
  missing to convert those adjustments into angle.
- Ncrit 10 minimizes the global `Cd(Cl)` disagreement with an RMS factor of 1.208 `[D]`
  (Ncrit 11: 1.209), but the optimum drifts to Ncrit 12 at Re 3–5×10⁵. B3 should
  use a 10–12 band.

### Corrections

| # | Error | Correction |
|---|---|---|
| **C19** | A4 described Nemesis vs. Stinger/Stormbird as a "controlled comparison" able to isolate the effect of sweep | It is a **quasi-controlled comparison**: same author, constructive family and comparable AR, but airfoil, size and propulsion do not all remain constant. It serves as a geometric prior; it does not demonstrate sweep causality |
| **C20** | B1 assumed that tuning a single Ncrit would "reproduce the measured polar" of the E387 across the whole range | The optimum changes with Reynolds: Ncrit 10–12 on the tested grid. The single number is replaced by a **band with published sensitivity** and validation against a second physical model before screening airfoils |
| **C21** | B2 still accepted `C_m0 ≥ 0 or close` after I-07 derived R-AIRFOIL | Criterion re-derived downstream: **C_m0 ≥ +0.008**, preferably +0.010–0.015. The old criterion could admit airfoils unable to close the trim within R-TWIST |

---

## [1.4] — 2026-07-28

**First in-house stability calculation.** G8 moves from open to partial.

### Added
- **`calculations/vlm_ala_volante.py`** — in-house vortex lattice with validation case.
- **`calculations/ventana_torsion.py`** — torsion window analysis.
- **[I-07](research/I-07-neutral-point-torsion-window.md)** — neutral point, static margin and torsion window.
- **R-AIRFOIL** — airfoil Cm0 ≥ +0.008. Bounds G2 with a number.
- **R-TWIST** — wash-in ≤ 2.5°.

### Results
- **Neutral point = 26.7 % MAC**, 101 mm ahead of the root quarter-chord. Target CG 18.7 % MAC for 8 % static margin.
- **R-NP is easy to meet:** the NP drift between 1100 to 1600 mm panels is only **1.6 MAC points**, and a ±2–4° sweep adjustment aligns them within 0.5 %.
- **The torsion window exists but is narrow.** With pure twist, balancing at 10 % static margin requires 3.9° of wash-in, and that moves the load peak to 62 % of half-span — the elevon zone. **The airfoil must carry most of the trim.**

### Corrections

| # | Error | Correction |
|---|---|---|
| **C17** | The first version of the VLM returned the non-dimensionalized moment **without dividing by the MAC**, introducing a spurious chord factor in the neutral point | Detected by the validation case: a straight wing must give the NP at c/4 and gave ~0. **Confirms the value of always including an analytic contrast case in any calculation script** |
| **C18** | The optimistic reading of C2 suggested that wash-in could free the project from using a reflexed airfoil | **Partially false.** Wash-in works, but **trades trim against the advantage that justified choosing forward sweep**: at 4° the load peak moves from 27 % to 62 % of half-span. Reflex remains necessary; twist is left for fine-tuning |

---

## [1.3] — 2026-07-28

Repository restructured into an evolutionary format, designed for external contributions.

### Added
- **`decisions/`** — ADR register: one decision per file, with context, alternatives, consequences and review conditions. Index with states.
- **`research/`** — five documented research threads (I-01 to I-05), separating *the why* from *the what*.
- **`gaps/`** — formal register of G1–G9 with impact and closing path.
- **`CONTRIBUTING.md`** — contribution flow, value ordering, source quality.
- **`docs/04-conventions.md`** — tags, identifiers, symbols and sign conventions.
- **D34** — motor mount angle as a design parameter, not assumed zero.
- **D35** — TPU-printed hinges as the baseline option.
- **G9** — altitude-loop coupling with pitch (*porpoising*). **Threatens the validity of E7.**

### Corrections

| # | Error | Correction |
|---|---|---|
| **C16** | The requirement `V_stall ≤ 40 km/h` was derived with AUW 1350 g (48 g/dm²) and **was not re-derived** when the AUW rose to 1620 g | With C_Lmax 0.65 at 57 g/dm² the real speed is **42.7 km/h**. Reaching 40 would require C_Lmax 0.74, outside the measured range (0.55–0.70). **Requirement relaxed to ≤ 45 km/h**, justified by Peregrine and Mojito precedent |

---

## [1.2] — 2026-07-28

### Added
- **Modular architecture** (ADR-0032): CORE + PANEL, joint at 30 % of half-span.
- **R-NP**, **R-JOINT**, **R-CG**.
- **ADR-0033** — motor and battery out of the design.
- **E7** — Southwell in flight.
- **G8** — neutral point and static margin, uncomputed. Blocks Phase 1.
- **`docs/02-measured-references.md`** — primary data of the Peregrine 840 mm.

### Changed
- **ADR-0027** — t/c to **13.5 % / 9 %**, confirmed by measurement on an in-service article.
- **ADR-0028** — **gyroid 5 %** infill instead of a third perimeter.
- V_NE of article #1 lowered to **160 km/h**.

### Superseded
- **ADR-0022 — carbon veil ±45°.** Withdrawn by project decision (objective O5).
- **E4** (bench twist) — replaced by anchoring to measured reference and E7.
- **E6** — see C13.

### Corrections

| # | Error | Correction |
|---|---|---|
| **C11** | It was claimed that carbon tubes and rods add no torsional stiffness | True for the calculated case (10/8 mm), **false as a rule**. In thin wall `J = πD³t/4`: it scales with the **cube of the diameter**. A well-bonded braided ±45° 18 mm tube is indeed a torsional element |
| **C12** | Infill 0 % was specified, inherited from LW-PLA vase-mode practice | **Wrong for a PETG shell.** Bredt-Batho assumes the skin does not buckle; an unsupported 0.4–0.9 mm skin buckles locally well below the material limit. **Without infill, GJ was overestimated** — the error ran in the opposite direction to what was assumed |
| **C13** | E6 was proposed, inverse calibration of the model against the Peregrine | **Withdrawn.** The Peregrine is at a factor ~3 from the prediction. A test that passes with that margin does not falsify the model **but does not validate it either** |
| **C14** | Structural risk was overestimated and communicated with more certainty than `[E]` ±35 % data supported | With gyroid and D-box the margin is 1.5–2.0×. The alarm corresponded to a configuration without infill and without D-box that was no longer the project's |
| **C15** | It was claimed that a single perimeter fails the divergence criterion | **Falsified by flying hardware.** The 840 mm Peregrine flies with 1 perimeter of 0.42 mm and 4 % gyroid |

---

## [1.1] — 2026-07-28

### Resolved
- **ADR-0010** — **branch A (fast cruise)** fixed, forced by PETG density.
- Efficiency objective quantified: **≤ 1.15 Wh/km**.

### Changed
- **ADR-0004** — aspect ratio tightened from 6–8 to **6.0**.
- **ADR-0005** — superseded: the airfoil moves from "thin" to higher thickness *(later replaced by ADR-0027)*.

### Added
ADR-0012, 0015, 0016, 0018, 0021, 0022, 0023, 0024, 0025, 0026. Gaps **G6** (sweep factor) and **G7 (flutter, unanalyzed)**.

### Superseded
ADR-0011, 0013, 0014, 0017, 0019, 0020 — after evaluating PETG, PLA, PLA+, ASA and LW-PLA.

### Corrections

| # | Error | Correction |
|---|---|---|
| C6 | GJ computed with a 231 mm chord while the one consistent with AR 6.0 is 217 mm | Net effect on V_div: **−3 %**. The chord appears in both the numerator and denominator of q_D |
| C7 | It was claimed that the Eliminator at 360 km/h validated printed construction in general | It validates **its** material, almost certainly PLA. With a 40 % lower G, the PETG does not inherit that endorsement |
| C8 | It was claimed that PETG has better layer adhesion than PLA | **False.** Z retention: PLA 55 %, PETG 46 %, ASA 29 %. PETG wins on toughness, not adhesion |
| C9 | It was claimed that PETG cannot be glued | Too categorical. 3D-Gloop PETG, DCM (restricted in the EU) and 30-min epoxy exist |
| C10 | Shell mass estimated at 450–500 g | Wetted-area count: **550–650 g** |

---

## [1.0] — 2026-07-27

Initial research closed. Data consolidation, analytical framework, ADR-0001 to 0010 decisions and gaps G1–G5.

### Corrections

| # | Error | Correction |
|---|---|---|
| C1 | It was claimed that the Oswald factor collapses with aspect ratio for physical reasons | It is largely a **definition artifact**: e_v decreases with AR by algebraic construction. Raising AR does work; the real effect is saturation and the chord→Re coupling |
| C2 | It was claimed that forward sweep depends exclusively on the airfoil C_m0 | **It can and should use wash-in.** The two planforms are symmetric solutions. Opens the door to lightly reflexed airfoils |
| C3 | 3D printing was assumed to be the structurally weak option | It is a closed shell = torsion box |
| C4 | Arithmetic error solving for the Solar Impulse L/D | The correct value is L/D ≈ 49, not 31 |
| C5 | The Mojito maximum L/D was estimated at ≈ 11 | The value solved from real flight data is **≈ 7.4 in fast cruise** |
