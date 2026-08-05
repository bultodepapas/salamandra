# I-15 — Airfoil evidence campaign (root and tip of the Salamandra)

**Status:** 🔄 **Open — campaign running (11 investigations; 6 partially executed 2026-08-05)**
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
| A2 | E205 Cm0 determination | 🔄 partial (geometry done; polar pending) | G-2 |
| A3 | PW51 coordinates/polars sourcing | ✅ executed (negative: not in UIUC) | G-2 |
| A4 | XFOIL cm0 prediction validation for reflexed sections | ⬜ pending (sources located) | G-1/G-2 |
| A5 | Thickness effects at Re 3–5×10⁵ (separation crossover, drag) | 🔄 partial (sources located) | G-3 |
| A6 | Horten thick reflexed sections + Prandtl-D line | 🔄 partial (methodology located) | G-1, tailless context |
| A7 | BWB / thick-airfoil low-speed design rules | ⬜ pending (query too narrow) | G-3 |
| A8 | Reflex magnitude → cm0 design curve | 🔄 partial (published values; XFOIL pending) | G-5 |
| A9 | LSB/Ncrit calibration at Re 3–5×10⁵ | 🔄 partial (key sources located) | G-4, I-06 |
| A10 | Flap/elevon interaction with reflexed sections at low Re | 🔄 partial (sources located) | G-6, I-10 |
| A11 | In-service thick (>12 %) reflexed practice | 🔄 partial | G-1/G-3 |

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

# 6. Transfer limits

- Most low-Re measured data is at Re ≤ 2×10⁵ (Notre Dame series) or ≥ 3×10⁶ (NACA);
  the 3–5×10⁵ band is a gap in *measured* data — XFOIL with the calibrated band is the
  bridge, and E2 (flight polar) is the closer.
- Horten/Prandtl-D operate at far higher Re and span loadings; their value is
  methodological.
- BWB thickness studies are high-Re and mostly non-reflexed; transfer only the
  thickness-distribution practice.
- No reflexed-section measured polar is known to exist at Re 3–5×10⁵; if A1 finds one,
  it becomes the single most valuable document in this campaign.
