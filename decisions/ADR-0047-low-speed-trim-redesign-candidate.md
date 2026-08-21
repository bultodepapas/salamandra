# ADR-0047 — Low-speed trim hold and r2a test candidate

**Status:** 🔄 Provisional test candidate — not flight or manufacturing release  
**Date:** 2026-08-21  
**Confidence:** Low `[D]`/`[I]`; E2A measured closure open  
**Reversible:** Yes, before wing CAD/tooling  
**Related gaps:** G2, OP-02, OP-03, OP-06, F2  
**Evidence:** [Low-speed trim redesign](../design/Low-Speed-Trim-Redesign-and-E2A-Plan.md)

## Context

ADR-0041 selected r1 using a cruise-only `Cm0` intercept and an ideal VLM
elevon-incidence increment. That calculation did not evaluate the section
moment at the local operating `CL`, did not include a deflected-section polar,
and gave the VLM control input the wrong physical trailing-edge label. The NF
Design Guide audit exposed 27...37 deg of low-speed demand in that legacy
screen, outside the +/-20 deg mechanical envelope.

The corrected coupled calculation uses root/mid/tip `CL`, `CD` and `Cm` at the
actual section Reynolds number, a nominal 0.45 mm printed trailing edge,
deflected-section XFOIL polars and the VLM span load. Positive physical
deflection is now unambiguously trailing-edge down. The r1 configuration fails
at least one 45 km/h/full-CG-band corner inside the mechanical limit.

## Decision

1. Place the r1 airfoil/twist/elevon system on **design hold** for new wing CAD.
   Existing r1 coordinate files remain immutable reference evidence and may be
   used to manufacture comparison coupons only.
2. Select **r2a-sm5** as the sole next physical-test candidate:

| Parameter | r1 reference | r2a test candidate |
|---|---:|---:|
| Root/tip t/c | 13.5% / 9.0% | unchanged |
| Added root/tip reflex aft of x/c 0.72 | 1.0 / 0.5 deg | **3.0 / 2.5 deg** |
| Linear tip twist | +3.0 deg wash-in | unchanged |
| Elevon | 28% c, eta 0.35...0.90 | unchanged for the first test |
| Nominal static margin | 8.0% MAC | **5.0% MAC** |
| Nominal xCG from root c/4 | -93.784 mm | **-87.035 mm** |
| xCG acceptance band | +/-5 mm | unchanged |

1. Do not publish r2a as canonical airfoil coordinates. First manufacture r1
   and r2a root/mid/tip E2A specimens with the real trailing edge and hinge,
   then measure section polars and rerun the coupled trim evaluation.
2. Retain the +/-20 deg mechanical stop. Measured acceptance requires trim
   inside +/-15 deg and its 95% uncertainty bound inside +/-20 deg.

## Quantitative basis

The XFOIL/VLM screen covers 45, 60, 75, 95 and 105 km/h; root/mid/tip Reynolds
numbers; Ncrit 6 and 10; and static margins 2.777%, 5.000% and 7.223%, which are
the 5% target plus the complete +/-5 mm CG band.

| Speed | Maximum absolute r2a trim over Ncrit and CG band |
|---:|---:|
| 45 km/h | 10.162 deg |
| 60 km/h | 7.627 deg |
| 75 km/h | 9.918 deg |
| 95 km/h | **11.030 deg** |
| 105 km/h | 10.969 deg |

All 30 cases remain inside the mechanical limit with at least 8.97 deg nominal
reserve. This is only a screen: 8 cases have a trim root bracketed by converged
deflected polars and 22 use a boundary control-slope extrapolation. The
`physical_gate_closed` flag therefore remains false.

The 5% nominal CG is analytically reachable in V1 with battery x = -338.976 mm.
The current aft station bound is -336.104 mm, leaving only 2.872 mm travel
reserve. F2 must demonstrate that reach with measured masses; the candidate
does not close packaging.

## Consequences

- ADR-0041 remains the record of r1 generation but no longer authorizes new
  flight-wing CAD. Its low-speed review condition has fired.
- ADR-0045 remains the geometric starting point, not validated pitch authority.
- The README, concise Design Guide and open-point register must show G2 as open.
- CAD, structure, winglet and O1 performance optimization remain downstream of
  E2A. Coupon geometry and balance-fixture work are allowed.
- A failed E2A result reopens reflex, twist, hinge/elevon chord/span and CG as a
  coupled trade; no single parameter is protected by this candidate ADR.

## Acceptance trigger

Promote or replace r2a only after the complete E2A matrix in
`tests/E2A-printed-section-polars/` is populated with measured data and the
measured-data evaluator passes every speed/CG trim case without control or
`CL` extrapolation. The signed E2A result must separately close uncertainty,
stall order/margin, hinge hysteresis and O1 drag propagation; the trim solver
cannot close the complete physical gate by itself.
