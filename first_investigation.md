# Forward-swept FPV flying wing — Base design document

**Status:** Initial research phase closed. Design not started.
**Revision:** 1.0 — 27 July 2026
**Scope:** Data consolidation, analytical framework, decisions made and open gaps.

---

## Confidence convention

Every quantitative claim carries one of these tags:

| Tag | Meaning |
|---|---|
| **[M]** | Measured and published by a primary source |
| **[D]** | Derived by calculation from [M] data |
| **[E]** | Estimated on declared assumptions |
| **[I]** | Reasoned inference, not verified |

No [E] or [I] datum should be used as the basis of an irreversible decision without prior verification.

---

# 1. Objective and problem state

## 1.1 Pending decision that blocks everything else

**The design objective is not fixed.** There are two mutually exclusive objective functions:

| Branch | Metric | Planform consequences |
|---|---|---|
| **A — Fast cruise** | Wh/km at 90–120 km/h | Low AR (5–7), high wing loading (55–70 g/dm²), focus on parasitic drag |
| **B — Endurance** | Minutes of flight | High AR (8–12), low wing loading (25–35 g/dm²), focus on induced drag |

They are not a continuous trade-off: they diverge from the first stroke. Everything that follows is calibrated on branch A, because that is what the analyzed reference platforms represent. **If the objective is B, a good part of the decisions in section 6 must be re-evaluated.**

---

# 2. Reference platforms

## 2.1 TBS Mojito — data published by the manufacturer [M]

| Parameter | Value |
|---|---|
| Wingspan | 1300 mm |
| AUW | ≥ 1800 g |
| Declared endurance | 60 min / 100 km |
| Cruise speed | 90–120 km/h |
| Maximum speed | > 200 km/h |
| Battery | 6S–8S; max. 70 × 50 × 230 mm; optimal Li-Ion 8S1P 5000 mAh |
| Motor | 3220, 1000 KV |
| Propeller | 8×4.5 or 7×12 |
| Servos | 23 mm; 2 units (4 with airbrakes) |
| Construction | High-density EPP, carbon reinforcement, injection-molded plastic edges |
| Price (kit) | USD 189.95 |

**From the manual (rev. 2025-11-04) [M]:**

- CG: raised line on the belly, ≈ 10 mm behind the leading edge. Explicit recommendation to fly with a forward CG.
- Elevon deflection: pitch ±15 mm; roll 20 mm up / 15 mm down.
- ESC: 3–12S, current limit 204 A, timing 15°, PWM 24–48 kHz, 14 poles.
- Airbrakes: produce a nose-down moment when deployed; requires compensation.

**Not published:** wing area, aspect ratio, sweep angle, twist, airfoil, coordinates. The manufacturer only states that *the airfoil derives from dynamic soaring gliders*.

## 2.2 TBS Mojito — measured flight data [M]

Source: Noah Waldner, 3.5 months of testing, hundreds of batteries.

- Comfortable cruise at 70–80 km/h with ≈ 8 A on 8S.
- ≈ 50 km of travel with two 4S 2300 mAh LiPo in series.

## 2.3 Nemesis (StuntDouble) [M]

| Parameter | Value |
|---|---|
| Wingspan | 1200 mm |
| Configuration | Flying wing, forward sweep, twin tractor |
| Airfoil | PW51 |
| Construction | 3D printing, open STL files |
| Cost | Free |

It belongs to a family of designs by the same author that allows a **quasi-controlled
comparison**: same manufacturing family and comparable AR, but not the same scale,
airfoil or propulsion. See correction C19 and
[I-08](research/I-08-stuntdouble-family.md).

| Model | Planform | Note |
|---|---|---|
| Interceptor V1/V2 | Forward sweep, twin engine | Origin of the line |
| **Eliminator** | Forward sweep, twin engine | **Record: 360 km/h, Nov. 2025 (P. Heiniger)** |
| Nemesis | Forward sweep, twin engine | FPV cruise version |
| Stinger V2 | Straight plank, twin engine, 1.3 m | Comparator without sweep; PW75 airfoil |
| Stormbird | Straight plank, 1.1 m | Comparator without sweep; PW75 airfoil and single pusher |

---

# 3. Energy analysis

## 3.1 Cross-validation of the Mojito [D]

Two independent specific-energy sources:

| Source | Energy | Distance | Wh/km |
|---|---|---|---|
| Waldner (measured) | 68.1 Wh (8S 2300 mAh LiPo) | 50 km | **1.36** |
| TBS (declared) | 144.0 Wh (8S1P 5000 mAh Li-Ion) | 100 km | **1.44** |

**Agreement within 5 %.** The official TBS figure is independently verified. **1.40 Wh/km** is adopted as the reference value.

*Consistency note:* Waldner's two data points (8 A at 70–80 km/h, and 50 km with 68 Wh) are only mutually compatible if the 50 km flight was done at a speed considerably higher than 80 km/h. They correspond to different operating points, not the same flight.

## 3.2 Specific-energy comparison [D]

Normalizing by mass removes the size effect:

| Platform | Wh/km | Mass | **Wh/(km·kg)** | Speed |
|---|---|---|---|---|
| Sonicmodell AR Wing 1000 | 0.78 [E] | 1.0 kg | **0.78** | ~55 km/h |
| **TBS Mojito** | 1.40 [D] | 1.9 kg | **0.74** | 100–150 km/h |
| Mini Talon | 1.20 [M] | 1.3 kg | **0.92** | 50 km/h |
| Solar Impulse 2 | 160 [D] | 2300 kg | **0.070** | 70 km/h |

### Conclusion 3.2 — The Mojito is not more efficient, it is faster

The Mojito consumes **the same energy per kilometer and kilogram** as a USD 40 foam wing. Its achievement is not reducing specific consumption: it is **sustaining it at two or three times the speed**. That is exactly what a dynamic-soaring-lineage airfoil buys — not a better maximum L/D, but preserving the L/D at the right end of the polar.

**Design implication:** if the mission does not require speed, the Mojito architecture offers no energy advantage over far cheaper alternatives.

## 3.3 Inverse L/D solution [D]

From the specific energy, the real aerodynamic efficiency is solved:

$$\frac{E/d}{W} = \frac{1}{\eta}\cdot\frac{D}{W} \quad\Longrightarrow\quad \left(\frac{L}{D}\right)_{aero} = \frac{1}{\eta}\left(\frac{L}{D}\right)_{effective}$$

| Platform | Effective L/D | Assumed η | **Aerodynamic L/D** |
|---|---|---|---|
| TBS Mojito | 3.7 | 0.50 [E] | **7.4** |
| AR Wing | 3.5 | 0.50 [E] | **7.0** |
| Mini Talon | 3.0 | 0.50 [E] | **5.9** |
| Solar Impulse 2 | 39.2 | 0.80 [E] | **49** |

**The Mojito L/D in fast cruise is ≈ 7.4**, well below its maximum L/D (which occurs at a lower speed). The ~7× difference against the Solar Impulse quantifies the combined scaling penalty: low Reynolds, low aspect ratio and a mediocre propulsion chain.

⚠️ The Solar Impulse value depends on coarse inputs (15 mean CV over 24 h, 70 km/h mean) and must be taken as an order of magnitude, not as a datum. It is probably an upper bound.

---

# 4. Adopted analytical framework

## 4.1 Master equation

For electric propulsion, range decomposes into three independent multiplicative factors:

$$R = \underbrace{\frac{E_{esp}}{g}\cdot\frac{m_{bat}}{m_{total}}}_{\text{energy}} \cdot \underbrace{\eta_{total}}_{\text{propulsion}} \cdot \underbrace{\frac{L}{D}}_{\text{aerodynamics}}$$

Doubling any of the three doubles the range. None compensates the deficiency of another.

## 4.2 Drag decomposition — mandatory formulation

**This is the most important methodological decision in the document.** Spedding & McArthur (2010) show that two different coefficients coexist in the literature under the same name:

| | Definition | Content |
|---|---|---|
| **e_i** (non-viscous) | $1/(1+\delta)$ | Only the elliptic-load deviation |
| **e_v** (Oswald) | $1/(1+\delta+k\pi AR)$ | The above **+ aspect ratio + viscous polar shape** |

**e_v decreases with aspect ratio by algebraic construction**, not by physics. Using it leads to wrongly concluding that raising AR is counterproductive.

**Adopted formulation** — separate the terms and never collapse them into a single number:

$$C_D = \underbrace{C_d(C_l, Re)}_{\text{real polar table}} + \underbrace{\frac{C_L^2}{\pi\,AR\,e_i}}_{\text{induced}}$$

Validity limit documented by the authors: the parabolic polar with a single Oswald **is only valid above Re ≈ 5×10⁶**. Our regime is three orders of magnitude below.

## 4.3 Figure of merit for maximum L/D

$$\left(\frac{L}{D}\right)_{max} = \frac{1}{2}\sqrt{\frac{\pi\,e\,AR}{C_{D0}}} \quad\propto\quad \sqrt{\frac{b^2}{C_f\,S_{wet}}}$$

The maximum L/D does not depend on aspect ratio or area separately, but on the ratio **wingspan² / wetted area**. Enlarging the wing without enlarging the rest improves twice over.

**Validation of the relation [D]:** applied to the Eta glider (AR 51.33; L/D 70), it solves for **C_D0 = 0.0081**. It is a physically consistent value for a polished composite competition glider, which confirms the formula. A typical foam wing is between 0.025 and 0.035 — three to four times worse.

---

# 5. Findings by research thread

## 5.1 Thread 1 — Aspect-ratio / Reynolds frontier

### Primary data

**Spedding & McArthur (J. Aircraft 47(1), 2010)** — Eppler 387, AR 6, low-turbulence tunnel:

| Re | k (2-D polar) | resulting e_v | e_i |
|---|---|---|---|
| 10–20 ×10³ | 0.24 | **0.22** | 0.53–0.76 |

- At C_L = 0.4: **C_D = 0.019 at Re 60×10³ versus 0.075 at Re 10×10³** — factor ~4. [M]
- Degraded lift slope: **C_lα ∝ Re^0.19** (2-D) and **Re^0.18** (AR 6). [M]
- Physical cause identified: **advance of the separation point from the trailing edge**, even at small angles of attack. [M]

**Ananda, Sukumar & Selig (Aerosp. Sci. Tech. 42, 2015)** — 10 flat-plate wings, AR 2–5, Re 60–160×10³:

- e_v from **0.81 (AR 2) to 0.33 (AR 5)** [M] — e_v-type magnitude, see §4.2.
- C_Lmax between 0.55 and 0.70 [M].
- C_Dmin between 0.01 and 0.02 [M].
- **No detectable benefit of taper** (λ 0.5 and 0.75) at low Reynolds [M].
- Carmichael, cited: the laminar separation bubble dominates in **70×10³ ≤ Re ≤ 200×10³** [M].

**Hepperle** — reflexed airfoils, mandatory on a flying wing, **suffer more at low Reynolds because the reflex aggravates the adverse pressure gradient** [M]. Double penalty for our configuration.

### Conclusion 5.1

A finite optimal aspect ratio does exist, but **not for the mechanism usually cited**. The correct causal chain is:

1. The induced term still falls as 1/(π·AR·e_i) — raising AR **does work**.
2. The viscous term k·C_L² **does not depend on aspect ratio** and does not improve.
3. Therefore the benefit of raising AR **saturates**.
4. At constant area, raising AR **shortens the chord → lowers Re → raises k and C_D0** — and past a certain point actively worsens.

Point 4 is what generates the optimum. Point 3 is what makes it flat.

⚠️ **Transfer limit:** the cited tests cover Re 10–160×10³. Our cruise regime is ≈ 4×10⁵. **Magnitudes do not transfer**; trends and methodology do.

## 5.2 Thread 2 — Tailless forward sweep

### Trim mechanism

A tailless wing requires positive pitching moment. There are only two paths: an airfoil with positive C_m0 (reflex), or a combination of sweep and twist. For sweep, the two solutions are **symmetric**:

| Planform | Required twist | Tip loading at zero lift |
|---|---|---|
| Aft sweep | **Wash-out** (tip down) | Downward — subtracts lift |
| **Forward sweep** | **Wash-in** (tip up) | Upward — adds lift |

*(Corrects the earlier claim that forward sweep depends exclusively on airfoil reflex.)*

### Quantifiable advantage: trim drag

Documented in configuration patents US 4.545.552 and US 4.674.709: in forward sweep the balance force acts **upward and ahead of the CG**, so the total lift required is essentially equal to the weight. In aft sweep, balance requires negative loading at the tips and the wing must generate **more** than the aircraft weighs.

⚠️ They are patent documents, not peer-reviewed literature. The physical argument is correct and verifiable; **the magnitude of the benefit is not quantified by an independent source**.

### Secondary advantage: stall behavior

The spanwise flow runs from tip to root. **The root stalls first**, and the outer elevons keep effectiveness by remaining in high-energy air. [M, multiple independent sources]

For a flying wing this weighs double: the elevons are the entirety of the control.

### Dominant risk: aeroelastic divergence

The aerodynamic center lies **ahead of** the torsional stiffness center. The load produces nose-up twist → more angle of attack → more lift → more twist. Positive feedback up to structural failure. [M]

Known remedies: increase stiffness (weight penalty) or **aeroelastic tailoring of the layup** (the X-29 solution). [M]

**Dangerous coupling identified [I]:** a tailless forward-swept wing **needs wash-in for trim**, and aeroelastic divergence **also produces wash-in**. The two effects add up and the second grows with dynamic pressure. Consequence: **the trim state shifts with speed**. An aft-swept wing has the opposite sign and self-damps.

This explains three Mojito characteristics that previously had no explanation: extremely forward CG, recommendation to move it even further forward, and deliberately short elevon deflections.

Additional documented risk: with sufficient aeroelastic deflection, **the tips can stall first, cancelling the main forward-sweep advantage** — precisely when it is most needed. [M]

### Empirical evidence that bounds the risk [D]

The **Eliminator** (same family, forward sweep, 3D printed) reached 360 km/h. The dynamic pressure is **13 times** that of the Mojito cruise (6,100 Pa versus 470 Pa). If the divergence speed were near the operating envelope, it would have manifested.

**Explanatory hypothesis [I]:** a 3D-printed wing is a **closed shell — a torsion box by construction**. The torsional stiffness of a closed section exceeds foam with embedded rods by orders of magnitude. For forward sweep, where torsional stiffness is the critical parameter, 3D printing is probably **superior** to molded foam.

This reverses an initial assumption and is the finding with the greatest practical consequence in the document.

### ⚠️ Source-quality warning

A secondary source (Grokipedia) claims that forward sweep *delays* aeroelastic divergence. **It contradicts all the primary and peer-reviewed sources consulted, including the X-29 program documentation. It must not be used.**

## 5.3 Thread 3 — Propulsion chain

### Primary data

**Brandt & Selig (AIAA 2011-1255)** — 79 propellers, 9–11 in, Re 50–100×10³ at the 75 % station:

- Peak efficiency between **0.65 (good) and 0.28 (bad)** — factor 2.3. [M]
- Efficiency **systematically improves with rpm**, via the Reynolds effect. [M]
- Extreme case: the Master Airscrew G/F 11×4 **nearly doubles** its peak efficiency over the tested rpm range. [M]
- Prior work: hobby propellers give **7.5 %–15 % less** than 36 in propellers with similar P/D. [M]
- Very thin blades can enter **flutter** at high J and lose performance. [M]

### Own extraction from the UIUC database [D]

Peak efficiency at ≈ 6000 rpm and the corresponding flight speed:

| Propeller | P/D | η max | Optimal J | V @6000 rpm | V @16000 rpm |
|---|---|---|---|---|---|
| APC-E 8×4 | 0.50 | 0.600 | 0.481 | 35 km/h | 94 km/h |
| APC-E 8×6 | 0.75 | 0.678 | 0.689 | 50 km/h | 134 km/h |
| **APC-E 8×8** | 1.00 | **0.731** | 0.784 | 57 km/h | 153 km/h |
| APC-E 9×6 | 0.67 | 0.683 | 0.583 | 48 km/h | 128 km/h |
| APC-E 10×7 | 0.70 | 0.705 | 0.576 | 53 km/h | 140 km/h |
| APC-Sport 8×10 | 1.25 | 0.513* | 0.596 | 44 km/h | 116 km/h |

\* Truncated measurement range; efficiency was still rising.

**Readings:**

1. **Pitch dominates.** From 8×4 to 8×8, same diameter: +22 % of peak efficiency.
2. **The optimal speed is a propeller×rpm product, not a propeller property.** The same 8×8 peaks at 57 km/h at 6000 rpm and at 153 km/h at 16000 rpm.
3. **The Mojito's 7×12 lacks data support.** Its P/D is 1.71; the maximum of UIUC vol. 1 is around 1.25, and that case did not even reach its peak within the measured range.

### Balance closure [D]

| Component | Range |
|---|---|
| Propeller at its optimal J | 0.65 – 0.73 |
| Well-sized motor + ESC | ≈ 0.85 |
| **Theoretical product** | **0.55 – 0.62** |
| **Real value solved from flight (§3.3)** | **≈ 0.50** |

The gap indicates that **the propeller does not operate at its optimal advance ratio**. Recoverable margin: moving from 0.50 to 0.60 is **+20 % range without modifying the aerodynamics**.

---

# 6. Design decisions

| # | Decision | Rationale | Confidence | Reversible |
|---|---|---|---|---|
| **D1** | Adopt **forward-swept flying wing** configuration | Trim advantage (§5.2) + root-first stall + independent convergence of two designers | High | No |
| **D2** | **Closed-shell** structure (3D printing or molded composite). **Reject foam with rods** | Torsional stiffness governs divergence; Eliminator evidence at 360 km/h | Medium [I] | No |
| **D3** | Geometric twist of **wash-in** type; magnitude to be determined | Equilibrium requirement in forward sweep (§5.2) | High | Partial |
| **D4** | Target aspect ratio **6–8** | Flat optimum by saturation (§5.1); penalizes shortening chord below Re 3×10⁵ | Medium [E] | No |
| **D5** | **Reflexed and thin** airfoil; **selection deferred** until polars at the design Re are available | No published polars of reflexed airfoils at Re 3–5×10⁵ exist | — | Yes |
| **D6** | **Single pusher motor** preferred over twin tractor | Higher blade Re with a single large propeller; wing in clean air preserves laminar flow | Low [I] | Yes |
| **D7** | Propeller of **P/D ≈ 0.8–1.0**, matched by J to cruise speed, at high rpm | UIUC data (§5.3); blade Re rises with rpm | High | Yes |
| **D8** | **Reject the 7×12 propeller** unless experimentally validated | P/D 1.71 outside all published data | High | Yes |
| **D9** | **Always** use the §4.2 decomposition. Never a single Oswald | Spedding & McArthur; parabolic-polar validity only above Re 5×10⁶ | High | No |
| **D10** | **Fix branch A or B before drawing geometry** | §1.1 | — | **Pending** |

## 6.1 Notes on the low-confidence decisions

**D6 is under dispute.** The twin tractor has legitimate arguments in its favor: larger total disk area, yaw control via differential thrust, redundancy, and mass balancing against flutter. And the wash over the wing has an ambiguous sign — it may **suppress the laminar separation bubble**, which is the mechanism Hepperle identifies as the main penalty of reflexed airfoils. **There is no data to resolve it.** It is the open question of highest experimental value.

**D2 rests on an inference**, not a measurement. It is validated with a half-hour bench test: apply a known torque at the tip and measure the twist angle, comparing both constructions.

---

# 7. Data gaps

| # | Gap | Impact | Closing path |
|---|---|---|---|
| **G1** | No manufacturer publishes wing area, airfoil or twist | All §3 calculations depend on S ≈ 0.30 m² [E] | **Measure on the Nemesis STL meshes** |
| **G2** | No measured polars of reflexed airfoils at Re 3–5×10⁵ | Blocks D5 | XFOIL/XFLR5 with calibrated transition, or own test |
| **G3** | C_D0 breakdown by component unknown | Prevents prioritizing parasitic-drag reduction | Glide test (§8) |
| **G4** | Torsional stiffness of both constructions unmeasured | D2 unverified | Bench twist test |
| **G5** | Effect of propeller wash on a thin airfoil at Re 4×10⁵ | D6 unresolved | Comparative in-flight test |

## 7.1 Sensitivity of G1

Uncertainty in the wing area propagates to everything:

| S [m²] | AR | Wing loading | Mean chord | Re @100 km/h |
|---|---|---|---|---|
| 0.26 | 6.50 | 73 g/dm² | 200 mm | 3.7×10⁵ |
| **0.30** | **5.63** | **63 g/dm²** | **231 mm** | **4.3×10⁵** |
| 0.34 | 4.97 | 56 g/dm² | 262 mm | 4.8×10⁵ |

A ±13 % in S produces ±13 % in aspect ratio and wing loading. **Closing G1 is an absolute priority.**

---

# 8. Proposed experimental program

Ordered by result/effort ratio.

### E1 — Geometry extraction from STL meshes
**Effort:** low. **Closes:** G1, and partially G2 and the validation of D3.

Cut sections of the Nemesis mesh at different spanwise stations. Obtain airfoil coordinates, area, aspect ratio, taper, c/4 sweep and **twist distribution** — verifying whether it actually uses wash-in and in what magnitude.

Repeat on the Stormbird or Stinger (*plank*, same author and manufacturing family)
for a **quasi-controlled planform comparison**. The PW51/PW75 airfoil and the
propulsion do not remain constant, so the sweep effect cannot be causally isolated.
See correction C19 and [I-08](research/I-08-stuntdouble-family.md).

### E2 — Glide test for a complete polar
**Effort:** medium. **Closes:** G3; feeds all three threads.

Glide flights with the motor off at stabilized speeds, recording descent rate with the flight controller's barometer. Produces the real polar of the complete aircraft without a wind tunnel. It is the only instrument that separates propulsive losses from aerodynamic losses.

### E3 — Propeller-matching sweep
**Effort:** low. **Closes:** the D7 gap; realizes the +20 % of §5.3.

Stabilized flight at fixed speed, logging current, for 3–4 diameter/pitch combinations. Compare against the J predicted by the UIUC database.

### E4 — Torsional stiffness test
**Effort:** low. **Closes:** G4, validates D2.

Known torque applied at the tip, twist-angle measurement, both constructions. Allows estimating the divergence-speed margin.

---

# 9. Correction register

Errors made during the research and corrected. They are documented because they affected intermediate conclusions.

| # | Error | Correction | Origin |
|---|---|---|---|
| C1 | It was claimed that the Oswald factor collapses with aspect ratio for physical reasons, and that this invalidates raising AR | It is largely a **definition artifact**: e_v decreases with AR by algebraic construction. Raising AR does work; the real effect is **saturation** and the chord→Re coupling | Spedding & McArthur (2010) |
| C2 | It was claimed that forward sweep depends exclusively on the airfoil C_m0 because twist cannot be used | It can and should use **wash-in**. The two planforms are symmetric solutions | Tailless-trim literature |
| C3 | 3D printing was assumed to be the structurally weak option | It is a **closed shell** = torsion box. Probably superior to foam for forward sweep | Inference + Eliminator evidence |
| C4 | **Arithmetic error:** solving for the Solar Impulse L/D, η was multiplied instead of divided. L/D ≈ 31 was reported | The correct value is **L/D ≈ 49**. The relation is L/D_aero = L/D_eff / η | Numerical verification |
| C5 | The Mojito maximum L/D was estimated at ≈ 11 | The value solved from real flight data is **≈ 7.4 in fast cruise** — a different operating point than the maximum L/D | Waldner data |

---

# 10. Sources

**Peer-reviewed**

1. Spedding, G. R. & McArthur, J. — *Span Efficiencies of Wings at Low Reynolds Numbers*. Journal of Aircraft 47(1), 2010, pp. 120–128. DOI 10.2514/1.44247
2. Ananda, G. K., Sukumar, P. P. & Selig, M. S. — *Measured aerodynamic characteristics of wings at low Reynolds numbers*. Aerospace Science and Technology 42, 2015, pp. 392–406.
3. Brandt, J. B. & Selig, M. S. — *Propeller Performance Data at Low Reynolds Numbers*. 49th AIAA Aerospace Sciences Meeting, AIAA 2011-1255.

**Databases**

4. UIUC Propeller Database, vols. 1–4. Brandt, Deters, Ananda, Dantsker & Selig, University of Illinois.
5. Hepperle, M. — *MH AeroTools*: laminar separation bubbles and turbulators.
6. aerodesign.de — airfoil database for flying and tailless wings.

**Manufacturer documentation**

7. Team BlackSheep — TBS Mojito, product datasheet and manual rev. 2025-11-04.
8. StuntDouble — Nemesis and associated family, Thingiverse.

**Patents** *(not peer-reviewed — use with the reservation of §5.2)*

9. US 4.545.552 and US 4.674.709 — tailless forward-sweep configuration.

**Independent flight test**

10. Waldner, N. — TBS Mojito test report, 3.5 months.

---

# 11. Executive summary

1. The **forward-swept flying wing architecture is justified** by trim and stall behavior, not by packaging. Two independent designers converged on it.
2. The dominant risk **is not aerodynamic but structural**: torsional stiffness against aeroelastic divergence. That reorders the project's priorities.
3. The reference platform **is not energy-efficient** — it is fast at the same specific energy cost as far cheaper alternatives. The architecture is only justified if the mission demands speed.
4. The **propulsion chain** is the lever with the greatest immediate return: +20 % of available range through propeller matching, without touching the aerodynamics.
5. The transversal obstacle is the **absence of published geometry**. The Nemesis open files solve it: they turn a speculative-simulation problem into direct measurement.

**Recommended next action:** run E1 (geometry extraction) and resolve D10 (branch A or B). Both are prerequisites of any design stroke.
