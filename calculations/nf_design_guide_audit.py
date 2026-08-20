#!/usr/bin/env python3
"""Reproduce the numerical evidence used in the NF Design Guide 2024 audit.

This is an audit harness, not a new aircraft-sizing model.  It imports the released
Salamandra design contract and reports the quantities used to compare Article #1 with
Peter Wick's *Designing Flying Wings* (2024 English PDF).  Inputs retain the project's
normal confidence status: calculations are [D], but model assumptions remain [E]/[I]
until their existing physical closure tests pass.

The source PDF is identified by SHA-256 when it is present.  Its text is not copied or
redistributed by this script.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

import design_config as config
import divergence
import equipment_layout
import yaw_stability


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT / "INSPIRATION" / "NF Design guide 2024 english.pdf"
EXPECTED_SOURCE_SHA256 = (
    "a0e81c98b884c7a9c29f75a9bd7ccdf19ff2255642ba2ac5bdd4337696daabca"
)

# The source recommends a 0.1 %-chord finite trailing edge for XFOIL moment
# screening (PDF pp. 20-22).  Article #1 instead declares a 0.4 mm nozzle and
# 0.45 mm line width; one line width is therefore a transparent first-order
# lower screen for a printable edge, not a released CAD dimension [E].
BOOK_XFOIL_TE_FRACTION = 0.001
PRINT_LINE_WIDTH_M = 0.00045


def read_xfoil_polar(path: Path) -> list[tuple[float, float, float, float]]:
    """Read alpha, CL, CD and CM from one repository XFOIL polar."""
    rows: list[tuple[float, float, float, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) != 7:
            continue
        try:
            alpha, cl, cd, _, cm, _, _ = (float(value) for value in fields)
        except ValueError:
            continue
        rows.append((alpha, cl, cd, cm))
    return rows


def pre_stall_cm0(rows: list[tuple[float, float, float, float]]) -> float:
    """Match the repository's first-branch CM(CL) fit evaluated at CL=0."""
    branch: list[tuple[float, float, float, float]] = []
    for row in rows:
        if row[1] >= 0.6:
            break
        branch.append(row)
    if len(branch) < 3:
        raise ValueError("polar does not contain three pre-stall CL < 0.6 points")
    n = len(branch)
    sx = sum(row[1] for row in branch)
    sy = sum(row[3] for row in branch)
    sxx = sum(row[1] ** 2 for row in branch)
    sxy = sum(row[1] * row[3] for row in branch)
    denominator = n * sxx - sx * sx
    if abs(denominator) < 1e-15:
        raise ValueError("degenerate CM(CL) regression")
    slope = (n * sxy - sx * sy) / denominator
    return (sy - slope * sx) / n


def source_fingerprint(path: Path = DEFAULT_SOURCE) -> tuple[int, str] | None:
    """Return source byte count and SHA-256, or ``None`` when absent."""
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return path.stat().st_size, digest.hexdigest()


def reynolds(speed_kmh: float, reference_length_m: float) -> float:
    """Reynolds number using the repository's declared kinematic viscosity."""
    return config.speed_mps(speed_kmh) * reference_length_m / config.NU_SL


def main() -> None:
    source = source_fingerprint()
    print("NF DESIGN GUIDE 2024 / SALAMANDRA REPOSITORY AUDIT")
    print("=" * 66)
    if source is None:
        print(f"source: MISSING ({DEFAULT_SOURCE})")
    else:
        source_bytes, source_sha256 = source
        source_status = "MATCH" if source_sha256 == EXPECTED_SOURCE_SHA256 else "CHANGED"
        print(f"source: {source_bytes:,} bytes; SHA-256 {source_sha256} [{source_status}]")

    root_chord = config.chord(0.0)
    tip_chord = config.chord(config.HALF_SPAN)
    le_sweep = config.line_sweep_deg(
        config.x_le(0.0), config.x_le(config.HALF_SPAN)
    )
    te_sweep = config.line_sweep_deg(
        config.x_te(0.0), config.x_te(config.HALF_SPAN)
    )

    print("\nPlanform and airfoil operating range [D]")
    print(
        f"  sweep LE / c/4 / TE: {le_sweep:+.3f} / "
        f"{config.SWEEP_C4_DEG:+.3f} / {te_sweep:+.3f} deg"
    )
    print(f"  root / tip chord: {root_chord*1000:.3f} / {tip_chord*1000:.3f} mm")
    for speed in (config.STALL_SPEED_LIMIT_KMH, config.CRUISE_SPEED_KMH):
        print(
            f"  Re at {speed:.0f} km/h, root / tip: "
            f"{reynolds(speed, root_chord):,.0f} / {reynolds(speed, tip_chord):,.0f}"
        )
    print(
        "  one 0.45 mm print line as c fraction, root / tip: "
        f"{100*PRINT_LINE_WIDTH_M/root_chord:.3f} / "
        f"{100*PRINT_LINE_WIDTH_M/tip_chord:.3f} %"
    )
    print(
        "  guide XFOIL finite-edge screen: "
        f"{100*BOOK_XFOIL_TE_FRACTION:.3f} % c"
    )
    sweep_radians = math.radians(abs(config.SWEEP_C4_DEG))
    print(
        "  15 deg section-axis convention sensitivity: "
        f"1-cos(Lambda)={100*(1-math.cos(sweep_radians)):.3f} %, "
        f"sec(Lambda)-1={100*(1/math.cos(sweep_radians)-1):.3f} %"
    )

    print("\nExisting sharp-edge XFOIL CM0 sensitivity [D screen, not [M]]")
    print("  station / condition              Ncrit 10    Ncrit 12      delta")
    polar_cases = (
        (
            "root / Re 240k",
            "salamandra_root_r240k_n10_a010.pol",
            "salamandra_root_r240k_n12_a010.pol",
        ),
        (
            "root / Re 510k",
            "salamandra_root_r510k_n10_a010.pol",
            "salamandra_root_r510k_n12_a010.pol",
        ),
        (
            "tip  / Re 120k",
            "salamandra_tip_r120k_n10_a005.pol",
            "salamandra_tip_r120k_n12_a005.pol",
        ),
        (
            "tip  / Re 255k",
            "salamandra_tip_r255k_n10_a005.pol",
            "salamandra_tip_r255k_n12_a005.pol",
        ),
    )
    polar_directory = REPO_ROOT / "calculations" / "xfoil_out"
    for label, n10_name, n12_name in polar_cases:
        n10 = pre_stall_cm0(read_xfoil_polar(polar_directory / n10_name))
        n12 = pre_stall_cm0(read_xfoil_polar(polar_directory / n12_name))
        print(f"  {label:<27} {n10:+.5f}    {n12:+.5f}    {n12-n10:+.5f}")

    clean, required_pack_x = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("clean")
    )
    cg_sigma = clean.cg_uncertainty_rss_mm()
    reserve_mass_g = sum(
        component.mass_g for component in clean.components if component.reserve
    )
    stall_mass_limit = config.mass_at_stall_speed(
        config.speed_mps(config.STALL_SPEED_LIMIT_KMH)
    )

    print("\nMass, balance and speed margins [D from current [E]/[I] inputs]")
    print(f"  CLEAN solved mass: {clean.mass_g():.2f} g")
    print(f"  CLEAN exact pack station: {required_pack_x:+.2f} mm")
    print(
        f"  longitudinal CG sigma / half-band: {cg_sigma[0]:.2f} / "
        f"{equipment_layout.CG_TOLERANCE_MM:.2f} mm"
    )
    print(f"  unresolved reserve mass in CLEAN layout: {reserve_mass_g:.2f} g")
    print(f"  45 km/h stall-mass ceiling: {stall_mass_limit*1000:.2f} g")
    print(
        "  V1 lower-model / allocated mass margin: "
        f"{1000*(stall_mass_limit-config.ARTICLE_V1_MASS_KG):.2f} / "
        f"{1000*(stall_mass_limit-config.ARTICLE_V1_ALLOCATION_MASS_KG):.2f} g"
    )

    v_div_kmh = divergence.conservative_divergence_speed() * 3.6
    criterion_kmh = 1.5 * config.ARTICLE_V_NE_KMH
    print(f"  conservative V_div: {v_div_kmh:.2f} km/h")
    print(
        f"  V_div / article V_NE / criterion: "
        f"{v_div_kmh/config.ARTICLE_V_NE_KMH:.3f} / "
        f"{v_div_kmh/criterion_kmh:.3f}"
    )
    print(
        f"  calculated/released initial cap: "
        f"{divergence.operational_speed_limit_kmh():.0f} / "
        f"{config.INITIAL_SPEED_LIMIT_KMH:.0f} km/h"
    )

    fin_area = yaw_stability.fin_area_for_target(0.0005)
    fin = yaw_stability.fin_geometry(fin_area)
    cnb_low, cnb_high = yaw_stability.cnb_total_band(fin_area)
    fin_mass_low, fin_mass_high = yaw_stability.fin_mass_band(fin_area)
    fin_delta_cd0, fin_skin_friction = yaw_stability.fin_drag(fin_area)

    print("\nV1 twin-fin low-Re screen [D from current [E] aerodynamic model]")
    print(f"  total area: {fin_area*100:.3f} dm2")
    print(
        f"  one-fin span / root / tip / MAC: {fin.span_m*1000:.1f} / "
        f"{fin.root_chord_m*1000:.1f} / {fin.tip_chord_m*1000:.1f} / "
        f"{fin.mac_m*1000:.1f} mm"
    )
    for speed in (config.STALL_SPEED_LIMIT_KMH, config.CRUISE_SPEED_KMH):
        print(f"  fin Re_MAC at {speed:.0f} km/h: {reynolds(speed, fin.mac_m):,.0f}")
    print(
        "  root / tip relative thickness: "
        f"{100*yaw_stability.FIN_ROOT_THICKNESS_M/fin.root_chord_m:.3f} / "
        f"{100*yaw_stability.FIN_TIP_THICKNESS_M/fin.tip_chord_m:.3f} %"
    )
    print(f"  Cn_beta band: {cnb_low:+.7f} .. {cnb_high:+.7f} /deg")
    print(f"  installed mass band: {fin_mass_low:.2f} .. {fin_mass_high:.2f} g")
    print(f"  estimated Delta CD0: {fin_delta_cd0:.5f}")
    print(f"  estimated local skin-friction coefficient: {fin_skin_friction:.5f}")

    checks = {
        "source fingerprint matches reviewed PDF": (
            source is not None and source[1] == EXPECTED_SOURCE_SHA256
        ),
        "forward-sweep line ordering is explicit": (
            te_sweep < config.SWEEP_C4_DEG < le_sweep < 0.0
        ),
        "V1 lower mass is below the stall ceiling": (
            config.ARTICLE_V1_MASS_KG < stall_mass_limit
        ),
        "CG uncertainty currently exceeds the half-band": (
            cg_sigma[0] > equipment_layout.CG_TOLERANCE_MM
        ),
        "conservative divergence result currently misses criterion": (
            v_div_kmh < criterion_kmh
        ),
        "V1a directional-stability band crosses zero": cnb_low < 0.0 < cnb_high,
    }
    print("\nAudit regression checks")
    for name, passed in checks.items():
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
