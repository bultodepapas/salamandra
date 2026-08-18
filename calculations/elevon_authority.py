#!/usr/bin/env python3
"""Elevon pitch authority and cruise trim for the Salamandra r1 family.

The physical 0.28 c plain-elevon deflection is converted to ideal local
incidence with thin-airfoil effectiveness, then applied over the selected
35--90 % half-span with partial-panel overlap. Flat-plate VLM has no section
moment, so root/tip XFOIL Cm0 remains the separate profile input. Positive
elevon angle is trailing-edge-up/reflex.
"""
from design_config import (
    ARTICLE_V1_MASS_KG,
    CRUISE_SPEED_KMH,
    STATIC_MARGIN,
    lift_coefficient,
    speed_mps,
)
from elevon_sizing import (
    ARTICLE_1,
    CM0_WING_N10,
    CM0_WING_N12,
    DESIGN_TWIST_DEG,
    FLAP_EFFECTIVENESS,
    cm0_wing as sizing_cm0_wing,
)

SM = STATIC_MARGIN
CL_CRU = lift_coefficient(ARTICLE_V1_MASS_KG, speed_mps(CRUISE_SPEED_KMH))
CM0_REQ = CL_CRU * SM
DESIGN_TWIST = DESIGN_TWIST_DEG


def cm0_wing(twist_deg, elev_deg):
    """Wing Cm at CL=0 for the selected physical Article #1 elevon."""
    return sizing_cm0_wing(twist_deg, elev_deg, ARTICLE_1)


def main():
    print("=" * 70)
    print("ELEVON AUTHORITY - Salamandra r1 trim at 8% static margin [D]")
    print("=" * 70)
    dCm_tw = cm0_wing(1.0, 0.0) - cm0_wing(0.0, 0.0)
    dCm_de = cm0_wing(0.0, 1.0) - cm0_wing(0.0, 0.0)
    print(f"  wash-in yield : {dCm_tw:+.5f} /deg")
    print(f"  elevon yield  : {dCm_de:+.5f} /physical deg over 35--90% b/2")
    print(f"  ideal flap tau: {FLAP_EFFECTIVENESS:.4f} for c_e/c=0.28")
    print(f"  required trim : Cm0 = {CM0_REQ:+.5f} "
          f"(SM 8%, cruise CL {CL_CRU:.4f})")

    print("\n  Trim closure with 3.0 deg printed wash-in:")
    elev_needed = {}
    for tag, cm0_wing_profile in [
            ("Ncrit 10 integrated r1", CM0_WING_N10),
            ("Ncrit 12 integrated r1", CM0_WING_N12)]:
        deficit = CM0_REQ - (cm0_wing_profile + dCm_tw * DESIGN_TWIST)
        elev_deg = deficit / dCm_de
        elev_needed[tag] = elev_deg
        print(f"    {tag:28s}: profile Cm0 {cm0_wing_profile:+.4f} -> "
              f"residual {deficit:+.4f} -> elevon {elev_deg:+.2f} deg")

    print("\n  Control margin (limiting Ncrit 12 case):")
    cm0_lim = CM0_WING_N12 + dCm_tw * DESIGN_TWIST
    d = CM0_REQ - cm0_lim
    for de in [5.0, 10.0, 20.0]:
        avail = dCm_de * de
        print(f"    elevon {de:5.1f} deg -> Dm {avail:+.4f}  "
              f"({avail/d:5.1f} x required trim residual {d:+.4f})")
    best = elev_needed["Ncrit 10 integrated r1"]
    worst = elev_needed["Ncrit 12 integrated r1"]
    checks = {
        "computed wash-in yield is positive": dCm_tw > 0.0,
        "Ncrit 10 trim is within +/-0.6 deg": abs(best) <= 0.6,
        "Ncrit 12 trim is within +/-0.6 deg": abs(worst) <= 0.6,
        "5 deg control covers the limiting residual": dCm_de * 5.0 > d,
    }
    print("\n  VALIDATION")
    for name, passed in checks.items():
        print(f"    [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)

    print("\n  DECISION: the r1 root/tip profile family plus 3.0 deg wash-in closes")
    print("  the complete Ncrit 10--12 neutral-trim band.  Measured E2 polars remain")
    print("  the flight-release acceptance gate; no provisional 1.9 deg offset remains.")


if __name__ == "__main__":
    main()
