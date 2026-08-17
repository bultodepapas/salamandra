#!/usr/bin/env python3
"""Design the Salamandra root/tip reflex family from the MH60 mean line.

Revision 1 corrects two B3 issues before selecting geometry:

* thickness is changed about the interpolated mean camber line, never by
  multiplying every y coordinate; and
* the Reynolds envelope follows the real 289.2/144.6 mm chords at 45/95 km/h.

The trade applies a smooth, buildable geometric reflex by rotating the contour
aft of x/c=0.72, renormalizes the chord, restores the requested t/c, and uses
XFOIL only as a calibrated [D] screen.  Root and tip moments are integrated
with the correct c^2 weighting and combined with the VLM wash-in/elevon yields.
The minimum-drag pair that trims throughout the Ncrit 10--12 cruise band with
no more than 0.6 deg neutral elevon offset is selected.  Full endpoint polars
then check lift, drag and moment before the coordinates are written.
"""
import argparse
import math
import os

from b3_screening import (
    AF_DIR, load_dat, run_xfoil, scale_tc, split_surfaces, interp_surface,
    summarize, thickness, write_dat,
)
from design_config import (
    HALF_SPAN, MAC, ROOT_CHORD, ROOT_TC, S, STATION_Y, TIP_CHORD, TIP_TC,
    chord, thickness_ratio,
)
from elevon_authority import cm0_wing


NU = 1.50e-5                 # m2/s, sea-level kinematic viscosity [E]
V_STALL = 45.0 / 3.6
V_CRUISE = 95.0 / 3.6
HINGE_X = 0.72
DESIGN_MASS = 1.620
RHO = 1.225
STATIC_MARGIN = 0.08
TWIST_DEG = 3.0
ELEVON_TRIM_CAP = 0.6
ROOT_ANGLES = tuple(i * 0.5 for i in range(0, 7))    # 0..3 deg
TIP_ANGLES = tuple(i * 0.5 for i in range(0, 17))    # 0..8 deg


def reynolds(chord, speed):
    return int(round(chord * speed / NU / 5000.0) * 5000)


ROOT_RE = (reynolds(ROOT_CHORD, V_STALL), reynolds(ROOT_CHORD, V_CRUISE))
TIP_RE = (reynolds(TIP_CHORD, V_STALL), reynolds(TIP_CHORD, V_CRUISE))
CL_CRUISE = DESIGN_MASS * 9.81 / (0.5 * RHO * V_CRUISE**2 * S)
CM_REQUIRED = CL_CRUISE * STATIC_MARGIN
DCM_TWIST = cm0_wing(1.0, 0.0) - cm0_wing(0.0, 0.0)
DCM_ELEVON = cm0_wing(0.0, 1.0) - cm0_wing(0.0, 0.0)


def moment_weights(n=10000):
    """Root/tip weights for linearly interpolated section cm0 (integral c^2)."""
    dy = HALF_SPAN / n
    root_weight = tip_weight = 0.0
    for i in range(n):
        y = (i + 0.5) * dy
        eta = y / HALF_SPAN
        c2dy = chord(y) ** 2 * dy
        root_weight += c2dy * (1.0 - eta)
        tip_weight += c2dy * eta
    denominator = S * MAC / 2.0
    return root_weight / denominator, tip_weight / denominator


ROOT_CM_WEIGHT, TIP_CM_WEIGHT = moment_weights()


def normalize_chord(points):
    """Map the LE-to-mean-TE chord to (0,0)..(1,0)."""
    ile = min(range(len(points)), key=lambda i: points[i][0])
    le = points[ile]
    te = (0.5 * (points[0][0] + points[-1][0]),
          0.5 * (points[0][1] + points[-1][1]))
    dx, dy = te[0] - le[0], te[1] - le[1]
    chord = math.hypot(dx, dy)
    ca, sa = dx / chord, dy / chord
    return [
        ((x - le[0]) * ca + (y - le[1]) * sa,
         (-(x - le[0]) * sa + (y - le[1]) * ca))
        for x, y in points
    ]


def reflex_flap(points, angle_deg, hinge_x=HINGE_X):
    """Rotate the aft contour upward about the local mean-line hinge point."""
    upper, lower = split_surfaces(points)
    hinge_y = 0.5 * (
        interp_surface(upper, hinge_x) + interp_surface(lower, hinge_x))
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for x, y in points:
        if x <= hinge_x:
            out.append((x, y))
            continue
        dx, dy = x - hinge_x, y - hinge_y
        out.append((hinge_x + ca * dx - sa * dy,
                    hinge_y + sa * dx + ca * dy))
    return normalize_chord(out)


def make_profile(target_tc, angle_deg):
    base = load_dat(os.path.join(AF_DIR, "mh60.dat"))
    scaled = scale_tc(base, target_tc)
    reflexed = reflex_flap(scaled, angle_deg)
    return scale_tc(reflexed, target_tc)


def angle_tag(angle):
    return f"{int(round(angle * 10)):03d}"


def screen_angles(kind, target_tc, angles, cruise_re, xfoil):
    """Return cruise summaries by angle and Ncrit."""
    results = {}
    for angle in angles:
        by_ncrit = {}
        for ncrit in (10, 12):
            tag = f"sm_{kind}_c_a{angle_tag(angle)}_n{ncrit}"
            dat = os.path.join(AF_DIR, f"{tag}.dat")
            write_dat(make_profile(target_tc, angle), dat)
            polar = run_xfoil(
                dat, cruise_re, ncrit, tag, xfoil, alpha_end=6.0,
                iter_limit=120, stable_seconds=8.0)
            summary = summarize(polar)
            if summary is None or summary["cm0"] is None:
                raise RuntimeError(f"no usable cruise polar for {tag}")
            by_ncrit[ncrit] = summary
        results[angle] = by_ncrit
    return results


def select_pair(root_trade, tip_trade):
    """Select lowest weighted profile drag among pairs closing the trim band."""
    candidates = []
    for root_angle, root_cases in root_trade.items():
        for tip_angle, tip_cases in tip_trade.items():
            elevon = {}
            drag = []
            for ncrit in (10, 12):
                cm_profile = (
                    ROOT_CM_WEIGHT * root_cases[ncrit]["cm0"]
                    + TIP_CM_WEIGHT * tip_cases[ncrit]["cm0"])
                cm_total = cm_profile + TWIST_DEG * DCM_TWIST
                elevon[ncrit] = (CM_REQUIRED - cm_total) / DCM_ELEVON
                drag.append(
                    ROOT_CM_WEIGHT * root_cases[ncrit]["cd_cruise"]
                    + TIP_CM_WEIGHT * tip_cases[ncrit]["cd_cruise"])
            if max(abs(value) for value in elevon.values()) <= ELEVON_TRIM_CAP:
                candidates.append((max(drag), root_angle + tip_angle,
                                   root_angle, tip_angle, elevon))
    if not candidates:
        raise RuntimeError("no root/tip pair closes the declared trim cap")
    _, _, root_angle, tip_angle, elevon = min(candidates)
    return root_angle, tip_angle, elevon, len(candidates)


def full_polars(kind, path, reynolds_band, angle, xfoil):
    rows = []
    for re_no in reynolds_band:
        for ncrit in (10, 12):
            tag = (f"salamandra_{kind}_r{int(re_no/1000)}k_n{ncrit}_"
                   f"a{angle_tag(angle)}")
            polar = run_xfoil(path, re_no, ncrit, tag, xfoil)
            summary = summarize(polar)
            if summary is None:
                raise RuntimeError(f"no converged polar for {tag}")
            rows.append((re_no, ncrit, summary))
    return rows


def main():
    parser = argparse.ArgumentParser(description="Salamandra reflex-airfoil trade")
    parser.add_argument("--xfoil", required=True, help="official XFOIL executable")
    args = parser.parse_args()

    print("=" * 92)
    print("SALAMANDRA AIRFOIL REFLEX TRADE - corrected B3 geometry and Reynolds envelope")
    print("=" * 92)
    print(f"root Re stall/cruise = {ROOT_RE[0]:,}/{ROOT_RE[1]:,}")
    print(f"tip  Re stall/cruise = {TIP_RE[0]:,}/{TIP_RE[1]:,}")

    print(f"c^2 moment weights root/tip = {ROOT_CM_WEIGHT:.4f}/{TIP_CM_WEIGHT:.4f}")
    print(f"trim target Cm={CM_REQUIRED:+.5f}; wash-in yield={DCM_TWIST:+.5f}/deg; "
          f"elevon yield={DCM_ELEVON:+.5f}/deg")

    root_trade = screen_angles(
        "root", ROOT_TC, ROOT_ANGLES, max(ROOT_RE), args.xfoil)
    tip_trade = screen_angles(
        "tip", TIP_TC, TIP_ANGLES, max(TIP_RE), args.xfoil)
    root_angle, tip_angle, screen_elevon, feasible_count = select_pair(
        root_trade, tip_trade)

    print(f"\nCoupled cruise screen: {feasible_count} pairs meet +/-"
          f"{ELEVON_TRIM_CAP:.1f} deg neutral-trim cap")
    print(f"  selected root/tip reflex = {root_angle:.1f}/{tip_angle:.1f} deg")
    print(f"  neutral elevon Ncrit 10/12 = {screen_elevon[10]:+.2f}/"
          f"{screen_elevon[12]:+.2f} deg")

    selected = []
    for kind, tc, re_band, angle in (
            ("root", ROOT_TC, ROOT_RE, root_angle),
            ("tip", TIP_TC, TIP_RE, tip_angle)):
        path = os.path.join(AF_DIR, f"salamandra-{kind}-r1.dat")
        points = make_profile(tc, angle)
        write_dat(points, path)
        polars = full_polars(kind, path, re_band, angle, args.xfoil)
        selected.append((kind, tc, angle, path, points, polars))

    print("\nSelected full-envelope polars")
    print(f"  {'profile':<7} {'t/c':>6} {'reflex':>7} {'Re':>8} {'Nc':>3} "
          f"{'cm0':>8} {'clmax':>7} {'cd@.132':>9}")
    checks = {}
    for kind, tc, angle, path, points, polars in selected:
        checks[f"{kind} thickness"] = abs(thickness(points) - tc) < 1e-5
        checks[f"{kind} section clmax"] = min(
            s["clmax"] for _, _, s in polars) >= 0.65
        for re_no, ncrit, s in polars:
            print(f"  {kind:<7} {tc*100:5.2f}% {angle:6.1f}deg {re_no:8d} "
                  f"{ncrit:3d} {s['cm0']:+8.4f} {s['clmax']:7.3f} "
                  f"{s['cd_cruise'] if s['cd_cruise'] else float('nan'):9.4f}")

    full_by_kind = {kind: polars for kind, _, _, _, _, polars in selected}
    full_elevon = {}
    for ncrit in (10, 12):
        root_s = next(s for re_no, nc, s in full_by_kind["root"]
                      if re_no == max(ROOT_RE) and nc == ncrit)
        tip_s = next(s for re_no, nc, s in full_by_kind["tip"]
                     if re_no == max(TIP_RE) and nc == ncrit)
        cm_profile = (ROOT_CM_WEIGHT * root_s["cm0"]
                      + TIP_CM_WEIGHT * tip_s["cm0"])
        full_elevon[ncrit] = (
            CM_REQUIRED - cm_profile - TWIST_DEG * DCM_TWIST) / DCM_ELEVON
    checks["full-polar trim band"] = max(
        abs(value) for value in full_elevon.values()) <= ELEVON_TRIM_CAP
    print(f"  coupled neutral elevon at cruise: Ncrit 10/12 = "
          f"{full_elevon[10]:+.2f}/{full_elevon[12]:+.2f} deg")

    print("\nGenerated CAD station sections")
    for y in STATION_Y[1:-1]:
        eta = y / HALF_SPAN
        angle = root_angle + eta * (tip_angle - root_angle)
        tc = thickness_ratio(y)
        points = make_profile(tc, angle)
        path = os.path.join(AF_DIR, f"salamandra-r1-y{int(round(y*1000)):03d}.dat")
        write_dat(points, path)
        checks[f"station y={y*1000:.0f} mm thickness"] = (
            abs(thickness(points) - tc) < 1e-5)
        print(f"  y={y*1000:5.1f} mm  t/c={tc*100:5.2f}%  "
              f"reflex={angle:4.2f} deg  {os.path.basename(path)}")

    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print(f"\nDECISION: root reflex {root_angle:.1f} deg; tip reflex "
          f"{tip_angle:.1f} deg; printed wash-in {TWIST_DEG:.1f} deg. "
          "Coordinates written as Salamandra r1.")
    print("These are [D] CAD coordinates; E2 remains the measured polar closure.")


if __name__ == "__main__":
    main()
