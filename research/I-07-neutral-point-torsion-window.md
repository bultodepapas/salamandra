# I-07 — Neutral point, static margin and torsion window

> **2026-08-17 supersession notice:** the −20° planform numbers in this historical
> thread are superseded by [I-21](I-21-sweep-trade-and-elastic-axis-correction.md) and
> ADR-0040. The current −15° results are xNP = −75.8 mm (VLM), −72.9 mm
> (Weissinger), xCG = −93.8 mm and 3.0° printed twist + 0.59° equivalent reflex.

**Status:** Open — preliminary result `[D]` · **Partially closes:** G8
**Feeds:** ADR-0003 (twist), ADR-0032 (R-NP), and the G2 airfoil requirement
**Tool:** [`calculations/vlm_ala_volante.py`](../calculations/vlm_ala_volante.py), [`calculations/ventana_torsion.py`](../calculations/ventana_torsion.py)

---

# 1. Method

In-house vortex lattice (VLM), 40 spanwise panels with cosine distribution × 6 in chord, horseshoes with the bound vortex at the panel c/4 and control point at 3c/4. Linearized boundary condition.

## Validation

Straight AR 6 wing, no sweep or twist:

| | Calculated | Theoretical | Error |
|---|---|---|---|
| CL_α | 4.274 /rad | 4.527 /rad (Helmbold) | −5.6 % |
| Neutral point | 24.0 % MAC | 25 % MAC | −1.0 point |

Acceptable for preliminary sizing. **The mesh is coarse in chord**; refining it would bring CL_α closer to the theoretical value.

> **Correction detected during validation:** the first version returned the non-dimensionalized moment without dividing by the MAC, which introduced a spurious chord factor in the neutral point. The validation case exposed it — a straight wing must give the NP at c/4, and it gave ~0.

---

# 2. Neutral point — Cruise configuration

Planform: b = 1300 mm · S = 0.282 m² · AR 6.0 · λ = 0.50 · Λ_c/4 = −20°
→ c_root 289 mm · c_tip 145 mm · **MAC 225 mm**

| Result | Value |
|---|---|
| **Neutral point** | **26.7 % MAC** |
| Absolute position | 101 mm **ahead of** the root c/4 |
| CL_α | 4.187 /rad |

**The NP ends up ahead of the root leading edge.** It is the expected behavior of a pronounced forward sweep, and the reason the balancing of this configuration is not intuitive.

## Target CG

| Static margin | x_CG (% MAC) |
|---|---|
| 6 % | 20.7 % |
| **8 %** | **18.7 %** |
| 10 % | 16.7 % |
| 12 % | 14.7 % |

---

# 3. The torsion window

Conditions: AUW 1620 g (6S1P) · 57 g/dm² · cruise 95 km/h · stall 45 km/h

| | Value |
|---|---|
| Cruise CL | 0.132 |
| Required CL_max | 0.589 |
| Section cl_max `[M]` | 0.65 (Ananda et al., 0.55–0.70) |
| **Wash-in yield** | **Cm0 = +0.00338 per degree** |

## 3.1 Lower limit — trim

Tailless equilibrium condition: `Cm0 = CL · StaticMargin`

| Static margin | Required Cm0 | **Twist only** | **With airfoil Cm0 = +0.010** |
|---|---|---|---|
| 6 % | +0.0079 | 2.34° | 0° |
| **8 %** | **+0.0106** | **3.13°** | **0.17°** |
| 10 % | +0.0132 | 3.91° | 0.95° |
| 12 % | +0.0159 | 4.69° | 1.73° |

## 3.2 Upper limit — tip stall

Section cl distribution at the required CL_max condition:

| wash-in | Position of max cl | cl root | cl tip | local max cl | Margin to 0.65 |
|---|---|---|---|---|---|
| 0° | **27 % b/2** | 0.616 | 0.105 | 0.633 | +0.017 |
| 2° | 49 % b/2 | 0.586 | 0.115 | 0.628 | +0.022 |
| 3° | 56 % b/2 | 0.571 | 0.120 | 0.633 | +0.017 |
| 4° | **62 % b/2** | 0.556 | 0.125 | 0.641 | +0.009 |
| 5° | 68 % b/2 | 0.542 | 0.130 | 0.651 | **−0.001** ❌ |
| 6° | 68 % b/2 | 0.527 | 0.135 | 0.663 | −0.013 ❌ |

---

# 4. Conclusion — the central Phase 1 result

**The window exists, but it is narrower than correction C2 suggested.**

The finding is not the hard 5° limit, but **how the load peak moves**:

| wash-in | cl peak | Consequence |
|---|---|---|
| 0° | 27 % b/2 | The root stalls first ✅ |
| 4° | 62 % b/2 | Elevon zone ⚠️ |
| 5°+ | 68 % b/2 | Tip stall ❌ |

> **Wash-in trades trim against the advantage that justified choosing forward sweep.**
>
> With pure twist, balancing at 10 % static margin requires 3.9°, and that moves the load peak to 62 % of half-span — right where the elevons are.

## 4.1 Derived requirement on the airfoil

**The airfoil must provide most of the trim. Twist does the fine-tuning.**

| # | Requirement |
|---|---|
| **R-AIRFOIL** | **Airfoil Cm0 ≥ +0.008**, preferably +0.010–0.015 |
| **R-TWIST** | **Wash-in ≤ 2.5°**, to keep the load peak inside 50 % of half-span |

This **bounds G2 with a number**: airfoil selection stops being open.

## 4.2 The tension this creates

The reflex that gives positive Cm0 **costs cl_max**, and the margin is already thin:

- With a section cl_max of 0.65, the wing reaches **CL_max ≈ 0.60** — a 92 %, by non-elliptic distribution.
- That gives V_stall = 44.5 km/h, **just inside** the ≤ 45 requirement.
- If reflex lowers cl_max to 0.60, V_stall rises to **46.6 km/h** and the requirement is violated.

**R-AIRFOIL and the stall-speed requirement compete directly.** It is the conflict Phase 1 must resolve, and it is now quantified.

---

# 5. R-NP — neutral-point drift in the modular family

Keeping root chord, taper and sweep:

| Config | b | S | AR | **NP (% MAC)** |
|---|---|---|---|---|
| Sport | 1100 mm | 0.238 m² | 5.07 | **26.0 %** |
| **Cruise** | 1300 mm | 0.282 m² | 6.00 | **26.7 %** |
| Range | 1600 mm | 0.347 m² | 7.38 | **27.6 %** |

**Total spread: 1.6 MAC points.** Much smaller than feared.

## Compensation with sweep

| Config | Sweep | NP |
|---|---|---|
| 1100 mm | −24° | 26.8 % |
| 1300 mm | −20° | 26.7 % |
| 1600 mm | −18° | 27.1 % |

**A ±2–4° sweep adjustment aligns the three panels within 0.5 % of MAC.**

> **R-NP is easy to meet.** It does not force redesigning each panel: adjusting the sweep is enough, and sweep is additionally a free parameter in each set. It is the best news of this analysis for the modular architecture.

---

# 6. Declared limitations

⚠️ Everything above is `[D]` on a linear non-viscous model. Before freezing geometry:

| Limitation | Probable effect |
|---|---|
| **No viscosity** | The VLM does not predict stall. The cl_max criterion is an indicator, not a prediction |
| **cl_max assumed constant across the span** | **Optimistic.** The tip has half the chord → half the Re → **lower real cl_max** (see [I-01](I-01-aspect-ratio-reynolds.md)). **The tip-stall margin is worse than calculated** |
| No central body | The fuselage adds lift and moves the NP forward |
| Coarse chord mesh | CL_α 5.6 % low |
| Assumed airfoil Cm0 | Must come from G2 with calibrated polars |
| No sweep effects on cl_max | Forward sweep modifies the real stall distribution |

**The variable-cl_max-with-Re limitation is the most serious** and acts in the dangerous direction: it worsens the upper window limit and reinforces the conclusion that the airfoil must be leaned on, not the twist.

---

# 7. What remains

1. **Verify the NP with a second independent method** (C2 of the Phase 1 plan). Two methods that disagree = error in one.
2. **Close G2** with calibrated polars, to have the real Cm0 and cl_max of the candidate airfoil.
3. **Repeat with cl_max variable across the span**, as a function of local Re.
4. **Incorporate the central body** when geometry exists.
5. **Verify elevon authority** (C6 of the plan) — still undone.
