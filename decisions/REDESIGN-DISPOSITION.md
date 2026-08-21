# Article #1 redesign — ADR disposition ledger

**Revision 1.0** · 21 August 2026 · **MP-02 COMPLETE — ACTIVE AUTHORITY MAP**

This ledger separates two facts that were previously conflated:

1. an ADR's historical status inside the released v0.6 design; and
2. its authority over the redesigned Article #1 governed by the
   [Revision-2 requirements](../docs/00-objectives-and-requirements.md) and
   [ADR-0048](ADR-0048-article-1-mission-and-configurations.md).

The historical ADR remains intact as evidence. The disposition below determines whether
its decision can constrain new M1–M9 work. The machine-readable owner and coverage check is
[`decision_ledger.py`](../calculations/decision_ledger.py).

## Classification rules

| Classification | Meaning |
|---|---|
| **RETAINED** | The decision remains binding for the redesigned Article #1 within the scope stated here. |
| **RETAINED-METHOD** | The analytical or evidence rule remains binding; embedded v0.6 geometry, hardware or numerical selections do not. |
| **CANDIDATE-ONLY** | The ADR is controlled comparison or test evidence. It has no authority to freeze v2 geometry, hardware or limits. |
| **REOPENED** | The underlying question is unresolved. The owning gate must compare alternatives and issue or amend an ADR. |
| **SUPERSEDED** | A later authority replaces the decision for redesigned Article #1. Historical results remain traceable. |
| **CANCELLED** | The option remains outside Article #1 scope unless a future controlled decision explicitly reopens it. |

`Owning gate` identifies the first gate that may promote, replace or close the disposition.
`All` means a programme-wide method or policy; `—` means that no active gate owns a
cancelled option. No CAD designer may infer authority from the historical status icon alone.

## Complete ADR disposition

<!-- BEGIN GENERATED: ADR redesign disposition · calculations/decision_ledger.py · do not edit by hand -->

| ADR | Historical decision | Article #1 disposition | Owning gate | v2 authority |
|---|---|---|---|---|
| [0001](ADR-0001-inverted-sweep.md) | Forward-swept flying wing | **CANDIDATE-ONLY** | `M3` | Forward sweep remains architecture candidate A; no v2 planform authority. |
| [0002](ADR-0002-closed-shell.md) | Closed three-cell shell | **REOPENED** | `M6` | A closed printed load path is credible, but cell count and topology follow correlated loads and stiffness. |
| [0003](ADR-0003-wash-in-twist.md) | Wash-in twist for trim (forward sweep) | **CANDIDATE-ONLY** | `M4` | Wash-in applies to the forward-swept r2a test candidate; twist is reselected with section and trim evidence. |
| [0004](ADR-0004-aspect-ratio.md) | Aspect ratio 6.0 | **CANDIDATE-ONLY** | `M3` | Aspect ratio 6 is a v0.6 comparison value, not a redesign constraint. |
| [0006](ADR-0006-single-pusher.md) | Single pusher motor preferred | **REOPENED** | `M3/M4` | One motor is retained; the pusher is the working baseline pending architecture and propulsion closure. |
| [0007](ADR-0007-propeller.md) | Propeller P/D 0.8–1.0 matched by advance ratio | **RETAINED-METHOD** | `M4` | Match propellers from measured maps by advance ratio; the 0.8–1.0 P/D band and hardware are not frozen. |
| [0008](ADR-0008-reject-7x12-propeller.md) | Reject the 7×12 propeller | **RETAINED-METHOD** | `M4` | Do not credit an unmeasured 7x12 efficiency claim; measured data may readmit the propeller. |
| [0009](ADR-0009-drag-decomposition.md) | Separate drag decomposition; never a single Oswald factor | **RETAINED-METHOD** | `All` | Keep viscous and induced drag separate in every candidate and mission state. |
| [0010](ADR-0010-mission-branch.md) | Mission branch: fast cruise | **SUPERSEDED** | `M0` | ADR-0048 replaces the single fast-cruise branch with the E0–E3 total-energy mission. |
| [0012](ADR-0012-light-color.md) | Light color mandatory | **REOPENED** | `M6` | Light colour remains the PETG default, but mandatory scope follows measured thermal/process evidence. |
| [0015](ADR-0015-carbon-non-torsional.md) | Carbon is a bending and alignment element, not torsion | **RETAINED-METHOD** | `M6` | Credit carbon only through an explicit load path and measured stiffness; its exact v0.6 role is not fixed. |
| [0016](ADR-0016-reject-pla-plus.md) | Reject PLA+ | **CANDIDATE-ONLY** | `M6` | The reviewed PLA+ data remain material evidence; Article #1 is governed by the PETG-primary requirement. |
| [0018](ADR-0018-reject-abs.md) | Reject ABS (UV degradation) | **CANDIDATE-ONLY** | `M6` | The reviewed ABS UV evidence remains material evidence; Article #1 is governed by the PETG-primary requirement. |
| [0021](ADR-0021-base-material.md) | PETG as the base structural material | **RETAINED** | `M0/M6` | PETG remains the primary printed-airframe material; any local exception needs its own evidence and decision. |
| [0022](ADR-0022-carbon-veil-cancelled.md) | Carbon veil ±45° over the skin | **CANCELLED** | `—` | Wet carbon-veil lamination remains outside Article #1 scope. |
| [0023](ADR-0023-joint-adhesive.md) | Segment joints: tenon + PETG adhesive, area ≥ 3× the skin section | **REOPENED** | `M6` | Adhesive, tenon and bond-area rules require production-process coupons and complete joint loads. |
| [0024](ADR-0024-segmentation.md) | Three segments per wing half, 45° roll on the bed | **CANDIDATE-ONLY** | `M6/M8` | The exact three-segment cuts and print orientation belong only to the v0.6 geometry; 256 mm fit remains binding. |
| [0025](ADR-0025-elevon-balancing.md) | Elevon mass balancing | **RETAINED-METHOD** | `M5/M6/M8` | Control-surface inertia, balance and freeplay are mandatory aeroelastic gates; the final balance target is model/test derived. |
| [0026](ADR-0026-dual-actuation.md) | No-freeplay linkage, one actuator per elevon | **CANDIDATE-ONLY** | `M1/M5` | Two DS-939MG servos and their stations are v0.6 packaging data; actuator count and selection are reopened. |
| [0027](ADR-0027-relative-thickness.md) | Relative thickness 13.5 % root / 9 % tip | **CANDIDATE-ONLY** | `M3/M4/M6` | The 13.5/9 percent thickness schedule remains candidate A evidence and must compete with other architectures. |
| [0028](ADR-0028-gyroid-infill.md) | Gyroid 5 % infill | **CANDIDATE-ONLY** | `M6` | Five-percent gyroid is a v0.6 process candidate pending shell buckling and stiffness tests. |
| [0030](ADR-0030-plastic-torsion-path.md) | Plastic torsion path as base; carbon torsion tube as option B | **REOPENED** | `M6` | The torsion architecture is selected only after process allowables and representative-section correlation. |
| [0031](ADR-0031-carbon-pin.md) | Carbon pin in the CORE↔PANEL joints | **CANDIDATE-ONLY** | `M6` | The exact carbon tube/pin couple is a v0.6 modular-joint candidate, not a v2 interface release. |
| [0032](ADR-0032-modularity.md) | Modular CORE + PANEL architecture | **REOPENED** | `M2/M3/M6` | Configuration-controlled modularity is retained; exact CORE/PANEL geometry and the range/sport catalogue are not. |
| [0033](ADR-0033-electronics-out.md) | Motor and battery out of the design | **SUPERSEDED** | `M0` | ADR-0048 requires a bound reference electrical and propulsion configuration for Article #1. |
| [0034](ADR-0034-motor-mount-angle.md) | Motor mount angle as a design parameter | **RETAINED-METHOD** | `M4/M5` | Keep thrust-line angle parametric and close power-on pitching moment; 0.8 degrees is precedent only. |
| [0035](ADR-0035-tpu-hinges.md) | TPU-printed elevon hinges | **REOPENED** | `M6` | TPU versus film hinge technology requires measured stiffness, hysteresis, fatigue and aeroelastic evidence. |
| [0036](ADR-0036-open-community-platform.md) | Community-driven open aircraft platform | **RETAINED** | `All` | The open community platform and human-CAD collaboration model remain programme policy. |
| [0037](ADR-0037-licence.md) | Licence: CERN-OHL-S v2 + CC BY-SA 4.0 | **RETAINED** | `All` | The repository licence decision remains programme policy. |
| [0038](ADR-0038-fixed-fin-variant.md) | Dual directional configuration: finless baseline + passive twin-fin variant (V1) | **SUPERSEDED** | `M0/M5` | ADR-0048 replaces the no-rudder first-flight concept; V1a survives only as comparison evidence. |
| [0039](ADR-0039-filament-dowel-pins.md) | Filament dowel pins in the glued segment joints | **CANDIDATE-ONLY** | `M6` | Filament dowels are a v0.6 glued-joint detail pending the selected structure and joint tests. |
| [0040](ADR-0040-quarter-chord-sweep.md) | Quarter-chord sweep reduced to −15° | **CANDIDATE-ONLY** | `M3` | Minus-15-degree quarter-chord sweep is candidate A, not the redesigned planform. |
| [0041](ADR-0041-salamandra-r1-airfoil-family.md) | Salamandra r1 spanwise airfoil family | **CANDIDATE-ONLY** | `M4` | r1 is immutable reference/coupon geometry and has no flight-wing CAD authority. |
| [0042](ADR-0042-cruise-propulsion-equilibrium.md) | Cruise propulsion is bounded by total power and closed by measured drag | **RETAINED-METHOD** | `M4` | Close propulsion by total battery power and measured drag; APC 8x8, 95 km/h and Kv values are v0.6 data. |
| [0043](ADR-0043-article-1-mass-allocation.md) | Article #1 mass allocation targets the 45 km/h stall requirement | **CANDIDATE-ONLY** | `M2/M3` | The v0.6 mass allocation and 45 km/h closure are comparison evidence; v2 rebuilds the ledger. |
| [0044](ADR-0044-flight-load-envelope.md) | Separate manoeuvre limits, ultimate loads and gust screening | **RETAINED-METHOD** | `M6` | Keep limit, ultimate and gust meanings separate; +6/-3 and 1.5 remain provisional screens. |
| [0045](ADR-0045-article-1-elevon-geometry.md) | Shorten the Article #1 elevons to 35–90 % half-span | **CANDIDATE-ONLY** | `M4/M5` | The 35–90 percent, 28-percent-chord elevon is the E2A starting geometry only. |
| [0046](ADR-0046-single-declaration-contract.md) | One declaration site per physical quantity, enforced by lint and mutation | **RETAINED** | `All` | Single declaration, contract lint and mutation proof remain mandatory calculation architecture. |
| [0047](ADR-0047-low-speed-trim-redesign-candidate.md) | Low-speed trim hold and r2a test candidate | **CANDIDATE-ONLY** | `M4` | r2a-sm5 is the sole next coupon candidate, not a selected redesign airfoil or CG. |
| [0048](ADR-0048-article-1-mission-and-configurations.md) | Article #1 mission, efficiency metric and configuration order | **RETAINED** | `M0–M9` | This is the governing Article #1 mission, configuration and product contract. |

<!-- END GENERATED: ADR redesign disposition -->

## Audit result

The reset produces four substantive outcomes:

1. Only product/governance decisions remain directly binding: PETG as the primary printed
   material, the open-community/licence policy, the executable calculation architecture
   and ADR-0048's mission contract.
2. Analytical disciplines survive independently of old hardware: drag decomposition,
   measured-map propeller matching, explicit carbon load-path credit, control-surface
   aeroelastic treatment, thrust-line coupling, total-power equilibrium and load taxonomy.
3. Every exact v0.6 planform, airfoil, thickness, control, mass, segmentation, joint and
   process choice is now visibly candidate-only or reopened under its responsible gate.
4. The direct conflicts—fast-cruise-only mission, electronics outside the aircraft and the
   passive no-rudder first-flight configuration—are superseded for Article #1.

This disposition does not declare the reopened options bad. It removes their authority to
become requirements merely because extensive calculations already exist.

## Change and promotion rule

A gate may change a disposition only by recording:

- the candidate set and equal-requirements comparison;
- the calculations, sources or physical evidence supporting the change;
- uncertainty and explicit rejection criteria;
- invalidated downstream artifacts; and
- the new or amended ADR that assumes authority.

Promoting `CANDIDATE-ONLY` directly to production CAD without that record is prohibited.
Adding a new ADR without adding it to the machine-readable ledger fails repository
verification.

## Reproduction

```bash
python3 calculations/decision_ledger.py
python3 calculations/verify_calculations.py --fast
```

Passing the ledger check proves complete and consistent classification. It does not prove
the technical validity of a candidate; that remains the responsibility of its owning gate.
