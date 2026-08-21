# Experimental program

Before aircraft experiments, Gate M1 uses the separate
[MP-04 H01–H22 hardware-characterisation campaign](MP04-hardware-characterisation/README.md).
Its schema-controlled record is intentionally blank: the repository supplies the method,
not invented measurements. The generated external-envelope/ballast fixtures live in
[`geometry/equipment-dummies/`](../geometry/equipment-dummies/README.md).

| # | Test | Closes | Effort | Status |
|---|---|---|---|---|
| **E1** | Geometry extraction from reference meshes | G1 | Low | 🔄 Partial |
| **E2** | Glide polar with pitot and blackbox | G3, G2 · validates **O1** | Medium | ⬜ |
| **E2A** | **Printed root/mid/tip section `CL/CD/Cm` with real TE/hinge** | **G2, OP-02/03/06** · validates low-speed trim | High | ⬜ |
| **E3** | Propeller-matching sweep | **Realizes O1** | Low | ⬜ |
| **E5** | FFT of blackbox gyro traces | G4, G7 | Null | ⬜ |
| **E7** | **Southwell in flight** | **G6** | Low | ⬜ |
| **E8** | **Yaw perturbation / Dutch-roll decay (I-20)** | **G10** — closes the directional-stability gap | Low | ⬜ |
| **E9** | **Normal-load / gust correlation (I-24)** | **G11** — validates the low-amplitude load model; does not proof-test +6 g | Low | ⬜ |

## Withdrawn

| # | Test | Reason |
|---|---|---|
| E4 | Bench twist on a printed coupon | Replaced by anchoring to measured reference and by E7 |
| E6 | Inverse calibration of the model against the Peregrine | **C13** — the Peregrine is at a factor ~3 from the prediction; it does not falsify the model but does not validate it either |

---

## E1 — geometry extraction

Slice sections of the reference meshes at different stations. Obtain airfoil coordinates, area, aspect ratio, taper, c/4 sweep and **twist distribution**.

**Done:** Peregrine t/c = 13.5 % `[M]`, designer's print profile.
**Missing:** full planform; requires the outer panel files.
**Alternative:** StuntDouble family (Nemesis + Stinger/Stormbird) — provides a
**quasi-controlled planform comparison**: same author, constructive family and
comparable AR, but airfoil, scale and propulsion change. It serves as a geometric prior; it
does not allow attributing causality to the sweep. See [I-08](../research/I-08-stuntdouble-family.md).

## E2 — glide polar

Flights with the motor off at stabilized speeds, recording descent rate with the barometer and **true airspeed with pitot**.

Produces the real polar of the complete aircraft without a wind tunnel. **It is the only instrument that separates propulsive losses from aerodynamic losses.**

⚠️ Without pitot it is not valid: ground speed is contaminated by the wind.

## E2A — printed-section polar and elevon trim

E2A is now the upstream aerodynamic gate. It measures root/mid/tip printed
sections, manufactured trailing edges and representative hinges at the exact
Reynolds ladder, including physical deflections. See the complete
[E2A procedure](E2A-printed-section-polars/README.md).

E2 and E2A are complementary: a motor-off aircraft glide polar cannot isolate
section pitching moment or hinge effectiveness, while a 2-D section test does
not measure complete-aircraft interference or total drag.

## E3 — propeller-matching sweep

Stabilized flight at fixed speed logging current, for 3–4 diameter/pitch combinations. Compare against the J predicted by the UIUC database.

**It is the test that realizes objective O1.** It can run on any test platform, including an existing one: **it does not depend on the project's airframe.**

## E5 — blackbox FFT

With the fixed-wing loop at 1000 µs, the gyroscope logs at 1 kHz → Nyquist 500 Hz. Enough to resolve ω_α (~106 Hz) and ω_β (~82 Hz).

**It requires no dedicated test:** it comes out of the first flight.

## E7 — Southwell in flight

See [I-05](../research/I-05-divergence-flutter.md) for the rationale.

1. Stabilized Cruise flight at 90, 110, 130, 150 km/h
2. Blackbox: elevon trim deflection against dynamic pressure
3. **1/Δtrim against q → a straight line that intercepts the axis at q_D**

⚠️ **Prerequisite: resolve G9** (porpoising in automatic modes).

## E8 — yaw perturbation / Dutch-roll decay

Closes **G10** (directional stability) with `[M]` data. Defined in
[I-20](../research/I-20-yaw-stability-centerline-fin.md) §8.

1. Stabilized flight at cruise (95 km/h), both variants (CLEAN and V1, ADR-0038)
2. Aileron-impulse perturbation (rudder-kick analog — no rudder surface), then hands-off
3. Blackbox gyro traces → yaw-subsidence time constant / Dutch-roll decay per variant
4. Compare against the corrected I-20/C31/C40 prediction (CLEAN: unstable mode
   τ ≈ **0.12 s**; V1: damped pair decay τ ≈ **0.8 s**, ω_n 5.35 rad/s, ζ 0.231 `[E]`)
   — the calculation is bounded, the flight decides

**This test also validates the claim that the fin is worth its drag** (ADR-0038): if the
CLEAN build shows acceptable yaw behavior, the V1 fin can be demoted to a
convenience-only variant.

## E9 — normal-load / gust correlation

Closes the measured part of **G11** without attempting a dangerous in-flight proof load.
The reduction method and reference equation are defined in
[I-24](../research/I-24-flight-load-envelope.md).

1. Calibrate the IMU normal axis against gravity in static orientations; record aircraft
   mass/configuration and synchronize pitot, IMU, attitude and blackbox time bases.
2. In calm conditions, fly stabilized segments at 65, 80, 95 and at most 105 km/h.
   Use ordinary shallow turns and small pitch inputs only; do not deliberately exceed
   2 g during this correlation test.
3. Reduce body acceleration to aircraft normal load `n_z`, separate control-commanded
   events from atmospheric events, and compare low-amplitude gust increments with the
   I-24 slope `Delta n / U_de` at each pitot speed.
4. Report positive and negative events separately, with speed, mass, configuration,
   turbulence context and uncertainty. If uncommanded load approaches the provisional
   +6/−3 limits, terminate the programme and lower the speed ceiling.

E9 validates only the small-disturbance part of the model. It does not establish CLmin,
dynamic-stall loads, ultimate strength or permission to expand V_limit; those require
section evidence, the S3 structural model and ground proof testing.

---

## Data format

Each test in its own subfolder:

```
tests/EX-name/
  README.md          Method, conditions, complete aircraft configuration
  raw/               Unprocessed blackbox logs
  reduction.py       Reduction script, versioned
  results.md         Result with confidence tag and error bars
```

**Contributors' data must declare the complete configuration** (pack, motor, propeller, mass, material, perimeters, infill) to be comparable.
