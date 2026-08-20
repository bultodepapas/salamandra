#!/usr/bin/env python3
"""NF Design Guide 2024 audit, Part 6: design-method synthesis.

The final pages of the guide are deliberately exploratory rather than a closed
recipe.  This harness turns their useful questions into auditable Salamandra
diagnostics.  It:

* inventories the released r1 airfoil-coordinate and endpoint-polar evidence;
* exposes chord-normalisation and newline-dependent cache-hash weaknesses;
* brackets the section-coordinate convention on the 15 degree swept wing;
* reconstructs a Fourier span-efficiency diagnostic at five flight states;
* propagates neutral-point and CG tolerances into static margin and trim;
* tests whether neutral or negative static margin is physically reachable with
  the present battery rail; and
* screens elevon chord with the repository's own ideal linear model.

Results marked [I] are audit inferences.  The VLM is rigid, inviscid, symmetric
and attached-flow; the Fourier result is a near-field lifting-line diagnostic,
not a measured drag polar.  Thin-airfoil flap effectiveness is ideal.  Nothing
in this file releases geometry, active stability or a flight-control law.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

import aero_contract
import balance_cg
from b3_screening import load_dat, parse_polar, thickness
import design_config as config
import drag_model
import elevon_sizing
import equipment_layout
from vlm_ala_volante import geom_cached, solve


PDF = config.REPO_ROOT / "INSPIRATION" / "NF Design guide 2024 english.pdf"
EXPECTED_PDF_SHA256 = (
    "a0e81c98b884c7a9c29f75a9bd7ccdf19ff2255642ba2ac5bdd4337696daabca"
)
AIRFOIL_DIRECTORY = config.REPO_ROOT / "geometry" / "airfoils"
POLAR_DIRECTORY = config.REPO_ROOT / "calculations" / "xfoil_out"

SPEEDS_KMH = (45.0, 60.0, 75.0, 95.0, 105.0)
FOURIER_ODD_HARMONICS = tuple(range(1, 22, 2))
FLAP_CHORD_FRACTIONS = (0.15, 0.20, 0.24, 0.28, 0.32, 0.40)


def sha256(path: Path) -> str:
    """Return a streaming SHA-256 fingerprint."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def newline_serialized_sha256(path: Path, newline: bytes) -> str:
    """Hash text after a declared newline serialization.

    Git can convert a tracked text file between CRLF and LF.  This helper does
    not claim either representation is canonical; it demonstrates whether a
    cached byte hash differs only because its newline convention was omitted.
    """
    lines = path.read_bytes().splitlines()
    serialized = newline.join(lines) + newline
    return hashlib.sha256(serialized).hexdigest()


def released_airfoil_files() -> list[Path]:
    """Return the nine controlling r1 station-coordinate files."""
    return sorted(AIRFOIL_DIRECTORY.glob("salamandra-*-r1.dat")) + sorted(
        AIRFOIL_DIRECTORY.glob("salamandra-r1-y*.dat")
    )


def coordinate_metrics(path: Path) -> dict[str, float | int | str]:
    """Geometry and discretisation metrics for one Selig-format contour."""
    points = load_dat(str(path))
    leading_edge = min(points, key=lambda point: point[0])
    mean_trailing_edge = (
        0.5 * (points[0][0] + points[-1][0]),
        0.5 * (points[0][1] + points[-1][1]),
    )
    chord = math.hypot(
        mean_trailing_edge[0] - leading_edge[0],
        mean_trailing_edge[1] - leading_edge[1],
    )
    panel_lengths = [
        math.hypot(second[0] - first[0], second[1] - first[1])
        for first, second in zip(points[:-1], points[1:])
    ]
    nonzero = [length for length in panel_lengths if length > 1e-14]
    return {
        "file": path.name,
        "points": len(points),
        "chord": chord,
        "chord_deficit_fraction": 1.0 - chord,
        "vertical_thickness": thickness(points),
        "actual_vertical_tc": thickness(points) / chord,
        "maximum_panel_fraction": max(nonzero) / chord,
        "minimum_panel_fraction": min(nonzero) / chord,
        "closed_trailing_edge": float(
            math.hypot(
                points[0][0] - points[-1][0],
                points[0][1] - points[-1][1],
            )
        ),
    }


def coordinate_inventory() -> list[dict[str, float | int | str]]:
    return [coordinate_metrics(path) for path in released_airfoil_files()]


def cached_polar_inventory() -> dict[str, object]:
    """Audit endpoint-polar coverage, bounds and geometry-hash portability."""
    metadata_paths = sorted(POLAR_DIRECTORY.glob("salamandra_*.meta.json"))
    rows: list[dict[str, object]] = []
    stations: set[str] = set()
    direct_matches = 0
    crlf_matches = 0
    minimum_alphas: list[float] = []
    maximum_alphas: list[float] = []

    for metadata_path in metadata_paths:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        station = "root" if "_root_" in metadata_path.name else "tip"
        stations.add(station)
        dat_path = AIRFOIL_DIRECTORY / f"salamandra-{station}-r1.dat"
        expected_hash = str(metadata["dat_sha256"])
        direct = sha256(dat_path) == expected_hash
        crlf = newline_serialized_sha256(dat_path, b"\r\n") == expected_hash
        direct_matches += int(direct)
        crlf_matches += int(crlf)

        polar_path = metadata_path.with_suffix("").with_suffix(".pol")
        polar_rows = parse_polar(str(polar_path))
        alphas = [row[0] for row in polar_rows]
        minimum_alphas.append(min(alphas))
        maximum_alphas.append(max(alphas))
        rows.append(
            {
                "station": station,
                "reynolds": int(metadata["reynolds"]),
                "ncrit": int(metadata["ncrit"]),
                "alpha_min": min(alphas),
                "alpha_max": max(alphas),
                "rows": len(polar_rows),
                "direct_hash_match": direct,
                "crlf_hash_match": crlf,
            }
        )

    return {
        "rows": rows,
        "metadata_count": len(metadata_paths),
        "station_count": len(stations),
        "released_station_count": len(released_airfoil_files()),
        "direct_hash_matches": direct_matches,
        "crlf_hash_matches": crlf_matches,
        "minimum_alpha": min(minimum_alphas),
        "maximum_alpha": max(maximum_alphas),
    }


def swept_section_projection() -> dict[str, float]:
    """Cosine bracket for flight-direction versus sweep-normal sections [D]."""
    cosine = math.cos(math.radians(abs(config.SWEEP_C4_DEG)))
    return {
        "cosine": cosine,
        "one_minus_cosine": 1.0 - cosine,
        "secant_minus_one": 1.0 / cosine - 1.0,
        "root_flight_as_normal_tc": config.ROOT_TC / cosine,
        "tip_flight_as_normal_tc": config.TIP_TC / cosine,
        "root_normal_as_flight_tc": config.ROOT_TC * cosine,
        "tip_normal_as_flight_tc": config.TIP_TC * cosine,
    }


def fourier_span_efficiency(
    y: np.ndarray,
    circulation: np.ndarray,
    span: float,
    harmonics: tuple[int, ...] = FOURIER_ODD_HARMONICS,
) -> tuple[float, float]:
    """Infer lifting-line span efficiency from a symmetric circulation shape.

    ``Gamma(theta) = sum(A_n sin(n theta))`` and
    ``e = A_1^2 / sum(n A_n^2)`` for odd harmonics.  Scaling cancels.  The
    returned residual is RMS error normalised by peak absolute circulation.
    """
    theta = np.arccos(np.clip(-2.0 * y / span, -1.0, 1.0))
    harmonic_numbers = np.asarray(harmonics, dtype=float)
    basis = np.sin(np.outer(theta, harmonic_numbers))
    coefficients = np.linalg.lstsq(basis, circulation, rcond=None)[0]
    denominator = float(np.sum(harmonic_numbers * coefficients**2))
    efficiency = float(coefficients[0] ** 2 / denominator)
    reconstructed = basis @ coefficients
    peak = float(np.max(np.abs(circulation)))
    residual = float(np.sqrt(np.mean((reconstructed - circulation) ** 2)) / peak)
    return efficiency, residual


def span_efficiency_state(
    speed_kmh: float,
    *,
    ny: int = 120,
    nx: int = 8,
    twist_deg: float = config.DESIGN_TWIST_DEG,
) -> dict[str, float]:
    """Rigid-VLM Fourier span-efficiency diagnostic at level-flight CL [I]."""
    target_cl = config.lift_coefficient(
        config.ARTICLE_V1_MASS_KG,
        config.speed_mps(speed_kmh),
    )
    lattice = geom_cached(
        config.B,
        config.S,
        config.TAPER,
        config.SWEEP_C4_DEG,
        twist_deg,
        ny=ny,
        nx=nx,
    )
    cl_zero = solve(lattice, 0.0)[0]
    cl_four = solve(lattice, 4.0)[0]
    cl_alpha_per_rad = (cl_four - cl_zero) / math.radians(4.0)
    alpha_deg = math.degrees((target_cl - cl_zero) / cl_alpha_per_rad)
    achieved_cl, _, _, gamma = solve(lattice, alpha_deg)
    strip_gamma = gamma.reshape(ny, nx).sum(axis=1)
    y = lattice["cps"][:, 1].reshape(ny, nx)[:, 0]
    efficiency, residual = fourier_span_efficiency(y, strip_gamma, config.B)
    inferred_to_current_cdi = drag_model.SPAN_EFFICIENCY / efficiency
    return {
        "speed_kmh": speed_kmh,
        "target_cl": target_cl,
        "achieved_cl": float(achieved_cl),
        "alpha_deg": alpha_deg,
        "efficiency": efficiency,
        "fit_residual": residual,
        "inferred_to_current_cdi": inferred_to_current_cdi,
    }


def span_efficiency_sweep(
    ny: int = 120,
    nx: int = 8,
    twist_deg: float = config.DESIGN_TWIST_DEG,
) -> list[dict[str, float]]:
    return [
        span_efficiency_state(
            speed,
            ny=ny,
            nx=nx,
            twist_deg=twist_deg,
        )
        for speed in SPEEDS_KMH
    ]


def static_margin_and_trim() -> dict[str, object]:
    """Propagate present NP methods and CG tolerance through the pitch screen."""
    np_vlm = aero_contract.neutral_point_vlm()
    np_weissinger = aero_contract.neutral_point_weissinger()
    target_cg = balance_cg.cg_target()
    cg_tolerance = balance_cg.R_CG
    implied_margins = [
        (neutral_point - cg) / config.MAC
        for neutral_point in (np_vlm, np_weissinger)
        for cg in (target_cg - cg_tolerance, target_cg + cg_tolerance)
    ]
    pitch = elevon_sizing.pitch_result(elevon_sizing.ARTICLE_1)
    speed_rows = []
    for speed in (45.0, 95.0):
        cl = config.lift_coefficient(
            config.ARTICLE_V1_MASS_KG,
            config.speed_mps(speed),
        )
        trim_per_margin_point = 0.01 * cl / pitch["elevon_cm_per_deg"]
        speed_rows.append(
            {
                "speed_kmh": speed,
                "cl": cl,
                "trim_per_margin_point_deg": trim_per_margin_point,
                "trim_for_cg_tolerance_deg": (
                    trim_per_margin_point * 100.0 * cg_tolerance / config.MAC
                ),
            }
        )
    return {
        "np_vlm_m": np_vlm,
        "np_weissinger_m": np_weissinger,
        "np_spread_m": abs(np_vlm - np_weissinger),
        "target_cg_m": target_cg,
        "cg_tolerance_m": cg_tolerance,
        "cg_tolerance_fraction_mac": cg_tolerance / config.MAC,
        "minimum_implied_margin": min(implied_margins),
        "maximum_implied_margin": max(implied_margins),
        "elevon_cm_per_deg": pitch["elevon_cm_per_deg"],
        "speed_rows": speed_rows,
    }


def active_stability_packaging() -> dict[str, object]:
    """Battery-only reachability of neutral and minus-five-percent margin [D]."""
    solution = equipment_layout.solve_v1_packaging()
    layout = solution.layout
    battery = layout.component(equipment_layout.PRIMARY_CG_ADJUSTER)
    aircraft_mass_g = layout.mass_g()
    present_cg_mm = balance_cg.cg_target() * 1000.0
    neutral_point_mm = aero_contract.neutral_point_vlm() * 1000.0
    cases = []
    for static_margin in (0.0, -0.05):
        target_cg_mm = (
            aero_contract.neutral_point_vlm()
            - static_margin * config.MAC
        ) * 1000.0
        aircraft_cg_shift_mm = target_cg_mm - present_cg_mm
        battery_shift_mm = (
            aircraft_cg_shift_mm * aircraft_mass_g / battery.mass_g
        )
        required_battery_mm = solution.required_battery_x_mm + battery_shift_mm
        cases.append(
            {
                "static_margin": static_margin,
                "target_cg_mm": target_cg_mm,
                "aircraft_cg_shift_mm": aircraft_cg_shift_mm,
                "battery_shift_mm": battery_shift_mm,
                "required_battery_x_mm": required_battery_mm,
                "aft_overrun_mm": max(
                    0.0,
                    required_battery_mm - battery.bounds.maximum_mm[0],
                ),
            }
        )

    available_battery_aft_mm = (
        battery.bounds.maximum_mm[0] - solution.required_battery_x_mm
    )
    available_cg_aft_mm = (
        available_battery_aft_mm * battery.mass_g / aircraft_mass_g
    )
    minimum_reachable_margin = (
        config.STATIC_MARGIN
        - available_cg_aft_mm / (config.MAC * 1000.0)
    )
    return {
        "aircraft_mass_g": aircraft_mass_g,
        "battery_mass_g": battery.mass_g,
        "present_cg_mm": present_cg_mm,
        "neutral_point_mm": neutral_point_mm,
        "battery_x_mm": solution.required_battery_x_mm,
        "battery_min_mm": battery.bounds.minimum_mm[0],
        "battery_max_mm": battery.bounds.maximum_mm[0],
        "available_battery_aft_mm": available_battery_aft_mm,
        "available_cg_aft_mm": available_cg_aft_mm,
        "minimum_reachable_margin": minimum_reachable_margin,
        "cases": cases,
    }


def flap_chord_screen() -> list[dict[str, float]]:
    """Ideal linear screen for a fixed 35--90 percent half-span elevon [I]."""
    rows = []
    for chord_fraction in FLAP_CHORD_FRACTIONS:
        surface = elevon_sizing.ElevonGeometry(
            f"audit c_e/c={chord_fraction:.2f}",
            config.ELEVON_ETA_IN,
            config.ELEVON_ETA_OUT,
            chord_fraction,
        )
        geometry = elevon_sizing.surface_geometry(surface)
        pitch = elevon_sizing.pitch_result(surface)
        roll = elevon_sizing.roll_derivatives(surface)
        rows.append(
            {
                "chord_fraction": chord_fraction,
                "effectiveness": elevon_sizing.thin_airfoil_flap_effectiveness(
                    chord_fraction
                ),
                "area_m2": geometry["area_m2"],
                "hinge_proxy_m3": geometry["hinge_proxy_m3"],
                "cm_per_deg": pitch["elevon_cm_per_deg"],
                "trim_n12_deg": pitch["trim_n12_deg"],
                "roll_derivative_per_rad": roll["cl_delta_a_per_rad"],
            }
        )
    return rows


def main() -> None:
    source_hash = sha256(PDF)
    coordinates = coordinate_inventory()
    endpoints = {
        row["file"]: row
        for row in coordinates
        if row["file"] in {
            "salamandra-root-r1.dat",
            "salamandra-tip-r1.dat",
        }
    }
    polars = cached_polar_inventory()
    projection = swept_section_projection()
    efficiency = span_efficiency_sweep()
    coarse_efficiency = span_efficiency_sweep(ny=80)
    untwisted = span_efficiency_sweep(twist_deg=0.0)
    stability = static_margin_and_trim()
    active = active_stability_packaging()
    flaps = flap_chord_screen()

    root = endpoints["salamandra-root-r1.dat"]
    tip = endpoints["salamandra-tip-r1.dat"]
    maximum_efficiency_mesh_change = max(
        abs(fine["efficiency"] - coarse["efficiency"])
        for fine, coarse in zip(efficiency, coarse_efficiency)
    )

    theta = np.linspace(0.01, math.pi - 0.01, 401)
    synthetic_y = -0.5 * config.B * np.cos(theta)
    synthetic_efficiency, _ = fourier_span_efficiency(
        synthetic_y,
        np.sin(theta),
        config.B,
    )

    print("=" * 94)
    print("NF DESIGN GUIDE PART 6 - DESIGN-METHOD SYNTHESIS")
    print("=" * 94)
    print(f"Source PDF SHA-256: {source_hash}")
    print("Guide scope: PDF pp. 317--331")

    print("\nReleased r1 coordinate inventory [D]")
    print(
        "  station   points  LE--mean-TE chord  deficit   vertical t/c  "
        "max panel"
    )
    for label, row, physical_chord in (
        ("root", root, config.ROOT_CHORD),
        ("tip", tip, config.TIP_CHORD),
    ):
        print(
            f"  {label:7s} {row['points']:6d}       {row['chord']:.8f}  "
            f"{row['chord_deficit_fraction']*100:7.4f}%   "
            f"{row['actual_vertical_tc']*100:9.4f}%  "
            f"{row['maximum_panel_fraction']*100:7.3f}%"
        )
        print(
            f"           dimensional chord deficit = "
            f"{row['chord_deficit_fraction']*physical_chord*1000:.4f} mm"
        )
    print(
        f"  family: {len(coordinates)} station files, "
        f"{min(int(row['points']) for row in coordinates)}.."
        f"{max(int(row['points']) for row in coordinates)} points each"
    )
    print(
        "  The generator rotates LE--mean-TE onto x but omits division by "
        "the computed chord."
    )

    print("\nCached endpoint-polar audit [D]")
    print(
        f"  metadata/polars={polars['metadata_count']}; "
        f"covered released stations={polars['station_count']}/"
        f"{polars['released_station_count']}"
    )
    print(
        f"  byte-exact DAT hash matches={polars['direct_hash_matches']}/"
        f"{polars['metadata_count']}; after declared CRLF serialization="
        f"{polars['crlf_hash_matches']}/{polars['metadata_count']}"
    )
    print(
        f"  alpha coverage={polars['minimum_alpha']:+.1f}.."
        f"{polars['maximum_alpha']:+.1f} deg; no negative-alpha or "
        "deflected-control polars"
    )

    print("\nSwept-section coordinate bracket [D, not an aerodynamic correction]")
    print(
        f"  |sweep c/4|={abs(config.SWEEP_C4_DEG):.1f} deg; "
        f"cos={projection['cosine']:.8f}; projection difference="
        f"{projection['one_minus_cosine']*100:.3f}% / "
        f"{projection['secant_minus_one']*100:.3f}%"
    )
    print(
        "  If current flight-direction t/c is read in the sweep-normal plane: "
        f"root/tip={projection['root_flight_as_normal_tc']*100:.3f}/"
        f"{projection['tip_flight_as_normal_tc']*100:.3f}%"
    )
    print(
        "  If current t/c were designed normal to c/4 and viewed in flight: "
        f"root/tip={projection['root_normal_as_flight_tc']*100:.3f}/"
        f"{projection['tip_normal_as_flight_tc']*100:.3f}%"
    )

    print("\nRigid-VLM Fourier span-efficiency diagnostic [I]")
    print("  speed     CL      alpha    e_Fourier   CDi[I]/CDi[current]  fit RMS")
    for row in efficiency:
        print(
            f"  {row['speed_kmh']:5.0f}  {row['target_cl']:7.4f}  "
            f"{row['alpha_deg']:+7.3f}     {row['efficiency']:.5f}          "
            f"{row['inferred_to_current_cdi']:.4f}        "
            f"{row['fit_residual']*100:.3f}%"
        )
    print(
        f"  e variation with fixed +{config.DESIGN_TWIST_DEG:.1f} deg wash-in: "
        f"{max(row['efficiency'] for row in efficiency)-min(row['efficiency'] for row in efficiency):.5f}"
    )
    print(
        f"  no-twist e range over the same states: "
        f"{min(row['efficiency'] for row in untwisted):.5f}.."
        f"{max(row['efficiency'] for row in untwisted):.5f}"
    )
    print(
        f"  ny=80 to 120 maximum change={maximum_efficiency_mesh_change:.5f}; "
        "no viscous, control-deflection, body or aeroelastic effects"
    )

    print("\nStatic-margin and trim sensitivity [D on linear/inviscid inputs]")
    print(
        f"  MAC={config.MAC*1000:.3f} mm; 1% MAC={config.MAC*10:.3f} mm; "
        f"CG band=+/-{stability['cg_tolerance_m']*1000:.1f} mm = "
        f"+/-{stability['cg_tolerance_fraction_mac']*100:.3f}% MAC"
    )
    print(
        f"  NP VLM/Weissinger={stability['np_vlm_m']*1000:+.3f}/"
        f"{stability['np_weissinger_m']*1000:+.3f} mm; implied rigid SM "
        f"range at the current physical CG band="
        f"{stability['minimum_implied_margin']*100:.3f}.."
        f"{stability['maximum_implied_margin']*100:.3f}% MAC"
    )
    for row in stability["speed_rows"]:
        print(
            f"  {row['speed_kmh']:4.0f} km/h: "
            f"{row['trim_per_margin_point_deg']:.3f} deg elevon per +1% MAC; "
            f"+/-5 mm CG contributes +/-"
            f"{row['trim_for_cg_tolerance_deg']:.3f} deg"
        )

    print("\nBattery-only reachability of active-stability research points [D]")
    print(
        f"  current V1 battery={active['battery_x_mm']:+.3f} mm; travel="
        f"{active['battery_min_mm']:+.3f}..{active['battery_max_mm']:+.3f} mm"
    )
    for case in active["cases"]:
        print(
            f"  SM={case['static_margin']*100:+.0f}%: target CG="
            f"{case['target_cg_mm']:+.3f} mm; aircraft shift="
            f"{case['aircraft_cg_shift_mm']:+.3f} mm; battery="
            f"{case['required_battery_x_mm']:+.3f} mm; aft overrun="
            f"{case['aft_overrun_mm']:.3f} mm"
        )
    print(
        f"  present rail can move CG aft only "
        f"{active['available_cg_aft_mm']:.3f} mm; minimum reachable passive "
        f"margin={active['minimum_reachable_margin']*100:.3f}% MAC"
    )

    print("\nElevon chord screen, eta=0.35..0.90 [I: ideal linear flap]")
    print(
        "   ce/c    tau    area cm2  hinge proxy m3  Cm/deg    "
        "trim N12   Cl_delta/rad"
    )
    for row in flaps:
        marker = "*" if math.isclose(
            row["chord_fraction"], config.ELEVON_CHORD_FRACTION
        ) else " "
        print(
            f" {marker}{row['chord_fraction']:5.2f}  "
            f"{row['effectiveness']:.4f}   {row['area_m2']*1e4:8.2f}  "
            f"{row['hinge_proxy_m3']:.9f}  "
            f"{row['cm_per_deg']:.7f}  {row['trim_n12_deg']:+8.3f}   "
            f"{row['roll_derivative_per_rad']:.5f}"
        )
    flap_low = flaps[0]
    flap_high = flaps[-1]
    print(
        "  15% to 40%: ideal pitch authority +"
        f"{(flap_high['cm_per_deg']/flap_low['cm_per_deg']-1.0)*100:.1f}%; "
        f"area x{flap_high['area_m2']/flap_low['area_m2']:.3f}; hinge proxy "
        f"x{flap_high['hinge_proxy_m3']/flap_low['hinge_proxy_m3']:.3f}"
    )

    selected_flap = next(
        row
        for row in flaps
        if math.isclose(row["chord_fraction"], config.ELEVON_CHORD_FRACTION)
    )
    checks = {
        "reviewed PDF fingerprint matches the controlled source":
            source_hash == EXPECTED_PDF_SHA256,
        "released r1 family has exactly nine station files":
            len(coordinates) == len(config.STATION_Y) == 9,
        "all released station contours contain 61 coordinate points":
            all(row["points"] == 61 for row in coordinates),
        "audit detects the generator's sub-0.1-percent chord-normalisation miss":
            all(0.0 < row["chord_deficit_fraction"] < 0.001 for row in coordinates),
        "all coordinate panels are finite and shorter than 6 percent chord":
            all(0.0 < row["maximum_panel_fraction"] < 0.06 for row in coordinates),
        "all eight endpoint-polar metadata records are present":
            polars["metadata_count"] == 8,
        "raw cached DAT hashes expose newline-dependent non-portability":
            polars["direct_hash_matches"] == 0
            and polars["crlf_hash_matches"] == polars["metadata_count"],
        "polar inventory confirms endpoint-only, non-negative-alpha coverage":
            polars["station_count"] == 2
            and polars["minimum_alpha"] >= 0.0,
        "15-degree section-plane bracket is 3.4--3.6 percent":
            0.034 < projection["secant_minus_one"] < 0.036,
        "Fourier method reproduces an elliptical circulation with e=1":
            abs(synthetic_efficiency - 1.0) < 1e-10,
        "statewise inferred efficiencies remain physical":
            all(0.0 < row["efficiency"] <= 1.0 for row in efficiency),
        "fixed wash-in produces more than 0.20 state variation in inferred e":
            max(row["efficiency"] for row in efficiency)
            - min(row["efficiency"] for row in efficiency) > 0.20,
        "current e=0.85 is within 0.02 of the cruise diagnostic":
            abs(
                next(
                    row["efficiency"]
                    for row in efficiency
                    if row["speed_kmh"] == config.CRUISE_SPEED_KMH
                )
                - drag_model.SPAN_EFFICIENCY
            ) < 0.02,
        "span-efficiency diagnostic changes less than 0.006 from ny=80 to 120":
            maximum_efficiency_mesh_change < 0.006,
        "NP methods plus CG band imply a material 5.7--11.6 percent SM range":
            0.057 < stability["minimum_implied_margin"] < 0.059
            and 0.114 < stability["maximum_implied_margin"] < 0.116,
        "CG tolerance alone exceeds the cruise airfoil-selection trim cap":
            next(
                row["trim_for_cg_tolerance_deg"]
                for row in stability["speed_rows"]
                if row["speed_kmh"] == 95.0
            ) > 0.6,
        "neutral and negative-margin targets lie beyond present battery travel":
            all(case["aft_overrun_mm"] > 0.0 for case in active["cases"]),
        "canonical 28-percent elevon appears exactly in the chord screen":
            math.isclose(
                selected_flap["chord_fraction"],
                config.ELEVON_CHORD_FRACTION,
                abs_tol=1e-12,
            ),
        "15-to-40-percent chord raises hinge proxy by more than sevenfold":
            flap_high["hinge_proxy_m3"] / flap_low["hinge_proxy_m3"] > 7.0,
    }
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print(f"\nVALIDATION: ALL {len(checks)} CHECKS PASS")
    print(
        "DISPOSITION: retain the passive 8% Article #1 target and 28% elevon "
        "provisionally; close coordinate, polar, section-plane, statewise "
        "spanload and dynamic-stability evidence before optimization or flight."
    )


if __name__ == "__main__":
    main()
