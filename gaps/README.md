# Gap register

**What we do not know.** A gap is an unknown that prevents or degrades a decision.

It is as important as the decision register: the project rule is that **no `[E]` or `[I]` datum supports an irreversible decision without prior verification**, and this table is where the tally is kept.

| # | Gap | Impact | Status | Closes with |
|---|---|---|---|---|
| **G1** | Reference geometry: area, airfoil, twist | All calculations depend on S ≈ 0.282 m² `[E]` | 🔄 **Partial** — t/c measured `[M]`, planform missing | E1 |
| **G2** | No measured polars of reflexed airfoils at Re 3–5×10⁵ | Blocks airfoil selection | 🔄 **Partial** — XFOIL bounded with E387; aerodesign.de database reviewed (I-11); still to screen and measure reflexed airfoils | I-06, I-11, E2 |
| **G3** | C_D0 breakdown by component | Prevents prioritizing parasitic-drag reduction | ⬜ Open | E2 |
| **G4** | Real torsional stiffness | ADR-0002 unverified | 🔄 `[E]` ±35 %, anchored to measured reference; printed-shell torsion bounds proposed (I-12) | E5, E7 |
| **G5** | Propeller wash effect on a thin airfoil at Re 4×10⁵ | ADR-0006 under dispute | ⬜ Open; literature bounds proposed (I-13) | I-13, comparative in-flight test |
| **G6** | **Sweep factor for divergence** | **Weakest link of the structural calculation** | ⬜ Open; X-29 data and theory bounds proposed (I-12) | **I-12 (bounds), E7** |
| **G7** | Flutter | Unverified. Sudden onset, no warning | ⬜ Open | E5 |
| **G8** | Neutral point and static margin | Blocks Phase 1 | 🔄 **Partial** — NP = 26.7 % MAC `[D]` by in-house VLM, **cross-checked by an independent Weissinger-L (28.0 % MAC, 3 mm agreement — I-15 §6.3)**; central-body effect still unquantified | I-07, I-15, C2 (body model) |
| **G9** | Altitude-loop coupling with pitch (*porpoising*) | **Threatens the validity of E7** | ⬜ Open | PID adjustment before testing |

---

## Detail of the critical ones

### G1 — reference geometry

No manufacturer publishes wing area, airfoil or twist.

**Partially closed:** measurement on the Peregrine 840 mm file gives **t/c = 13.5 %** `[M]`. The full planform is still missing: c/4 sweep, taper and **twist distribution** — the latter is what validates or overturns ADR-0003.

Sensitivity: a ±13 % in S produces ±13 % in aspect ratio and wing loading.

### G6 — sweep factor

The divergence calculation uses a reduction factor of **0.50–0.70** for −20° of sweep, taken from generic literature and **not computed on this section's EI/GJ ratio**. It is the term that dominates the `[E]` ±35 % uncertainty.

### G8 — neutral point and static margin

**Partially closed.** The in-house VLM gives **NP = 26.7 % MAC** `[D]`, validated against an analytic case (straight AR 6 wing: 24.0 % calculated against 25 % theoretical).

Target CG: **18.7 % MAC** for 8 % static margin.

**Missing:** verification with a second independent method, incorporating the central body, and **verifying elevon authority** — which still has not been done.

See [I-07](../research/I-07-neutral-point-torsion-window.md).

### G2 — now bounded with numbers

The I-07 analysis turns airfoil selection from an open problem into a bounded one:

| Requirement | Value |
|---|---|
| **R-AIRFOIL** | Cm0 ≥ +0.008, preferably +0.010–0.015 |
| **R-TWIST** | Wash-in ≤ 2.5° |

And it exposes the central conflict: **the reflex that gives positive Cm0 costs cl_max**, and with cl_max 0.65 the stall speed comes out at 44.5 km/h, just inside the 45 requirement. If reflex lowers cl_max to 0.60, the requirement is violated.

[I-06](../research/I-06-reflexed-airfoils.md) additionally bounds the transition model:
the E387 (C) calibration gives an Ncrit 10–12 band `[D]`, not a single value. At
Re ≈ 3–5×10⁵, Ncrit 12 minimizes the grid disagreement `[D]`, but it still needs validating
against a second physical model and screening the reflexed airfoils. **G2 is not closed.**

### G9 — porpoising

The Peregrine documentation reports altitude oscillation in INAV's RTH / Cruise / Loiter modes, with published corrective adjustments (Z position P from 30 to 15, pitch-throttle ratio from 10 to 5, level pitch from 0 to 3°).

**E7 depends on stabilized flight in Cruise.** If the aircraft oscillates, the trim deflection against q is noise.

---

## Closed gaps

None yet. They will move here with the reference of the test that closed them and the resulting datum.
