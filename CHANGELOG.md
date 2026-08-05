# Changelog

Continues the project's correction log. **Errors are documented because they affected intermediate conclusions.** The error history is part of the product: it is what allows trust in what remains standing.

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
