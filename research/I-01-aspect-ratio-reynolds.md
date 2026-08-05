# I-01 — Aspect-ratio / Reynolds frontier

**Status:** Closed · **Feeds:** ADR-0004 (aspect ratio 6.0), ADR-0009 (drag decomposition)

## Question

Is there a finite optimal aspect ratio at low Reynolds, and through what mechanism?

## Methodological finding — the most important in the project

**Spedding & McArthur (2010) show that two different coefficients coexist in the literature under the same name:**

| | Definition | Content |
|---|---|---|
| **e_i** (non-viscous) | 1/(1+δ) | Only the elliptic-load deviation |
| **e_v** (Oswald) | 1/(1+δ+kπAR) | The above **+ aspect ratio + viscous polar shape** |

**e_v decreases with aspect ratio by algebraic construction, not by physics.** Using it leads to wrongly concluding that raising AR is counterproductive.

### Adopted formulation — never collapse into a single number

    C_D = C_d(C_l, Re)  +  C_L² / (π · AR · e_i)
          ─────────────     ──────────────────
          real 2-D polar         induced

Validity limit documented by the authors: the parabolic polar with a single Oswald **is only valid above Re ≈ 5×10⁶**. Our regime is three orders of magnitude below.

## Primary data

**Spedding & McArthur, J. Aircraft 47(1), 2010** — Eppler 387, AR 6, low-turbulence tunnel:

| Re | k (2-D polar) | e_v | e_i |
|---|---|---|---|
| 10–20 ×10³ | 0.24 | 0.22 | 0.53–0.76 |

- At C_L = 0.4: **C_D = 0.019 at Re 60×10³ versus 0.075 at Re 10×10³** — factor ~4 `[M]`
- Degraded lift slope: **C_lα ∝ Re^0.19** (2-D), **Re^0.18** (AR 6) `[M]`
- Physical cause: **advance of the separation point from the trailing edge**, even at small angles `[M]`

**Ananda, Sukumar & Selig, Aerosp. Sci. Tech. 42, 2015** — 10 flat-plate wings, AR 2–5, Re 60–160×10³:

- e_v from **0.81 (AR 2) to 0.33 (AR 5)** `[M]` — e_v-type magnitude
- **C_Lmax between 0.55 and 0.70** `[M]` ← hard constraint on the stall speed
- C_Dmin between 0.01 and 0.02 `[M]`
- **No detectable benefit of taper** (λ 0.5 and 0.75) at low Reynolds `[M]`
- Carmichael, cited: the laminar separation bubble dominates in **70×10³ ≤ Re ≤ 200×10³** `[M]`

**Hepperle** — reflexed airfoils, mandatory on a flying wing, **suffer more at low Reynolds because the reflex aggravates the adverse pressure gradient** `[M]`. Double penalty for this configuration.

## Conclusion

A finite optimal aspect ratio does exist, **but not for the mechanism usually cited**. The correct causal chain:

1. The induced term still falls as 1/(π·AR·e_i) — raising AR **does work**.
2. The viscous term k·C_L² **does not depend on aspect ratio**.
3. Therefore the benefit **saturates**.
4. At constant area, raising AR shortens the chord → lowers Re → raises k and C_D0 — and past a certain point **actively worsens**.

Point 4 generates the optimum. Point 3 makes it flat.

## Figure of merit

    (L/D)_max = ½ · √(π·e·AR / C_D0)  ∝  √(b² / (C_f · S_wet))

**The maximum L/D depends not on aspect ratio or area separately, but on wingspan² / wetted area.** Enlarging the wing without enlarging the rest improves twice over.

**Validation `[D]`:** applied to the Eta glider (AR 51.33; L/D 70) it solves C_D0 = 0.0081 — a coherent value for a polished competition composite. A typical foam wing is between 0.025 and 0.035.

## Transfer limit

⚠️ The cited tests cover Re 10–160×10³. The project's cruise regime is ≈ 4×10⁵. **Magnitudes do not transfer; trends and methodology do.**

## Associated correction

**C1** — it was initially claimed that the Oswald factor collapses with aspect ratio for physical reasons, invalidating raising AR. It is largely a **definition artifact**.

## Sources

1. Spedding, G. R. & McArthur, J. — *Span Efficiencies of Wings at Low Reynolds Numbers*. J. Aircraft 47(1), 2010, pp. 120–128. DOI 10.2514/1.44247
2. Ananda, G. K., Sukumar, P. P. & Selig, M. S. — *Measured aerodynamic characteristics of wings at low Reynolds numbers*. Aerosp. Sci. Tech. 42, 2015, pp. 392–406.
3. Hepperle, M. — *MH AeroTools*: laminar separation bubbles and turbulators.
