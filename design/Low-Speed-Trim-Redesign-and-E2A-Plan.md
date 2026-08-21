# Salamandra low-speed trim redesign and E2A verification plan

**Date:** 2026-08-21  
**Authority:** engineering design screen `[D]` on manufacturing proxies `[I]`  
**Release state:** **DESIGN HOLD — no wing manufacturing or flight release**  
**Decision:** [ADR-0047](../decisions/ADR-0047-low-speed-trim-redesign-candidate.md)

## Outcome

The r1 profile/twist/elevon configuration is not a valid low-speed-trim
release. The project shall test one replacement candidate, **r2a-sm5**, before
continuing irreversible wing CAD.

r2a retains the 13.5/9.0% thickness schedule, +3 deg wash-in and 28% chord
elevon, increases added root/tip reflex from 1.0/0.5 deg to **3.0/2.5 deg**, and
moves the nominal target from 8% to **5% static margin**. Its nominal target CG
is **-87.035 mm** from the root quarter chord.

The five-speed computational screen places all 30 speed/Ncrit/CG cases inside
**11.04 deg**, compared with the +/-20 deg mechanical envelope. This does not
validate the aircraft: 22/30 trim roots extrapolate the local control slope
beyond the converged deflection matrix, and the hinge geometry is still a
sealed proxy.

## What was wrong in r1

The former closure combined three incompatible simplifications:

1. It selected the profile from the fitted cruise `Cm0` intercept and treated
   that moment as independent of operating `CL` and Reynolds number.
2. It represented a physical elevon as an ideal equivalent-incidence change in
   VLM but omitted the large deflected-section `Cm` increment.
3. It described positive control as trailing-edge up while applying positive
   local incidence, which corresponds to trailing-edge down lift effect.

The earlier 27...37 deg result remains useful as a non-conformance alarm, but
it is not a physically consistent elevon schedule. In the corrected model,
positive deflection is trailing-edge down and the low-speed nose-up trim input
is trailing-edge up.

The profile generator also rotated coordinates onto the chord line without
dividing by chord length. The error was small (about 0.15 mm at the root) but
systematic. `normalize_chord()` now maps the mean chord to exactly one before a
new candidate is generated. Existing r1 files remain historical evidence.

## Corrected calculation chain

[`low_speed_trim_redesign.py`](../calculations/low_speed_trim_redesign.py):

1. Generates root, eta=0.5 and tip section proxies with a 0.45 mm trailing
   edge and rigid 28% chord deflection.
2. Runs XFOIL 7.00 at the exact section Reynolds numbers for 45, 60, 75, 95
   and 105 km/h. Ncrit 6 and 10 bound the computational transition assumption;
   physical data use no Ncrit surrogate.
3. Converts the XFOIL zero-lift shift into a spanwise VLM control-incidence
   increment only over eta=0.35...0.90.
4. Solves global alpha at the required aircraft `CL`, then evaluates each
   strip's section `Cm` and `CD` at its local `cl`.
5. Adds the integrated section moment to the VLM lift-distribution moment and
   transfers it to each CG in the full +/-5 mm band.
6. Interpolates bracketed trim roots. A boundary control-slope extrapolation is
   explicitly marked `SCREEN` and can never close the physical gate.

The exact prediction matrix, trim table, solver version and binary hash are in
[`calculations/trim_redesign_out/`](../calculations/trim_redesign_out/README.md).

## Candidate comparison

| Quantity | r1-sm8 | r2a-sm5 |
|---|---:|---:|
| Root/tip added reflex | 1.0/0.5 deg | **3.0/2.5 deg** |
| Nominal static margin | 8.0% | **5.0%** |
| CG-band static margins | 5.777...10.223% | **2.777...7.223%** |
| Low-speed/full-band mechanical screen | **FAIL** | **PASS `[D]/[I]`** |
| Maximum predicted/extrapolated trim | >20 deg in at least one corner | **11.030 deg** |
| Directly bracketed cases | 12/18 quick cases | 8/30 full cases |
| Physical closure | No | No |

### r2a trim envelope

| Speed | Worst absolute trim | Limiting tendency |
|---:|---:|---|
| 45 km/h | 10.162 deg | Forward CG, Ncrit 10, trailing-edge up |
| 60 km/h | 7.627 deg | Aft CG, Ncrit 6, trailing-edge down |
| 75 km/h | 9.918 deg | Aft CG, Ncrit 6, trailing-edge down |
| 95 km/h | **11.030 deg** | Aft CG, Ncrit 10, trailing-edge down |
| 105 km/h | 10.969 deg | Aft CG, Ncrit 10, trailing-edge down |

The schedule crosses through neutral between low speed and cruise. That is
expected for the more-reflexed profile and reduced static margin, but it makes
hinge effectiveness and `Cm` uncertainty decisive.

## CG and packaging consequence

Using the VLM neutral point of -75.787 mm and MAC 224.854 mm:

- nominal 5% SM gives xCG = **-87.035 mm**;
- the +/-5 mm band is -92.035...-82.035 mm;
- the implied VLM static-margin band is 7.223...2.777%;
- V1 requires battery x = **-338.976 mm** at nominal CG;
- the present aft bound is -336.104 mm, only **2.872 mm** farther aft.

The target is analytically reachable but has little rail reserve. F2 measured
mass properties and first-assembly balance remain mandatory. A central-body NP
shift or a larger real CG uncertainty can invalidate the candidate.

## Physical work package

The controlling procedure is
[`tests/E2A-printed-section-polars/README.md`](../tests/E2A-printed-section-polars/README.md).
It requires printed r1 and r2a root/mid/tip specimens, as-built contour
metrology, the real trailing edge and hinge, five section Reynolds points,
seven deflections from -20 to +20 deg and repeated `CL/CD/Cm` sweeps.

Measured acceptance is:

- trim <= +/-15 deg at every speed and CG point;
- 95% trim uncertainty remains inside +/-20 deg;
- local `CLmax` retains at least 10% margin;
- no accepted case uses post-stall data or extrapolation;
- measured drag is propagated to O1 rather than ignored.

## Work permitted during the hold

Permitted: coupon CAD, balance-fixture design, printed contour metrology,
wind-tunnel planning, data reduction and reversible battery-rail review.

Held: final wing loft, production segmentation tied to r1 ordinates,
structure optimization around a frozen section, winglets, performance claims
and flight release.

## Reproduction

```bash
python3 calculations/low_speed_trim_redesign.py predict \
  --xfoil /home/bulto/.local/bin/xfoil-7.00 \
  --name r2a-sm5 --root-reflex 3.0 --tip-reflex 2.5 \
  --twist 3.0 --static-margin 5.0
```

The locally compiled executable reports XFOIL 7.00 and has SHA-256
`000b0468d9a7f4fce42d6fac24bd14147d7d326c8a9035909c8e9f98d180f50e`.
It was compiled from the official MIT `xfoil6.996.tgz` source with gfortran
13.3, double precision and `-fallow-argument-mismatch`. The Ubuntu 6.99 binary
was rejected after a reproducible `SIGFPE` even on NACA 0012.

No XFOIL result in this report is measured evidence.
