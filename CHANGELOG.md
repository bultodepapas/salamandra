# Changelog

Continues the project's correction log. **Errors are documented because they affected intermediate conclusions.** The error history is part of the product: it is what allows trust in what remains standing.

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
