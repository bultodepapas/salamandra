#!/usr/bin/env python3
"""Canonical Salamandra Article #1 numerical design contract.

This module is the single numerical source for quantities shared by two or more
analysis scripts: planform geometry, atmosphere, mission points, load cases and
released Article #1 mass targets.  Model-specific assumptions remain in their
own modules.  Run this file directly after changing any shared input; every
invariant must pass before the Design Guide or CAD is released.

Coordinate convention: x aft, y starboard, origin at the root quarter chord.
Negative quarter-chord sweep is forward sweep.
"""
from math import atan, degrees, isclose, radians, tan

B = 1.300
S = 0.282
TAPER = 0.50
SWEEP_C4_DEG = -15.0          # ADR-0040 / I-21
ROOT_TC = 0.135
TIP_TC = 0.090

# Physical reference conditions.  G0 deliberately retains the project's
# engineering value used by every released calculation; changing it is a
# controlled numerical-contract revision, not a local cleanup.
G0 = 9.81                     # m/s2
RHO_SL = 1.225                # kg/m3, ISA sea-level density [M]
NU_SL = 1.50e-5               # m2/s, declared low-altitude value [E]

# Mission and certification-like design points.  The operational article V_NE
# and the higher structural sizing speed are different quantities by design.
CRUISE_SPEED_KMH = 95.0
STALL_SPEED_LIMIT_KMH = 45.0
INITIAL_SPEED_LIMIT_KMH = 105.0
ARTICLE_V_NE_KMH = 160.0
STRUCTURAL_DESIGN_SPEED_KMH = 180.0
O1_ENERGY_LIMIT_WH_PER_KM = 1.15
REFERENCE_BEC_EFFICIENCY = 0.90   # battery-to-avionics rail efficiency [E]
POSITIVE_LIMIT_LOAD_FACTOR = 6.0
NEGATIVE_LIMIT_LOAD_FACTOR = -3.0
ULTIMATE_SAFETY_FACTOR = 1.5
PETG_DENSITY_KG_M3 = 1270.0    # 1.27 g/cm3, project material contract [M]/[E]

# Aerodynamic and mass contract used by coupled performance calculations.
CL_MAX_WING = 0.589           # I-07 wing value [D], pending E2
STATIC_MARGIN = 0.08
ARTICLE_CLEAN_MASS_KG = 1.5835
V1_FIN_MASS_CAP_KG = 0.03672          # allocation target retained by ADR-0043
V1_FIN_SHELL_MOUNT_LOWER_KG = 0.03731 # current V1a analytical lower model [E]
V1_FIN_SPAR_MASS_KG = 0.00570         # mandatory aluminium spar [D]/[E]
V1_FIN_MODEL_LOWER_KG = (
    V1_FIN_SHELL_MOUNT_LOWER_KG + V1_FIN_SPAR_MASS_KG)
ARTICLE_V1_ALLOCATION_MASS_KG = ARTICLE_CLEAN_MASS_KG + V1_FIN_MASS_CAP_KG
ARTICLE_V1_MASS_KG = ARTICLE_CLEAN_MASS_KG + V1_FIN_MODEL_LOWER_KG

HALF_SPAN = B / 2.0
ROOT_CHORD = 2.0 * S / (B * (1.0 + TAPER))
TIP_CHORD = TAPER * ROOT_CHORD
MAC = (2.0 / 3.0) * ROOT_CHORD * (1.0 + TAPER + TAPER**2) / (1.0 + TAPER)
Y_MAC = (B / 6.0) * (1.0 + 2.0 * TAPER) / (1.0 + TAPER)
ASPECT_RATIO = B**2 / S

STATION_Y = (0.000, 0.130, 0.195, 0.325, 0.347, 0.4875, 0.498, 0.585, 0.650)


def chord(y):
    """Local chord [m] for |y| in [0, b/2]."""
    if abs(y) > HALF_SPAN + 1e-12:
        raise ValueError(f"span station {y!r} m is outside +/-{HALF_SPAN} m")
    eta = abs(y) / HALF_SPAN
    return ROOT_CHORD * (1.0 - (1.0 - TAPER) * eta)


def thickness_ratio(y):
    """Linear relative-thickness schedule."""
    if abs(y) > HALF_SPAN + 1e-12:
        raise ValueError(f"span station {y!r} m is outside +/-{HALF_SPAN} m")
    eta = abs(y) / HALF_SPAN
    return ROOT_TC + (TIP_TC - ROOT_TC) * eta


def x_c4(y, sweep_deg=SWEEP_C4_DEG):
    if abs(y) > HALF_SPAN + 1e-12:
        raise ValueError(f"span station {y!r} m is outside +/-{HALF_SPAN} m")
    return abs(y) * tan(radians(sweep_deg))


def x_le(y, sweep_deg=SWEEP_C4_DEG):
    return x_c4(y, sweep_deg) - chord(y) / 4.0


def x_te(y, sweep_deg=SWEEP_C4_DEG):
    return x_c4(y, sweep_deg) + 3.0 * chord(y) / 4.0


def planform_centroid(sweep_deg=SWEEP_C4_DEG):
    """Exact area-centroid x station of the trapezoidal planform."""
    return Y_MAC * tan(radians(sweep_deg)) + MAC / 4.0


def line_sweep_deg(x_root, x_tip):
    return degrees(atan((x_tip - x_root) / HALF_SPAN))


def speed_mps(speed_kmh):
    """Convert km/h to m/s with a positive-domain check."""
    if speed_kmh <= 0.0:
        raise ValueError("speed must be positive")
    return speed_kmh / 3.6


def dynamic_pressure(speed, rho=RHO_SL):
    """Dynamic pressure [Pa] from speed [m/s] and density [kg/m3]."""
    if speed <= 0.0 or rho <= 0.0:
        raise ValueError("speed and density must be positive")
    return 0.5 * rho * speed**2


def lift_coefficient(mass_kg, speed, area=S, rho=RHO_SL):
    """Level-flight lift coefficient for SI inputs."""
    if mass_kg <= 0.0 or area <= 0.0:
        raise ValueError("mass and area must be positive")
    return mass_kg * G0 / (dynamic_pressure(speed, rho) * area)


def stall_speed(mass_kg, cl_max=CL_MAX_WING, area=S, rho=RHO_SL):
    """Stall speed [m/s] for SI inputs."""
    if mass_kg <= 0.0 or cl_max <= 0.0 or area <= 0.0 or rho <= 0.0:
        raise ValueError("mass, CLmax, area and density must be positive")
    return (2.0 * mass_kg * G0 / (rho * area * cl_max)) ** 0.5


def mass_at_stall_speed(speed, cl_max=CL_MAX_WING, area=S, rho=RHO_SL):
    """Maximum mass [kg] corresponding to a specified stall speed [m/s]."""
    if speed <= 0.0 or cl_max <= 0.0 or area <= 0.0 or rho <= 0.0:
        raise ValueError("speed, CLmax, area and density must be positive")
    return dynamic_pressure(speed, rho) * area * cl_max / G0


def wing_loading_g_dm2(mass_kg, area=S):
    """Wing loading [g/dm2]."""
    if mass_kg <= 0.0 or area <= 0.0:
        raise ValueError("mass and area must be positive")
    return mass_kg * 1000.0 / (area * 100.0)


def electrical_power_limit_w(
        speed_kmh=CRUISE_SPEED_KMH,
        energy_wh_per_km=O1_ENERGY_LIMIT_WH_PER_KM):
    """Total battery-power limit [W] implied by a Wh/km objective."""
    if speed_kmh <= 0.0 or energy_wh_per_km <= 0.0:
        raise ValueError("speed and specific energy must be positive")
    return speed_kmh * energy_wh_per_km


def stations(sweep_deg=SWEEP_C4_DEG):
    """Rows: y, chord, t/c, thickness, x_LE, x_c/4, x_TE [SI units]."""
    return tuple(
        (y, chord(y), thickness_ratio(y), chord(y) * thickness_ratio(y),
         x_le(y, sweep_deg), x_c4(y, sweep_deg), x_te(y, sweep_deg))
        for y in STATION_Y
    )


STATIONS = tuple((y, c, tc) for y, c, tc, *_ in stations())


def validate_geometry():
    """Return named invariant checks. Every result must be true."""
    area = B * (ROOT_CHORD + TIP_CHORD) / 2.0
    tip_from_coordinates = x_te(HALF_SPAN) - x_le(HALF_SPAN)
    c4_sweep = line_sweep_deg(x_c4(0.0), x_c4(HALF_SPAN))
    le_sweep = line_sweep_deg(x_le(0.0), x_le(HALF_SPAN))
    te_sweep = line_sweep_deg(x_te(0.0), x_te(HALF_SPAN))
    return {
        "trapezoid area equals S": isclose(area, S, abs_tol=1e-12),
        "tip chord equals x_TE - x_LE": isclose(
            tip_from_coordinates, TIP_CHORD, abs_tol=1e-12),
        "quarter-chord sweep is canonical": isclose(
            c4_sweep, SWEEP_C4_DEG, abs_tol=1e-12),
        "LE is forward swept": le_sweep < 0.0,
        "TE is forward swept": te_sweep < 0.0,
        "last station is the tip": isclose(STATION_Y[-1], HALF_SPAN),
        "root and tip t/c are preserved": (
            isclose(thickness_ratio(0.0), ROOT_TC)
            and isclose(thickness_ratio(HALF_SPAN), TIP_TC)),
        "canonical aspect ratio is six": isclose(ASPECT_RATIO, 6.0, rel_tol=5e-3),
        "mission power identity is 109.25 W": isclose(
            electrical_power_limit_w(), 109.25, abs_tol=1e-12),
        "reference BEC efficiency is physical":
            0.0 < REFERENCE_BEC_EFFICIENCY <= 1.0,
        "limit load factors have the declared signs":
            POSITIVE_LIMIT_LOAD_FACTOR > 1.0
            and NEGATIVE_LIMIT_LOAD_FACTOR < 0.0,
        "ultimate structural safety factor is 1.5": isclose(
            ULTIMATE_SAFETY_FACTOR, 1.5, abs_tol=1e-12),
        "V1 allocation mass is clean plus fin cap": isclose(
            ARTICLE_V1_ALLOCATION_MASS_KG,
            ARTICLE_CLEAN_MASS_KG + V1_FIN_MASS_CAP_KG,
            abs_tol=1e-12),
        "V1 analytical mass includes shell, mount and spar": isclose(
            ARTICLE_V1_MASS_KG,
            ARTICLE_CLEAN_MASS_KG + V1_FIN_SHELL_MOUNT_LOWER_KG
            + V1_FIN_SPAR_MASS_KG,
            abs_tol=1e-12),
        "V1 allocation stall rounds to 45.0 km/h": isclose(
            stall_speed(ARTICLE_V1_ALLOCATION_MASS_KG) * 3.6,
            45.0, abs_tol=0.05),
        "C32 analytical V1 currently exceeds the 45 km/h allocation":
            stall_speed(ARTICLE_V1_MASS_KG) * 3.6 > STALL_SPEED_LIMIT_KMH,
    }


def main():
    print("=" * 86)
    print("SALAMANDRA CANONICAL PLANFORM - ADR-0040")
    print("=" * 86)
    print(f"b={B:.3f} m  S={S:.3f} m2  AR={ASPECT_RATIO:.3f}  "
          f"taper={TAPER:.2f}  sweep_c/4={SWEEP_C4_DEG:+.1f} deg")
    print(f"c_root={ROOT_CHORD*1000:.1f} mm  c_tip={TIP_CHORD*1000:.1f} mm  "
          f"MAC={MAC*1000:.1f} mm")
    print("\n y(mm)   c(mm)   t/c(%)   t(mm)   x_LE(mm)   x_c4(mm)   x_TE(mm)")
    for y, c, tc, t, le, c4, te in stations():
        print(f" {y*1000:5.1f}  {c*1000:7.1f}   {tc*100:6.2f}  {t*1000:6.1f}"
              f"   {le*1000:8.1f}   {c4*1000:9.1f}   {te*1000:8.1f}")

    le_sweep = line_sweep_deg(x_le(0.0), x_le(HALF_SPAN))
    te_sweep = line_sweep_deg(x_te(0.0), x_te(HALF_SPAN))
    print(f"\nLE sweep={le_sweep:+.2f} deg  TE sweep={te_sweep:+.2f} deg  "
          f"planform centroid x={planform_centroid()*1000:+.1f} mm")
    print(f"Mission: cruise={CRUISE_SPEED_KMH:.0f} km/h, "
          f"O1={O1_ENERGY_LIMIT_WH_PER_KM:.2f} Wh/km "
          f"({electrical_power_limit_w():.2f} W total battery power), "
          f"V_NE={ARTICLE_V_NE_KMH:.0f} km/h, "
          f"structural case={STRUCTURAL_DESIGN_SPEED_KMH:.0f} km/h")

    checks = validate_geometry()
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
