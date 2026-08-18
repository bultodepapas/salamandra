#!/usr/bin/env python3
"""Match the APC 8x8E propeller to Salamandra cruise constraints.

The propeller operating point is an equilibrium only when its thrust equals a
measured or modelled aircraft drag.  With no accepted E2 drag polar yet, the O1
energy objective defines a *maximum allowable drag boundary*, not a predicted
equilibrium.  Revision 2 also reserves the avionics/FPV hotel load before
allocating battery power to the motor and ESC.

The embedded curve is the University of Illinois UIUC Propeller Database
wind-tunnel data for APC Thin Electric 8x8, file
``apce_8x8_2813rd_6418.txt`` (6418-rpm test).  Source:
https://m-selig.ae.illinois.edu/props/propDB.html

APC publishes a Thin Electric limit of 150,000 / diameter[in], hence
18,750 rpm for an 8-inch propeller.  Source:
https://www.apcprop.com/wp-content/uploads/2022/03/APC-Propeller-RPM-Limits-rev5.pdf

The measured coefficients are [M].  Scaling them with the standard propeller
relations and interpolating between measured points are [D].  Motor+ESC
efficiency remains [E] until the D2 bench map is measured.
"""
import argparse
from dataclasses import dataclass
from itertools import pairwise

from design_config import (
    ARTICLE_CLEAN_MASS_KG,
    CRUISE_SPEED_KMH,
    G0,
    O1_ENERGY_LIMIT_WH_PER_KM,
    REFERENCE_BEC_EFFICIENCY,
    RHO_SL,
    S,
    dynamic_pressure,
    electrical_power_limit_w,
    speed_mps,
)
from fpv_power_budget import reference_hotel_load_w

RHO = RHO_SL                        # kg/m3, shared design condition
DIAMETER = 8.0 * 0.0254             # m [M]
CRUISE_KMH = CRUISE_SPEED_KMH       # O1 design point [D]
O1_WH_PER_KM = O1_ENERGY_LIMIT_WH_PER_KM
MOTOR_ESC_EFF = 0.85                # centre of declared 0.80--0.88 band [E]
MOTOR_ESC_EFF_BAND = (0.80, 0.88)
APC_MAX_RPM = 150_000.0 / 8.0       # Thin Electric rule [M]
REFERENCE_HOTEL_LOAD_W = reference_hotel_load_w("O4 Lite")

# J, CT, CP, eta -- UIUC APC E 8x8, 6418-rpm wind-tunnel run [M].
UIUC_CURVE = (
    (0.474, 0.1207, 0.0999, 0.573),
    (0.503, 0.1183, 0.0995, 0.598),
    (0.536, 0.1156, 0.0993, 0.624),
    (0.559, 0.1136, 0.0990, 0.642),
    (0.592, 0.1105, 0.0985, 0.664),
    (0.619, 0.1076, 0.0980, 0.680),
    (0.643, 0.1053, 0.0976, 0.694),
    (0.676, 0.1013, 0.0964, 0.710),
    (0.701, 0.0985, 0.0957, 0.722),
    (0.729, 0.0949, 0.0947, 0.731),
    (0.762, 0.0900, 0.0929, 0.739),
    (0.789, 0.0851, 0.0910, 0.739),
    (0.812, 0.0801, 0.0884, 0.736),
    (0.848, 0.0694, 0.0824, 0.714),
    (0.873, 0.0631, 0.0779, 0.708),
    (0.903, 0.0544, 0.0718, 0.685),
    (0.928, 0.0486, 0.0676, 0.667),
    (0.961, 0.0412, 0.0619, 0.640),
    (0.986, 0.0360, 0.0582, 0.610),
    (1.018, 0.0293, 0.0528, 0.564),
    (1.041, 0.0254, 0.0495, 0.534),
    (1.072, 0.0196, 0.0451, 0.465),
    (1.105, 0.0130, 0.0391, 0.367),
    (1.124, 0.0097, 0.0362, 0.300),
)


@dataclass(frozen=True)
class Point:
    j: float
    ct: float
    cp: float
    eta_prop: float
    rpm: float
    thrust_n: float
    shaft_w: float
    electrical_w: float


def dimensional_point(row, speed_kmh=CRUISE_KMH,
                      motor_eff=MOTOR_ESC_EFF):
    """Scale one measured coefficient row to a fixed flight speed."""
    if speed_kmh <= 0.0 or not 0.0 < motor_eff <= 1.0:
        raise ValueError("speed must be positive and motor efficiency in (0, 1]")
    j, ct, cp, _eta_tabulated = row
    if j <= 0.0 or ct <= 0.0 or cp <= 0.0:
        raise ValueError("J, CT and CP must be positive")
    # Recompute eta after interpolation so T*V == eta*Pshaft exactly.  Linear
    # interpolation of the separately rounded UIUC eta column breaks that
    # first-law identity by a small but avoidable amount.
    eta_prop = j * ct / cp
    speed = speed_kmh / 3.6
    rev_s = speed / (j * DIAMETER)
    thrust = ct * RHO * rev_s**2 * DIAMETER**4
    shaft = cp * RHO * rev_s**3 * DIAMETER**5
    return Point(j, ct, cp, eta_prop, rev_s * 60.0, thrust, shaft,
                 shaft / motor_eff)


def lerp(a, b, fraction):
    return a + fraction * (b - a)


def interpolate_point(a, b, fraction, speed_kmh, motor_eff):
    row = tuple(lerp(x, y, fraction) for x, y in zip(a, b))
    return dimensional_point(row, speed_kmh, motor_eff)


def solve_power(electrical_w, speed_kmh=CRUISE_KMH,
                motor_eff=MOTOR_ESC_EFF):
    """Interpolate the measured curve at the requested electrical power."""
    if electrical_w <= 0.0:
        raise ValueError("electrical power must be positive")
    points = [dimensional_point(row, speed_kmh, motor_eff)
              for row in UIUC_CURVE]
    for i in range(len(points) - 1):
        p0, p1 = points[i], points[i + 1]
        if ((p0.electrical_w >= electrical_w >= p1.electrical_w) or
                (p1.electrical_w >= electrical_w >= p0.electrical_w)):
            lo, hi = 0.0, 1.0
            increasing = p1.electrical_w > p0.electrical_w
            for _ in range(60):
                fraction = 0.5 * (lo + hi)
                point = interpolate_point(
                    UIUC_CURVE[i], UIUC_CURVE[i + 1], fraction,
                    speed_kmh, motor_eff)
                if (point.electrical_w < electrical_w) == increasing:
                    lo = fraction
                else:
                    hi = fraction
            return interpolate_point(
                UIUC_CURVE[i], UIUC_CURVE[i + 1], 0.5 * (lo + hi),
                speed_kmh, motor_eff)
    raise ValueError("requested power is outside the measured positive-thrust curve")


def solve_thrust(thrust_n, speed_kmh=CRUISE_KMH,
                 motor_eff=MOTOR_ESC_EFF):
    """Interpolate the measured curve at aircraft drag = propeller thrust."""
    if thrust_n <= 0.0:
        raise ValueError("required thrust must be positive")
    points = [dimensional_point(row, speed_kmh, motor_eff)
              for row in UIUC_CURVE]
    for i, (p0, p1) in enumerate(pairwise(points)):
        if min(p0.thrust_n, p1.thrust_n) <= thrust_n <= max(
                p0.thrust_n, p1.thrust_n):
            lo, hi = 0.0, 1.0
            increasing = p1.thrust_n > p0.thrust_n
            for _ in range(60):
                fraction = 0.5 * (lo + hi)
                point = interpolate_point(
                    UIUC_CURVE[i], UIUC_CURVE[i + 1], fraction,
                    speed_kmh, motor_eff)
                if (point.thrust_n < thrust_n) == increasing:
                    lo = fraction
                else:
                    hi = fraction
            return interpolate_point(
                UIUC_CURVE[i], UIUC_CURVE[i + 1], 0.5 * (lo + hi),
                speed_kmh, motor_eff)
    raise ValueError("requested thrust is outside the measured positive-thrust curve")


def o1_boundary(hotel_load_w=REFERENCE_HOTEL_LOAD_W,
                motor_eff=MOTOR_ESC_EFF):
    """Return the motor operating point at the total O1 battery-power limit."""
    total_limit = electrical_power_limit_w()
    if hotel_load_w < 0.0 or hotel_load_w >= total_limit:
        raise ValueError("hotel load must be non-negative and below O1 power")
    return solve_power(total_limit - hotel_load_w, motor_eff=motor_eff)


def total_energy_wh_per_km(point, hotel_load_w=REFERENCE_HOTEL_LOAD_W):
    """Total battery energy per distance, including the hotel load."""
    if hotel_load_w < 0.0:
        raise ValueError("hotel load cannot be negative")
    return (point.electrical_w + hotel_load_w) / CRUISE_KMH


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--drag-n", type=float,
        help="accepted E2 aircraft drag at 95 km/h; prints its true equilibrium")
    parser.add_argument(
        "--hotel-load-w", type=float, default=REFERENCE_HOTEL_LOAD_W,
        help="continuous avionics plus FPV load (default: Article #1 O4 Lite)")
    args = parser.parse_args()

    electrical_target = electrical_power_limit_w()
    propulsion_target = electrical_target - args.hotel_load_w
    point = o1_boundary(args.hotel_load_w)
    band = [o1_boundary(args.hotel_load_w, motor_eff=eff)
            for eff in MOTOR_ESC_EFF_BAND]
    peak_row = max(UIUC_CURVE, key=lambda row: row[3])
    peak = dimensional_point(peak_row)

    print("=" * 79)
    print("SALAMANDRA PROPULSION MATCH - APC E 8x8 measured curve")
    print("=" * 79)
    print(f"O1 at {CRUISE_KMH:.0f} km/h -> total battery-power limit "
          f"{electrical_target:.2f} W")
    print(f"Hotel load={args.hotel_load_w:.2f} W -> motor+ESC allocation "
          f"{propulsion_target:.2f} W")
    print(f"Assumed motor+ESC efficiency: {MOTOR_ESC_EFF:.2f} "
          f"(sensitivity {MOTOR_ESC_EFF_BAND[0]:.2f}--"
          f"{MOTOR_ESC_EFF_BAND[1]:.2f})")
    q_cruise = dynamic_pressure(speed_mps(CRUISE_KMH))
    cd_allow = point.thrust_n / (q_cruise * S)
    ld_min_clean = ARTICLE_CLEAN_MASS_KG * G0 / point.thrust_n
    print("\nO1 POWER-LIMITED BOUNDARY - not a predicted aircraft equilibrium")
    print(f"  J={point.j:.3f}; rpm={point.rpm:.0f}; maximum allowable drag="
          f"{point.thrust_n:.2f} N")
    print(f"  prop eta={point.eta_prop:.3f}; shaft={point.shaft_w:.1f} W; "
          f"motor electrical={point.electrical_w:.1f} W")
    print(f"  aerodynamic acceptance at 95 km/h: CD <= {cd_allow:.5f}; "
          f"CLEAN L/D >= {ld_min_clean:.2f}")
    print(f"  motor-efficiency sensitivity: J={min(p.j for p in band):.3f}--"
          f"{max(p.j for p in band):.3f}, rpm={min(p.rpm for p in band):.0f}--"
          f"{max(p.rpm for p in band):.0f}, thrust="
          f"{min(p.thrust_n for p in band):.2f}--"
          f"{max(p.thrust_n for p in band):.2f} N")

    if args.drag_n is not None:
        equilibrium = solve_thrust(args.drag_n)
        total_wh_km = total_energy_wh_per_km(equilibrium, args.hotel_load_w)
        print("\nAIRCRAFT EQUILIBRIUM FOR SUPPLIED DRAG")
        print(f"  drag=thrust={equilibrium.thrust_n:.3f} N; J={equilibrium.j:.3f}; "
              f"rpm={equilibrium.rpm:.0f}")
        print(f"  motor electrical={equilibrium.electrical_w:.2f} W; "
              f"total={equilibrium.electrical_w + args.hotel_load_w:.2f} W; "
              f"energy={total_wh_km:.3f} Wh/km")
        print(f"  O1 result: {'PASS' if total_wh_km <= O1_WH_PER_KM else 'FAIL'}")

    print("\nWhy peak propeller efficiency is not the design point")
    print(f"  peak measured eta row: J={peak.j:.3f}, rpm={peak.rpm:.0f}, "
          f"thrust={peak.thrust_n:.2f} N, motor electrical="
          f"{peak.electrical_w:.0f} W")
    print("  The commanded point must instead satisfy measured aircraft drag; "
          "until E2, only the O1 boundary is known.")

    print("\nMotor and propeller checks")
    for cells, volts in ((6, 22.2), (4, 14.8)):
        fractions = [point.rpm / (volts * kv) for kv in (500, 550)]
        print(f"  {cells}S, 500--550 Kv: required rpm is "
              f"{min(fractions)*100:.0f}--{max(fractions)*100:.0f}% of no-load rpm")
    kv_4s_at_80 = point.rpm / (14.8 * 0.80)
    print(f"  4S needs approximately {kv_4s_at_80:.0f} Kv at an 80% loaded/no-load "
          "rpm ratio; it is not the same motor as the 6S reference.")
    print(f"  APC Thin Electric limit={APC_MAX_RPM:.0f} rpm; operating margin="
          f"{APC_MAX_RPM/point.rpm:.2f}x")

    checks = {
        "O1 total power is reproduced after hotel load": abs(
            point.electrical_w + args.hotel_load_w - electrical_target) < 0.1,
        "boundary is inside measured J range": UIUC_CURVE[0][0] < point.j < UIUC_CURVE[-1][0],
        "propeller energy identity T*V = eta*Pshaft": abs(
            point.thrust_n * speed_mps(CRUISE_KMH)
            - point.eta_prop * point.shaft_w) < 1e-9,
        "thrust solver reproduces the boundary point": abs(
            solve_thrust(point.thrust_n).rpm - point.rpm) < 0.1,
        "Article #1 battery hotel load is 14.04 W": (
            args.hotel_load_w != REFERENCE_HOTEL_LOAD_W
            or abs(args.hotel_load_w
                   - 12.6375 / REFERENCE_BEC_EFFICIENCY) < 1e-12),
        "propeller has at least 1.5x RPM margin": APC_MAX_RPM / point.rpm >= 1.5,
        "6S 500--550 Kv has a plausible loaded rpm ratio":
            0.65 <= min(point.rpm / (22.2 * kv) for kv in (500, 550))
            and max(point.rpm / (22.2 * kv) for kv in (500, 550)) <= 0.85,
        "4S 500--550 Kv cannot reach the required rpm unloaded":
            max(14.8 * kv for kv in (500, 550)) < point.rpm,
    }
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nDECISION: Article #1 remains 6S1P with APC E 8x8 and a "
          "500--550 Kv motor. E2 must supply drag before a unique cruise "
          "equilibrium can be claimed; D2 supplies the hardware map.")


if __name__ == "__main__":
    main()
