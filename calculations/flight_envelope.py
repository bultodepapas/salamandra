#!/usr/bin/env python3
"""Article #1 manoeuvre and regulatory-reference gust-envelope screening.

This module separates three quantities that must never be conflated:

* manoeuvre limit load factors (+6/-3);
* ultimate structural loads (limit x 1.5); and
* a rigid-aircraft discrete-gust screen based on legacy 14 CFR 23.341.

The gust calculation is a traceability and sensitivity tool, not certification and
not a final dynamic-load prediction for this very-low-wing-loading printed UAV.  Its
linear lift model is explicitly flagged when the implied positive CL exceeds CLmax.
The negative aerodynamic stall boundary remains open until traceable negative-polar
evidence supplies CLmin.
"""
import argparse
from dataclasses import dataclass
from math import isclose, sqrt

from design_config import (
    ARTICLE_CLEAN_MASS_KG,
    ARTICLE_V1_MASS_KG,
    ARTICLE_V_NE_KMH,
    CL_MAX_WING,
    G0,
    INITIAL_SPEED_LIMIT_KMH,
    MAC,
    NEGATIVE_LIMIT_LOAD_FACTOR,
    POSITIVE_LIMIT_LOAD_FACTOR,
    RHO_SL,
    ULTIMATE_SAFETY_FACTOR,
    S,
    lift_coefficient,
    speed_mps,
    stall_speed,
)
import aero_contract

# Legacy Part 23 sea-level reference values: 50 ft/s at VC and 25 ft/s at VD.
REFERENCE_GUST_VC_MPS = 15.24
REFERENCE_GUST_VD_MPS = 7.62
MPS_PER_KNOT = 0.5144444444444445
PASCAL_PER_PSF = 47.88025898033584
METRE_PER_FOOT = 0.3048


@dataclass(frozen=True)
class EnvelopeCase:
    """Derived envelope properties for one aircraft mass."""

    name: str
    mass_kg: float
    wing_loading_pa: float
    stall_kmh: float
    manoeuvring_kmh: float
    mass_ratio: float
    gust_alleviation: float


def project_lift_curve_slope():
    """Return the released-wing CL-alpha [rad^-1] at the canonical mesh.

    Delegated to `aero_contract` so the mesh and the wash-in are the shared
    ones.  The former call hardcoded both, and passed a twist that a linear
    lifting-surface model cannot use: CL-alpha superposes and is a property of
    the planform alone.
    """
    return aero_contract.lift_curve_slope()


def wing_loading_pa(mass_kg, area=S):
    """Weight per wing area [N/m2]."""
    if mass_kg <= 0.0 or area <= 0.0:
        raise ValueError("mass and wing area must be positive")
    return mass_kg * G0 / area


def airplane_mass_ratio(
    mass_kg, lift_curve_slope, rho=RHO_SL, area=S, mean_chord=MAC
):
    """Legacy 14 CFR 23.341 mass ratio, expressed consistently in SI."""
    if lift_curve_slope <= 0.0 or rho <= 0.0 or mean_chord <= 0.0:
        raise ValueError("lift slope, density and mean chord must be positive")
    return 2.0 * wing_loading_pa(mass_kg, area) / (
        rho * mean_chord * lift_curve_slope * G0
    )


def gust_alleviation_factor(mass_ratio):
    """Legacy 14 CFR 23.341 gust alleviation factor K_g."""
    if mass_ratio <= 0.0:
        raise ValueError("airplane mass ratio must be positive")
    return 0.88 * mass_ratio / (5.3 + mass_ratio)


def gust_load_increment(
    mass_kg, speed, gust_velocity, lift_curve_slope, rho=RHO_SL, area=S
):
    """Rigid-aircraft normal-load increment Delta-n for SI inputs."""
    if speed <= 0.0 or gust_velocity < 0.0 or rho <= 0.0:
        raise ValueError("speed/density must be positive and gust non-negative")
    mu = airplane_mass_ratio(mass_kg, lift_curve_slope, rho, area)
    kg = gust_alleviation_factor(mu)
    return (
        kg * rho * speed * gust_velocity * lift_curve_slope
        / (2.0 * wing_loading_pa(mass_kg, area))
    )


def gust_load_increment_imperial_reference(
    mass_kg, speed, gust_velocity, lift_curve_slope, area=S
):
    """Independent unit conversion of the published 498-denominator formula."""
    kg = gust_alleviation_factor(
        airplane_mass_ratio(mass_kg, lift_curve_slope, RHO_SL, area)
    )
    speed_knots = speed / MPS_PER_KNOT
    gust_ft_s = gust_velocity / METRE_PER_FOOT
    loading_psf = wing_loading_pa(mass_kg, area) / PASCAL_PER_PSF
    return kg * gust_ft_s * speed_knots * lift_curve_slope / (498.0 * loading_psf)


def allowable_gust_velocity(
    mass_kg, speed, load_increment, lift_curve_slope, rho=RHO_SL, area=S
):
    """Invert the gust equation for the non-negative equivalent vertical gust [m/s]."""
    if load_increment < 0.0:
        raise ValueError("load increment magnitude must be non-negative")
    unit_increment = gust_load_increment(
        mass_kg, speed, 1.0, lift_curve_slope, rho, area
    )
    return load_increment / unit_increment


def positive_manoeuvre_boundary(mass_kg, speed, positive_limit=POSITIVE_LIMIT_LOAD_FACTOR):
    """Positive manoeuvre V-n boundary, limited by CLmax and structural n."""
    if positive_limit <= 1.0:
        raise ValueError("positive limit load factor must exceed one")
    return min(positive_limit, (speed / stall_speed(mass_kg)) ** 2)


def manoeuvring_speed(mass_kg, positive_limit=POSITIVE_LIMIT_LOAD_FACTOR):
    """Positive manoeuvring speed VA [m/s] from Vs*sqrt(n_limit)."""
    if positive_limit <= 1.0:
        raise ValueError("positive limit load factor must exceed one")
    return stall_speed(mass_kg) * sqrt(positive_limit)


def reference_gust_velocity(
    speed, vc, vd, gust_vc=REFERENCE_GUST_VC_MPS, gust_vd=REFERENCE_GUST_VD_MPS
):
    """Legacy sea-level gust schedule: constant to VC, linear from VC to VD."""
    if not 0.0 < vc < vd or speed <= 0.0 or speed > vd:
        raise ValueError("require positive speed <= VD and 0 < VC < VD")
    if gust_vc < 0.0 or gust_vd < 0.0 or gust_vd > gust_vc:
        raise ValueError("require 0 <= Ude(VD) <= Ude(VC)")
    if speed <= vc:
        return gust_vc
    fraction = (speed - vc) / (vd - vc)
    return gust_vc + fraction * (gust_vd - gust_vc)


def critical_reference_gust_speed(
    vc, vd, gust_vc=REFERENCE_GUST_VC_MPS, gust_vd=REFERENCE_GUST_VD_MPS
):
    """Speed [m/s] maximizing V*Ude(V) over the VC-to-VD segment."""
    if not 0.0 < vc < vd or not 0.0 <= gust_vd <= gust_vc:
        raise ValueError("invalid speed or gust schedule")
    slope = (gust_vc - gust_vd) / (vd - vc)
    if isclose(slope, 0.0):
        return vd
    intercept = gust_vc + slope * vc
    stationary = intercept / (2.0 * slope)
    return min(vd, max(vc, stationary))


def reference_gust_exceeds_limits(mass_kg, speed, lift_curve_slope):
    """Diagnostic: does the reference gust cross the declared limit loads?

    Reported, never asserted.  It answers an OPEN question (G11: dynamic gust
    response of a very-low-wing-loading printed UAV), and the answer changing
    is information, not a regression.
    """
    dn = gust_load_increment(
        mass_kg, speed, REFERENCE_GUST_VC_MPS, lift_curve_slope)
    return (1.0 + dn > POSITIVE_LIMIT_LOAD_FACTOR,
            1.0 - dn < NEGATIVE_LIMIT_LOAD_FACTOR,
            dn)


def build_case(name, mass_kg, lift_curve_slope):
    """Build the coupled manoeuvre/gust properties for an aircraft mass."""
    mu = airplane_mass_ratio(mass_kg, lift_curve_slope)
    return EnvelopeCase(
        name=name,
        mass_kg=mass_kg,
        wing_loading_pa=wing_loading_pa(mass_kg),
        stall_kmh=stall_speed(mass_kg) * 3.6,
        manoeuvring_kmh=manoeuvring_speed(mass_kg) * 3.6,
        mass_ratio=mu,
        gust_alleviation=gust_alleviation_factor(mu),
    )


def validation_checks(lift_curve_slope):
    """Return named mathematical, unit and project-contract checks."""
    mass = ARTICLE_CLEAN_MASS_KG
    vc = speed_mps(INITIAL_SPEED_LIMIT_KMH)
    vd = speed_mps(ARTICLE_V_NE_KMH)
    dn_si = gust_load_increment(
        mass, vc, REFERENCE_GUST_VC_MPS, lift_curve_slope
    )
    dn_imperial = gust_load_increment_imperial_reference(
        mass, vc, REFERENCE_GUST_VC_MPS, lift_curve_slope
    )
    inverse = allowable_gust_velocity(mass, vc, dn_si, lift_curve_slope)
    critical_speed = critical_reference_gust_speed(vc, vd)
    critical_gust = reference_gust_velocity(critical_speed, vc, vd)
    critical_dn = gust_load_increment(
        mass, critical_speed, critical_gust, lift_curve_slope
    )
    endpoint_dn = max(
        gust_load_increment(mass, vc, REFERENCE_GUST_VC_MPS, lift_curve_slope),
        gust_load_increment(mass, vd, REFERENCE_GUST_VD_MPS, lift_curve_slope),
    )
    return {
        "released-wing VLM lift slope is in the finite-wing range":
            3.5 < lift_curve_slope < 5.5,
        "gust alleviation factor is physical":
            0.0 < gust_alleviation_factor(
                airplane_mass_ratio(mass, lift_curve_slope)
            ) < 0.88,
        "SI equation agrees with published imperial form within 0.2 percent":
            abs(dn_si - dn_imperial) / dn_si < 0.002,
        "gust equation inverse round-trip is exact": isclose(
            inverse, REFERENCE_GUST_VC_MPS, rel_tol=1e-12
        ),
        "positive stall boundary equals one g at Vs": isclose(
            positive_manoeuvre_boundary(mass, stall_speed(mass)),
            1.0,
            rel_tol=1e-12,
        ),
        "VA identity reaches the positive structural limit": isclose(
            positive_manoeuvre_boundary(mass, manoeuvring_speed(mass)),
            POSITIVE_LIMIT_LOAD_FACTOR,
            rel_tol=1e-12,
        ),
        "interior gust maximum is not missed by endpoint-only checking":
            critical_dn >= endpoint_dn,
        # The former check here ASSERTED that the reference gust breaches the
        # declared limits.  A validation suite must assert correctness, never
        # the current state of an open question: if the design improved so the
        # breach disappeared, that check would have reported a failure for a
        # good outcome.  The breach is now a printed diagnostic (see
        # `reference_gust_exceeds_limits`) tracked under G11.
        "the initial operational cap is below the manoeuvring speed":
            speed_mps(INITIAL_SPEED_LIMIT_KMH) < manoeuvring_speed(mass),
        "the screening speeds bracket the manoeuvring speed":
            vc < manoeuvring_speed(mass) < vd,
        "ultimate loads are limit loads times 1.5":
            isclose(
                POSITIVE_LIMIT_LOAD_FACTOR * ULTIMATE_SAFETY_FACTOR, 9.0
            )
            and isclose(
                NEGATIVE_LIMIT_LOAD_FACTOR * ULTIMATE_SAFETY_FACTOR, -4.5
            ),
    }


def print_case(case, lift_curve_slope, vc, vd):
    """Print one auditable envelope case."""
    initial = speed_mps(INITIAL_SPEED_LIMIT_KMH)
    n_manoeuvre = positive_manoeuvre_boundary(case.mass_kg, initial)
    u_pos = allowable_gust_velocity(
        case.mass_kg,
        initial,
        POSITIVE_LIMIT_LOAD_FACTOR - 1.0,
        lift_curve_slope,
    )
    u_neg = allowable_gust_velocity(
        case.mass_kg,
        initial,
        1.0 - NEGATIVE_LIMIT_LOAD_FACTOR,
        lift_curve_slope,
    )
    print(f"\n{case.name}: {case.mass_kg*1000:.1f} g")
    print(
        f"  W/S={case.wing_loading_pa:.2f} N/m2  Vs={case.stall_kmh:.2f} km/h  "
        f"VA(+6)={case.manoeuvring_kmh:.2f} km/h"
    )
    weight = case.mass_kg * G0
    print(
        "  symmetric normal-force resultants: "
        f"limit {POSITIVE_LIMIT_LOAD_FACTOR*weight:+.1f}/"
        f"{NEGATIVE_LIMIT_LOAD_FACTOR*weight:+.1f} N; ultimate "
        f"{POSITIVE_LIMIT_LOAD_FACTOR*ULTIMATE_SAFETY_FACTOR*weight:+.1f}/"
        f"{NEGATIVE_LIMIT_LOAD_FACTOR*ULTIMATE_SAFETY_FACTOR*weight:+.1f} N"
    )
    print(
        f"  mu_g={case.mass_ratio:.3f}  K_g={case.gust_alleviation:.4f}  "
        f"positive manoeuvre boundary at the "
        f"{INITIAL_SPEED_LIMIT_KMH:.0f} km/h cap={n_manoeuvre:.2f} g "
        f"(VA={case.manoeuvring_kmh:.1f} km/h is ABOVE the cap: the cap is an "
        f"operational limit, not a Part 23 V_C)"
    )
    print(
        f"  inverse screen at the {INITIAL_SPEED_LIMIT_KMH:.0f} km/h cap: "
        f"Ude(+6)={u_pos:.2f} m/s, Ude(-3)={u_neg:.2f} m/s "
        f"-> negative limit controls"
    )
    for label, speed in (("cap screen", vc), ("V_NE screen", vd)):
        gust = reference_gust_velocity(speed, vc, vd)
        dn = gust_load_increment(
            case.mass_kg, speed, gust, lift_curve_slope
        )
        n_positive = 1.0 + dn
        cl_positive = n_positive * lift_coefficient(case.mass_kg, speed)
        validity = "NONLINEAR/STALL FLAG" if cl_positive > CL_MAX_WING else "linear"
        print(
            f"  {label}: V={speed*3.6:.1f} km/h, Ude={gust:.2f} m/s -> "
            f"n={n_positive:+.2f}/{1.0-dn:+.2f}, "
            f"implied CL+={cl_positive:.2f} ({validity})"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cl-min",
        type=float,
        default=None,
        help="optional negative CL limit; omitted until traceable polar data exist",
    )
    args = parser.parse_args()
    if args.cl_min is not None and args.cl_min >= 0.0:
        parser.error("--cl-min must be negative")

    lift_curve_slope = project_lift_curve_slope()
    vc = speed_mps(INITIAL_SPEED_LIMIT_KMH)
    vd = speed_mps(ARTICLE_V_NE_KMH)
    print("=" * 82)
    print("SALAMANDRA ARTICLE #1 - MANOEUVRE AND GUST-REFERENCE ENVELOPE")
    print("=" * 82)
    print(
        f"VLM CL_alpha={lift_curve_slope:.4f}/rad; limit loads "
        f"{POSITIVE_LIMIT_LOAD_FACTOR:+.1f}/{NEGATIVE_LIMIT_LOAD_FACTOR:+.1f} g; "
        f"ultimate loads "
        f"{POSITIVE_LIMIT_LOAD_FACTOR*ULTIMATE_SAFETY_FACTOR:+.1f}/"
        f"{NEGATIVE_LIMIT_LOAD_FACTOR*ULTIMATE_SAFETY_FACTOR:+.1f} g"
    )
    print(
        "Reference only: legacy Part 23 sea-level discrete gust 15.24 m/s at "
        f"the {INITIAL_SPEED_LIMIT_KMH:.0f} km/h operational-cap screen and "
        f"7.62 m/s at the {ARTICLE_V_NE_KMH:.0f} km/h V_NE screen.  These are "
        "SCREENING speeds: the cap is not a design cruising speed V_C, and VA "
        "sits above it for every released mass."
    )

    for case in (
        build_case("SALAMANDRA-CLEAN", ARTICLE_CLEAN_MASS_KG, lift_curve_slope),
        build_case("SALAMANDRA-V1 lower model", ARTICLE_V1_MASS_KG, lift_curve_slope),
    ):
        print_case(case, lift_curve_slope, vc, vd)

    critical_speed = critical_reference_gust_speed(vc, vd)
    critical_gust = reference_gust_velocity(critical_speed, vc, vd)
    print(
        f"\nReference gust V*U maximum: {critical_speed*3.6:.1f} km/h at "
        f"Ude={critical_gust:.2f} m/s."
    )
    if args.cl_min is None:
        print(
            "Negative aerodynamic stall branch: OPEN (CLmin unavailable; use "
            "--cl-min only with traceable negative-polar data)."
        )
    else:
        for name, mass in (
            ("CLEAN", ARTICLE_CLEAN_MASS_KG),
            ("V1", ARTICLE_V1_MASS_KG),
        ):
            v_neg = sqrt(
                2.0 * mass * G0 * abs(NEGATIVE_LIMIT_LOAD_FACTOR)
                / (RHO_SL * S * abs(args.cl_min))
            )
            print(
                f"Negative manoeuvre intersection {name}: "
                f"{v_neg*3.6:.1f} km/h for CLmin={args.cl_min:.3f}."
            )

    for case_name, case_mass in (("CLEAN", ARTICLE_CLEAN_MASS_KG),
                                 ("V1", ARTICLE_V1_MASS_KG)):
        over_pos, under_neg, dn = reference_gust_exceeds_limits(
            case_mass, vc, lift_curve_slope)
        print(
            f"Reference-gust diagnostic ({case_name}): dn={dn:+.2f} g -> "
            f"positive limit {'EXCEEDED' if over_pos else 'respected'}, "
            f"negative limit {'EXCEEDED' if under_neg else 'respected'} "
            "(open question, tracked as G11; reported, not asserted)."
        )

    print(
        "\nINTERPRETATION: +6/-3 are provisional MANOEUVRE LIMIT loads. +9/-4.5 "
        "are their ULTIMATE structural counterparts, not a later flight target."
    )
    print(
        "The full reference gust produces non-linear/stall flags and crosses the "
        "declared limits; it is a conservative mismatch flag, not an adopted design "
        "load. Dynamic gust modelling, negative-polar evidence and E9 flight data "
        "remain required."
    )

    checks = validation_checks(lift_curve_slope)
    print("\nVALIDATION CHECKS")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
