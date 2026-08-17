# I-22 — High-ROI v0.3 engineering audit

**Status:** Executed · **Date:** 2026-08-17 · **Feeds:** ADR-0041/0042/0043,
Design Guide v0.18, release v0.3.0

## 1. Ranking method

The audit ranked findings by safety/design effect, ability to unblock CAD, evidence
quality and implementation cost. The three highest-return corrections were the airfoil
generator and trim chain, cruise propulsion equilibrium, and Article #1 mass allocation.

## 2. Airfoil pipeline correction

Three faults affected the prior screening:

1. multiplying all ordinates to change thickness also multiplied the camber/reflex;
2. cached polars were keyed by Re/Ncrit but not by a geometry hash;
3. root and tip used nominal rather than actual local Reynolds numbers, and a global
   low-CL filter admitted post-stall points into the `Cm(CL)` regression.

`b3_screening.py` now scales thickness about the interpolated mean line, hashes each
geometry and analysis configuration, uses short XFOIL output paths, and fits only the
first pre-stall branch. `airfoil_reflex_trade.py` then screens coupled root/tip reflex at
root Re 240k/510k and tip Re 120k/255k. The selected r1 family is documented in
ADR-0041. All final endpoint polars and coordinate-thickness checks pass.

XFOIL 6.99 is the official MIT build: <https://web.mit.edu/drela/Public/web/xfoil/>.
Its results remain `[D]`; E2 is the measured closer.

## 3. Propulsion-equilibrium correction

The prior 9,900 rpm prescription came from the APC 8×8's peak measured efficiency and
did not enforce `T = D`. Scaling the official UIUC wind-tunnel coefficients at 95 km/h
shows that the peak-efficiency row would require 230 W electrical, versus O1's 109.25 W.
Solving the measured curve at the O1 power produces J 0.899, 8,667 rpm and 2.42 N.
The full derivation and sensitivity band are executable in `propulsion_match.py`.

Primary sources: [UIUC Propeller Database](https://m-selig.ae.illinois.edu/props/propDB.html),
[APC 8×8E product data](https://www.apcprop.com/product/8x8e/) and
[APC RPM limits](https://www.apcprop.com/wp-content/uploads/2022/03/APC-Propeller-RPM-Limits-rev5.pdf).

## 4. Mass/stall correction

The release estimate mixed conservative component allowances with no selected build.
The new allocation selects catalogued components, corrects the propeller blade mass,
and turns the already-declared 550 g PETG shell lower bound into a CAD limit. It avoids
the tempting but structurally rejected LW-PLA path. `mass_budget.py` preserves the v0.2
case and validates CLEAN at 1,583.5 g and V1 at 1,620.2 g. The 36.72 g V1a fin cap
matches the lower bound from `yaw_stability.py`. The coupled balance solution
moves the 6S1P pack to −359.6 mm and shortens the forward support span to 327 mm.

The result is a design allocation, not a measured mass claim. F2 must report CAD mass
properties and the complete aircraft must be weighed before flight.

## 5. Remaining high-risk items

The audit does not close the conservative aeroelastic uncertainty: initial V_limit
remains 105 km/h until S3 measures elastic axis and torsional stiffness. It also does not
turn XFOIL predictions into measured polars; E2 remains mandatory.
