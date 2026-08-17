#!/usr/bin/env python3
"""Match the APC 8x8E propeller to Salamandra cruise equilibrium.

The previous baseline placed the propeller at its peak measured efficiency
(J ~= 0.78) without checking whether the resulting thrust equalled aircraft
drag.  This script instead solves the fixed-airspeed operating point from the
O1 electrical-energy ceiling, then checks motor Kv and propeller RPM limits.

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
from dataclasses import dataclass


RHO = 1.225                         # kg/m3, sea-level ISA [E]
DIAMETER = 8.0 * 0.0254             # m [M]
CRUISE_KMH = 95.0                   # O1 design point [D]
O1_WH_PER_KM = 1.15                 # must-have energy ceiling [D]
MOTOR_ESC_EFF = 0.85                # centre of declared 0.80--0.88 band [E]
MOTOR_ESC_EFF_BAND = (0.80, 0.88)
APC_MAX_RPM = 150_000.0 / 8.0       # Thin Electric rule [M]

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
    j, ct, cp, eta_prop = row
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


def main():
    electrical_target = O1_WH_PER_KM * CRUISE_KMH
    point = solve_power(electrical_target)
    band = [solve_power(electrical_target, motor_eff=eff)
            for eff in MOTOR_ESC_EFF_BAND]
    peak_row = max(UIUC_CURVE, key=lambda row: row[3])
    peak = dimensional_point(peak_row)

    print("=" * 79)
    print("SALAMANDRA PROPULSION MATCH - APC E 8x8 measured curve")
    print("=" * 79)
    print(f"O1 at {CRUISE_KMH:.0f} km/h -> electrical target "
          f"{electrical_target:.1f} W")
    print(f"Assumed motor+ESC efficiency: {MOTOR_ESC_EFF:.2f} "
          f"(sensitivity {MOTOR_ESC_EFF_BAND[0]:.2f}--"
          f"{MOTOR_ESC_EFF_BAND[1]:.2f})")
    print("\nEquilibrium operating point")
    print(f"  J={point.j:.3f}; rpm={point.rpm:.0f}; thrust/drag="
          f"{point.thrust_n:.2f} N")
    print(f"  prop eta={point.eta_prop:.3f}; shaft={point.shaft_w:.1f} W; "
          f"electrical={point.electrical_w:.1f} W")
    print(f"  motor-efficiency sensitivity: J={min(p.j for p in band):.3f}--"
          f"{max(p.j for p in band):.3f}, rpm={min(p.rpm for p in band):.0f}--"
          f"{max(p.rpm for p in band):.0f}, thrust="
          f"{min(p.thrust_n for p in band):.2f}--"
          f"{max(p.thrust_n for p in band):.2f} N")

    print("\nWhy peak propeller efficiency is not the design point")
    print(f"  peak measured eta row: J={peak.j:.3f}, rpm={peak.rpm:.0f}, "
          f"thrust={peak.thrust_n:.2f} N, electrical="
          f"{peak.electrical_w:.0f} W")
    print("  This would consume well above O1; throttle/rpm must be set by "
          "aircraft equilibrium.")

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
        "O1 power is reproduced": abs(point.electrical_w - electrical_target) < 0.1,
        "equilibrium is inside measured J range": UIUC_CURVE[0][0] < point.j < UIUC_CURVE[-1][0],
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
    print("\nDECISION: Article #1 is 6S1P with APC E 8x8 and a 500--550 Kv "
          "motor.  A 4S installation is a separate higher-Kv power module. "
          "D2 bench data remain the hardware acceptance gate.")


if __name__ == "__main__":
    main()
