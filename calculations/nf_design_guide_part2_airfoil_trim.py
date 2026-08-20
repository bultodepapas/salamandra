#!/usr/bin/env python3
"""Evidence harness for NF Design Guide audit Part 2: airfoil and pitch trim.

The default run uses only released Salamandra data.  It compares the repository's
pre-stall CM(CL) intercept with the guide's 4.5-degree moment diagnostic, propagates
root/tip moment uncertainty through the current pitch-control model, exposes the
low-speed trim gap, and reports neutral-point/CG/inertia sensitivities.

With ``--xfoil PATH``, the harness additionally runs a non-authoritative XFOIL 6.99
sensitivity at cruise Reynolds numbers for sharp, 0.1 %-chord and one-print-line
trailing edges at Ncrit 6/10/12.  The finite edges are linear wedge perturbations,
not released airfoil geometry.  Every XFOIL result remains [D], never [M].
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
from pathlib import Path
import re
import subprocess
import tempfile

import numpy as np

import aero_contract
from airfoil_reflex_trade import ROOT_CM_WEIGHT, TIP_CM_WEIGHT
from b3_screening import parse_polar
import design_config as config
from elevon_sizing import ARTICLE_1, pitch_result
import equipment_layout
from vlm_ala_volante import geom, solve


REPO_ROOT = Path(__file__).resolve().parent.parent
AIRFOIL_DIRECTORY = REPO_ROOT / "geometry" / "airfoils"
POLAR_DIRECTORY = REPO_ROOT / "calculations" / "xfoil_out"
PRINT_LINE_WIDTH_M = 0.00045
GUIDE_TE_FRACTION = 0.001


@dataclass(frozen=True)
class Endpoint:
    station: str
    reynolds_low: int
    reynolds_high: int
    angle_tag: str
    chord_m: float


ENDPOINTS = (
    Endpoint("root", 240_000, 510_000, "a010", config.ROOT_CHORD),
    Endpoint("tip", 120_000, 255_000, "a005", config.TIP_CHORD),
)


def polar_path(endpoint: Endpoint, reynolds: int, ncrit: int) -> Path:
    return POLAR_DIRECTORY / (
        f"salamandra_{endpoint.station}_r{reynolds//1000}k_"
        f"n{ncrit}_{endpoint.angle_tag}.pol"
    )


def first_pre_stall_branch(
    rows: list[tuple[float, float, float, float]],
) -> list[tuple[float, float, float, float]]:
    """Return the monotonically increasing-CL branch."""
    branch: list[tuple[float, float, float, float]] = []
    last_cl = -math.inf
    for row in rows:
        if row[1] < last_cl:
            break
        branch.append(row)
        last_cl = row[1]
    return branch


def fitted_cm0(rows: list[tuple[float, float, float, float]]) -> float:
    """Match ``b3_screening.summarize``: first consecutive CL < 0.6 points."""
    linear: list[tuple[float, float, float, float]] = []
    for row in rows:
        if row[1] >= 0.6:
            break
        linear.append(row)
    if len(linear) < 3:
        raise ValueError("fewer than three points in the CM(CL) fit")
    n = len(linear)
    sx = sum(row[1] for row in linear)
    sy = sum(row[3] for row in linear)
    sxx = sum(row[1] ** 2 for row in linear)
    sxy = sum(row[1] * row[3] for row in linear)
    denominator = n * sxx - sx * sx
    if abs(denominator) < 1e-15:
        raise ValueError("degenerate CM(CL) fit")
    slope = (n * sxy - sx * sy) / denominator
    return (sy - slope * sx) / n


def interpolate(
    points: list[tuple[float, float]], target: float
) -> tuple[float, bool]:
    """Linearly interpolate, or extrapolate from the nearest two points."""
    ordered = sorted(points)
    outside = target < ordered[0][0] or target > ordered[-1][0]
    if target <= ordered[0][0]:
        first, second = ordered[:2]
    elif target >= ordered[-1][0]:
        first, second = ordered[-2:]
    else:
        for index in range(len(ordered) - 1):
            if ordered[index][0] <= target <= ordered[index + 1][0]:
                first, second = ordered[index : index + 2]
                break
    fraction = (target - first[0]) / (second[0] - first[0])
    return first[1] + fraction * (second[1] - first[1]), outside


def cm_at_alpha(
    rows: list[tuple[float, float, float, float]], alpha_deg: float
) -> float:
    return interpolate([(row[0], row[3]) for row in rows], alpha_deg)[0]


def cm_at_cl(
    rows: list[tuple[float, float, float, float]], cl: float
) -> tuple[float, bool]:
    branch = first_pre_stall_branch(rows)
    return interpolate([(row[1], row[3]) for row in branch], cl)


def endpoint_polars() -> dict[tuple[str, str, int], list[tuple[float, float, float, float]]]:
    polars: dict[
        tuple[str, str, int], list[tuple[float, float, float, float]]
    ] = {}
    for endpoint in ENDPOINTS:
        for condition, reynolds in (
            ("low", endpoint.reynolds_low),
            ("high", endpoint.reynolds_high),
        ):
            for ncrit in (10, 12):
                rows = parse_polar(str(polar_path(endpoint, reynolds, ncrit)))
                if not rows:
                    raise RuntimeError(
                        f"no rows in {polar_path(endpoint, reynolds, ncrit)}"
                    )
                polars[(endpoint.station, condition, ncrit)] = rows
    return polars


def integrated_metric(
    polars: dict[tuple[str, str, int], list[tuple[float, float, float, float]]],
    condition: str,
    ncrit: int,
    metric,
) -> float:
    root = metric(polars[("root", condition, ncrit)])
    tip = metric(polars[("tip", condition, ncrit)])
    return ROOT_CM_WEIGHT * root + TIP_CM_WEIGHT * tip


def local_cl_distribution(speed_kmh: float, ny: int = 160) -> tuple[np.ndarray, ...]:
    """Return |eta|, chord, dy and local CL at the required aircraft CL."""
    required_cl = config.lift_coefficient(
        config.ARTICLE_V1_MASS_KG, config.speed_mps(speed_kmh)
    )
    lattice = geom(
        config.B,
        config.S,
        config.TAPER,
        config.SWEEP_C4_DEG,
        config.DESIGN_TWIST_DEG,
        ny=ny,
        nx=6,
    )
    cl_zero, _, _, _ = solve(lattice, 0.0)
    cl_four, _, _, _ = solve(lattice, 4.0)
    alpha = np.degrees(
        (required_cl - cl_zero) / ((cl_four - cl_zero) / np.radians(4.0))
    )
    _, _, strip_lift, _ = solve(lattice, float(alpha))
    strip_lift = strip_lift.reshape(ny, 6).sum(axis=1)
    dy = lattice["dy"].reshape(ny, 6)[:, 0]
    chord = lattice["chord"].reshape(ny, 6)[:, 0]
    y = lattice["cps"][:, 1].reshape(ny, 6)[:, 0]
    local_cl = strip_lift / (0.5 * chord * dy)
    return np.abs(y) / config.HALF_SPAN, chord, dy, local_cl


def inferred_operating_profile_cm(
    polars: dict[tuple[str, str, int], list[tuple[float, float, float, float]]],
    speed_kmh: float,
    ncrit: int,
) -> tuple[float, float]:
    """First-order endpoint interpolation of CM at the VLM local CL [I].

    This deliberately exposes what the current constant-Cm0 model omits.  It is not
    a replacement model: only endpoint airfoils are available, surface deflection does
    not feed the section polar, and Reynolds interpolation is linear with airspeed.
    The second return is the c-squared weight requiring CL extrapolation.
    """
    eta, chord, dy, local_cl = local_cl_distribution(speed_kmh)
    reynolds_fraction = (speed_kmh - config.STALL_SPEED_LIMIT_KMH) / (
        config.CRUISE_SPEED_KMH - config.STALL_SPEED_LIMIT_KMH
    )
    section_cm: list[float] = []
    extrapolated: list[bool] = []
    for span_fraction, section_cl in zip(eta, local_cl):
        root_low, root_low_ext = cm_at_cl(
            polars[("root", "low", ncrit)], float(section_cl)
        )
        root_high, root_high_ext = cm_at_cl(
            polars[("root", "high", ncrit)], float(section_cl)
        )
        tip_low, tip_low_ext = cm_at_cl(
            polars[("tip", "low", ncrit)], float(section_cl)
        )
        tip_high, tip_high_ext = cm_at_cl(
            polars[("tip", "high", ncrit)], float(section_cl)
        )
        root = root_low + reynolds_fraction * (root_high - root_low)
        tip = tip_low + reynolds_fraction * (tip_high - tip_low)
        section_cm.append((1.0 - span_fraction) * root + span_fraction * tip)
        extrapolated.append(
            root_low_ext or root_high_ext or tip_low_ext or tip_high_ext
        )
    weights = chord**2 * dy / (config.S * config.MAC)
    return (
        float(np.sum(np.asarray(section_cm) * weights)),
        float(np.sum(weights * np.asarray(extrapolated))),
    )


def load_coordinates(path: Path) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 2:
            points.append((float(fields[0]), float(fields[1])))
    if len(points) < 20:
        raise ValueError(f"insufficient airfoil coordinates in {path}")
    return points


def finite_trailing_edge(
    points: list[tuple[float, float]], gap_fraction: float
) -> list[tuple[float, float]]:
    """Open the trailing edge with a symmetric linear wedge about the mean line."""
    if gap_fraction < 0.0:
        raise ValueError("trailing-edge gap must be non-negative")
    leading_index = min(range(len(points)), key=lambda index: points[index][0])
    leading_x = points[leading_index][0]
    trailing_x = 0.5 * (points[0][0] + points[-1][0])
    denominator = trailing_x - leading_x
    modified: list[tuple[float, float]] = []
    for index, (x_value, y_value) in enumerate(points):
        fraction = max(0.0, min(1.0, (x_value - leading_x) / denominator))
        sign = 1.0 if index <= leading_index else -1.0
        modified.append(
            (x_value, y_value + sign * 0.5 * gap_fraction * fraction)
        )
    return modified


def write_coordinates(path: Path, points: list[tuple[float, float]]) -> None:
    lines = [path.stem]
    lines.extend(f"{x_value:.8f} {y_value:.8f}" for x_value, y_value in points)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


XFOIL_RESULT = re.compile(
    r"a =\s*([+-]?\d+(?:\.\d+)?)\s+CL =\s*([+-]?\d+(?:\.\d+)?)"
    r".*?\n\s*Cm =\s*([+-]?\d+(?:\.\d+)?)\s+CD =\s*"
    r"([+-]?\d+(?:\.\d+)?)"
)


def run_xfoil_stdout(
    executable: Path,
    work_directory: Path,
    coordinate_name: str,
    reynolds: int,
    ncrit: int,
) -> list[tuple[float, float, float, float]]:
    angles = [value / 2.0 for value in range(-6, 13)]
    angle_commands = "\n".join(f"ALFA {angle:.1f}" for angle in angles)
    commands = f"""PLOP
G F

LOAD {coordinate_name}
PANE
OPER
VISC {reynolds}
VPAR
N {ncrit}

ITER 250
{angle_commands}
QUIT
"""
    result = subprocess.run(
        [str(executable)],
        input=commands,
        text=True,
        cwd=work_directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60.0,
        check=False,
    )
    latest: dict[float, tuple[float, float, float, float]] = {}
    for alpha, cl, cm, cd in XFOIL_RESULT.findall(result.stdout):
        latest[float(alpha)] = (float(alpha), float(cl), float(cd), float(cm))
    rows = [latest[angle] for angle in angles if angle in latest]
    if len(rows) < 15 or not any(abs(row[0] - 4.5) < 1e-9 for row in rows):
        raise RuntimeError(
            f"XFOIL produced {len(rows)}/19 usable angles for "
            f"{coordinate_name}, Re={reynolds}, Ncrit={ncrit}; exit={result.returncode}"
        )
    return rows


def print_xfoil_sensitivity(executable: Path) -> None:
    if not executable.is_file():
        raise FileNotFoundError(executable)
    print("\nOptional XFOIL moment sensitivity [D], linear-wedge geometry [I]")
    print(
        "  station gap             Ncrit points      fitted CM0     CM at alpha=4.5"
    )
    results: dict[tuple[str, int, str], tuple[float, float]] = {}
    with tempfile.TemporaryDirectory(prefix="sal_nf_part2_") as temporary:
        work_directory = Path(temporary)
        for endpoint in ENDPOINTS:
            source = AIRFOIL_DIRECTORY / f"salamandra-{endpoint.station}-r1.dat"
            original = load_coordinates(source)
            gap_cases = (
                ("sharp", 0.0),
                ("guide 0.1%c", GUIDE_TE_FRACTION),
                ("0.45mm line", PRINT_LINE_WIDTH_M / endpoint.chord_m),
            )
            for gap_label, gap_fraction in gap_cases:
                coordinate_name = f"{endpoint.station}_{gap_label.replace(' ', '_')}.dat"
                write_coordinates(
                    work_directory / coordinate_name,
                    finite_trailing_edge(original, gap_fraction),
                )
                for ncrit in (6, 10, 12):
                    rows = run_xfoil_stdout(
                        executable,
                        work_directory,
                        coordinate_name,
                        endpoint.reynolds_high,
                        ncrit,
                    )
                    print(
                        f"  {endpoint.station:<7} {gap_label:<14} {ncrit:>5} "
                        f"{len(rows):>6}       {fitted_cm0(rows):+10.5f}"
                        f"       {cm_at_alpha(rows, 4.5):+10.5f}"
                    )
                    results[(gap_label, ncrit, endpoint.station)] = (
                        fitted_cm0(rows),
                        cm_at_alpha(rows, 4.5),
                    )
    print("\n  c-squared integrated XFOIL sensitivity")
    print("  gap             Ncrit     fitted CM0     CM at alpha=4.5")
    for gap_label in ("sharp", "guide 0.1%c", "0.45mm line"):
        for ncrit in (6, 10, 12):
            root = results[(gap_label, ncrit, "root")]
            tip = results[(gap_label, ncrit, "tip")]
            integrated_fit = ROOT_CM_WEIGHT * root[0] + TIP_CM_WEIGHT * tip[0]
            integrated_four_five = (
                ROOT_CM_WEIGHT * root[1] + TIP_CM_WEIGHT * tip[1]
            )
            print(
                f"  {gap_label:<15} {ncrit:>5}     {integrated_fit:+10.5f}"
                f"       {integrated_four_five:+10.5f}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--xfoil",
        type=Path,
        help="optional working XFOIL 6.99 executable for finite-edge sensitivity",
    )
    args = parser.parse_args()

    polars = endpoint_polars()
    pitch = pitch_result(ARTICLE_1)
    twist_moment = pitch["wash_in_cm_per_deg"] * config.DESIGN_TWIST_DEG
    elevon_yield = pitch["elevon_cm_per_deg"]

    print("NF DESIGN GUIDE PART 2 - AIRFOIL, TRIM AND LONGITUDINAL AUDIT")
    print("=" * 78)
    print(
        f"c-squared moment weights root/tip: "
        f"{ROOT_CM_WEIGHT:.6f} / {TIP_CM_WEIGHT:.6f}"
    )
    print(
        f"pitch yields: wash-in {pitch['wash_in_cm_per_deg']:+.6f}/deg; "
        f"elevon {elevon_yield:+.6f}/physical deg"
    )
    print(f"three-degree wash-in contribution: {twist_moment:+.6f}")

    print("\nReleased sharp-edge endpoint polar evidence [D]")
    print(
        "  station condition Nc  min CL   fitted CM0   CM@alpha4.5  "
        "CM4.5-CM0"
    )
    for endpoint in ENDPOINTS:
        for condition, reynolds in (
            ("45 km/h", endpoint.reynolds_low),
            ("95 km/h", endpoint.reynolds_high),
        ):
            condition_key = "low" if reynolds == endpoint.reynolds_low else "high"
            for ncrit in (10, 12):
                rows = polars[(endpoint.station, condition_key, ncrit)]
                cm_zero = fitted_cm0(rows)
                cm_four_five = cm_at_alpha(rows, 4.5)
                print(
                    f"  {endpoint.station:<7} {condition:<9} {ncrit:>2} "
                    f"{min(row[1] for row in rows):+7.4f}   {cm_zero:+10.5f}   "
                    f"{cm_four_five:+11.5f}   {cm_four_five-cm_zero:+10.5f}"
                )

    print("\nIntegrated root/tip moment diagnostics [D]")
    print("  condition Nc  fitted CM0   CM at alpha=4.5    difference")
    integrated_cm0: dict[tuple[str, int], float] = {}
    for condition in ("low", "high"):
        for ncrit in (10, 12):
            intercept = integrated_metric(polars, condition, ncrit, fitted_cm0)
            four_five = integrated_metric(
                polars, condition, ncrit, lambda rows: cm_at_alpha(rows, 4.5)
            )
            integrated_cm0[(condition, ncrit)] = intercept
            print(
                f"  {condition:<9} {ncrit:>2}  {intercept:+10.5f}   "
                f"{four_five:+15.5f}   {four_five-intercept:+10.5f}"
            )

    print("\nConstant-fitted-CM trim schedule [D screen; not physical closure]")
    print("  speed       CL   trim N10   trim N12   mechanical +/-20 deg")
    trim_schedule: dict[tuple[float, int], float] = {}
    for speed_kmh in (45.0, 60.0, 75.0, 95.0):
        required_cl = config.lift_coefficient(
            config.ARTICLE_V1_MASS_KG, config.speed_mps(speed_kmh)
        )
        reynolds_fraction = (speed_kmh - config.STALL_SPEED_LIMIT_KMH) / (
            config.CRUISE_SPEED_KMH - config.STALL_SPEED_LIMIT_KMH
        )
        values: list[float] = []
        for ncrit in (10, 12):
            profile_cm = integrated_cm0[("low", ncrit)] + reynolds_fraction * (
                integrated_cm0[("high", ncrit)]
                - integrated_cm0[("low", ncrit)]
            )
            trim = (
                config.STATIC_MARGIN * required_cl - (profile_cm + twist_moment)
            ) / elevon_yield
            trim_schedule[(speed_kmh, ncrit)] = trim
            values.append(trim)
        status = "PASS" if max(abs(value) for value in values) <= 20.0 else "FAIL"
        print(
            f"  {speed_kmh:5.0f}  {required_cl:8.5f}  {values[0]:+9.2f}  "
            f"{values[1]:+9.2f}       {status}"
        )

    print("\nOperating-CM interpolation diagnostic [I; endpoint-only model]")
    print("  speed Nc  profile CM  trim demand  c2-weight extrapolated in CL")
    for speed_kmh in (45.0, 60.0, 75.0, 95.0):
        required_cl = config.lift_coefficient(
            config.ARTICLE_V1_MASS_KG, config.speed_mps(speed_kmh)
        )
        for ncrit in (10, 12):
            profile_cm, extrapolated_weight = inferred_operating_profile_cm(
                polars, speed_kmh, ncrit
            )
            trim = (
                config.STATIC_MARGIN * required_cl - (profile_cm + twist_moment)
            ) / elevon_yield
            print(
                f"  {speed_kmh:5.0f} {ncrit:>2}  {profile_cm:+10.5f}  "
                f"{trim:+10.2f} deg       {100*extrapolated_weight:6.1f} %"
            )

    moment_error = 0.001
    print("\nSensitivity of the released cruise trim point [D]")
    print(
        f"  Delta Cm={moment_error:.4f} -> "
        f"Delta elevon={moment_error/elevon_yield:.3f} deg"
    )
    print(
        f"  Delta Cm={moment_error:.4f} -> "
        f"Delta static margin={100*moment_error/pitch['cruise_cl']:.3f} % MAC "
        f"or Delta CG={1000*config.MAC*moment_error/pitch['cruise_cl']:.3f} mm"
    )

    clean, _ = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("clean")
    )
    v1, _ = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("v1"), clamp=True
    )
    print("\nNeutral-point, CG and pitch-inertia evidence [D from current inputs]")
    method_spread = abs(
        aero_contract.neutral_point_vlm()
        - aero_contract.neutral_point_weissinger()
    )
    cg_sigma = clean.cg_uncertainty_rss_mm()[0]
    print(
        f"  VLM/Weissinger NP spread: {1000*method_spread:.3f} mm = "
        f"{100*method_spread/config.MAC:.3f} % MAC"
    )
    print(
        f"  released CG half-band: {equipment_layout.CG_TOLERANCE_MM:.2f} mm = "
        f"{100*equipment_layout.CG_TOLERANCE_MM/1000/config.MAC:.3f} % MAC"
    )
    print(
        f"  CLEAN one-sigma x-CG uncertainty: {cg_sigma:.3f} mm = "
        f"{100*cg_sigma/1000/config.MAC:.3f} % MAC"
    )
    for label, layout in (("CLEAN", clean), ("V1", v1)):
        mass_kg = layout.mass_g() / 1000.0
        pitch_inertia = layout.inertia_kg_m2()[1][1]
        radius = math.sqrt(pitch_inertia / mass_kg)
        print(
            f"  {label:<5} Iyy={pitch_inertia:.6f} kg m2; "
            f"pitch radius of gyration={radius*1000:.1f} mm"
        )

    checks = {
        "root/tip moment weights sum to one": abs(
            ROOT_CM_WEIGHT + TIP_CM_WEIGHT - 1.0
        ) < 1e-8,
        "stored cruise moments reproduce released constants": (
            abs(integrated_cm0[("high", 10)] - 0.003258) < 1e-5
            and abs(integrated_cm0[("high", 12)] - 0.002095) < 1e-5
        ),
        "released cruise trim remains inside the 0.6-degree CAD screen": (
            abs(trim_schedule[(95.0, 10)]) <= 0.6
            and abs(trim_schedule[(95.0, 12)]) <= 0.6
        ),
        "current constant-CM model exposes low-speed trim non-closure": (
            max(
                abs(trim_schedule[(45.0, 10)]),
                abs(trim_schedule[(45.0, 12)]),
            )
            > 20.0
        ),
        "one-sigma longitudinal CG uncertainty exceeds the released half-band": (
            cg_sigma > equipment_layout.CG_TOLERANCE_MM
        ),
    }
    print("\nAudit regression checks")
    for name, passed in checks.items():
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
    if not all(checks.values()):
        raise SystemExit(1)

    if args.xfoil is not None:
        print_xfoil_sensitivity(args.xfoil.expanduser().resolve())


if __name__ == "__main__":
    main()
