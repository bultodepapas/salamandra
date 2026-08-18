#!/usr/bin/env python3
"""Article #1 elevon span trade and first-prototype selection.

This module compares the retired 30--90 % half-span surface with the selected
35--90 % Article #1 surface.  It combines exact trapezoidal planform geometry,
thin-airfoil flap effectiveness, linear VLM pitch/roll derivatives, the 3-D
mass model and the hinge-moment proxy used by ``servo_torque.py``.

The results are screening calculations, not flight-envelope clearance.  Low-
Reynolds-number separation, hinge gaps, printed compliance, freeplay and
aeroelastic reversal remain E2/E5/G7 acceptance items.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import acos, degrees, pi, radians, sin

import numpy as np

import design_config
import equipment_layout
import servo_torque
from vlm_ala_volante import geom, solve

CM0_WING_N10 = +0.003258
CM0_WING_N12 = +0.002095
DESIGN_TWIST_DEG = design_config.DESIGN_TWIST_DEG   # released wash-in
VLM_NY = 80
VLM_NX = 6


@dataclass(frozen=True)
class ElevonGeometry:
    """Constant-chord-fraction control surface on each half-wing."""

    name: str
    eta_in: float
    eta_out: float
    chord_fraction: float = design_config.ELEVON_CHORD_FRACTION

    def __post_init__(self) -> None:
        if not 0.0 <= self.eta_in < self.eta_out <= 1.0:
            raise ValueError("elevon span fractions must satisfy 0 <= in < out <= 1")
        if not 0.0 < self.chord_fraction < 1.0:
            raise ValueError("elevon chord fraction must lie in (0, 1)")

    @property
    def inboard_m(self) -> float:
        return self.eta_in * design_config.HALF_SPAN

    @property
    def outboard_m(self) -> float:
        return self.eta_out * design_config.HALF_SPAN

    @property
    def span_m(self) -> float:
        return self.outboard_m - self.inboard_m


BASELINE = ElevonGeometry("retired 30--90 %", 0.30, 0.90)
ARTICLE_1 = ElevonGeometry(
    "Article #1 35--90 %",
    design_config.ELEVON_ETA_IN,
    design_config.ELEVON_ETA_OUT,
)


def thin_airfoil_flap_effectiveness(chord_fraction: float) -> float:
    """Ideal 2-D lift-effectiveness ratio for a plain trailing-edge flap.

    The thin-airfoil mapping uses ``x/c = (1-cos(theta))/2``.  This ideal
    factor deliberately excludes hinge-gap, viscosity and structural losses.
    """
    if not 0.0 < chord_fraction < 1.0:
        raise ValueError("flap chord fraction must lie in (0, 1)")
    theta_h = acos(2.0 * chord_fraction - 1.0)
    return 1.0 - (theta_h - sin(theta_h)) / pi


FLAP_EFFECTIVENESS = thin_airfoil_flap_effectiveness(
    design_config.ELEVON_CHORD_FRACTION
)


def surface_geometry(surface: ElevonGeometry) -> dict[str, float]:
    """Return span, area, MAC and hinge proxy for one surface in SI units.

    Both integrals are closed-form (`design_config.taper_integrals`): the chord
    law is linear, so the former 2001-point trapezoid rule bought nothing on
    the area and carried a small quadrature error on the quadratic hinge proxy.
    """
    area, hinge_proxy = design_config.taper_integrals(
        surface.inboard_m, surface.outboard_m, surface.chord_fraction)
    return {
        "span_m": surface.span_m,
        "area_m2": area,
        "mac_m": hinge_proxy / area,
        "hinge_proxy_m3": hinge_proxy,
    }


def _span_overlap_weights(g: dict, surface: ElevonGeometry) -> np.ndarray:
    """Fraction of each VLM span panel covered by the symmetric elevons."""
    lower = surface.inboard_m
    upper = surface.outboard_m
    weights: list[float] = []
    for first, second in g["panels"]:
        y0, y1 = sorted((float(first[1]), float(second[1])))
        overlap = 0.0
        for sign in (-1.0, 1.0):
            band0, band1 = sorted((sign * lower, sign * upper))
            overlap += max(0.0, min(y1, band1) - max(y0, band0))
        weights.append(overlap / (y1 - y0))
    return np.array(weights)


def cm0_wing(
    twist_deg: float,
    elevon_deg: float,
    surface: ElevonGeometry = ARTICLE_1,
) -> float:
    """Linear-VLM wing Cm at CL=0 for physical symmetric elevon deflection."""
    g = geom(
        design_config.B,
        design_config.S,
        design_config.TAPER,
        design_config.SWEEP_C4_DEG,
        0.0,
        ny=VLM_NY,
        nx=VLM_NX,
    )
    eta = np.abs(g["cps"][:, 1]) / design_config.HALF_SPAN
    coverage = _span_overlap_weights(g, surface)
    effectiveness = thin_airfoil_flap_effectiveness(surface.chord_fraction)
    g["eps"] = np.radians(
        twist_deg * eta + elevon_deg * effectiveness * coverage
    )
    cl0, cm0, _, _ = solve(g, 0.0)
    cl4, cm4, _, _ = solve(g, 4.0)
    dcm_dcl = (cm4 - cm0) / (cl4 - cl0)
    return float(cm0 - cl0 * dcm_dcl)


def pitch_result(surface: ElevonGeometry) -> dict[str, float]:
    """Return VLM pitch yield and Ncrit 10/12 neutral trim angles."""
    wash_in_yield = cm0_wing(1.0, 0.0, surface) - cm0_wing(0.0, 0.0, surface)
    elevon_yield = cm0_wing(0.0, 1.0, surface) - cm0_wing(0.0, 0.0, surface)
    cruise_cl = design_config.lift_coefficient(
        design_config.ARTICLE_V1_MASS_KG,
        design_config.speed_mps(design_config.CRUISE_SPEED_KMH),
    )
    required_cm0 = cruise_cl * design_config.STATIC_MARGIN

    def trim(profile_cm0: float) -> float:
        residual = required_cm0 - (
            profile_cm0 + DESIGN_TWIST_DEG * wash_in_yield
        )
        return residual / elevon_yield

    return {
        "wash_in_cm_per_deg": wash_in_yield,
        "elevon_cm_per_deg": elevon_yield,
        "cruise_cl": cruise_cl,
        "required_cm0": required_cm0,
        "trim_n10_deg": trim(CM0_WING_N10),
        "trim_n12_deg": trim(CM0_WING_N12),
    }


def _roll_coefficient(g: dict, strip_lift: np.ndarray) -> float:
    moment = float(np.sum(strip_lift * g["cps"][:, 1]))
    return moment / (0.5 * g["S"] * g["b"])


def roll_derivatives(surface: ElevonGeometry) -> dict[str, float]:
    """Return Cl_delta_a and Cl_p per radian from linear VLM."""
    g = geom(
        design_config.B,
        design_config.S,
        design_config.TAPER,
        design_config.SWEEP_C4_DEG,
        0.0,
        ny=VLM_NY,
        nx=VLM_NX,
    )
    coverage = _span_overlap_weights(g, surface)
    sign_y = np.sign(g["cps"][:, 1])
    test_delta = radians(1.0)
    effectiveness = thin_airfoil_flap_effectiveness(surface.chord_fraction)
    g["eps"] = test_delta * effectiveness * coverage * sign_y
    _, _, strip_lift, _ = solve(g, 0.0)
    cl_delta = _roll_coefficient(g, strip_lift) / test_delta

    # Positive dimensionless roll rate p_hat = p*b/(2V) produces the opposite
    # local incidence gradient; this convention gives the stabilizing Cl_p < 0.
    g["eps"] = -2.0 * g["cps"][:, 1] / design_config.B
    _, _, strip_lift, _ = solve(g, 0.0)
    cl_p = _roll_coefficient(g, strip_lift)
    return {"cl_delta_a_per_rad": cl_delta, "cl_p_per_rad": cl_p}


def _time_to_bank(bank_rad: float, steady_rate: float, time_constant: float) -> float:
    """Solve phi=p_ss*(t-tau*(1-exp(-t/tau))) by bisection."""
    if bank_rad <= 0.0 or steady_rate <= 0.0 or time_constant <= 0.0:
        raise ValueError("bank, steady rate and time constant must be positive")

    def bank_at(time_s: float) -> float:
        return steady_rate * (
            time_s - time_constant * (1.0 - np.exp(-time_s / time_constant))
        )

    lower = 0.0
    upper = max(bank_rad / steady_rate + 5.0 * time_constant, time_constant)
    while bank_at(upper) < bank_rad:
        upper *= 2.0
    for _ in range(80):
        middle = 0.5 * (lower + upper)
        if bank_at(middle) < bank_rad:
            lower = middle
        else:
            upper = middle
    return 0.5 * (lower + upper)


def roll_response(
    surface: ElevonGeometry,
    speed_kmh: float,
    differential_deg: float = 5.0,
) -> dict[str, float]:
    """Linear initial/steady roll response using the V1 3-D inertia model."""
    if speed_kmh <= 0.0 or differential_deg <= 0.0:
        raise ValueError("speed and differential deflection must be positive")
    derivatives = roll_derivatives(surface)
    layout, _ = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("v1"), clamp=True
    )
    ixx = layout.inertia_kg_m2()[0][0]
    speed = design_config.speed_mps(speed_kmh)
    q = design_config.dynamic_pressure(speed)
    delta = radians(differential_deg)
    control_moment = (
        q
        * design_config.S
        * design_config.B
        * derivatives["cl_delta_a_per_rad"]
        * delta
    )
    damping_per_rate = (
        q
        * design_config.S
        * design_config.B**2
        * (-derivatives["cl_p_per_rad"])
        / (2.0 * speed)
    )
    initial_acceleration = control_moment / ixx
    steady_rate = control_moment / damping_per_rate
    time_constant = ixx / damping_per_rate
    return {
        "ixx_kg_m2": ixx,
        "initial_accel_rad_s2": initial_acceleration,
        "steady_rate_rad_s": steady_rate,
        "time_constant_s": time_constant,
        "time_to_45_deg_s": _time_to_bank(radians(45.0), steady_rate, time_constant),
    }


def main() -> None:
    baseline_geometry = surface_geometry(BASELINE)
    selected_geometry = surface_geometry(ARTICLE_1)
    baseline_pitch = pitch_result(BASELINE)
    selected_pitch = pitch_result(ARTICLE_1)
    baseline_roll = roll_derivatives(BASELINE)
    selected_roll = roll_derivatives(ARTICLE_1)
    area_ratio = selected_geometry["area_m2"] / baseline_geometry["area_m2"]
    hinge_ratio = (
        selected_geometry["hinge_proxy_m3"]
        / baseline_geometry["hinge_proxy_m3"]
    )

    print("=" * 86)
    print("SALAMANDRA ARTICLE #1 ELEVON SIZING - ADR-0045 / I-27")
    print("=" * 86)
    print(
        f"Ideal plain-flap effectiveness tau={FLAP_EFFECTIVENESS:.4f} "
        f"for c_e/c={ARTICLE_1.chord_fraction:.2f} [D]"
    )
    print("\nGeometry per elevon")
    for surface, values in (
        (BASELINE, baseline_geometry),
        (ARTICLE_1, selected_geometry),
    ):
        print(
            f"  {surface.name:21s}: y={surface.inboard_m*1000:6.1f}.."
            f"{surface.outboard_m*1000:6.1f} mm  span={values['span_m']*1000:6.1f} mm  "
            f"area={values['area_m2']*1e4:6.1f} cm2  MAC_e={values['mac_m']*1000:5.1f} mm"
        )
    print(
        f"  Selected/baseline: area={area_ratio:.3f}, "
        f"hinge proxy integral(c_e^2 dy)={hinge_ratio:.3f}"
    )
    print(
        f"  Fixed root bridge={(ARTICLE_1.inboard_m-0.195)*1000:.1f} mm; "
        f"fixed tip={design_config.HALF_SPAN*1000-ARTICLE_1.outboard_m*1000:.1f} mm; "
        f"servo y={design_config.ELEVON_SERVO_STATION_M*1000:.2f} mm"
    )

    print("\nLinear-VLM control derivatives [D], physical deflection includes ideal tau")
    for surface, pitch, roll in (
        (BASELINE, baseline_pitch, baseline_roll),
        (ARTICLE_1, selected_pitch, selected_roll),
    ):
        print(
            f"  {surface.name:21s}: Cm_delta={pitch['elevon_cm_per_deg']:+.6f}/deg  "
            f"trim N10/N12={pitch['trim_n10_deg']:+.3f}/{pitch['trim_n12_deg']:+.3f} deg  "
            f"Cl_delta_a={roll['cl_delta_a_per_rad']:+.4f}/rad"
        )
    print(
        f"  Roll derivative retained="
        f"{selected_roll['cl_delta_a_per_rad']/baseline_roll['cl_delta_a_per_rad']:.3f}; "
        f"Cl_p={selected_roll['cl_p_per_rad']:+.4f}/rad"
    )

    print("\nSelected 5 deg differential linear response [D]/[E]")
    for speed_kmh in (45.0, 95.0):
        response = roll_response(ARTICLE_1, speed_kmh)
        print(
            f"  {speed_kmh:4.0f} km/h: initial={degrees(response['initial_accel_rad_s2']):6.0f} deg/s2  "
            f"steady={degrees(response['steady_rate_rad_s']):5.0f} deg/s  "
            f"tau={response['time_constant_s']:.3f} s  "
            f"t45={response['time_to_45_deg_s']:.3f} s"
        )

    required = servo_torque.required_catalog_torque_kgf_cm()
    print("\nStatic actuator and mass consequences [D]/[E]")
    print(
        f"  Hinge-moment proxy reduction={1.0-hinge_ratio:.1%}; "
        f"180 km/h catalog requirement={required:.3f} kgf*cm; "
        f"DS-939MG factored margin={servo_torque.CORONA_TORQUE_KGFCM/required:.2f}x"
    )
    print(
        f"  Moving printed mass estimate=22.5 g/elevon; balance allocation=27.0 g/elevon; "
        f"aircraft saving=6.0 g (balance only; fixed PETG bridge remains in the wing)."
    )

    checks = {
        "selected control span is 357.5 mm": abs(ARTICLE_1.span_m - 0.3575) < 1e-12,
        "selected moving area is 89--91 percent of baseline": 0.89 < area_ratio < 0.91,
        "selected hinge proxy is 87--90 percent of baseline": 0.87 < hinge_ratio < 0.90,
        "limiting Ncrit 12 trim remains inside +/-0.6 deg":
            abs(selected_pitch["trim_n12_deg"]) <= 0.6,
        "selected roll derivative retains at least 94 percent":
            selected_roll["cl_delta_a_per_rad"]
            / baseline_roll["cl_delta_a_per_rad"] >= 0.94,
        "selected roll damping derivative is stabilizing":
            selected_roll["cl_p_per_rad"] < 0.0,
        "Corona retains at least 1.5x factored static torque margin":
            servo_torque.CORONA_TORQUE_KGFCM / required >= 1.5,
    }
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
