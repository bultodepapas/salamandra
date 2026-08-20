#!/usr/bin/env python3
"""NF Design Guide 2024 audit, Part 5: wingtip and flap integration.

This audit calculation translates the guide's swept-wing/winglet lessons to the
current forward-swept Salamandra Article #1.  It deliberately does not design a
winglet.  Instead it:

* separates the current viscous and induced drag terms across speed;
* derives the optimistic wingtip-device crossover speed for declared parasite
  increments and an impossible-to-exceed ``e_span = 1`` endpoint;
* places possible vertical surfaces relative to the actual CG, demonstrating
  why a conventional tip-mounted fin does not inherit the current V1 yaw arm;
* interrogates the symmetric rigid-wing span loading at the 45 km/h requirement;
* locates the quarter-chord/CG crossing on the forward-swept wing; and
* maps the pitch-moment yield of hypothetical elevon segments, exposing what a
  one-piece elevon cannot schedule independently.

The drag polar is an engineering estimate and is transferred away from cruise
only as a sensitivity.  The VLM is rigid, inviscid, symmetric and attached-flow;
it contains neither vertical surfaces nor finite sideslip, transition, separation
or aeroelasticity.  Results marked [I] are therefore diagnostics, not a winglet,
stall, performance or flight release.
"""

from __future__ import annotations

import hashlib
import math
import sys
from pathlib import Path

import numpy as np

import design_config as config
import drag_model
import elevon_sizing
import propulsion_match
import yaw_stability as yaw
from balance_cg import cg_target
from vlm_ala_volante import geom, solve


PDF = config.REPO_ROOT / "INSPIRATION" / "NF Design guide 2024 english.pdf"
EXPECTED_PDF_SHA256 = (
    "a0e81c98b884c7a9c29f75a9bd7ccdf19ff2255642ba2ac5bdd4337696daabca"
)

SPEEDS_KMH = (45.0, 60.0, 75.0, 95.0, 105.0)
IDEAL_SPAN_EFFICIENCY = 1.0
DEVICE_DCD0_CASES = (0.00025, 0.00050, 0.00100, 0.00200)
LOCAL_SECTION_CL_SCREEN = 0.65  # generic screen already used by sweep_trade.py [E]
FLAP_WINDOW_ETA = 0.10


def sha256(path: Path) -> str:
    """Return a streaming SHA-256 fingerprint."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def level_flight_drag(speed_kmh: float) -> dict[str, float]:
    """Current V1-mass, CLEAN-aero drag sensitivity at one speed [D on E].

    ``CD_PROFILE_CRUISE`` is intentionally held constant.  Away from 95 km/h
    this is not a polar prediction; it only exposes how the induced fraction
    and the maximum possible span-efficiency benefit scale with speed.
    """
    speed = config.speed_mps(speed_kmh)
    cl = config.lift_coefficient(config.ARTICLE_V1_MASS_KG, speed)
    cd_profile, cd_induced = drag_model.clean_cd(cl)
    cd_induced_ideal = drag_model.induced_cd(
        cl,
        aspect_ratio=config.ASPECT_RATIO,
        span_efficiency=IDEAL_SPAN_EFFICIENCY,
    )
    drag = drag_model.drag_newton(cd_profile + cd_induced, speed)
    ideal_drag = drag_model.drag_newton(cd_profile + cd_induced_ideal, speed)
    return {
        "speed_kmh": speed_kmh,
        "cl": cl,
        "cd_profile": cd_profile,
        "cd_induced": cd_induced,
        "cd_induced_ideal": cd_induced_ideal,
        "induced_fraction": cd_induced / (cd_profile + cd_induced),
        "drag_n": drag,
        "ideal_drag_n": ideal_drag,
        "maximum_induced_saving_n": drag - ideal_drag,
    }


def crossover_state(delta_cd0: float, final_efficiency: float = 1.0) -> dict[str, float]:
    """Optimistic crossover where parasite cost equals induced-drag saving.

    The device is assumed to change only span efficiency from the repository's
    current estimate to ``final_efficiency``.  No real winglet can exceed 1.0,
    so the default is an upper bound on benefit, not a design prediction.
    """
    if delta_cd0 <= 0.0:
        raise ValueError("delta CD0 must be positive")
    initial_efficiency = drag_model.SPAN_EFFICIENCY
    if not initial_efficiency < final_efficiency <= 1.0:
        raise ValueError("final efficiency must be above the baseline and at most one")
    denominator = 1.0 / initial_efficiency - 1.0 / final_efficiency
    cl = math.sqrt(
        delta_cd0 * math.pi * config.ASPECT_RATIO / denominator
    )
    speed = math.sqrt(
        2.0
        * config.ARTICLE_V1_MASS_KG
        * config.G0
        / (config.RHO_SL * config.S * cl)
    )
    return {"delta_cd0": delta_cd0, "cl": cl, "speed_kmh": speed * 3.6}


def o1_drag_budget() -> dict[str, float]:
    """Contrast the current estimated clean/V1 drags with the O1 boundary."""
    cruise = level_flight_drag(config.CRUISE_SPEED_KMH)
    fin_area = yaw.fin_area_for_target(0.0005)
    fin_delta_cd0 = yaw.fin_drag(fin_area)[0]
    speed = config.speed_mps(config.CRUISE_SPEED_KMH)
    fin_drag = config.dynamic_pressure(speed) * config.S * fin_delta_cd0
    v1_drag = cruise["drag_n"] + fin_drag
    allowed = propulsion_match.o1_boundary().thrust_n
    clean_point = propulsion_match.solve_thrust(cruise["drag_n"])
    v1_point = propulsion_match.solve_thrust(v1_drag)
    return {
        "cl": cruise["cl"],
        "clean_drag_n": cruise["drag_n"],
        "fin_delta_cd0": fin_delta_cd0,
        "fin_drag_n": fin_drag,
        "v1_drag_n": v1_drag,
        "allowed_drag_n": allowed,
        "clean_margin_n": allowed - cruise["drag_n"],
        "v1_margin_n": allowed - v1_drag,
        "clean_energy_wh_km": propulsion_match.total_energy_wh_per_km(clean_point),
        "v1_energy_wh_km": propulsion_match.total_energy_wh_per_km(v1_point),
        "maximum_induced_saving_n": cruise["maximum_induced_saving_n"],
        "maximum_breakeven_delta_cd0": (
            cruise["cd_induced"] - cruise["cd_induced_ideal"]
        ),
    }


def wingtip_yaw_geometry() -> dict[str, float]:
    """Longitudinal arms of current and candidate vertical-surface stations."""
    cg = cg_target()
    tip_c4 = config.x_c4(config.HALF_SPAN)
    tip_te = config.x_te(config.HALF_SPAN)
    current_fin_arm = yaw.FIN_AC_STATION_M - cg
    tip_c4_arm = tip_c4 - cg
    tip_te_arm = tip_te - cg
    crossing_y = cg / math.tan(math.radians(config.SWEEP_C4_DEG))
    return {
        "cg_m": cg,
        "tip_c4_m": tip_c4,
        "tip_te_m": tip_te,
        "current_fin_ac_m": yaw.FIN_AC_STATION_M,
        "current_fin_arm_m": current_fin_arm,
        "tip_c4_arm_m": tip_c4_arm,
        "tip_te_arm_m": tip_te_arm,
        "c4_cg_crossing_y_m": crossing_y,
        "c4_cg_crossing_eta": crossing_y / config.HALF_SPAN,
        "tip_c4_fin_contribution_ratio": tip_c4_arm / current_fin_arm,
        "tip_te_fin_contribution_ratio": tip_te_arm / current_fin_arm,
        "tip_te_area_multiplier": current_fin_arm / tip_te_arm,
        "aft_extension_from_tip_te_m": yaw.FIN_AC_STATION_M - tip_te,
    }


def stall_distribution(
    ny: int = 80,
    nx: int = 8,
    twist_deg: float | None = None,
) -> dict[str, np.ndarray | float]:
    """Symmetric rigid-wing local-Cl screen at the 45 km/h requirement [I]."""
    if twist_deg is None:
        twist_deg = config.DESIGN_TWIST_DEG
    target_cl = config.lift_coefficient(
        config.ARTICLE_V1_MASS_KG,
        config.speed_mps(config.STALL_SPEED_LIMIT_KMH),
    )
    lattice = geom(
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
    cl_alpha = (cl_four - cl_zero) / math.radians(4.0)
    alpha_deg = math.degrees((target_cl - cl_zero) / cl_alpha)
    achieved_cl, _, panel_lift, _ = solve(lattice, alpha_deg)
    strip_lift = panel_lift.reshape(ny, nx).sum(axis=1)
    y = lattice["cps"][:, 1].reshape(ny, nx)[:, 0]
    dy = lattice["dy"].reshape(ny, nx)[:, 0]
    chord = lattice["chord"].reshape(ny, nx)[:, 0]
    local_cl = strip_lift / (0.5 * chord * dy)
    right = y > 0.0
    eta = y[right] / config.HALF_SPAN
    local_cl = local_cl[right]
    peak_index = int(np.argmax(local_cl))
    c4_relative_cg = np.array(
        [config.x_c4(float(station)) - cg_target() for station in y[right]]
    )
    return {
        "target_cl": target_cl,
        "achieved_cl": float(achieved_cl),
        "twist_deg": twist_deg,
        "alpha_deg": alpha_deg,
        "eta": eta,
        "local_cl": local_cl,
        "reserve": LOCAL_SECTION_CL_SCREEN - local_cl,
        "c4_relative_cg_m": c4_relative_cg,
        "peak_eta": float(eta[peak_index]),
        "peak_local_cl": float(local_cl[peak_index]),
        "peak_reserve": float(LOCAL_SECTION_CL_SCREEN - local_cl[peak_index]),
        "peak_c4_relative_cg_m": float(c4_relative_cg[peak_index]),
    }


def nearest_at(eta: np.ndarray, values: np.ndarray, target: float) -> tuple[float, float]:
    index = int(np.argmin(np.abs(eta - target)))
    return float(eta[index]), float(values[index])


def flap_cm_yield(eta_in: float, eta_out: float) -> float:
    """Cm0 yield per degree for a hypothetical symmetric control segment [I]."""
    surface = elevon_sizing.ElevonGeometry(
        f"audit {eta_in:.4f}-{eta_out:.4f}",
        eta_in,
        eta_out,
        config.ELEVON_CHORD_FRACTION,
    )
    return (
        elevon_sizing.cm0_wing(0.0, 1.0, surface)
        - elevon_sizing.cm0_wing(0.0, 0.0, surface)
    )


def moment_neutral_flap_window(width_eta: float = FLAP_WINDOW_ETA) -> dict[str, float]:
    """Locate a fixed-width segment whose linear-VLM Cm0 yield crosses zero."""
    if not 0.0 < width_eta < 1.0:
        raise ValueError("window width must lie in (0, 1)")
    lower, upper = 0.25, 0.65 - width_eta
    f_lower = flap_cm_yield(lower, lower + width_eta)
    f_upper = flap_cm_yield(upper, upper + width_eta)
    if f_lower * f_upper >= 0.0:
        raise RuntimeError("moment-neutral window is not bracketed")
    for _ in range(45):
        middle = 0.5 * (lower + upper)
        f_middle = flap_cm_yield(middle, middle + width_eta)
        if f_lower * f_middle <= 0.0:
            upper, f_upper = middle, f_middle
        else:
            lower, f_lower = middle, f_middle
    eta_in = 0.5 * (lower + upper)
    return {
        "eta_in": eta_in,
        "eta_out": eta_in + width_eta,
        "eta_center": eta_in + 0.5 * width_eta,
        "yield_per_deg": flap_cm_yield(eta_in, eta_in + width_eta),
    }


def reynolds_numbers(speed_kmh: float) -> dict[str, float]:
    speed = config.speed_mps(speed_kmh)
    return {
        "root": speed * config.ROOT_CHORD / config.NU_SL,
        "tip": speed * config.TIP_CHORD / config.NU_SL,
    }


def validation_checks() -> dict[str, bool]:
    source_hash = sha256(PDF)
    states = [level_flight_drag(speed) for speed in SPEEDS_KMH]
    o1 = o1_drag_budget()
    yaw_geometry = wingtip_yaw_geometry()
    span = stall_distribution()
    neutral = moment_neutral_flap_window()
    fin_cross = crossover_state(o1["fin_delta_cd0"])
    crossover_residual = level_flight_drag(fin_cross["speed_kmh"])
    q_s = config.dynamic_pressure(config.speed_mps(fin_cross["speed_kmh"])) * config.S
    device_drag = q_s * o1["fin_delta_cd0"]
    ideal_saving = crossover_residual["maximum_induced_saving_n"]
    return {
        "reviewed PDF exists and fingerprint matches":
            PDF.is_file() and source_hash == EXPECTED_PDF_SHA256,
        "induced fraction decreases monotonically with speed":
            all(a["induced_fraction"] > b["induced_fraction"]
                for a, b in zip(states, states[1:])),
        "crossover equality reproduces parasite and ideal induced terms":
            abs(device_drag - ideal_saving) < 1e-10,
        "current-fin-equivalent crossover lies beyond the released CLmax":
            fin_cross["cl"] > config.CL_MAX_WING,
        "estimated CLEAN drag is below but V1 drag is above the O1 boundary":
            o1["clean_margin_n"] > 0.0 > o1["v1_margin_n"],
        "perfect span efficiency saves less cruise drag than the current fins add":
            o1["maximum_induced_saving_n"] < o1["fin_drag_n"],
        "tip quarter chord is ahead of CG and tip trailing edge only slightly aft":
            yaw_geometry["tip_c4_arm_m"] < 0.0 < yaw_geometry["tip_te_arm_m"],
        "tip trailing-edge yaw arm is below one seventh of the V1 arm":
            0.0 < yaw_geometry["tip_te_fin_contribution_ratio"] < 1.0 / 7.0,
        "quarter-chord/CG crossing lies inside the high-loaded midspan region":
            0.50 < yaw_geometry["c4_cg_crossing_eta"] < 0.60,
        "symmetric VLM has less than 0.03 local-Cl margin to the generic screen":
            0.0 < span["peak_reserve"] < 0.03,
        "two more degrees of linear wash-in exceed the generic local-Cl screen":
            stall_distribution(twist_deg=5.0)["peak_reserve"] < 0.0,
        "moment-neutral ten-percent flap window lies inside the current elevon":
            config.ELEVON_ETA_IN < neutral["eta_in"]
            and neutral["eta_out"] < config.ELEVON_ETA_OUT
            and abs(neutral["yield_per_deg"]) < 1e-12,
        "forward-swept flap moment yield changes sign across the current elevon":
            flap_cm_yield(0.35, 0.50) < 0.0
            < flap_cm_yield(0.70, 0.90),
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 92)
    print("NF DESIGN GUIDE 2024 AUDIT - PART 5: WINGTIPS, DRAG, STALL AND FLAPS")
    print("=" * 92)
    source_hash = sha256(PDF)
    print(f"Source SHA-256: {source_hash}")
    print("NF scope: PDF pp. 270-303 and 308-316")

    print("\n1. CLEAN-POLAR DRAG DECOMPOSITION WITH V1 REFERENCE MASS [D on E]")
    print("   CD_profile=0.0136 is held outside cruise only as a sensitivity, not a polar.")
    print("   speed    CL      CDi(e=.85)  induced share   D_clean   max D saving to e=1")
    for speed_kmh in SPEEDS_KMH:
        state = level_flight_drag(speed_kmh)
        print(
            f"   {speed_kmh:5.0f}  {state['cl']:7.4f}   {state['cd_induced']:10.6f}"
            f"      {100*state['induced_fraction']:6.1f}%   {state['drag_n']:7.4f} N"
            f"       {state['maximum_induced_saving_n']:7.4f} N"
        )

    o1 = o1_drag_budget()
    print("\n2. CURRENT 95 km/h O1 DRAG BUDGET [D on E; not E2 acceptance]")
    print(
        f"   CLEAN-aero model at V1 mass: {o1['clean_drag_n']:.4f} N; "
        f"energy={o1['clean_energy_wh_km']:.3f} Wh/km"
    )
    print(
        f"   V1 fin estimate: delta CD0={o1['fin_delta_cd0']:.6f}; "
        f"delta D={o1['fin_drag_n']:.4f} N"
    )
    print(
        f"   V1 estimated total: {o1['v1_drag_n']:.4f} N; "
        f"energy={o1['v1_energy_wh_km']:.3f} Wh/km"
    )
    print(
        f"   O1 power-limited boundary: {o1['allowed_drag_n']:.4f} N; "
        f"CLEAN/V1 margins={o1['clean_margin_n']:+.4f}/{o1['v1_margin_n']:+.4f} N"
    )
    print(
        f"   Absolute upper-bound induced saving e=.85->1: "
        f"{o1['maximum_induced_saving_n']:.4f} N at cruise; "
        f"current fin drag is {o1['fin_drag_n']/o1['maximum_induced_saving_n']:.1f}x larger."
    )
    print(
        f"   Even at e=1, a new device must add less than delta CD0="
        f"{o1['maximum_breakeven_delta_cd0']:.6f} merely to improve the 95 km/h "
        "CLEAN aerodynamic model."
    )

    print("\n3. OPTIMISTIC WINGTIP-DEVICE CROSSOVER [I]")
    print("   Assumption: device raises e_span from 0.85 to the ideal 1.00.")
    print("   delta CD0     CL_cross    V_cross    relation to V1 stall")
    cases = list(DEVICE_DCD0_CASES) + [o1["fin_delta_cd0"]]
    for delta_cd0 in cases:
        state = crossover_state(delta_cd0)
        label = " (current fin drag)" if abs(delta_cd0-o1["fin_delta_cd0"]) < 1e-12 else ""
        relation = "below/unflyable" if state["cl"] > config.CL_MAX_WING else "above stall"
        print(
            f"   {delta_cd0:9.6f}   {state['cl']:8.4f}   "
            f"{state['speed_kmh']:7.2f} km/h   {relation}{label}"
        )

    yaw_geometry = wingtip_yaw_geometry()
    print("\n4. FORWARD-SWEPT WINGTIP YAW-ARM GEOMETRY [D]")
    print(
        f"   x_CG={yaw_geometry['cg_m']*1000:+.2f} mm; "
        f"current V1 fin x_AC={yaw_geometry['current_fin_ac_m']*1000:+.1f} mm; "
        f"arm={yaw_geometry['current_fin_arm_m']*1000:.1f} mm"
    )
    print(
        f"   Tip c/4 x={yaw_geometry['tip_c4_m']*1000:+.1f} mm -> "
        f"arm={yaw_geometry['tip_c4_arm_m']*1000:+.1f} mm "
        f"({100*yaw_geometry['tip_c4_fin_contribution_ratio']:+.1f}% of V1 fin contribution)"
    )
    print(
        f"   Tip TE x={yaw_geometry['tip_te_m']*1000:+.1f} mm -> "
        f"arm={yaw_geometry['tip_te_arm_m']*1000:+.1f} mm "
        f"({100*yaw_geometry['tip_te_fin_contribution_ratio']:+.1f}% of V1)"
    )
    print(
        f"   Same-area tip-TE fin would need {yaw_geometry['tip_te_area_multiplier']:.2f}x "
        f"area for the same isolated yaw contribution; matching x_AC requires "
        f"{yaw_geometry['aft_extension_from_tip_te_m']*1000:.1f} mm aft of the tip TE."
    )
    print(
        f"   Wing c/4 crosses the CG at eta={yaw_geometry['c4_cg_crossing_eta']:.3f} "
        f"(y={yaw_geometry['c4_cg_crossing_y_m']*1000:.1f} mm)."
    )

    span = stall_distribution()
    print("\n5. SYMMETRIC 45 km/h SPAN-LOAD SCREEN [I]")
    print(
        f"   required/achieved wing CL={span['target_cl']:.6f}/{span['achieved_cl']:.6f}; "
        f"alpha={span['alpha_deg']:.3f} deg"
    )
    print(
        f"   peak local cl={span['peak_local_cl']:.4f} at eta={span['peak_eta']:.3f}; "
        f"margin to generic 0.65 screen={span['peak_reserve']:.4f}; "
        f"peak x_c4-x_CG={span['peak_c4_relative_cg_m']*1000:+.1f} mm "
        "(positive aft)"
    )
    print("   eta      local cl   margin to 0.65   c/4 relative CG")
    eta = np.asarray(span["eta"])
    for target in (0.50, 0.60, 0.70, 0.80, 0.90, 0.95):
        eta_actual, local_cl = nearest_at(eta, np.asarray(span["local_cl"]), target)
        _, relative_cg = nearest_at(eta, np.asarray(span["c4_relative_cg_m"]), target)
        print(
            f"   {eta_actual:5.3f}     {local_cl:7.4f}       "
            f"{LOCAL_SECTION_CL_SCREEN-local_cl:+7.4f}          "
            f"{relative_cg*1000:+8.1f} mm"
        )
    print("\n   Linear-twist sensitivity at the same aircraft CL [I]")
    print("   tip twist      peak local cl    eta_peak    margin to 0.65")
    for twist_deg in (0.0, 2.0, 3.0, 4.0, 5.0):
        twist_state = stall_distribution(twist_deg=twist_deg)
        print(
            f"   {twist_deg:+7.1f} deg       {twist_state['peak_local_cl']:.4f}"
            f"         {twist_state['peak_eta']:.3f}        "
            f"{twist_state['peak_reserve']:+.4f}"
        )

    print("\n6. FLAP-MANAGEMENT SCREEN FOR THE CURRENT FORWARD SWEEP [I]")
    neutral = moment_neutral_flap_window()
    print("   Symmetric +1 deg incidence-equivalent command; Cm0 yield per degree.")
    print("   segment eta      area/side    delta Cm0/deg")
    segments = ((0.35, 0.50), (0.50, 0.70), (0.70, 0.90), (0.35, 0.90))
    for eta_in, eta_out in segments:
        surface = elevon_sizing.ElevonGeometry("audit", eta_in, eta_out)
        area = elevon_sizing.surface_geometry(surface)["area_m2"]
        print(
            f"   {eta_in:4.2f}-{eta_out:4.2f}       {area*1e4:7.1f} cm2    "
            f"{flap_cm_yield(eta_in, eta_out):+11.7f}"
        )
    print(
        f"   Moment-neutral {FLAP_WINDOW_ETA:.2f}-span window: "
        f"eta={neutral['eta_in']:.3f}-{neutral['eta_out']:.3f}, "
        f"center={neutral['eta_center']:.3f}."
    )
    print(
        "   The single 0.35-0.90 elevon combines both signs; two servos provide "
        "symmetric/differential mixing but no independent spanwise scheduling."
    )
    pitch = elevon_sizing.pitch_result(elevon_sizing.ARTICLE_1)
    compensation = pitch["wash_in_cm_per_deg"] / pitch["elevon_cm_per_deg"]
    print(
        f"   Linear trim exchange: removing 1 deg of current wash-in requires about "
        f"{compensation:.2f} deg additional symmetric elevon in this VLM."
    )
    print(
        f"   Ncrit-12 trim estimate: current +3 deg twist={pitch['trim_n12_deg']:+.2f} deg; "
        f"zero twist={pitch['trim_n12_deg'] + 3*compensation:+.2f} deg; "
        f"-2 deg washout={pitch['trim_n12_deg'] + 5*compensation:+.2f} deg [I]."
    )

    print("\n7. ROOT/TIP REYNOLDS CONTEXT [D on declared nu]")
    print("   speed      Re_root     Re_tip")
    for speed_kmh in SPEEDS_KMH:
        re = reynolds_numbers(speed_kmh)
        print(f"   {speed_kmh:5.0f}      {re['root']/1000:7.1f}k    {re['tip']/1000:7.1f}k")

    checks = validation_checks()
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"   [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
