# I-27 — Article #1 elevon span, chord and tip-clearance trade

**Status:** 🔄 **Computational selection executed; E2/E5/G7 physical closure open**  
**Date:** 2026-08-18  
**Feeds:** ADR-0045, OP-06, guide §6.6, F2, E2, E5, G7  
**Reproduction:** `python calculations/elevon_sizing.py`

## 1. Question and decision boundary

The released v0.4 geometry used one 0.28 c elevon per half-wing from y = 195 to
585 mm (30–90 % half-span). Its inboard edge coincided with the removable
CORE/PANEL joint. This thread asks whether Article #1 needs that complete length,
whether it should extend farther toward the tip, and whether chord should change.

The study is deliberately open to shorter, longer, narrower and wider surfaces.
It does **not** authorize flap/flaperon scheduling, final throws or speed-envelope
expansion. Those require measured low-Reynolds-number aerodynamics, servo/linkage
tests and modal evidence.

## 2. Primary-source evidence

1. Jones and Cohen formulate control-surface planform as an optimization between
   effectiveness and hinge moment; location and span are therefore design variables,
   not a rule that a surface should occupy the whole trailing edge. Their optimum
   aileron shape changes only moderately with wing planform. [NASA/NACA Report 731,
   *Determination of optimum planforms for control surfaces*](https://ntrs.nasa.gov/citations/19760011989).
2. NACA TN 2199 measured nonlinear returns with increasing aileron span. Positive
   deflection lowered stall angle, and the loss of rolling moment near stall became
   more pronounced for larger spans. The tested unswept configuration is not a direct
   Salamandra analogue, but it rejects the assumption that “more span is always safer.”
   [NACA TN 2199](https://ntrs.nasa.gov/api/citations/19930082848/downloads/19930082848.pdf).
3. NACA TN 2445 found that taper on swept-forward wings reduced rolling-moment
   effectiveness more than unswept-wing estimates predicted. Salamandra therefore
   needs its own spanwise calculation rather than a generic aileron percentage.
   [NACA TN 2445](https://ntrs.nasa.gov/api/citations/19930083063/downloads/19930083063.pdf).
4. NACA TR 370 measured hinge moments for several aileron spans and 0.20/0.30 c
   chords. The appropriate first-order reference is `q S_e c_bar_e C_h`, so chord
   reduction has a stronger hinge-moment benefit than area alone suggests.
   [NACA TR 370](https://ntrs.nasa.gov/citations/19930091443).
5. NACA TN 632 flight tests showed that preventing hinge-gap leakage materially
   increased conventional aileron effectiveness. A printed hinge gap and compliance
   can therefore consume a substantial part of ideal analytical authority.
   [NACA TN 632](https://ntrs.nasa.gov/citations/19930081459).
6. FAA AC 25.629-1C treats flutter, divergence and control reversal as connected
   aeroelastic phenomena and calls for rational analysis, parameter variation and
   testing across relevant configurations. It is used here as conservative engineering
   guidance, **not** as a certification claim for a 1.6 kg model aircraft.
   [FAA AC 25.629-1C](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_25.629-1C.pdf).
7. The UIUC Low-Speed Airfoil Tests provide the relevant experimental-data class for
   low-Reynolds-number sections, but no tested entry reproduces the Salamandra r1
   printed elevon, hinge gap and spanwise twist. E2 remains necessary.
   [UIUC Low-Speed Airfoil Tests](https://m-selig.ae.illinois.edu/uiuc_lsat.html).

The literature supports a trade, not a universal percentage. Its transferable findings
are: control location matters; span returns are nonlinear; hinge quality matters; and
outboard control must be checked for stall and aeroelastic behavior.

## 3. Method

The executable model uses the canonical −15° trapezoidal planform and evaluates one
surface per half-wing:

- exact numerical integrals for `S_e`, `c_bar_e = ∫c_e²dy/S_e` and the hinge proxy
  `∫c_e²dy`;
- ideal thin-airfoil plain-flap effectiveness
  `tau = 1 − (theta_h − sin(theta_h))/pi`, with
  `theta_h = acos(2 c_e/c − 1)`; for 0.28 c, `tau = 0.6408` `[D]`;
- an 80×6 linear VLM with fractional panel overlap for symmetric pitch and differential
  roll derivatives;
- the connected V1 `Ixx` from `equipment_layout.py` for a first-order roll response;
- the I-18 hinge-moment coefficient band and servo selection from `servo_torque.py`.

The ideal `tau` is deliberately not called a measured correction. Viscosity, separation,
gap leakage, TPU compliance and freeplay can only reduce or reshape the prediction.

## 4. Alternatives considered

All areas and derivatives below are per physical elevon. `Cm_delta` includes ideal
0.28 c flap effectiveness. The 35–90 c24/c32 rows change only chord; the remaining rows
use 0.28 c.

| Candidate | Span (mm) | Area (cm²) | `Cm_delta` /deg | Ncrit-12 trim | `Cl_delta_a` /rad | Assessment |
|---|---:|---:|---:|---:|---:|---|
| 30–90 % (v0.4) | 390.0 | 221.1 | +0.001648 | +0.555° | 0.3465 | Adequate, but hinge starts on removable joint |
| **35–90 %** | **357.5** | **199.0** | **+0.001828** | **+0.500°** | **0.3275** | **Selected** |
| 40–90 % | 325.0 | 177.7 | +0.001941 | +0.471° | 0.3057 | More roll loss; defer until flight data |
| 35–95 % | 390.0 | 213.2 | +0.002158 | +0.424° | 0.3536 | More tip exposure and inertia |
| 35–100 % | 422.5 | 226.7 | +0.002369 | +0.386° | 0.3692 | Reject for Article #1; no fixed sacrificial tip |
| 35–90 %, 0.24 c | 357.5 | 170.6 | +0.001706 | +0.536° | 0.3055 | Too little model margin before physical losses |
| 35–90 %, 0.32 c | 357.5 | 227.5 | +0.001939 | +0.472° | 0.3474 | Higher hinge load/drag/printed mass without need |

The selected span retains 94.5 % of the v0.4 linear roll derivative while removing
10.0 % of moving area. Its pitch yield is **higher**, not lower, in the rigid VLM:
on this forward-swept planform the removed inboard trailing-edge area has a less favorable
pitch lever about the reference axis. This is a model result, not a general rule for
all flying wings.

## 5. Selected Article #1 geometry

| Parameter | Selected value | Authority |
|---|---:|---|
| Inboard end | y = **227.5 mm** = 35 % half-span | `[D]`, ADR-0045 |
| Outboard end | y = **585.0 mm** = 90 % half-span | `[D]`, retained |
| Moving span | **357.5 mm** | `[D]` |
| Hinge / chord | **x/c = 0.72 / c_e = 0.28 c** | `[D]`, retained |
| Fixed bridge after PANEL joint | **32.5 mm**, y = 195…227.5 | `[D]`; structural benefit `[I]` |
| Fixed tip | **65.0 mm**, y = 585…650 | `[D]` |
| Servo station | y = **±406.25 mm**, geometric midspan | `[D]` |
| Area per elevon | **199.0 cm²** | `[D]` |
| Root/tip local elevon chord | **66.8 / 44.5 mm** | `[D]` |

The 32.5 mm fixed bridge separates the moving hinge from the removable joint and gives
the panel root a continuous fixed trailing edge. This is a strong CAD/manufacturing
reason, but its stiffness and fatigue benefit is `[I]` until a representative printed
joint is tested.

## 6. Quantitative consequences

- Moving area: **−10.0 %**; linear differential-roll derivative: **−5.5 %**.
- Limiting Ncrit-12 cruise trim: **+0.500°**, inside the ±0.6° computational criterion.
  Five degrees of symmetric elevon gives about 10× the remaining trim residual.
- Linear 5° differential screen, using connected V1 `Ixx`: **76 deg/s** steady and
  **0.72 s to 45° bank** at 45 km/h; **160 deg/s** and **0.34 s** at 95 km/h `[D]/[E]`.
  These are rigid, attached-flow predictions, not handling-quality requirements.
- Hinge proxy `∫c_e²dy`: **−11.7 %**. At 180 km/h and `C_h = 0.05`, the selected
  surface gives 0.086 N·m and a factored catalog requirement of **1.643 kgf·cm**.
  The 2.5 kgf·cm DS-939MG has **1.52×** static margin; stiffness, backlash, current and
  holding behavior remain separate gates.
- Moving PETG estimate: 25.0 → **22.5 g per surface** `[E]`; 1.2× balance allocation:
  30.0 → **27.0 g per surface** `[D]/[E]`. The fixed bridge remains PETG in the aircraft,
  so the connected AUW credit is only **6.0 g of balance mass**, not 11 g of surface plus
  balance. Current budgets become **1553.25 g CLEAN** and **1595.80 g V1 lower model** after the vertical-TE fin correction.
- The corrected V1 component model requires battery x = −375.48 mm against current travel ending
  at −371.20 mm. Exact target is therefore **4.28 mm unreachable**, but calculated
  xCG = −93.08 mm remains inside the released −98.8…−88.8 mm band. F2 must close this.

No flutter-speed improvement is claimed. Shortening reduces moving inertia, but it also
shortens the hinge and can change hinge stiffness; the net modal effect is unknown.

## 7. Why the elevon does not extend to the tip

The 65 mm fixed tip is retained for Article #1 because it:

- keeps the moving surface away from the lowest-Reynolds-number, thinnest, +3° wash-in
  region and the tip-vortex field;
- preserves a sacrificial fixed printed tip and avoids a hinge termination at the wingtip;
- limits moving inertia and the control-surface contribution to torsional/reversal risk;
- avoids spending torque and structural complexity for the last 5–10 % span when the
  selected surface already meets the computational pitch/roll screens.

The 95 and 100 % candidates are not intrinsically invalid. They are deferred because
their extra authority is unnecessary before E2/E5/G7, while their low-Re, damage and
aeroelastic penalties are not quantified.

## 8. Operational and CAD limits

- No symmetric flap or flaperon mode is released. Down-elevon changes section stall and
  pitching moment, and the current E2 data set does not establish a safe schedule.
- ±20° remains only an envelope/provisional mechanical capability, not the initial flight
  throw. Initial throws, rates, expo and differential are set by progressive ground and
  flight testing.
- Mass-balance each completed elevon assembly to the measured hinge axis. Do not install
  a fixed 27 g weight without measuring the printed surface moment.
- Model a separate 357.5 mm elevon and a continuous fixed panel trailing edge from
  y = 195 to 227.5 mm. Keep the drawing status **DRAFT — NOT FOR MANUFACTURE** until F2.

## 9. Closure plan

1. **F2:** CAD mass properties, hinge-axis balance moment, servo pocket, linkage geometry,
   battery travel and fixed-bridge manufacturability.
2. **E2:** printed-section/panel polar, hinge-gap effectiveness, stall progression and
   symmetric pitch authority.
3. **E5/G7:** freeplay, static stiffness, surface/modal response and progressive
   speed expansion.
4. Flight-test roll response at low altitude and safe speed before considering 40–90,
   35–95, tip-span or chord variants.
