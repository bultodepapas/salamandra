# Salamandra master design plan

**Revision 2.1** · 21 August 2026 · **Programme reset — Gate M0 closed; Gate M1 open**

**Document role:** canonical programme-control document for defining, designing,
validating and handing Salamandra Article #1 to a human CAD designer.

**Authorization:** aerodynamic production CAD, manufacturing release and flight remain
on hold. The released v0.6 geometry is retained as a well-developed comparison candidate,
not accepted as the final aircraft.

---

## 0. Authority and use

This plan answers four questions:

1. What aircraft is Salamandra trying to become?
2. What must be decided now, and what must remain open?
3. In what dependency order shall the aircraft be designed?
4. What evidence must exist before the human CAD designer receives a manufacturing brief?

It supersedes the former F1→F6 orchestration in this file and the sequence in
[`03-phase-1-plan.md`](03-phase-1-plan.md). That document remains useful as a historical
technical workstream. The present plan does not erase prior work: calculations, ADRs,
research threads, SVG sheets and v0.6 geometry are controlled inputs to the new trade.

Where documents conflict:

1. this plan owns **programme intent, sequence, gate status and authorization**;
2. [`00-objectives-and-requirements.md`](00-objectives-and-requirements.md) owns the
   active Article #1 mission and product requirements;
3. `calculations/mission_contract.py` owns the redesign mission/configuration constants,
   while `calculations/design_config.py` owns only the current v0.6 numerical baseline
   until a new candidate is selected;
4. ADRs own accepted technical decisions for their declared configuration; and
5. the concise Design Guide owns CAD execution only after this plan authorizes a new
   controlled edition.

No existing `FIXED` label silently carries into the redesigned aircraft. Each value is
either retained by a new trade, reopened explicitly, or confined to the v0.6 reference.

---

## 1. Product intent

### 1.1 Mission statement

Salamandra Article #1 shall be a **single-motor, front-camera, tailless FPV aircraft,
predominantly 3D printed in PETG**, optimized for the lowest practicable total battery
energy per kilometre while retaining useful, confidence-inspiring handling and field
durability.

It is an efficient FPV aircraft that is pleasant to manoeuvre, not a maximum-endurance
glider and not an aerobatic roll-rate project.

### 1.2 Objective hierarchy

The order below is binding. A lower objective cannot override a higher one.

| Priority | Objective | How it is judged |
|---|---|---|
| **P0** | Safe, controllable and testable | Passive first-flight stability, adequate control reserve, closed structural ground gates, pitot/current/blackbox data |
| **P1** | Minimize total electrical `Wh/km` | Measured battery energy including propulsion, avionics, FPV and conversion losses over the declared cruise matrix |
| **P2** | Retain practical agility | Trims without saturation; makes commanded bank changes and coordinated turns without sluggish or divergent response; retains recovery authority near approach |
| **P3** | Durable and field-repairable | PETG primary structure, replaceable printed modules, inspectable joints, survivable normal handling and landing loads |
| **P4** | Simple, open and reproducible | One motor, a small bought-in parts set, Python-owned calculations, traceable decisions and a reconstructible human-CAD handoff |
| **P5** | Preserve the Salamandra visual identity | Flying-wing form and, if technically competitive, forward sweep and a short, slender nose |

**Efficiency is an optimization objective, not an unsupported promise.** The programme
does not impose a 100 km range or any other arbitrary range target. Range and endurance
are reported outcomes of measured usable pack energy and the measured power curve.

The legacy `≤1.15 Wh/km at 95 km/h` requirement remains a useful external comparator and
falsifiable reporting point. It is not the only optimization state and does not justify
an aircraft that is poor elsewhere. Gate M0 defines the E0–E3 comparison matrix and
Pareto selection rule; no stakeholder weights are assumed.

**Agility is deliberately not reduced to “must perform a roll.”** Gate M0 defines the
required handling evidence and trim reserve; Gate M5 freezes a quantitative bank-response
test card from the selected aircraft model before flight. The design models control
reserve, inertia and modes to prevent an inefficient or unsafe result; it does not
optimize an arbitrary headline roll rate.

### 1.3 Hard product constraints

| ID | Constraint | Present interpretation |
|---|---|---|
| **C-AIRFRAME** | Flying wing / tailless Article #1 | Conventional tails are outside Article #1 unless all tailless candidates fail a P0 gate |
| **C-POWER** | One electric motor | Centreline pusher is the working baseline because it preserves the forward camera view; tractor remains a trade only if it solves a material problem |
| **C-FPV** | FPV camera at the front | Unobstructed forward field of view; serviceable camera; video transmitter cooling and antenna clearance |
| **C-BAT** | 21700 Li-ion, 6S or 8S architecture | 6S1P is the lower-risk first-prototype baseline; 8S1P is a controlled power-module candidate, not a battery-only swap |
| **C-TRAVEL** | Real CG adjustment | Battery carrier provides **at least 20 mm total longitudinal travel**, preferably ±10 mm about the nominal solution, after connector and retention allowances |
| **C-PRINT** | Desktop manufacture | Fits a 256 mm-class enclosed printer through deliberate segmentation |
| **C-MAT** | PETG primary airframe | Conventional light-colour PETG is the default structural print material; any local exception requires its own process data and ADR |
| **C-CAD** | Human-built native CAD | This repository delivers the requirements, geometry, loads, envelopes, drawings and evidence; a human CAD designer produces the native parametric assembly |
| **C-OPEN** | Open, traceable platform | Every released quantity has an owner, evidence tag, calculation or source and change history |

### 1.4 Required experimental configurations

Article #1 shall preserve a reversible directional-control experiment:

| Configuration | Purpose | Release order |
|---|---|---|
| **SALAMANDRA-6S-R** | Removable vertical-tail module with passive fin area and a rudder-capable trailing portion. It is the first-flight configuration. The rudder may be locked neutral during part of the test matrix to separate passive-fin benefit from active-control benefit. | First |
| **SALAMANDRA-6S-CLEAN** | No vertical-tail module. Measures the real efficiency and yaw-handling consequence of the clean flying wing. | Only after SALAMANDRA-6S-R identifies a safe baseline |
| **SALAMANDRA-8S-STUDY** | Separate complete voltage, mass, loss, packaging and propulsion architecture study. | Not a first-flight configuration |

The number, location, area and movable fraction of the vertical surfaces are **open design
outputs**. The existing passive twin-fin V1a is one candidate. ADR-0038 does not force it
into the redesign, and its current negative lower stability corner prevents treating it as
closed. A rudder servo is therefore a reserved envelope in early packaging, not yet an
Article #1 purchased part.

### 1.5 Preferences, not requirements

- Forward sweep is preferred visually and remains the lead candidate **only if** it is
  Pareto-competitive after equal-requirements aerodynamic, structural, stability, mass and
  packaging comparison.
- A short nose is preferred. Nose length is minimized after CG, camera, pack removal,
  wiring, structure, yaw and pusher-inflow constraints close; it is not prescribed first.
- A flat, one-cell-high battery region is preferred. Width versus length is selected from
  the complete body trade, not from pack frontal area alone.
- The clean finless configuration is desirable for efficiency research, but it cannot be
  the first-flight default without measured directional-stability evidence.

### 1.6 Explicit non-goals

- no fixed maximum-range claim;
- no thermal-soaring or minimum-sink specialization;
- no speed-record mission;
- no aerobatic roll-rate target;
- no requirement that one unchanged motor, ESC or carrier accept both 6S and 8S;
- no active-stability shortcut around an unsafe passive first-flight aircraft;
- no universal equipment bay that grows the airframe to accept every product; and
- no manufacturing CAD before the upstream gates in this plan close.

---

## 2. Programme reset: what is retained and what is reopened

| Item | Disposition | Reason |
|---|---|---|
| Evidence tags, ADRs, gaps and reproducible-calculation policy | **Retain** | They are the project's quality system |
| Python/NumPy, XFOIL, VLM, Weissinger-L and generated SVG workflow | **Retain** | Existing reproducible toolchain; each method keeps its known validity limits |
| Single motor, front FPV camera, 21700 cells, PETG and printed modular construction | **Retain as intent** | Direct user and platform constraints |
| Current 1.300 m forward-swept v0.6 aircraft | **Reference candidate A** | Substantial useful evidence, but trim, yaw, OML, structure and physical validation remain open |
| 6S1P P42A + APC E 8×8 + 500–550 Kv power chain | **Working Article #1 baseline** | Current calculations close the 6S screening point; exact motor and operating point still need bench/drag data |
| 8S1P | **Reopened variant trade** | Adds 140 g and presently fails the 45 km/h analytical screen; it also requires an 8S-rated electrical chain |
| −15° forward sweep | **Reopened** | Selected inside a restricted historical trade; must compete against straight and aft-swept tailless candidates |
| r1/r2a airfoil and +3° wash-in | **Hold / test candidates** | Operating-`Cm(CL)` and printed-section evidence are not closed |
| 28% elevons and two 12.5 g servos | **Working baseline** | Useful packaging and authority start point; final geometry follows the selected aircraft and printed hinge tests |
| Passive twin-fin V1a | **Comparison candidate** | Credible packaging work exists, but the lower `Cn_beta` corner remains negative and no rudder is present |
| Current fuselage OML | **Discard as design authority** | It is explicitly `[I]` and `aircraft_feasible: false`; retain only as a generator/test asset |
| 80/100 km range and 60 min endurance targets | **Withdraw as requirements** | The user requires maximum practicable efficiency, not arbitrary range/endurance numbers |
| `≤1.15 Wh/km at 95 km/h` | **Retain as comparator** | Useful legacy benchmark and acceptance reporting point, not the complete objective function |

---

## 3. Bought-in systems: working baseline before aerodynamic redesign

Electronics must be defined early enough to establish mass, volume, power, heat, wiring
and CG. They must not be frozen more precisely than the evidence allows. The programme
therefore uses three statuses:

- **CLASS:** capability and bounding envelope required for architecture work;
- **REFERENCE PART:** named component used for the first mass skeleton and procurement;
- **RELEASED PART:** actual batch measured and bench-accepted before production CAD.

### 3.1 Article #1 working bill of materials

| System | Reference part / class | Controlled design input now | Required closure |
|---|---|---|---|
| Battery | **6S1P Molicel P42A**, one-cell-high pack | 445 ±5 g installed estimate; 90.72 Wh arithmetic nominal; compare the 223.2×44.0×22.6 mm narrow and 142.8×70.8×22.6 mm moderate-width layouts | Build pack/dummy; measure complete envelope, leads, connector sweep, mass, removal and usable energy |
| 8S study pack | **8S1P P42A** | 585 ±5 g; 120.96 Wh; separate power module | Must recover current stall/mass deficit and pass an 8S electrical/thermal bench map |
| Propeller | **APC Thin Electric 8×8** datum | 203.2 mm disk; existing UIUC/APC model and rpm-limit evidence | Bench map with selected motor/ESC; compare at least two credible diameter/pitch alternatives after aircraft drag is known |
| Motor | 28-class, **500–550 Kv**, approximately 170 g, ≥400 W peak reference class | Envelope and mass for 6S packaging; no exact product release | Select from measured 6S motor/ESC/propeller maps at the aircraft operating points |
| ESC | 6S, ≥30 A class with current/temperature margin | Approximately 35 g reference envelope; telemetry desirable | Bench voltage, current, rpm, efficiency, thermal state, braking and failure behaviour |
| Flight controller | **SpeedyBee F405 WING** reference; Matek F405-WING-V2 fallback | Pitot/I2C, current sensing, barometer, microSD blackbox, adequate PWM/UART; use the full WING board, not the MINI by assumption | Procured-board pin/resource test and current calibration; firmware target verified at build time |
| Elevon servos | **2× digital metal-gear 12–15 g class**; Corona DS-939MG reference | One per elevon; ≥1.643 kgf·cm current factored static screen; low free play and adequate holding stiffness dominate | Measure actual batch mass, travel, speed, deadband, stiffness, current and heat; final torque/rate from the selected control surface |
| Rudder servo | Same class or smaller, **reserved only** | Bounding mass/envelope included in SALAMANDRA-6S-R mass skeleton | Select only after rudder authority, hinge load and required rate are known |
| FPV | **DJI O4 Air Unit** | Front camera 13.44×12.36×16.50 mm; VTX 30×30×6 mm; 50 mm coax; 8.95 g installed bare mass; cooling required | Physical connector/bend/FOV mock-up and measured power at selected settings |
| Navigation | M10-class GPS + magnetometer | External field-of-view and electromagnetic keep-out; separate from high-current path | Bench interference and installed compass/current test |
| Air data | MS4525-class digital pitot | Mandatory I2C resource and pressure-tube route | Calibration, leak test and comparison against a reference pressure source |
| Receiver | ELRS 2.4 GHz class | UART, antenna keep-out and failsafe | Range/failsafe and installed RF test |

The reference parts are concrete enough to draw the mass skeleton and buy test hardware.
They are deliberately replaceable. A substitution inside the controlled mass, envelope,
power, cooling, interface and performance bounds is a ledger update; a substitution
outside any bound reopens the dependent gate.

### 3.2 6S versus 8S programme decision

The first prototype is **6S1P**. Current reproducible screening gives:

| Quantity | 6S1P | 8S1P | Consequence |
|---|---:|---:|---|
| Installed pack mass | 445 ±5 g | 585 ±5 g | 8S adds 140 g |
| Arithmetic nominal energy | 90.72 Wh | 120.96 Wh | 8S adds 33.3% energy |
| Current CLEAN stall screen | 44.06 km/h | 46.00 km/h | 8S fails the inherited 45 km/h requirement at unchanged aircraft |
| Current FC/PDB compatibility | 6S baseline | Not released | SpeedyBee's official page states `7–36 V` and `2–6S`; treat as 6S-only until resolved |
| Motor starting band for APC 8×8 | 500–550 Kv | approximately 375–413 Kv | A different motor/ESC/PDB map is required |

This decision does not reject 8S. It prevents the first article from carrying the mass,
stall, voltage and procurement risks of two aircraft at once. Gate M2 shall preserve a
credible 8S packaging option only if doing so does not materially degrade the 6S aircraft.

### 3.3 Battery-adjustment rule

The bay model shall keep four dimensions separate:

1. measured pack rigid envelope;
2. connector, lead and safe bend swept volume;
3. installation/removal clearance; and
4. **at least 20 mm total CG-adjustment travel**.

None may be counted twice or hidden inside wall tolerance. Nominal CG should lie near the
middle of the adjustment range. A solution with only forward or only aft reserve fails
unless measured uncertainty proves the missing direction unnecessary.

---

## 4. The core design method: mass skeleton and wing first, fuselage last

The successful idea already present in the repository becomes a formal rule:

> Create a three-dimensional equipment and mass skeleton, iterate it with the wing and
> balance solution, and only then model the fuselage around the converged system.

The wing cannot be designed independently because its neutral point sets the allowable
CG. The electronics cannot be placed independently because their envelopes and moments
set nose length and inertia. Therefore “electronics first” means **early, explicit and
parametric**, not frozen in isolation.

```mermaid
flowchart LR
    Mission[Mission and acceptance] --> Hardware[Measured hardware envelopes]
    Hardware --> Skeleton[3-D mass and equipment skeleton]
    Mission --> Candidates[Equal-requirements wing candidates]
    Skeleton <--> Candidates
    Candidates --> Coupled[Trim, stability, control, structure and propulsion closure]
    Coupled --> OML[Fuselage OML around the converged skeleton]
    OML --> Handoff[Human CAD handoff]
    Handoff --> Ground[Printed evidence and ground qualification]
    Ground --> Flight[Instrumented flight and redesign]
```

### 4.1 Required mass-skeleton contents

Every item shall have:

- product/configuration identity;
- measured or sourced `L×W×H` envelope and a declared coordinate mapping;
- mass, mass-centre location and uncertainty;
- fixed, movable or alternate-configuration status;
- connector, cable, cooling, antenna, optical and service keep-outs;
- power source, voltage, continuous/peak current and heat rejection;
- structural attachment and load introduction; and
- configuration membership: 6S, 8S, R, CLEAN or common.

The initial placement order is:

1. forward optical camera and its true field of view;
2. propeller disk, motor, mount, hand/ground hazards and pusher inflow;
3. wing reference, neutral-point range and control surfaces;
4. servos and direct low-free-play linkages;
5. battery rail solved for CG and required travel;
6. FC/IMU near the dynamic centre with service access;
7. ESC, PDB and high-current path;
8. pitot, GPS/magnetometer, receiver and antennas in clean measurement/RF locations;
9. cooled VTX within real coax routing; and
10. optional rudder module and servo.

Dead ballast is not a baseline design variable. If the system balances only with ballast,
the component placement, planform or architecture returns to the trade.

### 4.2 Fuselage rule

The body OML begins only after a candidate closes packaging and balance without collision.
It shall be generated around **inflated installation envelopes**, then traded for:

- complete-aircraft drag, not isolated frontal area;
- wetted area and pressure-recovery gradients;
- forward side-area/yaw penalty;
- body-inclusive neutral point and trim;
- camera FOV, cooling, access and antenna function;
- root-junction flow on the selected sweep;
- pusher-plane inflow uniformity;
- structural load paths, mass, stiffness and print segmentation; and
- landing/handling damage tolerance.

The preferred body is the shortest/lightest Pareto solution that closes these functions.
A longer nose is accepted only when its CG or packaging benefit exceeds its drag, yaw,
inertia, mass and compliance penalties.

### 4.3 SVG review loop

Generated SVG sheets remain the fastest design-review interface before native CAD. Each
selected candidate shall provide, from common Python data:

1. equipment mass skeleton with CG/NP uncertainty and battery travel;
2. equal-scale architecture comparison planforms;
3. general arrangement in plan and side views;
4. battery-bay sections and extraction/connector sweep;
5. wing stations, controls, joins and structural reference lines;
6. propulsion disk, motor and hazard/clearance sheet;
7. R versus CLEAN directional-module comparison; and
8. final CAD-interface and tolerance sheet.

SVG is review authority, not manufacturing authority. No geometry may be traced from an
illustration when a numerical owner exists.

---

## 5. Dependency-gated design programme

The programme is ordered by information dependency, not calendar duration. Parallel work
is allowed only when every branch uses the same controlled configuration.

### M0 — mission, scoring and configuration contract

**Purpose:** convert the intent in §1 into falsifiable requirements before another shape is
optimized.

**Status:** complete on 21 August 2026.

Completed work:

1. defined launch/approach states, candidate-best-range, 65/80 km/h reporting states and
   the 95 km/h historical comparator;
2. selected total battery-terminal `Wh/km` and Pareto comparison without an unsupported
   scalar weighting or range/endurance target;
3. defined standard comparison conditions and the measurements required in actual weather;
4. defined handling through passive stability, trim/control reserve, bank response,
   actuator behavior and recovery, without inventing a roll-rate requirement;
5. defined 6S-R, 6S-CLEAN and 8S-STUDY roles and the flight-test order;
6. separated hard requirements, provisional screens and historical comparators; and
7. reissued `docs/00`, added ADR-0048 and created an executable mission contract.

**Exit evidence:** [Revision-2 requirements](00-objectives-and-requirements.md),
[ADR-0048](../decisions/ADR-0048-article-1-mission-and-configurations.md) and
[`mission_contract.py`](../calculations/mission_contract.py), verified by the calculation
harness. No final span, sweep, airfoil or motor was selected at this gate.

### M1 — bought-in hardware and measurement chain

**Purpose:** turn catalog rectangles and estimated masses into design inputs.

Required work:

1. procure or create hard dummies for the 6S pack, 8S study pack, FC/PDB, O4, two elevon
   servos, candidate rudder servo, GPS, pitot, receiver, ESC and motor classes;
2. measure mass, true body/lug dimensions, mass centre, connectors and cable sweeps;
3. bench the FC resources, pitot, current sensor, blackbox and synchronized logging;
4. bench servo deadband, stiffness, rate, current and temperature at the intended rail;
5. create an electrical single-line diagram and continuous/peak power budget; and
6. validate the measurement/reduction chain on an aircraft that already flies where
   practical.

**Exit evidence:** versioned equipment catalog, measured-envelope library, verified power
tree and usable pitot/current/blackbox data. Catalog data alone do not pass M1.

### M2 — mass skeleton, battery rail and packaging architectures

**Purpose:** establish the physical aircraft before drawing a body.

Required work:

1. build common 6S-R, 6S-CLEAN and 8S study component ledgers;
2. solve x/y/z positions and inertia with uncertainty, not only aggregate longitudinal CG;
3. compare at least flat-narrow and flat-moderate one-layer battery corridors;
4. prove ≥20 mm total battery travel, retention, extraction and connector safety;
5. reserve only justified alternate-component growth and the R rudder-servo envelope;
6. define camera/FOV, antenna, cooling, pressure-line and high-current keep-outs; and
7. generate the mass-skeleton and battery-bay SVG sheets.

**Exit evidence:** collision-free parametric skeletons with reachable CG intervals for the
candidate wing-neutral-point range, no baseline ballast and no hidden service volume.

### M3 — equal-requirements aircraft architecture trade

**Purpose:** decide whether forward sweep earns its penalties.

At minimum compare:

- **A — current forward-swept family**, including the v0.6 baseline;
- **B — straight/near-zero-sweep tailless plank family**; and
- **C — aft-swept tailless family**.

Each family may optimize span, area, taper, airfoil distribution, twist, elevon geometry
and body integration within the same M0 constraints. Comparing one optimized concept with
two deliberately frozen concepts is prohibited.

Every candidate reports:

- total estimated `Wh/km` at every mission state and the uncertainty drivers;
- trim drag, control reserve and local stall/lost-lift sequence;
- static and dynamic longitudinal/lateral-directional behavior;
- R and CLEAN feasibility;
- mass, CG reach, inertia and nose/body consequences;
- strength, stiffness, divergence and flutter risk proxies;
- printed wall depth, joints, segmentation and manufacturing risk;
- pusher installation and camera compatibility; and
- sensitivity to roughness, material properties and component substitution.

Use Pareto ranking. Aesthetics may break a genuine near-tie; they may not override a P0
failure or a material efficiency/structure penalty.

**Exit evidence:** an ADR selecting one family and preserving at least one credible backup,
with all candidates evaluated by the same scripts and inputs.

### M4 — section, twist and printed aerodynamic evidence

**Purpose:** create the real operating airfoil, not only a smooth DAT file.

Required work:

1. define one parametric airfoil master with finite printable trailing edge, hinge and
   declared swept-section plane;
2. generate root, control-region and tip sections for the selected planform;
3. run transition/roughness-bracketed XFOIL screening through negative lift, cruise,
   high lift and required physical elevon states;
4. run the three-dimensional solver with local viscous data at every mission state;
5. print representative sections using the intended printer/material/orientation;
6. measure contour, roughness, twist, gaps and trailing edge; and
7. execute E2A `CL/CD/Cm` tests to calibrate moment, drag and stall separately.

**Exit evidence:** a versioned geometry/polar/test manifest whose measured printed-section
evidence closes the required trim and stall domain. XFOIL convergence is not the gate.

### M5 — integrated aerodynamics, stability and control

**Purpose:** close the complete aircraft rather than independent subsystems.

Required work:

1. couple body, propulsor state, R/CLEAN surfaces, local polars and elastic state to the
   three-dimensional aircraft;
2. solve trim over speed, mass, complete CG travel, roughness and power states;
3. retain simultaneous pitch and differential-roll authority without saturation;
4. calculate control hinge moment, rate, stiffness and power requirements using the real
   selected geometry;
5. quantify longitudinal modes, yaw/roll modes, finite-yaw launch/recovery and adverse
   corners;
6. size the passive vertical area first, then the rudder area/servo only for a declared
   control task; and
7. freeze planform, controls, nominal CG band and R/CLEAN aerodynamic interfaces.

**Exit evidence:** every approved state trims, remains controllable and meets the M0
stability/handling criteria with uncertainty. A positive static margin alone does not pass.

### M6 — loads, printed structure and aeroelastic closure

**Purpose:** prove that the printable aircraft can carry the aerodynamic design.

Required work:

1. define complete positive/negative manoeuvre, dynamic-gust, control, propulsion,
   landing/handling and proof cases;
2. manufacture material, adhesive, hinge, joint and representative-section coupons with
   the production process;
3. measure orthotropic properties, creep/environment effects, `EI`, `GJ`, coupling,
   buckling, joint stiffness, free play and hysteresis;
4. size skins, cells, spars, sockets, bonds, hard points, motor mount and R module from
   net loads including mass relief;
5. correlate analytical/FE models to coupons and representative structures;
6. evaluate divergence and coupled flutter across material, joint, mass, servo and
   temperature uncertainty; and
7. freeze segmentation, wall schedule, materials and structural interfaces.

**Exit evidence:** positive structural margins, correlated stiffness and a justified
ground/initial-flight speed envelope. Component frequency separation alone is not flutter
clearance.

### M7 — final equipment freeze, body OML and human CAD handoff

**Purpose:** convert the closed system into an unambiguous CAD brief.

Required work:

1. select and measure the released 6S motor, ESC, servos, FC/PDB, sensors and FPV batch;
2. rerun propulsion, power, mass, CG, inertia, thermal and structural models with those
   exact parts;
3. generate and select a body-OML Pareto set around the converged mass skeleton;
4. close wing-body junction, pusher inflow, camera, antenna, cooling, access, grip,
   landing and print requirements;
5. publish the new concise Design Guide and parameter/configuration manifests;
6. issue the complete SVG review set; and
7. conduct the formal human-CAD kickoff and question review.

**Exit evidence:** the handoff package in §7 exists, contains no silent designer decisions
and has no unresolved geometry that controls safety, fit or aerodynamic shape.

### M8 — native CAD, production evidence and ground qualification

**Purpose:** prove that the human CAD implementation represents the selected aircraft.

Required work:

1. review native parameters, interfaces, STEP data, meshes and round-trip geometry error;
2. run interference, mass-properties, tolerance and assembly/service reviews;
3. print production-equivalent sections, joints, panels, CORE and R module;
4. measure as-built geometry, part masses, full CG and inertia;
5. conduct proof loads, control free-play/stiffness tests, propeller clearance, thermal
   tests and complete-aircraft ground vibration testing;
6. verify FC sensor signs, servo outputs, control balance, power failsafes and configuration
   hashes; and
7. issue a signed first-flight readiness review.

**Exit evidence:** one conforming SALAMANDRA-6S-R article inside the approved mass, CG,
geometry, structural, modal, thermal and software configuration. “It printed” is not an
exit criterion.

### M9 — first flight, identification and optimization loop

**Purpose:** turn predictions into aircraft-specific evidence.

The sequence is conservative and configuration-controlled:

1. restrained power and taxi/launch rehearsals;
2. first stabilized SALAMANDRA-6S-R flight inside the ground-cleared envelope;
3. low-amplitude longitudinal and lateral system identification;
4. stall/approach and launch/landing characterization;
5. motor-off glide polar and propulsion/energy measurements;
6. R tests with rudder neutral/active, followed by CLEAN only after review;
7. incremental envelope expansion with inspection and modal correlation; and
8. measured redesign of the largest `Wh/km`, handling or durability contributors.

**Exit evidence:** repeatable flight data with uncertainty, a correlated model and either
measured compliance or a quantified return to the responsible upstream gate.

---

## 6. Tool and evidence contract

| Need | Primary tool | Required independent or physical check |
|---|---|---|
| Shared inputs/configurations | Python dataclasses/manifests | Contract lint, hashes and cross-module verification |
| Trades, mass, CG, inertia and power | Python 3.11 + NumPy | CAD mass properties and physical weighing/balance |
| Local viscous aerodynamics | XFOIL 6.99/7.00 screening | Printed-section E2A data; separate drag/moment/stall calibration |
| Three-dimensional lift/NP | In-house VLM | Weissinger-L plus body-inclusive/higher-fidelity sensitivity and flight ID |
| Propulsion | UIUC/APC data + Python matching | Motor/ESC/propeller bench map and flight equilibrium |
| Loads and structure | Python load owner + analytical/FE model | Production-process coupons, representative sections and proof tests |
| Aeroelasticity | Correlated structural/aerodynamic model | Static test, GVT and conservative flight correlation |
| Geometry review | Generated metric SVG | Numerical manifest and native CAD; never trace artwork |
| Manufacturing definition | Human parametric CAD | STEP/mesh round trip, inspection and measured as-built geometry |
| Mission validation | Pitot + current + voltage + blackbox | Repeated runs, calibration and uncertainty report |

Rules learned from Peter Wick's *Designing Flying Wings* and the repository audit are
binding throughout:

1. optimize the aircraft task, not an isolated section or solver score;
2. treat planform, airfoil, twist, trim, CG, controls, structure and yaw as one system;
3. include the manufactured, deflected control contour in the effective airfoil;
4. treat static and dynamic stability as separate gates;
5. evaluate span loading and stall as state-dependent controllability problems;
6. distinguish strength, stiffness, free play and aeroelastic stability;
7. carry geometry, transition, material and component uncertainty through decisions;
8. preserve Pareto alternatives and state why candidates lose; and
9. calibrate theory with progressively representative physical articles before release.

Passing a software test proves reproducibility and internal consistency. It does not turn
an estimate into a physical measurement.

---

## 7. Required CAD handoff package

The human CAD designer receives one controlled package, not the whole repository with an
instruction to infer the aircraft. It shall contain:

1. approved mission, configuration and acceptance manifest;
2. selected architecture ADR and backup-candidate disposition;
3. canonical parameter table with units, status, tolerance and numerical owner;
4. hashed airfoil/station/control geometry and section-plane convention;
5. measured equipment models, keep-outs, mass centres and cable/service envelopes;
6. complete mass, CG, inertia and battery-travel ledger for R and CLEAN;
7. structural load cases, materials/process rules and explicit load paths;
8. joint, spar, hinge, servo, motor, landing and directional-module interfaces;
9. generated SVG review sheets and scale/authority legend;
10. print segmentation, orientation, wall and tolerance requirements;
11. required native assembly/component tree and named-parameter schema;
12. CAD review checklist, deviation register and stop-work questions; and
13. statement of which dimensions are fixed, provisional, designer-owned or excluded.

The CAD designer may shape genuinely designer-owned fairings inside their envelopes. They
may not choose an airfoil, move a mass, enlarge a bay, change a joint, reinterpret sweep,
add ballast or resolve a collision silently.

---

## 8. Configuration and change control

Every aircraft artifact shall identify at least:

```text
airframe geometry + airfoil/controls + R/CLEAN state + pack + motor + propeller + ESC
+ avionics/FPV + material/process + mass/CG + software/parameters
```

Change routing:

| Change | Minimum reopened work |
|---|---|
| Part fits inside released envelope and mass/power bounds | Equipment ledger, collision and CG check |
| Servo class, control geometry or linkage changes | M1 servo bench + M5 control + M6 aeroelastic checks |
| 6S ↔ 8S | M1 electrical bench, M2 packaging/CG/inertia, M3/M5 performance and M6 loads |
| Motor, propeller or propeller station changes | Propulsion map, CG, clearance, loads, vibration and pusher-inflow checks |
| Sweep, span, area, taper, airfoil or twist changes | Return to M3; all downstream aero/structure/CAD evidence invalidated |
| Body OML, nose length or equipment station changes | M2 balance, M5 body stability/trim, drag/yaw/inertia and M6 structure |
| R/CLEAN directional hardware changes | M2 mass, M5 finite-yaw/control, M6 structure/flutter and M9 test identity |
| Material, printer, orientation, wall or adhesive changes | M6 process allowables and representative tests |

No document may call a configuration “released” merely because its Python calculations
pass. Release binds the exact physical configuration and its evidence.

---

## 9. Physical article ladder

Do not make the first complete aircraft carry every unknown.

| Article | Purpose | Consumed by |
|---|---|---|
| Equipment and pack dummies | Envelope, service, cable and balance discovery | M1/M2 |
| Material/joint/hinge coupons | Process allowables and failure modes | M4/M6 |
| Printed root/mid/tip sections | Real contour and `CL/CD/Cm` | M4 |
| Representative wing boxes and removable joint | `EI`, `GJ`, coupling, strength, creep and free play | M6 |
| Propulsion bench rig | Motor/ESC/propeller efficiency, rpm, heat and vibration | M1/M5 |
| Systems “iron bird” | Complete power, FC, servo, pitot, logging and failsafe chain | M1/M8 |
| Production semispan/CORE/R module | Proof, assembly, access and modal correlation | M8 |
| SALAMANDRA-6S-R Article #1 | Safe first flight and system identification | M9 |
| SALAMANDRA-6S-CLEAN conversion | Controlled directional/efficiency A/B test | M9 |

---

## 10. Definition of the first functional prototype

The first functional prototype is:

- the selected tailless architecture, not automatically the current −15° planform;
- a 6S1P P42A-class, single-pusher, front-camera SALAMANDRA-6S-R article;
- predominantly PETG and printed with the released process;
- built from the human native-CAD handoff and conforming to its configuration manifest;
- fitted with pitot, calibrated current/voltage measurement, blackbox, GPS, receiver and
  the complete FPV system;
- physically weighed and balanced with ≥20 mm total usable battery travel;
- ground-proofed, stiffness/modal checked, and released only inside a justified initial
  envelope; and
- capable of producing valid data for the R/CLEAN, glide-polar and energy experiments.

It is not required to demonstrate 8S, maximum range, a full roll or the final efficiency
optimum. Its job is to fly safely, measure honestly and expose the next highest-value
redesign.

---

## 11. Immediate work order

Work shall proceed in this order:

1. **MP-01 — Reissue objectives — COMPLETE.** Revision 2 removes the arbitrary
   range/endurance requirements, defines the M0 mission/handling matrix and is enforced by
   `mission_contract.py` plus ADR-0048.
2. **MP-02 — Decision reset ledger — NEXT.** Mark every active ADR as retained, candidate-only,
   reopened or superseded for the redesign.
3. **MP-03 — Hardware manifest.** Create one machine-readable 6S/R/CLEAN equipment and
   power manifest, with an 8S study overlay.
4. **MP-04 — Measure hardware.** Procure or mock the packs, O4, FC, servos, motor/ESC,
   sensors and connectors; replace catalog-only installation estimates.
5. **MP-05 — Instrument first.** Complete the pitot/current/blackbox iron bird and test
   the reduction chain on an existing aircraft.
6. **MP-06 — Rebuild the mass skeleton.** Solve measured 6S/R/CLEAN placement, 20 mm
   battery travel, FOV, cooling, RF and service volumes with no OML.
7. **MP-07 — Execute the three-family architecture trade.** Extend the current Python
   trade so forward, straight and aft sweep receive equal optimization freedom and the
   same requirements.
8. **MP-08 — Select the planform family.** Issue the architecture ADR and preserve the
   runner-up.
9. **MP-09 — Close printed aerodynamics.** Create the selected parametric sections and
   run E2A before authorizing the flight-wing loft.
10. **MP-10 — Close aircraft controls/stability/structure.** Complete M5/M6, including the
    R rudder experiment, printed stiffness and ground aeroelastic gates.
11. **MP-11 — Shape the fuselage.** Generate the OML around the converged skeleton and
    select it on complete-aircraft evidence.
12. **MP-12 — Issue the CAD package.** Publish the new Design Guide/SVG set and start the
    controlled human CAD build.

The next engineering task is **MP-02**, followed by the M1 hardware manifest and
measurement chain—not another refinement of the current wing loft or fuselage OML.

---

## 12. Current status at the reset

| Gate | Status | Existing useful evidence | Principal missing evidence |
|---|---|---|---|
| **M0** | **Closed** | Revision-2 specification, ADR-0048 and executable mission contract | No M0 evidence missing; changes require controlled reopen |
| **M1** | **Open — next design gate** | I-16/I-17/I-18/I-19/I-32 catalogs and power models | Versioned candidate manifest, procured-part measurements and integrated iron bird |
| **M2** | Partial, to rebuild | Equipment ledger, balance solvers, SLM-EQP-001, I-31/I-32 | Unified measured 6S/R/CLEAN skeleton and 20 mm travel proof |
| **M3** | Open | Current forward-sweep trade and v0.6 candidate A | Equal-requirements straight and aft-swept optimized candidates |
| **M4** | Blocked by M3 | r1/r2a calculations and E2A plan | Selected printed sections and measured `CL/CD/Cm` |
| **M5** | Blocked | VLM/Weissinger, trim, elevon and yaw screens | Full selected-aircraft nonlinear/dynamic closure |
| **M6** | Blocked | Load, divergence and preliminary material/structure models | Process allowables, representative structures and correlated aeroelastic model |
| **M7** | Blocked | Provisional OML generator and current Design Guide | Final hardware, selected OML and new controlled CAD handoff |
| **M8** | Blocked | SVG workflow and test definitions | Native CAD and production-equivalent physical evidence |
| **M9** | Blocked | Instrumented flight-test methods | Conforming first article and readiness release |

---

## 13. Governing evidence

- [Consolidated NF Design Guide audit](../design/NF-Design-Guide-2024-Consolidated-Audit-and-Release-Programme.md)
  — application of Peter Wick's *Designing Flying Wings* and the full physical gate model.
- [NF design-method synthesis](../design/NF-Design-Guide-2024-Repository-Audit-Part-06-Design-Method-Synthesis.md)
  — the D0→D8 coupled method integrated here.
- [6S/8S P42A trade](../research/I-32-6s-8s-p42a-pack-and-aircraft-trade.md) and
  [flat-bay/fuselage-length trade](../research/I-31-flat-dual-pack-bay-and-fuselage-length-trade.md).
- [Flight-controller](../research/I-17-inav-flight-controllers.md),
  [servo](../research/I-18-servo-catalog.md),
  [FPV](../research/I-19-fpv-system-dji-o4.md) and
  [propulsion](../research/I-03-propulsion-chain.md) research.
- [Current concise Design Guide](../design/Salamandra-Design-Guide-v0.1.md) — historical
  v0.6 CAD baseline under hold, not the redesigned-aircraft release.
- [Experimental programme](../tests/README.md) and [gap register](../gaps/README.md).
- Current manufacturer verification: [Molicel P42A](https://www.molicel.com/product/inr-21700-p42a/),
  [SpeedyBee F405 WING](https://www.speedybee.com/speedybee-f405-wing-app-fixed-wing-flight-controller/),
  [DJI O4 Air Unit](https://www.dji.com/o4-air-unit/specs),
  [APC performance data](https://www.apcprop.com/performance-data-new/) and
  [INAV releases](https://github.com/iNavFlight/inav/releases).

---

## 14. Exit from the programme reset

The programme reset is complete only when:

- M0 requirements are approved and `docs/00` is reissued;
- the working hardware baseline is physically credible;
- the current forward-swept aircraft has competed fairly against the two alternative
  tailless families;
- one architecture is selected with explicit reasons and a backup retained; and
- every downstream document clearly distinguishes historical v0.6 data from the newly
  selected configuration.

Until then, research, coupons, test fixtures, electronics integration, mass-skeleton work
and reversible parametric tools are authorized. Production wing/body CAD and manufacture
are not.
