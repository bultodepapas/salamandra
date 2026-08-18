# I-24 — Article #1 manoeuvre and gust-load envelope

**Status:** Partial closure — manoeuvre/ultimate semantics and positive V-n branch
calculated; dynamic gust loads and negative stall branch remain open  
**Date:** 2026-08-17  
**Feeds:** C33–C34, ADR-0044, Design Guide v0.21, F4/S1–S2, G11, E9,
`calculations/flight_envelope.py`

## 1. Question

The specification carried `+6/−3 g, later +9, gust-dominated` as one undivided
assumption. That wording did not say whether the numbers were manoeuvre limits, gust
loads or ultimate loads, supplied no V-n calculation and gave the structure no
unambiguous acceptance case.

This investigation separates the three concepts and asks what can be closed before CAD:

1. Where does the positive stall boundary meet the `+6 g` manoeuvre limit?
2. What does a traceable regulatory-reference discrete-gust method predict?
3. Which quantities are limit loads and which are ultimate structural loads?

## 2. Source basis and scope

- The current EASA CS-23 structural rules require an envelope containing manoeuvre and
  gust cases, evaluated over mass/CG, and define ultimate load as limit load multiplied
  by 1.5. Its AMC3 maps the corresponding legacy CS-VLA methods as an accepted route:
  [EASA Easy Access Rules for Normal-Category Aeroplanes, CS Amendment 6](https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-normal-category-CS-6-AMC-GM-5).
- The archived official 2017 Part 23 text supplies the auditable discrete-gust equation,
  the `K_g` definition and the sea-level reference velocities of 50 ft/s at `V_C` and
  25 ft/s at `V_D`: [14 CFR Part 23, §§23.333, 23.337 and 23.341](https://www.govinfo.gov/content/pkg/CFR-2017-title14-vol1/pdf/CFR-2017-title14-vol1-part23.pdf).
- NASA specifically warns that ultralight aircraft near 5 kg/m² wing loading acquire a
  substantial fraction of the gust motion; their internal loads and accelerations do
  not scale like those of conventional aircraft:
  [NASA TM X-73228, *Dynamics of ultralight aircraft: Motion in vertical gusts*](https://ntrs.nasa.gov/citations/19770017108).

These are **methodology references**, not a claim that CS-23/CS-VLA legally applies to
this 1.6 kg RC aircraft. The legacy rigid-aircraft equation is used as a conservative
screen and unit-checked implementation. A final Salamandra gust load requires a dynamic,
nonlinear model and flight correlation.

## 3. Reproducible method

The released VLM gives the complete-wing lift-curve slope

```text
a = CL_alpha = 4.27118 rad^-1
```

For wing loading `W/S`, mean aerodynamic chord `c_bar` and sea-level density `rho`:

```text
mu_g = 2(W/S) / (rho c_bar a g)
K_g  = 0.88 mu_g / (5.3 + mu_g)
Delta n = K_g rho V U_de a / (2 W/S)
```

`flight_envelope.py` independently converts the same case into the published imperial
`498(W/S)` form; the two agree within 0.11 %, consistent with the rounded constant 498.
The positive manoeuvre boundary is

```text
n_positive(V) = min[+6, (V/Vs)^2]
VA = Vs sqrt(6)
```

Here `CLmax = 0.589` is the released **3-D wing** value. The older requirement text
called `0.65` aircraft `CLmax`, but I-07 defines it as the **local section** `clmax`
screen that maps to the lower wing value through the non-elliptic span load. C34
corrects that notation; substituting 0.65 into the aircraft stall equation would create
a false mass and V-n margin.

No negative aerodynamic branch is fabricated: it requires `CLmin`, which the project
does not have. The normal E2 glide polar cannot supply negative lift; the CLI accepts
`--cl-min` only after a validated negative-polar analysis or section test exists.

## 4. Results

### 4.1 Manoeuvre and ultimate loads

| Configuration | Mass | Vs | VA at +6 g | Positive boundary at 105 km/h |
|---|---:|---:|---:|---:|
| CLEAN | 1,583.5 g | 44.48 km/h | **108.96 km/h** | **+5.57 g** |
| V1 lower model | 1,626.5 g | 45.08 km/h | **110.43 km/h** | **+5.42 g** |

For symmetric structural sizing, the corresponding whole-aircraft normal-force
resultants are:

| Config. | Limit +6 / −3 | Ultimate +9 / −4.5 |
|---|---:|---:|
| CLEAN | +93.2 / −46.6 N | +139.8 / −69.9 N |
| V1 | **+95.7 / −47.9 N** | **+143.6 / −71.8 N** |

These are total resultants, not point loads. A wing or joint proof case must apply the
VLM spanwise distribution and the correct inertia relief rather than placing the total
force at one station.

The first-flight speed limit therefore lies below `VA`: a commanded positive manoeuvre
is stall-limited before it reaches `+6 g`. Above `VA`, `+6 g` is the structural
manoeuvre limit. The declared `−3 g` line is structural only until `CLmin` closes the
negative stall branch.

Applying the 1.5 structural factor gives:

| Quantity | Positive | Negative |
|---|---:|---:|
| Manoeuvre **limit** load | +6.0 g | −3.0 g |
| Structural **ultimate** load | **+9.0 g** | **−4.5 g** |

This corrects C33: `+9 g` is not a later flight or manoeuvre target.

### 4.2 Regulatory-reference gust screen

For a screen with 15.24 m/s at 105 km/h and 7.62 m/s at 160 km/h:

| Config. | `mu_g` | `K_g` | n at 105 km/h | n at 160 km/h |
|---|---:|---:|---:|---:|
| CLEAN | 9.541 | 0.5657 | **+12.94 / −10.94** | **+10.10 / −8.10** |
| V1 | 9.801 | 0.5711 | **+12.74 / −10.74** | **+9.94 / −7.94** |

The maximum of `V U_de(V)` occurs at 107.5 km/h, not exactly at either endpoint; the
script checks it explicitly. At 105 km/h the positive screen implies `CL ≈ 1.37–1.38`,
far above the released wing `CLmax = 0.589`. The linear calculation is therefore
outside its validity range and is **not adopted as a structural design load**. What it
does establish is that the old phrase `gust-dominated +6/−3` had no consistent basis.

Inverting the same equation at 105 km/h gives a useful sensitivity boundary:

| Config. | Equivalent vertical gust at +6 | At −3 | Controlling |
|---|---:|---:|---|
| CLEAN | 6.38 m/s | **5.10 m/s** | negative limit |
| V1 | 6.49 m/s | **5.19 m/s** | negative limit |

These are equivalent **vertical** gust inputs to the model, not forecast surface-wind
gusts and not operational weather limits. The measurable flight quantity is normal
acceleration `n_z`; E9 will correlate that signal with pitot speed and turbulence.

## 5. Decision boundary

Closed now:

- `+6/−3 g` are provisional manoeuvre **limit** loads;
- `+9/−4.5 g` are the corresponding structural **ultimate** loads;
- the positive V-n branch and both Article #1 `VA` values are calculated;
- static component analyses made at limit load require failure margin at least 1.5,
  before any additional printed-process special factor.

Still open:

- negative aerodynamic stall boundary (`CLmin`, validated B3 extension/section test);
- nonlinear/dynamic gust response, including aircraft plunge, spanwise gust variation,
  flexibility and unsteady stall (G11);
- measured `n_z(V)` envelope and gust correlation (E9);
- printed-shell strength and stiffness acceptance (S3).

No CAD dimension or speed limit is relaxed by this work. The initial 105 km/h limit and
calm-air test discipline remain controlling.

## 6. Reproduction

```bash
python3 calculations/flight_envelope.py
python3 calculations/verify_calculations.py --all-scripts
```

The script carries nine deterministic validations: VLM range, physical `K_g`, SI versus
imperial parity, inverse round-trip, stall and `VA` identities, interior gust maximum,
intentional mismatch detection, and the 1.5 ultimate-load identity.
