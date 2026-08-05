# Experimental program

| # | Test | Closes | Effort | Status |
|---|---|---|---|---|
| **E1** | Geometry extraction from reference meshes | G1 | Low | 🔄 Partial |
| **E2** | Glide polar with pitot and blackbox | G3, G2 · validates **O1** | Medium | ⬜ |
| **E3** | Propeller-matching sweep | **Realizes O1** | Low | ⬜ |
| **E5** | FFT of blackbox gyro traces | G4, G7 | Null | ⬜ |
| **E7** | **Southwell in flight** | **G6** | Low | ⬜ |

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
