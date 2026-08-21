# ADR-0048 — Article #1 mission, efficiency metric and configuration order

**Status:** ✅ Active · **Date:** 2026-08-21 · **Confidence:** High `[D]` for the
programme contract; Medium `[D]`/`[E]` for the initial architecture order
**Reversible:** Yes, before Gate M3; later changes invalidate affected downstream gates
**Related gates:** M0–M9
**Specification:** [Article #1 objectives and mission requirements](../docs/00-objectives-and-requirements.md)
**Calculation:** [`mission_contract.py`](../calculations/mission_contract.py)

## Context

The released v0.6 repository contained a detailed aircraft, but its controlling statements
did not express the redesign intent consistently:

- O1 optimized one point, `<=1.15 Wh/km at 95 km/h`, while the mission also prescribed
  80/100 km range and 60 minute endurance without a measurement-derived basis;
- ADR-0010 irreversibly selected “fast cruise” and ADR-0001 irreversibly selected forward
  sweep before a multi-state coupled trade existed;
- ADR-0033 kept the motor and battery outside the design, although propulsion efficiency,
  pack mass and CG are first-order aircraft variables;
- Article #1 was 6S, while the platform language still implied 4S–6S interchangeability;
- ADR-0038 selected fixed fins without a rudder, while the revised development intent is to
  test a rudder-capable baseline before a finless efficiency configuration; and
- detailed v0.6 geometry and speed values looked authoritative even though the programme
  had reopened the aircraft architecture.

The NF Design Guide synthesis independently identified the missing first step: define the
aircraft task, configurations, mission states, stability/control objectives, uncertainty
and rejection criteria before generating or optimizing geometry. It also recommends a
multi-state, multi-objective comparison that preserves Pareto alternatives.

## Alternatives considered

| Option | Advantages | Disadvantages | Disposition |
|---|---|---|---|
| Retain the complete v0.6 mission | No rework; all existing scripts remain directly authoritative | Preserves unsupported distance/time targets and prematurely fixed architecture | Rejected |
| Optimize only Wh/km at 95 km/h | Simple scalar ranking and continuity with O1 | Can hide poor low-speed, best-range or normal-FPV behavior; one point can drive a brittle aircraft | Rejected as sole objective; retained as comparator |
| Create one weighted score across performance and handling | Produces a total order | Weights have no stakeholder basis and can let efficiency compensate for a safety failure | Rejected until explicit stakeholder weights exist |
| Multi-state total-energy Pareto comparison after pass/fail safety gates | Exposes trade-offs, supports uncertainty and matches the NF method | Can retain more than one candidate and requires an explicit later decision | **Selected** |
| Defer mission definition until motor/geometry selection | Allows immediate hardware shopping | Makes the component list define the aircraft task by accident | Rejected |

## Decision

Salamandra Article #1 shall be designed to the following controlled programme contract:

1. Safety/controllability is a pass/fail condition before performance ranking.
2. Efficiency is total battery-terminal Wh/km, including propulsion, conversion,
   avionics and FPV energy.
3. Candidates are compared as a Pareto vector at candidate-best-range, 65 km/h, 80 km/h
   and the historical 95 km/h point. No scalar weighting is implied.
4. The programme sets no fixed range, endurance or roll-rate requirement. Those values are
   reported outcomes; practical handling is closed through trim reserve, stability,
   control authority, actuator response and predeclared bank-response tests.
5. `SALAMANDRA-6S-R`, using 21700 Li-ion cells and a removable rudder-capable vertical
   module, is the first-flight development configuration after all ground gates close.
6. `SALAMANDRA-6S-CLEAN` is a later controlled A/B experiment using the same 6S power
   module. It cannot precede the directional evidence from `6S-R`.
7. `SALAMANDRA-8S-STUDY` is a separate complete power-system study, not a battery swap or
   first-flight configuration.
8. The aircraft remains a single-motor, 3D-printed, front-camera FPV flying wing. A pusher
   is the working installation baseline. Sweep direction, detailed planform, airfoil,
   mass, motor, propeller, ESC, servo and OML remain open to the gated trade.
9. The battery installation shall provide at least 20 mm total usable longitudinal travel.
10. Conventional PETG and a 256 mm minimum printer-bed dimension remain product
    constraints. Native production CAD remains a human CAD deliverable after Gate M7.

## Rationale

The decision uses measured and reproducible evidence without over-promoting it:

- The v0.6 calculation system already owns the 95 km/h and 1.15 Wh/km values, so retaining
  them as a continuity state preserves comparability without allowing them to define the
  entire redesign `[D]`.
- I-32 estimates the present P42A 6S1P pack at `445 +/- 5 g` and 90.72 Wh, and 8S1P at
  `585 +/- 5 g` and 120.96 Wh. The 8S option therefore adds 140 g for 33.3% more nominal
  energy, changes its required CG station by 62.2 mm, and needs a separately qualified
  voltage/propulsion chain `[M]`/`[D]`/`[E]`. This supports 6S-first and 8S-as-study; it
  does not permanently reject 8S.
- The inherited pack trade already models `+/-10 mm` centre travel, exactly the 20 mm
  total minimum now required. Keeping this value makes CG adjustment physically testable
  while the v2 mass skeleton is rebuilt `[E]`.
- I-14 separates the hand-launch release gate, `V_release >= V_s`, from acceleration to a
  `1.20 V_s` post-release target. The contract retains that separation instead of claiming
  that a powered acceleration target is human release speed `[D]`/`[E]`.
- The NF audit D0–D8 method requires task definition before geometry, coupled trim/control
  over the full CG band, robust multi-state comparison, physical calibration and release by
  configuration. The new contract implements D0 and gives later gates explicit owners.

## Supersession and scope

- **ADR-0010 is superseded** as the governing Article #1 mission branch. Its conclusion
  that Wh/km matters more than pure endurance remains supporting rationale.
- **ADR-0033 is superseded for Article #1.** Open community variants remain encouraged,
  but the reference aircraft must select and bind a complete, reproducible electrical and
  propulsion configuration.
- **ADR-0001 and ADR-0040 are reopened for the redesign.** Their forward-swept v0.6
  geometry remains candidate A and historical evidence, not the automatic winner.
- **ADR-0038 is superseded for the redesigned directional configuration.** Its fixed-fin
  V1 remains a comparison candidate; the new first-flight interface is rudder-capable.
- Existing v0.6 calculations, drawings and release records remain valid as historical and
  candidate evidence. This ADR does not rewrite their numerical results.

## Consequences

- Gate M0 closes and Gate M1 becomes the only open design gate.
- `mission_contract.py` becomes the machine-readable owner of mission states,
  configuration order, printer/material/battery-travel constraints and historical aliases.
- The electronics work must now produce candidate envelopes and a mass ledger; it may not
  copy one v0.6 motor or servo into the v2 aircraft without a new comparison.
- M2 must solve the equipment/CG skeleton before the architecture and fuselage trades.
- M3 must compare forward-, straight- and aft-sweep candidates under the same mission and
  uncertainty contract.
- M4/M5 must report the entire E0–E3 efficiency vector and control/handling envelope.
- A candidate that is better at some energy states and worse at others remains a Pareto
  alternative. Selection then requires a recorded stakeholder priority, not a hidden score.
- Any later mission change shall update this ADR, the specification and executable contract
  together, then identify which downstream gate evidence is invalidated.

## Review conditions

Review this decision if one of the following occurs:

1. a stakeholder supplies a defensible range, endurance, speed or handling requirement and
   the operational basis needed to verify it;
2. M1 shows that no safe, practical 6S architecture can meet the mission while a complete
   8S architecture can;
3. M2/M5 shows that the rudder-capable module creates a safety or control disadvantage that
   cannot be removed by sizing or interface changes;
4. physical energy tests show that the selected comparison states do not discriminate the
   aircraft's actual use; or
5. regulation, test-site constraints or the launch/landing method introduce a new
   controlling mission state.

Do not review it merely because a preferred component or aesthetic geometry performs
poorly. That is evidence against the candidate, not evidence that the mission should move.
