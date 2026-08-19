#!/usr/bin/env python3
"""Cross-module verification for the Salamandra calculation system.

Individual scripts validate their own equations. This harness verifies the
interfaces between them: one geometry, one mass allocation, one battery model,
one atmosphere, distinct speed roles, and a closed total electrical-power
budget. It is the first command to run after changing a shared input.

By default it runs the interface contracts AND every deterministic local
calculation CLI, so each module's own validation case is actually exercised;
`--fast` restricts the run to the interface contracts. XFOIL-dependent and
network-calibration scripts are listed but intentionally excluded; their
raw-data workflows have separate acceptance gates.

Every contract group is evaluated in isolation: a group that raises is reported
as a failed check carrying the exception text, never as an aborted run.
"""
import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from functools import cache
from math import dist
from pathlib import Path

import aero_contract
import aircraft_scene
import airfoil_reflex_trade
import b3_screening
import balance_cg
import battery_pack_layout
import design_config
import divergence
import drag_model
import elevon_authority
import elevon_sizing
import equipment_catalog
import equipment_layout
import flight_envelope
import fpv_power_budget
import fuselage_contract
import fuselage_geometry
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
    "aircraft_scene.py",
    "drawing_index.py",
    "equipment_catalog.py",
    "fuselage_contract.py",
    "fuselage_geometry.py",
    "fuselage_trade.py",
    "drag_model.py",
    "aero_contract.py",
    "contract_lint.py",
    "generate_blueprints.py",
    "battery_pack_layout.py",
    "mass_budget.py",
    "balance_cg.py",
    "equipment_layout.py",
    "vlm_ala_volante.py",
    "weissinger_np.py",
    "sweep_trade.py",
    "elevon_sizing.py",
    "elevon_authority.py",
    "ventana_torsion.py",
    "flight_envelope.py",
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

# `mutation_test.py` deliberately stays OUT of this list: it runs the contract
# suite once per seeded defect, so nesting it here would re-enter the harness
# recursively.  CI runs it as its own step, right after this one.
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


# ---------------------------------------------------------------------------
# Shared setup.  Cached so each group can ask for what it needs independently:
# a group that cannot build its inputs fails on its own without taking the rest
# of the suite with it.
# ---------------------------------------------------------------------------
@cache
def _mass_totals():
    _, clean = mass_budget.build("all_petg", fin=False)
    _, v1 = mass_budget.build("all_petg", fin=True)
    return clean, v1


@cache
def _solved_equipment():
    clean_layout, clean_required = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("clean"))
    v1_layout, v1_required = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("v1"), clamp=True)
    return clean_layout, clean_required, v1_layout, v1_required


def check_geometry(add):
    for name, passed in design_config.validate_geometry().items():
        add(f"geometry: {name}", passed, "design_config invariant")


def check_mass(add):
    clean, v1 = _mass_totals()
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
        "mass: C32 analytical V1 remains below the stall requirement",
        v1["vs"] <= design_config.STALL_SPEED_LIMIT_KMH,
        f"{v1['vs']:.4f} km/h; measured F2 closure remains open",
    )


def check_aero_contract(add):
    for name, passed in aero_contract.validation_checks().items():
        add(f"aero contract: {name}", passed,
            f"x_NP={aero_contract.neutral_point_vlm()*1000:+.2f} mm "
            f"({aero_contract.neutral_point_percent_mac():.2f} % MAC)")
    add(
        "aero contract: the CG target is derived, not a copied literal",
        close(balance_cg.cg_target(),
              aero_contract.neutral_point_vlm()
              - design_config.STATIC_MARGIN * design_config.MAC, 1e-12),
        f"CG target={balance_cg.cg_target()*1000:+.3f} mm",
    )


def check_drag(add):
    for name, passed in drag_model.validation_checks().items():
        add(f"drag: {name}", passed, "shared polar, ADR-0009")
    add(
        "drag: yaw and launch modules share one polar",
        close(yaw_stability.CD_PROFILE_CRUISE, drag_model.CD_PROFILE_CRUISE)
        and close(yaw_stability.SPAN_EFFICIENCY, drag_model.SPAN_EFFICIENCY)
        and close(launch_speed.CD_LAUNCH, drag_model.launch_cd_band()[1]),
        f"CD0={drag_model.CD_PROFILE_CRUISE:.4f}, "
        f"e={drag_model.SPAN_EFFICIENCY:.2f}, "
        f"CD_launch={launch_speed.CD_LAUNCH:.4f} (conservative end)",
    )


def check_flight_envelope(add):
    cla = flight_envelope.project_lift_curve_slope()
    envelope_checks = flight_envelope.validation_checks(cla)
    for name, passed in envelope_checks.items():
        add(f"flight envelope: {name}", passed, f"CL_alpha={cla:.4f}/rad")


def check_balance_and_battery(add):
    clean, _v1 = _mass_totals()
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
        "balance: aggregate CLEAN mass agrees within boom-estimate precision",
        abs(balance_mass - design_config.ARTICLE_CLEAN_MASS_KG) <= 5e-4,
        f"{balance_mass*1000:.2f} g",
    )
    dynamic_boom_mass = layout["components"][-1][1]
    add(
        "structure: balance boom agrees within allocation rounding",
        abs(dynamic_boom_mass * 1000.0 - mass_budget.BOOM_REF) <= 0.5,
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
    add(
        "battery: 3D packaging uses the centralized maximum P42A envelope",
        all(
            close(actual, expected, 1e-12)
            for actual, expected in zip(
                equipment_layout.PACK_6S1P_CAD_ENVELOPE_MM,
                battery_pack_layout.reference_pack_cad_envelope(
                    "6S1P", "P42A"
                ),
            )
        ),
        " x ".join(
            f"{value:.1f}"
            for value in equipment_layout.PACK_6S1P_CAD_ENVELOPE_MM
        ) + " mm",
    )


def check_equipment_layout(add):
    clean, _v1 = _mass_totals()
    (equipment_clean, clean_battery_required,
     equipment_v1, v1_battery_required) = _solved_equipment()
    for name, passed in equipment_layout.validation_checks().items():
        add(f"equipment layout: {name}", passed, "3D packaging invariant")
    add(
        "equipment layout: CLEAN mass and x-CG close simultaneously",
        close(
            equipment_clean.mass_g(budgeted_only=True), clean["auw"], 1e-8
        )
        and close(
            equipment_clean.cg_mm()[0], equipment_layout.target_cg_mm(), 1e-9
        ),
        f"{equipment_clean.mass_g(budgeted_only=True):.2f} g; "
        f"battery x={clean_battery_required:+.2f} mm",
    )
    add(
        "equipment layout: FC is colocated with the CLEAN three-dimensional CG",
        dist(
            equipment_clean.component("fc").position_mm,
            equipment_clean.cg_mm(),
        ) <= 5.0,
        f"distance={dist(equipment_clean.component('fc').position_mm, equipment_clean.cg_mm()):.2f} mm",
    )
    add(
        "equipment mass: O4 antenna is budgeted inside the E19 VTX assembly",
        close(
            equipment_clean.mass_g()
            - equipment_clean.mass_g(budgeted_only=True),
            0.0,
            1e-12,
        ),
        f"installed delta={equipment_clean.mass_g() - equipment_clean.mass_g(budgeted_only=True):+.2f} g",
    )
    v1_battery = equipment_v1.component(equipment_layout.PRIMARY_CG_ADJUSTER)
    add(
        "equipment risk: V1 exact target exceeds current battery travel",
        v1_battery_required < v1_battery.bounds.minimum_mm[0],
        f"required={v1_battery_required:+.2f} mm; "
        f"forward limit={v1_battery.bounds.minimum_mm[0]:+.2f} mm",
    )
    add(
        "equipment risk: unextended V1 stop reaches only the tolerance band, not target",
        abs(equipment_v1.cg_mm()[0] - equipment_layout.target_cg_mm())
        <= equipment_layout.CG_TOLERANCE_MM
        and abs(equipment_v1.cg_mm()[0] - equipment_layout.target_cg_mm()) > 1.0,
        (
            f"xCG={equipment_v1.cg_mm()[0]:+.2f} mm; "
            f"target={equipment_layout.target_cg_mm():+.2f} ±"
            f"{equipment_layout.CG_TOLERANCE_MM:.1f} mm"
        ),
    )


def check_aerodynamics(add):
    _clean, v1 = _mass_totals()
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
        "aerodynamics: allocation and C32 V1 model pass released CLmax",
        ventana_torsion.CL_ALLOCATION_REQUIRED <= design_config.CL_MAX_WING
        and ventana_torsion.CL_MAX_REQUIRED <= design_config.CL_MAX_WING,
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


def check_power_and_propulsion(add):
    avionics_w = inav_fc_match.avionics_power_budget()[2]
    hotel_w = fpv_power_budget.reference_hotel_load_w()
    boundary = propulsion_match.o1_boundary()
    total_w = boundary.electrical_w + hotel_w
    add(
        "power: inav and FPV modules share avionics power",
        close(fpv_power_budget.reference_avionics_w(), avionics_w, 1e-12),
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
        boundary.thrust_n > 0.0 and propulsion_match.reference_hotel_load() > 0.0,
        f"allowable drag={boundary.thrust_n:.4f} N pending E2",
    )


def check_speeds(add):
    add(
        "speeds: divergence uses 160 km/h article V_NE",
        close(divergence.V_ARTICLE_NE * 3.6, design_config.ARTICLE_V_NE_KMH),
        f"{divergence.V_ARTICLE_NE*3.6:.1f} km/h",
    )
    add(
        "speeds: servo and fin strength use 180 km/h structural case",
        close(
            servo_torque.speed_mps(
                design_config.STRUCTURAL_DESIGN_SPEED_KMH) * 3.6,
            yaw_stability.V_STRUCTURAL * 3.6,
        ),
        f"{yaw_stability.V_STRUCTURAL*3.6:.1f} km/h",
    )
    # The aeroelastic clearance is a DERIVED ceiling on the operational cap.
    # divergence.py checked this internally; the relationship is cross-module,
    # so it belongs in the shared contract too.
    v_limit_kmh = divergence.operational_speed_limit_kmh()
    add(
        "speeds: the operational cap respects the aeroelastic clearance",
        design_config.INITIAL_SPEED_LIMIT_KMH <= v_limit_kmh,
        f"cap={design_config.INITIAL_SPEED_LIMIT_KMH:.0f} km/h vs "
        f"V_limit={v_limit_kmh:.0f} km/h "
        f"(conservative V_div="
        f"{divergence.conservative_divergence_speed()*3.6:.1f} km/h; "
        f"criterion needs {divergence.F_DIV*divergence.V_ARTICLE_NE*3.6:.0f} "
        "km/h - G6 remains open)",
    )
    add(
        "speeds: the ladder is ordered and V_A sits above the operational cap",
        design_config.validate_geometry()["the speed ladder is strictly ordered"]
        and design_config.validate_geometry()[
            "manoeuvring speed exceeds the initial operational cap"],
        "roles ordered; the cap is not a Part 23 V_C",
    )
    add(
        "airfoil: divergence uses the released Salamandra r1 root",
        divergence.PROFILE_FILE.name == "salamandra-root-r1.dat"
        and divergence.PROFILE_FILE.is_file(),
        str(divergence.PROFILE_FILE.relative_to(ROOT)),
    )


def check_stability(add):
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

def check_controls(add):
    add(
        "controls: the released torque factors are the declared ones",
        close(servo_torque.TORQUE_SAFETY_FACTOR, 1.50)
        and close(servo_torque.LINKAGE_EFFICIENCY, 0.80)
        and servo_torque.N_SERVOS_PER_ELEVON == 1,
        f"SF={servo_torque.TORQUE_SAFETY_FACTOR:.2f}, "
        f"eta={servo_torque.LINKAGE_EFFICIENCY:.2f}",
    )
    add(
        "power: the released O1 energy objective is the declared one",
        close(design_config.O1_ENERGY_LIMIT_WH_PER_KM, 1.15)
        and close(design_config.electrical_power_limit_w(), 109.25),
        f"{design_config.O1_ENERGY_LIMIT_WH_PER_KM:.2f} Wh/km -> "
        f"{design_config.electrical_power_limit_w():.2f} W",
    )
    add(
        "aerodynamics: the released CLmax is the I-07 value pending E2",
        close(design_config.CL_MAX_WING, 0.589),
        f"CLmax={design_config.CL_MAX_WING:.4f} [D], pending E2",
    )
    add(
        "controls: SI torque conversion and factored Corona margin pass",
        10.19 < servo_torque.nm_to_kgf_cm(1.0) < 10.20
        and servo_torque.CORONA_TORQUE_KGFCM
        / servo_torque.required_catalog_torque_kgf_cm() >= 1.5,
        f"required={servo_torque.required_catalog_torque_kgf_cm():.3f} kgf*cm",
    )
    selected_surface = elevon_sizing.surface_geometry(elevon_sizing.ARTICLE_1)
    selected_pitch = elevon_sizing.pitch_result(elevon_sizing.ARTICLE_1)
    selected_roll = elevon_sizing.roll_derivatives(elevon_sizing.ARTICLE_1)
    add(
        "controls: Article #1 elevon geometry is canonical across modules",
        close(selected_surface["span_m"], design_config.ELEVON_SPAN_M)
        and close(servo_torque.ETA_IN, design_config.ELEVON_ETA_IN)
        and close(servo_torque.ETA_OUT, design_config.ELEVON_ETA_OUT)
        and close(
            equipment_layout.SERVO_STATION_MM / 1000.0,
            design_config.ELEVON_SERVO_STATION_M,
        ),
        f"span={selected_surface['span_m']*1000:.1f} mm; "
        f"servo y={equipment_layout.SERVO_STATION_MM:.2f} mm",
    )
    add(
        "controls: the hinge-moment band covers the commanded trim deflection",
        abs(selected_pitch["trim_n12_deg"]) <= servo_torque.DELTA_TRIM_DEG
        and abs(selected_pitch["trim_n10_deg"]) <= servo_torque.DELTA_TRIM_DEG
        and servo_torque.DELTA_SIZING_DEG
        > abs(selected_pitch["trim_n12_deg"]),
        f"commanded trim <= {servo_torque.DELTA_TRIM_DEG:.1f} deg; Ch band "
        f"declared at {servo_torque.DELTA_SIZING_DEG:.1f} deg",
    )
    add(
        "controls: selected surface closes trim and retains roll authority",
        abs(selected_pitch["trim_n12_deg"]) <= 0.6
        and selected_roll["cl_delta_a_per_rad"] > 0.0
        and selected_roll["cl_p_per_rad"] < 0.0,
        f"trim={selected_pitch['trim_n12_deg']:+.3f} deg; "
        f"Cl_da={selected_roll['cl_delta_a_per_rad']:.4f}/rad",
    )

def check_yaw(add):
    fin_area = yaw_stability.fin_area_for_target(0.0005)
    fin_mass_lower = yaw_stability.fin_mass_band(fin_area)[0]
    add(
        "mass risk: twin-fin lower model stays within the cap by less than 1 g",
        0.0 <= design_config.V1_FIN_MASS_CAP_KG * 1000.0 - fin_mass_lower <= 1.0,
        f"{fin_mass_lower:.2f} g model vs "
        f"{design_config.V1_FIN_MASS_CAP_KG*1000.0:.2f} g cap; F2 open",
    )
    fin_cnr = yaw_stability.cnr_wing() + yaw_stability.cnr_fin(
        fin_area, yaw_stability.fin_moment_arm(),
        yaw_stability.helmbold_cla(
            yaw_stability.AR_FIN, yaw_stability.FIN_SWEEP_DEG))
    fin_modes = yaw_stability.yaw_modes(0.0005, fin_cnr)
    add(
        "yaw: corrected V1 2-DOF modes are damped",
        all(value.real < 0.0 for value in fin_modes),
        ", ".join(f"{value:.3f}" for value in fin_modes),
    )
    layout, _ = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("clean"))
    layout_izz = layout.inertia_kg_m2()[2][2]
    add(
        "yaw: one yaw inertia, shared with the 3D mass model",
        abs(yaw_stability.yaw_inertia() - layout_izz) / layout_izz < 0.10,
        f"yaw={yaw_stability.yaw_inertia():.5f} vs "
        f"layout={layout_izz:.5f} kg m2",
    )
    add(
        "yaw: the declared inertia band is propagated, not just declared",
        all(all(mode.real < 0.0 for mode in modes)
            for modes in yaw_stability.yaw_mode_band(0.0005, fin_cnr)),
        "modes stay damped across the full I_zz band",
    )


def check_fuselage(add):
    model = fuselage_geometry.reference_model()
    audits = fuselage_geometry.audit_envelopes(model)
    v1_state = fuselage_geometry.battery_state("v1")
    v1_packaging = equipment_layout.solve_v1_packaging()
    v1_model = fuselage_geometry.build_model(layout=v1_packaging.layout)
    for name, passed in fuselage_geometry.validation_checks(full=False).items():
        add(f"fuselage: {name}", passed, "I-28 NumPy OML software contract")
    add(
        "fuselage: generated OML contains every central inflated envelope",
        all(audit.passed for audit in audits),
        "; ".join(
            f"{audit.identifier}={audit.minimum_margin_mm:+.2f} mm"
            for audit in audits
        ),
    )
    add(
        "fuselage: generated OML remains provisional",
        model.design.family == fuselage_contract.DEFAULT_FAMILY
        and fuselage_contract.AUTHORITY == "[I]",
        f"{fuselage_contract.AUTHORITY} - {fuselage_contract.WARNING}",
    )
    add(
        "fuselage risk: V1 travel and multidisciplinary closure remain open",
        not v1_state["reachable"],
        (
            f"V1 required={v1_state['required_x_mm']:+.2f} mm; "
            "mesh feasibility is not aircraft release"
        ),
    )
    add(
        "fuselage: coupled V1 OML inherits the solved nose extension",
        close(
            v1_model.length_mm - model.length_mm,
            v1_packaging.nose_extension_mm,
            atol=1e-6,
        ),
        (
            f"CLEAN={model.length_mm:.2f} mm; V1={v1_model.length_mm:.2f} mm; "
            f"delta={v1_packaging.nose_extension_mm:.2f} mm"
        ),
    )


def check_aircraft_scene(add):
    for name, passed in aircraft_scene.validation_checks().items():
        add(f"aircraft scene: {name}", passed, "shared 3-D ledger/projection contract")


# ---------------------------------------------------------------------------
# Contract registry and isolated runner
# ---------------------------------------------------------------------------
CONTRACT_GROUPS = (
    ("geometry", check_geometry),
    ("mass", check_mass),
    ("aero contract", check_aero_contract),
    ("drag", check_drag),
    ("flight envelope", check_flight_envelope),
    ("balance and battery", check_balance_and_battery),
    ("equipment layout", check_equipment_layout),
    ("aerodynamics", check_aerodynamics),
    ("power and propulsion", check_power_and_propulsion),
    ("speeds", check_speeds),
    ("stability", check_stability),
    ("controls", check_controls),
    ("yaw", check_yaw),
    ("fuselage", check_fuselage),
    ("aircraft scene", check_aircraft_scene),
)


def contract_checks(groups=CONTRACT_GROUPS):
    """Evaluate every shared numerical contract, one isolated group at a time.

    A group that raises is reported as a failed check carrying the exception
    text.  It never aborts the run: a broken contract must produce a complete
    PASS/FAIL table and a non-zero exit code, not a traceback with no diagnosis.
    """
    checks = []
    for group_name, group in groups:
        produced = []

        def add(name, condition, detail, _sink=produced):
            _sink.append(Check(name, bool(condition), detail))

        try:
            group(add)
        except Exception as error:      # noqa: BLE001 - reported, never raised
            produced.append(Check(
                f"{group_name}: contract group raised",
                False,
                f"{type(error).__name__}: {error}",
            ))
        checks.extend(produced)
    return checks


def run_local_scripts(timeout_s):
    """Run deterministic local CLIs and return Check records."""
    checks = []
    for name in LOCAL_SCRIPTS:
        started = time.perf_counter()
        try:
            result = subprocess.run(
                [sys.executable, "-X", "utf8", str(Path(__file__).parent / name)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
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
        "--fast", action="store_true",
        help="interface contracts only; skip the deterministic script suite")
    parser.add_argument(
        "--all-scripts", action="store_true",
        help=argparse.SUPPRESS)      # retained: the script suite is now default
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

    if not args.fast:
        ok = print_checks(
            "DETERMINISTIC SCRIPT VALIDATIONS",
            run_local_scripts(args.timeout),
        ) and ok
    else:
        print("\nDeterministic script validations SKIPPED (--fast). "
              "Every module's own validation case is unverified in this run.")

    print("\nExternal workflows not run:")
    for workflow in EXTERNAL_WORKFLOWS:
        print(f"  - {workflow}")
    print(f"\nSYSTEM VERIFICATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
