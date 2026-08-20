# NF Design Guide 2024 — Salamandra Repository Audit

**Part 5: winglets, induced drag, outer-wing reserve, stall architecture and flap
management**

**Audit date:** 20 August 2026

**Aircraft baseline:** Salamandra Article #1, release v0.6.0, Design Guide v0.24

**Source:** Peter Wick, *Designing Flying Wings* (2024 English PDF), principally PDF
pages 270–303 and 308–316

**Previous:** [Part 4 — printed structure, joints and aeroelastic release](NF-Design-Guide-2024-Repository-Audit-Part-04-Structure-Aeroelasticity.md)

**Next:** [Part 6 — design-method synthesis](NF-Design-Guide-2024-Repository-Audit-Part-06-Design-Method-Synthesis.md)

## 1. Part 5 disposition

**Retain Salamandra Article #1's flat wingtip closures and CORE-rooted V1 fins. Do not
add or credit a winglet until a finite-sideslip, viscous, aeroelastic and measured
aircraft-level trade demonstrates a benefit.**

This is not a conclusion that winglets never work. It is the consequence of applying the
NF guide's own systems logic to this particular aircraft rather than copying an
aft-swept glider solution.

The guide's most important lesson in this range is that a winglet, its junction and the
outer wing form one aerodynamic and structural system. A winglet can reduce induced drag,
provide directional stability and improve low-speed handling, but those benefits are
conditional. It also adds wetted area, interference drag, outer-wing loading, low-Reynolds-
number sensitivity, yaw-dependent separation, tip mass and aeroelastic demand.

Salamandra makes that trade unusually severe:

- Article #1 cruises at low lift coefficient, where induced drag is only a small part of
  the estimated drag;
- its quarter-chord sweep is **forward**, so the tip quarter chord lies ahead of the CG;
- the current +3° wash-in already leaves little margin in the repository's generic local-
  `cl` screen;
- its O1 energy budget is tight enough that the estimated V1 fin penalty alone moves the
  model slightly beyond the power-limited boundary; and
- Part 4 found unresolved divergence and flutter margins, making added tip mass and an
  aft winglet support especially undesirable.

The principal quantitative results are:

| Audit result | Current value | Consequence |
|---|---:|---|
| Induced share of the estimated CLEAN drag at 45 km/h | **60.9%** | A low-drag wingtip device can help near stall, if the flow stays attached. |
| Induced share at the 95 km/h O1 point | **7.3%** | Cruise offers little induced-drag benefit to recover added wetted/interference drag. |
| Maximum possible cruise saving from `e_span = 0.85` to the ideal `1.00` | **0.0192 N** | This is an upper bound, not a realizable winglet prediction. |
| Maximum device `Delta CD0` merely to improve the CLEAN 95 km/h model at ideal `e = 1` | **0.000160** | Any larger increment makes cruise drag worse even under the ideal induced endpoint. |
| Current V1 fin estimate | **Delta CD0 = 0.003369; Delta D = 0.4052 N** | The CORE fins are parasite/interference devices, not induced-drag devices. |
| Estimated CLEAN/V1 drag at 95 km/h, evaluated at V1 mass | **1.764/2.169 N** | V1 is 0.0468 N above the 2.1226 N O1 power boundary under the same estimated polar. |
| Estimated CLEAN/V1 energy | **1.003/1.169 Wh/km** | V1 misses the 1.15 target by 1.7% in this unvalidated model; E2/E3 must decide. |
| Tip-quarter-chord arm from CG | **−80.4 mm** | A conventional vertical surface centered there has a destabilizing yaw arm. |
| Tip-trailing-edge arm from CG | **+28.1 mm** | Only 13.4% of the current V1 fin arm; equal isolated contribution would require 7.45× area. |
| Setback needed to place a tip device at the current V1 `x_AC` | **181.2 mm aft of tip TE** | Aerodynamically possible in concept, but structurally and aeroelastically costly. |
| Quarter-chord/CG crossing | **eta = 0.538; y = 350.0 mm** | The current high-loaded band straddles the pitch-moment sign change. |
| Peak symmetric local `cl` at 45 km/h | **0.6320 at eta = 0.603** | Only 0.0180 below the repository's generic 0.65 section screen. |
| Linear twist at which that screen is first exceeded | **approximately +5° wash-in** | Adding outer loading to compensate a winglet is not available margin. |
| Ten-percent-span moment-neutral flap window, linear VLM | **eta = 0.415–0.515** | The current one-piece elevon crosses regions of opposite pitch yield but cannot schedule them independently. |
| Ncrit-12 trim after replacing +3° wash-in with 0° / −2° linear washout | **+4.57° / +7.27° elevon** | The guide's aft-swept washout rule cannot be copied without redesigning trim and section aerodynamics. |

Accordingly:

| Item | Part 5 disposition |
|---|---|
| Flat tip closure for Article #1 | **Retain** |
| V1 CORE-rooted fixed fins | **Retain as the provisional directional test architecture; no induced benefit credited** |
| Existing rejection of quarter-chord-mounted wingtip fins | **Confirmed quantitatively** |
| Aft-set winglet/fin as a future module | **Study only; not rejected in principle** |
| `e_span = 0.85` | **Retain only as an `[E]` drag sensitivity, not a demonstrated planform property** |
| `CD_PROFILE_CRUISE = 0.0136` | **Retain only as an `[E]` O1 screen pending E2** |
| Current 45 km/h symmetric VLM as stall evidence | **Insufficient** |
| +3° linear wash-in | **Retain provisionally because it closes current trim; outer-wing robustness remains open** |
| Copying the guide's exponential washout directly | **Reject** |
| Current one-elevon-per-side geometry | **Retain for Article #1** |
| Symmetric flap/flaperon or brake schedule | **Keep unreleased** |
| Multi-segment flap system | **Analyze virtually for future panels; do not add hardware to Article #1 without mission benefit** |

## 2. Evidence, scope and reproducibility

The reviewed source is:

```text
/home/bulto/salmandra/INSPIRATION/NF Design guide 2024 english.pdf
SHA-256: a0e81c98b884c7a9c29f75a9bd7ccdf19ff2255642ba2ac5bdd4337696daabca
```

The calculations cited here are generated by
[`calculations/nf_design_guide_part5_wingtip_efficiency.py`](../calculations/nf_design_guide_part5_wingtip_efficiency.py):

```bash
python3 -m pip install -r calculations/requirements.txt
python3 calculations/nf_design_guide_part5_wingtip_efficiency.py
```

The script consumes the current repository owners rather than restating their inputs:

- `design_config.py` for planform, mass, speed, twist, elevon and atmosphere contracts;
- `drag_model.py` for the mandatory separated viscous and induced terms;
- `propulsion_match.py` for the measured-propeller O1 power boundary;
- `yaw_stability.py` for current V1 fin geometry, arm and drag estimate;
- `balance_cg.py` for the controlled CG target;
- `vlm_ala_volante.py` for rigid symmetric span loading; and
- `elevon_sizing.py` for physical-flap effectiveness and pitch-moment yield.

Evidence tags retain the repository convention:

- `[M]`: measured evidence on a relevant physical article;
- `[D]`: deterministic consequence of declared inputs;
- `[E]`: engineering estimate or transferred empirical input; and
- `[I]`: audit diagnostic from an incomplete model, not a design release.

The most important limitations are explicit:

1. `CD_PROFILE_CRUISE = 0.0136` and `e_span = 0.85` are estimates. Holding the profile
   term fixed away from 95 km/h is only a scaling study.
2. Raising `e_span` to 1.00 is a mathematical upper endpoint. It does not predict what any
   winglet will achieve.
3. The VLM is a horizontal flat lifting surface. It cannot model a vertical winglet,
   junction flow, finite sideslip, viscosity, transition, separation or elasticity.
4. The generic local `cl = 0.65` threshold is not a measured root-to-tip `clmax` schedule.
5. Flap-segment results are linear, attached-flow incidence-equivalent yields. They do not
   contain hinge gaps, section moment nonlinearities or separated-flow behavior.
6. No result in this part authorizes a winglet, a flap schedule, manufacture or flight.

## 3. What the NF guide contributes

### 3.1 Induced drag belongs to the complete lift field

The guide correctly moves the discussion away from the popular idea that a winglet merely
blocks pressure equalization or erases a visible tip vortex. The wake is the consequence of
producing lift over the full span. A useful wingtip device changes that complete three-
dimensional loading and can behave like an increase in effective span (PDF pp. 272–279).

For a given lift and span, an elliptical distribution is the minimum-induced-drag reference.
That does not make an elliptical planform or constant local `cl` the best complete aircraft.
At model scale:

- very small tip chords reduce Reynolds number;
- local `clmax` and zero-lift angle change with Reynolds number;
- roughness and transition move the real load distribution;
- trim deflections change the distribution in every flight state; and
- a constant local `cl` distribution can make stall simultaneous and asymmetric.

The transferable requirement is therefore not “make the outline elliptical.” It is:

```text
for every relevant flight state:
    integrate viscous drag from local section state
    + induced drag from the complete 3-D lift field
    + trim/control drag
    + junction/device drag
    while retaining stall and control margins
```

Salamandra's ADR-0009 already enforces the most important bookkeeping rule: viscous and
induced terms must remain separate. That is a repository strength. The weakness is that
neither term has yet been identified on the physical aircraft and the induced efficiency is
not derived from the current geometry.

### 3.2 Every wingtip device has a crossover speed

The guide explains that induced drag grows with lift, while the added profile, pressure and
interference drag of a winglet exists even at low lift. A device can therefore help slow,
high-`CL` flight and hurt fast, low-`CL` flight. The balance point is its crossover velocity
(PDF pp. 278–279 and 297).

That is directly relevant to Salamandra because its primary measurable objective is not
thermal duration or minimum sink. O1 is **1.15 Wh/km at 95 km/h**. A winglet optimized for
45–60 km/h may be a poor O1 device even if it improves circling, approach or stall.

Consequently, “winglet improves efficiency” is not an acceptable requirement or result.
The repository must state:

- the configuration and mass;
- the speed, `CL`, Reynolds number and sideslip range;
- the separate change in viscous/interference drag;
- the separate change in induced drag;
- the propulsion equilibrium and total electrical energy; and
- the change in handling, stability and aeroelastic margins.

### 3.3 The outer wing, junction and winglet are one system

The guide's Snap/Vision comparison is valuable because two wings with superficially similar
main-wing load distributions behaved differently. The likely discriminators were the
winglet-root loading, airfoil choice, junction recovery and finite-yaw separation. The guide
therefore treats the following as inseparable (PDF pp. 280–301):

1. outer-wing lift reserve;
2. transition geometry and pressure recovery;
3. winglet airfoils, twist/toe and Reynolds-number sensitivity;
4. directional stability and the sideslip actually reached; and
5. stall behavior after local asymmetric separation.

This is a stronger standard than Salamandra's present toolchain can meet. The current VLM
can show the symmetric horizontal-wing loading before a device is installed. It cannot show
how the winglet reloads the tip at `beta = 5–20°`, whether the inside or outside junction
separates, or whether the loss produces roll, yaw and pitch transients.

### 3.4 Junction robustness competes with ideal performance

The guide discusses small transition radii, setbacks, gaps, pressure-equalization passages,
turbulators, vortex generators and separation-tolerant root airfoils (PDF pp. 285–297).
These are not interchangeable styling options:

- a smooth large fillet can combine the suction peaks of two sections and create severe
  adverse recovery;
- a small aerodynamic transition limits the area affected if separation occurs;
- moving the winglet aft reduces junction interference and increases yaw arm, but reduces
  its direct lift interaction and complicates structure;
- gaps or pressure equalization can unload the junction but surrender performance;
- turbulators and vortex generators can improve attachment but add drag; and
- a flat or low-lift section can be robust but cannot be assumed efficient.

For a 3D-printed aircraft, aerodynamic and structural radii must be treated separately. A
small external flow-interaction region does not justify a sharp internal load-path corner.
The winglet would need a strong, fatigue-tolerant internal root with an independently shaped
external fairing, printable surface quality and controlled post-processing.

### 3.5 Straight-flight optimization is not a handling-quality proof

The guide deliberately accepts some static performance loss on Snap through progressive
outer washout, toe-out, a short transition and low-Reynolds-number airfoils. The reason is
finite-yaw and stall tolerance. A device optimized at `beta = 0°` can be heavily loaded or
separated in a turn, after a gust or during an imperfect launch (PDF pp. 298–301).

That lesson transfers fully. Article #1 is hand-launched, has no rudder and currently has
only a reduced two-state yaw model. An optimizer that maximizes `L/D` in symmetric flight
without imposing finite-yaw, control and separation constraints would solve the wrong
problem.

### 3.6 Stall location must be interpreted through moment arm, not span label

The guide's general recovery principle is sound: losing lift ahead of the CG tends to remove
a nose-up contribution and promote nose-down recovery; losing lift behind the CG tends to
promote pitch-up. Its examples are principally aft-swept wings, where the outer wing is
usually behind the CG (PDF pp. 280–284 and 308–310).

The transferable rule is:

```text
evaluate the moment of the lift that is lost relative to the actual CG
```

The non-transferable shortcut is:

```text
outer-wing stall always means lift is lost behind the CG
```

Salamandra's outer quarter chord is **ahead** of the CG because the sweep is forward. An
outer stall can therefore create a more favorable direct pitch increment than on the guide's
aft-swept examples. It remains dangerous because it can remove elevon authority and create
large asymmetric roll/yaw. Pitch recovery alone is not an acceptable stall criterion.

### 3.7 Flap management is a multi-state optimization

The guide's Blonde Helene example uses multiple flap segments to separate functions:

- an inner surface contributes trim and camber;
- a middle surface is approximately pitch-moment neutral and reshapes the span loading;
- an outer surface has the opposite pitch influence and manages tip reserve; and
- combinations provide cruise, thermal, speed and braking states (PDF pp. 311–316).

The larger lesson is not that every flying wing needs six servos. It is that trim, local
section drag, induced drag, stall progression and braking must be evaluated together in
every commanded state. Large deflections may trim the aircraft while driving parts of the
span outside their low-drag or attached-flow windows. Linear VLM does not capture the
plateau and collapse behavior of deflected low-Reynolds-number sections.

## 4. The critical Salamandra difference: forward-swept yaw-arm geometry

The repository uses `x` positive aft, with the root quarter chord at zero. The controlled
stations are:

| Station | `x` | Arm `x - xCG` | Isolated yaw implication for the same area and slope |
|---|---:|---:|---|
| Target CG | −93.78 mm | — | Reference |
| Current V1 fin AC | +115.50 mm | **+209.28 mm** | Current arm |
| Wingtip quarter chord | −174.17 mm | **−80.38 mm** | Destabilizing; −38.4% of current fin contribution |
| Wingtip trailing edge | −65.71 mm | **+28.07 mm** | Stabilizing, but only +13.4% of current fin contribution |

For a vertical surface in linear sideforce theory,

```text
Cn_beta,fin is proportional to (S_v / S) (l_v / b) CLalpha_v
```

Holding area, dynamic-pressure ratio and lift-curve slope fixed only to isolate geometry:

- a tip-quarter-chord surface has the wrong arm sign;
- a surface whose aerodynamic center is at the tip trailing edge needs **7.45 times** the
  current total fin area to recover the same fin contribution;
- applying that multiplier to V1's 0.06144 m² total area gives approximately **0.458 m²**,
  which is not a credible solution; and
- matching the current `x_AC` instead requires the wingtip device AC to sit **181.2 mm aft
  of the tip trailing edge**.

The last option resembles the guide's set-back concept, but Salamandra would pay for it
with a long cantilever at the tip. It would add structural load, yaw/roll inertia and an
aeroelastic mass behind the swept wing. Part 4 already found that the aircraft lacks a
flutter clearance and that the conservative divergence case fails. A long, heavy tip
support is therefore a particularly poor Article #1 experiment.

This confirms ADR-0038's rejection of conventional wingtip fins for the current planform.
It does **not** prove that every canted, toed, set-back or actively controlled tip device is
impossible. It proves that such a device must earn its stability and efficiency in the
complete geometry; no benefit follows from the label “winglet.”

### 4.1 Why the current V1 fins are not winglets

V1 uses two vertical surfaces rooted at `y = ±140 mm` in the CORE, with aerodynamic
centers at `x = +115.5 mm`. They are separated from the wingtip lift field and sized as
directional stabilizers. The repository correctly models their drag as an added `Delta CD0`
term and credits no induced benefit.

That architecture loses the guide's attractive dual-use opportunity, but it gains:

- a useful positive yaw arm;
- a short load path into the CORE;
- no panel or tip redesign;
- less tip inertia;
- easier removal and variant testing; and
- clean attribution in E8 stability tests.

The price is large estimated parasite/interference drag and uncertain low-Reynolds-number
fin behavior. Part 3 remains the governing directional-stability audit; Part 5 only shows
why moving the same surface area to the tip does not solve both problems.

## 5. Induced-drag benefit versus the O1 mission

The repository's clean drag screen is:

```text
CD = CD_profile + CD_induced
CD_profile = 0.0136                         [E]
CD_induced = CL^2 / (pi AR e_span)
AR = 5.993; e_span = 0.85                  [E]
```

Using the current V1 reference mass only to hold weight constant gives:

| Speed | `CL` | `CDi`, e = 0.85 | Induced share of estimated total | Estimated CLEAN drag | Maximum saving if `e = 1` |
|---:|---:|---:|---:|---:|---:|
| 45 km/h | 0.5823 | 0.021188 | 60.9% | 0.9389 N | 0.0858 N |
| 60 km/h | 0.3275 | 0.006704 | 33.0% | 0.9742 N | 0.0482 N |
| 75 km/h | 0.2096 | 0.002746 | 16.8% | 1.2254 N | 0.0309 N |
| **95 km/h** | **0.1307** | **0.001067** | **7.3%** | **1.7641 N** | **0.0192 N** |
| 105 km/h | 0.1070 | 0.000715 | 5.0% | 2.1034 N | 0.0158 N |

The off-cruise rows do not predict drag because profile drag is held fixed. They isolate the
scaling that matters: by 95 km/h, almost all of the estimated drag is outside the induced
term. Improving span efficiency from 0.85 to the unattainable perfect endpoint removes
only 0.0192 N.

### 5.1 Optimistic crossover calculation

If a device adds `Delta CD0` and changes only the induced efficiency from `e0` to `e1`, the
optimistic crossover lift coefficient is:

```text
CL_cross = sqrt[Delta CD0 pi AR / (1/e0 - 1/e1)]
```

With `e0 = 0.85` and the ideal `e1 = 1.00`:

| Added `Delta CD0` | `CL_cross` | `V_cross`, V1 mass | Interpretation |
|---:|---:|---:|---|
| 0.00025 | 0.1633 | 84.97 km/h | Helpful only below this speed under the ideal assumption |
| 0.00050 | 0.2310 | 71.45 km/h | Same |
| 0.00100 | 0.3266 | 60.08 km/h | Same |
| 0.00200 | 0.4619 | 50.52 km/h | Narrow usable low-speed interval |
| **0.003369** | **0.5995** | **44.35 km/h** | Beyond released `CLmax`; no level-flight crossover before V1 stall |

The final row is intentionally hypothetical. The current CORE fins do not raise span
efficiency. It shows that even if a device with their parasite increment somehow achieved
the ideal `e = 1`, its crossover would lie just below the calculated V1 stall and require
`CL = 0.5995`, above the released wing value 0.589.

At 95 km/h, the perfect-efficiency induced-coefficient saving is only **0.000160**. A new
wingtip device must add less than that to improve the CLEAN aerodynamic estimate. This is
an exceptionally demanding threshold for a printed device with two sides, a junction,
surface roughness and attachment hardware.

### 5.2 Current O1 consequence

At the 95 km/h O1 point, using the same estimated polar and V1 mass:

| Quantity | CLEAN aerodynamic model | V1 with current fin estimate | O1 boundary |
|---|---:|---:|---:|
| Drag | 1.7641 N | **2.1694 N** | **maximum 2.1226 N** |
| Margin to boundary | +0.3585 N | **−0.0468 N** | — |
| Propeller-model total energy | 1.003 Wh/km | **1.169 Wh/km** | **maximum 1.150 Wh/km** |

This is not an E2 polar or an E3 acceptance result. It is a deterministic consequence of
the repository's own `[E]` drag assumptions and measured-propeller interpolation. It says:

- CLEAN has analytical room under O1 but lacks passive directional stability;
- V1 has the intended passive stability architecture but consumes the modeled O1 margin;
- the V1 estimate misses O1 by only 0.0468 N, so surface finish, junctions and actual
  propulsive efficiency can change the conclusion; and
- no winglet should be justified by an induced-drag percentage while omitting its complete
  O1 electrical equilibrium.

This is exactly the kind of coupled trade the NF guide advocates.

## 6. Outer-wing reserve and stall architecture

### 6.1 What the current symmetric model says

At the 45 km/h requirement with V1 mass, the rigid 80×8 VLM produces:

| Span station `eta` | Local `cl` | Margin to generic 0.65 screen | Quarter chord relative to CG |
|---:|---:|---:|---:|
| 0.506 | 0.6287 | +0.0213 | +5.7 mm aft |
| **0.603** | **0.6320** | **+0.0180** | **11.3 mm forward** |
| 0.693 | 0.6247 | +0.0253 | 26.9 mm forward |
| 0.797 | 0.5919 | +0.0581 | 45.1 mm forward |
| 0.900 | 0.4992 | +0.1508 | 62.9 mm forward |
| 0.945 | 0.4096 | +0.2404 | 70.7 mm forward |

The current wing does show a useful reduction in local loading over the last 20% of the
semispan. That qualitatively agrees with the guide's requirement for outer reserve. It does
not prove the reserve needed for a winglet because:

- the winglet-induced increment is absent;
- the condition is symmetric `beta = 0°`;
- the local threshold 0.65 is generic, not a Salamandra r1 polar;
- tip Reynolds number is only about 120,500;
- print roughness, waviness, seams and the fixed tip closure are absent; and
- control deflection and elastic twist are absent.

The apparent tip margin is therefore a good starting geometry, not a stall clearance.

### 6.2 The high-loaded band crosses the CG moment boundary

The quarter-chord line crosses `xCG` at `eta = 0.538`. The broad high-`cl` region near
`eta = 0.50–0.70` lies on both sides of that crossing. Its peak is only 11.3 mm forward of
the CG. Small changes in transition, airfoil `clmax`, elevon deflection, manufacturing
twist, sideslip or elasticity can therefore move the first lost lift between opposite pitch-
moment signs.

The repository currently cannot establish either of these required facts:

1. the initial lost-lift centroid produces a nose-down recovery moment; and
2. sufficient roll/yaw control remains after that loss.

This is a more precise weak point than the generic phrase “tip-stall risk.” The problem is
that the predicted peak and the CG crossing nearly coincide, while the model has none of
the physics that selects the real separation point.

### 6.3 Wash-in cannot also be spent as winglet reserve

The guide's successful aft-swept examples use progressive negative washout toward the tip.
Salamandra uses **+3° linear wash-in** because forward sweep, airfoil moment, static margin
and trim were solved together. The current VLM sensitivity at the same aircraft `CL` is:

| Linear tip twist | Peak local `cl` | Peak `eta` | Margin to 0.65 screen |
|---:|---:|---:|---:|
| 0° | 0.6259 | 0.328 | +0.0241 |
| +2° | 0.6260 | 0.539 | +0.0240 |
| **+3°** | **0.6320** | **0.603** | **+0.0180** |
| +4° | 0.6406 | 0.634 | +0.0094 |
| +5° | 0.6509 | 0.664 | **−0.0009** |

Increasing wash-in to compensate a device's trim or loading is therefore not available.
Conversely, replacing the current twist with the guide's washout is not free. The linear
VLM pitch yields imply:

| Twist schedule | Ncrit-12 symmetric trim estimate |
|---|---:|
| Current +3° wash-in | +0.52° elevon |
| 0° linear twist | +4.57° elevon |
| −2° linear washout | +7.27° elevon |

Each degree of removed wash-in requires approximately 1.35° additional symmetric elevon
in this model. Those larger commands would change section moment, local `clmax`, drag and
stall progression—the exact coupled penalties the guide warns against.

The correct future trade is not “wash-in versus washout.” It is a joint re-optimization of:

- nonlinear geometric twist, including a localized outer schedule;
- root-to-tip airfoil/reflex family;
- CG and static margin;
- control segmentation and trim schedule;
- finite-yaw outer-wing/winglet loading;
- local measured polars; and
- divergence and flutter.

Until that exists, retain the released +3° geometry as a provisional trim solution and do
not describe it as a demonstrated stall-safe distribution.

## 7. Low-Reynolds-number and printed-junction consequences

The current horizontal-wing Reynolds context is:

| Speed | Root Reynolds number | Tip Reynolds number |
|---:|---:|---:|
| 45 km/h | 241,000 | **120,500** |
| 60 km/h | 321,400 | 160,700 |
| 75 km/h | 401,700 | 200,900 |
| 95 km/h | 508,800 | **254,400** |
| 105 km/h | 562,400 | 281,200 |

A slender winglet would normally use a chord smaller than the 144.6 mm wingtip chord and
would therefore operate at still lower Reynolds number. The guide's warning is directly
applicable: a tall, narrow device may have attractive induced geometry while its section
cannot sustain the assumed loading, especially at yaw.

For a printed winglet, a credible definition must include:

- root, intermediate and tip aerodynamic coordinates with finite trailing-edge thickness;
- section polars over Reynolds number, roughness, transition, toe and sideslip;
- external junction surfaces and pressure-recovery intent;
- internal spar/web/socket geometry and load transfer into the panel;
- print orientation, seams, wall schedule and measured surface waviness;
- drain/vent and pressure-equalization details if present;
- mass, CG and inertia of each complete device;
- repeatable alignment and toe tolerances; and
- a replaceable failure mode that does not damage the primary torsion box.

### 7.1 What should not be copied from the guide without evidence

- **Small transition radius:** useful as an aerodynamic separation-area strategy, not an
  excuse for a structural notch.
- **Set-back winglet:** promising for arm and junction relief, but exceptionally costly in
  a printed forward-swept tip with unresolved flutter.
- **Flat plate:** potentially separation-tolerant, but the current V1 plate-like concept
  already has uncertain slope, drag and root flow; robustness must be measured.
- **DSA passage or gap:** a testable low-speed device, not free performance.
- **Turbulator or vortex generator:** a configuration-controlled boundary-layer device;
  location, height, roughness and drag must be tested.
- **Large winglet for smaller yaw:** circular unless the complete finite-yaw derivatives
  and stall behavior are demonstrated.

The sensible Article #1 baseline remains the simplest one: a flat closure whose mass,
surface and geometry can be measured, followed by reversible instrumented variants.

## 8. Flap management versus the current two-servo architecture

Article #1 has one 28%-chord elevon per half-wing from `eta = 0.35` to `0.90`. Two servos
provide symmetric pitch and differential roll commands. They do **not** provide independent
spanwise camber or loading control.

Dividing the existing span virtually and applying a symmetric +1° incidence-equivalent
command gives:

| Hypothetical segment | Area per side | `Delta Cm0` per degree |
|---|---:|---:|
| `eta = 0.35–0.50` | 62.2 cm² | −0.0001524 |
| `eta = 0.50–0.70` | 73.7 cm² | +0.0006499 |
| `eta = 0.70–0.90` | 63.2 cm² | +0.0013307 |
| Current combined `0.35–0.90` | 199.0 cm² | +0.0018282 |

A ten-percent-span moving window crosses zero pitch yield at approximately
`eta = 0.415–0.515`, centered at 0.465. The sign distribution is specific to the current
forward-swept geometry and the repository's linear model; it must not be copied from the
guide's aft-swept chart.

This produces two useful conclusions:

1. The current elevon combines regions with opposite pitch leverage. Its net pitch and roll
   performance can look acceptable while concealing spanwise opportunities or penalties.
2. A future segmented panel could use a near-neutral middle segment to reshape loading
   without a large first-order trim change, but the nonlinear section and structural costs
   remain unknown.

### 8.1 Why Article #1 should not immediately adopt six flaps

The Blonde Helene is an all-round thermal/speed glider. Salamandra Article #1 is a compact,
printed, powered FPV aircraft with a specific 95 km/h energy objective. Adding three
surfaces per side would imply four additional actuators, wiring, power, openings, hard
points, freeplay sources and moving masses. Those changes directly affect:

- the O1 hotel and propulsion budget;
- the 1.60 kg mass/stall closure;
- the printed torsion box;
- control-surface modes and flutter;
- maintenance and field reliability; and
- FC mixing and failure analysis.

The current repository decision to release no flap/flaperon mode is therefore sound. The
weakness is not the absence of a six-flap aircraft. It is the absence of a multi-state
aerodynamic analysis proving that the simple elevon is adequate.

### 8.2 Required control-state matrix

Before any symmetric schedule is released, the model and tests must cover at least:

| State | Aerodynamic questions | Control/structural questions |
|---|---|---|
| Hand launch | high `CL`, transient thrust, roll/yaw upset | pitch reserve, differential reserve, saturation |
| 45 km/h slow flight | local `clmax`, finite sideslip, outer reserve | retained roll and nose-down recovery |
| Climb | propeller wake and higher power | trim, thermal load and servo duty |
| 95 km/h O1 cruise | section-drag bucket and total drag | small trim, no hunting/freeplay |
| 105 km/h initial cap | low `CL`, surface reversal sensitivity | hinge moment and modal margin |
| Approach/landing | gust, yaw, sink and ground proximity | controllable flare and go-around |
| Brake command | separated-flow topology and pitching moment | actuator load, asymmetry and safe retraction |
| Maximum roll command | adverse yaw and one-sided outer loading | combined hinge/torsion load and rate limit |

For every row, report local `Re`, `cl`, flap angle, section drag, section moment, margin to
measured `clmax`, complete-aircraft trim, control reserve and structural load. A single
neutral-elevon VLM result is not a schedule.

## 9. Direct contrast: guide lessons versus repository maturity

| Topic | NF guide lesson | Current repository strength | Current weak point | Engineering disposition |
|---|---|---|---|---|
| Induced drag | Optimize the complete lift field | Viscous and induced terms are separated | `e = 0.85` is assumed, not derived or measured | Retain as sensitivity only |
| Mission trade | Winglets have a crossover speed | O1 has a precise speed, power and energy boundary | No wingtip trade is connected to propulsion equilibrium | Add mission-weighted device trade |
| Outer reserve | Winglet reloads the outer wing | Current symmetric VLM shows unloading near the tip | No finite-yaw/device/local-`clmax` calculation | No winglet release |
| Stall location | Lost-lift moment relative to CG governs pitch recovery | CG and planform stations are controlled | High-loaded band straddles the CG crossing; no nonlinear stall | Build lost-lift moment and control-reserve maps |
| Junction | Transition separation can dominate handling | Flat cap avoids a winglet junction on Article #1 | No winglet/junction CAD or flow model exists | Keep baseline simple |
| Low Reynolds number | Slender devices may not sustain assumed loading | Root/tip Reynolds numbers are reproducible | No winglet airfoil family or measured printed polar | Test sections before a device |
| Directional stability | Winglets can perform two functions | V1 stability and drag are tracked separately | Tip arm is adverse or very short on this FSW planform | CORE fins remain the rational baseline |
| Washout | Progressive outer unloading improves tolerance | Twist is configuration-controlled | +3° wash-in is trim-driven and leaves limited screen margin | Re-optimize, do not copy |
| Flap management | Optimize trim, drag, lift distribution and stall together | Elevon geometry/yields are reproducible | One surface cannot schedule spanwise states; no nonlinear schedule model | Retain hardware, expand analysis |
| Validation | Experience must be checked in real flight | E2/E3/E8 gates exist | No physical article or accepted polar exists | No performance/flight claim |
| Structure | Winglets must be light; tip inertia matters | V1 fins are CORE-rooted | Wingtip/aft-set device conflicts with unresolved flutter | GVT/aeroelastic clearance first |

## 10. Repository weak points exposed by Part 5

### P0 — blocks a winglet or flap release

1. **No aircraft-level viscous/induced drag identification.** `CD0 = 0.0136` and
   `e_span = 0.85` remain estimates; no E2 polar separates them.
2. **No finite-sideslip three-dimensional wing/device model.** The VLM cannot represent a
   vertical surface, junction or yawed asymmetric loading.
3. **No local section database.** Root-to-tip `clmax`, `cd`, `cm`, transition and roughness
   are not available for the printed r1 family and control deflections.
4. **No demonstrated stall sequence.** The current high-loaded span band crosses the CG
   moment boundary and the analysis cannot select real separation.
5. **No control-state closure.** No symmetric flap/flaperon or brake schedule has a
   nonlinear aerodynamic, servo and structural proof.
6. **No wingtip structural/aeroelastic definition.** Part 4's divergence/flutter gaps make
   added tip mass or long setback unacceptable without new analysis and GVT.
7. **No manufacturing-authoritative device geometry.** Airfoils, toe, cant, junction,
   load path, attachment, mass and tolerances are undefined.

### P1 — materially weakens design confidence

1. The current drag model has no Reynolds-number or surface-finish dependence.
2. The V1 fin drag estimate does not include measured as-built junction/wake effects.
3. The generic local `cl = 0.65` screen can be mistaken for an airfoil capability even
   though it is not a measured spanwise limit.
4. Linear twist is used where the guide shows that localized/exponential outer twist can
   be the useful degree of freedom.
5. The two-servo control study optimizes pitch/roll screening, not complete mission-state
   drag and stall behavior.
6. No uncertainty or tolerance propagation links print twist, toe, surface waviness and
   hinge gaps to loading or trim.
7. CLEAN and V1 solve different primary problems, but no integrated requirement ranks O1
   efficiency against minimum passive directional stability.

### P2 — documentation and future-development gaps

1. The design guide says “flat end cap; no winglet” but does not yet record the numerical
   yaw-arm and cruise-crossover reasons in one controlled trade.
2. Candidate wingtip devices are listed in the remediation plan without a standard
   geometry/model/test data package.
3. No generated table compares variant mass, inertia, `Cn_beta`, drag, crossover speed,
   stall reserve and flutter impact.
4. There is no naming/configuration convention for interchangeable tip modules, their
   left/right alignment or their FC parameter set.

## 11. Required engineering workflow for any future wingtip device

### W0 — requirements before geometry

Define whether the device is intended to improve:

- O1 energy at 95 km/h;
- minimum sink or endurance;
- slow-flight controllability;
- passive directional stability;
- yaw damping;
- launch/landing robustness; or
- more than one objective with stated weighting.

Set numerical acceptance gates before running an optimizer. A low-speed handling device
may be acceptable even if it increases O1 drag, but it must not be called an O1 efficiency
improvement.

### W1 — parametric geometry and mass

Create reversible candidates that control:

- in-plane setback and aerodynamic-center arm;
- height, taper, cant, toe and sweep;
- root/tip airfoil family;
- junction radius, gap or pressure-equalization feature;
- external aerodynamic fairing versus internal structural root;
- attachment stiffness and repeatability; and
- complete printed mass, CG and inertia.

Include the present flat cap and CORE V1 fins as mandatory comparison cases.

### W2 — local aerodynamic evidence

Generate or measure section polars over the relevant Reynolds and control ranges. At
minimum:

```text
main wing: Re = 120k ... 560k
winglet: candidate-specific Re, likely extending below 120k
alpha: through attached flight and stall
beta/toe: both signs over the operational disturbance range
roughness: smooth reference and representative printed surface
controls: every proposed symmetric and differential deflection
```

XFOIL can screen attached two-dimensional sections but cannot close the junction, finite-
yaw or separated-flow problem. Use wind-tunnel or validated CFD/experiment correlation for
the critical candidates.

### W3 — complete-aircraft three-dimensional model

The model must output, for each speed, `CL`, control state and sideslip:

- total forces and moments;
- `Cn_beta`, `Cn_r`, `Cy_beta`, roll/yaw coupling and adverse yaw;
- near-field span load on both halves;
- winglet and junction load;
- separate viscous/interference and induced drag;
- lost-lift moment about the actual CG; and
- remaining control authority.

A horizontal VLM with a manually adjusted span-efficiency number is not sufficient.

### W4 — mission and control optimization

Compare the flat cap, CORE fins and each device through the complete state matrix in
Section 8.2. Optimize total electrical energy at the actual propeller equilibrium, not
`L/D` alone. Use virtual flap segmentation first; add actuators only if the quantified
mission or safety benefit exceeds mass, power, structure and reliability costs.

### W5 — structure and aeroelasticity

For every retained device:

- calculate limit/ultimate junction loads in symmetric and asymmetric flight;
- measure attachment rotational stiffness and freeplay;
- update mass properties and the complete-aircraft modal model;
- repeat GVT with the heaviest and most aft-set module;
- include winglet aerodynamic and inertial coupling in flutter analysis; and
- proof-load a representative printed root and panel interface.

No device advances if it reduces the already-open conservative divergence/flutter margin
without a validated mitigation.

### W6 — physical comparison

Use instrumented, configuration-controlled A/B testing:

1. flat caps;
2. flat caps plus CORE V1 fins;
3. the lightest credible wingtip candidate; and
4. only then any larger, set-back or boundary-layer-control variant.

Measure mass/CG, surface geometry, power-off and power-on glide polar, electrical Wh/km,
yaw perturbation/decay, control inputs, sideslip if available, stall sequence and modal
response. Randomize test order where practical and repeat points so small drag differences
are not confused with atmosphere or battery state.

## 12. Proposed acceptance matrix

| Gate | Required evidence | Flat cap | CORE V1 | Future winglet |
|---|---|---|---|---|
| Configuration definition | Native CAD, mass, CG, alignment tolerances | Partial `[I]`; no manufacturing CAD | Partial `[D/E/I]` | Absent |
| O1 performance | E2 drag + E3 total energy at 95 km/h | Open | Open; current estimate slightly fails | Open |
| Directional static stability | Positive agreed lower `Cn_beta` gate | CLEAN estimate fails | V1a lower corner still open | Absent |
| Finite-yaw behavior | Valid derivatives and no junction separation in envelope | Open | Open | Absent |
| Stall pitch response | Lost-lift moment promotes recovery | Open | Open | Absent |
| Roll authority after incipient stall | Measured/model-correlated reserve | Open | Open | Absent |
| Local section capability | Printed polars across `Re`, roughness and deflection | Open | Open | Absent |
| Structural root | Limit/ultimate proof and inspectable load path | Flat cap only | Open F2 | Absent |
| Flutter | Correlated GVT/unsteady model with installed module | Open | Open | Absent |
| Mission crossover | Measured total drag/energy versus speed | Not applicable baseline | No induced credit | Absent |

No current configuration passes the complete flight-release matrix. That statement is
consistent with v0.6.0's explicit status as a documentation integration release.

## 13. Immediate repository changes recommended

1. Add this audit's yaw-arm and crossover results to the controlled wingtip-candidate
   trade; do not change the Article #1 geometry.
2. Label `e_span = 0.85` everywhere as an unvalidated induced-only estimate and prevent it
   from being read as a measured Oswald factor.
3. Extend the drag owner with configuration, Reynolds number and uncertainty inputs while
   preserving separate viscous and induced outputs.
4. Add a complete-aircraft wingtip trade owner that reports mass, inertia, yaw arm,
   `Cn_beta` band, `Delta CD0`, induced benefit, crossover speed and O1 energy.
5. Add finite-sideslip vertical-surface capability through an appropriate 3-D method; do
   not force winglets into the current horizontal VLM.
6. Replace the single generic local-`cl` screen with spanwise measured/predicted
   `clmax(Re, roughness, delta)` envelopes and a lost-lift moment calculation.
7. Add nonlinear/localized twist as a design variable while keeping trim, divergence and
   manufacturing tolerance in the same trade.
8. Use the virtual flap-segment yields to study mission states before considering more
   servos or hinge cuts.
9. Keep the “no flap/flaperon mode released” statement until the complete state matrix and
   E2 evidence close.
10. Define a wingtip-module CAD/test standard: datums, alignment, mass/inertia, root proof,
    GVT and configuration-specific FC parameters.
11. Require every claimed device improvement to report its speed range and crossover; ban
    unqualified percentage claims.
12. Preserve flat caps and CORE fins as A/B references so future results remain attributable.

## 14. Part 5 conclusion

The NF Design Guide does not provide Salamandra with a ready-made winglet. It provides a
better question: **at which flight state does a complete outer-wing/device system improve
the aircraft after its viscous drag, junction flow, yaw behavior, stall progression, mass
and flexibility are included?**

For Article #1, the current answer is unfavorable at the primary mission point. At
95 km/h, induced drag is only 7.3% of the estimated CLEAN total, and even the mathematical
improvement from `e = 0.85` to 1.00 saves only 0.0192 N. The forward-swept tip also has the
wrong quarter-chord yaw arm; moving a device far enough aft to recover the present V1 arm
creates exactly the tip-mass and flutter penalties that Part 4 says are unresolved.

The repo made two sound choices before this audit: keep Article #1's tips simple and reject
flap scheduling until evidence exists. Its main weakness is that those cautious decisions
are not yet surrounded by a complete aerodynamic method. Span efficiency is assumed,
local section capability is unknown, finite sideslip is absent, and the high-loaded band
lies across the CG moment boundary.

The engineering conclusion is therefore conservative and actionable:

- fly no design claim from the present winglet arithmetic;
- retain flat caps and CORE-rooted fins as separate controlled baselines;
- measure the aircraft and printed sections;
- build the finite-yaw, local-polar and aeroelastic models; and
- introduce reversible wingtip variants only if their mission-specific benefit survives
  the full system trade.

[Part 6](NF-Design-Guide-2024-Repository-Audit-Part-06-Design-Method-Synthesis.md) covers
the guide's final pages 317–331: airfoil geometry and optimization, swept-section
interpretation, state-dependent spanloads, static-margin iteration, artificial stability
and flap definition, contrasted with Salamandra's present r1 workflow.
