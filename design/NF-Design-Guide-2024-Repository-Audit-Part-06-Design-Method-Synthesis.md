# NF Design Guide 2024 — Salamandra Repository Audit

**Part 6: airfoil geometry, swept-section interpretation, state-dependent spanloads,
static margin, active stability and flap-chord synthesis**

**Audit date:** 20 August 2026

**Aircraft baseline:** Salamandra Article #1, release v0.6.0, Design Guide v0.24

**Source:** Peter Wick, *Designing Flying Wings* (2024 English PDF), PDF pages 317–331

**Previous:** [Part 5 — wingtips, drag, stall and flap management](NF-Design-Guide-2024-Repository-Audit-Part-05-Wingtips-Drag-Flaps.md)

**Source-series status:** this part reaches PDF page 331 and completes the current book.
A subsequent part, if required, should consolidate the six audits into one prioritized
verification and redesign programme rather than invent another source-page range.

## 1. Part 6 disposition

**Retain the current passive Article #1 architecture provisionally, but do not treat its
airfoil files, constant span efficiency, 8% static margin or 28% elevon chord as optimized
physical results. The final chapter of the NF guide converts each of them into an
experimentally calibrated, whole-aircraft design variable.**

The book's closing chapter is not a completed design recipe. It is an agenda of unresolved
questions: thinner and better-defined airfoils, optimization against precisely stated tasks,
surface flow on swept wings, the relationship between sweep and usable static margin,
alternative proverse-yaw load distributions, active stability and flap geometry. That
uncertainty is a strength when it is kept visible. It would be unsafe to turn the author's
experience trends into Salamandra requirements without calculation and test.

Salamandra already implements several parts of the proposed method well:

- a canonical numerical planform and mass contract;
- local root/tip Reynolds numbers rather than a generic airfoil condition;
- an Ncrit sensitivity band rather than one declared universal turbulence value;
- coupled airfoil moment, wash-in and elevon trim selection;
- two independent inviscid neutral-point formulations;
- a physical component-level CG and battery-travel model; and
- explicit measured, derived, estimated and inferred evidence labels.

The closing pages nevertheless expose a gap between **traceable analytical selection** and
**validated optimization**. The present workflow generates smooth-looking station files and
internally consistent numbers, but it does not yet prove the printed geometry, swept-section
convention, intermediate-section aerodynamics, deflected-control behavior, statewise span
efficiency, dynamic stability or physical flap response.

The principal quantitative findings are:

| Audit result | Current value | Engineering consequence |
|---|---:|---|
| Released r1 station files | 9 files, 61 coordinates each | Traceable station coverage exists, but point count is not a geometric-quality proof. |
| LE-to-mean-TE chord after `normalize_chord()` | root 0.99948228; tip 0.99943560 | The routine rotates but does not scale by its computed chord; dimensional deficits are 0.150/0.082 mm. Small effect, real missing invariant. |
| Actual vertical thickness divided by exported chord | root 13.507%; tip 9.005% | Nominal 13.5/9.0% is nearly reproduced, but the written coordinates are not exactly unit chord. |
| Endpoint-polar metadata | 8 polars, 2 of 9 released stations | Root/tip × low/high Reynolds × Ncrit 10/12 exists; intermediate and deflected-control polars do not. |
| Raw DAT hashes versus metadata | 0/8 direct; 8/8 after CRLF serialization | Geometry is traceable, but byte hashes are newline-dependent and therefore not portable across Git checkouts. |
| Polar angle range | 0° to 16° maximum; one case stops at 10.5° | No negative-alpha or physically deflected-surface evidence supports braking, high-speed trim or asymmetric control states. |
| Section-plane cosine bracket at 15° sweep | 3.407–3.528% | Root/tip 13.5/9.0% can mean 13.976/9.317% in the normal plane or 13.040/8.693% in the flight plane, depending on convention. |
| Fourier-inferred rigid span efficiency, +3° wash-in | 0.9917 at 45 km/h; 0.8367 at 95; 0.7690 at 105 | The lift distribution changes with flight state; one geometry-wide `e_span = 0.85` is not a state-independent property. |
| Same diagnostic, zero twist | 0.9931 at every tested state | The large variation is caused by fixed geometric twist becoming a different fraction of total incidence as `CL` falls. |
| Present CG tolerance | ±5 mm = ±2.223% MAC | It is large relative to an 8% static-margin target. |
| Rigid SM range from two NP methods and CG band | 5.777–11.507% MAC | Fixed 8% in the sweep trade hides a material stability/trim envelope. |
| Elevon trim sensitivity to +1% MAC margin | 3.185° at 45 km/h; 0.715° at 95 | The complete ±5 mm CG band contributes ±7.079°/±1.588° in the present linear model. |
| Battery position required for 0% / −5% SM | −298.484/−257.993 mm | Both are beyond the current aft rail limit by 37.620/78.112 mm. |
| Minimum margin reachable by battery alone | 4.645% MAC | Active-neutral/unstable research is not a parameter-file change; it requires new packaging and a new safety architecture. |
| Ideal 15→40% elevon chord screen | +55.6% pitch yield, 2.667× area, 7.111× hinge proxy | Authority shows diminishing returns while structural/actuator exposure rises rapidly. |
| Current 28% elevon | Ncrit-12 trim +0.521° in the ideal cruise screen | The book's experimental tendency toward about 28% is supportive context, not independent validation. |

Accordingly:

| Item | Part 6 disposition |
|---|---|
| Salamandra r1 airfoil family | **Retain as provisional CAD input; repair normalization through a controlled regeneration, not by editing files manually** |
| Existing endpoint XFOIL polars | **Retain as screening evidence only** |
| Intermediate station interpolation | **Retain geometrically; aerodynamic interpolation remains unvalidated** |
| Section orientation on swept wing | **Open; declare and test both conventions before manufacturing CAD** |
| `e_span = 0.85` | **Retain only as the current induced-drag estimate at the O1 screen; make it state/configuration dependent in future analysis** |
| 8% static-margin target | **Retain for passive Article #1, subject to body-inclusive and flight-identified closure** |
| CG target and ±5 mm band | **Target retained; tolerance must be evaluated in every trim/control state, not only as a balance pass/fail** |
| Artificial stability / CG behind NP | **Reject for Article #1; establish a separate research configuration if pursued** |
| 28% chord elevon | **Retain provisionally; physical nonlinear/printed-section evidence remains open** |
| Braking with the current one-piece elevons | **No schedule released** |
| Turbulators, nose flaps, vortex flaps or divergent trailing edges | **Hypotheses for controlled experiments, not baseline features** |
| Jones or Klein–Viswanathan load distributions | **Future optimization variables only; not transferable solutions** |

## 2. Evidence, scope and reproducibility

The reviewed source is:

```text
/home/bulto/salmandra/INSPIRATION/NF Design guide 2024 english.pdf
SHA-256: a0e81c98b884c7a9c29f75a9bd7ccdf19ff2255642ba2ac5bdd4337696daabca
```

The calculations cited here are generated by
[`calculations/nf_design_guide_part6_design_synthesis.py`](../calculations/nf_design_guide_part6_design_synthesis.py):

```bash
python3 -m pip install -r calculations/requirements.txt
python3 calculations/nf_design_guide_part6_design_synthesis.py
```

The harness consumes the current owners rather than copying design values:

- `design_config.py` for planform, twist, control geometry, mass and flight states;
- `airfoil_reflex_trade.py` and the released DAT family for generated geometry;
- `xfoil_out/*.pol` and `*.meta.json` for endpoint-polar evidence;
- `vlm_ala_volante.py` for the rigid symmetric lift field;
- `drag_model.py` for the current induced-efficiency estimate;
- `aero_contract.py` for VLM and Weissinger neutral points;
- `balance_cg.py` and `equipment_layout.py` for CG and battery authority; and
- `elevon_sizing.py` for ideal flap effectiveness and linear pitch/roll yield.

Evidence tags retain the repository convention:

- `[M]`: measured evidence on a relevant physical article;
- `[D]`: deterministic consequence of declared inputs;
- `[E]`: engineering estimate or transferred empirical input; and
- `[I]`: audit diagnostic from an incomplete model, not a design release.

The principal limitations are deliberate:

1. The guide's statements about future concepts and flight experience are used as design
   prompts. This part does not independently reproduce the external studies referenced in
   the book.
2. The Fourier span-efficiency reconstruction uses circulation from the existing rigid,
   symmetric, inviscid VLM. It is not a Trefftz-plane viscous calculation and contains no
   body, control deflection, separation, transition or elastic deformation.
3. The section-plane calculation is a coordinate projection bracket. It does not decide
   the actual surface-streamline direction or correct a polar.
4. The CG-to-trim calculation is the current linear static model. It demonstrates
   sensitivity; it does not predict the nonlinear low-speed trim already identified as
   open in Part 2.
5. The flap screen uses ideal thin-airfoil effectiveness and linear VLM. It cannot prove
   printed hinge gaps, separated flow, positive/negative asymmetry or servo loads.
6. No result in this part authorizes optimization, manufacturing, active-stability flight
   or expansion of the flight envelope.

## 3. What the closing chapter teaches

### 3.1 Optimization begins with the task, not the optimizer

The guide expects future airfoils to become thinner, potentially 7% chord or less, because
thin sections can reduce pressure drag and extend laminar flow at low lift coefficient. It
also states the corresponding structural penalty (PDF pp. 318–319). That direction cannot
be copied to Salamandra by changing `ROOT_TC` and `TIP_TC`:

- the current root/tip values are 13.5/9.0%;
- Part 4 found unresolved printed-wing torsional stiffness and aeroelastic release;
- the tip is already the thinnest, lowest-Reynolds and highest-wash-in region; and
- a thinner shell changes spar depth, local buckling, joint geometry, servo packaging and
  divergence together.

The transferable lesson is the optimizer definition. Xoptfoil/Xoptfoil-JX can search
geometries that a human would not try, but the guide requires sharply defined Reynolds
numbers, Ncrit values, lift coefficients, moment constraints, flap states and objective
weights (PDF pp. 319–320). The optimizer only optimizes its internal solver. A superior
XFOIL objective value is not proof of a superior physical section.

Salamandra's r1 workflow already follows part of this lesson. It uses actual root/tip
cruise Reynolds numbers, Ncrit 10/12, a coupled moment requirement, +3° wash-in and a
±0.6° cruise neutral-elevon selection cap. Its weakness is objective breadth:

- the search variables are root/tip thickness and a simple aft-contour rotation, not a
  smooth parametric airfoil family;
- selection is dominated by one low-`CL` cruise condition;
- root and tip carry the polar evidence while seven intermediate sections are assumed to
  interpolate acceptably;
- no deflected physical control contour is in the polar set;
- no measured printed geometry enters the optimizer; and
- the output is not recalibrated through a closed flight-test loop.

The correct next optimizer is therefore not “more XFOIL iterations.” It is a robust
whole-aircraft objective evaluated over a declared state and uncertainty matrix.

### 3.2 A DAT file is not a geometric master

The guide identifies nose-region coordinate quality as an active development area and
points toward airfoil editors and Bézier representations that produce smoother, better-
defined geometry (PDF p. 319). The concern is deeper than visual smoothness. A production
airfoil master should define or bound:

- exact unit chord and datum transformation;
- leading-edge radius and curvature continuity;
- upper/lower tangent continuity;
- maximum thickness and camber locations;
- finite printable trailing-edge thickness and wedge angle;
- absence of duplicate, inverted or self-intersecting panels;
- sampling by arc length or curvature rather than an unexplained point count;
- interpolation between span stations; and
- deterministic export identity independent of operating-system newlines.

Salamandra's coordinate provenance README, eight-decimal output and generated nine-station
family are strengths. The audit nevertheless finds two concrete implementation weaknesses.

First, `airfoil_reflex_trade.normalize_chord()` computes the LE-to-mean-TE chord and uses
it to form the rotation cosine and sine, but does not divide the rotated coordinates by
that chord. The released consequences are small but measurable:

| Endpoint | Written LE–mean-TE chord | Deficit | Physical deficit | Nominal vertical t/c | Vertical t/c over written chord |
|---|---:|---:|---:|---:|---:|
| Root | 0.99948228 | 0.0518% | 0.1497 mm | 13.500% | 13.5070% |
| Tip | 0.99943560 | 0.0564% | 0.0816 mm | 9.000% | 9.0051% |

This is not a reason to manually rescale the tracked DAT files. Those coordinates feed
CAD, packaging and cached polars. The correct repair is a controlled generator change,
regeneration of all nine stations, comparison of geometry deltas, invalidation and rerun
of every dependent polar, drawing regeneration and an ADR/CHANGELOG entry.

Second, every endpoint metadata hash differs from the checked-out DAT byte hash. All eight
match when the same text is serialized with CRLF newlines. This proves the coordinates
have not silently changed; it also proves the cache identity is coupled to an undeclared
text-serialization detail. A future manifest should hash a canonical numeric coordinate
array or canonical UTF-8/LF serialization, while retaining an optional raw-file hash.

The 61-point files have a largest segment of about 5.36% chord. That fact is an inventory,
not a pass/fail quality criterion. The repository has no explicit curvature, leading-edge
radius, tangent, panel-angle or interpolation-error acceptance gate.

### 3.3 Flying-wing airfoils must include the flap state

The guide's concise point is that a flying-wing section and its flap cannot be optimized
independently (PDF p. 320). Elevon deflection changes:

- effective camber and zero-lift angle;
- pitching moment;
- local lift and induced loading;
- transition and separation behavior;
- hinge moment;
- neutral point and usable static margin; and
- stall recovery and control reserve.

The current r1 endpoint polars are all generated on the undeformed sharp-edge DAT contour.
They cover root/tip, low/high Reynolds and Ncrit 10/12, but begin at zero angle and include
no physical flap geometry. `elevon_sizing.py` then adds an ideal incidence-equivalent flap
effectiveness in a separate inviscid model. This separation is appropriate for screening,
but it cannot validate a tailless trim system.

The required matrix is at least:

```text
station:      root, control-inboard, control-mid, control-outboard, tip
Reynolds:     local minimum, mission points, local maximum
transition:   smooth reference, representative print, forced/tripped sensitivity
elevon:       negative, neutral, positive trim; roll differential; brake candidates
angle/CL:     negative-lift high-speed range through attached flight and stall
geometry:     sharp analytical reference and scanned printed contour
```

The final acceptance must measure moments and control effectiveness. XFOIL remains useful
for screening but cannot establish the complete three-dimensional or separated response.

### 3.4 Turbulators and alternative lift devices are experiments

The guide suggests turbulators as a way to suppress laminar separation bubbles and make
pitching moment more consistent. It also identifies nose flaps, leading-edge vortex flaps,
receding steps and divergent trailing edges as possible development directions (PDF
pp. 320–321). It explicitly warns that published information may not transfer to model
Reynolds numbers and calls for experiments.

For Salamandra, none should enter the baseline merely because it may improve one polar:

- a turbulator may stabilize moment while increasing drag and changing `CLmax`;
- a receding step is also a printed-geometry, contamination and structural detail;
- a nose flap adds a hinge, gap, actuator, mass and failure mode at the leading edge;
- a vortex flap is fundamentally three-dimensional and incidence dependent; and
- a divergent trailing edge changes printable thickness, moment, drag and hinge mechanics.

A useful experiment must measure the complete change in `CL`, `CD`, `Cm`, transition,
stall, trim and repeatability on representative printed surfaces. A favorable isolated
quantity is not a design decision.

## 4. The swept-section question remains physically open

### 4.1 What the guide says

For a swept wing, the guide asks whether the two-dimensional section should be defined in
the flight-direction plane or normal to the quarter-chord line. It notes that thickness
and camber change with the cosine of sweep and that neither potential-flow paths nor
near-wall surface streamlines necessarily follow either simple direction (PDF pp. 321–325).

The cited model-flight paint observations show a curved path: outward near the nose,
closer to the flight direction after transition and outward again near the trailing edge.
The author reports better practical correlation from orthogonal XFOIL design, but also
states that precise proof is absent (PDF pp. 323–325).

The correct learning is therefore not “orthogonal is true.” It is:

1. declare the geometric reference plane;
2. distinguish potential flow from surface flow;
3. expect dependence on angle, pressure distribution, transition and Reynolds number;
4. bracket both simple interpretations; and
5. correlate the selected method against relevant physical evidence.

### 4.2 Salamandra's present ambiguity

The repository defines airfoils at constant span stations and the VLM uses flight-axis
`x-y-z` geometry. Neither the coordinate-family README nor the loft instructions make the
section plane controlling CAD explicit. The profile generator and XFOIL inputs also contain
no sweep/orientation parameter.

At `|Lambda_c/4| = 15°`:

```text
cos(15 deg)       = 0.96592583
1 - cos(15 deg)   = 3.4074%
sec(15 deg) - 1   = 3.5276%
```

If the current 13.5/9.0% coordinates are flight-direction sections and are interpreted
relative to the shorter normal chord, they become 13.976/9.317%. If they were intended as
normal sections and are then viewed in the flight-direction plane, they appear as
13.040/8.693%.

This is a coordinate-convention bracket, not a prediction that the aerodynamic answer is
wrong by 3.5%. It is large enough to invalidate silent convention switching and to alter
local chord, thickness, Reynolds number, spar depth and polar interpretation.

### 4.3 Required closure

Before production loft release:

1. name the master section plane in the geometry contract and every drawing;
2. implement both transforms from one parametric master;
3. calculate local chord, t/c, camber, spar depth and Reynolds consistently in each case;
4. run the full section and three-dimensional state matrix for both interpretations;
5. inspect tufts or oil/paint flow on a representative swept printed panel;
6. correlate surface direction, transition and integrated forces/moments; and
7. select the convention by evidence and configuration control.

## 5. Span efficiency is a flight-state output

### 5.1 The book's broader lesson

The final chapter revisits proverse-yaw loading. Prandtl's `sin^3` bell is not the only
candidate: the guide discusses Jones and Klein–Viswanathan distributions, noting different
induced-drag and yaw-agility properties in the cited analyses (PDF pp. 328–329). It also
warns that distribution, flap geometry and flap management cannot be optimized separately.

This is directly relevant to Salamandra even though Article #1 is not a pure finless Horten
configuration. A named target distribution is never a complete design. At minimum it must
be evaluated with:

- the real planform and twist;
- local section polars and stall limits;
- the actual control segmentation and schedule;
- pitch trim and static margin;
- adverse/proverse yaw and yaw damping;
- structural bending and torsion;
- mass, inertia and aeroelastic deformation; and
- mission-weighted total energy and handling.

### 5.2 What the current VLM reveals

For a symmetric lifting-line circulation represented by

```text
Gamma(theta) = sum(A_n sin(n theta))
```

the classical harmonic diagnostic is

```text
e = A_1^2 / sum(n A_n^2), for odd n
```

The Part 6 harness sums the existing panel-VLM circulation chordwise, fits odd harmonics
1–21 and evaluates that expression at the level-flight `CL` of V1. A synthetic elliptical
circulation returns `e = 1.000000`. Refining the VLM from `ny = 80` to 120 changes the
reported states by no more than 0.00512.

| Speed | Required `CL` | VLM alpha | Fourier-inferred `e` | Inferred `CDi` / present `e=0.85` model |
|---:|---:|---:|---:|---:|
| 45 km/h | 0.5823 | +6.562° | 0.99172 | 0.8571 |
| 60 km/h | 0.3275 | +3.116° | 0.97487 | 0.8719 |
| 75 km/h | 0.2096 | +1.521° | 0.93529 | 0.9088 |
| 95 km/h | 0.1307 | +0.453° | 0.83669 | 1.0159 |
| 105 km/h | 0.1070 | +0.133° | 0.76899 | 1.1053 |

The ratio is not a measured drag correction. It shows the direction and scale implied by
the rigid circulation shape if the classical harmonic interpretation is applied.

The important result is the **0.22273 change in inferred efficiency across the operating
states**. With zero twist, the same linear VLM gives 0.99312 at every state because the
circulation shape merely scales with angle of attack. With fixed +3° wash-in, twist becomes
a progressively larger share of total incidence as aircraft `CL` falls, so the load shape
and efficiency change.

This finding refines Part 5:

- the present `e_span = 0.85` happens to be close to the rigid cruise diagnostic;
- it is conservative for the low-speed rigid loading;
- it becomes optimistic in the 105 km/h diagnostic; and
- none of those comparisons contains viscous, body, control, separation or elasticity.

The repository should therefore retain the scalar only as an explicitly estimated O1
screen until a statewise owner exists. It should not call 0.85 a fixed planform property.

### 5.3 What an alternative-distribution study must do

Do not begin by forcing a `sin^3`, Jones or Klein–Viswanathan curve. Define the mission and
constraints, then let the trade report how close each feasible state can come. Required
outputs include:

- spanwise circulation and local `cl` at all mission/control states;
- separate viscous and induced drag;
- roll/yaw moments from symmetric and differential controls;
- `Cn_beta`, `Cn_r`, `Cl_beta` and control derivatives;
- lost-lift pitch/yaw/roll response at incipient separation;
- root bending moment and torsion;
- trim drag and control reserve; and
- robustness to CG, surface geometry, transition and elastic twist.

Article #1's provisional fixed fins mean it need not acquire a Horten loading merely to
claim proverse yaw. A future finless research wing can compare the distributions after the
baseline aircraft has measured aerodynamic and structural correlation.

## 6. Sweep and static margin must be iterated together

### 6.1 What the guide contributes

The guide reports an approximately linear empirical relationship between sweep and the
static margin flown successfully in surveyed models. It does not establish the mechanism
or prove that the larger margin is unavoidable (PDF pp. 325–327). It then asks whether
different geometry or loading could retain acceptable behavior at lower margin.

That is a useful warning against two opposite errors:

- treating one static-margin percentage as universal; or
- reducing static margin for performance before stall response, damping, control authority
  and uncertainty are known.

### 6.2 Repository contrast

`sweep_trade.py` varies quarter-chord sweep from −20° to −10° but holds static margin at
8%. It re-solves neutral point, battery station, trim, local lift and an aeroelastic trend,
which is good coupling. It does not ask whether the **required usable margin changes with
sweep**, and both neutral-point methods are inviscid lifting-surface formulations.

For the current physical target CG and ±5 mm band:

```text
MAC                              224.957 mm
1% MAC                             2.250 mm
CG tolerance                      ±5.000 mm = ±2.223% MAC
x_NP, panel VLM                  -75.787 mm
x_NP, Weissinger-L               -72.899 mm
method spread                      2.889 mm = 1.284% MAC
combined rigid implied SM range    5.777% ... 11.507% MAC
```

The range does not include body, viscosity, Reynolds-dependent moment, control deflection,
propulsion or aeroelasticity. It therefore understates the complete uncertainty rather than
defining a safe band.

### 6.3 The trim impact is larger than the airfoil-selection cap

In the current linear pitch model, increasing static margin by one percentage point of MAC
adds a required pitching-moment coefficient of `0.01 CL`. Dividing by the current ideal
elevon moment yield gives:

| Speed | `CL` | Elevon change per +1% MAC margin | Elevon change across ±5 mm CG |
|---:|---:|---:|---:|
| 45 km/h | 0.5823 | 3.185° | ±7.079° |
| 95 km/h | 0.1307 | 0.715° | ±1.588° |

The ±0.6° value used by the airfoil trade is a **geometry-selection criterion at the target
CG and cruise**, not an approved flight-control limit. Nevertheless, the comparison exposes
a missing closure: the permitted physical CG band is more influential at cruise than the
entire neutral-trim cap used to select the root/tip reflex pair.

At 45 km/h the linear result is already in the large-deflection range that Part 2 showed is
not aerodynamically closed. It should be interpreted as a sensitivity alarm, not an exact
control command.

The design process must jointly evaluate sweep, mass/CG distribution, required static
margin, section moment, twist, control state, stall sequence and dynamic modes. Passing a
target-CG cruise trim point does not close that system.

## 7. Artificial stability is a separate aircraft configuration

### 7.1 What the guide suggests

The guide discusses gyro-assisted low static margin, CG behind the neutral point and
real-time sideslip correction. It reports that an older study found an optimum near a 5%
aft shift and claimed glide-ratio gains as large as 13%, while larger shifts degraded drag
or handling. It also notes that no decisive modern breakthrough is known and questions
whether the complexity is worthwhile for small gains (PDF pp. 329–330).

These are research prompts, not Salamandra performance credits. The figures are not
transferable without reproducing the complete aircraft, control law and measurement.

### 7.2 Current packaging does not reach the proposed states

Using the converged V1 layout and moving only its 445 g battery:

| Target | Target CG | Aircraft CG shift | Required battery x | Current aft limit | Overrun |
|---|---:|---:|---:|---:|---:|
| 0% SM, CG at VLM NP | −75.787 mm | +17.997 mm aft | −298.484 mm | −336.104 mm | 37.620 mm |
| −5% SM, CG behind NP | −64.540 mm | +29.244 mm aft | −257.993 mm | −336.104 mm | 78.112 mm |

The current battery can travel only 27.167 mm aft from the V1 position. That moves the
aircraft CG 7.546 mm and reaches approximately 4.645% passive margin. Neutral and unstable
flight would therefore require physical repackaging or redistribution, not merely a flight-
controller setting.

### 7.3 Why Article #1 must remain passively stable

The current repository does not contain the evidence needed for intentional static
instability:

- the body-inclusive and viscous neutral point is open;
- low-speed `Cm` and control effectiveness are open;
- CLEAN is predicted directionally unstable and the V1 lower `Cn_beta` corner remains
  uncertain;
- no measured sideslip state is available;
- servo bandwidth, freeplay and nonlinear load response are not flight-qualified;
- no full longitudinal/lateral dynamic model is correlated;
- no control-law stability margins, sensor-noise analysis or delay budget exist;
- no redundant power, watchdog, fail-passive or degraded-mode architecture exists; and
- the flutter boundary is not closed.

An unstable tailless aircraft can depart faster than a pilot or non-qualified controller
can recognize the model error. Artificial stability also couples to the flexible modes that
Part 4 says must be measured before speed expansion.

If pursued, create a separately named research configuration with:

1. a body-inclusive nonlinear aerodynamic model;
2. measured actuator, sensor and structural dynamics;
3. explicit gain/phase margins and uncertainty analysis;
4. saturation, anti-windup, mode-transition and envelope-protection logic;
5. independent fail-safe recovery to a passively stable CG or configuration;
6. hardware-in-the-loop and restrained ground testing;
7. incremental captive or low-energy flight cards; and
8. configuration-specific mass, CG, software and parameter control.

Reducing V1 fin area through sideslip feedback is similarly premature. First measure
finite-sideslip response and close passive V1 directional stability. A beta estimator that
has not been validated cannot replace aerodynamic restoring moment.

## 8. Flap chord: 28% is plausible, not proven

### 8.1 What the guide contributes

The guide states that the moment response of typical flaps is not strongly dependent on
chord through a broad 15–40% range, but cautions that this generalization may not hold for
plank sections at model Reynolds numbers. Its reported experience suggests asymmetric
response to positive and negative deflection and a tendency toward chords around 28%
(PDF p. 330).

This supports experimentation with the current 28% choice. It does not validate it.

### 8.2 Repository screen

Holding the current 35–90% half-span limits and changing only chord gives:

| Elevon chord | Ideal `tau` | Area per side | Hinge proxy `integral(c_e^2 dy)` | `Cm_delta` /deg | Ncrit-12 cruise trim | `Cl_delta_a` /rad |
|---:|---:|---:|---:|---:|---:|---:|
| 15% | 0.4805 | 106.63 cm² | 0.0003223 m³ | 0.0013708 | +0.694° | 0.24557 |
| 20% | 0.5498 | 142.18 cm² | 0.0005730 m³ | 0.0015686 | +0.607° | 0.28099 |
| 24% | 0.5978 | 170.61 cm² | 0.0008251 m³ | 0.0017055 | +0.558° | 0.30552 |
| **28%** | **0.6408** | **199.05 cm²** | **0.0011230 m³** | **0.0018282** | **+0.521°** | **0.32750** |
| 32% | 0.6797 | 227.48 cm² | 0.0014668 m³ | 0.0019393 | +0.491° | 0.34739 |
| 40% | 0.7478 | 284.35 cm² | 0.0022918 m³ | 0.0021334 | +0.446° | 0.38216 |

From 15% to 40%, this ideal model gains only 55.6% pitch yield while moving area grows
2.667× and the hinge-moment proxy grows 7.111×. The diminishing effectiveness and rapidly
increasing load exposure make 28% a rational preliminary compromise.

The model still omits exactly the effects emphasized by the guide:

- positive/negative deflection asymmetry;
- finite printed trailing edge and hinge gap;
- local Reynolds and transition;
- separation at large deflection;
- control-surface flexibility and freeplay;
- physical hinge moments and servo dynamics; and
- the complete spanload/trim change.

The minimum experiment is a representative printed section or half-wing with interchangeable
24/28/32% control chords, positive and negative deflections, measured forces/moments and
repeatable surface condition. Do not select the test winner from pitch authority alone;
include drag, stall, hinge load, roll response and trim range.

### 8.3 Braking must preserve outer control

The last page before the future chapter advises keeping calculation deflections small,
because the moment response becomes increasingly nonlinear beyond roughly 45°, and retaining
outer controls during braking for stall safety and controllability (PDF p. 317).

Salamandra has one elevon per side. It cannot independently command an inboard brake and an
outer roll-control segment. Any symmetric high-deflection schedule consumes pitch/roll
authority on both complete elevons. Consistent with Part 5, no brake mode should be released
for Article #1. A future segmented system must first prove:

- pitch trim and roll authority throughout deployment and retraction;
- local section behavior to and beyond the commanded deflection;
- servo torque, current and thermal duty;
- asymmetric jam or deployment response;
- stall progression and recovery; and
- a flight-tested schedule beginning below the guide's 30° calculation range.

## 9. Direct contrast: closing-chapter lessons versus repository maturity

| Guide lesson | Repository strength | Weak point / missing evidence | Disposition |
|---|---|---|---|
| Define optimizer conditions and weights sharply | Actual endpoint Reynolds numbers, Ncrit band, trim coupling | One main cruise objective; no robust multi-state/uncertainty optimizer | Extend before any new airfoil family |
| Optimizer quality is limited by solver correlation | E387 drag calibration and explicit E2 gate | Moment, printed geometry and complete-aircraft correlation remain open | XFOIL remains screening `[D]` |
| Use geometrically well-defined airfoils | Generated nine-station family and provenance | No parametric curvature master; normalization defect; no geometry-quality gates | Controlled regeneration required |
| Treat airfoil and flap as one design | Elevon yield is coupled to profile moment for trim | No deflected-section polars or nonlinear complete-wing model | P0 aerodynamic closure |
| Consider boundary-layer devices experimentally | Existing transition/Ncrit awareness | No representative printed-section A/B data | Test only, no baseline feature |
| Declare swept-section interpretation | Coordinate axes and sweep are numerically controlled | Loft plane is unstated; surface-streamline evidence absent | Close before manufacturing CAD |
| Iterate geometry and static margin | Sweep trade re-solves NP, trim and battery | Static margin fixed at 8%; no empirical/dynamic usability model | Add SM/CG dimension to trade |
| Compare complete lift distributions | Rigid VLM provides circulation/load shape | Constant `e`; no induced/state owner, yaw agility or viscous integration | Replace scalar when evidence exists |
| Treat artificial stability as an integrated aircraft/control problem | FC, servo, power and inertia models exist | No qualified dynamics, sensing, control law, redundancy or reachable CG | Separate future research configuration |
| Optimize flap chord experimentally | 15–40% ideal geometric/aerodynamic screen exists | No physical positive/negative response or printed hinge data | Retain 28% provisionally |
| Preserve controllability during braking | Repository has not released a brake schedule | One-piece elevons cannot separate outer control from braking | Keep mode prohibited |

## 10. Weak points exposed by Part 6

### P0 — blocks aerodynamic or manufacturing release

1. **The r1 airfoil family lacks a manufacturing-grade geometric contract.** Unit chord,
   curvature, leading-edge radius, tangency, printable trailing edge and interpolation
   accuracy are not jointly validated.
2. **The section plane on the swept wing is undefined.** A 3.4–3.5% projection ambiguity
   remains in the geometry/aerodynamic interpretation.
3. **The endpoint polar set is not a control-system polar set.** It lacks negative alpha,
   deflected physical contours, intermediate stations and representative printed surfaces.
4. **The physical CG band is not closed against the trim envelope.** Its cruise sensitivity
   exceeds the neutral-trim criterion used for airfoil selection.
5. **Dynamic stability and handling are not correlated.** Static margin cannot be reduced
   rationally, much less made negative.
6. **Braking has no independently controllable outer surface.** No schedule is authorized.

### P1 — materially weakens optimization confidence

1. `e_span = 0.85` is state independent while the current rigid loading is not.
2. The sweep trade fixes static margin rather than optimizing a usable margin envelope.
3. The airfoil cache hash is newline dependent, so identical numerical coordinates can
   appear stale after a platform checkout.
4. Seven intermediate airfoils are generated geometrically but have no station-specific
   polar evidence.
5. `Cm0` endpoint results are copied into control modules instead of being owned by a
   versioned geometry/polar manifest.
6. No integrated objective combines energy, trim, handling, stall, structure and control
   across flight states.
7. No model compares candidate spanload families with the current flap geometry and fins.

### P2 — future research and documentation gaps

1. No surface-streamline/transition observation plan exists for the swept printed wing.
2. No reversible turbulator, step, nose-flap or divergent-trailing-edge experiment is
   defined.
3. No named active-stability research configuration or safety case exists.
4. No beta sensor/estimator evidence supports vertical-surface reduction.
5. No control-chord test article compares positive and negative physical response.
6. Airfoil/planform optimization inputs, weights and uncertainty distributions are not
   stored as a controlled manifest.

## 11. Required end-to-end design method learned from the book

### D0 — define the aircraft task and configurations

For CLEAN, V1 and every research variant, declare:

- mission speed/`CL`/Reynolds distribution and weighting;
- energy, stall, handling and control objectives;
- allowed mass, CG, inertia and geometry;
- passive stability requirements;
- roughness/transition and manufacturing uncertainty;
- structural/aeroelastic limits; and
- explicit rejection criteria.

An optimizer without this input contract is only a geometry generator.

### D1 — create one parametric geometry authority

Use a smooth master representation for root, intermediate and tip sections. It must own:

- chord-normalized curves and section-plane convention;
- thickness, camber, reflex and leading/trailing-edge definitions;
- finite printable edge and hinge geometry;
- spanwise interpolation laws;
- structural reference lines and minimum depths; and
- canonical numerical hashes independent of text newlines.

Export DAT/DXF/mesh formats from the master and verify their round-trip error.

### D2 — build the local aerodynamic evidence matrix

For every critical station/state:

- calculate smooth and rough/tripped polars;
- include actual positive/negative flap contours;
- extend through the required negative-lift and stall ranges;
- propagate geometry and transition uncertainty; and
- measure representative printed sections to calibrate lift, drag and moment separately.

Do not tune one Ncrit value to make every metric agree.

### D3 — solve the complete three-dimensional aircraft

Integrate local viscous polars with a three-dimensional method that produces:

- statewise circulation and induced drag;
- body, fin and junction effects;
- finite-sideslip forces/moments and yaw damping;
- control derivatives and nonlinear saturation;
- stall/lost-lift sequence about the actual CG; and
- elastic twist and control-surface deformation.

Compare multiple formulations and carry their disagreement as uncertainty.

### D4 — close trim, stability and control together

Sweep the full physical CG band and plausible neutral-point movement. For every state,
report:

- static margin and dynamic modes;
- equilibrium control position;
- remaining positive/negative pitch and roll authority;
- hinge load, servo current and rate;
- sensitivity to freeplay and latency; and
- recovery after local stall or actuator failure.

The output is an admissible envelope, not one nominal trim angle.

### D5 — couple aerodynamics to mass and structure

Every thinner section, flap, load distribution or control concept must update:

- printed shell and spar geometry;
- stiffness and divergence;
- component placement, CG and inertia;
- root/joint loads and proof cases;
- control-surface mass balance and flutter modes; and
- manufacturing tolerance and inspectability.

Part 4's ground-test programme remains a prerequisite.

### D6 — optimize robustly, then preserve alternatives

Use multi-state, multi-objective optimization with explicit uncertainty. Retain Pareto
alternatives rather than publishing only a scalar winner. At minimum include:

- current r1/flat-cap baseline;
- current r1/V1 fins;
- section-plane alternatives;
- bounded twist and control-chord variants; and
- any alternative spanload or active-control research concept.

Every candidate must report why it loses, not merely its rank.

### D7 — calibrate theory with physical evidence

Build representative coupons, sections, panels and finally aircraft configurations. Measure:

- as-built contour, roughness, gaps, mass and CG;
- section or complete-aircraft forces and moments;
- surface streamlines and transition where informative;
- hinge moment and actuator response;
- static/dynamic stability and control derivatives;
- structural stiffness and modal properties; and
- propulsion-coupled energy over repeated mission points.

Feed measured discrepancies back into the models and uncertainty bounds before the next
optimization cycle.

### D8 — release by configuration and evidence

A released geometry must bind:

- source/master version and canonical hash;
- derived coordinate and CAD exports;
- polar/test data and their exact geometry;
- mass, CG and control configuration;
- software/FC parameters;
- operational envelope; and
- passed acceptance gates.

“Best XFOIL polar” or “optimizer winner” is not a release status.

## 12. Proposed acceptance matrix

| Gate | Required evidence | Current status |
|---|---|---|
| Geometry identity | Exact unit chord, smooth master, finite printed TE, canonical hash | **Fail/open:** DAT family is traceable but normalization and quality contract are incomplete |
| Section plane | Declared convention with both-case sensitivity and physical correlation | **Open** |
| Local polar matrix | Relevant stations, Re, transition, alpha and physical control states | **Partial:** endpoints, clean contour, non-negative alpha only |
| Statewise spanload | Correlated circulation, induced drag and local capability per state | **Partial `[I]`:** rigid symmetric diagnostic only |
| Viscous/induced integration | Local polar integration plus 3-D induced field | **Open** |
| Sweep/static-margin trade | Geometry, CG, trim, modes and handling iterated together | **Partial:** 8% margin fixed |
| Passive Article #1 stability | Body-inclusive aerodynamic/dynamic correlation | **Open** |
| Active stability | Qualified sensors, dynamics, control law, redundancy and reachable CG | **Absent; not Article #1** |
| Elevon chord | Printed-section nonlinear moment/drag/hinge comparison | **Open; 28% provisional** |
| Braking | Controllability, nonlinear aero, actuator and failure closure | **Absent; mode not released** |
| Physical calibration loop | Measured contour, aerodynamics, CG/inertia and modes fed back | **Open E2/F2/GVT/flight ID** |

## 13. Immediate repository changes recommended

1. Correct `normalize_chord()` by dividing by the computed chord, but only inside a
   controlled r2 regeneration that invalidates and reruns every dependent artifact.
2. Add a geometry-quality validator for unit chord, closure/finite TE, leading-edge radius,
   curvature/tangent continuity, self-intersection, panel-angle change and round-trip error.
3. Replace raw platform-dependent DAT cache identity with a canonical coordinate hash and
   record newline serialization separately.
4. Declare the master swept-section plane in the geometry contract, loft documentation and
   drawings; retain both interpretations as a sensitivity until tested.
5. Expand the polar manifest to intermediate/control stations, negative alpha, physical
   deflections, roughness/transition and scanned printed contours.
6. Move root/tip moment data out of copied literals and into the versioned polar/geometry
   manifest consumed by trim and control modules.
7. Replace the single span-efficiency input with a state/configuration interface when the
   3-D/viscous method is available; retain 0.85 as a clearly labelled estimate meanwhile.
8. Add static margin and the full CG band as dimensions in the sweep/airfoil/control trade.
9. Require trim and remaining authority across the CG, Reynolds, transition and speed
   envelope rather than only at target-CG cruise.
10. Keep Article #1 passively stable. Name and isolate any future active-stability aircraft,
    packaging and control-law data.
11. Build interchangeable 24/28/32% printed control test articles before changing the
    released 28% chord.
12. Keep braking prohibited until segmentation or a verified schedule preserves pitch and
    roll authority.
13. Treat turbulators, steps and alternative high-lift/moment devices as reversible A/B
    experiments with complete force/moment/drag measurements.
14. Store optimizer variables, constraints, objective weights, solver version and
    uncertainty ranges in a machine-readable manifest.
15. Add a consolidated six-part audit closure table to the eventual flight-release review.

## 14. Part 6 conclusion

The final chapter's most valuable contribution is methodological humility. It identifies
promising tools and configurations, but repeatedly states that flow direction, sweep/static-
margin coupling, proverse-yaw loading, active stability and flap response remain partly
experimental. The lesson is not to adopt every idea. It is to organize the uncertainty so
that computation and physical evidence can reduce it.

Salamandra's repository is unusually strong at numerical traceability, but the audit found
that traceability alone can hide fragile assumptions. The airfoil generator nearly, but not
exactly, normalizes the chord. Polar hashes identify newline serialization as well as
geometry. Seven intermediate profiles exist without local polar evidence. The loft plane
is not declared. A constant `e = 0.85` is used even though the rigid +3° wash-in load shape
changes strongly with flight `CL`. The permitted CG band moves predicted trim more than
the airfoil-selection cap. Neutral or negative margin cannot be reached with current
packaging and would not be safe with the current evidence.

The present configuration should therefore remain conservative:

- retain the passive 8% target and current battery rail for Article #1;
- retain the 28% elevon as a provisional compromise;
- release no brake or active-stability mode;
- repair coordinate identity through controlled regeneration;
- define the swept-section plane;
- replace endpoint/nominal optimization with a full state and uncertainty matrix; and
- close the loop with measured printed geometry, aerodynamic moments, CG/inertia,
  structural dynamics and flight identification.

This part reaches the end of the 331-page source. The logical next deliverable is a single
prioritized programme that merges Parts 1–6 into configuration decisions, calculation
owners, physical tests and objective release gates for Salamandra Article #1.
