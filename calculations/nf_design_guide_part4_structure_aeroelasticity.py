#!/usr/bin/env python3
"""NF Design Guide 2024 audit, Part 4: structure and aeroelastic release.

This is an audit calculation, not a structural substantiation of Salamandra.  It
connects the repository's current VLM, mass/load contract and divergence model to
the structural lessons in Peter Wick's *Designing Flying Wings* (2024 English
edition).  In particular it:

* converts the +6 g/+9 g aircraft resultants into aerodynamic-only semispan load,
  bending-moment and elastic-axis torque screens;
* compares those screens with the current CORE--PANEL torque band and carbon tube;
* corrects the shear-plane interpretation used by the filament-dowel screen;
* quantifies divergence clearance, Southwell schedule and stiffness sensitivities;
* exposes the inertia cost of static elevon balance; and
* inventories the forcing frequencies and manufacturing-authority gap.

The span loads exclude inertia relief, control-load movement, cut-outs, local load
introduction and nonlinear stall.  They are therefore load-path diagnostics [I],
not proof loads.  No result from this script authorizes manufacture or flight.
"""

from __future__ import annotations

import hashlib
import math
import sys
from pathlib import Path

import numpy as np

import design_config as config
import divergence
import filament_dowel_pins
import joint_pin_trade
import propulsion_match
from vlm_ala_volante import geom, solve


PDF = config.REPO_ROOT / "INSPIRATION" / "NF Design guide 2024 english.pdf"
EXPECTED_PDF_SHA256 = (
    "a0e81c98b884c7a9c29f75a9bd7ccdf19ff2255642ba2ac5bdd4337696daabca"
)

# Structural-screen assumptions.  These are explicit because the repository has
# no released as-built spanwise mass model or wing finite-element model.
EA_CONSERVATIVE_XC = 0.45
AC_XC = 0.25
EA_ARM_FRACTION = EA_CONSERVATIVE_XC - AC_XC
JOINT_STATIONS_M = (0.195, 0.347, 0.498)

# Main bending tube from ADR-0031.  Stress is a section-demand screen only: no
# laminate allowable, socket bearing or bonded-transfer allowable is released.
TUBE_OUTER_DIAMETER_M = 0.012
TUBE_INNER_DIAMETER_M = 0.010

# Static balance proxy from ADR-0025/ADR-0045.  Treating each mass as a point at
# its CG gives a lower-bound inertia illustration, not the moving surface inertia.
ELEVON_MASS_KG = 0.0225
ELEVON_CG_AFT_M = 0.024
BALANCE_MASS_KG = 0.027
BALANCE_ARM_FORWARD_M = 0.020

# Values published only in I-05/ADR-0025; no reproducible modal owner exists.
PUBLISHED_MODAL_ESTIMATES_HZ = {
    "wing bending": 25.0,
    "wing torsion": 106.0,
    "elevon": 82.0,
}


def sha256(path: Path) -> str:
    """Return a streaming SHA-256 fingerprint."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def wing_load_shape(target_cl: float = config.CL_MAX_WING) -> dict[str, np.ndarray | float]:
    """Return the current rigid-wing VLM strip load shape at ``target_cl``.

    Unit-density, unit-speed panel loads are normalized to fractions of total
    aircraft lift.  Physical loads can then be applied without copying an
    aerodynamic distribution into this audit.
    """
    ny, nx = config.VLM_NY, config.VLM_NX
    lattice = geom(
        config.B,
        config.S,
        config.TAPER,
        config.SWEEP_C4_DEG,
        config.DESIGN_TWIST_DEG,
        ny=ny,
        nx=nx,
    )
    cl_zero = solve(lattice, 0.0)[0]
    cl_four = solve(lattice, 4.0)[0]
    cl_alpha = (cl_four - cl_zero) / math.radians(4.0)
    alpha_deg = math.degrees((target_cl - cl_zero) / cl_alpha)
    cl, _, panel_lift, _ = solve(lattice, alpha_deg)
    strip_lift = panel_lift.reshape(ny, nx).sum(axis=1)
    y = lattice["cps"][:, 1].reshape(ny, nx)[:, 0]
    chord = lattice["chord"].reshape(ny, nx)[:, 0]
    return {
        "cl": float(cl),
        "cl_alpha": float(cl_alpha),
        "alpha_deg": float(alpha_deg),
        "y": y,
        "chord": chord,
        "share": strip_lift / strip_lift.sum(),
    }


def semispan_loads(load_factor: float, shape: dict[str, np.ndarray | float]) -> dict:
    """Aerodynamic-only right-semispan load-path screen at one load factor."""
    y = np.asarray(shape["y"])
    chord = np.asarray(shape["chord"])
    share = np.asarray(shape["share"])
    strip_force = load_factor * config.ARTICLE_V1_MASS_KG * config.G0 * share
    right = y > 0.0
    half_force = float(strip_force[right].sum())
    root_moment = float(np.sum(strip_force[right] * y[right]))
    root_torque = float(
        np.sum(strip_force[right] * EA_ARM_FRACTION * chord[right])
    )
    rows = []
    for station in JOINT_STATIONS_M:
        outboard = right & (y >= station)
        force = float(strip_force[outboard].sum())
        moment = float(np.sum(strip_force[outboard] * (y[outboard] - station)))
        torque = float(
            np.sum(strip_force[outboard] * EA_ARM_FRACTION * chord[outboard])
        )
        rows.append(
            {
                "station": station,
                "force": force,
                "moment": moment,
                "torque": torque,
                "couple_force": torque / joint_pin_trade.ARM,
            }
        )
    return {
        "load_factor": load_factor,
        "half_force": half_force,
        "centroid": root_moment / half_force,
        "root_moment": root_moment,
        "root_torque": root_torque,
        "stations": rows,
    }


def tube_section_modulus() -> float:
    inertia = math.pi / 64.0 * (
        TUBE_OUTER_DIAMETER_M**4 - TUBE_INNER_DIAMETER_M**4
    )
    return inertia / (TUBE_OUTER_DIAMETER_M / 2.0)


def divergence_cases() -> dict[str, float]:
    """Consume the current divergence owner and reproduce its three corners."""
    ys, chord, _, torsion_j = divergence.grid()
    e_nominal, e_optimistic, _ = divergence.E_BAND
    q_nominal = divergence.q_divergence(
        ys,
        chord,
        torsion_j,
        divergence.G_PETG,
        divergence.A_SLOPE[0],
        e_nominal,
        joint=True,
    )
    nominal = divergence.K_SWEEP[0] * divergence.v_from_q(q_nominal) * 3.6

    ys_o, chord_o, _, torsion_j_o = divergence.grid(
        area_factor=divergence.AREA_BAND[2]
    )
    q_optimistic = divergence.q_divergence(
        ys_o,
        chord_o,
        torsion_j_o,
        divergence.G_PETG * (1.0 + divergence.G_BAND),
        divergence.A_SLOPE[1],
        e_optimistic,
        joint=True,
    )
    optimistic = divergence.K_SWEEP[2] * divergence.v_from_q(q_optimistic) * 3.6
    conservative = divergence.conservative_divergence_speed() * 3.6
    return {
        "nominal": nominal,
        "conservative": conservative,
        "optimistic": optimistic,
    }


def static_amplification(speed_kmh: float, v_div_kmh: float) -> float:
    ratio = (speed_kmh / v_div_kmh) ** 2
    return math.inf if ratio >= 1.0 else 1.0 / (1.0 - ratio)


def file_inventory() -> dict[str, int]:
    """Count design-review artifacts without treating placeholders as authority."""
    meaningful_cad = [
        path
        for folder in (config.REPO_ROOT / "cad", config.REPO_ROOT / "stl")
        for path in folder.rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    ]
    return {
        "manufacturing_files": len(meaningful_cad),
        "review_svgs": len(list(config.DRAWINGS_DIR.glob("*.svg"))),
        "provisional_objs": len(
            list((config.REPO_ROOT / "geometry" / "fuselage" / "provisional").glob("*.obj"))
        ),
    }


def main() -> None:
    print("=" * 88)
    print("NF DESIGN GUIDE 2024 AUDIT - PART 4: STRUCTURE, JOINTS AND AEROELASTIC RELEASE")
    print("=" * 88)
    source_hash = sha256(PDF)
    print(f"Source SHA-256: {source_hash}")
    print("NF scope: PDF pp. 109-113, 246-266 and 303-308")

    shape = wing_load_shape()
    limit = semispan_loads(config.POSITIVE_LIMIT_LOAD_FACTOR, shape)
    ultimate = semispan_loads(
        config.POSITIVE_LIMIT_LOAD_FACTOR * config.ULTIMATE_SAFETY_FACTOR, shape
    )
    print("\n1. RIGID-WING AERODYNAMIC LOAD-PATH SCREEN [I]")
    print(
        f"   VLM {config.VLM_NY}x{config.VLM_NX}; CL={shape['cl']:.6f}; "
        f"alpha={shape['alpha_deg']:.3f} deg; +{limit['load_factor']:.0f} g limit / "
        f"+{ultimate['load_factor']:.0f} g ultimate"
    )
    print(
        "   Excludes inertia relief, control-load movement, flexibility, cut-outs and stall."
    )
    print("   case       half lift   centroid y   root M      root T (xEA/c=0.45)")
    for label, case in (("limit", limit), ("ultimate", ultimate)):
        print(
            f"   {label:8s}  {case['half_force']:8.2f} N   "
            f"{case['centroid']*1000:8.1f} mm  {case['root_moment']:7.2f} N*m  "
            f"{case['root_torque']:7.3f} N*m"
        )

    print("\n   Outboard demands at structural interfaces")
    print("   case      y       shear      local BM    EA torque   65-mm couple force")
    for label, case in (("limit", limit), ("ultimate", ultimate)):
        for row in case["stations"]:
            print(
                f"   {label:8s} {row['station']*1000:4.0f} mm  "
                f"{row['force']:8.2f} N  {row['moment']:8.3f} N*m  "
                f"{row['torque']:8.3f} N*m  {row['couple_force']:8.2f} N"
            )

    z_tube = tube_section_modulus()
    joint_limit = limit["stations"][0]
    joint_ultimate = ultimate["stations"][0]
    print("\n2. CORE--PANEL JOINT DIAGNOSTICS")
    print(
        f"   Ø12/10 tube section modulus={z_tube:.3e} m3; if it alone carried the "
        f"y=195 bending screen: {joint_limit['moment']/z_tube/1e6:.1f} MPa limit / "
        f"{joint_ultimate['moment']/z_tube/1e6:.1f} MPa ultimate."
    )
    print(
        f"   Current joint torque band maximum={joint_pin_trade.T_JOINT[1]:.3f} N*m; "
        f"rigid-wing screen={joint_limit['torque']:.3f} N*m limit / "
        f"{joint_ultimate['torque']:.3f} N*m ultimate."
    )
    print(
        "   Pin-couple rotational stiffness scales with translational socket/pin "
        "stiffness times arm^2; the repository has only a relative pin EI trade, "
        "not an absolute assembly k_joint."
    )

    pin_area = math.pi * (filament_dowel_pins.D_PIN / 2.0) ** 2
    two_pin_single_shear_capacity = (
        filament_dowel_pins.N_PINS_PER_JOINT
        * pin_area
        * filament_dowel_pins.TAU_PETG[0]
    )
    worst_limit_dowel_demand = (
        config.POSITIVE_LIMIT_LOAD_FACTOR
        * config.ARTICLE_V1_MASS_KG
        * config.G0
        / 2.0
        * max(filament_dowel_pins.FRAC_OUT[347])
    )
    worst_ultimate_dowel_demand = (
        config.ULTIMATE_SAFETY_FACTOR * worst_limit_dowel_demand
    )
    print(
        f"   Glued-joint dowels cross one butt-joint shear plane: two-pin, "
        f"single-shear capacity at 26 MPa={two_pin_single_shear_capacity:.1f} N; "
        f"worst declared y=347 ultimate demand={worst_ultimate_dowel_demand:.1f} N; "
        f"screen FS={two_pin_single_shear_capacity/worst_ultimate_dowel_demand:.2f}."
    )
    print(
        "   The published FS~11 uses double shear and mean limit demand; it is not "
        "the governing one-plane ultimate comparison."
    )

    div = divergence_cases()
    required = divergence.F_DIV * config.ARTICLE_V_NE_KMH
    gj_factor = (required / div["conservative"]) ** 2
    equivalent_wall = divergence.T_SKIN * gj_factor
    combined = div["conservative"] * math.sqrt(
        0.69e9 / (divergence.G_PETG * (1.0 - divergence.G_BAND))
    ) * math.sqrt(1.10) * math.sqrt(1.20)
    combined_factor = (required / combined) ** 2
    print("\n3. DIVERGENCE CLEARANCE AND TEST-SCHEDULE AUDIT")
    print(
        f"   Vdiv conservative/nominal/optimistic = {div['conservative']:.1f} / "
        f"{div['nominal']:.1f} / {div['optimistic']:.1f} km/h."
    )
    print(
        f"   Criterion={required:.1f} km/h; conservative margin="
        f"{div['conservative']/required:.3f}x; strict supported VNE="
        f"{div['conservative']/divergence.F_DIV:.1f} km/h."
    )
    print(
        f"   Required GJ multiplier at unchanged aero/geometry={gj_factor:.3f}x "
        f"(linear-wall analogy: 0.9 -> {equivalent_wall*1000:.2f} mm)."
    )
    print(
        f"   Published combined sensitivity={combined:.1f} km/h; residual GJ "
        f"multiplier to 240 km/h={combined_factor:.3f}x."
    )
    print(
        f"   Corner spread: V ratio={div['optimistic']/div['conservative']:.2f}x; "
        f"q ratio={(div['optimistic']/div['conservative'])**2:.1f}x; this is a "
        "non-statistical uncertainty envelope."
    )
    print("\n   speed   q/qdiv   static amplification   current schedule status")
    for speed in (90.0, 95.0, 105.0, 110.0, 130.0, 150.0):
        q_ratio = (speed / div["conservative"]) ** 2
        amplification = static_amplification(speed, div["conservative"])
        if q_ratio >= 1.0:
            amp_text = "SUPERCRITICAL"
        else:
            amp_text = f"{amplification:6.2f}x"
        if speed > config.INITIAL_SPEED_LIMIT_KMH:
            status = "above 105-km/h cap"
        else:
            status = "inside active cap"
        print(f"   {speed:5.0f}   {q_ratio:7.3f}       {amp_text:>13s}   {status}")

    inertia_before = ELEVON_MASS_KG * ELEVON_CG_AFT_M**2
    inertia_added = BALANCE_MASS_KG * BALANCE_ARM_FORWARD_M**2
    fixed_k_frequency_ratio = math.sqrt(inertia_before / (inertia_before + inertia_added))
    point = propulsion_match.o1_boundary()
    print("\n4. MODAL AND CONTROL-SURFACE EVIDENCE")
    for mode, frequency in PUBLISHED_MODAL_ESTIMATES_HZ.items():
        print(f"   I-05 {mode:12s}: {frequency:6.1f} Hz [E], no reproducible modal owner")
    print(
        f"   Point-mass balance proxy: elevon inertia={inertia_before*1e6:.2f}e-6 "
        f"kg*m2; added balance inertia={inertia_added*1e6:.2f}e-6 kg*m2; "
        f"fixed-K frequency ratio={fixed_k_frequency_ratio:.3f}."
    )
    print(
        f"   O1 boundary propeller: {point.rpm:.0f} rpm -> 1/rev "
        f"{point.rpm/60.0:.1f} Hz, two-blade passage {2.0*point.rpm/60.0:.1f} Hz."
    )
    print(
        f"   APC limit: {propulsion_match.APC_MAX_RPM:.0f} rpm -> 1/rev "
        f"{propulsion_match.APC_MAX_RPM/60.0:.1f} Hz, blade passage "
        f"{2.0*propulsion_match.APC_MAX_RPM/60.0:.1f} Hz; a 1-kHz log has "
        "500-Hz Nyquist before sensor filtering."
    )

    inventory = file_inventory()
    print("\n5. MANUFACTURING AUTHORITY")
    print(
        f"   cad/ + stl/ meaningful files: {inventory['manufacturing_files']}; "
        f"review SVGs: {inventory['review_svgs']}; provisional OBJ meshes: "
        f"{inventory['provisional_objs']}."
    )
    print(
        "   The review geometry is useful for packaging, but no native assembly, "
        "manufacturing mesh or as-built structural definition exists."
    )

    print("\n6. VALIDATION CASES")
    checks: list[tuple[str, bool]] = []
    checks.append(("reviewed PDF fingerprint matches", source_hash == EXPECTED_PDF_SHA256))
    checks.append(("VLM solution reaches released wing CLmax", abs(shape["cl"] - config.CL_MAX_WING) < 1e-10))
    checks.append(("right semispan carries one half of total symmetric lift", abs(limit["half_force"] / (config.POSITIVE_LIMIT_LOAD_FACTOR * config.ARTICLE_V1_MASS_KG * config.G0) - 0.5) < 1e-10))
    checks.append(("ultimate load is exactly 1.5 times limit", abs(ultimate["root_moment"] / limit["root_moment"] - config.ULTIMATE_SAFETY_FACTOR) < 1e-12))
    checks.append(("current joint torque band is below the +6-g EA-torque screen", joint_limit["torque"] > joint_pin_trade.T_JOINT[1]))
    checks.append(("a butt-joint dowel has one shear plane, half the assumed double-shear capacity", math.isclose(two_pin_single_shear_capacity * 2.0, filament_dowel_pins.N_PINS_PER_JOINT * filament_dowel_pins.pin_capacity(filament_dowel_pins.D_PIN, filament_dowel_pins.TAU_PETG[0], double_shear=True), rel_tol=1e-12)))
    checks.append(("conservative divergence fails the 1.5-VNE criterion", div["conservative"] < required))
    checks.append(("130 and 150 km/h are supercritical in the conservative model", all((speed / div["conservative"]) ** 2 >= 1.0 for speed in (130.0, 150.0))))
    checks.append(("static balance lowers the fixed-K point-mass frequency proxy", fixed_k_frequency_ratio < 1.0))
    checks.append(("no CAD/STL manufacturing authority is present", inventory["manufacturing_files"] == 0))

    ok = True
    for name, passed in checks:
        ok = ok and passed
        print(f"   [{'PASS' if passed else 'FAIL'}] {name}")
    print(f"\n   VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
