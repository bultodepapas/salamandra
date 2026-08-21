# Changelog

Continues the project's correction log. **Errors are documented because they affected intermediate conclusions.** The error history is part of the product: it is what allows trust in what remains standing.

---

## [1.46] — 2026-08-21

**C55 — the repository had detailed subsystem work but no current master design contract;
the roadmap assumed the selected geometry before mission, hardware and architecture had
been revalidated.**

- Replaced the former F1→F6 roadmap with the canonical Master Design Plan v2.0. Its M0→M9
  gates run from mission/scoring through measured hardware, a 3-D mass skeleton,
  equal-requirements architecture selection, printed aerodynamic/structural evidence,
  human CAD handoff, ground qualification and instrumented flight.
- Reopened arbitrary range/endurance targets and retained `≤1.15 Wh/km at 95 km/h` only
  as a legacy comparator. Efficiency is now the primary multi-state objective; practical
  agility is a handling/control-reserve requirement rather than an arbitrary roll target.
- Fixed the working electronics architecture early enough to design around it: 6S1P P42A
  first prototype, 8S1P study module, APC E 8×8 / 500–550 Kv 6S datum, two digital
  12–15 g elevon servos, full-size SpeedyBee F405 WING-class instrumentation and a front
  DJI O4 installation. Exact bought-in parts remain subject to measurement and bench gates.
- Made the equipment mass skeleton ↔ wing/neutral-point loop the formal design method and
  moved fuselage OML selection after that loop converges. Battery adjustment is at least
  20 mm total travel, kept separate from connector and installation allowances.
- Reopened −15° forward sweep. The v0.6 aircraft is candidate A and must compete against
  optimized straight and aft-swept tailless families under identical requirements.
- Defined reversible `SALAMANDRA-R` (rudder-capable vertical module, first flight) and
  `SALAMANDRA-CLEAN` configurations. Existing passive twin-fin V1a remains one candidate,
  not the redesigned-aircraft decision.
- Updated the README, inherited objectives file, docs index and concise Design Guide so
  none authorizes production CAD while Gate M0 and the architecture trade remain open.
  No released v0.6 numerical geometry or calculation changed.

---

## [1.45] — 2026-08-21

**C54 — the cruise-only trim closure hid an infeasible low-speed/CG corner and used an
incomplete section-moment model.**

- Reopened the r1 airfoil, twist, elevon and CG decisions. The previous constant-`Cm0`
  screen requires approximately +27° to +37° at 45 km/h, outside the +/-20° mechanical
  travel in part of the CG band; it cannot support release of new wing CAD.
- Added `low_speed_trim_redesign.py`, which evaluates root/mid/tip section polars at the
  local lift coefficient and couples their `Cm(CL)` and control effect to the aircraft
  VLM over 45–105 km/h and the complete +/-5 mm CG band. Positive deflection is now
  unambiguously trailing-edge down.
- Selected r2a only as a physical-test candidate: +3.0°/+2.5° root/tip reflex, +3.0°
  wash-in and 5% nominal static margin. Its XFOIL screen stays within 11.03° absolute
  trim, but 22 of 30 cases require bounded control extrapolation and therefore provide
  no physical release evidence.
- Added E2A, requiring measured printed root/mid/tip specimens with their real trailing
  edge and hinge. Release requires every speed/CG case inside +/-15° nominal trim, its
  95% uncertainty bound inside +/-20°, 10% local `CLmax` margin and no tip-first stall.
- The XFOIL cache key includes its exact executable hash and model schema. The official
  XFOIL 7.00 build used for the prediction matrix is retained outside the repository;
  its SHA-256 is recorded in the generated metadata.

---

## [1.44] — 2026-08-20

**C53 — the battery catalog multiplied ampere-hours through a series string, and the
6S/8S choice had no coupled packaging, balance or aircraft-level calculation.**

- I-16 printed 4S1P/6S1P P42A capacity as 16.8/25.2 Ah. A series-only string retains
  the cell's **4.2 Ah**; voltage and energy, not Ah, multiply by cell count. Corrected
  `battery_pack_layout.py` and the published I-16 tables, and added a validation guard.
- Added I-32 and `battery_6s_8s_trade.py`. The calculator uses current P42A v4 maximum
  dimensions and enumerates all **18 six-cell / 20 eight-cell** rectangular layouts.
  It separates the manufacturer's 15.5/14.7 Wh typical/minimum rating from the
  15.12 Wh arithmetic nominal cell energy.
- The installed design cases are **6S 445 ± 5 g / 90.72 Wh** and
  **8S 585 ± 5 g / 120.96 Wh**. The 8S pack centre solves 62.2 mm aft of 6S, but
  CLEAN becomes **1693.25 g / 46.00 km/h**, failing the 45 km/h gate by 72.9 g.
- The complete common-bay screen now distinguishes the user's flat/narrow option
  (**340.5 × 44.0 × 22.6 mm** pack union) from flat moderate-width
  (**246.7 × 70.8 × 22.6 mm**) and stacked alternatives. Rail length includes the
  one-ended lead envelope and ±10 mm pack travel; dimensions remain pre-wall `[E]`.
- No design baseline changes: Article #1 remains the released 6S1P power system, and
  no 8S motor, ESC, PDB, bay or OML is authorized by this research calculation.

---

## [1.43] — 2026-08-19

**C52 — the repository was renamed and the documentation site still pointed at the old
name.**

- `salmandra` → **`salamandra`**. GitHub redirects the repository URL, so clones and links
  keep working, but **GitHub Pages does not**: the site is served from
  `https://bultodepapas.github.io/salamandra/` while `wiki/base.mjs` still declared
  `salmandra`, which is where the Astro `base` and every internal link come from. The
  published site would have resolved its own navigation against a path that no longer
  exists.
- `wiki/base.mjs` exists precisely so the deployment identity is declared once — but eight
  further files had re-typed the old name in `editUrl` frontmatter, 404 links and README
  URLs. Single declaration, defeated by copy-paste, again (ADR-0046 in the documentation
  layer this time).
- Fixed in all nine places; the local `origin` remote is repointed. Verified: strict
  generation, reference check, production build and **18,204 built-site links across 115
  pages** all pass on the new base.
- No engineering value, drawing or gate is affected. Release `v0.6.0` remains the current
  release; this is post-release documentation infrastructure.

---

## [1.42] — 2026-08-19

**Release v0.6.0 — twin-fin directional architecture and the parametric fuselage
programme.**

- Design Guide **v0.24** (concise + Advanced), justification/open points **v0.19** and
  [`docs/16-release-v0.6.md`](docs/16-release-v0.6.md) are the released record.
- **The two shapes v0.5.0 left as sketches are now derivations.** The centreline fin
  (rejected in C47) is replaced by two CORE-rooted fixed fins at y = ±140 mm whose station
  is the output of a coupled clearance/mass/CG trade (C48, I-30), and the fuselage stops
  being ~50 hand-placed Bézier control points inside the drawing generator: I-28
  Revision 3 with `fuselage_contract.py`, `fuselage_geometry.py` and `fuselage_trade.py`
  generates a superelliptic body around the equipment skeleton and **audits containment**,
  so a candidate body can now fail a check.
- **Released twin-fin values:** total `S_v` **6.1437 dm²**; each fin **b_v 247.9 mm**,
  `c_r` **170.9** / `c_t` **76.9 mm**, AR_v 2.0, taper 0.45, Λc/4 **15.064°**; fin AC
  **x = +115.5 mm**, arm 209.3 mm; lower assembly **48.73 g** against the 60.00 g
  allocation; V1 **1601.98 g / 44.74 km/h**; V1 battery station **x = −363.27 mm**;
  propeller clearance 29.4 mm nominal, 13.4 mm residual radial, 8.33 mm axial, zero
  projected overlap.
- **Fuselage state, stated honestly:** `integrated_spindle-000` is the review selection
  with `geometry_feasible: true` and **`aircraft_feasible: false`**. Maximum section
  9300 mm² at x = −22.6 mm sits inside the root band, with one dominant peak, no
  payload-to-root neck and no long parallel sides; every audited equipment envelope passes
  with margin. **All OML dimensions remain `[I]` and take no structural credit.**
- Drawing set grows to **six manifest-verified A3 sheets** with the new `SLM-FUS-001`
  fuselage review and `SLM-FIN-001` twin-fin review.
- Packages corrections **C45–C51**. C49, C50 and C51 were found while cutting this
  release; C51 was a required CI step failing on `main`.
- **Engineering delta:** the V1 directional architecture and the body. Unchanged: planform,
  Salamandra r1 airfoil and 3.0° wash-in, ADR-0045 elevon geometry, materials, load
  envelope, CG target, the 105 km/h operational cap and the 160 km/h article `V_NE`.

---

### Corrections in this release

**C49 — one numeric-stack support window was declared in three places, with two different
floors, and CI was testing a numpy the code cannot run on.**

- `calculations/requirements.txt` declares `numpy>=2.0,<3.0` and states that the floor is
  hard because `servo_torque.py`, `elevon_sizing.py` and `fuselage_geometry.py` integrate
  with `numpy.trapezoid`, which exists only from numpy 2.0. It further promises that
  "`design_config.py` enforces this floor at import time so the failure is a named error
  and not an AttributeError three modules deep."
- `design_config.NUMPY_MINIMUM` was **`(1, 24)`**, and the `calculations.yml` matrix still
  pinned **`numpy==1.24.4`** on its floor job. On numpy 1.26.4 the suite therefore failed
  with exactly the `AttributeError: module 'numpy' has no attribute 'trapezoid'` the
  comment promised to prevent, three modules deep, in `fuselage_geometry.py`,
  `fuselage_trade.py` and `generate_blueprints.py`.
- The enforced floor is raised to **`(2, 0)`** and the CI floor job moves to
  **`numpy==2.0.2`**, so requirements, enforcement and CI state one window. Verified: on
  numpy 1.26.4 the import now raises the named contract error instead of the
  AttributeError.
- This is the single-declaration failure (ADR-0046) escaping the code contract into the
  *dependency* contract, where `contract_lint.py` does not look. The lesson is the same
  one C44 taught for prose: what the linter does not read, review must.

**C50 — the released twin-fin geometry moved after C48 and the changelog was not
re-derived.**

- The C48 entry published the intermediate solution: total 3.4737 dm², 186.4 mm span each,
  128.5/57.8 mm chords, taper 0.45, Λc/4 20.379°, x_AC ≈ +280 mm, battery at −386.74 mm and
  V1 1615.63 g. The subsequent pre-release refinement moved every one of those numbers.
- The **released** values are those in §3.1 of [`docs/16-release-v0.6.md`](docs/16-release-v0.6.md):
  **6.1437 dm² total, 247.9 mm span each, 170.9/76.9 mm chords, Λc/4 15.064°, x_AC +115.5 mm,
  battery −363.27 mm, V1 1601.98 g / 44.74 km/h**. The guides, ADR-0038, I-29, I-30 and the
  drawings already carried them; the CHANGELOG did not.
- **Failure mode #3 again, in the release window this time.** The refinement updated eleven
  documents and the generated sheets and stopped one file short. C48 keeps its text as the
  record of that step, with a pointer to this correction.

**C51 — the link rewrite that exists to preserve traceability was breaking the audit's own
evidence links.**

- `docs/12` cites its measured findings as line references into the source
  (`../calculations/servo_torque.py#L67`). The wiki generator rewrites every
  `calculations/*.py` link onto the generated reproduction-guide page **and carried the
  line anchor with it**, where no such anchor can exist. Result: **14 built-site integrity
  failures**, every one of them an evidence link of the audit document, and
  `npm run check:site` — a required step of the `docs.yml` workflow — failing on `main`.
- Line-anchored script links now resolve to the repository source file, where `#L67`
  genuinely works; plain script links still resolve to the reproduction guide. Verified:
  `check:site` reports **18,187 internal links across 115 pages OK**.
- The defect had nothing to do with the documents that failed. A generator that silently
  rewrites references is infrastructure, and infrastructure needs the same rule as a
  calculation: state what result would make it fail.

---

## [1.41] — 2026-08-19

**C48 — fin placement, propeller clearance, mass/CG packaging and side-view geometry were
not one coupled calculation.**

> **Superseded by C50:** the fin figures below are the intermediate solution of this step.
> The released geometry is 6.1437 dm² total, 247.9 mm span each, 170.9/76.9 mm chords,
> Λc/4 15.064°, x_AC +115.5 mm, battery −363.27 mm and V1 1601.98 g / 44.74 km/h.

- Replaced the assumed `x_AC = +285 mm` and vertical-TE planform with a reproducible
  +225…+325 mm station trade. The first mass-feasible minimum-score knee is +280 mm.
- Re-derived V1a as a 25°-LE swept trapezoid: 3.4737 dm² total, 186.4 mm span each,
  128.5/57.8 mm root/tip chords, taper 0.45 and Λc/4 20.379°.
- Derived PETG volume, aluminium spar mass and carbon-boom mass from geometry. The lower
  complete module is 59.97 g, leaving 0.03 g against the provisional 60 g allocation.
- Added the iterative V1 package solver. It closes the released CG in two passes by adding
  17.81 mm of nose structure and 2.40 g of support mass, placing battery/camera/VTX at
  x = −386.74/−463.79/−429.61 mm. V1 is 1615.63 g and 44.93 km/h analytically.
- Added a shared 3-D aircraft scene and inflated propeller hazard. Boom clearance is
  29.4 mm nominal / 13.4 mm residual after the explicit 16.0 mm allowance. Side axial
  overlap is reported but rear projection proves analytical lateral separation; F2 remains open.
- Rebuilt the V1 side OML from its solved layout (757.51 mm versus 739.70 mm CLEAN), added
  the complete electronics skeleton and rear clearance proof, and regenerated the fin and
  mass-skeleton sheets from the same Python objects.
- Added I-30 with the equations, trade table, evidence boundary and remaining physical gates.

---

## [1.40] — 2026-08-19

**CAD documentation split — no technical baseline change.**

- Replaced the 67 kB designer entry point with a concise canonical CAD execution guide
  organized around geometry, interfaces, packaging, mass limits and handoff gates.
- Renamed the former full document to `Salamandra-Design-Guide-Advanced-v0.1.md`; it
  remains the canonical source for engineering context, calculation results, release
  migration and detailed traceability.
- Kept version 0.23 and all released dimensions unchanged. The documentation site now
  publishes both guides, while the primary Design Guide URL resolves to the concise one.
- Corrected the stale advanced-guide component-map row so it agrees with its own released
  V1 definition: two fixed fins, one on each aft CORE boom.
- Added a maintainer release guide and an explicit README map explaining the distinct
  authority and audience of the concise guide, advanced guide, justification and
  open-points register.
- Added the current manifest-controlled SVG drawing set to both Design Guides, with
  `SLM-GA-001` as the visual entry point and explicit task/authority guidance for all six
  generated sheets. The links follow the stable canonical filenames and therefore resolve
  to the latest regenerated drawings.

---

## [1.39] — 2026-08-19

**C47 — the centreline-fin carrier was physically incompatible with the pusher propeller
and arose from a visual misreading of the reference aircraft.**

- Rejected the floating single-fin/carrier architecture after joint side/top-view review:
  its root extended 84.1 mm behind the body OML and its centreline load path crossed the
  x = +235 mm propeller plane.
- Reviewed NASA X-48B/X-48C and the official TBS Chupito/Mojito manuals. The transferable
  precedent is an integrated fin/load path at a usable aft station, not a plate behind a
  rotating propeller. Research and the quantified architecture trade are in I-29.
- Selected two passive fixed fins on aft CORE booms at y = ±140 mm. The 18 × 14 mm boom
  envelopes give 29.4 mm inner radial clearance to the Ø203.2 mm propeller and support the
  complete root chord.
- Re-derived V1a from the same nominal `Cnβ` target with no slipstream credit: total area
  3.4404 dm²; each fin 185.5 mm span, 142.7/42.8 mm root/tip chord, AR 2.0, taper 0.30,
  Λc/4 21.991° and x_ac +285 mm. Added an uncredited dorsal root-fillet envelope.
- Connected both fin shells/mounts, both LE spars and both aft booms to the mass and 3-D
  equipment models. Lower assembly mass is 59.20 g; V1 is 1612.45 g / 44.9 km/h and its
  required battery station is 18.47 mm beyond current travel. These remain F2 gates.
- Regenerated and visually reviewed SLM-GA-002 and SLM-FIN-001. The dedicated fin sheet
  now includes a top-view propeller-clearance proof; both SVGs remain draft review data.

---

## [1.38] — 2026-08-19

**C46 — the V1 fin drawing and yaw model described different planforms, and the
published stability band did not span independent uncertainty corners.**

- Replaced the separate 12° aerodynamic sweep and vertical-TE SVG construction with one
  `FinGeometry` object. The retained vertical trailing edge derives Λc/4 = 7.125° and
  supplies area, AR, taper, MAC, AC and all four vertices to aerodynamics, equipment and
  drawings. Validation now checks every invariant instead of area/AR only.
- The V1a root LE/TE are x = +244.4/+349.1 mm. The corrected root requires an 84.1 mm
  carrier beyond the current x = +265 pod; the former +30 mm / x = +295 concept is
  geometrically insufficient and retired.
- Replaced paired uncertainty cases with independent extrema and separated powered
  η = 1.25 from motor-off η = 1.00. V1a is −0.00029…+0.00119/deg powered and
  −0.00057…+0.00087/deg motor-off. V1b has higher powered margin but also retains a
  negative full motor-off lower corner; neither is flight-test closure.
- `fin_drag()` now uses the actual 85.5 mm trapezoidal MAC instead of an unrelated
  163 mm chord surrogate. V1a becomes ΔCD0 ≈ +0.0015 and +10.2 % energy `[E]`.
- Corrected the impossible enclosed Ø3.2 mm channel inside a 3.0→1.5 mm plate: the Ø3 mm
  aluminium rod is now explicitly an external leading-edge nose in an open seat `[I]`.
- The revised lower fin model is 42.55 g and V1 is 1595.80 g before the still-open carrier
  mass. Corrected fin mass centres move the required pack station to −375.48 mm, 4.28 mm
  beyond current travel; the stopped solution remains inside the released CG band.
- Added generated A3 sheet `SLM-FIN-001`, strengthened semantic/geometry checks and made
  the relevant Windows CLIs configure UTF-8 output explicitly.

---

## [1.37] — 2026-08-19

**I-28 Revision 3 — rejected the box-derived lifting saddle and replaced it with a
constraint-driven integrated spindle.**

- Equipment AABBs are now containment inequalities only. The battery's real envelope,
  not the long cradle box, constrains the outer mold line; the cradle and nose tube are
  separately declared structural corridors.
- The reference body uses bounded, slope-limited quintic Hermite segments with C2 joins.
  This removes both global-cubic overshoot and the flat shoulders produced by zero-slope
  station blending. Asymmetric superelliptic sections remain limited to exponent 3.2.
- The rounded-nose operand now starts 22.0 mm ahead of the camera lens plane. The camera
  aperture Boolean remains an explicit open CAD gate, so the review mesh cannot be
  mistaken for a flight-ready optical installation.
- Added hard section-area gates: one dominant maximum at x = −22.6 mm inside the root
  band, no payload-to-root neck, and no long parallel-sided run. All nine inflated
  central envelopes pass; the limiting motor margin remains positive.
- Replaced the canonical artifact with `integrated-spindle-body.obj` and regenerated the
  GA, side-elevation and FUS review sheets from that same NumPy source. The rejected
  `lifting-saddle-body.obj` remains only as a regression fixture.
- The current gross operand is watertight and reports approximately 0.228 m² wetted area,
  4.916 L volume and a non-additive 261 g gross 0.9 mm PETG screen. Aircraft feasibility
  remains false until the declared battery, reserve-mass, Boolean-union, NP/trim, wing
  installation, camera-aperture and printable-shell gates close.

---

## [1.36] — 2026-08-18

**I-28 — the provisional fuselage is now one audited 3-D source instead of unrelated
2-D styling curves.**

- Added a stdlib design/authority contract and a NumPy analytical body generator around
  the body-owned subset of the CG-derived equipment skeleton. Three bounded asymmetric
  superelliptic families prevent a cylindrical default while hard envelopes cannot be
  removed by the styling controls.
- The canonical `lifting_saddle` review mesh spans x = −452.70…+265.00 mm, is watertight,
  encloses all nine central envelopes and reports 0.1583 m² gross wetted area, 2.195 L
  volume and a non-additive 180.9 g gross 0.9 mm PETG skin screen.
- Added deterministic seeded family/trade output in `geometry/fuselage/provisional/`,
  including an ASCII-stable manifest and OBJ. Feasibility-first/Pareto bookkeeping does
  not claim an aerodynamic optimum.
- GA-001 and GA-002 now project this common loft. New generated sheet `SLM-FUS-001`
  overlays plan/side envelopes, five transverse sections, containment margins, topology
  and the aircraft-level blockers.
- Added analytical, regression and mutation coverage. The body operand is geometrically
  feasible, but aircraft feasibility remains false pending exact V1 battery reach,
  physical location of 92.88 g reserves, net wing/body mass ownership, body-inclusive
  NP/trim, wing installation audit and printable structural/thermal closure.

---

## [1.35] — 2026-08-18

**C45 — the O4 VTX was ahead of the FPV camera in the 3-D equipment model.**

- Aircraft forward is −x, but E18 was at x = −387.1 mm while E19 was at
  x = −418.0 mm. The drawing symbol also used an unrelated side-view height and
  omitted the camera-to-VTX link, so the generated sheets concealed the reversed
  installation.
- E18 is now fixed on y = 0, looking along −x, with its measured 13.44 mm body
  extending aft from the forward cradle plane. The derived centre is x = −445.98 mm
  and the lens face is x = −452.70 mm; E19 remains aft at x = −418.0 mm.
- The 3-D centre-distance lower bound is 45.99 mm against the measured 50 mm coax.
  Connector exits, bend radius and a service loop remain an F2 CAD gate: passing the
  lower-bound calculation does not release a cable route.
- The change moves the 3.10 g camera forward and therefore re-derives the coupled
  battery solution: CLEAN x = −337.74 mm; V1 requires −373.73 mm against the
  −371.20 mm forward stop. The re-derived fin model is 42.80 g and V1 is
  1596.05 g; both remain within the prior acceptance conclusions.
- `balance_cg.py` and `equipment_layout.py` now fail if the camera is not flush,
  forward-facing, centred, fixed, ahead of E19, or within the coax limit. All three
  generated arrangement/equipment views show the same envelopes and cable relation.

---

## [1.34] — 2026-08-18

**Release v0.5.0 — verification integrity and the connected design contract.**

- Design Guide **v0.23**, justification/open points **v0.18** and
  [`docs/13-release-v0.5.md`](docs/13-release-v0.5.md) are the released record.
- The audit in [`docs/12`](docs/12-calculation-system-audit-and-remediation.md) measured,
  by executing the code, that v0.4.0's "connected" baseline was partly nominal: twelve
  quantities declared twice, a hand-copied neutral point, a factor-1.76 yaw-inertia
  contradiction, checks that could not turn red and a CI that aborted at install time.
  C35–C43 close that programme (WP1–WP5 complete; WP6 structural/physics items remain).
  **C44**, found while cutting the release, is the same failure mode surviving in prose:
  four documents still quoted the pre-C40 yaw modes, including the E8 acceptance
  criterion.
- **[ADR-0046](decisions/ADR-0046-single-declaration-contract.md)** makes the rule
  executable: `design_config.py` owns chosen inputs, `aero_contract.py` derived
  aerodynamics, `drag_model.py` the polar; `contract_lint.py` fails a second declaration
  and `mutation_test.py` proves the suite can fail.
- **ADR-0045 elevon geometry is released**: 357.5 mm surfaces at y 227.5…585.0 mm, two
  servos at y ±406.25 mm, 32.5 mm fixed PANEL-root bridge. Existing 390 mm elevon solids,
  hinge strips, pockets and balance values are obsolete for Article #1.
- The four generated A3 drawing sheets become part of the released package, published
  from one manifest with a SHA-256 per sheet.
- Verification at release: **112 cross-module contracts, 28 deterministic CLIs, 19/19
  seeded defects caught**, drawing set current, strict wiki generation, reference check
  and production build passing, `git diff --check` clean. Full suite 36.5 s.
- **Engineering delta from guide v0.22:** one published result moves — the V1a yaw mode,
  ω_n 4.03 → 5.35 rad/s, ζ 0.197 → 0.231 (C40). Nothing else physical changes: no
  planform, airfoil, twist, material, mass, CG station, propulsion boundary, 105 km/h
  operational cap or 160 km/h article `V_NE`.

---

### Corrections in this release

**C44 — C40 corrected the yaw inertia but did not re-derive the documents that quoted the
old modes.**

- C40 replaced the `[E]` 0.28 kg·m² yaw inertia with the `[D]` 0.1587 kg·m² derived from
  the 3-D mass model, and republished the V1a mode from `yaw_stability.py`. **Four
  documents kept the pre-C40 eigenvalues**: I-20 §5.1/§5.5, the Design Guide stability
  table, the justification row, and — worst — the **E8 acceptance criterion** in
  `tests/README.md`, which is the number a flight test would have been compared against.
- Corrected to the live values: finless worst-case 2-DOF λ = **+8.247/−9.456 s⁻¹**,
  divergence τ **0.16 → 0.12 s**; V1a pair λ = **−1.233 ± 5.205i s⁻¹**, decay
  τ **1.3 → 0.8 s** (ω_n 5.35 rad/s, ζ 0.231), damped across the whole ±15 % inertia band.
  I-20's finless `Cnβ` band is also restated at the live −0.00055 … −0.00141 /deg and
  `Cnr` at −0.083 /rad.
- This is **failure mode #3 in the middle of the release that exists to close it**. The
  lesson is specific and worth stating: `contract_lint.py` and `mutation_test.py` guard
  the *code*; nothing guards a number that has been transcribed into prose. Narrative
  quotations of computed results remain a manual re-derivation obligation, and C44 is the
  evidence that the obligation is real.
- I-23 and `docs/12` retain the old figures **deliberately** — they are historical audit
  records of the state at the time they were written, not live specifications.
- No decision changes. The qualitative conclusion of I-20 is unchanged and slightly
  strengthened: CLEAN diverges faster than previously published, V1a damps faster.

---

**C43 — Three verification checks could not fail, and the suite was never run by CI.**

- `balance_cg.py` asserted "VLM/Weissinger NP agreement < 5 mm" by comparing **two
  hardcoded literals** to each other; `generate_blueprints.py` carried the same check. It
  could only fail if a human edited one of the two numbers, and verified nothing about the
  solvers. Replaced by a live re-derivation of both methods (`aero_contract.py`).
- The companion check "SM is 8 percent MAC" evaluated
  `abs((NP_VLM - CG_TARGET) / MAC - 0.08)` where `CG_TARGET := NP_VLM - STATIC_MARGIN*MAC`
  — algebraically the identity `abs(STATIC_MARGIN - 0.08)`. Worse, it hardcoded `0.08`
  instead of reading `STATIC_MARGIN`, so a legitimate revision of the static margin would
  have turned it **red for the wrong reason**. It now reads the contract and compares the
  solved layout CG against the derived target.
- `servo_torque.py` asserted that the per-servo torque equalled the elevon hinge moment,
  with `HORN_RADIUS_RATIO = 1.0` and `N_SERVOS_PER_ELEVON = 1` — true by construction.
  Replaced by a parameterised lever-arm test: two actuators must halve the demand, and
  halving the horn ratio must halve it again.
- `flight_envelope.py` **asserted that a problem exists**: the reference-gust check
  required the gust to breach the +6/−3 limits. Had the design improved, the suite would
  have reported a failure for a good outcome. It is now a printed diagnostic under `G11`.
- `vlm_ala_volante.py` accepted the lift slope "within 8 percent of Helmbold" — wider than
  any error the discretisation makes, and blind to correction **C17** (a missing MAC
  normalisation), which is the defect class it was supposed to guard. Replaced by exact
  linear-model identities (linearity in α, twist superposition, spanwise symmetry), a
  bounded mesh-convergence statement, and a direct **C17 guard**: re-taking the pitching
  moment about the computed neutral point must give dCm/dCL = 0.
- Root cause of the whole class: nothing measured whether the suite could fail.
  `calculations/mutation_test.py` now seeds 19 deliberate defects — sign flips, dropped
  normalisations, desynchronised copies — and requires each to turn at least one check
  red. Three survived the first run and were real holes; all 19 are now caught.
- `.github/workflows/docs.yml` ran exactly one Python step, `generate_blueprints.py
  --check`. It never ran `verify_calculations.py`. A new required workflow,
  `.github/workflows/calculations.yml`, runs the contracts, every deterministic script,
  the contract lint and the mutation test on a Python × numpy matrix.
- **No geometry, mass or aerodynamic result changed.** What changed is that the checks
  protecting them can now fail.

---

**C42 — Drag was treated three incompatible ways, one of them forbidden by ADR-0009.**

- `CLAUDE.md` and ADR-0009 are explicit: never use a single Oswald factor; always separate
  the viscous term from the induced one. That rule exists because conflating them produced
  correction **C1**. The project honoured it in exactly one place: `yaw_stability.py` held
  `CD_PROFILE_CRUISE = 0.0136` and `SPAN_EFFICIENCY = 0.85` as local literals and added the
  induced term separately. `launch_speed.py` used a single lumped `CD_LAUNCH = 0.08` `[E]`
  with no decomposition at all, and `propulsion_match.py` inverted an *allowable* drag from
  the power budget without a polar.
- `calculations/drag_model.py` is now the single polar, returning the two terms separately
  so a caller that conflates them has to do so visibly. `yaw_stability` and `launch_speed`
  both consume it.
- The decomposition alone gives CD ≈ 0.035 at launch incidence — **2.3× lower** than the
  retired lumped estimate. Adopting that outright would have made the hand-launch analysis
  markedly more optimistic on drag with no new evidence, which is precisely the unwarranted
  -transfer failure mode of **C7/C12**. Instead the launch CD is carried as a declared band
  whose conservative end reproduces the retired 0.08, and the release gate is judged on
  that end, because higher drag is what makes reaching V_release harder. **The published
  launch conclusions are unchanged** (typical throw 12.9 m/s vs V_stall 12.4 m/s).
- `launch_speed.py` also gained the term it was missing entirely: the along-path equation
  was `m dV/dt = T − ½ρV²S·CD`, with **no gravity component and no declared flight-path
  angle**. Below V_stall the wing cannot carry the weight by definition, so the trajectory
  is not level and the sign of the model's conservatism was unstated. The equation is now
  `m dV/dt = T − ½ρV²S·CD − m g sin γ` with γ declared, banded (−10°/0°/+10°) and
  propagated; the released level throw is shown to be the conservative end against a
  descent.

---

**C41 — The speed ladder had no ordering invariant, and V_A sits above the speed being
used as V_C.**

- Five speeds (45 / 95 / 105 / 160 / 180 km/h) carried five different roles and **nothing
  asserted their order**. Any single edit could silently invert two roles.
- Worse, `flight_envelope.py` used the 105 km/h initial limit as the Part 23 design
  cruising speed `V_C` in the discrete-gust schedule, while the manoeuvring speed at the
  +6 g limit is **107.9 km/h (CLEAN) and 109.4 km/h (V1)** — above it. In a V-n
  construction `V_C ≥ V_A` is a structural premise, not a convention. Resolved by
  declaring 105 km/h an **operational cap**, not a `V_C`: the module labels its screening
  speeds accordingly and `design_config.validate_geometry` now asserts the relationship
  explicitly rather than leaving it silent.
- `divergence.py` publishes a first-flight clearance of 110 km/h at the conservative band
  while V_NE 160 and a 180 km/h structural case sit in the same contract. That clearance is
  now an exported function, `operational_speed_limit_kmh()`, and the shared harness asserts
  the operational cap respects it. **G6 remains open**: the conservative V_div of 129.6
  km/h is still short of the 240 km/h criterion, and that is reported, not asserted away.
- `V_NE` also meant two different speeds: `divergence.V_NE` was 160 km/h and
  `yaw_stability.V_NE` was 180 km/h, and the harness codified the confusion. Renamed to
  `V_ARTICLE_NE` and `V_STRUCTURAL`.
- **No speed value changed.** What changed is that they now have declared roles, an
  asserted order, and one name each.

---

**C40 — Two irreconcilable yaw inertias, and a declared band that the code could not
propagate.**

- `yaw_stability.py` carried `I_z = 0.28 kg·m²` `[E]` with a `(0.23, 0.33)` band, while
  `equipment_layout.py` computed **0.1587 kg·m²** from the released three-dimensional mass
  model of the same aircraft. A factor **1.76** disagreement, with the computed value lying
  entirely outside the declared band, and nothing cross-checking the two. The harness
  accepted both in the same run.
- The 2-DOF yaw mode scales as 1/√I_z, so the published frequency was **33 % low**.
  Resolved in favour of the traceable `[D]` derivation: `yaw_inertia()` now reads the 3-D
  mass model, and a contract check requires the two to agree within 10 %.
- **Published result moves.** The V1a reduced 2-DOF pair goes from
  λ = −0.794 ± 3.948j (ω_n 4.03 rad/s, ζ 0.197) to **λ = −1.233 ± 5.205j (ω_n 5.35 rad/s,
  ζ 0.231)**. The qualitative conclusion is unchanged and slightly strengthened: the mode
  is damped, and now stays damped across the whole declared band.
- The residual uncertainty is the idealisation itself — `equipment_layout` represents every
  part as an oriented cuboid, which captures the spanwise mass stations but not the
  distribution inside each shell. That is carried as a declared ±15 % band and, unlike its
  predecessor, is **actually propagated**: the old `IZ_BAND` appeared exactly once in the
  repository, its own definition, and `yaw_modes()` had no inertia parameter at all, so the
  band was unpropagatable by construction.

---

**C39 — The published neutral point was a hand-copied literal quoted from an unconverged
mesh.**

- `balance_cg.py` declared `NP_VLM = -75.8e-3` and `NP_WL = -72.9e-3` as constants, with
  `CG_TARGET = NP_VLM − STATIC_MARGIN·MAC` built on top. The CG target propagates to the
  3-D equipment layout, the yaw model, the battery solve and the drawing set. **Nothing
  re-derived it.** A change to span, area, taper or sweep moved the real neutral point and
  left the literal untouched — the project's most repeated correction (failure mode #3,
  C6) written into the source of its most consequential number.
- `calculations/aero_contract.py` now derives and caches the neutral point, and the
  published values are retained only as **regression anchors with an explicit ±0.5 mm
  tolerance**. Re-derivation reproduces both: VLM −75.79 mm, Weissinger-L −72.90 mm.
- The published pair was quoted at VLM 40×6 and Weissinger ny=100 while the cross-check ran
  at 24×4 and ny=60, and `elevon_sizing` used 80×6. Measured convergence: the VLM neutral
  point runs −76.895 mm (12×3) → −75.482 mm (120×14), Richardson limit ≈ −75.43 mm; the
  Weissinger value runs −73.966 mm (ny=20) → −72.718 mm (ny=300), limit ≈ −72.65 mm. So the
  published figures carried ≈ 0.36 mm and ≈ 0.25 mm of **undeclared discretisation error**,
  quoted to 0.1 mm on top of a 2.9 mm method spread — false precision, failure mode #2.
  `VLM_NY`, `VLM_NX` and `WEISSINGER_NY` are now canonical, and a convergence assertion
  bounds the mesh error at 0.4 mm instead of leaving it unmeasured.
- `docs/09-release-v0.2.md` stated **−75.9 mm** on line 66 and **−75.8 mm** on lines 44 and
  110. The drift had already reached the documents. Corrected to the released value.
- Numerical effect of the change: the CG target moves by **0.017 mm** and the reference
  battery station by **0.04 mm**, against a ±5 mm CG tolerance. Nothing physical moved;
  what moved is that it is now re-derived on every run.

---

**C38 — The documentation CI could not run, so no gate was actually enforcing anything.**

- `npm ci` failed on every job: `wiki/package-lock.json` was missing the optional
  `@emnapi/core` and `@emnapi/runtime` entries its dependency tree resolves, so the install
  aborted before any check ran. The lock file is regenerated and `npm ci` reproduces the
  tree from it.
- `check-refs --strict` failed on 17 references to `E01`, `E18` and `E19`. None was wrong:
  the `E` prefix carries **two** registers and the checker only knew one. Tests are written
  unpadded (`E1`…`E9`, `tests/README.md`); controlled equipment item balloons are written
  zero-padded (`E01`…`E21`) and live in the mass-skeleton reference map that feeds
  `SLM-EQP-001`. Both registers are now read from their canonical sources, retired numbers
  included, and the convention is recorded in `docs/04-conventions.md`.
- Retired equipment numbers became data instead of a comment
  (`RETIRED_MASS_SKELETON_REFERENCES`), and the drawing contract now checks that a retired
  number is never reused. `E10` is the flight controller, so a test register reaching ten
  must be re-prefixed rather than colliding.
- No geometry, number or confidence tag changed. What changed is that the gates in
  `.github/workflows/docs.yml` — referential integrity, markdown lint, strict site
  generation, built-link check and the new drawing gate — now run instead of failing at
  install time.

---

**C37 — The published drawing set had drifted from the generated one.**

- The generator wrote four A3 sheets, but the wiki drawing page described only three:
  `SLM-EQP-001` (equipment mass skeleton) was rendered, copied to the site and never
  listed. The repository README embedded no drawing at all and only mentioned the folder.
  Every sheet description — purpose, scale and authority tag — was maintained by hand in
  two places, so nothing detected the omission.
- Fixed at the source rather than in the text: `calculations/drawing_index.py` now holds
  one registry of sheet number, purpose, sheet scale, authority and reviewer note, and
  writes `geometry/drawings/manifest.json` (title and description read back from the
  rendered SVG, plus byte size and SHA-256) in the same run that renders the drawings.
- `README.md` and `geometry/drawings/README.md` carry generated blocks published from that
  manifest; the wiki expands the same manifest at build time and refuses to build when a
  served sheet does not match its recorded digest. The README now embeds all four sheets
  as SVG, so zoom does not degrade them.
- `python3 calculations/generate_blueprints.py --check` fails on a stale sheet, manifest or
  published block, and now runs in CI on any change under `calculations/` or `geometry/`.
  No geometry, number or confidence tag changed: this is a traceability correction.

---

**C36 — Article #1 elevon geometry selected from a span/chord/tip trade.**

- New I-27/ADR-0045 and `elevon_sizing.py` compare retained, shorter, tip-extended
  and 0.24/0.28/0.32 c surfaces using exact planform integrals, ideal plain-flap
  effectiveness, an 80×6 VLM, connected V1 inertia and the corrected hinge model.
- Each 0.28 c elevon now spans **y = 227.5…585 mm (35–90 % half-span), 357.5 mm**.
  A 32.5 mm fixed PANEL-root trailing-edge bridge separates the hinge from the
  removable joint; the 65 mm fixed tip remains. The servo moves to y = **±406.25 mm**.
- Moving area falls 10.0 %, while the rigid-VLM roll derivative retains 94.5 %.
  Limiting Ncrit-12 trim is +0.500° after ideal 0.28 c flap effectiveness; the hinge
  proxy falls 11.7 %. The DS-939MG factored static margin becomes 1.52× at 180 km/h.
- Moving PETG is estimated at 45 g total and balance allocation at 54 g. The removed
  surface PETG becomes fixed panel material, so only 6 g lead saving is credited:
  **1553.25 g CLEAN / 1596.26 g V1**, with V1 24.1 g below the exact stall-mass limit.
- The connected V1 battery target is 2.72 mm beyond current forward travel, although
  CG remains in the released band. F2 remains open; no flap mode, final throw or
  flutter-speed improvement is claimed.
- Design Guide **v0.22**, justification/open points **v0.17**. Release v0.4.0 remains
  the immutable v0.21 snapshot. The inconsistent interim C35 narrative mass figures
  are superseded by the connected C36 values above.

---

**C35 — Article #1 actuation simplified from four servos to two.**

- ADR-0026 now specifies one midspan servo per 390 mm elevon. The former `sqrt(2)`
  flutter-frequency credit assumed an unmeasured doubling of effective hinge stiffness
  and is withdrawn pending G7 stiffness and modal evidence.
- The corrected single-actuator demand is 0.978 kgf·cm ideal and 1.834 kgf·cm after
  1.5 torque factor / 0.80 linkage efficiency. DS-939MG margin is 1.36× at 180 km/h
  and approximately 4.0× at the initial 105 km/h limit.
- Servo mass falls 50.0 → 25.0 g. CLEAN becomes 1558.5 g / 44.1 km/h; the complete
  V1 lower model becomes 1601.5 g / 44.7 km/h and analytically passes C16 with about
  18.9 g mass margin. F2 measured mass and G7 flutter verification remain open.

---

## [1.33] — 2026-08-17

**Release v0.4.0 — the connected calculation baseline and Article #1 flight-load
definitions become the controlling engineering package.**

- Design Guide **v0.21**, justification/open points **v0.16** and
  `docs/11-release-v0.4.md` are the released record.
- C29–C34 are no longer post-release amendments to v0.3.0: the corrected propulsion,
  servo, yaw, V1 mass, load-factor and maximum-lift semantics are packaged together.
- The released structural convention is **+6/−3 g manoeuvre limit** and
  **+9/−4.5 g ultimate**. The positive V-n branch is reproducible; the negative branch
  remains open pending traceable `CLmin` data.
- The legacy rigid-aircraft gust calculation remains a conservative screen, not an
  adopted design load. G11/E9 must close the nonlinear dynamic response before a gust
  envelope can control structure or operations.
- The package passes 51 cross-module contracts, all 20 deterministic calculation CLIs,
  Python static/compile checks, documentation reference checks and the production wiki
  build.
- **Engineering delta from guide v0.20:** none. No planform, airfoil, twist, material,
  mass, CG, propulsion, CAD dimension, 105 km/h initial limit or 160 km/h V_NE changed.

---

## [1.32] — 2026-08-17

**Flight-load envelope correction — manoeuvre, ultimate and gust loads are now
separate, calculated quantities.**

- **C33, load-factor semantics:** the old `+6/−3, later +9, gust-dominated` line mixed
  three different load definitions. Article #1 now uses provisional **+6/−3 g
  manoeuvre limit loads** and their 1.5× **+9/−4.5 g ultimate structural loads**. +9 g
  is not a future flight target.
- **C34, section versus wing maximum lift:** controlling documents called 0.65 a wing
  `CLmax` while the connected stall chain correctly uses 0.589. I-07 defines 0.65 as
  the local section `clmax` screen and 0.589 as the 3-D wing design `CLmax`; the
  specification and Phase-1 criteria now preserve that distinction.
- **Positive V-n branch:** the connected CLEAN/V1 masses and released CLmax give
  **VA = 109.0/110.4 km/h**. At the 105 km/h initial limit, positive manoeuvre is
  stall-limited to **5.57/5.42 g**. The negative aerodynamic branch remains open
  because no defensible CLmin exists.
- **Regulatory-reference gust screen:** the legacy Part 23 equation is implemented in
  SI and independently checked against its published imperial form. At 105 km/h the
  CLEAN screen gives **+12.94/−10.94 g**, but implies CL 1.37 > CLmax 0.589; it is
  explicitly a nonlinear/dynamic-model mismatch flag, not an adopted structural load.
  The inverse −3 g sensitivity is 5.10 m/s CLEAN / 5.19 m/s V1 equivalent vertical
  gust. G11/E9 retain the physical closure.
- **Connected implementation:** new `flight_envelope.py`, I-24, ADR-0044 and OP-31;
  `design_config.py` owns negative limit and ultimate factor; the verifier now runs 20
  deterministic CLIs and checks the flight-envelope contracts.
- **Test-document correction:** E8 now carries the already-corrected C31 predictions
  (CLEAN divergence τ ≈ 0.16 s; V1 decay ≈ 1.3 s), replacing stale 0.7/1.5 s values.
- Design Guide **v0.20**, justification/open points **v0.15**. No planform, airfoil,
  mass, material, CAD dimension, 105 km/h initial limit or 160 km/h V_NE changed.

---

## [1.31] — 2026-08-17

**Calculation-system integration audit — one numerical design contract, corrected
physics and automated cross-module verification.**

- **C29, propulsion energy boundary:** the v0.3 calculation incorrectly allocated all
  109.25 W of O1 battery power to motor+ESC and called a propeller point an aircraft
  equilibrium despite having no aircraft drag input. The corrected chain reserves
  14.04 W for avionics, O4 Lite and BEC losses, leaving 95.21 W. The APC E 8×8 boundary
  is J 0.923, 8,443 rpm, maximum drag 2.06 N and ηprop 0.671; E2 drag is required for a
  unique equilibrium. Four-cell sizing becomes approximately 713 Kv.
- **C30, servo units:** SI hinge moment had been labelled g·cm after applying a kgf·cm
  conversion, a factor-1000 unit error in the text. The corrected worst ideal demand is
  0.489 kgf·cm per servo; with 0.80 linkage efficiency and SF 1.5, the catalog
  requirement is 0.917 kgf·cm. MG90S margin is 3.68× ideal / 1.96× factored.
- **C31, yaw dynamics:** dimensional yaw-rate derivatives omitted the standard `1/(2V)`
  factor. Corrected CLEAN eigenvalues are +6.25/−7.13 s⁻¹ (unstable); V1 is
  −0.80 ± 3.95i s⁻¹ with approximately 1.3 s decay. The fixed-fin decision stands, but
  the previous 0.8 s finless time constant is superseded.
- **C32, V1 mass chain:** the former 36.72 g fin row represented only an allocation and
  omitted the mandatory 5.70 g aluminium spar from the analytical assembly. The
  complete lower model is 43.01 g, so connected V1 mass/stall are 1,626.5 g and
  45.1 km/h. The 1,620.2 g allocation remains the target, but F2 is reopened by
  6.29 g; a passing calculation suite must not disguise this requirement failure.
- **Integrated numerical contract:** `design_config.py` now owns shared atmosphere,
  speeds, load factor, stall model, mass targets and O1 power as well as geometry.
  Battery mass/envelope, CG, boom, mass, avionics, FPV, propulsion, launch, controls,
  yaw, divergence and aerodynamic tools consume those shared values instead of local
  copies.
- **Verification and model improvements:** new `verify_calculations.py` checks all
  interfaces and can execute all 19 deterministic local CLIs. Launch propagation now
  includes drag and motor delay; the boom uses exact multi-point beam superposition;
  VLM caches/vectorizes its influence calculation; divergence uses the final r1 profile
  (129.6 km/h conservative) while retaining the 105 km/h released limit.
- Design Guide **v0.19**, justification/open points **v0.14**, docs/07 revision 4 and
  research thread I-23 are the corrected technical record. This entry supersedes the
  propulsion, servo and yaw values in [1.30] and earlier entries without rewriting
  their historical audit trail. C32 likewise supersedes the V1 closure claim in
  [1.30].

---

## [1.30] — 2026-08-17

**Release v0.3.0 — the three highest-ROI open design chains are corrected and closed
for CAD: airfoil, propulsion equilibrium and Article #1 mass/CG.**

- **Airfoil-pipeline correction (ADR-0041 / I-15 §8):** the previous thickness routine
  multiplied all ordinates and therefore changed camber/reflex while claiming to
  preserve the mean line. Polar caches also did not identify geometry, and cm0 could
  include post-stall points. The corrected pipeline changes thickness about the mean
  camber line, hashes geometry/settings, fits only the pre-stall branch and uses actual
  local Reynolds numbers. It releases the Salamandra r1 root/tip and station DAT files:
  13.5/9.0 % t/c, +1.0/+0.5° reflex, +3.0° wash-in, −0.06°…+0.39° neutral trim.
- **Propulsion correction (ADR-0042):** v0.2 prescribed the APC E 8×8
  peak-efficiency point without satisfying aircraft thrust/power equilibrium. That row
  requires about 230 W against O1's 109.25 W. The measured UIUC curve now solves at
  J 0.899, 8,667 rpm, 2.42 N and ηprop 0.688. Article #1 is 6S1P, 500–550 Kv; a 4S
  installation needs approximately 730 Kv and is a separate module.
- **Mass/stall closure (ADR-0043):** conventional PETG is retained with a binding 550 g
  shell cap and selected FC/PDB, O4 Lite, four Corona servos and 25 g prop assembly.
  CLEAN is 1,583.5 g / 44.5 km/h; V1 is ≤1,620.2 g / 45.0 km/h. The 36.7 g fin cap
  matches the calculated V1a lower mass bound. The exact modeled ceiling is 1,620.4 g,
  so V1 has only 0.2 g allocation margin and remains an F2 scale
  gate. Coupled balance moves the 6S1P pack to −359.6 mm and the boom to 37.4 g.
- Design Guide **v0.18**, justification/open points **v0.13**, I-22 audit and
  `docs/10-release-v0.3.md` are the released record. The v0.2 numerical case remains an
  automated regression; its provisional profile, −372.7 mm station and 1,685.2 g mass
  are historical, not current CAD inputs.

---

## [1.29] — 2026-08-17

**Release v0.2.0 — safety-corrected CAD baseline, Design Guide first.**

- Design Guide **v0.17** promoted to the controlling release specification, with an
  explicit document-authority order and a breaking migration table from v0.1.0.
- Release rule: do not mix v0.1.0 wing sketches, panels, CORE interfaces or cradle
  coordinates with v0.2.0. Regenerate planform geometry from `design_config.py`.
- Published `docs/09-release-v0.2.md`: package manifest, old/new CAD drivers,
  verification record, known limitations and designer hand-off checklist.
- Companion versions: justification **v0.12**, open points **v0.12**. README and docs
  index now point to v0.2.0 as current; v0.1.0 remains a historical audit record.
- **Engineering delta:** none beyond [1.28]; this entry freezes and releases that
  audited state without pretending the airfoil, mass or measured aeroelastic gates are
  closed.

---

## [1.28] — 2026-08-17

**Highest-ROI design audit — coupled sweep selection, canonical geometry and corrected
elastic-axis uncertainty.**

- **ADR-0040 / I-21:** full −20/−16/−15/−12/−10° trade using 32×5 VLM,
  100-station Weissinger, trim/reflex, section-Cl, self-consistent balance and the NASA
  TP-1685 divergence trend. **−15° selected**; −12° rejected because it requires 4.54°
  equivalent trim against the 3.0° twist + 0.6° reflex cap.
- **Single geometry source:** `calculations/design_config.py` now owns b, S, taper,
  sweep, thickness and stations. Guide v0.16 receives the generated −15° station table.
  **Correction:** v0.15 gave mutually inconsistent tip trailing-edge values (−128.1 in
  the station table and +108.5 in the CAD controls); the correct −15° value is −65.7 mm.
- **Aeroelastic correction:** the enclosed-area centroid x/c = 0.353 was incorrectly
  called the shear centre in revision 2. It is only a geometric diagnostic. Revision 3
  brackets xEA/c = 0.30…0.45 `[E]`: Vdiv 325.3 nominal / **128.8 conservative** /
  91.1 AERO; initial **Vlimit 105 km/h**, 150 only after GXY validation. The shell-alone
  240 km/h claim in ADR-0030 remains unproven.
- **Balance/mass correction:** target CG −93.8 mm; 6S1P P42A at −372.7 mm; cradle
  −473.3…−272.2; hybrid boom 38.2 g; AUW 1685.2 g. The aluminium boom is now a fixed
  hybrid row in `mass_budget.py`, so printed-material policies no longer scale its mass.
- **Yaw/structure correction:** the fin sizing block calculated 2.16 dm² but downstream
  checks still used a stale fixed 2.0 dm². All blocks now consume the calculated area;
  the 2.5 mm solid root is rejected at FS 1.15 and the baseline becomes **3.0 mm**
  (FS 1.65). The Ø3 mm spar is retained for stiffness but receives no strength credit.
- **Elevon-authority correction:** the script reported the current VLM wash-in yield
  (+0.00249/°) but still calculated trim with a stale +0.00338/°. It now uses its own
  computed yield: the favourable provisional polar closes at about **0.6°** reflex,
  while the adverse Ncrit-12 polar needs about **1.9°** and therefore fails the
  permanent-reflex cap. Control authority passes; the final B3 polar is a CAD gate.
- Documents updated: guide v0.16, justification v0.11, open points v0.11 (OP-30 added),
  docs/06 rev. 1.1, docs/07 rev. 3, README and calculation index.

---

## [1.27] — 2026-08-06

**First release — tag `v0.1.0`: Salamandra Design Package (CAD baseline).**

- Guide **v0.15** released (status RELEASED, tag v0.1.0): segment spans added (§6.5,
  C24); new §6.9 bought-in items and consumables table; open items named with their
  triggers (OP-02 airfoil, OP-21 CORE shape).
- **`docs/08-release-v0.1.md`** (new): release notes — package contents, verification
  status (all 16 scripts ALL PASS), frozen vs open items, binding constraints for the
  designer and the build, working and feedback flow.
- Indexes: `docs/README.md` row for docs/08; README release pointer.
- **Corrections:** none — release of the v0.14/v0.15 state with documentation only.

---

## [1.26] — 2026-08-06

**Design guide reorganized as a CAD designer's guide — v0.14 (structure only, no engineering change).**

- **Guide structure** re-ordered for the designer's workflow: §4 reference planform →
  §5 airfoil → §6 structure and parts (with a new **component map** listing the 11 parts
  to model: CORE, 6 segments, 2 elevons, fin, cradle, skid, balance tabs) → §7 mass/CG →
  §8 battery and cradle → §9 propulsion → §10 avionics → §11 flight envelope (stall,
  divergence/V_limit, launch consolidated from old §4) → §12 assembly → §13 references →
  §14 log. CAD method promoted to §6.8.
- **Analysis moved out, nothing lost:** long blockquotes compressed to one-line flags;
  the full rationale remains in `Design-Guide-Justification-v0.1.md` (v0.10: twist
  working-value row, cradle row §9, boom row §6, straight-channel row §5, divergence row
  §8) and the CHANGELOG. Historical bay sizing kept in justification §9 as the
  fit-analysis basis.
- **Values reconciled to the canonical scripts** (no silent changes, corrections listed):
  twist working value **+0.5° → +3.0°** (parametric, C5; target 0.5° with the designed
  section); divergence numbers updated to docs/07 rev. 2 (**275.6 / 151.5 / 107.1**,
  V_limit 110 — the guide's v0.10-era 267.7/121.9 were stale); battery **bay → cradle**
  throughout (§8, assembly step 8 verifies 6S1P only); AUW summary row reconciled
  (1697 current / 1620 design ref.); guide §14 log compacted with CHANGELOG mapping.
- Documents: guide **v0.14**, justification **v0.10**, open-points **v0.10** (OP-01/03/16/
  19/21/23 reworded to the cradle). **Corrections:** stale divergence numbers; stale
  twist value; bay-vs-cradle contradiction; 4S2P balance-verification step.

---

## [1.25] — 2026-08-06

**CAD questions Q1–Q5 answered — guide v0.13 (modelable as-is).**

The 5 questions a CAD designer would raise are now resolved in the guide:

- **Q1 — Cradle replaces the battery bay:** printed cradle (2 halves, 155×66×24 mm inner, ≤ 15 g, Ø8.2 channel gripping the tube, 2× velcro + spring-lock hatch) replaces the internal 200×70×32 bay; pack centred at x ≈ −415 between the two supports; CORE has no bay; boom socket Ø8.2 at z = 0 with a 4-perimeter collar (§7.6).
- **Q2 — Tube/pin channels vs dihedral kinks (`[D]`, `boom_flexion.py` §6):** straight bores Ø12.4–12.6 / Ø6.3–6.5 per flat segment; the kinks (max 1.07°) deviate the tube ≤ 0.19 mm across the joint face — inside the 0.30 mm radial clearance; even forced, the elastic bend is σ 34 MPa (CFRP ~1600) (§7.3).
- **Q3 — Elevon as a separate part:** TPU hinge strip 4×6 mm × 390 mm glued in a 4.2×6.2 groove; balance pocket 40×14×12 mm at x/c 0.74, lid 1× M2, 40 g capacity; the lead amount (not the geometry) closes the ADR-0025 balance in CAD (§7.5).
- **Q4 — Fin section:** symmetric biconvex plate, 2.5 → 1.5 mm, LE r 1.5 / TE 0.8 mm, Ø3 spar in a Ø3.2 LE channel, slot + dowel + M2 mount (§5.4).
- **Q5 — CAD method declared:** solid bodies; slicer makes skin 0.9 + gyroid 5 %; web, channels, collars, cavities, sockets modelled explicitly; CORE torsion box closed to the TE; print orientation is a slicer task.
- Documents: guide **v0.13** (§5.4/§7.2/§7.3/§7.5/§7.6 + CAD-method note), `boom_flexion.py` §6 (kink check, 13 validations ALL PASS). **Corrections:** the internal battery bay is superseded by the cradle (prototype decision, no analysis depended on it).

---

## [1.24] — 2026-08-06

**PROTOTYPE 0.1 materials decided (user): aluminium nose boom Ø8/int6 + Ø3 aft spar — `boom_flexion.py`.**

- **Nose boom = aluminium tube Ø8 / int Ø6 (wall 1.0 mm, measured) + printed cradle (15 g):** the structural analysis found and resolved the governing trap — the tube **cannot cantilever** the 455 g pack (+6 g: σ 322 MPa > 276 yield, δ 57 mm, 5.2 Hz), but the existing geometry (pack centred x −415 between the tip support −516 and the CORE −132) is exactly a **two-support beam: σ 60 MPa (FS 4.6), δ 2.0 mm, mode 21 Hz — PASS** (`boom_flexion.py`, 11 validations ALL PASS). The cradle is a structural requirement; the tip skid is the crush zone.
- **Boom mass ≈ 41 g** (tube 25.8 + cradle 15) — OP-24 target 40 + 2 absorbed (V_stall +0.03 km/h).
- **Ø3 mm aluminium spar along the V1 fin leading edge** (aft, near the TE): root stiffness ×2.05 (EI 0.278 + 0.265 N·m²), 5.7 g, load path vs slipstream buffeting (OP-26).
- **Carbon optimisation deferred** (documented pending, ADR-0015 revision).
- Documents: guide **v0.12** (§7.6 nose boom, §7.2 fin mount, §8.1 table), OP-24/OP-26 updated, mass_budget boom 41 g, calculations/README §16. **Corrections:** none.

---

## [1.23] — 2026-08-06

**Divergence model refined: real profile geometry + literature sensitivity (docs/07 rev. 2).**

Designer's empirical report (printed PETG thin-wall/low-infill parts feel stiffer than
simple calculations) investigated and quantified:

- **Real geometry:** `divergence.py` now computes the torsion box from the actual
  profile coordinates (`geometry/airfoils/mh60-135.dat`): A1 = 0.0310c², A2 = 0.0415c²,
  real arc perimeters, shear centre x/c = 0.353 (e = 0.103c). The k_h = 0.8 rectangle
  idealization validates within 0.4 % (validated as a check). 14 validations ALL PASS,
  C2 cross-check 0.07 %.
- **Results (real geometry):** nominal 275.6 km/h (1.15×), conservative end 151.5 km/h
  (0.63× — FAIL, below V_NE 160), optimistic 521 km/h, AERO 107.1 km/h (not airworthy).
- **Literature sensitivity (docs/07 §4):** in-plane G_XY ≈ 0.69–0.72 GPa from E–ν
  (Özen 2021, CNC Kitchen E 1.9 GPa; Sadaghian 2022's ~0.24 GPa applies to across-layer
  loading, not the wing's in-plane skin path) moves the conservative end to 210 km/h
  (+39 %); gyroid 5 % and real wall 1.0–1.1 mm add ~5–10 % each. **Combined best case:
  242 km/h — touches the criterion but does not guarantee it.** The dominant unresolved
  term remains the sweep factor 0.50–0.70 `[E]` (I-12).
- **S3 expectation declared:** printed torsion coupon should measure G_XY ≈ 0.65–0.72
  GPa → V_div ≈ 200–240 km/h; V_limit 110 km/h for the first flights, raisable to
  ≈ 160 km/h if the coupon confirms the in-plane G.
- Documents: docs/07 rev. 2 (model table, results, §4 sensitivity, S3 expectation).
  **Corrections:** none — the verdict is unchanged, its band is now quantified with
  real geometry and literature.

---

## [1.22] — 2026-08-06

**Launch verdict CORRECTED (I-14 rev. 2) — hand launch IS feasible.**

Designer review challenged the rev-1 verdict ("cannot leave the hand"): the model was
too strict in two respects, now corrected with data:

- **(a) Release gate corrected:** rev. 1 demanded k_safe = 1.20 at the release instant
  (15.3 m/s). The correct gate is **V_suelta ≥ V_stall (12.8 m/s)** — the margin is
  built by motor acceleration at T/W ≈ 1.0 in 0.2–0.4 s.
- **(b) Thrust/throw data corrected:** published throwing biomechanics (van den
  Tillaar, JSSM 2004: 0.409 kg → 21.5 m/s, significant negative linear mass–velocity
  relation → 1.6–1.7 kg band 8–13 m/s, ref 10.5) and the full throw gesture (0.4–0.6 s)
  with the motor at wing-throw idle (0.5–0.67 × hover) add 2–4 m/s.
- **Configuration-class anchor `[M]`:** the TBS Mojito — 1300 mm, ≈ 1800 g, higher
  reported stall (~60 km/h) — is hand-launched in service (TBS manual + community:
  idle 1300 + launch 1850, over-head technique). The Salamandra is the easier case.
- **New verdict:** typical throw = **13.4 m/s (48.4 km/h, k = 1.05) at release, k = 1.20
  in 0.39 s; firm throw = 17.3 m/s (62.4 km/h, k = 1.36)**; weak throw stays below
  stall → technique rule (firm throw ≥ 10 m/s, 0–5° pitch) is part of the spec.
  Torque-roll check: launch T/W ≈ 1.0 inside the community 1.5 threshold.
- Documents: I-14 rev. 2 (correction record), guide **v0.11** (§4/§12), calculations
  README §15. **Corrections:** rev-1 launch verdict (too strict gate + low thrust
  estimate); the divergence findings (docs/07) are untouched.

---

## [1.21] — 2026-08-06

**I-14 executed — hand-launch feasibility quantified (`launch_speed.py`, guide v0.10 §4/§12).**

The open thread that had zero data now closes with the quantitative envelope:

- **A typical throw releases the aircraft BELOW its own stall speed: 44.5 km/h vs 45.9 km/h (1687 g).** Best case (hard throw 12 m/s + high idle throttle) = 14.9 m/s — **0.4 m/s short of k_safe = 1.20** (55.1 km/h). Danger window ≈ 0.8 s (200 ms motor delay + acceleration at hover throttle).
- **Official autolaunch data integrated `[D]`:** INAV guide (Hoffmann): `nav_fw_launch_thr` = hover throttle (T/W ≈ 1.0 → 16.5 N), idle 0.5–0.67 ×, motor delay 200 ms, spinup 200 ms (8-in prop), climb 18–25°; ArduPlane: `TKOFF_THR_MINACC` 15 m/s², delay ≥ 0.2 s, minspd 4 m/s, **release at 0–5° pitch** (higher → stall).
- **Envelope declared:** release ≥ 1.20 × V_stall at 0–5° pitch, hard throw + high idle; launch lever: CL_max chain (R-AIRFOIL) is now double-critical (lowers V_stall AND raises the release margin).
- Documents: research/I-14 executed, guide **v0.10** (§4 launch envelope, §12 autolaunch settings, §13 refs), calculations/README §15, I-14 §3.2 settings table for D1/D2. **Corrections:** none.

---

## [1.20] — 2026-08-06

**Absolute divergence speed computed (G6 first pass) — `calculations/divergence.py` + `docs/07`. Criterion FALSIFIED at nominal and conservative ends.**

The ADR-0030 claim "V_div ≥ 1.5 × V_NE met with the shell alone" had no calculation behind it (I-05 gave only the relative Peregrine anchor, 1.14×). New absolute estimate:

- **Nominal: 267.7 km/h — margin 1.12× (barely PASS). Conservative end (G −35 %, a 11.2, k_sweep 0.50): 121.9 km/h — 0.51× — FAIL, below V_NE 160 km/h.** Optimistic end: 664 km/h.
- **AERO LW-PLA wings: 86.2 km/h — below the 95 km/h design cruise: NOT airworthy under this model** (OP-28 confirmed with numbers).
- R-JOINT penalty at 5× = **−12 %** on the real wing (lumped table −9 % slightly optimistic); tube Ø12 fully bonded = **+7 % max** ("bending only" quantified, holds).
- **Method bug caught by C2:** a first shooting implementation (θ′ continuity) converged to the WRONG equation (drops GJ′·θ′; 3× error on the tapered wing). Flux-form shooting agrees with the FEM weak form to **0.06 %**. Recorded in the validation discipline.
- **Action:** declared **V_limit 110 km/h** for the first test flights; S3 (real section GJ in Fusion 360) + I-12 (sweep factor) + E7 (Southwell) are the closers; 3 perimeters (+22 % V_div, +200 g) is the structural option.
- Documents: `docs/07-divergence-margin.md` (new), open points **OP-29 added**, OP-28 updated with numbers, calculations/README §14, docs/README index. **Corrections:** none — a falsified claim replaced by a calculated band.

---

## [1.19] — 2026-08-06

**Material mass variants tool (F2-class) — `mass_budget.py` + `docs/06`.**

New data-driven weight calculator with per-part material selection: **ALL PETG**
(baseline), **AERO WINGS / AERO MAX** (LW-PLA wings/tips ± elevons), **PLA+** (rejected
material, computed for completeness), or arbitrary per-part assignment. Options:
battery 4S1P/6S1P/4S2P/6S2P × Molicel P42A/Samsung 50E (I-16 `[D]` model), FC catalog
(I-17 `[M]`, 8.4–26 g), FPV O4/Pro/Lite/O3 (I-19 `[M]`), motor/prop/servo class, V1 fin
(ADR-0038). Twelve validation cases, ALL PASS.

- **Baseline refinement (−10 g):** the script uses the I-16 `[D]` pack mass 445 g
  (validated vs the measured packs) instead of the guide §8.1 `[E]` 455 g → 1687 g /
  45.9 km/h vs 1697 / 46.1. The OP-24 stall tension holds in both; the guide's figures
  remain the conservative published values.
- **Results (6S1P P42A, O4 Pro, CLEAN):** ALL PETG 1687 g / 45.9 km/h · **AERO WINGS
  1508 g / 43.4 (stall-compliant, −179 g)** · AERO MAX 1457 g / 42.7 · PLA+ 1670 g.
- **Engineering flags:** AERO wings are E ≈ 0.5× PETG → divergence/torsion re-check
  required before airworthiness (OP-28, F4/S3–S4); AERO needs flow 0.60 (never 0.95);
  elevon balance mass derived from elevon mass (ADR-0025); PLA+ stays rejected
  (ADR-0016).
- Documents: `docs/06-material-mass-variants.md` (new), guide **v0.9** (§8.1 note),
  open-points v0.9 (OP-28), calculations/README §13, docs/README index.
  **Corrections:** none (refinement, not overturn).

---

## [1.18] — 2026-08-06

**Filament dowel pins adopted in the glued segment joints (ADR-0039).**

Community proposal (refined after the §1.17 trade): filament pins are NOT a carbon
replacement — they are **alignment/shear dowels in the glued joints**. New tool
`filament_dowel_pins.py` (six validation cases, ALL PASS):

- **Spec:** 2 × Ø1.75 mm filament (PETG scraps preferred) per glued segment joint
  (y = 347/498, 8 dowels/aircraft); holes Ø1.8–1.9 mm at x/c 0.40/0.60 with solid
  collars Ø8 × 4 mm; adhesive dab on one side; length 20–22 mm.
- **Shear redundancy:** demand at +6 g V_NE ≈ 27 N (y=347) / 12 N (y=498) `[E]` vs
  2-dowel double-shear capacity ≈ 293 N → **FS ≈ 11 / 24** `[D]`.
- **Alignment** (primary function, `[I]`): prevents shear slip during glue cure —
  alignment IS strength; zero cost (scraps), 2.6 g/aircraft.
- **Boundary declared:** the CORE↔PANEL torque couple keeps the carbon Ø6 pin
  (§1.17); the ADR-0023 bond-area rule is unchanged (dowels are additive).

Documents: ADR-0039 (new), guide **v0.8** (§7.3 spec, §7.4 print row, §5.4 fin-root
dowel, §12 assembly, §13, §14), justification/open-points v0.8 (OP-27: first-print fit
verification), calculations/README §12, decisions index. **Corrections:** none.

---

**R-JOINT pin material trade — filament proposal evaluated and rejected with numbers.**

Community proposal: replace the carbon Ø6 anti-rotation pin with pieces of 3D-printer
filament (PETG/PLA Ø1.75). New tool `joint_pin_trade.py` (five validation cases, ALL
PASS) shows:

- **Strength passes** (not the binding requirement): couple force F = T/arm =
  2.3–15.4 N `[E]` → shear FS ≈ 4.7 (PETG) / 6.3 (PLA); bearing ≈ 5 MPa.
- **Stiffness fails by ≈ 9000×**: E·I carbon Ø6 = 7.63 N·m² vs PETG filament
  Ø1.75 = 0.0009 N·m². With identical sockets/arm/loads, k_joint ∝ E·I → R-JOINT
  collapses from ≥ 5× to ≈ 0.005× the section → **−29 % V_div** (ADR-0032 table) on a
  forward-swept wing whose dominant risk is aeroelastic divergence (I-05).
- Printed-PETG alternatives: tenon Ø8 → 5 %, Ø10 → 12 %, Ø17 → parity (≈ 40 g vs
  6.3 g) — worse than carbon on every axis.
- Cost/complexity: carbon ≈ €0.25–0.50 per pin, 6.3 g; the socket (bore, embedment,
  sliding fit) is identical for any pin — filament saves ≈ €1/aircraft, no complexity
  change. **Verdict: −29 % divergence margin is not purchasable for €0.5.**

Documents: ADR-0031 (trade-study section added), guide §7.3 (pin material fixed,
with reference), calculations/README §11. **Corrections:** none (proposal evaluated,
no datum overturned).

---

**Catalog audit — everything integrated, two gaps closed (O3 + 14 missing ADR files).**

### Audit result (batteries / FC / servos / FPV)
Verified in the design guide: **batteries** (I-16: bay 200×70×32 mm, pack 6S1P
153.2×64.5×22.2 mm, energy 90.7/108 Wh — §7.6/§8.1/§9/§10.1), **FC** (I-17: station
cavity 64×45×21 mm, 30.5×30.5 boss, F405-WING-V2/SpeedyBee reference, exclusions —
§7.6/§11), **servos** (I-18: class 12–15 g, cavity 34×16×39 mm, current 1.2–2.8/5–9 A —
§7.5/§8.1/§11), **FPV O4 series** (I-19: camera 25.55×20×23.30 / Lite 13.44×12.36×16.50,
VTX 33.5×33.5×13 / Lite 30×30×6, power rails — §7.6/§8.1/§11). **All integrated.**

### Gap closed 1 — DJI O3 Air Unit (legacy) `[M]`
Not previously cataloged. Added to **I-19 §2.4** with DJI official data (module
32.5×30.5×14.5 mm, camera 21.2×20×19.5 mm, 36.4 g, 7.4–26.4 V, coax 115 mm): fits the
Salamandra mounts (camera inside the O4 cavity, module on the O4 tray); declared
verifications pending (camera hole spacing, measured current). Guide §7.6/§8.1/§11 and
OP-25 updated. O4 series remains the reference.

### Gap closed 2 — OP-22: all 14 missing ADR files published
ADR-0003 (wash-in twist), 0006 (single pusher, ⚠️ dispute), 0008 (reject 7×12), 0009
(drag decomposition), 0012 (light color), 0016 (reject PLA+), 0018 (reject ABS), 0023
(joint adhesive), 0024 (segmentation), 0026 (dual actuation), 0030 (plastic torsion
path), 0031 (carbon pin), 0034 (motor mount angle), 0035 (TPU hinges) — written from
their guide/justification values with tags; decisions index linked; OP-22 **closed**;
guide §13 note updated (all ADRs published).

### Versioning
Design guide **v0.7** (O3 + ADR publication; §14), justification/open-points v0.7.

### Corrections
None (catalog extension and file publication; no overturned datum).

---

## [1.17] — 2026-08-06

**R-JOINT pin material trade — filament proposal evaluated and rejected with numbers.**

Community proposal: replace the carbon Ø6 anti-rotation pin with pieces of 3D-printer
filament (PETG/PLA Ø1.75). New tool `joint_pin_trade.py` (five validation cases, ALL
PASS) shows:

- **Strength passes** (not the binding requirement): couple force F = T/arm =
  2.3–15.4 N `[E]` → shear FS ≈ 4.7 (PETG) / 6.3 (PLA); bearing ≈ 5 MPa.
- **Stiffness fails by ≈ 9000×**: E·I carbon Ø6 = 7.63 N·m² vs PETG filament
  Ø1.75 = 0.0009 N·m². With identical sockets/arm/loads, k_joint ∝ E·I → R-JOINT
  collapses from ≥ 5× to ≈ 0.005× the section → **−29 % V_div** (ADR-0032 table) on a
  forward-swept wing whose dominant risk is aeroelastic divergence (I-05).
- Printed-PETG alternatives: tenon Ø8 → 5 %, Ø10 → 12 %, Ø17 → parity (≈ 40 g vs
  6.3 g) — worse than carbon on every axis.
- Cost/complexity: carbon ≈ €0.25–0.50 per pin, 6.3 g; the socket (bore, embedment,
  sliding fit) is identical for any pin — filament saves ≈ €1/aircraft, no complexity
  change. **Verdict: −29 % divergence margin is not purchasable for €0.5.**

Documents: ADR-0031 (trade-study section added), guide §7.3 (pin material fixed,
with reference), calculations/README §11. **Corrections:** none (proposal evaluated,
no datum overturned).

---

## [1.16] — 2026-08-06

**Catalog audit — everything integrated, two gaps closed (O3 + 14 missing ADR files).**## [1.15] — 2026-08-06

**Directional (yaw) stability quantified — dual configuration adopted (I-20, ADR-0038).**

### New analysis
- **`calculations/yaw_stability.py`** — Cnβ budget, fin sizing, rudder authority, yaw
  damping/subsidence, fin bending, drag/mass/stall cost. Six validation cases (Helmbold,
  fin reference, Raymer body, tier consistency, damping) — **all PASS**.
- **I-20 — directional stability thread** with primary-source evidence: the TBS Mojito
  (same FSW + nose + pusher class) carries a **fixed** vertical stabilizer and **no
  rudder servo** (product page, manual, official INAV CLI: `servo 1/2` elevons only,
  `fw_ff_roll 93` bank-to-turn) — `[M]`, new.

### Findings (honest, not silent)
- **The finless baseline is directionally unstable:** Cnβ = −0.0006…−0.0015/deg `[E]`
  (negative across the band — FSW wing sign + nose boom); yaw divergence τ ≈ 0.7 s.
  The guide's "no tail, no vertical stabilizer, no rudder" was an **assumption, not a
  calculation** — the same failure mode C6 corrected for pitch. Now quantified.
- **A movable rudder is rejected with numbers:** |Cnδr| ≈ 0.00043/deg cannot hold a
  20 km/h crosswind slip at stall (δr ≈ 24° > ±20°); differential elevons ≈ 1/5 of a
  rudder's authority; no mission need (bank-to-turn); no in-service precedent.
- **Cost of the fin:** V1a (2.1 dm²) 36–60 g, ΔCD0 +0.0014 → +9.6 % energy `[E]`
  (Wh/km ≈ 1.26 — still < the Mojito's 1.40 `[M]`); V_stall +0.6 km/h (OP-24 lever).

### Decisions and documents
- **ADR-0038 — dual directional configuration:** `SALAMANDRA-CLEAN` (finless, O1
  efficiency build) and `SALAMANDRA-V1` (fixed centreline fin — **first platform
  variant**, recommended for the Article #1 test programme). Fin = CORE component:
  no servo, no linkage, no FC change; panels untouched.
- **Design guide v0.6:** §5.4 (full variant spec: S_v 2.1/2.8 dm², b_v 250–290 mm,
  root t ≥ 2.5 mm, rear-pod extension ≈ 30 mm, fin AC ≈ +285), §7.6 fin-mount row,
  §4/§8.1 stall flags, §12 assembly step, §13 references.
- **Justification v0.6** (§11) and **Open Points v0.6** (OP-26 added).
- **docs/00 §3.6**, **docs/02 §3 (Mojito `[M]` register + R5 pending)**, **docs/03 C8**
  (directional budget + exit criterion), **docs/05 S8** (fin loads/flutter in F4),
  **tests/README E8** (yaw perturbation — the `[M]` closure of G10), **gaps G10**,
  **README** (status + article table + variants).
- **Corrections:** none (new analysis, no overturned datum). Mojito fin dimensions
  (R5) pending human measurement — the analysis model cannot process images.

---

## [1.14] — 2026-08-05

**Component catalogs integrated: batteries (I-16), FC (I-17), servos (I-18), FPV DJI O4 (I-19).**

### Integration
- **Mass balance re-run with the FPV unit** (`balance_cg.py` `[D]`): DJI O4/Pro
  (camera 16.4 g at the boom front ≈ −450, VTX 16.6 g at the avionics station, 2×
  antennas 4.2 g) → AUW **1697 g**; 6S1P pack station **−415 mm** (was −421), bay
  **−516…−315** (200 mm, was −521), boom ≈ 385 mm. The FPV camera in the boom helps the
  balance (≈ 4 mm forward).
- **Guide v0.5:** §7.5 servo class 12–15 g metal-gear (I-18), cavity 34×16×39 mm,
  hinge moment 10–48 mN·m/servo NOT binding (≥ 3.7× margin, `servo_torque.py`), current
  avg 1.2–2.8 A / peaks 5–9 A with capacitance guidance; §7.6 avionics station cavity
  64×45×21 + 30.5×30.5 boss (I-17), FPV camera mount (2× M2, 16 mm) and VTX tray with
  airflow (I-19); §8.1 FPV row 37 g `[M]`; §11 FC reference class (F405-WING-V2 /
  SpeedyBee; F411 no blackbox, Foxeer no current, H7A3 no INAV target), avionics
  6.6 W ≈ 6 % of cruise ≈ 7.3 % of pack per flight-hour, FPV power (Pro on the 9 V/2 A
  rail ≥ 13.5 W, NOT the 5 V rail; total electronics 17.0 W Pro = 18.8 %/h); §10.1
  battery energy reference 90.7 Wh P42A / 108 Wh 50E (I-16); §4 stall flag updated.
- **Open points v0.5:** OP-06 partial closure (torque not binding); OP-18 catalog check;
  OP-24 (three mass levers, AUW 1697 → 46.1 km/h, borderline); OP-25 (FPV selection)
  added.
- **I-18 collision fixed:** the DJI O4 catalog was numbered I-18 twice — the FPV system
  is now **I-19** (`git mv`, references updated in `research/README.md`,
  `calculations/README.md`, `fpv_power_budget.py`).

### Stall flag (honest, not silent)
AUW 1697 g → V_stall ≈ **46.1 km/h** vs ≤ 45 required. Levers: shell 550 g + boom
≤ 40 g + servos 48 g → ≈ 45.1 km/h — **borderline; F2 must arbitrate the mass budget
against C16 (OP-24).**
---

## [1.13] — 2026-08-05

**Bay re-derived with the real pack envelope (I-16).**

### Context
The parallel battery-pack analysis (I-16, `battery_pack_layout.py`) established the
finished pack envelopes with datasheet `[M]` + assembly allowances `[E]`: **6S1P =
153.2 × 64.5 × 22.2 mm** (2×3 cells, orientation A, leads included) and 4S1P =
153.2 × 43.2 × 22.2. The v0.3 bay sizing assumed an 84 mm pack — **corrected**.

### Corrected (`balance_cg.py`, all `[D]`)
- Bay: **200 × 70 × 32 mm**, forward end **x ≈ −521**, boom ≈ **390 mm** (was 190 mm /
  −493 / 360 mm). The 6S1P pack (153.2 mm) + 36.5 mm R-CG slide + 5 mm clearances
  require the 200 mm length.
- Fit verdict: **only 6S1P fits the single-layer bay and reaches its band
  (−439.5…−403)**; 4S1P fits physically but needs x ≈ −577 (outside the bay);
  **4S2P/6S2P fit no n_z = 1 arrangement of 8/12 cells (I-16)** — the earlier
  "also covers 4S2P" claim is withdrawn.
- OP-23 sharpened accordingly; the v0.4 bay serves the reference 6S1P only.

### Changed
- Design guide v0.4: §7.6 boom/bay rows, §8.2 OP-01 blockquote, §9 bay/configs rows,
  §14 log; justification §3.2 (table + adopted geometry + flag 1); open points v0.4
  (OP-01, OP-16, OP-19, OP-21, OP-23).

---

## [1.12] — 2026-08-05

**OP-01 resolved by decision (nose boom), R-TWIST raised to 3.0°, elevon authority verified.**

### New tools (both validated, all `[D]`)
- **`calculations/balance_cg.py`** — mass/CG balance with the pack-station solver.
  Self-consistency validation: numerical planform area centroid −48.9 mm vs the
  −49 mm assumed in the mass table (OK).
- **`calculations/elevon_authority.py`** — elevon control power via the VLM
  (step incidence over 30–90 % half-span): yield **0.00348 °/°**; 10° elevon
  ≈ 4.8× the SM-8 % trim requirement.

### Resolution (guide v0.3, justification §3.2)
- **OP-01 (CG reachability):** target CG −119 mm needs the 6S1P pack CG at
  **x ≈ −421 mm** — the v0.2 nose pod could only reach ≈ −100 (band −24…+9 mm).
  **Adopted: nose boom** carrying the battery bay (forward end x ≈ −493, 190×70×32,
  slide ≈ 36 mm covers R-CG ±5 mm), ≈ 360 mm forward of the nose pod tip, skid at the
  tip — Mojito pattern (I-02). Pack stations: 4S1P −577 / **6S1P −421** / 4S2P −346 /
  6S2P −270.
- **OP-23 (new):** the R-CG four-config requirement is not satisfiable with one bay
  (stations span 307 mm); the bay covers 6S1P (reference) + 4S2P; requirement
  re-derived in F2.
- **OP-24 (new):** boom structure ≤ 40 g target; AUW 1660 g → V_stall ≈ 45.6 km/h vs
  ≤ 45 required; declared lever: shell at 550 g (low end) + boom ≤ 40 g → ≈ 44.7 km/h.
- **R-TWIST 2.5° → 3.0°:** at 3.0° the stall criterion holds (load peak 56 % b/2,
  margin +0.017 — same as 0°; at 4° it drops to +0.009). Trim closure at SM 8 %:
  worst-case residual ≈ 0.6° permanent elevon reflex (authority verified).
- Central-body effect (I-07 §6): direction known (NP forward), margin applied in F2;
  does not reverse the solution.

### Changed
- Design guide v0.3: §4 stall flag (45.6 km/h + mass lever); §5.3 twist note
  (R-TWIST 3.0° + reflex closure); §6.1 trim-closure blockquote; §7.6 CORE nose
  boom + bay 190×70×32; §8.1 mass budget (boom 40 g, AUW 1660 g); §8.2 NP row
  (Weissinger-L) + OP-01 resolution blockquote; §9 bay; §12 step 7; §14 log.
- Justification §3.2 (resolution with pack-station table and honest flags); Open
  Points v0.3 (OP-01 resolved by decision, OP-02 updated, OP-16/OP-19 updated,
  OP-23/OP-24 added).

## [1.11] — 2026-08-05

**B3 screening executed (XFOIL 6.99, 24 cases) and C2 NP cross-check executed.**

### Executed
- **`calculations/b3_screening.py`** — batch XFOIL screening of the shortlist
  (E205, E205→9 %, S5010, MH60, MH60→12 %, MH60→13.5 %) at Re 3e5/5e5 × Ncrit 10/12
  (the I-06 calibrated band). Coordinates in `geometry/airfoils/`; 24 polars in
  `calculations/xfoil_out/`; all `[D]`.
- **`calculations/weissinger_np.py`** — independent NP check (Weissinger-L swept
  lifting line), validated on a straight AR 6 wing (NP 25.00 % MAC).

### Results (I-15 §6, all `[D]`)
- **E205 DISCARDED**: cm0 ≈ −0.07 at project Re (fails R-AIRFOIL by ≈ 0.08;
  ≈ 22° wash-in needed). In-service evidence does not imply Cm0 — confirmed.
- **Thinning quantified**: E205→9 % loses ≈ 0.1 clmax and 3–4° stall angle.
- **Published cm0 not achieved at project Re** (S5010: +0.0080 → −0.011…−0.016);
  **thickening a reflexed section improves cm0** (MH60: −0.0136 → +0.0016 at 13.5 %,
  Re 5e5, Ncrit 10).
- **Trim closure at SM 8 %: no off-the-shelf candidate fits R-TWIST ≤ 2.5°**
  (MH60→13.5 % needs 2.6–3.7° wash-in). Closure paths: designed section
  (cm0 ≥ +0.008), reduced SM target, or elevon reflex.
- **C2: NP verified by two methods** — VLM −101.3 mm (26.7 % MAC) vs Weissinger-L
  −98.3 mm (28.0 % MAC): **3 mm agreement**. The "least-verified number in the chain"
  claim (justification §3.1) is superseded; the central-body effect remains
  unquantified (moves NP forward).

### Changed
- Design guide: §3 NP row (C2 cross-check); §5.3 twist note (parametric; 2.6–3.7°
  preview with current candidates); §6.1 trim-closure blockquote; §6.2 E205 →
  discarded, MH60→13.5 % cm0 +0.0016; §14 log.
- Justification §3.1 (NP note), §4 airfoil rows; Open Points OP-02 (screening
  executed), OP-05 (cross-check done); gaps G8; calculations README.

### Engineering notes
- XFOIL 6.99 batch-mode quirks solved and baked into the script: Ncrit lives in the
  VPAR submenu (command `N`), polar via PACC/PWRT, CRLF input file, Fortran stdin EOF
  noise tolerated; the script is incremental (reuses valid polars).
- Two implementation bugs were found and fixed by validation: a wrong validation
  harness (b for S) and an odd `y·tanΛ` moment arm in Weissinger-L (the c/4 line
  sweeps forward on **both** halves, `|y|·tanΛ`).
- **Reproducibility packaging:** XFOIL path is now configurable (`--xfoil` / `XFOIL_EXE`);
  full reproduction guide in `calculations/README.md` (tools, versions, commands,
  batch quirks, validation discipline); coordinate provenance in
  `geometry/airfoils/README.md`; root README documents the toolchain and the current
  Phase-1 status (G8 largely closed, G2 screening executed).

---

## [1.10] — 2026-08-05

**Airfoil evidence campaign (I-15) opened — 11 investigations, 6 partially executed.**

### Added
- **[I-15](research/I-15-airfoil-evidence-campaign.md)** — analysis of the airfoil
  criterion (the guide's weakest, matrix score 60/100) and an evidence campaign with
  11 investigations (A1–A11) on the root/tip problem.
- Executed evidence (all NTRS, public fulltext where noted): E387 LSB measurements
  (NASA-CR-186263 — the project's calibration airfoil), Carmichael low-Re survey
  (NASA-CR-165803-VOL-1), thickness-induced separation crossover (NASA-CR-4096,
  Barnett & Carter), NACA-SR-83 (thickness vs drag), Notre Dame LSB series covering
  Re 40k–400k (AIAA 80-1440, 86-1065, 83-1671), flap-deflection LSB data (AIAA
  79-0004), Prandtl-D/Horten minimum-induced-drag line (DFRC-E-DAA-TN2041/3811/4103).
- Negative results recorded: PW51 not in UIUC (A3); airfoiltools unreachable from this
  environment (E205 XFOIL polar deferred to the local calibrated run); NTRS has **zero**
  reflexed-section records — the reflexed evidence base is the RC/glider world + LSB
  physics, not NASA.

### Changed
- Design guide §6.1 — R-AIRFOIL note: the root section is to be **designed, not
  selected**; **new binding criterion: gentle root-first stall character**; **declared
  confidence basis of the polar** (no measured reflexed polar at Re 3–5×10⁵; XFOIL
  `[D]` anchored on the E387 LSB measurements; printed-skin transition runs earlier;
  E2 closes); §1/§13 research set extended to I-01…I-15; §14 log updated.
- Justification §4 — provisional recipe row rewritten (MH 60-12 % family, designed
  root); stall-character row added with its `[M]` evidence; references extended.
- Open Points OP-02 — trigger now includes I-15; criteria now include the stall
  character.
- **Knowledge integration into the owning documents:**
  - I-06 — measured LSB anchors for the Ncrit calibration (NASA-CR-186263 E387, Notre
    Dame series at Re 40k–400k, Schmidt & Mueller, Carmichael survey); B1 closing list
    now includes the E387 bubble-level comparison.
  - I-01 — Carmichael fulltext source added; measured bridge to Re 4×10⁵ declared.
  - I-02 — Prandtl-D/Horten line added as supplementary evidence (does not reopen the
    closure), with its transfer limits.
  - I-08 — PW51 availability gap recorded (not in UIUC, 404).
  - ADR-0027 — evidence register added (thickness/separation sources) without reopening
    the decision; review conditions unchanged.

### Declared (not a correction)
- The airfoil criterion analysis concludes: no published reflexed section satisfies
  R-AIRFOIL at 13.5 % t/c; B3's central deliverable is a **designed section**, with
  R-AIRFOIL re-derivation against the twist window as the declared alternative.

---

## [1.9] — 2026-08-05

**Five new investigation threads (I-10…I-14) and correction C28.**

### Added
- **[I-10](research/I-10-control-authority-static-margin.md)** — tailless pitch control
  authority and minimum static margin (feeds C6/S5 — never done before — OP-01, OP-06).
- **[I-11](research/I-11-reflexed-airfoil-database.md)** — reflexed-airfoil database for
  the B3 shortlist (aerodesign.de tailless database reviewed; E205/UIUC availability
  checked). Partial: database values extracted, measured polars still to be compiled.
- **[I-12](research/I-12-x29-divergence-sweep-factor.md)** — X-29 divergence flight
  data and sweep-factor bounds (NASA-TM-86025 located on NTRS; feeds G6 — the declared
  weakest link — and G4).
- **[I-13](research/I-13-pusher-tractor-slipstream.md)** — pusher vs tractor slipstream
  at Re 3–5×10⁵ (feeds the disputed ADR-0006 and G5).
- **[I-14](research/I-14-hand-launch-stall-margin.md)** — hand-launch and stall-margin
  practice (feeds the O1 stall requirement with its 0.4 km/h margin and the launch
  method).

### Changed
- Design guide §6.2/§6.3 — provisional airfoil candidates corrected (C28); §1/§13
  research set extended to I-01…I-14.

### Corrections

| # | Error | Correction |
|---|---|---|
| **C28** | The design guide listed the provisional root airfoil as "MH 45 (t/c ≈ 13 %)". The aerodesign.de tailless-airfoil database (reviewed in I-11) lists **MH 45 at 9.85 % thickness, cm0 +0.0070**, documented for 15–40 g/dm² — below the project's 57 g/dm², and below R-AIRFOIL's +0.008 | Provisional root candidate moved to **MH 60-12 %** (12.0 %, cm0 +0.0030) scaled to 13.5 %; the guide now declares that **no off-the-shelf reflexed section reaches 13.5 %**, making R-AIRFOIL feasibility at 13.5 % an explicit B3 question; the 9 % tip must use camber compensation, not pure thickness scaling (MH 45-8 % precedent warns of clmax loss and harsh stall) |

---

## [1.8] — 2026-08-05

**Salamandra Design Guide v0.2 — designer-review release.**

The three `design/` documents were reviewed as a CAD specification (Fusion 360): every
value was re-derived and cross-checked (planform, stations, NP/CG/SM, speeds, balance).
All planform and stability numbers verified. Six inconsistencies were corrected; the
guide is now fully self-consistent and complete enough to model the v0.2 geometry.

### Changed
- **Design Guide v0.2** — new §7.6 "CORE (center module)": nose pod (60 mm forward of the
  root LE, battery reach x ≈ −100), rear pod (motor mount, prop disk at x ≈ +235), prop
  ground-clearance constraint (belly ≤ −111.6 mm at the prop plane), joint sockets with
  centerlines and clearances, avionics stations. Carbon tube/pin physical lengths.
  Provisional airfoil coordinate recipe (§6.3). Wing tips declared (flat caps, no winglet).
- **Justification v0.2** — moment balance re-derived with corrected motor station and the
  v0.2 bay limits; band ≈ −24…+9 mm (6S1P; ≈ −36…+9 across the packs, was −27…+29).
  Battery for target CG ≈ −439 mm (was −428).
- **Open Points v0.2** — OP-01/04/06/19 updated; OP-20 (wingtips), OP-21 (CORE outer
  mold), OP-22 (missing ADR files) added.

### Corrections

| # | Error | Correction |
|---|---|---|
| **C22** | The guide stated dihedral as both "polyhedral segment rotations" (0 / 1.07 / 0.46 / 0.47°) and a "linear schedule Γ(y) = 2.0°·y/650" — two different surfaces (tip rise 11.35 vs 12.18 mm), with ambiguous kink locations | Defined unambiguously: **piecewise-linear polyhedral, flat segments, kinks at every segment joint** (y = 195/347/498), cumulative values 0 / 1.07 / 1.53 / 2.0°, tip rise ≈ 12 mm; the linear schedule remains only as the generator of the joint values |
| **C23** | Elevon inner end at 20 % half-span (y = 130) crossed the removable CORE↔PANEL joint at 30 % (y = 195), placing a control surface on the shared, non-reprinted CORE with no servo for it | Elevon is a **panel component**: y = 195 → 585 (30–90 %), length 390 mm; CORE trailing edge fixed (torsion box may run to the TE inboard of the joint). Dual actuation retained as flutter margin pending C6 |
| **C24** | Print-fit statement inconsistent: "segments of ≈ 118 mm span" (actual: 152/151/152 mm), and span-at-45°-in-bed-plane does not fit the 256 mm bed (≈ 281 mm footprint for segment 1) | 45° defined as **roll of the airfoil plane about the span axis** (LE low): footprint 152 × 174 mm — fits; orientation constraints added to §7.4 |
| **C25** | Motor+prop station at x = +190 in the OP-01 balance — inside the planform (root TE at +216.9), impossible for a pusher with the prop disk aft of the TE | Prop disk at x ≈ +235 (≥ 10 mm aft of root TE), mount face +230, motor+prop centroid ≈ +217. OP-01 band re-derived with the v0.2 bay limits: ≈ **−24…+9 mm** (6S1P; ≈ −36…+9 across the packs, was −27…+29); battery for the target ≈ −439 mm |
| **C26** | "Prop with ≥ 10 mm ground clearance" at z = 0 with the 8×8 prop (radius 101.6 mm): the lowest blade tip falls ≈ 82 mm below the wing lower surface — the constraint was physically unsatisfiable with an airfoil-shaped CORE | CORE rear pod defined: **lower surface ≤ z = −111.6 mm at the prop plane** (≈ 92 mm below the wing lower surface). Thrust line stays at z = 0 (no pitch coupling) |
| **C27** | Tube "~390 mm per panel" is the spanwise extent; the physical tube is longer along the swept c/4 line (≈ 415 mm) plus ≈ 70 mm socket insertion | Tube ≈ **485 mm** total; pin ≈ 140 mm (70 + 70, matching the socket depth); socket bores Ø12.2–12.4 / Ø6.1–6.2, depth ≈ 70 mm — added to §7.2/§7.3 |

### Identified
- **OP-22** — ADR files 0003, 0006, 0008, 0009, 0012, 0016, 0018, 0023, 0024, 0026,
  0030, 0031, 0034, 0035 exist in the decisions **index** but were never published as
  files; several are referenced by the guide. Must be published before v1.0.

---

## [1.7] — 2026-08-05

**Salamandra Design Guide v0.1 released.**

### Added
- **`design/Salamandra-Design-Guide-v0.1.md`** — first release of the CAD-ready
  specification for the designer: reference planform (b 1300 mm, S 0.282 m², AR 6.0,
  λ 0.50, Λ_c/4 −20°, t/c 13.5/9 %), provisional airfoil (B3 pending), structure,
  mass budget, propulsion, bay and avionics.
- **`design/Design-Guide-Justification-v0.1.md`** — per-value rationale with confidence
  tags and derivations.
- **`design/Design-Guide-Open-Points-v0.1.md`** — open points and evolution process.

### Identified
- **OP-01 (critical)** — preliminary moment balance shows the target CG (18.7 % MAC,
  47 mm forward of the root LE) is not reachable with the current mass layout; the
  neutral point must be re-verified with an independent method (C2) before the bay
  position is finalized.

---

## [1.6] — 2026-08-05

**Project reframed as an open, community-driven aircraft platform.**

### Added
- **ADR-0036** — the repository is an open, community-driven, modular 3D-printed FPV
  aircraft platform: AI performs the aerodynamic/theoretical research and design
  exploration; the community creates the actual 3D parts, experiments and manufacturing
  know-how.
- **ADR-0037** — licence selected: **CERN-OHL-S-2.0** for hardware/design/scripts and
  **CC BY-SA 4.0** for documentation.
- `LICENSE` (CERN-OHL-S v2) and `LICENSE-docs.md` (CC BY-SA 4.0).

### Changed
- `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `docs/00-...` and `docs/05-...` updated to
  communicate the platform purpose, the AI–human division of labour, the modular and
  extensible nature (beyond the forward-swept flying wing), and the importance of community
  participation.
- PR template updated to welcome diverse contributions and declare the licence.

---

## [1.5] — 2026-07-28

**A4 started with primary sources from the StuntDouble family.**

### Added
- **[I-08](research/I-08-stuntdouble-family.md)** — base comparison of Nemesis,
  Stinger V2 and Stormbird.
- **[I-06](research/I-06-reflexed-airfoils.md)** and
  **`calculations/calibra_xfoil_e387.py`** — first reproducible XFOIL calibration against
  the measured E387 (C) polar.
- Primary Stinger V2 and Stormbird files for the later reconstruction of planform,
  airfoil and twist.

### Results
- The three published designs converge on **AR = 6.05–6.55** `[D]`.
- Nemesis and Stinger keep twin tractor and comparable wing loading, but switch from
  PW51 to PW75; Stormbird additionally switches to a single pusher.
- Nemesis publishes 2 mm of reflex and Stormbird 1–2 mm `[M]`; the local chord is
  missing to convert those adjustments into angle.
- Ncrit 10 minimizes the global `Cd(Cl)` disagreement with an RMS factor of 1.208 `[D]`
  (Ncrit 11: 1.209), but the optimum drifts to Ncrit 12 at Re 3–5×10⁵. B3 should
  use a 10–12 band.

### Corrections

| # | Error | Correction |
|---|---|---|
| **C19** | A4 described Nemesis vs. Stinger/Stormbird as a "controlled comparison" able to isolate the effect of sweep | It is a **quasi-controlled comparison**: same author, constructive family and comparable AR, but airfoil, size and propulsion do not all remain constant. It serves as a geometric prior; it does not demonstrate sweep causality |
| **C20** | B1 assumed that tuning a single Ncrit would "reproduce the measured polar" of the E387 across the whole range | The optimum changes with Reynolds: Ncrit 10–12 on the tested grid. The single number is replaced by a **band with published sensitivity** and validation against a second physical model before screening airfoils |
| **C21** | B2 still accepted `C_m0 ≥ 0 or close` after I-07 derived R-AIRFOIL | Criterion re-derived downstream: **C_m0 ≥ +0.008**, preferably +0.010–0.015. The old criterion could admit airfoils unable to close the trim within R-TWIST |

---

## [1.4] — 2026-07-28

**First in-house stability calculation.** G8 moves from open to partial.

### Added
- **`calculations/vlm_ala_volante.py`** — in-house vortex lattice with validation case.
- **`calculations/ventana_torsion.py`** — torsion window analysis.
- **[I-07](research/I-07-neutral-point-torsion-window.md)** — neutral point, static margin and torsion window.
- **R-AIRFOIL** — airfoil Cm0 ≥ +0.008. Bounds G2 with a number.
- **R-TWIST** — wash-in ≤ 2.5°.

### Results
- **Neutral point = 26.7 % MAC**, 101 mm ahead of the root quarter-chord. Target CG 18.7 % MAC for 8 % static margin.
- **R-NP is easy to meet:** the NP drift between 1100 to 1600 mm panels is only **1.6 MAC points**, and a ±2–4° sweep adjustment aligns them within 0.5 %.
- **The torsion window exists but is narrow.** With pure twist, balancing at 10 % static margin requires 3.9° of wash-in, and that moves the load peak to 62 % of half-span — the elevon zone. **The airfoil must carry most of the trim.**

### Corrections

| # | Error | Correction |
|---|---|---|
| **C17** | The first version of the VLM returned the non-dimensionalized moment **without dividing by the MAC**, introducing a spurious chord factor in the neutral point | Detected by the validation case: a straight wing must give the NP at c/4 and gave ~0. **Confirms the value of always including an analytic contrast case in any calculation script** |
| **C18** | The optimistic reading of C2 suggested that wash-in could free the project from using a reflexed airfoil | **Partially false.** Wash-in works, but **trades trim against the advantage that justified choosing forward sweep**: at 4° the load peak moves from 27 % to 62 % of half-span. Reflex remains necessary; twist is left for fine-tuning |

---

## [1.3] — 2026-07-28

Repository restructured into an evolutionary format, designed for external contributions.

### Added
- **`decisions/`** — ADR register: one decision per file, with context, alternatives, consequences and review conditions. Index with states.
- **`research/`** — five documented research threads (I-01 to I-05), separating *the why* from *the what*.
- **`gaps/`** — formal register of G1–G9 with impact and closing path.
- **`CONTRIBUTING.md`** — contribution flow, value ordering, source quality.
- **`docs/04-conventions.md`** — tags, identifiers, symbols and sign conventions.
- **D34** — motor mount angle as a design parameter, not assumed zero.
- **D35** — TPU-printed hinges as the baseline option.
- **G9** — altitude-loop coupling with pitch (*porpoising*). **Threatens the validity of E7.**

### Corrections

| # | Error | Correction |
|---|---|---|
| **C16** | The requirement `V_stall ≤ 40 km/h` was derived with AUW 1350 g (48 g/dm²) and **was not re-derived** when the AUW rose to 1620 g | With C_Lmax 0.65 at 57 g/dm² the real speed is **42.7 km/h**. Reaching 40 would require C_Lmax 0.74, outside the measured range (0.55–0.70). **Requirement relaxed to ≤ 45 km/h**, justified by Peregrine and Mojito precedent |

---

## [1.2] — 2026-07-28

### Added
- **Modular architecture** (ADR-0032): CORE + PANEL, joint at 30 % of half-span.
- **R-NP**, **R-JOINT**, **R-CG**.
- **ADR-0033** — motor and battery out of the design.
- **E7** — Southwell in flight.
- **G8** — neutral point and static margin, uncomputed. Blocks Phase 1.
- **`docs/02-measured-references.md`** — primary data of the Peregrine 840 mm.

### Changed
- **ADR-0027** — t/c to **13.5 % / 9 %**, confirmed by measurement on an in-service article.
- **ADR-0028** — **gyroid 5 %** infill instead of a third perimeter.
- V_NE of article #1 lowered to **160 km/h**.

### Superseded
- **ADR-0022 — carbon veil ±45°.** Withdrawn by project decision (objective O5).
- **E4** (bench twist) — replaced by anchoring to measured reference and E7.
- **E6** — see C13.

### Corrections

| # | Error | Correction |
|---|---|---|
| **C11** | It was claimed that carbon tubes and rods add no torsional stiffness | True for the calculated case (10/8 mm), **false as a rule**. In thin wall `J = πD³t/4`: it scales with the **cube of the diameter**. A well-bonded braided ±45° 18 mm tube is indeed a torsional element |
| **C12** | Infill 0 % was specified, inherited from LW-PLA vase-mode practice | **Wrong for a PETG shell.** Bredt-Batho assumes the skin does not buckle; an unsupported 0.4–0.9 mm skin buckles locally well below the material limit. **Without infill, GJ was overestimated** — the error ran in the opposite direction to what was assumed |
| **C13** | E6 was proposed, inverse calibration of the model against the Peregrine | **Withdrawn.** The Peregrine is at a factor ~3 from the prediction. A test that passes with that margin does not falsify the model **but does not validate it either** |
| **C14** | Structural risk was overestimated and communicated with more certainty than `[E]` ±35 % data supported | With gyroid and D-box the margin is 1.5–2.0×. The alarm corresponded to a configuration without infill and without D-box that was no longer the project's |
| **C15** | It was claimed that a single perimeter fails the divergence criterion | **Falsified by flying hardware.** The 840 mm Peregrine flies with 1 perimeter of 0.42 mm and 4 % gyroid |

---

## [1.1] — 2026-07-28

### Resolved
- **ADR-0010** — **branch A (fast cruise)** fixed, forced by PETG density.
- Efficiency objective quantified: **≤ 1.15 Wh/km**.

### Changed
- **ADR-0004** — aspect ratio tightened from 6–8 to **6.0**.
- **ADR-0005** — superseded: the airfoil moves from "thin" to higher thickness *(later replaced by ADR-0027)*.

### Added
ADR-0012, 0015, 0016, 0018, 0021, 0022, 0023, 0024, 0025, 0026. Gaps **G6** (sweep factor) and **G7 (flutter, unanalyzed)**.

### Superseded
ADR-0011, 0013, 0014, 0017, 0019, 0020 — after evaluating PETG, PLA, PLA+, ASA and LW-PLA.

### Corrections

| # | Error | Correction |
|---|---|---|
| C6 | GJ computed with a 231 mm chord while the one consistent with AR 6.0 is 217 mm | Net effect on V_div: **−3 %**. The chord appears in both the numerator and denominator of q_D |
| C7 | It was claimed that the Eliminator at 360 km/h validated printed construction in general | It validates **its** material, almost certainly PLA. With a 40 % lower G, the PETG does not inherit that endorsement |
| C8 | It was claimed that PETG has better layer adhesion than PLA | **False.** Z retention: PLA 55 %, PETG 46 %, ASA 29 %. PETG wins on toughness, not adhesion |
| C9 | It was claimed that PETG cannot be glued | Too categorical. 3D-Gloop PETG, DCM (restricted in the EU) and 30-min epoxy exist |
| C10 | Shell mass estimated at 450–500 g | Wetted-area count: **550–650 g** |

---

## [1.0] — 2026-07-27

Initial research closed. Data consolidation, analytical framework, ADR-0001 to 0010 decisions and gaps G1–G5.

### Corrections

| # | Error | Correction |
|---|---|---|
| C1 | It was claimed that the Oswald factor collapses with aspect ratio for physical reasons | It is largely a **definition artifact**: e_v decreases with AR by algebraic construction. Raising AR does work; the real effect is saturation and the chord→Re coupling |
| C2 | It was claimed that forward sweep depends exclusively on the airfoil C_m0 | **It can and should use wash-in.** The two planforms are symmetric solutions. Opens the door to lightly reflexed airfoils |
| C3 | 3D printing was assumed to be the structurally weak option | It is a closed shell = torsion box |
| C4 | Arithmetic error solving for the Solar Impulse L/D | The correct value is L/D ≈ 49, not 31 |
| C5 | The Mojito maximum L/D was estimated at ≈ 11 | The value solved from real flight data is **≈ 7.4 in fast cruise** |
