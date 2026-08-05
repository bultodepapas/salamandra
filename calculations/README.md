# Calculations

Analysis scripts. Each self-contained and runnable.

| File | What it does | Feeds |
|---|---|---|
| `vlm_ala_volante.py` | Vortex lattice for a forward-swept wing with taper and twist. Neutral point, CL_α, load distribution | I-07, G8 |
| `ventana_torsion.py` | Twist required for trim against tip-stall margin | I-07, G2 |
| `calibra_xfoil_e387.py` | Cross-checks an XFOIL Ncrit grid against the E387 (C) polar measured by UIUC | I-06, G2 |

## Usage

```bash
python3 vlm_ala_volante.py     # includes validation case
python3 ventana_torsion.py     # window analysis
python3 calibra_xfoil_e387.py --xfoil /path/to/xfoil
```

The first two scripts require only `numpy`.

`calibra_xfoil_e387.py` uses only the Python standard library, but needs the official
XFOIL executable. It downloads the coordinates and the measured polar from UIUC at runtime;
it does not replace them with a secondary copy.

## Validation

`vlm_ala_volante.py` includes a contrast case: a straight AR 6 wing without sweep or twist,
whose neutral point must fall at c/4 and whose CL_α must approximate the Helmbold formula.

**Any modification must pass that validation before use.** A MAC normalization error was detected exactly this way.

`calibra_xfoil_e387.py` validates its interpolation and its metric against an analytic case:
a polar with `Cd_calculated = 1.1 × Cd_measured` must return exactly a factor 1.1.

## Conventions

- `x` positive backward, origin at the root c/4
- `Lambda_c4` negative = forward sweep
- `epsilon` positive = wash-in (tip at higher incidence)
