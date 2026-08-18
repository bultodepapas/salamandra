# Gap register

**What we do not know.** A gap is an unknown that prevents or degrades a decision.

It is as important as the decision register: the project rule is that **no `[E]` or `[I]` datum supports an irreversible decision without prior verification**, and this table is where the tally is kept.

| # | Gap | Impact | Status | Closes with |
|---|---|---|---|---|
| **G1** | Reference geometry: area, airfoil, twist | All calculations depend on S ≈ 0.282 m² `[E]` | 🔄 **Partial** — t/c measured `[M]`, planform missing | E1 |
| **G2** | No measured polars of the released r1 printed sections at local Re 1.2–5.1×10⁵ | Blocks flight-envelope acceptance, not CAD | 🔄 **Computational/CAD closure:** Salamandra r1 selected and generated (ADR-0041, I-15 §8); measured lift/drag/moment/stall remain open | E2 |
| **G3** | C_D0 breakdown by component | Prevents prioritizing parasitic-drag reduction | ⬜ Open | E2 |
| **G4** | Real torsional stiffness | ADR-0002 unverified | 🔄 `[E]` ±35 %, anchored to measured reference; printed-shell torsion bounds proposed (I-12) | E5, E7 |
| **G5** | Propeller wash effect on a thin airfoil at Re 4×10⁵ | ADR-0006 under dispute | ⬜ Open; literature bounds proposed (I-13) | I-13, comparative in-flight test |
| **G6** | **Sweep factor for divergence** | **Weakest link of the structural calculation** | ⬜ Open; X-29 data and theory bounds proposed (I-12) | **I-12 (bounds), E7** |
| **G7** | Flutter | Unverified. Sudden onset, no warning | ⬜ Open | E5 |
| **G8** | Neutral point and static margin | Blocks Phase 1 | 🔄 **Partial** — NP = 26.7 % MAC `[D]` by in-house VLM, **cross-checked by an independent Weissinger-L (28.0 % MAC, 3 mm agreement — I-15 §6.3)**; central-body effect still unquantified | I-07, I-15, C2 (body model) |
| **G9** | Altitude-loop coupling with pitch (*porpoising*) | **Threatens the validity of E7** | ⬜ Open | PID adjustment before testing |
| **G10** | **Directional stability Cnβ** — finless baseline estimated negative (FSW + nose boom); the fin/no-fin choice is an assumption, not a measured decision | The finless config is FC-dependent in yaw; the fin costs ≈ +10 % energy `[E]` | 🔄 **Bounded by calculation (I-20 `[D]`, `[E]` bands)** — finless −0.0006…−0.0015/deg; fin tiers V1a/V1b restore stability | **E-flight yaw test** (perturbation, Dutch-roll decay) + CAD side-area check (OP-21) |
| **G11** | **Dynamic gust loads and negative lift boundary** — rigid Part 23 transfer leaves the linear/stall domain; printed-aircraft CLmin is unknown | Blocks a complete V-n/gust envelope and traceable sizing of shell/attachments | 🔄 **Partial:** I-24 closes +6/−3 manoeuvre limit vs +9/−4.5 ultimate semantics and the positive V-n branch; gust screen is not an adopted load | Nonlinear unsteady gust model after S3 mass/stiffness data; validated B3 negative-polar extension/section evidence for CLmin; E9 blackbox `n_z(V)` correlation |

---

## Detail of the critical ones

### G1 — reference geometry

No manufacturer publishes wing area, airfoil or twist.

**Partially closed:** measurement on the Peregrine 840 mm file gives **t/c = 13.5 %** `[M]`. The full planform is still missing: c/4 sweep, taper and **twist distribution** — the latter is what validates or overturns ADR-0003.

Sensitivity: a ±13 % in S produces ±13 % in aspect ratio and wing loading.

### G6 — sweep factor

Revision 4 uses **0.55–0.85** at the selected −15° sweep, with its trend anchored to
NASA TP-1685. The numerical transfer to this printed section remains `[E]`. Together
with the unmeasured xEA/c = 0.30…0.45 bracket and GJ, it dominates the conservative
129.6 km/h result (I-21/I-23, OP-29/30).

### G8 — neutral point and static margin

**Largely closed.** On the −15° planform, the full VLM gives **NP = 25.72 % MAC /
−75.8 mm** `[D]`; independent Weissinger-L gives 27.0 % / −72.9 mm (2.9 mm spread).

Target CG: **17.72 % MAC / −93.8 mm** for 8 % static margin.

**Missing:** central-body model and measured flight NP. Elevon authority is calculated;
Salamandra r1 closes the computed trim band with 3.0° twist and −0.04°…+0.41°
neutral elevon. E2 must confirm the printed-airframe result.

See [I-21](../research/I-21-sweep-trade-and-elastic-axis-correction.md).

### G2 — now bounded with numbers

The I-07 analysis turns airfoil selection from an open problem into a bounded one:

| Requirement | Value |
|---|---|
| **R-AIRFOIL** | Coupled root/tip profile moment + twist shall trim at SM 8 % with neutral elevon within ±0.6° |
| **R-TWIST** | Printed wash-in = 3.0° for Salamandra r1; exposed for E2 refinement |

The coupled criterion replaces the earlier single-section Cm0 target, which ignored the
large negative low-Re tip moment and c² weighting. XFOIL endpoint `clmax` passes with
large computational margin, but printed roughness and three-dimensional stall remain E2
questions.

[I-06](../research/I-06-reflexed-airfoils.md) additionally bounds the transition model:
the E387 (C) calibration gives an Ncrit 10–12 band `[D]`, not a single value. At
Re ≈ 3–5×10⁵, Ncrit 12 minimizes the grid disagreement `[D]`, but it still needs validating
against a second physical model. **G2 is closed for CAD, not for flight acceptance.**

### G9 — porpoising

The Peregrine documentation reports altitude oscillation in INAV's RTH / Cruise / Loiter modes, with published corrective adjustments (Z position P from 30 to 15, pitch-throttle ratio from 10 to 5, level pitch from 0 to 3°).

**E7 depends on stabilized flight in Cruise.** If the aircraft oscillates, the trim deflection against q is noise.

### G11 — gust envelope

At 105 km/h, the legacy rigid-aircraft method predicts CLEAN +12.94/−10.94 g, but
the positive branch implies CL ≈ 1.37 versus the released CLmax 0.589. It therefore
flags missing nonlinear/unsteady physics rather than supplying a usable structural
load. The inverse linear sensitivity reaches the current negative limit at an equivalent
vertical gust of 5.10 m/s (5.19 m/s V1). These values are not surface-weather limits.

Closure requires the Article #1 mass distribution and S3 stiffness, a dynamic model
including plunge/flexibility/spanwise gust and unsteady stall, plus E9 blackbox
correlation. See I-24 and ADR-0044.

---

## Closed gaps

None yet. They will move here with the reference of the test that closed them and the resulting datum.
