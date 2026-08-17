# Salamandra — Release v0.1.0: Design Package (CAD Baseline)

> **Superseded geometry notice (2026-08-17):** this document describes the original
> v0.1.0 release. Do not use its −20° planform, −119 mm CG, old cradle coordinates or
> 110 km/h limit for new CAD. Guide v0.16 / ADR-0040 now specify −15°, CG −93.8 mm,
> pack −373 mm and initial V_limit 105 km/h. The historical values below are retained
> as a release record. The current package is
> [`v0.2.0`](09-release-v0.2.md); its Design Guide v0.17 is authoritative for CAD.

**Date:** 2026-08-06 · **Tag:** `v0.1.0` · **Status:** RELEASED

This is the first formal release of the Salamandra open 3D-printed FPV aircraft
platform: a complete, self-consistent **design package** for the Cruise configuration
(Article #1, 1300 mm wingspan), handed to the CAD designer as the modelling baseline.

This release is **not** the final flying configuration: per the project's definition
(`docs/05-master-plan.md`, open-points §3), **v1.0** is the configuration actually built,
assembled, balanced and flying with valid blackbox data. This release freezes everything
that is decidable today and names precisely what remains open and what will close it.

---

## 1. What this release contains

| Document | Version | Role |
|---|---|---|
| [`design/Salamandra-Design-Guide-v0.1.md`](../design/Salamandra-Design-Guide-v0.1.md) | **0.15** | The specification for the CAD designer: geometry, structure, parts, integration — every value needed to model the aircraft |
| [`design/Design-Guide-Justification-v0.1.md`](../design/Design-Guide-Justification-v0.1.md) | 0.10 | The **why** behind every value: source, confidence tag, derivation |
| [`design/Design-Guide-Open-Points-v0.1.md`](../design/Design-Guide-Open-Points-v0.1.md) | 0.10 | Everything **not yet fixed**, with the trigger that resolves each item |
| [`docs/00-objectives-and-requirements.md`](../docs/00-objectives-and-requirements.md) | — | Mission specification (Phase 0) |
| [`docs/02-measured-references.md`](../docs/02-measured-references.md) | — | Primary `[M]` measured data |
| [`docs/06-material-mass-variants.md`](../docs/06-material-mass-variants.md) | — | Mass-budget tool results (PETG / AERO / PLA+ policies) |
| [`docs/07-divergence-margin.md`](../docs/07-divergence-margin.md) | rev. 2.0 | Absolute divergence speed — the flight-envelope limiter |
| [`decisions/`](../decisions/) | ADR-0001…0039 | Every architectural decision, published |
| [`research/`](../research/) | I-01…I-20 | Evidence: catalog data, literature, precedents |
| [`calculations/`](../calculations/) | 16 scripts | Reproducible analysis; all validations documented in each script |
| [`CHANGELOG.md`](../CHANGELOG.md) | [1.0]…[1.27] | Full revision history and corrections (C-series) |

The design guide is the single entry point. The justification and open-points documents
are its companions, and the wiki (GitHub Pages) renders the package for browsing.

---

## 2. Verification status (at release)

Every value that drives a decision is backed by a calculation, a measured datum or a
published reference, and every calculation script is reproducible and self-validating.
**All scripts pass their validation cases** at the release commit:

| Script | Analysis | Validations |
|---|---|---|
| `vlm_ala_volante.py` | Neutral point, load distribution (VLM) | pass |
| `weissinger_np.py` | Independent NP cross-check (Weissinger-L) | pass |
| `balance_cg.py` | CG reachability, pack stations | pass |
| `mass_budget.py` | Mass budget, material variants | 12 |
| `divergence.py` | Absolute divergence (FEM + independent shooting) | 14 + cross-check 0.07 % |
| `launch_speed.py` | Hand-launch feasibility (rev. 2) | 9 |
| `boom_flexion.py` | Nose-boom and fin-spar structure, channel kinks | 13 |
| `yaw_stability.py` | Directional stability, fin sizing | 6 |
| `joint_pin_trade.py` | Pin material trade | 5 |
| `filament_dowel_pins.py` | Dowel-pin shear redundancy | 6 |
| `elevon_authority.py` / `servo_torque.py` / `ventana_torsion.py` | Control and trim authority | pass |
| `b3_screening.py` / `calibra_xfoil_e387.py` | Airfoil screening toolchain | pass |
| `battery_pack_layout.py` / `inav_fc_match.py` / `fpv_power_budget.py` | Pack layout, FC catalog, FPV power | pass |

Two cross-checks anchor the analysis: the neutral point is confirmed by two independent
methods within 3 mm (VLM vs Weissinger-L, I-15 §6.3), and the divergence model's FEM
weak form agrees with an independent flux-form shooting to 0.07 % (docs/07 §2).

---

## 3. What is decided (frozen for this release)

- **Geometry:** b 1300 mm, S 0.282 m², AR 6.0, λ 0.50, Λ_c/4 −20°, t/c 13.5 % → 9 %,
  dihedral polyhedral 0/1.07/1.53/2.0° (kinks at y = 195/347/498), twist working value
  +3.0° (parametric, C5), station table, chord/LE/TE line equations (guide §4).
- **Segmentation and printing:** CORE + 3 segments per half (cuts 347/498, spans
  152/151/152 mm), 45° airfoil-roll orientation, PETG 2 perimeters 0.9 mm + gyroid 5 %
  (guide §6.5).
- **Structure:** three-cell section (D-box 0–0.30, closed box to 0.72), carbon tube
  Ø12×1.0 + pin Ø6 in straight channels (Ø12.4–12.6 / Ø6.3–6.5), filament dowel
  redundancy, R-JOINT ≥ 5× (guide §6.2–6.4).
- **Prototype 0.1 materials (user decision):** aluminium nose boom **Ø8/int6** +
  printed cradle ≈ 41 g (two-support arrangement, `boom_flexion.py`), Ø3 aluminium fin
  spar; carbon optimisation deferred (ADR-0015).
- **Elevons:** separate parts at x/c 0.72–1.00, span 195–585, TPU hinge strip, balance
  pocket 40×14×12 mm, dual actuation, 12–15 g servo class (guide §6.6).
- **Integration:** CORE outer-mold constraints (boom, cradle, rear pod, sockets,
  avionics stations, FPV mounts), mass budget 1697 g AUW, CG −119 mm (SM 8 %),
  propulsion reference (APC-E 8×8, 28-class 500–550 KV), avionics (INAV/ArduPilot,
  pitot mandatory), assembly and control setup (guide §6.7–§8–§12).
- **Flight envelope rules:** V_NE 160 km/h, **V_limit 110 km/h** for first flights
  (≈ 160 if the S3 coupon confirms G_XY ≈ 0.69 GPa), load +6/−3 g, hand-launch gate
  V_suelta ≥ V_stall with the declared technique (guide §11–§12).

## 4. What remains open — and what closes it

| Item | Current value | Closing trigger | Tracked as |
|---|---|---|---|
| **Airfoil** | Provisional: MH 60-12 % scaled 13.5 % root / 9 % camber-compensated tip; geometry is swappable (external coordinate file) | Calibrated B3 screening (G2); E2 flight polar as final `[M]` | **OP-02** |
| **Twist value** | +3.0° working, parametric in CAD | Re-derived from the fixed airfoil Cm0 | C5 (OP-03) |
| **CORE outer shape** | Binding constraints given; body shape is designer's choice | F2 mass model with real CAD geometry | **OP-21** |
| **Dihedral** | 2.0° polyhedral (defined piecewise) | Phase-1 stability verification, first flights | OP-04 |
| **Servo/hinge final choice** | Class and pockets fixed; TPU hinge baseline | Stiffness characterization (C7/S6), flight tests | OP-10 |
| **Motor/prop final units** | Reference class given (not prescribed) | Matching table (D3/D4) and bench tests | OP-12/13 |
| **Absolute divergence** | V_limit 110 km/h; levers declared | S3 torsion coupon → I-12 → E7 Southwell | **OP-29** |
| **Boom/printed structure masses** | Budget values 600/41 g etc. | Fusion 360 mass properties (P2) | OP-24/28 |
| **R-CG across pack configs** | Reference 6S1P fully compliant | Requirement re-derivation in F2 | OP-23 |

Nothing in §4 blocks the CAD work: the airfoil is swappable by design, and the CORE
shape is open within binding constraints **by design**.

---

## 5. Constraints the designer and the build must respect

1. **Do not change the wing surface**: planform, thickness schedule and section family
   are continuous across CORE and panels; the airfoil is a swappable external component,
   not a re-model.
2. **Model the explicit features**: web at x/c 0.30, channels, collars, cavities,
   sockets — the slicer will not create them (guide §6.8).
3. **Channels stay straight**: the dihedral kinks fit the 0.2–0.3 mm radial clearance
   (`boom_flexion.py` §6); do not bend the tube in CAD.
4. **CORE trailing edge is fixed** (no elevon on the CORE); elevons are separate parts.
5. **Mass is a requirement**: every modelled part must be weight-checked against the
   §7.1 budget (shell 600 g, boom 41 g, cradle ≤ 15 g); F2 arbitrates against C16.
6. **CG is a requirement**: −119 mm from root c/4, verified with the balance tabs;
   only the 6S1P reference pack reaches the band.
7. **Flight limits are binding**: V_limit 110 km/h, load +6/−3 g, launch per §12 step 0.

---

## 6. How to work with this release

- **CAD designer:** model from the design guide; raise any value that cannot be realised
  (clearance, printability, fit) as an issue against this repository, referencing the
  guide section — the open-points document records the resolution.
- **Builders:** follow the assembly sequence (§12); the verification lote (torsion
  coupon S3, dowel-fit check OP-27, wall-thickness probe, 45° fragment) can be printed
  **before** the full CAD is finished.
- **Contributors:** see [`CONTRIBUTING.md`](../CONTRIBUTING.md) and the wiki's
  "Contributing" page.
- **Feedback:** open an issue at <https://github.com/bultodepapas/salmandra/issues>.

Release checklist (closed): docs consistent (guide/justification/open-points/CHANGELOG
in sync), all scripts ALL PASS, wiki generates with zero unresolved links, CHANGELOG
entries [1.10]–[1.27] intact, tag `v0.1.0` on `main`.
