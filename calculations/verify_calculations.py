#!/usr/bin/env python3
"""Cross-module verification for the Salamandra calculation system.

Individual scripts validate their own equations. This harness verifies the
interfaces between them: one geometry, one mass allocation, one battery model,
one atmosphere, distinct speed roles, and a closed total electrical-power
budget. It is the first command to run after changing a shared input.

Use --all-scripts to execute every deterministic local calculation CLI after
the interface checks. XFOIL-dependent and network-calibration scripts are
listed but intentionally excluded; their raw-data workflows have separate
acceptance gates.
"""
import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import airfoil_reflex_trade
import b3_screening
import balance_cg
import battery_pack_layout
import design_config
import divergence
import elevon_authority
import fpv_power_budget
import inav_fc_match
import launch_speed
import mass_budget
import propulsion_match
import servo_torque
import sweep_trade
import ventana_torsion
import vlm_ala_volante
import weissinger_np
import yaw_stability

ROOT = Path(__file__).resolve().parent.parent

LOCAL_SCRIPTS = (
    "design_config.py",
    "battery_pack_layout.py",
    "mass_budget.py",
    "balance_cg.py",
    "vlm_ala_volante.py",
    "weissinger_np.py",
    "sweep_trade.py",
    "elevon_authority.py",
    "ventana_torsion.py",
    "servo_torque.py",
    "inav_fc_match.py",
    "fpv_power_budget.py",
    "propulsion_match.py",
    "launch_speed.py",
    "filament_dowel_pins.py",
    "joint_pin_trade.py",
    "boom_flexion.py",
    "yaw_stability.py",
    "divergence.py",
)

EXTERNAL_WORKFLOWS = (
    "airfoil_reflex_trade.py (XFOIL)",
    "b3_screening.py (XFOIL)",
    "calibra_xfoil_e387.py (network + XFOIL)",
)


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def close(actual, expected, atol=1e-9):
    return abs(actual - expected) <= atol


def contract_checks():
    """Build and evaluate every shared numerical contract."""
    checks = []

    def add(name, condition, detail):
        checks.append(Check(name, bool(condition), detail))

    for name, passed in design_config.validate_geometry().items():
        add(f"geometry: {name}", passed, "design_config invariant")

    _, clean = mass_budget.build("all_petg", fin=False)
    _, v1 = mass_budget.build("all_petg", fin=True)
    add(
        "mass: CLEAN budget equals shared contract",
        close(clean["auw"] / 1000.0, design_config.ARTICLE_CLEAN_MASS_KG),
        f"{clean['auw']:.2f} g",
    )
    add(
        "mass: V1 analytical lower model equals shared contract",
        close(v1["auw"] / 1000.0, design_config.ARTICLE_V1_MASS_KG),
        f"{v1['auw']:.2f} g",
    )
    add(
        "mass risk: C32 analytical V1 currently exceeds the stall requirement",
        v1["vs"] > design_config.STALL_SPEED_LIMIT_KMH,
        f"{v1['vs']:.4f} km/h; allocation/F2 closure open",
    )

    pack_mass = battery_pack_layout.pack_mass_g("6S1P", "P42A") / 1000.0
    layout = balance_cg.solve_reference_layout()
    balance_mass = layout["m0"] + pack_mass
    add(
        "battery: layout, mass budget and balance use one 6S1P mass",
        close(pack_mass, mass_budget.pack_mass("6S1P", "P42A") / 1000.0)
        and close(pack_mass, balance_cg.REFERENCE_PACK),
        f"{pack_mass*1000:.1f} g",
    )
    add(
        "balance: solved CLEAN mass closes against mass budget",
        abs(balance_mass - design_config.ARTICLE_CLEAN_MASS_KG) < 5e-5,
        f"{balance_mass*1000:.2f} g",
    )
    dynamic_boom_mass = layout["components"][-1][1]
    add(
        "structure: balance boom agrees with mass-budget allocation",
        abs(dynamic_boom_mass * 1000.0 - mass_budget.BOOM_REF) < 0.1,
        f"{dynamic_boom_mass*1000:.2f} vs {mass_budget.BOOM_REF:.2f} g",
    )
    add(
        "battery: balance cradle length comes from pack envelope",
        close(
            balance_cg.PACK_LEN["6S1P"],
            battery_pack_layout.reference_pack_envelope("6S1P")[0] / 1000.0,
        ),
        f"{balance_cg.PACK_LEN['6S1P']*1000:.1f} mm",
    )

    v1_cl = design_config.lift_coefficient(
        design_config.ARTICLE_V1_MASS_KG,
        design_config.speed_mps(design_config.CRUISE_SPEED_KMH),
    )
    for module_name, value in (
        ("airfoil_reflex_trade", airfoil_reflex_trade.CL_CRUISE),
        ("b3_screening", b3_screening.CRUISE_CL),
        ("elevon_authority", elevon_authority.CL_CRU),
        ("sweep_trade", sweep_trade.CL_CRUISE),
        ("ventana_torsion", ventana_torsion.CL_CRUISE),
    ):
        add(
            f"aerodynamics: {module_name} uses shared V1 cruise CL",
            close(value, v1_cl, 1e-12),
            f"CL={value:.8f}",
        )
    add(
        "aerodynamics: torsion window separates V1 allocation from C32 model",
        ventana_torsion.CL_ALLOCATION_REQUIRED <= design_config.CL_MAX_WING
        < ventana_torsion.CL_MAX_REQUIRED,
        f"CL allocation={ventana_torsion.CL_ALLOCATION_REQUIRED:.5f}; "
        f"model={ventana_torsion.CL_MAX_REQUIRED:.5f}; "
        f"CLmax={design_config.CL_MAX_WING:.5f}",
    )
    clean_cl = design_config.lift_coefficient(
        design_config.ARTICLE_CLEAN_MASS_KG,
        design_config.speed_mps(design_config.CRUISE_SPEED_KMH),
    )
    add(
        "aerodynamics: yaw CLEAN model uses shared clean cruise CL",
        close(yaw_stability.CL_CRU, clean_cl, 1e-12),
        f"CL={yaw_stability.CL_CRU:.8f}",
    )
    add(
        "launch: V1 stall uses the same mass/CLmax equation as mass budget",
        close(
            launch_speed.v_stall(design_config.ARTICLE_V1_MASS_KG) * 3.6,
            v1["vs"],
            1e-12,
        ),
        f"{v1['vs']:.4f} km/h",
    )

    avionics_w = inav_fc_match.avionics_power_budget()[2]
    hotel_w = fpv_power_budget.reference_hotel_load_w()
    boundary = propulsion_match.o1_boundary()
    total_w = boundary.electrical_w + hotel_w
    add(
        "power: inav and FPV modules share avionics power",
        close(fpv_power_budget.AVIONICS_W, avionics_w, 1e-12),
        f"{avionics_w:.4f} W",
    )
    add(
        "power: motor plus hotel load closes exactly to O1",
        close(total_w, design_config.electrical_power_limit_w(), 1e-9),
        f"{boundary.electrical_w:.4f} + {hotel_w:.4f} = {total_w:.4f} W",
    )
    add(
        "propulsion: coefficient and dimensional power obey T*V=eta*P",
        close(
            boundary.thrust_n
            * design_config.speed_mps(design_config.CRUISE_SPEED_KMH),
            boundary.eta_prop * boundary.shaft_w,
            1e-9,
        ),
        f"J={boundary.j:.5f}, eta={boundary.eta_prop:.5f}",
    )
    add(
        "propulsion: O1 boundary awaits measured E2 drag",
        boundary.thrust_n > 0.0 and propulsion_match.REFERENCE_HOTEL_LOAD_W > 0.0,
        f"allowable drag={boundary.thrust_n:.4f} N pending E2",
    )

    add(
        "speeds: divergence uses 160 km/h article V_NE",
        close(divergence.V_NE * 3.6, design_config.ARTICLE_V_NE_KMH),
        f"{divergence.V_NE*3.6:.1f} km/h",
    )
    add(
        "speeds: servo and fin strength use 180 km/h structural case",
        close(
            servo_torque.speed_mps(
                design_config.STRUCTURAL_DESIGN_SPEED_KMH) * 3.6,
            yaw_stability.V_NE * 3.6,
        ),
        f"{yaw_stability.V_NE*3.6:.1f} km/h",
    )
    add(
        "airfoil: divergence uses the released Salamandra r1 root",
        divergence.PROFILE_FILE.endswith("salamandra-root-r1.dat")
        and (ROOT / divergence.PROFILE_FILE).is_file(),
        divergence.PROFILE_FILE,
    )

    vlm = vlm_ala_volante.analiza(
        design_config.B, design_config.S, design_config.TAPER,
        design_config.SWEEP_C4_DEG, 0.0, ny=24, nx=4, verbose=False)
    weissinger = weissinger_np.weissinger(
        design_config.B, design_config.S, design_config.TAPER,
        design_config.SWEEP_C4_DEG, ny=60)
    add(
        "stability: independent NP methods agree within 5 mm",
        abs(vlm["x_np"] - weissinger["x_np"]) < 0.005,
        f"VLM={vlm['x_np']*1000:.2f}, WL={weissinger['x_np']*1000:.2f} mm",
    )
    add(
        "controls: SI torque conversion and factored Corona margin pass",
        10.19 < servo_torque.nm_to_kgf_cm(1.0) < 10.20
        and servo_torque.CORONA_TORQUE_KGFCM
        / servo_torque.required_catalog_torque_kgf_cm() >= 2.5,
        f"required={servo_torque.required_catalog_torque_kgf_cm():.3f} kgf*cm",
    )
    fin_area = yaw_stability.fin_area_for_target(0.0005)
    fin_mass_lower = yaw_stability.fin_mass_band(fin_area)[0]
    add(
        "mass risk: complete V1 fin analytical lower bound exceeds its allocation",
        6.0 <= fin_mass_lower - design_config.V1_FIN_MASS_CAP_KG * 1000.0 <= 7.0,
        f"{fin_mass_lower:.2f} g model vs "
        f"{design_config.V1_FIN_MASS_CAP_KG*1000.0:.2f} g cap; F2 open",
    )
    fin_cnr = yaw_stability.cnr_wing() + yaw_stability.cnr_fin(
        fin_area, yaw_stability.L_V,
        yaw_stability.helmbold_cla(3.0, 12.0))
    fin_modes = yaw_stability.yaw_modes(0.0005, fin_cnr)
    add(
        "yaw: corrected V1 2-DOF modes are damped",
        all(value.real < 0.0 for value in fin_modes),
        ", ".join(f"{value:.3f}" for value in fin_modes),
    )

    return checks


def run_local_scripts(timeout_s):
    """Run deterministic local CLIs and return Check records."""
    checks = []
    for name in LOCAL_SCRIPTS:
        started = time.perf_counter()
        try:
            result = subprocess.run(
                [sys.executable, str(Path(__file__).parent / name)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
            elapsed = time.perf_counter() - started
            tail = " | ".join(
                (result.stdout + result.stderr).strip().splitlines()[-2:])
            checks.append(Check(
                f"script: {name}",
                result.returncode == 0,
                f"{elapsed:.2f} s; exit={result.returncode}; {tail}",
            ))
        except subprocess.TimeoutExpired:
            checks.append(Check(
                f"script: {name}", False, f"timeout after {timeout_s:.0f} s"))
    return checks


def print_checks(title, checks):
    print(f"\n{title}")
    print("-" * len(title))
    for check in checks:
        print(f"[{'PASS' if check.passed else 'FAIL'}] {check.name}: {check.detail}")
    return all(check.passed for check in checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all-scripts", action="store_true",
        help="also run every deterministic local calculation CLI")
    parser.add_argument(
        "--timeout", type=float, default=180.0,
        help="per-script timeout used with --all-scripts")
    args = parser.parse_args()
    if args.timeout <= 0.0:
        parser.error("--timeout must be positive")

    print("=" * 78)
    print("SALAMANDRA CALCULATION SYSTEM - CROSS-MODULE VERIFICATION")
    print("=" * 78)
    ok = print_checks("INTERFACE CONTRACTS", contract_checks())

    if args.all_scripts:
        ok = print_checks(
            "DETERMINISTIC SCRIPT VALIDATIONS",
            run_local_scripts(args.timeout),
        ) and ok

    print("\nExternal workflows not run:")
    for workflow in EXTERNAL_WORKFLOWS:
        print(f"  - {workflow}")
    print(f"\nSYSTEM VERIFICATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
