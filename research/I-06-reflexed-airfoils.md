# I-06 — Reflexed airfoils at Re 3–5×10⁵

**Status:** Open — B1 partial, reproducible E387 (C) calibration
**Closes:** G2
**Feeds:** B2/B3 of the Phase 1 plan and R-AIRFOIL

---

# 1. Question

With what uncertainty can XFOIL be used to screen reflexed airfoils at the project's
Reynolds number?

The first task is not to compare candidate airfoils. It is to measure how wrong XFOIL is
against a tunnel polar before trusting its outputs.

# 2. Primary sources

- E387 coordinates from the
  [UIUC Airfoil Data Site](https://m-selig.ae.illinois.edu/ads/coord_seligFmt/e387.dat).
- Clean E387 (C) polar, five Reynolds numbers, from the
  [UIUC LSATs Vol. 3](https://m-selig.ae.illinois.edu/pd/pub/lsat/vol3/E387C.DRG).
- [Official XFOIL by Mark Drela](https://web.mit.edu/drela/Public/web/xfoil/),
  version 6.99 used in this run.

The tunnel data are `[M]`; every XFOIL output and every computed comparison are `[D]`.

## 2.1 Measured anchors located by the airfoil evidence campaign (I-15, 2026-08-05) `[M]`

The calibration band now has direct physical anchors for the bubble physics it relies on:

| Source (NTRS) | Content | Relevance |
|---|---|---|
| **NASA-CR-186263** — Cole & Mueller (1990), *Experimental measurements of the laminar separation bubble on an Eppler 387 airfoil at low Reynolds numbers* | LDV boundary-layer + static pressure + flow visualization of the LSB on **the calibration airfoil itself** at Re 100 000 | Direct anchor for the Ncrit 10–12 band and for what XFOIL must reproduce |
| **AIAA 80-1440** — Mueller & Batill (1980) | LSB on NACA 66(3)-018 at **Re 40 000–400 000**, smoke visualization + force measurements | Covers the project's Reynolds band (3–5×10⁵) |
| **AIAA 86-1065** — O'Meara & Mueller (1986) | LSB structure at Re 50 000–200 000 | Bubble behavior vs. existing correlations at low Re |
| **AIAA 83-1671** — Jansen & Mueller (1983) | Hot-wire boundary-layer data, Re 80 000–400 000 | Bubble physics in-band |
| **AIAA 87-1271** — Stack, Mangalam & Berry (1987) | Heat-transfer sensor on NASA LRN(1)-1010, Re 50 000–300 000 | Nonintrusive separation detection |
| **NASA-CR-165803-VOL-1** — Carmichael (1981), *Low Reynolds number airfoil survey* | The classic critical-Re survey | Regime reasoning (I-01) |
| **AIAA J. 27(8)** — Schmidt & Mueller (1989), *Analysis of low Reynolds number separation bubbles using semiempirical methods* | Horton's method tested at Re 50 000–200 000 | Validation of the semiempirical bubble models behind XFOIL's transition logic |

**Negative result (recorded in I-15):** NTRS full-text search for reflexed-section
pitching-moment data returns **zero** results — no NASA/Gov measured polar exists for the
candidate family; the tunnel data gap at Re 3–5×10⁵ is real and E2 remains the closer.

# 3. Reproducible method

Tool: [`calculations/calibra_xfoil_e387.py`](../calculations/calibra_xfoil_e387.py).

1. Download coordinates and polar directly from UIUC.
2. Run XFOIL at the measured Reynolds numbers: 59 885, 99 744, 199 604, 299 856 and
   458 992 `[M]`.
3. Sweep Ncrit = 8–12 `[I]`.
4. Generate the pre-stall branch between α = 0–9° in 0.5° steps `[I]`.
5. Compare `Cd(Cl)` by interpolation for 0.25 ≤ Cl ≤ 0.85 `[I]`.

The metric is:

`factor = exp(RMSE(log(Cd_XFOIL / Cd_UIUC)))`

A factor of 1 is an exact match. A factor of 1.20 represents an RMS multiplicative
disagreement of about 20 % `[D]`.

The `Cl` window avoids mixing the drag fit with the stall prediction,
which XFOIL does not reproduce robustly at these Reynolds numbers. It is a methodological
choice `[I]`, declared and modifiable.

# 4. Preliminary result `[D]`

| Ncrit | Global factor | Re 59 885 | Re 99 744 | Re 199 604 | Re 299 856 | Re 458 992 |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | 1.502 | 1.896 | 1.509 | 1.197 | 1.143 | 1.129 |
| 9 | 1.351 | 1.569 | 1.395 | 1.162 | 1.123 | 1.118 |
| **10** | **1.208** | **1.297** | 1.252 | 1.122 | 1.098 | 1.107 |
| 11 | 1.209 | 1.384 | **1.110** | 1.076 | 1.071 | 1.091 |
| 12 | 1.245 | 1.424 | 1.248 | **1.026** | **1.041** | **1.071** |

## 4.1 Reading

- The best global fit of this grid is Ncrit = 10, with factor 1.208 `[D]`;
  Ncrit 11 is practically indistinguishable, at 1.209 `[D]`.
- The optimum drifts with Reynolds: Ncrit 10 at Re ≈ 60 000, Ncrit 11 at Re ≈ 100 000
  and Ncrit 12 from Re ≈ 200 000 `[D]`.
- In the project's range, Re ≈ 3–5×10⁵, Ncrit 12 gives the smallest grid disagreement:
  factors 1.041 and 1.071 `[D]`.

**There is no single Ncrit that reproduces the whole polar family.** Tuning a single
number and calling it "XFOIL calibration" hides a Reynolds dependence that the measured
data do show.

# 5. Consequence for B3

The candidate screening must:

1. run at minimum the Ncrit 10–12 band `[I]`;
2. publish the sensitivity of `Cm0`, `Clmax` and `L/D`, not only the most favorable curve;
3. treat Ncrit 12 as a smooth-tunnel reference at Re 3–5×10⁵ `[D]`, **not** as a
   measured representation of a printed PETG skin;
4. keep every resulting polar as `[D]`.

A printing roughness or seam can force transition earlier than the tunnel. That is why
this calibration reduces G2 but does not replace E2.

# 6. What is left to close B1

- Validate the Ncrit 10–12 band against a second independent physical E387 model
  (E387 E, UIUC Vol. 5), without re-tuning the metric.
- **Extract NASA-CR-186263 (E387 LSB, `[M]`, fulltext on NTRS) and compare the measured
  bubble position/length with the XFOIL Ncrit 10–12 prediction** — the calibration
  airfoil has now been measured at the bubble level (I-15/A9).
- Publish the sensitivity to paneling and α step.
- Separate the `Cd(Cl)` error and the `Cl(α)` error.
- Check that the same band does not systematically fail on another low-speed airfoil
  before using it as a general rule.

Until then B1 stays **partial** and G2 remains open. The full evidence campaign
(root/tip design, E205 and PW51 data availability) lives in
[I-15](I-15-airfoil-evidence-campaign.md).
