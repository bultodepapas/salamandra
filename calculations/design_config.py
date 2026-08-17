#!/usr/bin/env python3
"""Canonical Salamandra Article #1 planform geometry.

This module is the single numerical source for the planform used by the analysis
scripts and by the CAD station table.  Run it directly after any planform change;
all invariant checks must pass before the Design Guide or CAD is released.

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

HALF_SPAN = B / 2.0
ROOT_CHORD = 2.0 * S / (B * (1.0 + TAPER))
TIP_CHORD = TAPER * ROOT_CHORD
MAC = (2.0 / 3.0) * ROOT_CHORD * (1.0 + TAPER + TAPER**2) / (1.0 + TAPER)
Y_MAC = (B / 6.0) * (1.0 + 2.0 * TAPER) / (1.0 + TAPER)
ASPECT_RATIO = B**2 / S

STATION_Y = (0.000, 0.130, 0.195, 0.325, 0.347, 0.4875, 0.498, 0.585, 0.650)


def chord(y):
    """Local chord [m] for |y| in [0, b/2]."""
    eta = abs(y) / HALF_SPAN
    return ROOT_CHORD * (1.0 - (1.0 - TAPER) * eta)


def thickness_ratio(y):
    """Linear relative-thickness schedule."""
    eta = abs(y) / HALF_SPAN
    return ROOT_TC + (TIP_TC - ROOT_TC) * eta


def x_c4(y, sweep_deg=SWEEP_C4_DEG):
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

    checks = validate_geometry()
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
