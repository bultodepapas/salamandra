#!/usr/bin/env python3
"""Measured-data-ready low-speed trim analysis and r2 design screen.

This module replaces the invalid assumption that a cruise ``Cm0`` intercept is
constant from 45 to 105 km/h.  It couples root/mid/tip section polars to the
repository VLM at the operating local lift coefficient and evaluates symmetric
elevon trim over the complete CG band.

Two evidence paths are deliberately separate:

* ``predict`` runs XFOIL on a *sealed-hinge, nominal 0.45 mm trailing-edge*
  proxy.  Those results are computational ``[D]`` on inferred manufacturing
  geometry ``[I]`` and can screen a candidate, never release it.
* ``evaluate`` reads the E2A measured CSV.  Only rows whose ``source`` is
  ``measured`` can pass the measured-trim subgate. The complete physical gate
  also requires the uncertainty, stall, hysteresis and drag dispositions in
  the E2A test record and is never closed by this calculation alone.

Sign convention: positive deflection is trailing-edge DOWN.  This increases
lift on the forward-swept elevon region and is nose-up in the present planform.
The former text calling the positive VLM input "trailing-edge up" was opposite
to the aerodynamic model and is not retained here.

XFOIL is an isolated 2-D-section model.  The VLM is inviscid and rigid.  Hinge
gap leakage, print roughness, separation interaction, aeroelastic twist and the
central body remain physical-test items.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from dataclasses import dataclass
from functools import cache
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Iterable

import numpy as np

import aero_contract
from airfoil_reflex_trade import make_profile
import design_config as config
from vlm_ala_volante import geom_cached, solve


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "trim_redesign_out"
DEFAULT_MEASURED = REPO_ROOT / "tests" / "E2A-printed-section-polars" / "raw" / "section_polars.csv"

SPEEDS_KMH = (45.0, 60.0, 75.0, 95.0, 105.0)
# XFOIL does not consistently converge the low-lift branch of the present
# low-Re section at large TE-up/down deflection. Those mechanical-limit points
# remain mandatory in E2A, but are not invented computationally. A bounded
# control-slope extrapolation is reported as SCREEN and can never close E2A.
PREDICTION_DEFLECTIONS_DEG = {
    45.0: (-5.0, 0.0, 5.0, 10.0),
    60.0: (-5.0, 0.0, 5.0),
    75.0: (-5.0, 0.0, 5.0),
    95.0: (-5.0, 0.0, 5.0),
    105.0: (-5.0, 0.0, 5.0),
}
NCRIT_CASES = (6, 10)
PRINT_LINE_WIDTH_M = 0.00045
CG_HALF_BAND_M = 0.005
MECHANICAL_LIMIT_DEG = 20.0
RELEASE_RESERVE_DEG = 5.0
XFOIL_CACHE_SCHEMA = "xfoil-7-oper-cl-v1"


@dataclass(frozen=True)
class Station:
    name: str
    eta: float

    @property
    def y_m(self) -> float:
        return self.eta * config.HALF_SPAN

    @property
    def chord_m(self) -> float:
        return config.chord(self.y_m)

    @property
    def thickness_ratio(self) -> float:
        return config.thickness_ratio(self.y_m)


STATIONS = (
    Station("root", 0.0),
    Station("mid", 0.5),
    Station("tip", 1.0),
)


@dataclass(frozen=True)
class Candidate:
    name: str
    root_reflex_deg: float
    tip_reflex_deg: float
    twist_deg: float
    target_static_margin: float

    def reflex_at(self, eta: float) -> float:
        return self.root_reflex_deg + eta * (
            self.tip_reflex_deg - self.root_reflex_deg
        )


BASELINE = Candidate("r1-sm8", 1.0, 0.5, 3.0, 0.08)


@dataclass(frozen=True)
class PolarRow:
    alpha_deg: float
    cl: float
    cd: float
    cm_c4: float


@dataclass(frozen=True)
class Polar:
    rows: tuple[PolarRow, ...]

    def attached_rows(self) -> tuple[PolarRow, ...]:
        """Monotonically increasing pre-stall branch, sorted by alpha."""
        ordered = sorted(self.rows, key=lambda row: row.alpha_deg)
        branch: list[PolarRow] = []
        last_cl = -math.inf
        for row in ordered:
            if row.cl <= last_cl + 1e-5:
                if len(branch) >= 5:
                    break
                continue
            branch.append(row)
            last_cl = row.cl
        if len(branch) < 5:
            raise ValueError("polar has fewer than five attached-flow points")
        return tuple(branch)

    def at_cl(self, target_cl: float) -> PolarRow:
        branch = self.attached_rows()
        ordered = sorted(branch, key=lambda row: row.cl)
        if target_cl < ordered[0].cl:
            if ordered[0].cl - target_cl <= 0.10:
                intervals = [(ordered[0], ordered[1])]
            else:
                raise ValueError(
                    f"CL={target_cl:.4f} outside polar coverage "
                    f"{ordered[0].cl:.4f}..{ordered[-1].cl:.4f}"
                )
        elif target_cl > ordered[-1].cl:
            if target_cl - ordered[-1].cl <= 0.05:
                intervals = [(ordered[-2], ordered[-1])]
            else:
                raise ValueError(
                    f"CL={target_cl:.4f} outside polar coverage "
                    f"{ordered[0].cl:.4f}..{ordered[-1].cl:.4f}"
                )
        else:
            intervals = list(zip(ordered, ordered[1:]))
        for first, second in intervals:
            if (
                first.cl <= target_cl <= second.cl
                or target_cl < ordered[0].cl
                or target_cl > ordered[-1].cl
            ):
                fraction = (target_cl - first.cl) / (second.cl - first.cl)
                return PolarRow(
                    alpha_deg=first.alpha_deg
                    + fraction * (second.alpha_deg - first.alpha_deg),
                    cl=target_cl,
                    cd=first.cd + fraction * (second.cd - first.cd),
                    cm_c4=first.cm_c4
                    + fraction * (second.cm_c4 - first.cm_c4),
                )
        if target_cl < ordered[0].cl or target_cl > ordered[-1].cl:
            raise ValueError(
                f"CL={target_cl:.4f} outside polar coverage "
                f"{ordered[0].cl:.4f}..{ordered[-1].cl:.4f}"
            )
        raise AssertionError("interpolation interval not found")

    def zero_lift_alpha_deg(self) -> float:
        branch = self.attached_rows()
        if branch[0].cl <= 0.0 <= branch[-1].cl:
            return self.at_cl(0.0).alpha_deg
        nearest = sorted(branch, key=lambda row: abs(row.cl))[:5]
        if min(abs(row.cl) for row in nearest) > 0.25:
            raise ValueError(
                "zero lift is not bracketed and the nearest converged CL "
                "is farther than 0.25"
            )
        slope, intercept = np.polyfit(
            [row.alpha_deg for row in nearest],
            [row.cl for row in nearest],
            1,
        )
        if abs(slope) < 1e-8:
            raise ValueError("degenerate lift-curve fit around zero lift")
        return float(-intercept / slope)

    @property
    def cl_min(self) -> float:
        return min(row.cl for row in self.attached_rows())

    @property
    def cl_max(self) -> float:
        return max(row.cl for row in self.attached_rows())


def reynolds(station: Station, speed_kmh: float) -> int:
    value = station.chord_m * config.speed_mps(speed_kmh) / config.NU_SL
    return int(round(value / 1000.0) * 1000)


def finite_trailing_edge(
    points: list[tuple[float, float]], gap_fraction: float
) -> list[tuple[float, float]]:
    """Add a symmetric linear TE wedge without changing the mean line."""
    leading_index = min(range(len(points)), key=lambda index: points[index][0])
    leading_x = points[leading_index][0]
    trailing_x = 0.5 * (points[0][0] + points[-1][0])
    chord = trailing_x - leading_x
    output: list[tuple[float, float]] = []
    for index, (x_value, y_value) in enumerate(points):
        fraction = max(0.0, min(1.0, (x_value - leading_x) / chord))
        side = 1.0 if index <= leading_index else -1.0
        output.append(
            (x_value, y_value + side * 0.5 * gap_fraction * fraction)
        )
    return output


def deflect_elevon(
    points: list[tuple[float, float]], deflection_deg: float
) -> list[tuple[float, float]]:
    """Rigidly rotate x/c > hinge; positive is trailing-edge down."""
    hinge_x = config.ELEVON_HINGE_XC
    leading_index = min(range(len(points)), key=lambda index: points[index][0])
    upper = sorted(points[: leading_index + 1], key=lambda pair: pair[0])
    lower = sorted(points[leading_index:], key=lambda pair: pair[0])

    def ordinate(surface: list[tuple[float, float]]) -> float:
        for first, second in zip(surface, surface[1:]):
            if first[0] <= hinge_x <= second[0]:
                fraction = (hinge_x - first[0]) / (second[0] - first[0])
                return first[1] + fraction * (second[1] - first[1])
        raise ValueError("hinge outside coordinate surface")

    hinge_y = 0.5 * (ordinate(upper) + ordinate(lower))
    angle = math.radians(-deflection_deg)
    cosine, sine = math.cos(angle), math.sin(angle)
    output: list[tuple[float, float]] = []
    for x_value, y_value in points:
        if x_value <= hinge_x:
            output.append((x_value, y_value))
            continue
        dx, dy = x_value - hinge_x, y_value - hinge_y
        output.append(
            (
                hinge_x + cosine * dx - sine * dy,
                hinge_y + sine * dx + cosine * dy,
            )
        )
    return output


def candidate_coordinates(
    candidate: Candidate, station: Station, deflection_deg: float
) -> list[tuple[float, float]]:
    points = make_profile(
        station.thickness_ratio, candidate.reflex_at(station.eta)
    )
    points = finite_trailing_edge(
        points, PRINT_LINE_WIDTH_M / station.chord_m
    )
    return deflect_elevon(points, deflection_deg)


def write_coordinates(path: Path, points: Iterable[tuple[float, float]]) -> None:
    lines = [path.stem]
    lines.extend(f"{x_value:.9f} {y_value:.9f}" for x_value, y_value in points)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_xfoil_polar(path: Path) -> Polar:
    rows: list[PolarRow] = []
    if not path.exists():
        return Polar(())
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        fields = line.split()
        if len(fields) < 5:
            continue
        try:
            alpha, cl, cd, _cdp, cm = (float(value) for value in fields[:5])
        except ValueError:
            continue
        rows.append(PolarRow(alpha, cl, cd, cm))
    unique = {round(row.alpha_deg, 6): row for row in rows}
    return Polar(tuple(unique[key] for key in sorted(unique)))


def write_polar_cache(path: Path, polar: Polar) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["alpha_deg,cl,cd,cm_c4"]
    lines.extend(
        f"{row.alpha_deg:.8f},{row.cl:.8f},{row.cd:.8f},{row.cm_c4:.8f}"
        for row in polar.rows
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_polar_cache(path: Path) -> Polar:
    rows: list[PolarRow] = []
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            rows.append(
                PolarRow(
                    float(row["alpha_deg"]),
                    float(row["cl"]),
                    float(row["cd"]),
                    float(row["cm_c4"]),
                )
            )
    polar = Polar(tuple(rows))
    polar.zero_lift_alpha_deg()
    return polar


def _xfoil_version(executable: Path) -> str:
    result = subprocess.run(
        [str(executable)],
        input="QUIT\n",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=5.0,
        check=False,
    )
    for line in result.stdout.splitlines():
        if "XFOIL Version" in line:
            return line.strip()
    raise RuntimeError(f"cannot identify XFOIL at {executable}")


def run_xfoil(
    executable: Path,
    points: list[tuple[float, float]],
    reynolds_number: int,
    ncrit: int,
    deflection_deg: float,
) -> Polar:
    """Run one isolated polar; retain converged rows after a timeout."""
    with tempfile.TemporaryDirectory(prefix="sal_trim_xfoil_") as directory:
        work = Path(directory)
        coordinates = work / "section.dat"
        polar_path = work / "polar.txt"
        write_coordinates(coordinates, points)
        center = -0.64 * deflection_deg
        alpha_up_start = center + 0.5
        alpha_up_end = center + 10.0
        alpha_down_start = center - 0.5
        alpha_down_end = center - 5.0
        commands = (
            "PLOP\nG F\n\n"
            "LOAD section.dat\nPANE\nOPER\n"
            f"VISC {reynolds_number}\nVPAR\nN {ncrit}\n\n"
            "ITER 250\nPACC\npolar.txt\n\n"
            f"ALFA {center:.2f}\n"
            f"ASEQ {alpha_up_start:.2f} {alpha_up_end:.2f} 0.50\n"
            "INIT\n"
            f"ALFA {center:.2f}\n"
            f"ASEQ {alpha_down_start:.2f} {alpha_down_end:.2f} -0.50\n"
            "PACC\n\n\nQUIT\n"
        )
        environment = os.environ.copy()
        environment["GFORTRAN_UNBUFFERED_ALL"] = "1"
        process = subprocess.Popen(
            [str(executable)],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            cwd=work,
            env=environment,
        )
        try:
            process.communicate(commands, timeout=25.0)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2.0)
        polar = parse_xfoil_polar(polar_path)
    if len(polar.rows) < 5:
        raise RuntimeError(
            f"XFOIL returned {len(polar.rows)} points at Re={reynolds_number}, "
            f"Ncrit={ncrit}, delta={deflection_deg:+.1f} deg"
        )
    # These are required by the coupled solver, not cosmetic coverage checks.
    polar.zero_lift_alpha_deg()
    return polar


PolarKey = tuple[str, float, int, float]


def predict_matrix(
    executable: Path,
    candidate: Candidate,
    speeds: Iterable[float] = SPEEDS_KMH,
    deflections: Iterable[float] | None = None,
    ncrit_cases: Iterable[int] = NCRIT_CASES,
    workers: int = 4,
    cache_directory: Path | None = None,
) -> dict[PolarKey, Polar]:
    """Generate exact-speed root/mid/tip XFOIL polars in isolated workers."""
    matrix: dict[PolarKey, Polar] = {}
    executable_digest = hashlib.sha256(executable.read_bytes()).hexdigest()
    jobs: list[
        tuple[
            PolarKey,
            list[tuple[float, float]],
            int,
            int,
            float,
            Path | None,
        ]
    ] = []
    for speed_kmh in speeds:
        speed_deflections = (
            tuple(deflections)
            if deflections is not None
            else PREDICTION_DEFLECTIONS_DEG[speed_kmh]
        )
        for station in STATIONS:
            re_no = reynolds(station, speed_kmh)
            for deflection_deg in speed_deflections:
                points = candidate_coordinates(
                    candidate, station, deflection_deg
                )
                for ncrit in ncrit_cases:
                    key = (station.name, speed_kmh, ncrit, deflection_deg)
                    coordinate_text = "\n".join(
                        f"{x_value:.9f},{y_value:.9f}" for x_value, y_value in points
                    )
                    digest = hashlib.sha256(
                        (
                            f"{XFOIL_CACHE_SCHEMA}|{executable_digest}|"
                            f"{coordinate_text}|{re_no}|{ncrit}|"
                            f"{deflection_deg:.3f}"
                        ).encode("ascii")
                    ).hexdigest()
                    cache_path = (
                        cache_directory / f"{digest}.csv"
                        if cache_directory is not None
                        else None
                    )
                    if cache_path is not None and cache_path.exists():
                        matrix[key] = read_polar_cache(cache_path)
                        continue
                    jobs.append(
                        (key, points, re_no, ncrit, deflection_deg, cache_path)
                    )
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                run_xfoil, executable, points, re_no, ncrit, deflection_deg
            ): (key, re_no, ncrit, deflection_deg)
            for key, points, re_no, ncrit, deflection_deg, _cache_path in jobs
        }
        cache_paths = {
            key: cache_path
            for key, _points, _re_no, _ncrit, _deflection, cache_path in jobs
        }
        errors: list[RuntimeError] = []
        for future in as_completed(futures):
            key, re_no, ncrit, deflection_deg = futures[future]
            try:
                matrix[key] = future.result()
                cache_path = cache_paths[key]
                if cache_path is not None:
                    write_polar_cache(cache_path, matrix[key])
            except Exception as error:
                failure = RuntimeError(
                    f"polar failed for station={key[0]}, speed={key[1]:g} "
                    f"km/h, Re={re_no}, Ncrit={ncrit}, "
                    f"delta={deflection_deg:+g} deg: {error}"
                )
                errors.append(failure)
        if errors:
            raise errors[0]
    return matrix


def write_matrix(
    path: Path,
    matrix: dict[PolarKey, Polar],
    candidate: Candidate,
    source: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=(
                "source",
                "candidate",
                "station",
                "y_mm",
                "chord_mm",
                "reflex_deg",
                "twist_deg",
                "hinge_xc",
                "te_thickness_mm",
                "hinge_gap_mm",
                "speed_kmh",
                "reynolds",
                "ncrit",
                "deflection_deg_te_down_positive",
                "alpha_deg",
                "cl",
                "cd",
                "cm_c4",
            ),
        )
        writer.writeheader()
        stations = {station.name: station for station in STATIONS}
        for key in sorted(matrix):
            station_name, speed_kmh, ncrit, deflection_deg = key
            station = stations[station_name]
            for row in matrix[key].rows:
                writer.writerow(
                    {
                        "source": source,
                        "candidate": candidate.name,
                        "station": station.name,
                        "y_mm": f"{station.y_m * 1000.0:.3f}",
                        "chord_mm": f"{station.chord_m * 1000.0:.3f}",
                        "reflex_deg": f"{candidate.reflex_at(station.eta):.3f}",
                        "twist_deg": f"{candidate.twist_deg:.3f}",
                        "hinge_xc": f"{config.ELEVON_HINGE_XC:.4f}",
                        "te_thickness_mm": f"{PRINT_LINE_WIDTH_M * 1000.0:.3f}",
                        "hinge_gap_mm": "0.000",
                        "speed_kmh": f"{speed_kmh:.1f}",
                        "reynolds": reynolds(station, speed_kmh),
                        "ncrit": ncrit,
                        "deflection_deg_te_down_positive": f"{deflection_deg:.1f}",
                        "alpha_deg": f"{row.alpha_deg:.6f}",
                        "cl": f"{row.cl:.7f}",
                        "cd": f"{row.cd:.7f}",
                        "cm_c4": f"{row.cm_c4:.7f}",
                    }
                )


def read_matrix(path: Path) -> tuple[dict[PolarKey, Polar], set[str]]:
    grouped: dict[PolarKey, list[PolarRow]] = {}
    sources: set[str] = set()
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if not row.get("alpha_deg"):
                continue
            source = row["source"].strip().lower()
            sources.add(source)
            key = (
                row["station"].strip().lower(),
                float(row["speed_kmh"]),
                int(row["ncrit"]),
                float(row["deflection_deg_te_down_positive"]),
            )
            grouped.setdefault(key, []).append(
                PolarRow(
                    float(row["alpha_deg"]),
                    float(row["cl"]),
                    float(row["cd"]),
                    float(row["cm_c4"]),
                )
            )
    return ({key: Polar(tuple(rows)) for key, rows in grouped.items()}, sources)


def _span_overlap(g: dict) -> np.ndarray:
    lower = config.ELEVON_INBOARD_M
    upper = config.ELEVON_OUTBOARD_M
    weights: list[float] = []
    for first, second in g["panels"]:
        y0, y1 = sorted((float(first[1]), float(second[1])))
        overlap = 0.0
        for sign in (-1.0, 1.0):
            band0, band1 = sorted((sign * lower, sign * upper))
            overlap += max(0.0, min(y1, band1) - max(y0, band0))
        weights.append(overlap / (y1 - y0))
    return np.asarray(weights)


def _station_interpolate(values: tuple[float, float, float], eta: float) -> float:
    if eta <= 0.5:
        return values[0] + 2.0 * eta * (values[1] - values[0])
    return values[1] + 2.0 * (eta - 0.5) * (values[2] - values[1])


def coupled_state(
    matrix: dict[PolarKey, Polar],
    candidate: Candidate,
    speed_kmh: float,
    ncrit: int,
    deflection_deg: float,
    static_margin: float,
    ny: int = 80,
    nx: int = 6,
) -> dict[str, float]:
    """Solve CL and moment about the requested CG for one control state."""
    fixed = tuple(
        matrix[(station.name, speed_kmh, ncrit, 0.0)] for station in STATIONS
    )
    moving = tuple(
        matrix[(station.name, speed_kmh, ncrit, deflection_deg)]
        for station in STATIONS
    )
    incidence_nodes = tuple(
        base.zero_lift_alpha_deg() - deflected.zero_lift_alpha_deg()
        for base, deflected in zip(fixed, moving)
    )
    lattice = geom_cached(
        config.B,
        config.S,
        config.TAPER,
        config.SWEEP_C4_DEG,
        0.0,
        ny=ny,
        nx=nx,
    )
    eta_panels = np.abs(lattice["cps"][:, 1]) / config.HALF_SPAN
    coverage_panels = _span_overlap(lattice)
    control_incidence = np.asarray(
        [_station_interpolate(incidence_nodes, eta) for eta in eta_panels]
    )
    lattice["eps"] = np.radians(
        candidate.twist_deg * eta_panels
        + coverage_panels * control_incidence
    )
    target_cl = config.lift_coefficient(
        config.ARTICLE_V1_MASS_KG, config.speed_mps(speed_kmh)
    )
    cl_zero, _, _, _ = solve(lattice, 0.0)
    cl_four, _, _, _ = solve(lattice, 4.0)
    alpha_deg = (target_cl - cl_zero) / ((cl_four - cl_zero) / 4.0)
    wing_cl, wing_cm, panel_lift, _ = solve(lattice, alpha_deg)

    strip_lift = panel_lift.reshape(ny, nx).sum(axis=1)
    strip_dy = lattice["dy"].reshape(ny, nx)[:, 0]
    strip_chord = lattice["chord"].reshape(ny, nx)[:, 0]
    strip_eta = np.abs(lattice["cps"][:, 1].reshape(ny, nx)[:, 0]) / config.HALF_SPAN
    strip_coverage = coverage_panels.reshape(ny, nx).mean(axis=1)
    local_cl = strip_lift / (0.5 * strip_chord * strip_dy)

    profile_cm: list[float] = []
    profile_cd: list[float] = []
    for eta, cl_value, coverage in zip(strip_eta, local_cl, strip_coverage):
        fixed_rows = tuple(polar.at_cl(float(cl_value)) for polar in fixed)
        moving_rows = tuple(polar.at_cl(float(cl_value)) for polar in moving)
        cm_fixed = _station_interpolate(
            tuple(row.cm_c4 for row in fixed_rows), float(eta)
        )
        cm_moving = _station_interpolate(
            tuple(row.cm_c4 for row in moving_rows), float(eta)
        )
        cd_fixed = _station_interpolate(
            tuple(row.cd for row in fixed_rows), float(eta)
        )
        cd_moving = _station_interpolate(
            tuple(row.cd for row in moving_rows), float(eta)
        )
        profile_cm.append(cm_fixed + coverage * (cm_moving - cm_fixed))
        profile_cd.append(cd_fixed + coverage * (cd_moving - cd_fixed))

    moment_weights = strip_chord**2 * strip_dy / (config.S * config.MAC)
    drag_weights = strip_chord * strip_dy / config.S
    section_cm = float(np.sum(moment_weights * np.asarray(profile_cm)))
    section_cd = float(np.sum(drag_weights * np.asarray(profile_cd)))
    x_cg = aero_contract.neutral_point_vlm() - static_margin * config.MAC
    cm_root_c4 = wing_cm + section_cm
    cm_cg = cm_root_c4 + x_cg / config.MAC * wing_cl
    return {
        "alpha_deg": float(alpha_deg),
        "cl": float(wing_cl),
        "cm_cg": float(cm_cg),
        "cm_root_c4": float(cm_root_c4),
        "cm_section": section_cm,
        "cd_profile": section_cd,
        "local_cl_min": float(np.min(local_cl)),
        "local_cl_max": float(np.max(local_cl)),
    }


def interpolate_trim(states: list[tuple[float, dict[str, float]]]) -> dict[str, float]:
    ordered = sorted(states, key=lambda item: item[0])
    for (delta0, state0), (delta1, state1) in zip(ordered, ordered[1:]):
        cm0, cm1 = state0["cm_cg"], state1["cm_cg"]
        if cm0 == 0.0:
            return {"trim_deg": delta0, "control_extrapolated": False, **state0}
        if cm0 * cm1 <= 0.0:
            fraction = -cm0 / (cm1 - cm0)
            result = {
                key: state0[key] + fraction * (state1[key] - state0[key])
                for key in state0
            }
            result["trim_deg"] = delta0 + fraction * (delta1 - delta0)
            result["control_extrapolated"] = False
            return result
    # A boundary extrapolation is useful only as a design screen.  It does not
    # convert a missing deflected polar into evidence: the result is flagged
    # and cannot receive PASS status.
    boundary = min(
        (ordered[:2], ordered[-2:]),
        key=lambda pair: min(abs(item[1]["cm_cg"]) for item in pair),
    )
    (delta0, state0), (delta1, state1) = boundary
    cm0, cm1 = state0["cm_cg"], state1["cm_cg"]
    if abs(cm1 - cm0) < 1e-9:
        raise ValueError("control-moment slope is degenerate")
    fraction = -cm0 / (cm1 - cm0)
    trim_deg = delta0 + fraction * (delta1 - delta0)
    if abs(trim_deg) > MECHANICAL_LIMIT_DEG:
        raise ValueError("extrapolated trim root exceeds the mechanical limit")
    result = {
        key: state0[key] + fraction * (state1[key] - state0[key])
        for key in state0
    }
    result["trim_deg"] = trim_deg
    result["control_extrapolated"] = True
    return result


def evaluate_matrix(
    matrix: dict[PolarKey, Polar], candidate: Candidate
) -> list[dict[str, float | int | str]]:
    results: list[dict[str, float | int | str]] = []
    cg_tolerance_sm = CG_HALF_BAND_M / config.MAC
    margins = (
        ("aft", candidate.target_static_margin - cg_tolerance_sm),
        ("nominal", candidate.target_static_margin),
        ("forward", candidate.target_static_margin + cg_tolerance_sm),
    )
    available_speeds = sorted({key[1] for key in matrix})
    available_ncrit = sorted({key[2] for key in matrix})
    for speed_kmh in available_speeds:
        for ncrit in available_ncrit:
            station_deflections = [
                {
                    key[3]
                    for key in matrix
                    if key[0] == station.name
                    and key[1] == speed_kmh
                    and key[2] == ncrit
                }
                for station in STATIONS
            ]
            available_deflections = sorted(
                set.intersection(*station_deflections)
            )
            for cg_case, static_margin in margins:
                states: list[tuple[float, dict[str, float]]] = []
                for deflection_deg in available_deflections:
                    states.append(
                        (
                            deflection_deg,
                            coupled_state(
                                matrix,
                                candidate,
                                speed_kmh,
                                ncrit,
                                deflection_deg,
                                static_margin,
                            ),
                        )
                    )
                try:
                    trim = interpolate_trim(states)
                    if (
                        not trim["control_extrapolated"]
                        and abs(trim["trim_deg"])
                        <= MECHANICAL_LIMIT_DEG - RELEASE_RESERVE_DEG
                    ):
                        status = "PASS"
                    else:
                        status = "SCREEN"
                except ValueError:
                    trim = {
                        "trim_deg": math.nan,
                        "control_extrapolated": False,
                        "alpha_deg": math.nan,
                        "cl": config.lift_coefficient(
                            config.ARTICLE_V1_MASS_KG,
                            config.speed_mps(speed_kmh),
                        ),
                        "cm_cg": math.nan,
                        "cm_root_c4": math.nan,
                        "cm_section": math.nan,
                        "cd_profile": math.nan,
                        "local_cl_min": math.nan,
                        "local_cl_max": math.nan,
                    }
                    status = "FAIL"
                results.append(
                    {
                        "speed_kmh": speed_kmh,
                        "ncrit": ncrit,
                        "cg_case": cg_case,
                        "static_margin_percent": 100.0 * static_margin,
                        **trim,
                        "status": status,
                    }
                )
    return results


def write_results(path: Path, results: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(results[0]))
        writer.writeheader()
        writer.writerows(results)


def summary(results: list[dict[str, object]]) -> dict[str, object]:
    finite = [row for row in results if math.isfinite(float(row["trim_deg"]))]
    passed = [row for row in results if row["status"] == "PASS"]
    limiting = max(finite, key=lambda row: abs(float(row["trim_deg"])))
    return {
        "case_count": len(results),
        "pass_count": len(passed),
        "all_pass": len(passed) == len(results),
        "mechanical_screen_pass": not any(
            row["status"] == "FAIL" for row in results
        ),
        "maximum_absolute_trim_deg": abs(float(limiting["trim_deg"])),
        "limiting_case": limiting,
    }


def _candidate_from_args(args: argparse.Namespace) -> Candidate:
    return Candidate(
        args.name,
        args.root_reflex,
        args.tip_reflex,
        args.twist,
        args.static_margin / 100.0,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("predict", "evaluate"))
    parser.add_argument("--xfoil", type=Path)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--name", default="candidate")
    parser.add_argument("--root-reflex", type=float, default=1.0)
    parser.add_argument("--tip-reflex", type=float, default=0.5)
    parser.add_argument("--twist", type=float, default=3.0)
    parser.add_argument("--static-margin", type=float, default=8.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="evaluate 45/95/105 km/h instead of the five-speed ladder",
    )
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least one")
    candidate = _candidate_from_args(args)
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    if args.mode == "predict":
        if args.xfoil is None:
            parser.error("predict requires --xfoil")
        executable = args.xfoil.expanduser().resolve()
        version = _xfoil_version(executable)
        speeds = (45.0, 95.0, 105.0) if args.quick else SPEEDS_KMH
        ncrit_cases = NCRIT_CASES
        matrix = predict_matrix(
            executable,
            candidate,
            speeds,
            None,
            ncrit_cases,
            workers=args.workers,
            cache_directory=output / ".xfoil-cache",
        )
        matrix_path = output / f"{candidate.name}-xfoil-matrix.csv"
        write_matrix(matrix_path, matrix, candidate, "xfoil")
        metadata = {
            "candidate": candidate.__dict__,
            "xfoil": version,
            "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
            "evidence": "[D] on sealed-hinge finite-TE [I] geometry; not measured",
            "matrix": str(matrix_path.relative_to(REPO_ROOT)),
        }
        (output / f"{candidate.name}-metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        input_path = (
            args.input.expanduser().resolve()
            if args.input is not None
            else DEFAULT_MEASURED
        )
        matrix, sources = read_matrix(input_path)
        if not matrix:
            raise SystemExit(
                f"no polar rows in {input_path}; E2A physical measurements remain open"
            )

    results = evaluate_matrix(matrix, candidate)
    results_path = output / f"{candidate.name}-trim-results.csv"
    write_results(results_path, results)
    disposition = summary(results)
    disposition["sources"] = sorted(sources) if args.mode == "evaluate" else ["xfoil"]
    disposition["measured_trim_subgate_pass"] = (
        args.mode == "evaluate"
        and sources == {"measured"}
        and disposition["all_pass"]
    )
    disposition["physical_gate_closed"] = False
    disposition["physical_gate_reason"] = (
        "E2A requires separate uncertainty, CLmax/stall-order, hinge-hysteresis "
        "and O1 drag dispositions; this solver evaluates the trim subgate only"
    )
    summary_path = output / f"{candidate.name}-summary.json"
    summary_path.write_text(
        json.dumps(disposition, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(disposition, indent=2, sort_keys=True))
    print(f"matrix/results: {output}")
    if args.mode == "evaluate" and not disposition["measured_trim_subgate_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
