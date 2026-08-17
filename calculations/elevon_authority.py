#!/usr/bin/env python3
"""Elevon pitch authority and cruise trim for the Salamandra r1 airfoil family.

The VLM models an elevon as a local incidence change over 30--90 % of the
semi-span.  Flat-plate VLM has no section moment, so root and tip XFOIL Cm0 are
integrated with c^2 weights (0.6071/0.3929) before the VLM twist contribution
is added.  Positive elevon angle is trailing-edge-up/reflex.
"""
import numpy as np
from vlm_ala_volante import geom, solve
from design_config import B, S, SWEEP_C4_DEG, TAPER

SWEEP = SWEEP_C4_DEG
ETA_IN, ETA_OUT = 0.30, 0.90          # tramo de elevon (30-90 % b/2)
SM = 0.08
CL_CRU = 0.132                        # ventana_torsion.py
CM0_REQ = CL_CRU * SM                 # 0.01056
CM0_WING_N10 = +0.003258              # r1 root/tip integrated at cruise Re [D]
CM0_WING_N12 = +0.002095              # conservative trim case [D]
TWIST_DISENO = 3.0                    # R-TWIST (nueva cota, ver guia §5.3)


def cm0_wing(twist_deg, elev_deg):
    """Cm a CL=0 del ala (VLM, placa plana) para wash-in + elevon por tramos."""
    g = geom(B, S, TAPER, SWEEP, 0.0)
    eta = np.abs(g['cps'][:, 1]) / (B / 2)
    mask = (eta >= ETA_IN) & (eta <= ETA_OUT)
    g['eps'] = np.radians(twist_deg * eta + elev_deg * mask)
    CL1, Cm1, _, _ = solve(g, 0.0)
    CL2, Cm2, _, _ = solve(g, 4.0)
    dCm_dCL = (Cm2 - Cm1) / (CL2 - CL1)
    return Cm1 - CL1 * dCm_dCL


def main():
    print("=" * 70)
    print("ELEVON AUTHORITY - Salamandra r1 trim at 8% static margin [D]")
    print("=" * 70)
    dCm_tw = cm0_wing(1.0, 0.0) - cm0_wing(0.0, 0.0)
    dCm_de = cm0_wing(0.0, 1.0) - cm0_wing(0.0, 0.0)
    print(f"  wash-in yield : {dCm_tw:+.5f} /deg")
    print(f"  elevon yield  : {dCm_de:+.5f} /deg over 30--90% b/2")
    print(f"  required trim : Cm0 = {CM0_REQ:+.5f} (SM 8%, cruise CL 0.132)")

    print("\n  Trim closure with 3.0 deg printed wash-in:")
    elev_needed = {}
    for tag, cm0_wing_profile in [
            ("Ncrit 10 integrated r1", CM0_WING_N10),
            ("Ncrit 12 integrated r1", CM0_WING_N12)]:
        deficit = CM0_REQ - (cm0_wing_profile + dCm_tw * TWIST_DISENO)
        elev_deg = deficit / dCm_de
        elev_needed[tag] = elev_deg
        print(f"    {tag:28s}: profile Cm0 {cm0_wing_profile:+.4f} -> "
              f"residual {deficit:+.4f} -> elevon {elev_deg:+.2f} deg")

    print(f"\n  Control margin (limiting Ncrit 12 case):")
    cm0_lim = CM0_WING_N12 + dCm_tw * TWIST_DISENO
    d = CM0_REQ - cm0_lim
    for de in [5.0, 10.0, 20.0]:
        avail = dCm_de * de
        print(f"    elevon {de:5.1f} deg -> Dm {avail:+.4f}  "
              f"({avail/d:5.1f} x el trim requerido {d:+.4f})")
    best = elev_needed["Ncrit 10 integrated r1"]
    worst = elev_needed["Ncrit 12 integrated r1"]
    checks = {
        "computed wash-in yield is positive": dCm_tw > 0.0,
        "Ncrit 10 trim is within +/-0.6 deg": abs(best) <= 0.6,
        "Ncrit 12 trim is within +/-0.6 deg": abs(worst) <= 0.6,
        "5 deg control covers the limiting residual": dCm_de * 5.0 > d,
    }
    print("\n  VALIDACION")
    for name, passed in checks.items():
        print(f"    [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)

    print("\n  DECISION: the r1 root/tip profile family plus 3.0 deg wash-in closes")
    print("  the complete Ncrit 10--12 neutral-trim band.  Measured E2 polars remain")
    print("  the flight-release acceptance gate; no provisional 1.9 deg offset remains.")


if __name__ == "__main__":
    main()
