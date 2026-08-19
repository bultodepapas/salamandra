# I-28 — Senior master plan for an automatic parametric Salamandra fuselage

**Status:** 🟡 **Revision 3 foundational OML implemented; coupled CAD/aircraft gates remain open**
**Revision:** 3
**Date:** 2026-08-19
**Scope:** automatic aerodynamic body around the CG-derived equipment, electrical and
structural skeleton; smooth wing-body integration; CLEAN/V1 compatibility; Python
generation, optimization, verification and drawing publication  
**Feeds:** OP-21, F1/F2, G10, future fuselage-generator ADR, body-inclusive aerodynamic
model, structural CORE definition and `SLM-FUS-001`  
**Authority:** installed hardware and released aircraft inputs retain their existing
`[M]`/`[D]`/`[E]` tags. Every surface law, blend law and acceptance threshold introduced
here is `[I]` until its named computational and physical gates close.  
**Warning:** **DRAFT — NOT FOR MANUFACTURE**

This document is the single controlling plan for the Salamandra fuselage programme. It
supersedes the earlier collection of I-28 implementation notes and the rejected
`lifting_saddle` Revision 2 surface. It deliberately separates four different objects:

1. the installed equipment/electrical skeleton;
2. structural and service corridors;
3. the aerodynamic outer mould line (OML);
4. the printable internal solid and its joints.

Passing one layer never grants authority to the next.

---

## 1. Executive engineering decision

The fuselage shall be generated as a **globally smooth, flattened, asymmetric spindle
integrated into the root wing**, not as a pointwise inflation of equipment boxes and not
as a conventional cylindrical tube.

The automatic generator shall solve a constrained multidisciplinary problem:

```text
wing + mission + configuration
              |
              v
      aerodynamic NP / target CG
              |
              v
equipment + electrical + cooling + load-path skeleton
              |
              v
global C2 body laws + nose aperture + wing-body blend
              |
              v
containment + topology + mass + structure + aero + service screens
              |
              v
      feasible nondominated candidates
              |
              v
body-inclusive balance / trim / yaw iteration
              |
              v
native CAD + print definition + physical evidence
```

The equipment creates **inequality constraints**. It does not directly create the
external silhouette. The shape shall be selected only from candidates that satisfy every
hard constraint and remain credible in CLEAN and V1.

### 1.1 Required visual and geometric character

The reference aircraft images supplied for the programme are qualitative `[I]` evidence,
not dimensional sources. They establish the following desired grammar:

- a local camera aperture inside a rounded nose, not a complete flat nose plane;
- continuous growth from the nose through the payload region;
- maximum useful body volume at or near the wing-root load-transfer region;
- an asymmetric section with a fuller forward belly and a lower dorsal height;
- broad, continuous wing-body shoulders rather than a body intersecting the wing;
- long, monotonic recovery toward the pusher motor;
- one common body architecture for CLEAN and V1, with the fin added to a credible aft
  spine rather than to a thin pedestal;
- no long parallel-sided bay, packaging-shaped corner, pinched neck or isolated bulge.

No coordinate shall be traced from a photograph. These statements become mathematical
shape constraints below.

### 1.2 Definition of programme success

The programme succeeds only when one candidate:

1. encloses all controlling hardware, routes, service motions and structural corridors;
2. has one coherent body-area distribution with no packaging imprint or unjustified
   neck;
3. joins the released root wing with at least geometric `C2` continuity in the analytical
   master and an auditable native-CAD equivalent;
4. returns net material mass and centroid to the canonical mass ledger;
5. closes CLEAN and V1 CG, body-inclusive NP, trim, yaw and battery travel without
   clamping;
6. meets structural, thermal, access, print-segmentation and assembly requirements;
7. passes mesh, drawing, CFD and physical validation gates;
8. is explicitly released by ADR and F2/S3 evidence.

A visually attractive watertight mesh is not programme success.

---

## 2. Rejected Revision 2 baseline and root-cause report

The current `lifting_saddle` surface is rejected as a design baseline. Its mesh may remain
temporarily as a regression fixture demonstrating what the new gates must catch, but it
must not be refined, promoted, dimensioned or used to make parts.

### 2.1 Observed failure

The top view exhibits a long rounded rectangle around the battery, a near-parallel neck,
an abrupt CORE enlargement and a disconnected-looking aft pod. The front reads as a
battery container rather than an aircraft nose. The wing and body overlap graphically but
do not form a designed aerodynamic union.

### 2.2 Mathematical causes

| Cause | Failure mechanism | Required correction |
|---|---|---|
| Pointwise smooth maximum of component AABBs | Printed the box dimensions into the OML | Use oriented/swept volumes only as sampled inequalities |
| Smooth-max power 8 | Approximated a hard maximum too closely | Remove envelope maximum from the shape law |
| 20 mm longitudinal transition over a 717.7 mm body | Created short shoulders and local slope reversals | Solve global longitudinal laws |
| Superellipse exponents near 4 | Produced slab sides and box-like corners | Restrict normal body sections primarily to `n = 2.0…3.0 [I]` |
| Full-section cap at the camera plane | Created a blunt complete front face | Generate a rounded nose and subtract a local viewing aperture |
| Body generated independently of the wing | Produced a visual intersection, not a junction | Include the released root wing in the surface construction |
| Containment-only feasibility | Allowed plateaus, necks and zero manufacturing reserve | Add distribution, structural, service and manufacturing constraints |
| Minimum audited residual `+0.001 mm` | Passed numerically with no robust geometric reserve | Require explicit numerical and manufacturing margins |

### 2.3 Mandatory regression rule

The rejected geometry shall cause at least the following new tests to fail:

- packaging-imprint/parallel-side gate;
- single-maximum area-distribution gate;
- CORE neck/section-modulus gate;
- camera-aperture topology gate;
- wing-body continuity gate;
- robust containment reserve gate.

If it passes the new suite, the suite is incomplete.

---

## 3. Authority and input contract

### 3.1 Coordinate system

Use the existing aircraft coordinates throughout:

- `x`: positive aft;
- `y`: positive starboard;
- `z`: positive upward;
- origin: released root quarter-chord datum;
- internal numerical unit: millimetres;
- SI conversion only at the analysis boundary.

Define a normalized longitudinal coordinate:

\[
s=\frac{x-x_N}{x_T-x_N},\qquad 0\le s\le1
\]

where `x_N` is the aerodynamic nose extent and `x_T` the aft body/motor closure. Neither
shall be inferred from a drawing.

### 3.2 Authoritative inputs

| Input | Owner | Use |
|---|---|---|
| Planform, root/tip sections, twist, sweep | `design_config.py` + released DAT files | exact root-wing surface |
| NP, target CG and mass targets | `aero_contract.py`, `balance_cg.py`, `mass_budget.py` | coupled balance |
| Component mass, position, OBB and movement authority | `equipment_layout.py` | containment and CG |
| Bought-in dimensions and thermal/electrical data | `equipment_catalog.py` | hardware envelopes |
| Boom, spar, supports and load cases | structural calculation modules | load corridors and section demand |
| Camera view direction and lens plane | equipment model/catalog | aperture and FOV keep-out |
| Propeller and motor planes | propulsion/drawing contract | aft exclusion and closure |
| Printer volume, material and measured process data | F2 manufacturing evidence | segmentation and wall release |

### 3.3 Inputs still required before manufacturing geometry

- connector bodies, bend radii and service loops;
- cable bundle cross-sections and routing corridors;
- camera horizontal/vertical FOV keep-out;
- inlet/outlet flow paths and heat loads;
- hatch removal swept volumes and tool-access cones;
- definitive CORE/wing material ownership;
- local load matrix at wing root, boom supports and motor mount;
- measured PETG/AERO-PLA orthotropic coupon properties;
- printer compensation, minimum reliable wall and joint tolerances.

Missing inputs remain named open gates. They shall not be replaced by silent defaults.

---

## 4. Geometry representation

### 4.1 Body section

At every body station, define an asymmetric superelliptic section:

\[
\left|\frac{y-y_c(s)}{b(s)}\right|^{n(s)}+
\left|\frac{z-z_c(s)}{a_{\pm}(s)}\right|^{n(s)}=1
\]

with:

\[
a_{\pm}(s)=
\begin{cases}
a_+(s), & z\ge z_c(s)\\
a_-(s), & z<z_c(s)
\end{cases}
\]

The centreline remains laterally symmetric for Article #1, so `y_c = 0` unless a future
configuration ADR changes it. Vertical asymmetry is intentional.

Design laws:

- `b(s)`: plan half-width;
- `a_+(s)`: dorsal radius;
- `a_-(s)`: ventral radius;
- `z_c(s)`: vertical section centre;
- `n(s)`: section exponent;
- optional `theta(s)`: local section roll, default zero;
- optional local camber/skew only after a named aerodynamic need is demonstrated.

The preferred normal range is `2.0 ≤ n ≤ 3.0 [I]`. A local excursion up to `3.2 [I]`
may be tested around a packaging-limited bay, but must not create a visible flat.

### 4.2 Positive global longitudinal laws

Represent positive dimensions in log space using clamped cubic B-splines:

\[
\log b(s)=\sum_j B_j(s)c_{b,j}
\]

\[
\log a_+(s)=\sum_j B_j(s)c_{+,j},\qquad
\log a_-(s)=\sum_j B_j(s)c_{-,j}
\]

and use ordinary cubic B-splines for `z_c(s)` and bounded logistic mapping for `n(s)`.
This provides positive dimensions and analytical `C2` continuity without manually drawn
Bezier segments.

Equipment starts/ends are **constraint sampling events**, not spline knots by default.
Knots are added only when a genuine geometric event requires an independent degree of
freedom: nose/lip, maximum-area region, wing blend, motor transition or released hard
interface.

### 4.3 Cross-sectional area

For the asymmetric section:

\[
A_b(s)=2b(s)\left(a_+(s)+a_-(s)\right)
\frac{\Gamma(1+1/n)^2}{\Gamma(1+2/n)}
\]

The equivalent radius is:

\[
r_e(s)=\sqrt{\frac{A_b(s)}{\pi}}
\]

`A_b`, `r_e`, their first two derivatives and their extrema shall be reported for every
candidate. The main body shall have one dominant maximum in the wing-root band. Minor
changes caused by the camera lip or motor interface must remain below the explicit
prominence tolerance recorded in the manifest.

### 4.4 Nose and camera aperture

The outer nose begins ahead of the camera lens plane and wraps around it. A first
analytical cap is an ellipsoid or compatible CST cap:

\[
F_N=\left(\frac{x-x_c}{L_N}\right)^2+
\left(\frac{y}{B_N}\right)^2+
\left(\frac{z-z_N}{H_N}\right)^2-1
\]

The camera FOV is a swept conical/frustum keep-out `F_C`. With negative-inside implicit
fields, the opened nose is:

\[
F_{N\setminus C}=\max(F_N,-F_C)
\]

The exact CAD implementation shall add a controlled lip radius and wall offset. The
camera lens plane shall never again cap the complete body. Acceptance requires zero ray
occlusion over the declared camera FOV plus an uncertainty allowance.

### 4.5 Wing-body integration

Construct the exact released root-wing upper and lower surfaces from the airfoil station
files, chord law and twist. The body shall not be designed or assessed in isolation at the
root.

Use a local blend coordinate:

\[
t=\operatorname{clamp}\left(
\frac{|y|-y_{b0}(x)}{y_{b1}(x)-y_{b0}(x)},0,1
\right)
\]

and the quintic smoothstep:

\[
H_5(t)=6t^5-15t^4+10t^3
\]

so that:

\[
H'_5(0)=H'_5(1)=H''_5(0)=H''_5(1)=0
\]

The provisional transition surface is:

\[
z_{blend}=[1-H_5(t)]z_{body}+H_5(t)z_{wing}
\]

This is a construction method, not proof of low drag. The blend boundaries, width and
thickness are optimization variables constrained by wing containment, local thickness,
surface normals and section-area recovery. Native CAD must reproduce the analytical
surface within a declared tolerance.

Implicit R-functions or normalized smooth unions may be used as diagnostic alternatives,
but their zero-level displacement and volume inflation must be quantified. An unmeasured
`softmin` is not acceptable as the released surface.

### 4.6 Aft body and pusher installation

The body shall retain a continuous load/service spine through the wing-root region and
then recover monotonically toward the motor envelope. The motor body, mount, cooling
route, wiring, propeller plane and blade exclusion volume are independent constraints.

The aft law shall prevent:

- a pinched boom-like OML immediately behind the wing;
- a separate motor bulb connected by a thin neck;
- an adverse expansion immediately before the propeller;
- a V1 fin pedestal unsupported by the common body structure.

CLEAN and V1 share the same primary aft-body law. V1 may add only the documented local
fin root reinforcement and fairing.

---

## 5. Skeleton and containment model

### 5.1 Replace AABB-driven shaping

Each component shall expose an oriented bounding volume or justified primitive. AABBs may
remain broad-phase collision accelerators but shall not drive the OML.

Required per-component metadata:

- authority and source;
- mass, centre and orientation;
- exact or conservative OBB/primitive;
- wall allowance;
- assembly clearance;
- connector and bend keep-outs;
- thermal keep-out;
- removal direction and swept service volume;
- collidable/non-collidable status;
- body-owned or wing-owned installation authority.

### 5.2 Containment inequality

For every sampled point `p` on a controlling volume:

\[
d_{OML}(p)\ge
t_{wall}(p)+c_{assembly}(p)+c_{service}(p)+\epsilon_{num}
\]

where `d_OML` is signed inward clearance and `epsilon_num` is a separate numerical
reserve. Initial review value:

\[
\epsilon_{num}=0.25\ \text{mm}\ [I]
\]

This value guards optimizer/mesh sampling only. It is not print tolerance and cannot
replace measured process compensation.

Containment shall be evaluated over surfaces and swept volumes, not only at eight box
corners. Adaptive refinement shall be triggered near the limiting point.

### 5.3 Structural corridors

The body generator shall receive immutable swept corridors for:

- nose boom and its two supports;
- wing spars, anti-rotation elements and joiners;
- battery cradle primary load path;
- motor mount and thrust reaction path;
- V1 fin spar/root when installed;
- required glue, fastener and tool-access volumes.

Styling variables cannot reduce these corridors.

---

## 6. Constrained design problem

### 6.1 Design vector

The bounded vector shall contain only independent choices:

```text
body spline coefficients:
    log half-width
    log dorsal radius
    log ventral radius
    vertical centre
    section exponent
nose:
    cap length, width, height, vertical centre, lip radius
wing-body blend:
    forward/aft extent, lateral extent, dorsal/ventral weights
aft body:
    recovery controls, motor transition controls
manufacturing concept:
    candidate split stations only after print constraints are active
```

Raw station ordinates, mesh vertices and component dimensions are derived data, not design
variables.

### 6.2 Hard feasibility constraints

A candidate is infeasible if any of the following fails:

1. component, route, structural or service-volume containment;
2. camera FOV and pitot/antenna keep-outs;
3. wing upper/lower surface containment and blend continuity;
4. motor/propeller exclusion;
5. positive dimensions and bounded section exponent;
6. watertight, consistently oriented, self-intersection-free topology;
7. one dominant body-area maximum in the declared root band;
8. no significant width/area minimum between battery and wing root;
9. minimum structural section properties from the imported load matrix;
10. CLEAN and V1 battery travel and CG closure without clamping;
11. mass allocation and material-ownership closure;
12. print-volume, access and assembly feasibility once those inputs exist.

### 6.3 Anti-box and anti-neck metrics

Define a packaging-imprint metric outside a small neighbourhood of the single area
maximum:

\[
P_{parallel}=\frac{1}{L}
\operatorname{meas}\{x: |db/dx|<\delta_b\}
\]

and report it with the chosen `delta_b`. A candidate fails if a nearly parallel interval
longer than `0.08 L [I]` is not tied to a released hard interface.

Define the forward-to-root neck ratio:

\[
R_{neck}=\frac{\min_{x\in[x_{battery,aft},x_{root,aft}]}A_b(x)}
{\max_{x\in[x_{battery,aft},x_{root,aft}]}A_b(x)}
\]

The optimizer shall enforce monotonic growth through this band unless the exact wing-body
union already provides the required area and structural section. Any exception requires
an ADR and load calculation.

Peak counting shall use prominence relative to the main area maximum, not raw derivative
sign changes caused by numerical noise.

### 6.4 Structural constraints

At each critical station, compute section properties for the actual candidate wall and
internal structure:

\[
I_y(x),\quad I_z(x),\quad J(x),\quad A_m(x)
\]

and evaluate the imported load cases:

\[
\sigma(x)=\frac{M_y z}{I_y}+\frac{M_z y}{I_z}
\]

\[
\tau(x)\approx\frac{T}{2A_m t}
\]

The material allowable, anisotropy, print direction and safety factors shall come from the
structural contract and physical coupons. Until then, the skin takes zero primary
structural credit and the geometry must preserve explicit internal load corridors.

### 6.5 Objective vector

Do not collapse the programme initially into one arbitrary scalar score. Retain a
feasible Pareto set over:

\[
\mathbf f=
\left[
S_{wet},
V_{material},
m_{net},
\int(A''(x))^2dx,
\int\kappa_s^2dS,
C_{pressure\ recovery},
C_{junction},
C_{service},
C_{thermal}
\right]
\]

where aerodynamic terms are fidelity-labelled proxies until validated. Candidate ranking
shall never compensate a failed hard constraint with a good merit score.

### 6.6 Aerodynamic screening hierarchy

1. **Geometry proxy:** wetted area, frontal area, area distribution, curvature and
   recovery-gradient metrics.
2. **Low-order aircraft model:** body side area, mass properties and first body/wing lift
   or moment corrections; no absolute drag claim.
3. **VSPAERO/OpenVSP diagnostic:** configuration trends and interaction screening, with
   documented limitations.
4. **Viscous CFD:** finalists only; mesh/domain/transition/roughness/opening and powered
   propulsor assumptions documented.
5. **Physical E2/E8 evidence:** drag/stall/trim and yaw response close the flight gate.

The available research explicitly warns against treating a smooth fillet or low-order
solver as proof of junction drag or separation behaviour.

---

## 7. Automatic solver architecture

### 7.1 Required Python modules

The current three files shall be refactored rather than incrementally styling Revision 2:

| Module | Required responsibility |
|---|---|
| `fuselage_contract.py` | schema, authority, bounds, gate thresholds and variant policy |
| `fuselage_envelopes.py` | OBBs, routes, swept volumes, service and structural corridors |
| `fuselage_sections.py` | asymmetric sections, area and section properties |
| `fuselage_body.py` | global positive `C2` longitudinal laws and body surface |
| `fuselage_nose.py` | cap, aperture, FOV and lip geometry |
| `fuselage_wing_blend.py` | released root-wing reconstruction and controlled blend |
| `fuselage_mesh.py` | tessellation, normals, caps/open boundaries and topology |
| `fuselage_constraints.py` | containment, anti-box, anti-neck, structural and service gates |
| `fuselage_objectives.py` | labelled merit/proxy calculations |
| `fuselage_optimize.py` | deterministic sampling, refinement and Pareto filtering |
| `fuselage_report.py` | manifest, residuals, uncertainty and rejected-reason reporting |
| `generate_blueprints.py` | projection only; never an independent OML |

Module names may be consolidated if interfaces remain equally explicit. Geometry,
constraints and reporting shall not be placed in one monolithic function.

### 7.2 Dependency policy

The baseline shall remain NumPy-only until a demonstrated limitation requires another
dependency. A candidate optimizer can begin with:

- seeded Latin hypercube exploration;
- feasibility projection/rejection;
- deterministic coordinate or pattern refinement;
- nondominated sorting;
- restart and convergence diagnostics.

SciPy may be proposed later for bounded nonlinear optimization only through an ADR that
demonstrates reproducible Windows installation and a measurable benefit. CadQuery or
another B-rep kernel is a downstream exact-solid backend, not the analytical authority.

### 7.3 Deterministic generation sequence

```python
inputs = load_canonical_aircraft_and_variants()
skeleton = build_oriented_swept_envelopes(inputs)
wing = reconstruct_released_root_wing(inputs)

population = seeded_designs(contract.seed, contract.bounds)
records = []
for design in population:
    body = solve_global_body_laws(design, skeleton)
    nose = subtract_camera_fov(build_nose(body, design), skeleton.camera)
    airframe = blend_body_and_wing(body, wing, design.blend)
    mesh = tessellate_with_resolution_control(airframe)
    residuals = evaluate_hard_constraints(mesh, airframe, skeleton, inputs)
    if residuals.all_pass:
        merits = evaluate_labelled_objectives(mesh, airframe, inputs)
        records.append((design, residuals, merits))

pareto = nondominated(records)
refined = deterministic_refinement(pareto)
publish_manifest_meshes_drawings(refined)
```

Every rejected candidate shall retain a machine-readable primary reason and worst
residual. Silent exception-based rejection is prohibited.

### 7.4 Coupled aircraft iteration

For each feasible geometric candidate:

1. compute net body material, excluding overlap with already budgeted wing/CORE material;
2. return mass, centroid and inertia to the canonical ledger;
3. solve CLEAN CG and battery station;
4. solve body-inclusive NP and trim;
5. repeat for V1 with the common body and local fin installation;
6. update side-area/yaw contribution;
7. update shell/structure and repeat until state changes are below declared tolerances;
8. reject any candidate requiring battery clamping or reserve mass without a physical
   location.

Convergence must be demonstrated for mass, CG, NP, trim and geometry, not inferred from a
single pass.

---

## 8. Verification and acceptance matrix

### 8.1 Analytical unit tests

- B-spline basis partition and derivative consistency;
- positivity/log-law round trip;
- superellipse points satisfy the implicit equation;
- asymmetric area matches numerical integration;
- sphere/ellipsoid mesh area and volume benchmarks;
- rigid-translation and reflection invariance;
- exact orientation and signed-volume consistency;
- camera-frustum Boolean truth cases;
- quintic blend endpoint position, slope and curvature identities;
- section-property checks against analytical ellipse/thin-wall cases.

### 8.2 Geometry contract tests

- every controlling volume present exactly once;
- adaptive containment convergence at limiting points;
- zero self-intersections, zero nonmanifold and unintended boundary edges;
- area/volume convergence under doubled resolution: retain the current review targets of
  `<0.5 %` area and `<0.3 %` volume `[I]` until tightened by evidence;
- one dominant area maximum;
- no significant battery-to-root neck;
- no unauthorized parallel-sided interval longer than `0.08 L [I]`;
- camera FOV unoccluded;
- wing blend position and normal continuity;
- motor and propeller exclusions;
- CLEAN/V1 common-body identity outside declared variant features.

### 8.3 Mutation tests

Seed at least these defects and require each to turn a named test red:

- containment function always returns clearance;
- camera aperture omitted;
- camera FOV direction reversed;
- battery AABB substituted for its OBB;
- one width control duplicated to create a plateau;
- CORE width reduced to create a neck;
- section exponent forced to 4.5;
- wing-body blend disabled;
- blend derivative changed from quintic to linear;
- face orientation reversed;
- overlap material counted twice;
- V1 battery requirement clamped to the stop.

### 8.4 Drawing acceptance

`SLM-FUS-001`, GA-001 and GA-002 shall project the exact accepted analytical model. After
every final regeneration:

- validate XML, A3 physical size, IDs, accessibility, provenance and static content;
- inspect full sheet and dense regions in a browser;
- inspect colour and grayscale;
- verify equipment remains visible separately from OML and structure;
- reject clipping, collisions, flat spots, kinks, islands, misleading line authority or
  manufacturing implication;
- compare sibling diffs and reject unintended generator fan-out.

### 8.5 Aerodynamic acceptance

Before release:

- body-inclusive NP/trim and static margin close for CLEAN and V1;
- credible viscous analysis shows no unacceptable junction separation over the flight
  envelope;
- cooling openings and propeller-on/off cases are represented;
- E2 measured drag, stall and trim agree within the declared model uncertainty;
- E8 yaw-decay evidence closes the finless/fixed-fin directional model.

### 8.6 Structural, thermal and manufacturing acceptance

- exact net printed mass and centroid close the ledger;
- wing-root, boom, cradle, motor and fin load paths pass analytical and physical tests;
- curved coupons reproduce material/process assumptions in actual orientation;
- VTX/ESC temperatures pass worst-case ground and flight tests;
- battery, camera, VTX, connectors and harnesses fit and remain serviceable;
- every part fits the qualified printer volume and has an assembly sequence;
- joints, wall schedule, tolerances and compensation are released by F2/S3 evidence.

---

## 9. Work breakdown and definitions of done

### WP0 — quarantine and authority closure

#### Tasks

1. Mark Revision 2 `lifting_saddle` as rejected in manifests and drawings.
2. Preserve one failed artifact only as a regression fixture.
3. Publish the fuselage authority/ownership ADR.
4. Resolve the 92.88 g reserve-mass locations.
5. Resolve V1 battery travel without acceptance clamping.
6. Define wing/CORE/body material replacement ownership.

#### Definition of done

No repository surface presents Revision 2 as a candidate; mass,
configuration and ownership blockers have named owners and machine-readable states.

### WP1 — complete skeleton contract

#### Tasks

1. Replace body-driving AABBs with OBBs or justified primitives.
2. Add connectors, routes, bends, service sweeps and thermal volumes.
3. Add camera FOV and cooling-flow corridors.
4. Add structural corridors and the local load matrix.
5. Add uncertainty for every non-measured dimension.

#### Definition of done

One command emits the complete skeleton manifest; every volume has
source, authority, owner and audit policy; no silent placeholder remains.

### WP2 — global body mathematical core

#### Tasks

1. Implement log-space `C2` body laws.
2. Implement asymmetric sections and analytical area.
3. Implement single-maximum, anti-box and anti-neck constraints.
4. Implement adaptive surface containment.
5. Implement nose cap, camera aperture and FOV audit.
6. Generate deterministic longitudinal/section diagnostic plots.

#### Definition of done

The rejected Revision 2 body fails the new gates; at least one new
body passes packaging and mathematical fairness without using the wing blend to hide a
neck.

### WP3 — released wing reconstruction and blend

#### Tasks

1. Reconstruct the exact root wing from released DAT sections.
2. Implement the bounded quintic transition surface.
3. Audit position, normal and curvature continuity.
4. Compute union area, volume and overlap ownership.
5. Add root structural thickness and spar/joiner constraints.

#### Definition of done

One analytical body-wing surface is watertight and resolution
converged; the junction has no visible or computed kink and no double-counted mass.

### WP4 — multidisciplinary feasible set

#### Tasks

1. Generate seeded design populations.
2. Reject infeasible candidates before merit evaluation.
3. Compute Pareto fronts for area, mass, fairness, structure, service and thermal proxies.
4. Propagate dimensional/mass uncertainty and adverse cases.
5. Retain multiple families if evidence cannot separate them.

#### Definition of done

Deterministic manifest, reproducible hashes and a nondominated set
with complete residuals; no winner selected by an undocumented weighted score.

### WP5 — coupled aircraft closure

#### Tasks

1. Return net material mass properties to the ledger.
2. Iterate geometry, battery, CG, NP and trim for CLEAN and V1.
3. Update yaw/side-area and propulsion-interaction models.
4. Run low-order and viscous aerodynamic hierarchy.
5. Reject candidates failing either configuration.

#### Definition of done

Coupled convergence demonstrated without clamping; selected
candidate meets static-margin, trim, mass, stall, yaw and propulsion boundaries with
uncertainty stated.

### WP6 — exact CAD and print definition

#### Tasks

1. Reproduce the analytical OML in the approved B-rep backend.
2. Generate exact offsets, openings, ribs, reinforcements, joints and segments.
3. Demonstrate analytical-to-CAD deviation within the released tolerance.
4. Produce assembly/service and manufacturing drawings.
5. Print fit articles and structural/thermal coupons.

#### Definition of done

Native CAD, drawings, mass properties and print process agree;
F2/S3 physical evidence exists. Only then may `[I]` geometry be promoted.

### WP7 — flight validation and release

#### Tasks

1. Complete E2 glide/drag/stall/trim testing.
2. Complete E8 yaw-response identification for CLEAN/V1.
3. Reconcile model-to-test discrepancies.
4. Publish the configuration and manufacturing release ADR.

#### Definition of done

Measured evidence satisfies the acceptance matrix and the warning
can be removed by an explicit release decision, never automatically.

---

## 10. Deliverables and repository contract

Every run shall produce deterministic, ASCII-safe machine data and review artifacts:

```text
geometry/fuselage/candidates/<candidate-id>/
    design-vector.json
    skeleton-residuals.json
    geometry-metrics.json
    aircraft-state-clean.json
    aircraft-state-v1.json
    body-review.obj
    body-wing-review.obj
    section-schedule.csv
    rejection-or-merit.json

geometry/fuselage/selected/
    selection-manifest.json
    selected-review.obj

geometry/drawings/
    SLM-FUS-001-fuselage-oml-review.svg
    SLM-GA-001-general-arrangement.svg
    SLM-GA-002-side-elevations.svg
```

The selection manifest shall include source hashes, design vector, solver seed, mesh
resolution, every hard residual, every objective, uncertainty case, configuration status,
software version and explicit authority warning. Timestamps shall not enter content hashes.

---

## 11. Current numerical anchors and open blockers

These values initialize the programme but do not validate a surface:

| Quantity | Current value | Authority/use |
|---|---:|---|
| VLM neutral point | approximately `−75.8 mm` | `[D]`, first coupled iteration |
| Target CG | approximately `−93.8 mm` | `[D]`, 8 % MAC static margin |
| CLEAN component-level battery x | `−337.74 mm` | `[D]/[E]` |
| V1 exact required battery x | `−375.48 mm` | `[D]/[E]`, 4.28 mm outside current stop after corrected fin mass centres |
| V1 forward battery stop | `−371.20 mm` | `[D]/[E]` |
| Camera lens plane | `−452.70 mm` | `[D]`, aperture datum—not full nose plane |
| Prior aft pod extent | approximately `+265 mm` | `[I]`, must be re-solved |
| Unlocated reserve mass | `92.88 g` | open hard blocker |
| Rejected gross 0.9 mm body screen | `180.9 g` | diagnostic only; cannot enter ledger |

The previous body length, width, wetted area and volume describe only the rejected
regression fixture. They are not target dimensions.

---

## 12. Risk register and mandatory falsifiers

The concept shall be changed or rejected if:

- the required payload cannot be enclosed without a packaging-shaped external body;
- the body-inclusive NP/trim cannot close inside real battery travel;
- root integration produces unacceptable separation or exceeds the propulsion drag
  boundary;
- the required structure, openings and joints exceed the mass/stall allocation;
- the camera, pitot, antennas or cooling system cannot function without destructive
  surface discontinuities;
- the printed material/process cannot support the assumed load path;
- service access requires weak or inaccessible seams;
- CLEAN and V1 cannot share the primary body without unacceptable compromise;
- a simpler modular pod is demonstrably lighter, safer and aerodynamically equivalent.

Desired appearance is a legitimate design objective, but it cannot override a falsifier.

---

## 13. Evidence base and transfer limits

The plan is reinforced by seven focused research lines. Each source informs method or
risk; none directly supplies Salamandra dimensions.

1. **Fineness and pressure recovery.** NACA/NASA results show that fuselage drag cannot be
   selected from one universal fineness ratio; location of maximum area and recovery
   matter. [NACA TN-614](https://ntrs.nasa.gov/citations/19930081378),
   [NASA general-aviation drag workshop](https://ntrs.nasa.gov/citations/19760003915).
2. **Wing-body junction flow.** Junction separation is three-dimensional and fillet
   performance is not proven by visual smoothness.
   [NASA juncture-flow experiments](https://ntrs.nasa.gov/citations/19890009287),
   [NASA Juncture Flow programme](https://ntrs.nasa.gov/citations/20160007544),
   [automatic intersection/fillet method](https://ntrs.nasa.gov/citations/19930013298).
3. **Parametric surfaces.** CST and OpenVSP support compact section-based representation,
   but fitting accuracy and cross-section choices require independent validation.
   [NASA 3-D CST](https://ntrs.nasa.gov/citations/20160006023),
   [OpenVSP fuselages](https://www.nasa.gov/reference/openvsp-fuselages/),
   [OpenVSP cross-sections](https://www.nasa.gov/reference/openvsp-cross-sections/),
   [improved CST limitations](https://ntrs.nasa.gov/citations/20250003963).
4. **Integrated centerbodies.** Hybrid/blended-wing-body studies demonstrate that
   packaging, lifting surface and body aerodynamics must be solved together.
   [integrated HWB design](https://ntrs.nasa.gov/citations/20170008006),
   [HWB parameterization with packaging constraints](https://ntrs.nasa.gov/citations/20170001410),
   [low-speed HWB investigation](https://ntrs.nasa.gov/citations/20150000554).
5. **Low-order model limits.** VSPAERO and parasite-drag tools are useful for trends but do
   not close viscous junction or powered-installation drag.
   [VSPAERO capability evaluation](https://ntrs.nasa.gov/citations/20210017397),
   [OpenVSP Parasite Drag Tool](https://www.nasa.gov/reference/openvsp-parasite-drag-tool/).
6. **Non-circular structure and printed anisotropy.** A non-circular shell changes load
   paths, and PETG behaviour depends on filament/layer arrangement.
   [NASA non-circular fuselage structural concepts](https://ntrs.nasa.gov/citations/20040110967),
   [PETG layer-arrangement study](https://www.mdpi.com/2504-4494/8/6/295).
7. **Cooling openings.** Inlet and exit geometry are aerodynamic components and must be
   analysed with the external body.
   [NACA/NASA cooling inlet and exit study](https://ntrs.nasa.gov/citations/19980214918).

Photographic references contribute only the qualitative grammar in §1.1 because
perspective, unknown scale and unknown internal construction prohibit dimensional
reverse engineering.

---

## 14. Reproduction and completion commands

During implementation, the minimum local campaign is:

```bash
python calculations/fuselage_contract.py
python calculations/fuselage_geometry.py
python calculations/fuselage_trade.py --check
python calculations/generate_blueprints.py
python calculations/generate_blueprints.py --check
python calculations/contract_lint.py
python calculations/mutation_test.py
python calculations/verify_calculations.py --all-scripts
git diff --check
```

Commands naming not-yet-created modules are required target interfaces. A work package is
not complete merely because its code runs: its definition of done, mutation coverage,
generated artifact review and downstream coupled gates must also pass.

---

## 15. Final plan rule

The next fuselage shall not be drawn and then justified. It shall emerge from a global,
constrained and reproducible mathematical model whose failure modes are tested explicitly.

The shape hierarchy is mandatory:

```text
hard physical skeleton
        < global smooth body
        < controlled wing-body union
        < coupled aircraft feasibility
        < printable structural solid
        < physical release
```

No layer may be skipped, and no attractive render may be used as evidence that a later
layer has passed.
