# Salamandra Article #1 — objectives and mission requirements

**Revision 2.0** · 21 August 2026 · **GATE M0 CLOSED — ACTIVE PROGRAMME SPECIFICATION**

This document controls what the redesigned Salamandra Article #1 must do. It does not
release a planform, airfoil, mass, motor, propeller, servo, structure or CAD geometry.
Those are candidate-dependent decisions made by the gated process in the
[Master Design Plan](05-master-plan.md).

The machine-readable owner of the mission states, configuration order and inherited
comparators is [`calculations/mission_contract.py`](../calculations/mission_contract.py).
[ADR-0048](../decisions/ADR-0048-article-1-mission-and-configurations.md) records the
programme decision. A value marked **provisional screen** is useful for rejecting clearly
unsuitable concepts, but is not a released-aircraft limit.

---

## 1. Product intent

Salamandra Article #1 is an open, single-motor, 3D-printed FPV flying wing intended to
demonstrate the lowest practical total energy consumption that the project can achieve
without becoming a fragile, slow-handling pure glider. It must remain controllable,
repairable and useful as an instrumented development aircraft.

The objective priority is deliberately lexicographic:

1. safety and controllability;
2. total-energy efficiency;
3. practical handling;
4. durability and repairability;
5. simplicity and open reproducibility; and
6. aesthetic preference.

An item lower in this list cannot compensate for failure of an item above it. Forward
sweep is therefore an aesthetic and research preference, not a requirement: it is selected
only if the coupled architecture trade shows a defensible benefit or no material penalty.

The programme has **no fixed range or endurance requirement**. Range and endurance will be
reported as outcomes of usable battery energy, measured total energy consumption,
operating state and declared reserve policy. This avoids designing backwards from an
unsupported 80 km, 100 km or 60 minute target.

## 2. Controlled configurations

The suffix is part of the aircraft identity. Data from one configuration must not be used
as if it came from another.

| Configuration | Electrical architecture | Directional hardware | Programme role | Release order |
|---|---|---|---|---:|
| **SALAMANDRA-6S-R** | 6S, 21700 Li-ion | Removable vertical module with rudder capability | First-flight development baseline after all ground gates close | 1 |
| **SALAMANDRA-6S-CLEAN** | Same controlled 6S power module | Vertical module removed | Post-baseline efficiency and directional-stability experiment | 2 |
| **SALAMANDRA-8S-STUDY** | Separate 8S, 21700 Li-ion power module | Not released | Voltage, loss, mass, packaging and propulsion trade only | Study may run in parallel; no flight order assigned |

`6S-R` is the only first-flight configuration authorized by this specification. “Rudder
capability” means that the geometry and installation shall support a movable surface and
actuator if the directional/control analysis selects them; it does not predetermine their
size or control law. `6S-CLEAN` may proceed only after `6S-R` supplies correlated stability,
control and launch evidence. `8S-STUDY` cannot inherit a motor, ESC, propeller, bay or flight
release from 6S merely because it fits electrically. Its M1/M2 analysis may proceed in
parallel; only an 8S flight release is unordered and outside the first-article baseline.

## 3. Mission-state matrix

Every architecture candidate shall be evaluated at the same named states. Candidate-
specific stall, optimum-efficiency and limit speeds are outputs, not copied constants.

| ID | State | Speed definition | Required output | Authority |
|---|---|---|---|---|
| **L0** | Hand-launch release | `V_release >= 1.00 V_s` | Release margin, torque-roll margin and acceleration to the I-14 `1.20 V_s` target | Requirement plus inherited I-14 method |
| **L1** | Approach/low-speed handling | `1.30 V_s` | Trim, remaining pitch/roll/yaw authority, mode behavior and stall recovery | Provisional engineering state `[E]`; not a certification rule |
| **E0** | Best range | Candidate-derived speed that minimizes total battery Wh/km inside its admissible envelope | Speed, total Wh/km and uncertainty | Primary efficiency state |
| **E1** | Low cruise comparison | 65 km/h TAS at the standard comparison atmosphere | Total Wh/km and subsystem breakdown | Common reporting state |
| **E2** | Normal FPV cruise | 80 km/h TAS at the standard comparison atmosphere | Total Wh/km, trim/control reserve, propulsion equilibrium and temperatures | Provisional design state `[E]` |
| **E3** | v0.6 continuity comparison | 95 km/h TAS at the standard comparison atmosphere | Total Wh/km and delta from the historical 1.15 Wh/km target | Historical comparator, not the sole objective |
| **H0** | Handling envelope | L1, E2 and candidate manoeuvre points established at Gate M5 | Static/dynamic stability, control time histories, actuator load/rate and recovery | Gate-M5 analytical contract, Gate-M9 flight validation |
| **S0** | Structural/aeroelastic envelope | Derived from the accepted mass, handling envelope, gust basis and propulsion cases | Net loads, stiffness, strength, divergence and flutter clearance | Gates M6–M8 |

For candidate-to-candidate calculations, the comparison atmosphere is ISA sea level,
`rho = 1.225 kg/m3`. This is a repeatability convention, not an assumed operating altitude.
Physical tests shall record air density, temperature, pressure, wind, aircraft mass, CG,
configuration and battery state. Energy-per-distance tests shall use air distance or
reciprocal-course correction so that wind is not credited as aerodynamic efficiency.

The admissible speed range for the E0 search is bounded by the later low-speed,
propulsion, control, structural and aeroelastic gates. E0 is invalid if an optimizer finds
a mathematical minimum outside that envelope.

## 4. Efficiency and comparison method

### 4.1 Metric boundary

The controlled metric is energy removed at the battery terminals divided by air distance:

```text
total Wh/km = (propulsion + ESC + BEC/conversion + avionics + FPV energy) / air distance
```

Reports shall include the subsystem breakdown, measurement uncertainty and configuration.
Motor-only or shaft-only figures do not satisfy the objective. Range is then an explicitly
conditional result:

```text
range [km] = usable battery energy [Wh] / total energy [Wh/km]
```

Usable energy and operational reserve shall be reported, not hidden inside a claimed range.

### 4.2 Selection rule

The efficiency result is the vector `(E0, E1, E2, E3)`. Candidate A is unambiguously more
efficient than candidate B only when A is no worse at every state, within declared model or
test tolerance, and materially better at at least one. Otherwise both remain on the Pareto
front until a stakeholder decision supplies explicit weights. No undocumented weighted
score may select the aircraft.

Safety, stability, launchability, structure, aeroelasticity, packaging and manufacturing
constraints are pass/fail gates before efficiency ranking. A low Wh/km result cannot buy
its way through a failed gate.

The former `<= 1.15 Wh/km at 95 km/h` objective remains a useful v0.6 comparator at E3.
It is not the redesign's only success criterion and is not evidence of range.

## 5. Practical handling objective

“Agile” means that the aircraft is not optimized into glider-like handling that consumes
all available control just to trim or makes ordinary FPV bank changes impractical. It does
**not** create an arbitrary roll-rate or aerobatic-roll requirement.

A candidate satisfies the preliminary handling objective only when the Gate-M5 model shows:

- passive static stability for the first-flight `6S-R` configuration over the physical CG
  and aerodynamic-uncertainty band;
- stable or explicitly bounded dynamic modes at L1, E2 and the candidate manoeuvre states;
- equilibrium without actuator saturation or unmodelled control extrapolation;
- absolute trim no greater than 75% of one-sided mechanical travel, leaving at least 25%
  trim-only reserve in the limiting direction before simultaneous pitch/roll allocation;
- usable bank establishment and reversal without continuous full control, with the actual
  response time, roll rate and remaining authority reported rather than prescribed here;
- adequate servo torque, rate, thermal margin and linkage stiffness for simultaneous
  commands; and
- a recoverable stall/lost-lift sequence about the adverse CG, including directional
  behavior and propeller effects.

Gate M5 shall convert “usable bank establishment and reversal” into a test card and
quantitative acceptance band based on the selected candidate's simulated response and
actuator capability. That band must be frozen before flight validation; flight performance
must not be judged after observing the result.

## 6. Article #1 requirements

Evidence status uses `[M]` measured, `[D]` reproducibly derived, `[E]` engineering estimate
and `[I]` incomplete-model inference. “Open” means the requirement exists but the design
has not demonstrated compliance.

| ID | Requirement | Verification | Current evidence |
|---|---|---|---|
| **A1-R01** | Article #1 shall be a tailless flying wing. Sweep direction, taper, span, area and airfoil family remain open until M3/M4. | Configuration review and controlled CAD identity | Requirement fixed; geometry open |
| **A1-R02** | One propulsion motor shall be used. A pusher is the working baseline, not a frozen architecture. | Architecture review, hazard/launch analysis and propulsion trade | Requirement fixed; installation open |
| **A1-R03** | A forward-facing FPV camera shall have an unobstructed view and a replaceable protective installation. | Packaging drawing, field-of-view check and inspection | Requirement fixed; device and envelope open |
| **A1-R04** | The first-flight power system shall be 6S and use 21700 Li-ion cells. | Pack manifest, electrical inspection and measured mass | Requirement fixed; cell, layout and capacity open |
| **A1-R05** | 8S shall be evaluated only as a separate complete architecture, including cell mass, voltage limits, motor Kv, propeller, ESC, BEC, wiring, CG and thermal effects. | Controlled 6S/8S trade | Open at M1 |
| **A1-R06** | The battery installation shall provide at least 20 mm total usable longitudinal adjustment, with retention, wiring and access valid at both ends. | Mass-skeleton solution, CAD measurement and physical travel test | Numerical requirement fixed; packaging open |
| **A1-R07** | Conventional PETG, preferably light colored, is the primary printed-airframe material. Any exception requires a part-specific structural, thermal and process decision. | Material/process specification and coupon evidence | Material intent fixed; allowables open |
| **A1-R08** | Every printed aircraft part shall fit a printer with a 256 mm minimum bed dimension without fiber lamination. | Oriented bounding-box check in CAD and slicer | Requirement fixed; segmentation open |
| **A1-R09** | The aircraft shall be designed around the equipment mass/envelope skeleton before the fuselage OML is lofted. Only battery position is an automatic CG variable; other movement requires an explicit installation allowance. | Mass ledger, CG solver, equipment SVG and OML containment check | Method fixed; v2 ledger open |
| **A1-R10** | `6S-R` shall support a removable rudder-capable vertical module; `6S-CLEAN` shall preserve the controlled interfaces needed for an A/B comparison. | Interface drawing, mass/configuration manifest and stability/control evidence | Requirement fixed; geometry open |
| **A1-R11** | Pitot/airspeed, battery voltage/current, blackbox flight logging, GPS and attitude data shall support launch, efficiency and model-correlation tests. | Instrumentation plan, calibration and synchronized log audit | Functional requirement fixed; hardware open |
| **A1-R12** | Flight-control geometry shall not depend on one autopilot firmware. INAV and ArduPlane compatibility remain objectives where practical. | I/O/interface review and configuration records | Open at M1/M5 |
| **A1-R13** | Native CAD shall be produced by a human CAD designer from the released handoff package; repository scripts own requirements, calculations, parametric evidence and SVG review drawings. | Signed CAD handoff and round-trip drawing review | Process fixed; handoff blocked until M7 |
| **A1-R14** | Every released value shall identify its numerical owner, evidence class, uncertainty and verification event. | Contract lint, calculation verification and review | Active repository policy |
| **A1-R15** | Source, documentation and reusable hardware interfaces shall remain open and versioned under the repository's published licences. | Release audit | Active programme objective |

## 7. Provisional screening assumptions

These values prevent unbounded early trades. They must be rederived or explicitly adopted
before they can enter a CAD release.

| Screen | Provisional value | Use now | Required closure |
|---|---:|---|---|
| Stall-speed ceiling | 45 km/h | Compare initial area/mass/`CLmax` combinations and launch burden | M3/M5 candidate-specific requirement and E2 physical aerodynamic evidence |
| Manoeuvre limit loads | +6 / -3 | Initial structure and actuator sensitivity only | M5 operational handling envelope and M6 complete net-load model |
| Ultimate factor | 1.5 x limit | Initial strength sensitivity | M6 materials/process basis and approved load cases |
| Post-release launch target | 1.20 `V_s` | I-14 acceleration comparison after the `V_release >= V_s` gate | M5 candidate propulsion/launch analysis |
| Trim-only reserve | >=25% of one-sided mechanical travel | Reject trim-saturated concepts | M5 simultaneous pitch/roll/control allocation |

The v0.6 values of 105 km/h initial cap, 160 km/h article `V_NE` and 180 km/h structural
case do **not** govern the redesign. M6 shall derive a candidate-specific expansion limit
from manoeuvre/gust/control/propulsion loads and independent structural, divergence and
flutter clearance. Likewise, 1.300 m span, 0.282 m2 area, aspect ratio 6, -15 degree
quarter-chord sweep and the r1/r2a airfoils are comparison candidates, not requirements.

No fixed all-up mass is declared. M2/M3 shall derive the feasible mass/area region from the
selected battery architecture, equipment ledger, launch/low-speed screens, structural
allowance and uncertainty. The fuselage is then modelled around that solved skeleton;
nose length is not chosen aesthetically or shortened before CG closes.

## 8. Operations, manufacture and instrumentation assumptions

The working concept uses hand launch and a controlled belly landing on a suitable clear,
soft surface. Site, altitude, wind and pilot limitations are intentionally not invented at
M0; they become explicit release-card inputs at M8. Until then, calculations shall sweep
plausible density and wind rather than claiming one universal operating condition.

The aircraft should be segmented for repair by reprinting damaged modules. Print time,
assembly time, structure cost and transport-case length shall be measured and reported as
design outcomes. They are not acceptance requirements until physical workflow data show
that a defensible limit is needed. Carbon or metal may provide local bending, joint or
hard-point functions when justified; PETG remains the primary printed load path and fiber
lamination is outside Article #1 scope.

## 9. Non-goals

- A speed record, aerobatic roll-rate target or unlimited manoeuvre envelope.
- A thermal-soaring or maximum-endurance glider optimized at the expense of FPV handling.
- A guaranteed distance or flight time before measured energy and reserve policy exist.
- Active, neutral-margin or negative-static-margin stability on Article #1.
- Automatic selection of forward sweep for visual reasons.
- One motor, propeller, servo or battery layout chosen before the coupled trade.
- Production CAD, STL publication or free flight before the applicable gates close.
- Certification claims. The NF Design Guide is expert model-aircraft evidence, not a
  certification specification.

## 10. Method inherited from the NF Design Guide audit

The repository's review of Peter Wick's *Designing Flying Wings* is integrated as a method,
not copied as geometry. The applicable sequence is:

| NF synthesis step | Salamandra implementation |
|---|---|
| D0 — define task/configurations | This specification, `mission_contract.py` and ADR-0048 |
| D1 — one parametric geometry authority | M3 architecture and M4 geometry contract |
| D2 — local aerodynamic evidence | M4 printed-section/XFOIL matrix with measured closure |
| D3 — complete 3-D aircraft | M4/M5 viscous 3-D, finite-sideslip and control models |
| D4 — close trim, stability and control together | M5 full CG/uncertainty/control envelope |
| D5 — couple aerodynamics, mass and structure | M2 mass skeleton and M6 structural/aeroelastic loop |
| D6 — robust multi-state optimization | M3 Pareto comparison across E0–E3 with retained alternatives |
| D7 — calibrate with physical evidence | M6 coupons through M9 instrumented flights |
| D8 — release by configuration/evidence | Configuration manifest, hashes and gate-specific release |

This preserves the book audit's central lessons: analyze a flying wing as a coupled system;
carry low-Reynolds-number and manufactured-geometry uncertainty; solve the entire physical
CG band; preserve Pareto alternatives; and never call an optimizer output a release.

## 11. Inherited v0.6 requirement disposition

| Inherited item | Revision-2 disposition | Reason |
|---|---|---|
| `<=1.15 Wh/km at 95 km/h` | **Retain as E3 historical comparator** | Valuable continuity point, too narrow to define global efficiency |
| 80 km / 100 km / 60 min | **Withdraw** | Unsupported scalar targets; now reported outcomes |
| 90–105 km/h cruise | **Replace** | E0–E3 expose best-range, low, nominal and legacy behavior |
| 4S–6S platform | **Supersede** | 6S first-flight baseline; 8S separate study; no current 4S requirement |
| 45 km/h stall | **Retain as provisional screen** | Useful launch/area comparator; final value requires candidate and evidence |
| 160 km/h `V_NE` / 180 km/h design case | **Withdraw from redesign authority** | Must follow candidate load and aeroelastic closure |
| +6/-3 limit, x1.5 ultimate | **Retain as provisional screens** | Starting sensitivity values, not yet a complete load basis |
| Forward sweep -15 degrees | **Reopen** | Candidate A only; benefit must survive the coupled trade |
| Fixed fins, no rudder | **Supersede** | First configuration is now rudder-capable `6S-R`; CLEAN follows evidence |
| Fixed 1.300 m / 0.282 m2 / AR 6 geometry | **Reopen** | Candidate must follow mission, energy, mass and packaging trades |
| PETG and 256 mm printer | **Retain** | Explicit product/manufacturing intent |
| <=20 h print/half, <=3 h assembly, <EUR60, 700 mm case | **Demote to reported outcomes** | No evidence-based thresholds at M0 |
| Modularity and repairability | **Retain with evidence** | Interfaces must not impose unjustified mass, drag or stiffness penalties |
| Exact v0.6 motor/propeller/servo choices | **Comparison data only** | M1 must reselect against the v2 mission and mass skeleton |

## 12. Gate-M0 acceptance and next closure

Gate M0 is closed because the programme now has:

- a single product intent and objective order;
- named 6S-R, 6S-CLEAN and 8S-STUDY configurations with release order;
- a repeatable mission-state matrix and total-energy metric boundary;
- an explicit no-range/no-endurance/no-arbitrary-roll-rate disposition;
- hard requirements separated from provisional screens and historical comparators;
- an executable contract with repository-level verification; and
- a decision record that supersedes the conflicting v0.6 mission assumptions.

M0 closure does not release hardware. **Gate M1 is now open.** Its first controlled output,
the [MP-03 hardware and power manifest](17-article-1-hardware-manifest.md), now identifies
candidate 21700 packs, 6S and 8S power architectures, motor/propeller/ESC envelopes,
servos, flight controller, FPV system, power conversion, sensors and wiring without
prematurely selecting geometry. MP-04/MP-05 must replace its catalog/estimated inputs and
prove the measurement chain before M1 can close.

| Open numerical question | Owner/gate | Closure evidence |
|---|---|---|
| Final low-speed/stall requirement | M3/M5 | Candidate mass/area/`CLmax`, launch and handling trade |
| Normal-cruise 80 km/h suitability | M3/M4 | Aerodynamic and propulsion Pareto results |
| Practical bank-response acceptance band | M5 | Predeclared simulation/test-card criterion |
| Final limit/ultimate/gust envelope and speed limits | M5/M6 | Operational cases plus complete load and aeroelastic models |
| Motor, propeller, ESC and servo selections | M1/M4/M5/M7 | Catalog evidence, bench tests and coupled margins |
| 6S versus 8S release disposition | M1/M2/M3/M4 | Energy, loss, mass, CG, thermal and propulsion comparison |
| R versus CLEAN directional architecture | M3/M5/M9 | Fin/rudder model, ground evidence and controlled flight A/B test |

## 13. Evidence and reproduction

Primary supporting evidence:

- [Master Design Plan](05-master-plan.md) — gate order, ownership and CAD handoff;
- [Consolidated NF Design Guide audit](../design/NF-Design-Guide-2024-Consolidated-Audit-and-Release-Programme.md)
  and its [design-method synthesis](../design/NF-Design-Guide-2024-Repository-Audit-Part-06-Design-Method-Synthesis.md);
- [I-14 hand-launch feasibility](../research/I-14-hand-launch-stall-margin.md) — release and
  post-release method;
- [I-32 6S/8S trade](../research/I-32-6s-8s-p42a-pack-and-aircraft-trade.md) — inherited
  mass, packaging and voltage evidence; and
- [measured reference aircraft](02-measured-references.md) — empirical
  context without copying their missions.

Reproduce the controlling checks with:

```bash
python3 calculations/mission_contract.py
python3 calculations/verify_calculations.py --fast
python3 calculations/contract_lint.py
```

Passing these commands proves that the declared contract is internally consistent. It does
not prove that a future aircraft meets it; that requires the analyses and physical evidence
at Gates M1–M9.
