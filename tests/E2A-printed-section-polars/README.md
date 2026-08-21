# E2A — printed-section polar and elevon-trim acceptance

**Gate:** G2 / OP-02 / OP-03 / OP-06  
**Status:** OPEN  
**Evidence required:** measured `[M]`  
**Configurations:** r1 reference and r2a candidate from ADR-0047

## 1. Purpose

Measure the lift, drag and quarter-chord pitching moment of the actual printed
root, midspan and tip section families, including the manufactured trailing
edge and representative hinge/elevon construction. The data replace the
constant-`Cm0`, ideal-flap and sealed-hinge assumptions that produced the
incorrect r1 low-speed trim closure.

E2A is a section test. The existing E2 motor-off glide test remains the
complete-aircraft drag-polar test; it cannot identify root/mid/tip `Cm(CL)` or
hinge effectiveness by itself.

## 2. Specimens

Print at least two independently manufactured sets for each candidate family:

| ID | Span station | Nominal chord | Required construction |
|---|---:|---:|---|
| ROOT | eta = 0.00 | 289.231 mm | Actual fixed root trailing-edge bridge; an additional representative hinged coupon may be used to identify the section control derivative |
| MID | eta = 0.50 | 216.923 mm | Actual 28% chord elevon, hinge, seal or gap, bevel and surface finish |
| TIP | eta = 1.00 | 144.615 mm | Actual fixed tip; an additional representative hinged coupon may be used to identify the outer control derivative |

Use the released slicer orientation, material, wall count, line width, layer
height, hinge material, post-processing and paint. Do not hand-fair the model
unless the flight article will receive the identical process.

Before aerodynamic testing, scan or CMM each section in its unloaded state and
record:

- chord, maximum thickness and its station;
- mean-line/reflex ordinates at x/c = 0.10 increments;
- leading-edge radius proxy;
- upper/lower trailing-edge coordinates and thickness;
- hinge axis, gap, bevel, freeplay and commanded versus measured deflection;
- surface roughness method and print orientation.

The provisional geometry screen is RMS contour error <= 0.30 mm and maximum
local error <= 0.50 mm `[E]`. These are specimen-quality limits, not claims
about an unmeasured printer.

## 3. Test matrix

Run root, mid and tip at the section Reynolds numbers produced by the five
aircraft speeds. Values are calculated from the actual chords and
`nu = 1.50e-5 m2/s`; set tunnel speed from the measured chord and measured air
properties.

| Aircraft speed | Root Re | Mid Re | Tip Re |
|---:|---:|---:|---:|
| 45 km/h | 241k | 181k | 121k |
| 60 km/h | 321k | 241k | 161k |
| 75 km/h | 402k | 301k | 201k |
| 95 km/h | 509k | 382k | 254k |
| 105 km/h | 562k | 422k | 281k |

The 562k root point is required because the trim envelope extends to 105 km/h,
even though the original request ended near 510k.

At every applicable station/Reynolds point test symmetric-equivalent elevon
deflections `-20, -10, -5, 0, +5, +10, +20 deg`, where positive means
trailing-edge down. Root/tip hinged coupons are aerodynamic interpolation
specimens; the flight wing remains fixed outside eta = 0.35...0.90.

Sweep alpha from a confirmed negative-lift point through stall and at least
two post-stall points. Use steps <= 0.5 deg in the attached-flow range and
<= 0.25 deg around the expected trim `CL`. Repeat every sweep three times,
including one descending-alpha sweep to expose hysteresis.

## 4. Facility and uncertainty controls

- Correct tare, support interference, wall/blockage and balance-axis transfer
  to the section quarter chord. Document the equations and raw tare runs.
- Keep projected solid blockage below 5%; report the applied correction.
- Measure dynamic pressure, temperature and pressure for every run. Hold
  Reynolds number within +/-2%.
- Calibrate lift, drag and moment before and after the campaign with traceable
  loads. Target expanded uncertainties (k = 2): `CL <= 0.02`, `CD <= 0.002`
  and `Cm <= 0.002` in the attached range.
- Set alpha within +/-0.10 deg and loaded elevon angle within +/-0.20 deg.
- Record tunnel turbulence intensity. Natural-transition XFOIL `Ncrit` is not
  a substitute for that measurement.
- Inspect loaded hinge deformation photogrammetrically or with a second angle
  encoder. Commanded servo angle alone is not the aerodynamic angle.

## 5. Data contract

Write unmodified observations to `raw/section_polars.csv`. One row is one
settled alpha point in one repeat. Required conventions are:

- `source=measured` only for physical balance data;
- `ncrit=0` for measurements;
- `cm_c4` is nose-up positive about the measured section quarter chord;
- `deflection_deg_te_down_positive` uses the sign above;
- coefficient sigma columns contain one-standard-deviation reduction
  uncertainty; retain raw sensor files separately when available.

Do not average repeat sweeps in the raw file. The processed polar supplied to
`low_speed_trim_redesign.py evaluate` must contain one uncertainty-weighted
mean row per station/speed/deflection/alpha.

## 6. Acceptance

E2A closes only if all of the following hold after uncertainty propagation:

1. Every 45...105 km/h point and the complete nominal-CG +/-5 mm band has a
   trim root within +/-15 deg, leaving at least 5 deg to the mechanical stop.
2. The 95% uncertainty bound on required trim remains inside +/-20 deg.
3. The measured local section `CLmax` exceeds the coupled demand with at least
   10% coefficient margin; the outer section must not lose lift before the
   inboard section at the matched wing state.
4. No trim point depends on post-stall data or extrapolation beyond the
   measured deflection range.
5. Hinge reversal, freeplay, hysteresis and repeat-to-repeat `Cm` variation
   remain within the uncertainty budget.
6. Measured profile drag is propagated into the 95 km/h O1 energy calculation;
   aerodynamic acceptance does not by itself close the energy objective.

If r2a fails, update profile reflex, twist, elevon chord/span or target CG in a
new candidate. Do not alter canonical CAD coordinates silently.

## 7. Reproduction

After producing an aggregated measured CSV with the same aerodynamic columns:

```bash
python3 calculations/low_speed_trim_redesign.py evaluate \
  --input tests/E2A-printed-section-polars/processed/section_polars.csv \
  --name r2a-sm5 --root-reflex 3.0 --tip-reflex 2.5 \
  --twist 3.0 --static-margin 5.0
```

The evaluator sets `measured_trim_subgate_pass=true` only when every input row
has `source=measured` and every trim case passes without extrapolation. It
deliberately leaves `physical_gate_closed=false`: the signed E2A result must
also dispose uncertainty, `CLmax`/stall order, hinge hysteresis and O1 drag
propagation. This prevents a polar CSV alone from authorizing flight CAD.
