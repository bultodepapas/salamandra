#!/usr/bin/env python3
"""Wash-in trim and section-stall window for Salamandra Article #1.

The lower bound is the geometric wash-in (plus equivalent neutral elevon)
required to trim at the selected static margin. The upper bound is set by the
first span station reaching the declared section cl_max. This script shares
mass, atmosphere, mission speed and geometry with the rest of the calculation
chain and exposes its results as importable functions.
"""
from functools import cache

import numpy as np
from design_config import (
    DESIGN_TWIST_DEG as SHARED_DESIGN_TWIST_DEG,
    ARTICLE_V1_ALLOCATION_MASS_KG,
    ARTICLE_V1_MASS_KG,
    CL_MAX_WING,
    CRUISE_SPEED_KMH,
    STALL_SPEED_LIMIT_KMH,
    STATIC_MARGIN,
    SWEEP_C4_DEG,
    TAPER,
    B,
    S,
    lift_coefficient,
    speed_mps,
    wing_loading_g_dm2,
)
from vlm_ala_volante import analiza, cl_local, geom, solve

DESIGN_REF_MASS = ARTICLE_V1_MASS_KG
V_CRUISE = speed_mps(CRUISE_SPEED_KMH)
V_STALL = speed_mps(STALL_SPEED_LIMIT_KMH)
SECTION_CL_MAX = 0.65       # Ananda et al. section band [M]
PROFILE_CM0 = 0.002095      # r1 root/tip integral, Ncrit 12 [D]
DESIGN_TWIST_DEG = SHARED_DESIGN_TWIST_DEG   # released wash-in
ELEVON_EQUIVALENT_CAP_DEG = 0.6

CL_CRUISE = lift_coefficient(DESIGN_REF_MASS, V_CRUISE)
CL_MAX_REQUIRED = lift_coefficient(DESIGN_REF_MASS, V_STALL)
CL_ALLOCATION_REQUIRED = lift_coefficient(ARTICLE_V1_ALLOCATION_MASS_KG, V_STALL)


@cache
def wash_in_pitch_yield(ny=40, nx=6):
    """Wing Cm0 increment per degree of linear tip wash-in."""
    zero = analiza(
        B, S, TAPER, SWEEP_C4_DEG, 0.0, ny=ny, nx=nx, verbose=False)
    four = analiza(
        B, S, TAPER, SWEEP_C4_DEG, 4.0, ny=ny, nx=nx, verbose=False)
    return (four["Cm0"] - zero["Cm0"]) / 4.0


def trim_requirement(static_margin=STATIC_MARGIN, profile_cm0=PROFILE_CM0,
                     ny=40, nx=6):
    """Required geometric-equivalent wash-in [deg] for cruise trim."""
    if static_margin <= 0.0:
        raise ValueError("static margin must be positive")
    yield_per_degree = wash_in_pitch_yield(ny, nx)
    if yield_per_degree <= 0.0:
        raise RuntimeError("wash-in pitch yield must be positive")
    required_cm0 = CL_CRUISE * static_margin
    twist_only = required_cm0 / yield_per_degree
    mixed = max(0.0, (required_cm0 - profile_cm0) / yield_per_degree)
    return {
        "required_cm0": required_cm0,
        "cm0_per_degree": yield_per_degree,
        "twist_only_deg": twist_only,
        "profile_plus_twist_deg": mixed,
    }


def section_stall_result(twist_deg, ny=40, nx=6):
    """Local-cl distribution when total CL reaches the 45 km/h requirement."""
    g = geom(B, S, TAPER, SWEEP_C4_DEG, twist_deg, ny=ny, nx=nx)
    cl_zero, _, _, _ = solve(g, 0.0)
    cl_four, _, _, _ = solve(g, 4.0)
    slope = (cl_four - cl_zero) / np.radians(4.0)
    alpha_deg = np.degrees((CL_MAX_REQUIRED - cl_zero) / slope)
    total_cl, _, lift, _ = solve(g, alpha_deg)
    y, local_cl, _ = cl_local(g, lift)
    right = y > 0.0
    y_right, cl_right = y[right], local_cl[right]
    peak = int(np.argmax(cl_right))
    return {
        "alpha_deg": alpha_deg,
        "wing_cl": total_cl,
        "eta_peak": y_right[peak] / (B / 2.0),
        "cl_root": cl_right[0],
        "cl_tip": cl_right[-1],
        "cl_peak": cl_right[peak],
        "margin": SECTION_CL_MAX - cl_right[peak],
    }


def main():
    neutral = analiza(B, S, TAPER, SWEEP_C4_DEG, 0.0, verbose=False)
    np_pct = (neutral["x_np"] - neutral["g"]["x_le_mac"]) / neutral["cbar"] * 100.0
    trim = trim_requirement()

    print("=" * 76)
    print("SALAMANDRA WASH-IN TRIM AND SECTION-STALL WINDOW")
    print("=" * 76)
    print(f"  Reference mass={DESIGN_REF_MASS:.5f} kg; wing loading="
          f"{wing_loading_g_dm2(DESIGN_REF_MASS):.2f} g/dm2")
    print(f"  CL cruise={CL_CRUISE:.5f} at {CRUISE_SPEED_KMH:.0f} km/h; "
          f"required CL at {STALL_SPEED_LIMIT_KMH:.0f} km/h={CL_MAX_REQUIRED:.5f}")
    print(f"  allocation-target CL at {STALL_SPEED_LIMIT_KMH:.0f} km/h="
          f"{CL_ALLOCATION_REQUIRED:.5f}; shared wing CLmax={CL_MAX_WING:.5f}")
    print(f"  section cl_max={SECTION_CL_MAX:.2f} [M]")
    print(f"  neutral point={np_pct:.2f} % MAC "
          f"(x={neutral['x_np']*1000:+.1f} mm); CL_alpha={neutral['CLa']:.3f}/rad")
    print(f"  wash-in pitch yield={trim['cm0_per_degree']:+.5f} Cm/deg")

    print("\nLOWER BOUND - cruise trim")
    print("  static margin   required Cm0   twist only   with r1 profile")
    for sm in (0.06, 0.08, 0.10, 0.12, 0.15):
        row = trim_requirement(sm)
        print(f"      {sm*100:4.0f} %        {row['required_cm0']:+.4f}       "
              f"{row['twist_only_deg']:5.2f} deg      "
              f"{row['profile_plus_twist_deg']:5.2f} deg")

    print("\nUPPER BOUND - local section cl at required aircraft CL")
    print("  wash-in   peak eta   root cl   tip cl   peak cl   margin")
    rows = {}
    for twist in (0.0, 2.0, 3.0, 4.0, 5.0, 6.0):
        row = section_stall_result(twist)
        rows[twist] = row
        print(f"   {twist:4.1f} deg    {row['eta_peak']*100:5.0f} %    "
              f"{row['cl_root']:+.3f}    {row['cl_tip']:+.3f}    "
              f"{row['cl_peak']:+.3f}    {row['margin']:+.3f}")

    residual = max(
        0.0, trim["profile_plus_twist_deg"] - DESIGN_TWIST_DEG)
    checks = {
        "allocation target retains positive shared-CLmax margin":
            CL_ALLOCATION_REQUIRED < CL_MAX_WING,
        "C32 lower model remains below shared wing CLmax at 45 km/h":
            CL_MAX_REQUIRED < CL_MAX_WING,
        "3 deg wash-in plus <=0.6 deg elevon equivalent closes trim":
            residual <= ELEVON_EQUIVALENT_CAP_DEG,
        "3 deg wash-in retains positive computed local-cl stall margin":
            rows[3.0]["margin"] > 0.0,
        "5 deg wash-in remains only marginally below the section-cl limit":
            0.0 < rows[5.0]["margin"] < 0.005,
        "6 deg wash-in exceeds the section-cl limit":
            rows[6.0]["margin"] < 0.0,
        "VLM solution reproduces requested total CL":
            abs(rows[3.0]["wing_cl"] - CL_MAX_REQUIRED) < 1e-10,
    }
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
