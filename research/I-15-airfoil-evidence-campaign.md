# I-15 — Airfoil evidence campaign (root and tip of the Salamandra)

**Status:** 🔄 **Open — B3 screening EXECUTED (2026-08-05): 24 XFOIL cases + C2 NP cross-check done; extraction of the NTRS literature still pending**
**Feeds:** B3/G2 (airfoil screening), OP-02 (provisional profile), R-AIRFOIL
re-derivation, guide §6.1/§6.2/§6.3
**Closes:** G2 (with I-06, E2)
**Companion:** I-11 (aerodesign.de database review), I-09 (E205 in-service evidence)

---

# 1. The problem (analysis of the guide's airfoil criterion)

The airfoil is the guide's weakest criterion (matrix score 60/100). The evidence gaps,
stated as questions the designer and B3 must answer:

| Gap | Question | Current evidence |
|---|---|---|
| G-1 | What reflexed section gives Cm0 ≥ +0.008 **at 13.5 % t/c**? | **None exists off-the-shelf** (I-11: thickest reflexed = MH 60-12 %, cm0 +0.0030; HS 3.4/12.0 at 12 %, cm0 −0.0010) |
| G-2 | What is E205's actual Cm0 at Re 3–5×10⁵? | Unknown — only geometry `[M]` (I-09); tailed planes trim it, so in-service evidence does not imply Cm0 |
| G-3 | Can a 13.5 % section keep C_Lmax ≥ 0.65 and gentle stall at Re 3–5×10⁵? | Thickness-separation crossover literature says thick sections transition local → massive separation (Barnett/Carter); MH 45-8 % precedent warns reflexed thinning fails |
| G-4 | What is the Ncrit 10–12 calibration band worth at Re 3–5×10⁵? | E387 LSB measured data exist (NASA-CR-186263) — the exact calibration airfoil; not yet extracted |
| G-5 | What does the reflex amount do to cm0 per unit (design curve)? | Only scattered published cm0 values (I-11) |
| G-6 | Do elevons on reflexed sections behave at low Re (hysteresis, pitch problems)? | Siegmann's `[M]` warnings (SB-13, RS 004A, SD7003, EH); no quantitative data |

**Core conclusion (as aircraft designer):** the 13.5 % root is structurally locked
(ADR-0027: 21700 cell housing, divergence ∝ h/c) and the aerodynamic evidence says
**no published reflexed section satisfies it — the root airfoil must be DESIGNED, not
selected**, and the tip must be camber-compensated (not thinned). The campaign below is
the evidence base for that design exercise and for re-deriving R-AIRFOIL if needed.

# 2. The eleven investigations

| # | Investigation | Status 2026-08-05 | Feeds |
|---|---|---|---|
| A1 | Measured low-Re polars of the reflexed shortlist | ⬜ pending | G-1/G-2 |
| A2 | E205 Cm0 determination | ✅ **executed — E205 DISCARDED (cm0 ≈ −0.07)** | G-2 |
| A3 | PW51 coordinates/polars sourcing | ✅ executed (negative: not in UIUC) | G-2 |
| A4 | XFOIL cm0 prediction validation for reflexed sections | ⬜ pending (sources located) | G-1/G-2 |
| A5 | Thickness effects at Re 3–5×10⁵ (separation crossover, drag) | 🔄 partial (screening trend done; NTRS extraction pending) | G-3 |
| A6 | Horten thick reflexed sections + Prandtl-D line | 🔄 partial (methodology located) | G-1, tailless context |
| A7 | BWB / thick-airfoil low-speed design rules | ⬜ pending (query too narrow) | G-3 |
| A8 | Reflex magnitude → cm0 design curve | 🔄 partial (thickness trend from screening §6.2; parametric sweep pending) | G-5 |
| A9 | LSB/Ncrit calibration at Re 3–5×10⁵ | 🔄 partial (key sources located) | G-4, I-06 |
| A10 | Flap/elevon interaction with reflexed sections at low Re | 🔄 partial (sources located) | G-6, I-10 |
| A11 | In-service thick (>12 %) reflexed practice | 🔄 partial | G-1/G-3 |
| **C2** | **Independent NP cross-check** | ✅ **executed — Weissinger-L vs VLM: 3 mm agreement (§6.3)** | G-8 |

# 3. Executed evidence (2026-08-05, with tags)

## A3 — PW51 availability `[D]`
PW51 (Nemesis airfoil, I-08) is **not in the UIUC database** (404 on
`coord_seligFmt/pw51.dat`). Alternatives pending: airfoiltools (unreachable from this
environment), German nurflügel sources, Unverferth's "Faszination Nurflügel". Until
found, PW51 stays out of the measured-data path.

## A5 — Thickness and separation at low Re `[M]` (sources located, NTRS)
- **NASA-CR-4096 / AIAA 87-1268** — Barnett & Carter, "Crossover between local and
  massive separation on airfoils": as **thickness increases**, the flow evolves from
  local to massive separation (triple-deck and interacting boundary-layer theory).
  Direct evidence for the G-3 risk at 13.5 %.
- **NACA-SR-83** — Jacobs (1938), "Effect on the Choice of Wing-Section Thickness":
  classic thickness-vs-profile-drag evidence (smaller drag increase with thickness than
  the old variable-density-tunnel data suggested).
- **NACA-RM-L8L08** — Loftin & Smith, 34 airfoil sections at Re 3–9×10⁶ (high-Re
  reference; transfer limits apply).
- **AIAA 80-1440, 86-1065, 83-1671, 87-1271** — Mueller/Batill/Stack et al.: LSB
  structure on NACA 66(3)-018 and LRN(1)-1010 at Re 40,000–400,000 — **covers the
  project's Reynolds band**.

## A6 — Horten / Prandtl-D line `[M]` (sources located, NTRS, fulltext available)
- **DFRC-E-DAA-TN2041 / TN3811 / TN4103** — Bowers (NASA Dryden), "On the Minimum
  Induced Drag of Wings": Prandtl's 1932 solution and the **Horten refinements**
  (bell-shaped span load, no vertical tail). Methodology evidence for the tailless
  context (I-02); not airfoil-section data. Horten **section data** (thick reflexed
  profiles) still to be extracted from the glider literature — with the declared
  transfer limit (their Re ≈ 5–10×10⁶ vs the project's 3–5×10⁵).

## A9 — LSB/Ncrit calibration `[M]` (sources located, NTRS)
- **NASA-CR-186263** — Cole & Mueller, "Experimental measurements of the laminar
  separation bubble on an **Eppler 387** airfoil at low Reynolds numbers" (1990,
  fulltext available): LDV boundary-layer data at Re 100,000 — the project's
  calibration airfoil (I-06), measured.
- **NASA-CR-165803-VOL-1** — Carmichael, "Low Reynolds number airfoil survey" (1981,
  fulltext available): the classic critical-Re survey; strengthens the I-01 regime
  reasoning.
- **AIAA 89 / Schmidt & Mueller** — "Analysis of low Reynolds number separation bubbles
  using semiempirical methods" (Horton's method at Re 50–200k).
- **AIAA 79-0004** (Arena & Mueller): LSB behavior including **flap deflection
  effects** at Re 150–470k — feeds A10 as well.

## A2 — E205 geometry `[M]` (UIUC coordinates, done in I-09)
t/c 10.6 % at 30 % c; camber 2.9 % at 34 % c; mean line positive through 90 % c.
Cm0 **not determinable from geometry** — the XFOIL run (Ncrit 10–12) is pending;
airfoiltools was unreachable from this environment on 2026-08-05 (transport error,
three attempts), so the polar must come from the project's own calibrated XFOIL in B3.

## Negative result worth recording `[D]`
NTRS full-text search "reflexed airfoil pitching moment": **0 results**. NASA's
database contains essentially no reflexed-section work; the reflexed evidence base is
the RC/glider world (aerodesign.de, UIUC, Unverferth) plus low-Re LSB physics
(Notre Dame/NASA). The campaign should not expect US-government section data.

# 4. Investigations still to execute (with their planned sources)

| # | Plan |
|---|---|
| A1 | UIUC LSATs vols. 1–3 (Selig et al.) — measured polars of SD7003, E387, E205-class sections at Re 1–5×10⁵; extract what is published for the shortlist; mark the rest XFOIL-only |
| A2 | Run the project's calibrated XFOIL (Ncrit 10–12, I-06) on E205 at Re 200k/300k/500k → Cm0, clmax; compare with any measured data found in A1 |
| A3 | airfoiltools (when reachable), German nurflügel sites, Unverferth book — PW51 coordinates + polars |
| A4 | XFOIL-vs-measured cm0 validation studies for reflexed/low-Re sections (Selig's validation papers, E387 comparisons in A9) → uncertainty band for the Cm0 gate |
| A5 | Extract NASA-CR-4096 and NACA-SR-83 numbers → declared thickness-drag and separation-onset rules for the 13.5 % root |
| A6 | Horten IV/V section data + the Prandtl-D flight results → historical thick-reflexed precedent and the bell-load context for the tailless trim (I-02) |
| A7 | Retry NTRS with "blended wing body" + "airfoil design" queries; plus AIAA BWB low-speed papers (thick 15–20 % sections at low speed) → modern thick-section design rules |
| A8 | Parametric XFOIL sweep: reflex amount vs cm0 at constant thickness (9 % and 13.5 %) → the design curve for the tip and root |
| A9 | Extract NASA-CR-186263 numbers → tighten the Ncrit band and the clmax expectations for the project's Re |
| A10 | Arena & Mueller (AIAA 79-0004) flap data + Siegmann's practice warnings → elevon/reflex design rules (feeds I-10) |
| A11 | RC FPV practice: Zagi 12 % (EPP), HS 3.4/12, combat wings, any 13.5 %+ section in service → feasibility prior for the root thickness |

# 5. Expected outputs and design consequence

1. **A designed root section** (not an off-the-shelf pick): thickness distribution
   managed per A5, reflex per A8, clmax per A9 — or a declared R-AIRFOIL re-derivation
   against the twist window (I-07) if the evidence closes the door at 13.5 %.
2. **A camber-compensated tip design rule** (A8) replacing the warned-against thinning.
3. **An uncertainty band for the Cm0 gate** (A4) — the number R-AIRFOIL lives on.
4. E205 admitted or discarded on its polar (A2), not on the manuals.
5. Ncrit band re-affirmed or widened (A9) for B3's XFOIL screening.

# 6. Executed results — Part 2 (2026-08-05): B3 screening and C2 cross-check

The B3 screening was **executed** with the official XFOIL 6.99 (batch mode), and the C2
independent NP check was **executed**. Scripts: `calculations/b3_screening.py`,
`calculations/weissinger_np.py`; coordinates in `geometry/airfoils/`; polars in
`calculations/xfoil_out/` (24 cases, all `[D]`).

## 6.1 Screening table `[D]` (cm0 = CM at CL=0 about c/4, linear fit)

| Airfoil | Re | Ncrit | cm0 | clmax | α_stall | (L/D)max | cd@CL 0.132 |
|---|---|---|---:|---:|---:|---:|---:|
| E205 (10.6 %) | 3e5 | 10 | −0.0745 | 1.205 | 13.5 | 88.6 | 0.0078 |
| | 3e5 | 12 | −0.0760 | 1.230 | 13.0 | 89.0 | 0.0079 |
| | 5e5 | 10 | −0.0681 | 1.225 | 14.0 | 105.7 | 0.0068 |
| | 5e5 | 12 | −0.0749 | 1.224 | 13.0 | 106.8 | 0.0066 |
| E205→9 % | 3e5 | 10 | −0.0621 | 1.136 | 10.5 | 84.3 | 0.0070 |
| | 3e5 | 12 | −0.0641 | 1.078 | 9.0 | 85.5 | 0.0070 |
| | 5e5 | 10 | −0.0612 | 1.162 | 10.5 | 98.7 | 0.0059 |
| | 5e5 | 12 | −0.0621 | 1.124 | 10.5 | 100.9 | 0.0060 |
| S5010 (9.8 %) | 3e5 | 10 | −0.0140 | 1.257 | 12.0 | 73.3 | 0.0081 |
| | 3e5 | 12 | −0.0156 | 1.239 | 12.0 | 72.6 | 0.0084 |
| | 5e5 | 10 | −0.0114 | 1.300 | 12.0 | 86.9 | 0.0065 |
| | 5e5 | 12 | −0.0129 | 1.288 | 11.5 | 87.7 | 0.0066 |
| MH60 (10.1 %) | 3e5 | 10 | −0.0210 | 1.186 | 13.0 | 71.0 | 0.0078 |
| | 3e5 | 12 | −0.0238 | 1.203 | 12.5 | 70.3 | 0.0082 |
| | 5e5 | 10 | −0.0136 | 1.215 | 13.5 | 83.3 | 0.0061 |
| | 5e5 | 12 | −0.0184 | 1.212 | 13.0 | 84.1 | 0.0062 |
| MH60→12 % | 3e5 | 10 | −0.0191 | 1.291 | 12.5 | 72.6 | 0.0084 |
| | 3e5 | 12 | −0.0269 | 1.284 | 12.5 | 71.4 | 0.0092 |
| | 5e5 | 10 | −0.0036 | 1.316 | 13.0 | 86.8 | 0.0065 |
| | 5e5 | 12 | −0.0108 | 1.317 | 12.0 | 87.0 | 0.0066 |
| **MH60→13.5 %** | 3e5 | 10 | −0.0084 | 1.366 | 15.0 | 72.8 | 0.0088 |
| | 3e5 | 12 | −0.0166 | 1.370 | 15.0 | 71.5 | 0.0094 |
| | **5e5** | **10** | **+0.0016** | 1.425 | 15.0 | 87.7 | 0.0070 |
| | 5e5 | 12 | −0.0018 | 1.425 | 15.0 | 87.6 | 0.0070 |

## 6.2 Findings `[D]` (XFOIL, Ncrit 10–12 — the I-06 calibrated band)

1. **E205 is DISCARDED.** cm0 = −0.068…−0.076 at the project's Re — fails R-AIRFOIL
   (≥ +0.008) by ≈ 0.08. It would need ≈ 22° of wash-in; impossible (R-TWIST 2.5°).
   Its tip-data-point role is resolved: **not admitted on the polar** (the campaign's
   predicted outcome, now measured). High clmax (1.2) and L/D (106) do not compensate.
2. **Thinning is quantified as harmful:** E205→9 % loses ≈ 0.1 of clmax and 3–4° of
   stall angle at the same cm0. The C28 tip rule (camber compensation, not pure
   scaling) is now `[D]`-anchored.
3. **The published cm0 of reflexed sections is not achieved at project Re.** S5010:
   published +0.0080 → computed −0.011…−0.016. The reflex loses effectiveness at low
   Re with free transition (the Hepperle warning in I-01, quantified).
4. **Thickening a reflexed section IMPROVES cm0** (MH60 family, Re 5e5, Ncrit 10):
   −0.0136 (10 %) → −0.0036 (12 %) → **+0.0016 (13.5 %)**; clmax also rises (1.22 →
   1.43). The database note "lack of thickness causes trouble on reflexed airfoils" is
   confirmed and quantified in the favorable direction.
5. **Trim closure at SM 8 % (Cm0_req = 0.01056; yield 0.0034/° per VLM):** required
   wash-in per candidate (Re 5e5, Ncrit 10–12):
   - MH60→13.5 %: **2.6–3.7°** (best case just outside R-TWIST ≤ 2.5°);
   - MH60→12 %: 4.2–6.3°; S5010: 6.5°+; MH60: 7°+; E205: ≈ 22°.
   **No off-the-shelf section closes the trim inside the torsion window at SM 8 %.**
   Either the section is **designed** for cm0 ≥ +0.008 at Re 4–5×10⁵ (the campaign's
   central conclusion, now numeric), or the SM target drops (at SM 6 %, Cm0_req =
   0.00792 → MH60→13.5 % needs 1.9–2.9°, marginal at Ncrit 10), or permanent elevon
   reflex takes part of the trim (in-service practice, I-08 — at the cost of authority).
6. **Section clmax is not the binding link of the stall chain:** every candidate
   ≥ 1.08 at Re 3e5 vs the ≥ 0.65 requirement (XFOIL overpredicts stall, I-06, but the
   margin is ≈ 2×). The wing-level C_Lmax (3-D losses, printed roughness) is the real
   question for the 0.4 km/h stall margin.
7. **The thick root costs little profile drag at cruise CL:** MH60→13.5 % cd ≈ 0.0070
   vs S5010 ≈ 0.0065 at Re 5e5 (with the E387 calibration factor ≈ 1.2: ≈ 0.008 in
   service) — ADR-0027's accepted penalty is mild.

## 6.3 C2 — neutral point cross-check `[D]` (executed)

| Method | Structure | x_NP (root c/4) | NP |
|---|---|---|---|
| In-house panel VLM (I-07) | 2-D vortex lattice, chordwise panels | **−101.3 mm** | 26.7 % MAC |
| **Weissinger-L** (new, independent) | 1-D swept lifting line (c/4 bound, 3/4-chord cps), textbook formulation | **−98.3 mm** | 28.0 % MAC |

- **Agreement: 3 mm (≈ 0.6 % MAC).** Two structurally different methods converge on
  NP ≈ **−100 mm ± 3 mm**. The in-house code's NP is no longer the least-verified
  number in the chain (justification §3.1 point 1 is superseded by this result).
- Validation: Weissinger-L on a straight AR 6 wing → NP 25.00 % MAC (exact); CL_α
  within 7 % of Helmbold (the classical 1-D/2-D difference).
- Mesh-converged (ny 40→320: 27.8→28.2 % MAC).
- **Remaining NP uncertainty (unchanged):** the central-body effect (I-07 §6, §7.4)
  moves the NP forward — still unquantified; both methods are inviscid flat-plate
  (no thickness, no camber, no body).

## 6.4 Reproducibility (for anyone repeating this work)

- **Scripts:** `calculations/b3_screening.py` (screening) and
  `calculations/weissinger_np.py` (C2) — self-contained, with validation cases and
  full usage notes in `calculations/README.md`.
- **Tools:** Python ≥ 3.8 + numpy; XFOIL **6.99** (official MIT Windows build,
  <https://web.mit.edu/drela/Public/web/xfoil/> → `XFOIL6.99.zip`; GPL). Point the
  script at it with `--xfoil <path>` or `XFOIL_EXE`.
- **Inputs:** coordinates in `geometry/airfoils/` (provenance in its README); the
  script regenerates the scaled variants itself.
- **Commands:**
  ```bash
  python3 calculations/b3_screening.py --xfoil /path/to/xfoil.exe
  python3 calculations/weissinger_np.py
  ```
- **Artifacts:** raw XFOIL polars in `calculations/xfoil_out/` (24 files, each header
  verified to carry the requested Re/Ncrit); results table above. The screening is
  incremental: reruns reuse valid polars.
- **Known platform notes (Windows):** XFOIL 6.99 batch mode needs a CRLF input file
  redirected as stdin, the Ncrit command lives in the VPAR submenu, and the Fortran
  runtime prints a harmless EOF message after QUIT — all handled by the script.
- **Validation:** `weissinger_np.py` must reproduce NP = 25.00 % MAC on a straight
  AR 6 wing; `b3_screening.py` verifies each polar header. A modification that fails
  either check is not accepted (CHANGELOG [1.11] records the two bugs this caught).

## 6.5 Consequences applied to the design documents

- Guide §6.2: E205 row → **discarded on the polar** (values above); MH60→13.5 % row →
  cm0 +0.0016 `[D]` at Re 5e5/Ncrit 10 (published +0.0030 not reached at project Re).
- Guide §6.1: R-AIRFOIL note carries the trim-closure numbers (SM 8 % → no off-the-shelf
  section fits R-TWIST; designed section mandatory; SM reduction or elevon reflex as
  declared alternatives).
- Guide §3 summary and §8.2: NP row annotated with the C2 cross-check.
- Open points: OP-02 (screening executed, E205 discarded, designed section confirmed),
  OP-05 (independent method done, 3 mm agreement; body effect pending).
- Justification §3.1: NP verification note updated (the "least-verified number" claim
  is superseded).
- CHANGELOG [1.11] records the execution.

# 7. Transfer limits

- Most low-Re measured data is at Re ≤ 2×10⁵ (Notre Dame series) or ≥ 3×10⁶ (NACA);
  the 3–5×10⁵ band is a gap in *measured* data — XFOIL with the calibrated band is the
  bridge, and E2 (flight polar) is the closer.
- Horten/Prandtl-D operate at far higher Re and span loadings; their value is
  methodological.
- BWB thickness studies are high-Re and mostly non-reflexed; transfer only the
  thickness-distribution practice.
- No reflexed-section measured polar is known to exist at Re 3–5×10⁵; if A1 finds one,
  it becomes the single most valuable document in this campaign.
