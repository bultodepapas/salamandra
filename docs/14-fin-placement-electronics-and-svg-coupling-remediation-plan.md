# Fin Placement, Electronics Skeleton, and SVG Coupling Remediation Plan

**Document type:** engineering remediation and implementation plan  
**Status:** planning baseline; no geometry or manufacturing authority  
**Applies to:** SALAMANDRA-CLEAN and the provisional V1 fixed-fin variant  
**Primary outputs affected:** `SLM-GA-002`, `SLM-FIN-001`, `SLM-EQP-001`  
**Date:** 19 August 2026  

> This document deliberately does not select a final fin position or planform.
> It defines the evidence, calculations, data architecture, trades, drawing views,
> checks, and acceptance gates required before that selection can be made.

---

## 1. Executive decision

The current fixed-fin installation shall not be treated as aerodynamically,
structurally, or geometrically released.

The present `x_AC = +285 mm` station is an engineering estimate used as an input to
the directional-stability sizing calculation. It is not the result of a constrained
placement optimisation. The generated side elevation then projects two laterally
separated fins onto the aircraft centre plane, making the fins appear to intersect the
propeller. The nominal three-dimensional model gives radial separation, but the drawing
does not prove it, and the current root-fairing graphic extends forward beyond the
credited aerodynamic planform without participating in the clearance calculation.

The remediation shall therefore proceed in this order:

1. establish one authoritative three-dimensional aircraft scene derived from Python;
2. place the complete electronics and propulsion skeleton in that scene;
3. calculate the complete propeller swept-volume exclusion envelope;
4. compare multiple directional-stability architectures and fin stations;
5. select geometry using aerodynamic, mass, balance, structural, propulsion, printing,
   inspection, and safety criteria;
6. generate the side, top, rear, and local-detail views from the selected scene;
7. validate both the numerical model and the rendered SVGs before publication.

Moving the existing fin aft by an arbitrary axial distance is explicitly not an
approved correction. Longitudinal overlap with a propeller plane is not inherently an
interference when the parts are separated laterally or vertically; the correct test is
minimum three-dimensional distance to the complete swept-volume envelope under
worst-case tolerances and deflections.

---

## 2. Problem statement

### 2.1 Observed drawing failure

The current side elevation creates the following visual and engineering problems:

- the propeller plane crosses the projected fin-root chord;
- both fins collapse onto one silhouette because the lateral coordinate is hidden;
- the drawing does not show a rear view proving radial clearance;
- the complete electronics skeleton is absent from the same view;
- the viewer cannot see what physical structure supports the fin;
- the root fairing appears to project into the propeller region;
- provisional installation geometry is visually similar to calculated geometry;
- a reader can reasonably conclude that the propeller will strike the fin;
- the drawing communicates more certainty than the underlying installation possesses.

This is unacceptable for an engineering-review sheet. A technically valid hidden
coordinate is not sufficient if the drawing chosen to communicate the installation
conceals that coordinate.

### 2.2 Model-design problem

The location problem is deeper than graphic presentation. The aerodynamic-centre
station was declared before the full installation trade was performed. The existing
calculation then sizes total fin area around that station. Consequently, the root and
tip coordinates are outputs of a planform construction around a preselected AC rather
than outputs of a placement optimisation.

The model currently answers:

> Given a fin AC at `x = +285 mm`, how much total projected fin area is required for the
> nominal directional-stability target?

It does not yet answer:

> Which fin architecture, position, planform, and support arrangement gives the best
> robust aircraft-level solution while remaining clear of the propeller, balanceable,
> printable, structurally adequate, and visually inspectable?

The second question is the governing design question.

### 2.3 Digital-thread problem

The current drawing generator already reads some equipment positions from
`equipment_layout.py`, but the connection is incomplete. Some equipment is drawn from
the common component layout, other installation geometry is constructed locally inside
the SVG generator, and the complete aircraft scene is not represented by a single
intermediate object.

That architecture permits three classes of inconsistency:

1. a component moves numerically but remains absent from one or more views;
2. a local drawing literal duplicates or contradicts a canonical model value;
3. a graphical fairing or support exists without entering collision, mass, or structural
   calculations.

The remediation must eliminate these classes rather than patch the appearance of one
SVG.

---

## 3. Terminology and configuration control

### 3.1 Required terminology

The following terms shall be used consistently:

- **Fixed fin:** a non-moving vertical stabilising surface.
- **Rudder:** a movable yaw-control surface, normally hinged to a fixed fin.
- **Drag rudder:** a split or differential drag device used to produce yawing moment.
- **V1a:** the current provisional twin-fixed-fin configuration; no movable rudder.
- **CLEAN:** the finless baseline.
- **Propeller plane:** the nominal plane traced by an undeformed propeller at the
  declared shaft station.
- **Swept-volume envelope:** the three-dimensional volume occupied by the propeller plus
  defined dynamic, manufacturing, and installation allowances.
- **Near/far fin:** drawing-only identifiers for the two laterally separated fins in a
  projected view; they do not define different hardware.
- **Electronic skeleton:** the positioned, oriented component-envelope and mass-centre
  model used for packaging, balance, inertia, collision, and drawing generation.

The current V1a part is therefore a fixed fin, not a rudder. If a movable rudder is later
selected, it becomes a new controlled geometry, mass, actuation, hinge, and authority
problem.

### 3.2 Authority tags

Every relevant value and graphic shall retain one of the project authority tags:

- `[M]`: measured;
- `[D]`: directly declared or externally controlled;
- `[E]`: engineering estimate or calculation;
- `[I]`: inferred or provisional implementation geometry.

An inferred root fairing may be shown, but it shall not be allowed to bypass collision,
mass, or geometry checks merely because it carries `[I]` authority.

### 3.3 Planning freeze

Until this plan reaches the architecture-selection gate:

- `x_AC = +285 mm` remains a study datum, not a released placement;
- the current fin area remains a study result tied to that datum;
- the current boom arrangement remains provisional;
- no axial propeller-to-fin clearance shall be declared as a new requirement;
- no SVG silhouette shall be used as manufacturing authority;
- no aerodynamic benefit shall be inferred from visual shape alone.

---

## 4. Current numerical baseline and audit findings

The following values describe the current model and are included so that the remediation
starts from a reproducible baseline rather than from the screenshot alone.

| Quantity | Current value | Status | Interpretation |
|---|---:|---|---|
| Wing reference area, `S` | 0.282 m² | `[D]` | Aircraft aerodynamic reference |
| Wing reference span, `b` | 1.300 m | `[D]` | Aircraft aerodynamic reference |
| Target CG station | −93.784 mm | `[D]/[E]` | Current solved target relative to root c/4 |
| Fin count | 2 | `[I]` | Provisional V1a architecture |
| Fin lateral stations | ±140.0 mm | `[I]` | Centre of each aft support/fin |
| Boom width | 18.0 mm | `[I]` | Plan-view installation envelope |
| Propeller diameter | 203.2 mm | `[D]` | Eight-inch propeller |
| Propeller radius | 101.6 mm | `[D]` | Nominal undeformed radius |
| Nominal inner boom-to-disk clearance | 29.4 mm | `[E]` | `140 − 9 − 101.6`; static geometry only |
| Assumed fin AC station | +285.0 mm | `[E]` | Input, not placement optimum |
| CG-to-fin-AC arm | 378.784 mm | `[E]` | `285 − (−93.784)` |
| Total calculated fin area | 0.034404 m² | `[E]` | 3.4404 dm² for the nominal target |
| Area of each fin | 0.017202 m² | `[E]` | Half of total area |
| Per-fin aspect ratio | 2.0 | `[E]` | Current low-Re planform assumption |
| Taper ratio | 0.30 | `[E]` | Current planform assumption |
| Per-fin span | 185.484 mm | `[E]` | Derived from area and aspect ratio |
| Root chord | 142.680 mm | `[E]` | Derived trapezoid |
| Tip chord | 42.804 mm | `[E]` | Derived trapezoid |
| Root leading-edge station | +218.599 mm | `[E]` | Derived around the assumed AC |
| Root trailing-edge station | +361.279 mm | `[E]` | Vertical trailing-edge construction |
| Vertical-tail volume coefficient | 0.03555 | `[E]` | Screening value, not validation |
| Current independent-corner `Cn_beta` band | −0.000290 to +0.001192 /deg | `[E]` | Lower corner remains directionally unstable |

### 4.1 What the nominal clearance does prove

For an ideal centred propeller and an undeformed rectangular boom envelope, the current
inner lateral boom edge is:

\[
y_{inner}=140.0-\frac{18.0}{2}=131.0\ \text{mm}
\]

The nominal lateral separation beyond the propeller radius is:

\[
C_{nominal}=131.0-101.6=29.4\ \text{mm}
\]

This proves that the idealised boom rectangle does not intersect the idealised circular
disk in plan/rear projection.

### 4.2 What the nominal clearance does not prove

The `29.4 mm` result does not include:

- propeller blade coning, bending, torsion, or manufacturing variation;
- shaft runout;
- motor-mount angular or translational error;
- boom bending and torsion under fin, landing, handling, or vibration loads;
- printed saddle tolerance and creep;
- lateral offset of the motor axis;
- fasteners, wire loops, guards, fillets, or local fairings;
- transient displacement following a hard landing or propeller imbalance;
- maintenance and assembly errors;
- the axial thickness of the hazardous rotating region.

It is therefore a geometric observation, not a released safety margin.

### 4.3 Why an aft fin can be beneficial

The current analytical screening uses the vertical-fin contribution:

\[
C_{n_\beta,v}=\eta_v
\left(1+\frac{d\sigma}{d\beta}\right)
a_v\frac{S_v}{S}\frac{l_v}{b}
\]

For a fixed target and unchanged aerodynamic assumptions:

\[
S_v\propto\frac{1}{l_v}
\]

A longer arm can therefore reduce required area. The simplified fin yaw-damping term is:

\[
C_{n_r,v}=-2\eta_v a_v\frac{S_v}{S}
\left(\frac{l_v}{b}\right)^2
\]

If area is resized to maintain a fixed static target, damping magnitude increases
approximately with arm. These are legitimate benefits, but they do not make the most-aft
possible station optimal because the aircraft-level penalties can grow simultaneously.

### 4.4 Penalties that must be coupled to the aerodynamic benefit

The placement study shall calculate, not merely discuss:

- added boom length and mass;
- aft movement of installed mass and resulting CG shift;
- battery displacement needed to recover the CG;
- boom bending stress and displacement;
- boom torsional displacement at the fin root;
- fin root bending moment;
- structural natural frequencies;
- exposed wetted area and interference drag;
- power-on wake or slipstream sensitivity;
- inspection and assembly accessibility;
- transport and landing vulnerability;
- printer build-envelope and segmentation implications.

---

## 5. Objectives, non-objectives, and success definition

### 5.1 Objectives

The work shall:

1. determine whether any fin is required for the intended V1 test mission;
2. determine the appropriate fixed-fin or yaw-control architecture;
3. select fin placement using coupled numerical evidence;
4. prove propeller separation in three dimensions;
5. display the complete electronic and propulsion skeleton in the side view;
6. make every relevant SVG coordinate a projection of Python-owned geometry;
7. ensure a changed component position propagates to balance, inertia, clearance,
   annotations, and every relevant drawing;
8. prevent unmodelled fairings or supports from appearing as apparently released parts;
9. preserve explicit uncertainty and open-gate reporting;
10. provide reproducible acceptance tests for future changes.

### 5.2 Non-objectives

This plan does not itself:

- release a final fin;
- select a `20 mm` axial separation rule;
- assume that longitudinal overlap with the propeller plane is prohibited;
- define a movable rudder;
- approve a printable saddle or boom joint;
- replace wind-tunnel or flight-test validation;
- convert an inferred fuselage OML into manufacturing geometry;
- claim that a visually aerodynamic silhouette is aerodynamically adequate.

### 5.3 Definition of success

The remediation is successful only when:

- one Python scene reproduces all relevant orthographic views;
- the complete electronic skeleton is visible and traceable;
- all propeller clearances are calculated from three-dimensional envelopes;
- the selected architecture wins a documented trade against credible alternatives;
- stability closes at the defined uncertainty level, not only nominally;
- mass and CG close without undisclosed ballast or impossible battery placement;
- structural screening closes for the declared load cases;
- SVG content and annotations agree numerically with the calculation outputs;
- rendered sheets communicate the installation without requiring hidden assumptions;
- all automated and visual review gates pass.

---

## 6. Governing design questions

The investigation shall answer the following questions explicitly.

### 6.1 Need and authority

1. What directional-stability and damping behaviour is required for Article #1 testing?
2. Is a fixed fin required, or can the CLEAN configuration meet the mission with control
   augmentation?
3. Is active yaw authority required, or is passive stability sufficient?
4. What minimum lower-bound `Cn_beta` and `Cn_r` are defensible for this aircraft?
5. Which requirements are analytical screening limits and which require flight data?

### 6.2 Placement

1. Should the surfaces overlap the propeller station longitudinally while remaining
   outside the disk radially?
2. Should they be entirely forward of the propeller plane?
3. Should they be entirely aft of the hazardous swept-volume slab?
4. Should they move farther outboard onto the wing?
5. Is the current `y = +/-140 mm` driven by structure, aerodynamics, or drawing
   convenience?
6. Does local wing/fuselage sidewash invalidate a free-stream effectiveness assumption?
7. Does power-on flow increase useful dynamic pressure, introduce unsteady loading, or
   create unacceptable vibration?

### 6.3 Geometry

1. What area is needed at each candidate station?
2. What aspect ratio, taper, sweep, and leading-edge radius are suitable at the relevant
   Reynolds number?
3. Is a vertical trailing edge advantageous for printing and packaging, or an artificial
   restriction?
4. Does a dorsal root fillet improve structural load transfer or merely add uncredited
   area and ambiguity?
5. Can the support be integrated into the wing or CORE structure more efficiently than
   by extending separate booms?

### 6.4 Aircraft coupling

1. How does each option change empty mass, CG, inertia, and battery station?
2. Does the required battery movement remain inside the physical battery bay?
3. Does the option increase yaw damping while degrading pitch inertia or longitudinal
   balance?
4. How much drag and energy-use penalty is introduced at cruise?
5. Does the installation obstruct cooling, wiring, antennas, camera field of view, motor
   access, or propeller replacement?

---

## 7. Evidence and research programme

### 7.1 Evidence hierarchy

Research shall be ranked in this order:

1. applicable regulations, standards, and manufacturer limits;
2. NASA, NACA, FAA, EASA, military, or university primary technical reports;
3. wind-tunnel and flight-test papers with disclosed geometry and conditions;
4. manufacturer drawings, manuals, and measured propeller data;
5. validated aerodynamic texts and methods;
6. comparable aircraft used only as configuration evidence;
7. informal build reports used only to identify failure modes.

No configuration shall be selected because it resembles a successful aircraft unless
the relevant scale, Reynolds number, propulsion arrangement, stability philosophy, and
structural constraints are comparable.

### 7.2 Research topics

The evidence review shall cover:

- fixed vertical surfaces on tailless and flying-wing aircraft;
- twin-fin placement in pusher configurations;
- wingtip fins and winglets as directional stabilisers;
- canted fins and their roll/yaw coupling;
- drag rudders and split elevons;
- propeller wake, swirl, and unsteady loading on nearby surfaces;
- low-Reynolds-number fin effectiveness;
- vertical-tail volume coefficients as screening data, not universal rules;
- propeller blade deflection and practical clearance envelopes;
- boom flexibility, empennage vibration, and whirl-related excitation;
- printed polymer saddle creep and tolerance;
- inspection practices for propeller-adjacent structures.

### 7.3 Starting primary references

The research log shall begin with, but not be limited to:

- NASA X-48B programme material for blended-wing-body directional-control
  architecture: <https://www.nasa.gov/aeronautics/x-48b/>.
- NASA X-48C configuration material for the effect of propulsion and aft-body
  integration: <https://www.nasa.gov/image-article/x-48c-hybrid-blended-wing-body-3/>.
- NACA/NASA technical literature on tailless gliders and directional stability:
  <https://ntrs.nasa.gov/search.jsp?R=20090026465>.
- TBS Chupito manual as a current small pusher flying-wing configuration reference:
  <https://www.team-blacksheep.com/media/files/tbs-chupito-manual.pdf>.
- TBS Mojito manual as an in-service fixed-fin forward-swept reference:
  <https://www.team-blacksheep.com/media/files/tbs-mojito-manual.pdf>.

Each source entry shall record:

- exact configuration;
- geometric values available;
- speed and Reynolds-number relevance;
- power-on or power-off condition;
- measured versus inferred claims;
- direct relevance to Salamandra;
- limitations preventing direct transfer.

### 7.4 Research deliverable

A new investigation note shall provide:

- a configuration taxonomy;
- a comparison table with traceable dimensions where available;
- documented applicability limits;
- derived candidate bounds for the parametric study;
- explicit statements where no reliable published margin exists;
- citations adjacent to every externally supported claim.

---

## 8. Single-source three-dimensional scene architecture

### 8.1 Architectural principle

The SVG generator shall not be the owner of aircraft geometry. It shall consume a
resolved scene containing typed three-dimensional objects and project that scene into
views.

The intended dependency direction is:

```text
design contract + measured component ledger + aerodynamic parameters
                              |
                              v
                    numerical solvers
        packaging / mass / CG / inertia / fins / structures
                              |
                              v
                    resolved aircraft scene
             components + surfaces + hazards + datums
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
         top view         side view        rear view
             |                |                |
             +----------------+----------------+
                              |
                              v
                     generated SVG sheets
```

Reverse dependencies are prohibited. A solver shall never read an SVG coordinate, and a
canonical physical coordinate shall never be recovered from hand-authored drawing text.

### 8.2 Proposed scene-object classes

The detailed implementation may adapt existing dataclasses, but the resolved scene must
represent at least:

```python
ComponentEnvelope
    identifier
    display_name
    mass_kg
    centre_xyz_m
    size_xyz_m
    orientation_rpy_deg
    authority
    system
    variant

SurfaceGeometry
    identifier
    vertices_xyz_m
    thickness_model
    aerodynamic_reference
    mass_model
    authority

StructuralMember
    identifier
    centreline_xyz_m
    section
    material
    mass_model
    authority

HazardEnvelope
    identifier
    geometry
    operating_condition
    included_allowances
    authority

AircraftScene
    components
    surfaces
    structures
    hazards
    datums
    derived_properties
    variant
```

### 8.3 Coordinate contract

The project coordinate system shall remain explicit:

- origin: root quarter-chord datum;
- `+x`: aft;
- `+y`: starboard;
- `+z`: upward;
- all solver geometry: SI units;
- drawing dimensions: millimetres;
- angles: degrees only at interfaces and annotations, radians internally where required.

Every drawing projection shall use a shared tested transformation:

| View | Horizontal drawing axis | Vertical drawing axis | Hidden axis |
|---|---|---|---|
| Top | `x` | `y` | `z` |
| Side | `x` | `z` | `y` |
| Rear | `y` | `z` | `x` |

Mirroring, sign conventions, and paper-coordinate inversion shall be implemented once.

### 8.4 Component authority

`equipment_layout.py` shall remain the owner of component:

- mass;
- position;
- orientation;
- external envelope;
- variant membership;
- mass-centre location;
- installation maturity.

The drawing code shall request resolved components. It shall not repeat camera, battery,
VTX, ESC, receiver, controller, servo, GPS, motor, or antenna coordinates.

### 8.5 Surface authority

The fin calculation shall own:

- number of surfaces;
- total and individual area;
- root and tip vertices;
- aerodynamic-centre station;
- local aerodynamic reference chord;
- taper, aspect ratio, and sweep;
- lateral and vertical installation stations;
- thickness schedule;
- credited aerodynamic area.

Any root fairing, saddle, fastener, or load spreader shall exist as a separate scene
object. It shall have its own geometry, authority, mass treatment, and collision status.

---

## 9. Complete electronic-skeleton representation

### 9.1 Required components

The side elevation shall render every component present in the authoritative reference
layout, including as applicable:

- flight battery and its complete adjustment/travel envelope;
- flight controller;
- ESC;
- radio receiver;
- GPS and compass;
- camera;
- DJI O4/VTX or selected video transmitter;
- antennas and rigid keep-out volumes;
- motor;
- motor mount;
- propeller hub and swept envelope;
- elevon servos;
- wiring or coaxial routing envelopes where they are controlled;
- structural tubes and cradles;
- variant-specific fin supports.

The list shall be generated from component metadata rather than maintained as a second
hard-coded drawing list.

### 9.2 Projection rules

For each oriented cuboid or envelope, the renderer shall:

1. transform its local corners into aircraft coordinates;
2. project all corners onto the selected view plane;
3. compute the convex projected outline or exact projected polygon;
4. draw its true projected mass centre;
5. assign line and fill style from authority and system metadata;
6. generate its label from the canonical identifier;
7. preserve near/far ordering where relevant;
8. expose the projected coordinates to validation tests.

Axis-aligned rectangles may be used only when the component orientation makes them exact
or when the graphic is explicitly labelled as a bounding envelope.

### 9.3 Visual hierarchy

The side-view hierarchy shall be:

1. light construction grid and datums;
2. hazard envelopes;
3. wing and fuselage OML with low-opacity fill;
4. structural skeleton;
5. electronic component envelopes;
6. component mass-centre markers;
7. propulsion system;
8. fixed fins and supports;
9. dimensions, leaders, and review warnings.

The OML shall remain transparent enough to inspect the skeleton. Hidden components shall
not disappear merely because they are inside the body.

### 9.4 Labels and collision control

Labels shall be placed by a deterministic layout routine or an explicit reviewed label
map keyed by component identifier. Label location may be drawing-owned, but the leader
endpoint must always come from the component geometry or mass centre.

The generator shall check:

- label-to-label overlap;
- label-to-dimension overlap;
- label intrusion into the title block;
- ambiguous leaders crossing unrelated components;
- component identifiers missing from the view;
- duplicate identifiers;
- unreadable text after normal wiki scaling.

### 9.5 Variant consistency

The CLEAN and V1 views shall be produced from the same base scene. V1 may add only its
declared variant objects and derived mass/balance changes. A common component shall not
silently change coordinates between variants unless the variant model explicitly moves
it.

---

## 10. Propeller swept-volume and clearance model

### 10.1 Nominal geometry

The nominal propeller shall be described by:

- shaft-axis origin and unit vector;
- propeller-plane station;
- diameter;
- hub diameter and thickness;
- blade count where needed for dynamic evaluation;
- nominal axial thickness of the rotating region;
- direction of rotation where wake modelling requires it.

### 10.2 Allowance stack

The minimum safe separation shall not be a single guessed constant. The model shall carry
an allowance stack such as:

\[
C_{required}=
\delta_{blade}+
\delta_{shaft}+
\delta_{motor\ mount}+
\delta_{support}+
\delta_{assembly}+
\delta_{manufacturing}+
C_{residual}
\]

Each term shall have:

- value and units;
- source or calculation;
- operating/load condition;
- sign convention;
- statistical or worst-case interpretation;
- authority tag;
- sensitivity range.

Unknown terms shall remain explicit intervals. They shall not be silently set to zero.

### 10.3 Clearance calculation

For every candidate component near the propeller, Python shall calculate the minimum
distance between its complete three-dimensional envelope and the inflated propeller
swept volume.

The report shall distinguish:

- nominal geometric clearance;
- worst-case tolerance clearance;
- loaded structural clearance;
- residual safety margin;
- axial overlap length;
- radial separation at every overlapping axial station.

The minimum shall be located and reported as an `(x, y, z)` witness-point pair so the
drawing can identify the controlling location.

### 10.4 Operating cases

At minimum, clearance shall be checked for:

1. static assembly;
2. maximum commanded motor speed on the ground;
3. maximum predicted flight dynamic pressure and fin side load;
4. maximum declared manoeuvre load;
5. asymmetric fin load or gust;
6. hard-landing residual displacement if the booms can be knocked out of alignment;
7. thermal/creep tolerance at the motor mount and printed saddles;
8. maintenance misassembly within physically possible fastener clearances.

### 10.5 Drawing representation

The propeller shall be represented differently in each view:

- side view: propeller plane plus the axial hazard thickness;
- top view: swept disk intersection and lateral support clearance;
- rear view: full swept circle and inflated exclusion circle;
- local detail: controlling witness points and allowance breakdown.

No side-view line shall be labelled as proof of radial clearance.

---

## 11. Directional-architecture trade space

The study shall not assume that the current twin-boom arrangement is the only viable
solution.

### 11.1 Candidate A — current lateral twin fins with axial overlap

Study purpose:

- determine whether the current concept is physically valid once the complete clearance
  envelope is included;
- quantify the aerodynamic and structural effects of its present lateral station;
- determine whether improved views alone would resolve the apparent collision.

Required variants:

- current `y = +/-140 mm`;
- increased lateral station;
- reduced or increased longitudinal station;
- root fairing removed;
- fairing fully modelled.

### 11.2 Candidate B — twin fins entirely forward of the propeller hazard slab

Study purpose:

- eliminate axial overlap without increasing aft boom length;
- determine the area penalty from reduced moment arm;
- evaluate body/wing sidewash and local flow quality;
- evaluate whether the surfaces obstruct propulsion or equipment access.

### 11.3 Candidate C — twin fins entirely aft of the propeller hazard slab

Study purpose:

- evaluate a geometrically obvious separation arrangement;
- quantify boom-length, vibration, aft-mass, and balance penalties;
- evaluate propeller-wake excitation and power-on effectiveness.

This candidate shall not receive preference merely because it looks unambiguous in side
view.

### 11.4 Candidate D — outboard wing-mounted fins

Study purpose:

- use existing wing structure and large lateral separation;
- examine wing bending/torsion coupling and printed-joint loads;
- evaluate added wetted area, interference, and transport vulnerability;
- determine whether local forward sweep alters fin inflow or yaw-roll coupling.

### 11.5 Candidate E — wingtip fins or winglets

Study purpose:

- compare directional stability with possible induced-drag interaction;
- assess tip mass and flutter/divergence implications;
- examine ground handling and modular wing-joint penalties.

No induced-drag benefit shall be credited without an aircraft-level aerodynamic result.

### 11.6 Candidate F — canted twin fins

Study purpose:

- investigate height reduction and combined directional/lateral effects;
- quantify lost vertical projected area;
- calculate roll moment from sideslip and asymmetric loading;
- evaluate print and root-joint complexity.

### 11.7 Candidate G — active drag-yaw devices

Study purpose:

- determine whether split elevons or drag rudders can provide required control authority;
- distinguish control authority from passive stability;
- calculate actuator count, mass, power, hinge moment, failure modes, and drag.

This is a new controlled-system architecture and shall not be treated as a cosmetic
variation of V1a.

---

## 12. Parametric aerodynamic study

### 12.1 Independent variables

The screening model shall expose at least:

- fin count;
- fin aerodynamic-centre `x` station;
- lateral `y` station;
- root `z` station;
- total area;
- aspect ratio;
- taper ratio;
- quarter-chord sweep;
- cant angle;
- root and tip thickness;
- fixed-fin versus movable-surface fraction;
- power-on effectiveness ratio;
- sidewash factor;
- support/fairing geometry class.

Bounds shall come from packaging, research, low-Re aerodynamic suitability, and printable
geometry. Bounds shall not be chosen only to surround the current solution.

### 12.2 Dependent quantities

For every candidate, Python shall calculate:

- individual and total area;
- span, root chord, tip chord, MAC, and centroid;
- aerodynamic-centre coordinates;
- fin Reynolds-number range;
- lift-curve-slope uncertainty;
- fin contribution to `Cn_beta`;
- complete-aircraft `Cn_beta` uncertainty band;
- fin contribution to `Cn_r`;
- estimated yaw-mode properties using the current inertia model;
- drag increment and uncertainty;
- local side-force and root bending moment;
- mass range;
- CG and inertia changes;
- required battery station;
- propeller clearance margins;
- boom geometry and structural metrics.

### 12.3 Robust target formulation

The optimiser shall not size the fin only to a nominal `Cn_beta = +0.0005/deg` value.
Before optimisation, the project shall define:

- the handling or test objective behind the target;
- the uncertainty variables included;
- which uncertainties are independent;
- the required lower-bound stability margin;
- acceptable yaw natural frequency and damping;
- required power-on and power-off behaviour;
- acceptable control-system dependence.

The screening constraint shall use the independent worst-case corner or a justified
probabilistic formulation. A nominally positive result with a negative credible lower
bound shall remain open.

### 12.4 Analysis fidelity ladder

The study shall progress through increasing fidelity:

1. analytical tail-volume and DATCOM/Helmbold-style screening;
2. sensitivity and uncertainty sweep;
3. lifting-surface or vortex-lattice aircraft model;
4. viscous section analysis over relevant Reynolds numbers where applicable;
5. propeller-wake sensitivity model;
6. CFD or higher-fidelity local investigation only for unresolved finalists;
7. ground and flight-test correlation.

Low-fidelity results shall be used to eliminate poor concepts, not to manufacture false
precision.

### 12.5 Required plots and tables

The investigation output shall include:

- required fin area versus AC station;
- lower/nominal/upper `Cn_beta` versus AC station;
- `Cn_r` versus AC station;
- fin mass versus AC station;
- aircraft CG and required battery station versus AC station;
- boom tip displacement versus fin station;
- propeller clearance versus lateral station;
- drag increment versus fin area and architecture;
- Pareto plots for stability, mass, drag, and clearance;
- a table of all rejected candidates with explicit rejection reasons.

---

## 13. Mass, balance, and inertia coupling

### 13.1 Mass model

Each candidate shall include:

- printed shell or plate mass;
- spar or leading-edge reinforcement;
- saddle and load spreader;
- fasteners;
- boom extension or replacement;
- adhesive where applicable;
- servo, horn, linkage, and wiring for an active rudder;
- fairing mass;
- any compensating ballast.

The mass model shall use geometry-derived lengths and areas wherever possible. Fixed
mass literals may be used only for measured or catalogued hardware.

### 13.2 Balance closure

For every candidate:

1. add all variant-specific mass objects to the component ledger;
2. solve the aircraft CG from the complete ledger;
3. solve the required battery station;
4. compare that station with the physical travel envelope;
5. report residual CG error if clamped to the envelope;
6. prohibit hidden ballast or undeclared component movement;
7. recompute pitch, roll, and yaw inertia.

Any candidate that cannot meet the controlled CG range with a feasible battery station
shall fail or explicitly propose a separately reviewed packaging change.

### 13.3 Propagation requirement

Changing a component coordinate or mass shall automatically affect:

- the component in every drawing view;
- total mass;
- CG;
- inertia tensor;
- fin moment arm where CG-dependent;
- stability and yaw-mode results;
- battery solution;
- collision and containment checks;
- annotation tables.

---

## 14. Structural and aeroelastic screening

### 14.1 Fin loads

At minimum, calculate side force using declared dynamic-pressure cases and bounded fin
lift coefficient. Convert this to:

- shear at root;
- root bending moment;
- torsional moment about the attachment;
- local bearing and fastener loads;
- spar stress;
- printed-shell stress and strain screening.

### 14.2 Boom response

For each boom concept, calculate:

- bending stiffness in both principal directions;
- torsional stiffness;
- fin-root displacement under side load;
- fin-root rotation;
- clearance reduction at the propeller plane;
- stress and safety factor;
- first relevant natural frequencies;
- sensitivity to joint compliance.

The calculation shall include the actual distance from the structural constraint to the
fin load resultant. Using only fin area without installation lever arms is insufficient.

### 14.3 Dynamic interaction

The study shall compare structural frequencies with:

- motor rotational frequency range;
- blade-passing frequency range;
- expected autopilot control activity;
- plausible fin vortex-shedding frequencies;
- airframe modes already identified elsewhere in the project.

Resonance separation criteria shall be declared before acceptance.

### 14.4 Printed interfaces

The root concept shall define or bound:

- material;
- print orientation;
- wall and rib schedule;
- fastener preload and bearing;
- layer-normal tension risk;
- creep temperature;
- replaceability;
- inspection access;
- assembly tolerance;
- failure containment relative to the propeller.

---

## 15. Propulsion and wake interaction

### 15.1 Power-off baseline

Every architecture shall first be assessed in free-stream or justified local-flow
conditions without propeller assistance. No stabilising slipstream credit shall be
required for safe power-off behaviour unless that dependence is an explicit system
decision.

### 15.2 Power-on cases

For surfaces influenced by propeller flow, evaluate:

- local dynamic-pressure ratio;
- swirl angle;
- spatial non-uniformity;
- blade-passage unsteadiness;
- throttle dependence;
- yawing moment caused by asymmetric inflow;
- vibration and fatigue implication;
- control or stability discontinuity during throttle transients.

### 15.3 Installation penalty

The design shall also check whether fins or supports:

- obstruct propeller inflow;
- create noise or efficiency loss;
- disturb motor cooling;
- complicate propeller replacement;
- expose cables to the rotating envelope;
- create debris paths toward the propeller after minor damage.

---

## 16. Drawing redesign specification

### 16.1 General drawing rules

All affected sheets shall be generated from the resolved scene. They shall preserve:

- metric A3 format;
- authority-tag line hierarchy;
- stable element identifiers;
- technical descriptions and metadata;
- draft/not-for-manufacture status while gates remain open;
- numerical dimensions derived from the same values used by calculations.

### 16.2 `SLM-GA-002` side elevation

The revised side sheet shall show:

- CLEAN and selected fixed-fin variant from a common base scene;
- complete electronic skeleton;
- mass-centre markers;
- total CG and relevant allowable band;
- battery travel and solved battery position;
- motor, mount, shaft, hub, and propeller hazard slab;
- booms and all fin supports;
- near and far fin identities;
- credited fin planform separately from fairing geometry;
- actual longitudinal relationships and dimensions;
- warnings that radial clearance is proved in the rear/top views;
- links or callouts to the controlling clearance detail.

The sheet shall not use a single opaque fin silhouette when two surfaces coincide in
projection. Options include controlled offset line styles, near/far labels, or a small
local exploded projection, provided no physical coordinate is falsified.

### 16.3 `SLM-EQP-001` electronic skeleton

This sheet shall remain the detailed component authority view and shall use the same
scene as `SLM-GA-002`. It shall show:

- top, side, and where useful rear projections;
- every reference-layout component;
- component IDs and mass centres;
- coordinate and mass schedule;
- variant additions;
- collision or containment findings;
- CG and inertia summary;
- propeller exclusion envelope as packaging context.

The side skeleton in `SLM-GA-002` may simplify labels, but it shall not omit physical
components that control packaging or interpretation.

### 16.4 `SLM-FIN-001` fin review

The dedicated fin sheet shall show:

- exact calculated planform vertices;
- aerodynamic centre and MAC;
- credited area boundary;
- root section and thickness schedule;
- reinforcement and attachment concept;
- root fairing as a distinct object;
- top installation view;
- rear installation view with propeller circles;
- controlling three-dimensional clearance witness points;
- boom deflection allowance;
- mass and load summary;
- stability and damping summary;
- open manufacturing and test gates.

### 16.5 Rear-view requirement

The rear view shall include:

- motor/propeller axis;
- nominal propeller circle;
- inflated hazard circle or envelope;
- left and right booms;
- left and right fins with thickness;
- vertical and lateral datums;
- minimum-clearance dimension at the controlling point;
- distinction between nominal and worst-case clearance;
- an explicit PASS/OPEN/FAIL status.

### 16.6 Top-view requirement

The top view shall include:

- propeller disk or hazard intersection;
- axial span of each support and fin root;
- lateral stations;
- full component widths;
- fairing and fastener envelopes;
- axial overlap dimensions;
- minimum lateral or planar clearance where meaningful.

### 16.7 Root-fairing rule

No fairing shall be drawn as an arbitrary Bezier addition inside the renderer. The
fairing must be one of:

1. absent;
2. generated from declared parameters as a scene object;
3. imported from controlled CAD/geometry and projected;
4. shown schematically, outside the physical view, and explicitly excluded from any
   installation claim.

If physically present, it shall enter:

- collision calculation;
- mass and CG;
- structural load path;
- wetted-area/drag estimate where relevant;
- all orthographic views.

---

## 17. Automated verification strategy

### 17.1 Unit tests

Add tests for:

- coordinate transformations;
- oriented component projections;
- propeller-envelope construction;
- point/envelope minimum distance;
- planform area and centroid reconstruction;
- AC, MAC, and moment-arm consistency;
- mass and CG propagation;
- fin-area solver convergence;
- uncertainty-corner monotonicity;
- boom stiffness and clearance coupling.

### 17.2 Contract tests

Contract tests shall ensure:

- no duplicate declaration of controlled component coordinates;
- no duplicate propeller diameter or station;
- no drawing-owned fin station;
- no drawing-owned component envelope;
- every rendered physical object resolves to a scene identifier;
- every scene object required by a sheet appears exactly once or is explicitly filtered;
- authority tags propagate from model to drawing.

### 17.3 Mutation tests

The following deliberate mutations shall each cause the expected calculations and
drawings to change or a check to fail:

1. move the battery `+10 mm` in `x`;
2. move the VTX `+5 mm` in `z`;
3. increase propeller diameter by `5 mm`;
4. move the motor axis laterally by `2 mm`;
5. increase boom width by `2 mm`;
6. move a fin laterally inward by `10 mm`;
7. move the fin AC forward by `20 mm`;
8. add a forward-projecting root fairing;
9. increase fin mass by `10 g`;
10. rotate an electronics component.

For example, moving the battery shall alter its top and side projection, total CG,
inertia, solved layout report, and any dependent stability output. If only the drawing or
only the mass table changes, the digital thread is incomplete.

### 17.4 SVG structural tests

Generated SVGs shall be checked for:

- valid XML;
- A3 viewBox and physical size;
- expected drawing and object IDs;
- complete metadata and technical description;
- no stale values in annotations;
- no missing electronic-skeleton objects;
- propeller nominal and hazard-envelope IDs;
- near/far fin identifiers;
- rear-view clearance element;
- title-block and authority legend;
- absence of unsupported raster overlays.

### 17.5 Numerical-to-graphic round-trip checks

For selected points and envelopes, tests shall:

1. calculate the physical coordinate;
2. apply the view transformation;
3. locate the generated SVG element;
4. compare its SVG coordinate with the expected paper coordinate;
5. invert the transformation;
6. confirm recovery of the physical coordinate within tolerance.

This prevents an SVG from being numerically labelled correctly while geometrically
drawn at the wrong position.

### 17.6 Staleness tests

`generate_blueprints.py --check` shall fail whenever any canonical input, solver output,
scene object, annotation, README preview, or wiki copy is stale.

---

## 18. Visual review protocol

Automated checks cannot determine whether an engineering sheet communicates clearly.
Every regenerated sheet shall therefore be rendered and inspected.

### 18.1 Required render formats

- full A3 raster render at print-equivalent resolution;
- normal wiki/browser preview size;
- close crops of the propeller/fin installation;
- close crop of the electronic skeleton;
- monochrome or grayscale inspection if line hierarchy may depend excessively on colour.

### 18.2 Visual review checklist

The reviewer shall confirm:

- the propeller cannot reasonably be mistaken for intersecting a fin;
- side-view projection ambiguity is explicitly explained;
- the complete electronic skeleton is visible;
- internal and external objects are distinguishable;
- the motor axis and propeller plane are unambiguous;
- near and far fins are distinguishable;
- the rear view proves the controlling radial clearance;
- the top view proves the lateral and axial relationship;
- fairing and credited fin boundaries cannot be confused;
- dimensions point to the intended geometry;
- labels do not obscure the installation;
- annotation text remains legible at normal display size;
- no leader line implies a false mechanical connection;
- the overall shape is aerodynamically and structurally plausible;
- the title and notes do not claim more maturity than the model supports.

### 18.3 Adversarial interpretation test

At least one review pass shall ask:

> What incorrect physical conclusion could a competent reader draw from this sheet?

Any plausible conclusion that the fin intersects the propeller, floats without support,
occupies the fuselage centre plane, or hides required electronics is a drawing failure
even if the underlying coordinates are correct.

---

## 19. Decision matrix and selection gate

### 19.1 Scored criteria

Finalists shall be compared using a documented matrix. Suggested top-level criteria are:

| Criterion | Required evidence |
|---|---|
| Propeller safety | Worst-case three-dimensional clearance |
| Static directional stability | Lower/nominal/upper `Cn_beta` |
| Yaw damping | `Cn_r` and yaw-mode estimate |
| Control authority | Rudder/drag-device derivative if applicable |
| Mass | Complete installed mass range |
| Balance | Feasible battery position and residual CG error |
| Structure | Stress, deflection, torsion, and frequency screens |
| Aerodynamic drag | Increment and uncertainty |
| Wake robustness | Power-on/off sensitivity |
| Printability | Build orientation, segmentation, tolerances |
| Maintainability | Propeller, motor, wiring, and fastener access |
| Damage tolerance | Consequence of boom or fin displacement |
| Drawing clarity | Unambiguous three-view communication |
| Testability | Ability to instrument and compare configurations |

Weights shall be approved before scoring to prevent adjusting them to favour a preferred
shape.

### 19.2 Hard constraints

Regardless of weighted score, a candidate shall fail if:

- worst-case propeller clearance is negative;
- stability fails the approved lower-bound requirement;
- the aircraft cannot meet the CG range with a feasible layout;
- structural deflection consumes the clearance margin;
- the support cannot be inspected or assembled reliably;
- geometry shown in drawings is absent from mass or collision models;
- the drawing cannot communicate the installation without hidden-coordinate assumptions.

### 19.3 Architecture-selection record

The selected architecture shall receive a revised or superseding ADR containing:

- alternatives considered;
- research evidence;
- numerical comparison;
- sensitivity results;
- selected geometry and authority;
- rejected alternatives and reasons;
- remaining open gates;
- required tests;
- drawing references.

---

## 20. Implementation work breakdown

### Phase 0 — preserve and baseline

1. Capture current numerical outputs and rendered SVGs as audit evidence.
2. Record the exact current fin, boom, CG, mass, and stability values.
3. Identify every local literal related to fins, booms, equipment, motor, and propeller.
4. Classify each literal as controlled, derived, duplicated, or drawing-only.
5. Confirm the current full verification suite passes before refactoring.

**Exit gate:** a reproducible baseline and duplication inventory exist.

### Phase 1 — evidence closure and requirements

1. Complete the primary-source research programme.
2. Define operating and load cases.
3. Define the propeller-clearance allowance method.
4. Define directional-stability and damping acceptance criteria.
5. Define required power-on and power-off behaviour.
6. Define structural and vibration screening criteria.
7. Record unknowns that require measurement.

**Exit gate:** optimisation constraints are defensible and traceable.

### Phase 2 — canonical scene model

1. Define scene dataclasses and coordinate contract.
2. Adapt the existing component ledger into scene objects.
3. Add controlled structural and hazard objects.
4. Represent fins and supports independently.
5. Add shared orthographic projection functions.
6. Add unit and round-trip tests.

**Exit gate:** a scene can generate consistent top, side, and rear coordinates without an
SVG renderer.

### Phase 3 — complete electronic skeleton

1. Resolve all reference-layout components.
2. Project every component into all applicable views.
3. add system/authority styling metadata;
4. add mass-centre markers and schedule data;
5. add component-presence and uniqueness tests;
6. compare the scene projections with existing `SLM-EQP-001` output.

**Exit gate:** the side projection contains the same physical reference layout as the
equipment sheet.

### Phase 4 — clearance and structural coupling

1. Implement nominal and inflated propeller envelopes.
2. Implement minimum-distance witness-point calculations.
3. represent boom deflection and tolerance states;
4. add fin and fairing envelopes;
5. add static, loaded, and maintenance clearance cases;
6. expose results to drawings and reports.

**Exit gate:** every propeller-adjacent object has a computed PASS/OPEN/FAIL result.

### Phase 5 — architecture and placement trade

1. Generate all credible candidate architectures.
2. Sweep longitudinal, lateral, vertical, and planform variables.
3. Couple stability, damping, drag, mass, CG, inertia, structure, and clearance.
4. identify Pareto-optimal candidates;
5. perform higher-fidelity checks on finalists;
6. select or reject an architecture through the decision matrix.

**Exit gate:** the selected station is an optimisation result or a documented compromise,
not an unexplained literal.

### Phase 6 — drawing implementation

1. Refactor the affected sheets to consume the scene.
2. Add the complete side electronic skeleton.
3. Add rear and top clearance views.
4. separate credited fin, fairing, support, and hazard graphics;
5. generate all dimensions and annotations from model values;
6. remove obsolete drawing-only geometry and literals;
7. preserve stable semantic SVG identifiers.

**Exit gate:** no physical fin/equipment/propeller coordinate is owned by the SVG code.

### Phase 7 — verification and publication

1. Run unit, contract, mutation, drawing, and full repository checks.
2. Regenerate all affected SVGs and documentation indexes.
3. render full sheets and critical crops;
4. complete the visual and adversarial review checklists;
5. update design guide, research note, ADR, calculation documentation, and open points;
6. publish only after numerical and visual gates close.

**Exit gate:** drawings and documentation accurately represent the selected calculated
configuration and explicitly state unresolved manufacturing/test gates.

---

## 21. File-level implementation map

The final implementation is expected to touch the following areas, subject to detailed
code audit:

| File or area | Planned responsibility |
|---|---|
| `calculations/equipment_layout.py` | Canonical component envelopes, masses, positions, CG, inertia |
| `calculations/yaw_stability.py` | Candidate fin geometry, stability, damping, mass/drag coupling |
| New scene/projection module if justified | Resolved aircraft scene and shared view transforms |
| Structural calculation module | Boom/fin loads, deflection, frequency, clearance coupling |
| `calculations/generate_blueprints.py` | Pure scene-to-SVG presentation and annotations |
| `calculations/drawing_index.py` | Accurate sheet descriptions and publication metadata |
| `geometry/drawings/*.svg` | Generated outputs only |
| `tests/` | Unit, contract, mutation, SVG, and propagation checks |
| `research/` | Primary-source architecture and clearance investigation |
| `decisions/ADR-0038-fixed-fin-variant.md` | Supersede or revise the current architecture decision |
| `design/Salamandra-Design-Guide-v0.1.md` | Selected controlled geometry and remaining gates |
| `design/Design-Guide-Open-Points-v0.1.md` | Unresolved test and manufacturing questions |
| `README.md` and wiki | Regenerated drawing descriptions and previews |

No generated SVG shall be edited directly.

---

## 22. Required numerical reports

The implementation shall produce machine-readable or reproducible reports containing:

### 22.1 Configuration summary

- configuration identifier;
- source revision;
- fin architecture;
- geometry coordinates;
- component layout identifier;
- propeller definition;
- authority and maturity state.

### 22.2 Stability summary

- assumptions and method;
- `Cn_beta` contributions and uncertainty band;
- `Cn_r` contributions;
- fin lift-curve-slope band;
- sidewash and dynamic-pressure factors;
- yaw inertia;
- yaw-mode metrics;
- power-on/off comparison.

### 22.3 Clearance summary

- nominal propeller geometry;
- every inflation allowance;
- evaluated object;
- operating case;
- closest witness points;
- nominal and worst-case distance;
- required clearance;
- residual margin;
- status.

### 22.4 Mass and balance summary

- component-level mass changes;
- total mass;
- CG;
- allowable CG range;
- solved battery station;
- battery travel limit;
- residual CG error;
- inertia tensor.

### 22.5 Structural summary

- load cases;
- fin side force;
- root bending and torsion;
- boom stress and deflection;
- joint loads;
- frequency comparison;
- uncertainty and safety factors.

---

## 23. Measurement and test plan

Analytical closure shall identify measurements needed before flight.

### 23.1 Bench measurements

- actual propeller maximum radius and blade-to-blade variation;
- shaft runout;
- motor-mount angular and lateral error;
- as-built boom lateral station;
- fin-root station and cant;
- static boom deflection under calibrated side load;
- saddle slip and creep;
- complete fin assembly mass;
- aircraft CG and inertia estimation;
- vibration spectrum across throttle.

### 23.2 Static clearance demonstration

Use a physical keep-out gauge or controlled slow-rotation inspection representing the
approved inflated envelope. A visual gap to an undeformed stationary blade is not enough.

### 23.3 Ground power test

The ground test shall check:

- clearance throughout the throttle range;
- vibration and resonance;
- boom/fin displacement;
- fastener movement;
- wiring security;
- propeller-wake loading;
- post-test inspection dimensions.

### 23.4 Flight-test progression

Subject to the project flight-test plan:

1. power-off or low-power handling where safe;
2. conservative speed envelope;
3. controlled yaw excitation;
4. system-identification manoeuvres;
5. throttle-dependent comparison;
6. expansion toward cruise and maximum declared cases;
7. comparison against calculated yaw response;
8. inspection after each expansion step.

No flight result shall be used to hide a pre-flight geometric interference.

---

## 24. Risks and controls

| Risk | Consequence | Control |
|---|---|---|
| Optimising to an arbitrary nominal `Cn_beta` | Oversized or misplaced fin | Define handling requirement and robust lower bound first |
| Treating side projection as 3D proof | Undetected collision or misleading drawing | Top/rear views and 3D distance solver |
| Moving fins aft only for visual separation | Excess boom mass, vibration, CG penalty | Compare full architecture trade |
| Crediting propeller slipstream without data | Unsafe power-off stability | Maintain power-off case and bounded power-on sensitivity |
| Drawing-only fairing | Unmodelled collision and mass | Separate scene object with full checks |
| Incomplete equipment view | False packaging understanding | Render complete canonical component list |
| Duplicated coordinates | Silent divergence | Contract lint and mutation tests |
| Excessive label density | Unreadable sheet | Deterministic hierarchy and rendered review |
| Low-Re method overconfidence | Incorrect fin effectiveness | Fidelity ladder and flight correlation |
| Printed joint creep | Clearance loss in service | Thermal/creep allowance and inspection plan |
| Boom resonance near blade passage | Fatigue or propeller strike | Modal screening and ground vibration test |
| Tip-mounted mass on swept wing | Aeroelastic penalty | Couple candidate to wing structural model |

---

## 25. Acceptance checklist

### 25.1 Before architecture selection

- [ ] Primary-source research completed and cited.
- [ ] Stability and damping requirements defined.
- [ ] Propeller allowance stack defined.
- [ ] Complete candidate set evaluated.
- [ ] Mass, balance, structure, and clearance coupled.
- [ ] Uncertainty and sensitivity results available.
- [ ] Decision weights frozen before final scoring.

### 25.2 Before SVG regeneration is accepted

- [ ] All electronic components come from the canonical layout.
- [ ] Side view shows the complete skeleton.
- [ ] Top and rear views prove the propeller relationship.
- [ ] Near/far fins are unambiguous.
- [ ] Fin, fairing, support, and hazard envelopes are distinct.
- [ ] All dimensions are generated from model values.
- [ ] No physical coordinate is duplicated in drawing code.
- [ ] SVG IDs and metadata pass validation.
- [ ] Full-size and normal-size renders pass visual review.

### 25.3 Before design release

- [ ] Worst-case propeller clearance is positive with declared residual margin.
- [ ] Stability lower bound meets the approved requirement.
- [ ] Yaw damping and control behaviour meet the approved requirement.
- [ ] Battery and CG close without hidden ballast.
- [ ] Structural stress, deflection, and frequency screens pass.
- [ ] Printed interfaces have controlled geometry and tolerance.
- [ ] Bench measurements agree with the model within limits.
- [ ] Ground power test passes.
- [ ] ADR and design guide are updated.
- [ ] Remaining flight-test gates are explicit.

---

## 26. Immediate next action after approval of this plan

The first implementation action shall not be to redraw the fin. It shall be a read-only
declaration audit producing a table of every fin, boom, propeller, motor, and electronics
coordinate, its current owner, every consumer, and every duplicate literal.

Only after that audit shall the common scene and clearance model be introduced. The
existing drawings will then be regenerated from the connected model, and the fin
architecture trade will determine whether the current twin-fin concept is retained,
moved, reshaped, or rejected.

This sequence preserves the central engineering rule of the Salamandra project:

> The drawing represents the calculated aircraft; the calculation does not justify a
> shape invented by the drawing.

