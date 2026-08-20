# NF Design Guide 2024 — Salamandra Repository Audit

**Part 1: full-book triage, configuration risk and release disposition**
**Audit date:** 20 August 2026  
**Aircraft:** Salamandra Article #1, CLEAN and V1 configurations  
**Repository baseline:** README revision 1.20, release v0.6.0, design guide v0.24  
**Auditor role:** senior aircraft configuration, stability and aeroelasticity review

## 1. Disposition

**Salamandra is a rigorous and unusually transparent preliminary design study. It is not
yet a manufacturing-authoritative aircraft definition and is not ready for first flight.**

The repository's strongest product is its traceable reasoning: numerical ownership,
confidence tags, alternative records, deterministic calculations and an explicit gap
register. The software contract passes. That proves internal numerical consistency; it
does not validate the physical assumptions.

The current release should retain the following disposition:

| Item | Disposition | Reason |
|---|---|---|
| Analytical design review | **Proceed** | The design intent, equations and uncertainty declarations are reviewable. |
| Configuration selection | **Reopen at architecture level** | The −15° forward-sweep choice is only optimal inside a narrowly fixed planform/airfoil/control trade. |
| Manufacturing release | **Hold** | There is no manufacturing-authoritative native CAD, STEP, 3MF or STL set; all six released sheets state “not for manufacture.” |
| Ground structural/aeroelastic test | **Proceed after representative parts exist** | These tests are the fastest route to replacing the dominant `[E]` inputs. |
| First flight | **Hold** | Directional stability, printed-section aerodynamics, body-inclusive neutral point, structural stiffness and flutter are physically open. |
| Published 160 km/h article `V_NE` | **Not substantiated** | The current conservative divergence estimate is 129.59 km/h and flutter speed has not been calculated or measured. |

This is not a rejection of the concept. It is a statement about maturity and evidence.

## 2. Audit source, scope and method

The reviewed source is [NF Design guide 2024 english.pdf](../INSPIRATION/NF%20Design%20guide%202024%20english.pdf),
331 PDF pages, 23,686,056 bytes, SHA-256:

```text
a0e81c98b884c7a9c29f75a9bd7ccdf19ff2255642ba2ac5bdd4337696daabca
```

The PDF cover identifies the work as Peter Wick's *Designing Flying Wings — An update
book therefore incomplete*. Page references in this audit are PDF page numbers, including
the cover and contents pages.

The book was read in one indexing pass over all 331 pages and then in a focused second
pass over the sections relevant to Article #1. The repository comparison included the
README, concise and advanced design guides, open points, gaps, tests, ADRs, research
threads, drawings, airfoil coordinates and calculation sources. The complete deterministic
verification suite was also run successfully on the audited baseline.

The numerical evidence in this document is reproduced by
[`calculations/nf_design_guide_audit.py`](../calculations/nf_design_guide_audit.py):

```bash
python3 -m pip install -r calculations/requirements.txt
python3 calculations/nf_design_guide_audit.py
```

The book is an expert RC flying-wing design guide, not a certification specification.
Many recommendations are experience-based and some are explicitly presented by the author
as unresolved. They are used here as design-review prompts, not imported as requirements
without a Salamandra-specific calculation or test.

### 2.1 Part structure

This living audit began as a four-part release review and now continues with focused
technical deep dives:

1. **This part — full-book triage and critical disposition:** configuration, airfoil
   moment, directional stability, aeroelasticity, manufacturing maturity and test safety.
2. [**Part 2 — Airfoil, trim and longitudinal control**](NF-Design-Guide-2024-Repository-Audit-Part-02-Airfoil-Trim.md):
   detailed `Cm(CL, Re, transition, geometry)`, neutral-point uncertainty, inertia,
   elevon scheduling and stall progression.
3. [**Part 3 — Lateral-directional stability and operations**](NF-Design-Guide-2024-Repository-Audit-Part-03-Directional-Stability.md):
   finite sideslip, adverse yaw, fin section behavior, body integration, stall, launch,
   landing and flight-test identification.
4. [**Part 4 — Printed structure and release closure**](NF-Design-Guide-2024-Repository-Audit-Part-04-Structure-Aeroelasticity.md):
   load paths, joints, ground vibration test, flutter model, proof-test articles,
   CAD/manufacturing data and final closure matrix.
5. [**Part 5 — Wingtips, drag, stall and flap management**](NF-Design-Guide-2024-Repository-Audit-Part-05-Wingtips-Drag-Flaps.md):
   winglet crossover, forward-swept yaw-arm geometry, outer-wing lift reserve,
   junction/low-Reynolds-number behavior and multi-state control scheduling.
6. [**Part 6 — Design-method synthesis**](NF-Design-Guide-2024-Repository-Audit-Part-06-Design-Method-Synthesis.md):
   airfoil geometry and optimization, swept-section interpretation, state-dependent
   spanloads, static margin, active stability and flap-chord closure.

Part 1 includes a complete guide coverage map so later parts can deepen the analysis
without losing whole-book context.

## 3. Configuration reconstructed from the repository

| Parameter | Current Article #1 value | Audit note |
|---|---:|---|
| Span / area / aspect ratio | 1.300 m / 0.282 m² / 6.0 | Compact, low-AR powered model; unlike most high-AR composite glider examples in the book. |
| Taper | 0.50 | Root/tip chords 289.231/144.615 mm. |
| Sweep | `Lambda_LE = −11.987°`, `Lambda_c/4 = −15.000°`, `Lambda_TE = −23.500°` | Forward sweep is substantial at every reference line; the tip does not recover aft sweep. |
| Airfoil family | Salamandra r1, MH60 mean line, 13.5/9.0% t/c, +1.0/+0.5° reflex | Sharp-edge CAD coordinates; printed geometry is unmeasured. |
| Twist | +3.0° linear wash-in | At the declared structural/trim cap. |
| Elevons | 28% chord, 35–90% half-span | Well aligned with the guide's broad 15–40% useful chord range. |
| Static margin / CG | 8% MAC / `x = −93.8 ±5 mm` | Body and flight neutral-point closure remain open. |
| CLEAN / V1 mass | 1553.25 / 1601.98 g lower model | V1 allocation is 1613.25 g. |
| Stall requirement | no more than 45 km/h | Exact mass ceiling is 1620.40 g at the current estimated `CLmax = 0.589`. |
| Speed declarations | 105 initial / 160 article `V_NE` / 180 structural case | These roles are separated correctly in code, but the physical aeroelastic basis is not closed. |
| Directional variants | CLEAN finless; V1 two fixed fins | V1 has no movable rudder; both variants use two elevon servos. |
| Primary material | 0.9 mm two-perimeter PETG skin, 5% gyroid | Material, process and representative structural properties are not yet measured. |

## 4. What the repository already does well

### 4.1 Configuration control and traceability

The single numerical contract in `design_config.py`, generated airfoil stations, ADRs,
research threads and confidence labels are stronger than the normal documentation level
for an open-source model aircraft. The repository often distinguishes measured `[M]`,
derived `[D]`, estimated `[E]` and inferred `[I]` information correctly.

This directly supports the guide's most important methodological warning: flying-wing
variables are strongly coupled and apparently small changes cannot safely be transferred
between designs (NF Guide, PDF pp. 7–11).

### 4.2 Reproducible coupled calculations

Mass, CG, packaging, neutral point, trim, propulsion, yaw, loads and divergence share
common inputs. The complete deterministic verification passes, including the mutation and
contract-lint protections. This is a real strength.

The limitation is equally important: agreement between two codes using related potential-
flow assumptions is a model cross-check, not independent physical validation. A passing
test suite cannot close airfoil, body, material, joint or aeroelastic uncertainty.

### 4.3 Honest gap reporting

The repository does not hide the fact that measured printed-section polars, complete-wing
stiffness, absolute divergence, flutter, body-inclusive neutral point, yaw stability and
gust response are open. The gap register currently has **no closed gaps**. That honesty
prevents numerical maturity from being mistaken for aircraft maturity.

### 4.4 Several design choices align with the guide

- The 28% elevon chord lies near the guide's broad 25% optimum and inside its 15–40%
  effective range at model Reynolds numbers (PDF pp. 68–70).
- The airfoil family changes thickness and reflex with span and is evaluated at root and
  tip Reynolds numbers, rather than assuming one rigid section for the entire wing.
- Mass-balanced elevons, limited hinge free play, a closed leading structure and explicit
  joint stiffness are recognized as aeroelastic requirements.
- The design recognizes the long forward battery/boom installation as a coupled mass,
  balance, drag and yaw problem.
- The CLEAN/V1 split exposes the real efficiency-versus-directional-stability trade instead
  of silently adding fin area.

## 5. Critical findings

Priority definitions are: **P0** blocks manufacturing or safe first flight; **P1** blocks
credible performance/envelope validation; **P2** is a configuration-control or development
quality weakness.

| ID | Priority | Finding | Evidence and consequence | Required closure |
|---|---|---|---|---|
| NF-01 | **P0** | No manufacturing-authoritative aircraft definition exists. | `cad/` and `stl/` contain only placeholders. The generated body OBJ is provisional and the drawings state “not for manufacture.” Geometry, interfaces and load paths therefore cannot be inspected as one released assembly. | Native parametric assembly, STEP review export, part drawings/3MF, material/process specifications, mass-properties report and closed deviation register. |
| NF-02 | **P0** | The flutter model does not address the principal swept-wing body-freedom mechanism. | `I-05` lists approximately 25/106/82 Hz bending/torsion/elevon frequencies without a reproducible owner and concludes classic bending–torsion flutter is not critical. The guide instead identifies bending–pitch/body-freedom coupling, stiffness-to-mass ratio, joint softness and sweep-induced bending/twist as central (PDF pp. 248–249 and 303–308). | Full-aircraft GVT, correlated structural model and a coupled unsteady aeroelastic speed analysis including wing bending, pitch, torsion, elevon and fin modes. |
| NF-03 | **P0** | The written E7 flight schedule violates the repository's own speed clearance. | E7 proposes 90, 110, 130 and 150 km/h. The released initial cap is 105 km/h; calculated conservative divergence is 129.59 km/h. The 130 and 150 km/h points approach or exceed the current conservative prediction. | Withdraw the schedule. Use ground stiffness/GVT correlation first, then a formally reviewed incremental expansion that never exceeds the active clearance. |
| NF-04 | **P0** | V1 directional stability is not robust at the unfavorable uncertainty corner. | Current model gives `Cn_beta = −0.0002899…+0.0011915 /deg`; the lower corner remains divergent. Fin `Re_MAC` is only 108k at 45 km/h and 228k at cruise, while its 1.76–1.95% thick section has no measured or computed finite-yaw polar. The guide warns that small fins can tumble after a slightly yawed launch and stresses separate static and dynamic sizing (PDF pp. 98–108). | Define the fin section, measure/model its low-Re side-force curve and deadband, include the final body, and make the lower-bound static and dynamic result acceptable before launch. |
| NF-05 | **P0** | Printed-airfoil pitching moment and stall evidence are inadequate for a tailless release. | The CAD polar uses a zero-thickness trailing edge and Ncrit 10–12 calibrated mainly against E387 drag. A printable 0.45 mm edge is already 0.156% root chord and 0.311% tip chord. Existing sharp-edge tip `Cm0` changes by 0.0291 between Ncrit 10 and 12 at Re 120k. The guide specifically warns that low-Re laminar bubbles can corrupt XFOIL moment (PDF pp. 12–23). | Scan representative printed sections; rerun moment-specific sensitivity on measured contours and transition cases; then close E2 with measured complete-aircraft/section evidence. |
| NF-06 | **P0** | Mass and balance uncertainty consume the remaining aerodynamic margin. | The 45 km/h mass ceiling is 1620.40 g. Margin is 18.42 g against the V1 lower model and only 7.15 g against its allocation. The CLEAN layout still contains 92.88 g of unresolved reserve mass, and one-sigma longitudinal CG uncertainty is 7.81 mm against a ±5 mm half-band. | Replace allowances with weighed parts, measured installed stations and an article-level CG test. Do not release the 45 km/h claim from an estimated `CLmax`. |
| NF-07 | **P1** | The −15° forward-sweep decision is conditional, not architecture-optimal. | ADR-0040 fixes span, area, taper, airfoil and control concept and samples only −20/−16/−15/−12/−10°. It therefore selects the least-negative sweep that closes constraints created partly by those fixed choices. The guide advises against large forward sweep and its example Amokka 202 uses only slight forward sweep with aft-recovering tips (PDF pp. 136–142). | Run an equal-requirements architecture trade including slight/zero sweep, different reflex/control allocation, aft-recovering tips and a conventional-tail reference. |
| NF-08 | **P1** | The stall screen is symmetric and infinitesimal where the guide demands finite sideslip/control assessment. | The current VLM screen reports a peak section `Cl` near 59.5% semispan, but does not model as-printed section `CLmax`, sideslip, differential-elevon commands or stall location relative to CG. The guide emphasizes outer-wing lift reserve and a stall location that produces recovery (PDF pp. 308–310). | Build a matrix over speed, sideslip, elevator/aileron mix, surface roughness and section `CLmax`; verify separation progression experimentally. |
| NF-09 | **P1** | Body/wing/fin aerodynamic integration is unresolved. | The long nose is required by the forward CG, while its OML and projected side area remain `[I]`. The guide notes that forward body area is yaw-destabilizing and that a long nose increases drag, pitch inertia and trim demand (PDF pp. 93–97 and 138–140). | Freeze a feasible body around real equipment, include it in RANS or validated low-order aerodynamic increments, and update NP, `Cm`, `Cn_beta`, drag and inertia together. |
| NF-10 | **P1** | The yaw test input conflates adverse-yaw control coupling with free directional dynamics. | E8 uses an aileron impulse as a rudder-kick analogue. On a flying wing, the elevon command itself changes roll and yaw moments; the guide treats yaw from control deflection separately from passive directional stability. | Identify a coupled MIMO model or explicitly separate the forced command interval from the free ring-down; estimate `Cn_delta_a`, `Cl_delta_a`, `Cn_beta` and damping rather than only one decay trace. |
| NF-11 | **P1** | Printed joints and control-system stiffness are represented by assumptions, not assembly measurements. | The guide emphasizes swept-spar load redirection, soft joints and play-free control systems (PDF pp. 246–249, 303–308). Repository joint factors, hinge stiffness and shell properties remain estimated. | Test representative joints, hinge lines, servo mounts and a full semispan for stiffness, free play, hysteresis and proof load before flight. |
| NF-12 | **P1** | There is no released first-flight control and abort card. | Mechanical travel is defined, but final throws, mixing, rate/attenuation schedule, launch yaw contingency and test points are open. The guide recommends a deliberate launch and progressive CG/control evaluation (PDF pp. 151–153). | Release configuration-specific control limits, preflight inspections, launch criteria, abort triggers, telemetry and an incremental envelope card. |
| NF-13 | **P2** | Primary document control contains stale contradictions. | Design guide v0.24 says to start from the “v0.23 baseline,” retains a “known V1 cradle-travel conflict” now reported closed, and points current release rules to v0.5. ADR-0040 also reports a superseded V1 lower mass. The gap register carries fin mass/drag figures inconsistent with the current numerical owner. | Run a document-authority audit and make generated release facts replace copied prose where practical. |
| NF-14 | **P2** | The airfoil loft-section reference plane is not explicit. | The guide identifies the unresolved choice between a section normal to the quarter-chord line and a flight-direction section at sweep of approximately 15° (PDF pp. 321–323). Repository loft instructions define span stations but not this convention. The simple cosine projection difference at 15° is 3.41–3.53%, large enough to alter chord, thickness and Reynolds interpretation. | Declare the master section plane, transform imported coordinates consistently, and run both conventions as an aerodynamic/geometric sensitivity before production CAD. |

## 6. Detailed engineering comparison

### 6.1 Tool fidelity: useful answers require physical calibration

The guide repeatedly states that panel codes, XFOIL and CFD are imperfect empirical tools
whose results must be judged against practice. It also warns that panel distribution and
mesh choices can change the answer (PDF pp. 9–11).

Salamandra responds well to this lesson in software terms: canonical meshes are declared,
VLM convergence is checked and Weissinger-L supplies a structurally different lifting-line
comparison. The two neutral-point results differ by 2.9 mm, which the repository retains as
uncertainty rather than averaging away.

The remaining weakness is physical independence. Both methods are inviscid, omit the final
body and do not establish Reynolds-dependent pitch stability. The 2.9 mm spread is already
58% of the ±5 mm CG band; the body and viscous corrections could be comparable or larger.
The correct conclusion is therefore “computationally bounded,” not “neutral point closed.”

### 6.2 The “fluent airfoil” is a direct Salamandra risk

The book's “fluent airfoil” concept is especially relevant: at model Reynolds numbers, a
laminar separation bubble changes the aerodynamically effective camber, zero-lift angle and
pitching moment even when the solid contour is unchanged (PDF pp. 12–23).

Article #1 operates exactly in that sensitive range:

| Condition | Root Re | Tip Re |
|---|---:|---:|
| 45 km/h | 241,026 | 120,513 |
| 95 km/h | 508,832 | 254,416 |

The existing sharp-edge XFOIL results themselves demonstrate transition sensitivity:

| Station / condition | fitted `Cm0`, Ncrit 10 | fitted `Cm0`, Ncrit 12 | Change |
|---|---:|---:|---:|
| Root, Re 240k | +0.00910 | +0.00292 | −0.00618 |
| Root, Re 510k | +0.01602 | +0.01689 | +0.00087 |
| Tip, Re 120k | −0.04780 | −0.07687 | **−0.02907** |
| Tip, Re 255k | −0.01646 | −0.02077 | −0.00430 |

These values are computational screens, not measurements. Their message is the
sensitivity, not which Ncrit is “correct.”

The guide recommends testing XFOIL moments with a finite 0.1%-chord trailing edge,
evaluating moment near 4–5° angle of attack, trying Ncrit near 6 and optionally tripping
the lower surface near 95% chord (PDF pp. 20–23). Salamandra should **not** replace its
drag-calibrated Ncrit 10–12 band with Ncrit 6 by assertion. It should maintain two explicit
uses:

- a drag-calibrated transition band for performance prediction; and
- a moment-specific sensitivity matrix over Ncrit, trips and the measured printed contour.

The printed contour matters. One declared 0.45 mm extrusion line corresponds to 0.156%
root chord and 0.311% tip chord, already larger than the guide's molded-aircraft 0.1%
example. Actual trailing-edge thickness, waviness, hinge gap and surface roughness must be
measured on representative coupons and propagated into trim and stall predictions.

### 6.3 Static margin cannot be separated from pitch inertia and control precision

The guide relates trim deflection to static margin and flap span, warns that the real
neutral point can move with Reynolds number and control deflection, and discusses pitch
inertia as a contributor to the minimum flyable margin (PDF pp. 48–64). It gives typical
experience ranges rather than a universal rule.

Salamandra's 8% static margin falls inside the guide's broad swept-wing experience range,
but this does not validate it. The repository calculates a three-dimensional inertia
tensor, yet that inertia is not used in a longitudinal dynamic-stability and control-
robustness analysis. The current closure is almost entirely static.

Part 2 should therefore calculate a longitudinal state-space model across the mass/CG/Re
envelope, include actuator delay and airspeed-sensor uncertainty, and test how much neutral-
point shift or `Cm` error can be tolerated before the controller or pilot runs out of trim
and pitch damping.

### 6.4 The elevon geometry is plausible; its operating map is incomplete

The 28%-chord elevon agrees well with the guide's broad optimum. The repository also
improves on a simple handbook rule by solving the actual spanwise surface geometry and
connected mass consequences.

What remains open is finite deflection. The guide notes that moment effectiveness is
approximately linear only through a limited deflection range and deteriorates at large
angles (PDF pp. 68–70). Salamandra presently uses idealized flap effectiveness for key
trim/authority results and has no released final flight throws or mix schedule.

Required follow-up includes low-Re hinge-gap sensitivity, nonlinear `Cm_delta`, servo and
linkage compliance under load, differential-elevon adverse yaw and a scheduled control
allocation versus airspeed.

### 6.5 Forward sweep is not a free root-stall guarantee

The guide identifies real advantages of slight forward sweep: higher root Reynolds number,
useful root pitching moment, inward-shifted separation, low tip mass and potentially small
torsional load when the quarter-chord line is nearly straight (PDF pp. 136–140).

It also gives direct warnings: forward CG drives a long nose, forward side area demands
more fin, pitch inertia grows, braking/control arrangements become difficult, directional
stability deteriorates and aeroelastic problems intensify. It advises against large
forward-sweep angles (PDF p. 140).

Salamandra does not have a nearly straight quarter-chord: it is −15°. Its trailing edge is
even more forward swept at −23.50°, while the guide's Amokka 202 example has only slight
forward sweep and recovers useful geometry through taper. Thus, the book does not validate
Article #1 by similarity; it establishes a warning case.

ADR-0040 is a competent optimization of one fixed architecture, but it is not an
architecture trade. Near-zero sweep, slight sweep, aft-recovering tips, a different
root/tip moment distribution or a conventional tail could change the trim constraint that
currently rejects −12° and −10°. Those alternatives must be evaluated at equal mission,
mass, propulsion, control and manufacturability requirements before forward sweep is called
irreversible or high-confidence.

### 6.6 Directional stability must be safe at launch, not merely nominal at cruise

The guide separates fin static effectiveness, damping, lift distribution, finite-yaw stall
and launch behavior. Its flight experience warns that an aircraft with too little fin can
tumble when launched with only a small yaw angle (PDF pp. 98–108). This maps directly to
Salamandra because forward sweep and the long forward body are both yaw-destabilizing.

The current V1a nominal target is not robust:

| V1a quantity | Current result |
|---|---:|
| Total fin area | 6.144 dm² |
| One-fin span / MAC | 247.9 / 129.9 mm |
| `Re_MAC`, 45 / 95 km/h | 108k / 228k |
| Root / tip relative thickness | 1.755 / 1.950% |
| `Cn_beta` band | **−0.0002899…+0.0011915 /deg** |
| Estimated fin-system `Delta CD0` | +0.00337 (`Cf = 0.00573` input) |

The very thin symmetric/biconvex section can have a low-Re deadband, early separation or
surface-finish sensitivity not represented by a Helmbold lift-slope factor. A linear
small-angle area calculation cannot demonstrate recovery from a yawed hand launch.

Before flight, the final body/fin installation needs section polars or a conservative
physical test, finite-yaw force/moment sweeps, a launch-condition simulation and a
positive lower-bound stability result. Dynamic damping must be assessed independently;
increasing area until nominal `Cn_beta` is positive is not sufficient.

### 6.7 The body is part of the aircraft, not packaging wrapped around an approved wing

The guide recommends locating maximum fuselage thickness forward, avoiding constrictions
and minimizing forward side area because it destabilizes yaw (PDF pp. 93–97). It further
connects a long nose to drag, pitch inertia, vertical-tail demand and negative pitch moment
(PDF pp. 138–140).

The repository recognizes most of these couplings but cannot close them while the OML is
`[I]`. The provisional generated body is useful for envelope discovery; it cannot be used
to approve NP, trim, drag or yaw. A body-free wing analysis plus an empirical body band is
not enough when the body exists specifically because the forward-sweep balance solution
requires a 321 mm-class forward support.

### 6.8 Swept-wing flutter is a stiffness-to-mass and coupling problem

The most consequential lesson in the book is that strength alone does not prevent
swept-wing flutter. Bending of a swept wing produces geometric twist; body pitch, wing
bending, control surfaces, fins, joints and concentrated masses can couple. The relevant
design variable is often stiffness divided by mass, not just torsional stiffness or static
strength (PDF pp. 248–249 and 303–308).

The guide cites 15–20° sweep as a particularly sensitive coupling region in its example
discussion (PDF p. 305). Salamandra is at −15°. The direction is reversed, but the
geometric bending/twist coupling does not disappear; its sign and modal consequence must
be calculated for this structure.

The current `I-05` conclusion is not supportable as a flutter clearance because:

1. the quoted bending, torsion and elevon frequencies have no reproducible calculation or
   measured modal source;
2. frequency separation alone is not a stability solution;
3. body-freedom and fin modes are absent;
4. aerodynamic damping and unsteady generalized forces are absent;
5. soft removable joints and control-system free play are only estimated; and
6. E5 proposes learning from the first flight, after the aircraft has already entered the
   risk environment.

The correct order is representative-property testing, full-assembly GVT, model
correlation, coupled flutter analysis, ground control-system checks and only then flight
envelope expansion. Southwell extrapolation can help estimate static divergence after
these steps, but it does not clear flutter.

### 6.9 Stall location must be tested in sideslip and with control commands

The guide emphasizes outer-wing lift reserve and recommends arranging stall so that the
resulting aerodynamic change promotes recovery rather than deeper stall (PDF pp. 308–310).
It also shows that winglet/vertical-surface interaction can load the outer wing in sideslip.

Salamandra's current stall screen is a useful symmetric, attached-flow VLM diagnostic. It
does not prove root-first separation or retained elevon authority. At minimum, the next
analysis must vary:

- measured root-to-tip `CLmax` and roughness;
- sideslip amplitude and sign;
- elevator and differential-aileron deflection;
- propeller on/off state;
- body and fin interference; and
- geometric/elastic twist tolerance.

The result should report not just peak section `Cl`, but the predicted separation sequence,
its position relative to CG, pitch/yaw consequence and control authority remaining after
the first section separates.

### 6.10 Maiden-flight advice must become an engineering test card

The guide's maiden section stresses accurate CG, a decisive launch, precise play-free
servos and progressive adjustment rather than adding arbitrary nose ballast (PDF pp.
151–153). Salamandra's test program contains several good ingredients—pitot, blackbox,
configuration recording and conservative initial speed—but is not yet a safe executable
card.

The card must define article identity, measured mass/CG, configuration, software hash,
control directions, throws, rates, mix, launch method, wind/yaw limits, telemetry, abort
criteria and point-by-point envelope expansion. CLEAN and V1 need separate cards. No test
point may exceed the currently active structural/aeroelastic clearance merely because it
is intended to measure that clearance.

### 6.11 The airfoil section-plane convention must be controlled

The guide closes with an unresolved swept-wing airfoil question: at sweep near and above
15°, should a two-dimensional section be defined normal to the quarter-chord line or in a
plane aligned with the flight direction (PDF pp. 321–323)? Near-wall streamlines need not
follow either simple direction, so this is not resolved by geometry alone.

Salamandra is exactly at 15° quarter-chord sweep. Its loft instructions specify constant-y
stations but do not state whether the imported airfoil coordinates are authoritative in
those planes or normal to the quarter-chord. The elementary projection difference is
`1 − cos(15°) = 3.407%`, or `sec(15°) − 1 = 3.528%` under the reciprocal convention.
That is not automatically a 3.5% aerodynamic error, but it is large enough that the CAD
definition and the Reynolds/section analysis must use one declared interpretation.

## 7. Full-guide learning map

| NF Guide pages | Subject | Salamandra lesson | Current repository response |
|---|---|---|---|
| 7–11 | Reading method and analysis programs | Treat the aircraft as a coupled system; validate numerical tools against practice and disclose mesh sensitivity. | **Strong computationally; physical validation open.** |
| 12–23 | Reynolds-dependent “fluent airfoil” and XFOIL moment | `Cm`, zero-lift angle and bubble behavior must be tested on realistic trailing edges and transition conditions. | **Critical open issue NF-05/G2.** |
| 31–67 | Plank airfoils, trim and static margin | Airfoil, flap, static margin, inertia and real NP cannot be selected independently. | **Partial; static model strong, dynamics/body/measurement open.** |
| 68–77 | Flap geometry and yaw/brake functions | 28% elevon chord is credible; nonlinear effectiveness, adverse yaw and braking/landing concept remain. | **Good geometry, incomplete operating map.** |
| 78–108 | Fuselage and vertical tail | Forward body area destabilizes yaw; fin static and dynamic functions differ; launch yaw can be critical. | **Critical open issue NF-04/NF-09.** |
| 109–120 | Structure and slight sweep | Spar position, mass inertia, D-box and aft structure interact; FSW reverses roll/yaw effects. | **Conceptually recognized; test evidence absent.** |
| 121–142 | Slight forward sweep | Slight FSW has useful aerodynamic benefits but excessive sweep brings flap, stall, yaw and aeroelastic penalties. | **Architecture trade incomplete.** |
| 143–153 | BWB and maiden | Central body affects aerodynamics; first flight needs precise CG, control and launch discipline. | **Body and flight card open.** |
| 154–245 | Pure swept wings, lift distribution and control | Passive yaw stability, adverse yaw, control-induced yaw and stall behavior are separate design tasks. | **Current reduced yaw model does not separate all derivatives.** |
| 246–269 | Swept-wing construction | Spars, joiners, hinge gaps and removable joints can govern stiffness and flutter. | **Estimated; no representative assembly measurements.** |
| 270–302 | Winglets and directional devices | Fin/wing interaction must be checked at finite yaw and outer-wing lift reserve must remain. | **V1 sizing is small-angle only.** |
| 303–316 | Swept-wing flutter and design synthesis | Body-freedom flutter, bending stiffness-to-mass, modal mass placement and soft joints dominate. | **Current flutter scope is inadequate.** |
| 317–331 | Future airfoils, transition, stabilization and sweep questions | Optimization only optimizes its model; flight data and section-axis conventions remain research questions. | **Relevant at exactly 15° sweep; sensitivity not yet run.** |

## 8. Transfer limits: what should not be copied from the book

The following limitations prevent uncritical rule transfer:

- Most examples are unpowered composite or molded gliders with aspect ratios and surface
  finishes unlike a powered PETG AR-6 print.
- The guide's 0.1%-chord trailing-edge example describes molded construction; Salamandra's
  extrusion process may impose a larger and rougher edge.
- The guide's static-margin values are experience ranges, not stability requirements for
  an INAV-controlled aircraft with this inertia and sensor installation.
- Its statements about reduced flutter sensitivity beyond approximately 25° sweep are
  explicitly experience-based and lack a systematic general study; they are not a reason
  to increase Salamandra sweep.
- The Amokka and Horten examples use different lift distributions, taper, twist, controls,
  airfoils, fins and missions. Similarity of outline does not validate performance or
  stability.
- The source itself calls the work incomplete. Its best use is to expose interactions and
  failure modes that the repository must calculate or test.

## 9. Required release programme

### Gate A — configuration and authority

1. Correct the stale v0.23/v0.24, V1 cradle, release-link, mass and fin-penalty statements.
2. Register this source and audit in the research/source index.
3. Run an architecture-level trade with equal mission constraints before freezing forward
   sweep as irreversible.
4. Declare one current aircraft configuration baseline and generate copied numerical facts
   into prose documents where possible.

**Exit:** no contradictory current values and a reviewed configuration-selection ADR.

### Gate B — manufacturing definition

1. Produce the native parametric assembly and released interchange geometry.
2. Close all wing/body/fin/control/propeller interfaces and manufacturing tolerances.
3. Replace unresolved mass reserves with part-level CAD and measured prototype values.
4. Define final printed trailing edge, hinge gap, surface finish, wall paths, joints and
   material/process coupons.

**Exit:** reviewable STEP plus part manufacturing data, mass/CG report and zero unresolved
geometric interference.

### Gate C — ground aerodynamic and structural evidence

1. Measure printed section coordinates and run the full moment/transition/roughness matrix.
2. Test PETG and LW-PLA-HT coupons from the actual printers and orientations.
3. Measure semispan bending/torsion, elastic axis, joint stiffness and hysteresis.
4. Static-test the fin roots, servo mounts, hinges, joiners and representative airframe.
5. Perform full-aircraft GVT in CLEAN and V1 with flight equipment installed.
6. Correlate structural and aeroelastic models; calculate divergence and flutter boundaries
   with uncertainties.

**Exit:** physical properties replace dominant `[E]` inputs and both static and dynamic
aeroelastic clearances exceed the proposed first-flight envelope with reviewed margin.

### Gate D — stability, controls and first flight

1. Close body-inclusive longitudinal and directional aerodynamics.
2. Demonstrate robust V1 launch behavior across the declared yaw/wind tolerance.
3. Resolve mass and CG on the actual article; reduce uncertainty below the acceptance band.
4. Release control throws/mixes, rate schedules, failsafes, launch method and abort card.
5. Fly only inside the ground-cleared envelope and expand in reviewed increments.
6. Redesign E7/E8 identification so excitation, free response and active speed clearance
   are not conflated.

**Exit:** a signed first-flight readiness review with every P0 item closed or explicitly
accepted by the project authority on measured evidence.

## 10. Immediate decisions recommended from Part 1

1. **Keep all manufacturing labels blocked.** The repository already says this in the
   drawings; make the release status equally explicit in the top-level README.
2. **Withdraw the 90/110/130/150 km/h E7 schedule immediately.** It conflicts with the
   105 km/h initial cap and the 129.59 km/h conservative divergence result.
3. **Reclassify `I-05` flutter as an unsupported preliminary hypothesis.** Retain elevon
   mass balance, but remove the conclusion that classic flutter is not critical until a
   reproducible coupled model and GVT exist.
4. **Treat V1—not CLEAN—as the only candidate for first-flight development**, and only
   after its negative `Cn_beta` lower corner and low-Re fin behavior are resolved. This is
   not yet approval to fly V1.
5. **Split XFOIL drag calibration from pitching-moment validation.** Do not select one
   Ncrit value to serve both purposes.
6. **Reopen the forward-sweep architecture before production CAD.** The current trade is
   valuable but conditional on choices it never varied.
7. **Make measured mass/CG and GVT preflight gates, not post-flight learning.** The current
   stall and CG margins are too small for estimated installed data.

## 11. Part 1 conclusion

The NF Design Guide reinforces the repository's central philosophy—coupled decisions,
empirical checking and explicit uncertainty—but exposes a maturity mismatch. Salamandra's
documentation and calculations resemble a late preliminary design review, while several
published labels and proposed tests imply a released flight article.

The next engineering step is not another isolated aerodynamic optimization. It is to turn
the current analytical configuration into one controlled physical article, measure the
properties that dominate its uncertainty, and correlate an integrated aerodynamic,
structural and control model before first flight.

[Part 2](NF-Design-Guide-2024-Repository-Audit-Part-02-Airfoil-Trim.md) deepens the
airfoil/trim/longitudinal-control analysis and converts the guide's “fluent airfoil”
lesson into a specific reproducible test matrix for Salamandra r1.

[Part 3](NF-Design-Guide-2024-Repository-Audit-Part-03-Directional-Stability.md) propagates
the published directional uncertainty into the dynamics and audits finite sideslip,
adverse yaw, stall, launch, landing and E8 identification.

[Part 4](NF-Design-Guide-2024-Repository-Audit-Part-04-Structure-Aeroelasticity.md)
closes the initial audit series with printed load paths, joint mechanics, divergence,
body-freedom flutter, physical verification and a consolidated release matrix.

[Part 5](NF-Design-Guide-2024-Repository-Audit-Part-05-Wingtips-Drag-Flaps.md) extends the
series with a focused systems audit of winglets, induced-versus-parasite drag, the
forward-swept wingtip yaw arm, outer-wing reserve and flap management.

[Part 6](NF-Design-Guide-2024-Repository-Audit-Part-06-Design-Method-Synthesis.md) reaches
the end of the source and converts its future-design questions into airfoil-geometry,
section-plane, statewise spanload, static-margin, active-stability and flap-chord gates.
