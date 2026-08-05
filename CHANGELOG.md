# Changelog

Continues the project's correction log. **Errors are documented because they affected intermediate conclusions.** The error history is part of the product: it is what allows trust in what remains standing.

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
