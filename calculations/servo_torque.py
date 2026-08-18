#!/usr/bin/env python3
"""Elevon-servo hinge-moment requirement for Salamandra Article #1.

The aerodynamic hinge moment is

    H = q * S_control * c_control * Ch.

One servo actuates each elevon. A 1:1 servo/control-horn radius ratio is the
conservative CAD contract until linkage geometry is frozen. The selection
check includes 80 % linkage efficiency and a 1.5 torque safety factor.

All calculations use SI units internally. Catalog torque is reported in
kgf*cm; 1 N*m = 10.197 kgf*cm. Revision 2 corrects the former 1000x display
error that labelled kgf*cm values as gf*cm.
"""
from math import isclose

from design_config import (
    ELEVON_CHORD_FRACTION,
    ELEVON_ETA_IN,
    ELEVON_ETA_OUT,
    ELEVON_INBOARD_M,
    ELEVON_OUTBOARD_M,
    ELEVON_SPAN_M,
    KGF_STANDARD_GRAVITY,
    RHO_SL,
    STRUCTURAL_DESIGN_SPEED_KMH,
    speed_mps,
    taper_integrals,
)

ELEVON_CHORD_FRAC = ELEVON_CHORD_FRACTION
ETA_IN, ETA_OUT = ELEVON_ETA_IN, ELEVON_ETA_OUT
CH_RANGE = (0.01, 0.05)       # hinge-moment coefficient [E]
N_SERVOS_PER_ELEVON = 1
HORN_RADIUS_RATIO = 1.0       # servo horn / control horn [E], CAD upper bound
LINKAGE_EFFICIENCY = 0.80     # joints, horn alignment and compliance [E]
TORQUE_SAFETY_FACTOR = 1.50

# Lowest catalog torque used only as a comparison; the Article #1 Corona
# DS-939MG is 2.5 kgf*cm at 4.8 V (I-18 [M]).
MG90S_TORQUE_KGFCM = 1.80
CORONA_TORQUE_KGFCM = 2.50
STRUCTURAL_SPEED_MPS = speed_mps(STRUCTURAL_DESIGN_SPEED_KMH)
MAX_HINGE_COEFFICIENT = max(CH_RANGE)


def control_geometry():
    """Return aerodynamic mean chord, span and area of one elevon [SI].

    The aerodynamic mean chord is ``integral(c_e**2 dy) / S_e``. Thus
    ``S_e * c_bar_e`` is the exact tapered-surface hinge-moment reference.

    Both integrals come from ``design_config.taper_integrals`` in closed form.
    The former 1001-point trapezoid rule carried a 2.6e-8 relative error on the
    mean chord because ``c_e**2`` is quadratic, and it re-derived the chord law
    locally instead of reading the canonical one.
    """
    area, second = taper_integrals(
        ELEVON_INBOARD_M, ELEVON_OUTBOARD_M, ELEVON_CHORD_FRAC)
    return second / area, ELEVON_SPAN_M, area


def hinge_moment(ch, speed=STRUCTURAL_SPEED_MPS):
    """Aerodynamic hinge moment of one elevon [N*m]."""
    if ch < 0.0 or speed <= 0.0:
        raise ValueError("Ch must be non-negative and speed positive")
    mean_chord, _, area = control_geometry()
    q = 0.5 * RHO_SL * speed**2
    return q * area * mean_chord * ch


def servo_torque_nm(ch, speed=STRUCTURAL_SPEED_MPS,
                    horn_ratio=HORN_RADIUS_RATIO,
                    n_servos=N_SERVOS_PER_ELEVON):
    """Ideal torque demand per servo [N*m] before efficiency and safety factor.

    The lever arms are parameters, not baked-in constants: the ratio and the
    actuator count are exactly what a linkage revision changes, and the
    validation case below exercises both.
    """
    if horn_ratio <= 0.0 or n_servos < 1:
        raise ValueError("horn ratio must be positive and n_servos at least 1")
    return hinge_moment(ch, speed) * horn_ratio / n_servos


def nm_to_kgf_cm(torque_nm):
    """Convert N*m to kgf*cm.

    Uses standard gravity, which defines the kilogram-force, rather than the
    project's engineering G0: they are different physical constants and the
    former is exact by definition.
    """
    return torque_nm / (KGF_STANDARD_GRAVITY * 0.01)


def required_catalog_torque_kgf_cm(ch=MAX_HINGE_COEFFICIENT):
    """Minimum catalog torque after efficiency and safety factor."""
    ideal = servo_torque_nm(ch)
    return nm_to_kgf_cm(ideal) * TORQUE_SAFETY_FACTOR / LINKAGE_EFFICIENCY


def main():
    mean_chord, span, area = control_geometry()
    speed = speed_mps(STRUCTURAL_DESIGN_SPEED_KMH)
    print("=" * 74)
    print("SALAMANDRA ELEVON SERVO TORQUE - SI MODEL AND CATALOG CHECK")
    print("=" * 74)
    print(f"  Elevon mean chord={mean_chord*1000:.1f} mm, span={span*1000:.0f} mm, "
          f"area={area*1e4:.0f} cm2")
    print(f"  Structural sizing speed={speed*3.6:.0f} km/h; one servo/elevon; "
          f"horn ratio={HORN_RADIUS_RATIO:.2f}")

    print("\n  Aerodynamic hinge moment and ideal demand per servo")
    for ch in CH_RANGE:
        total = hinge_moment(ch, speed)
        per_servo = servo_torque_nm(ch, speed)
        print(f"    Ch={ch:.2f}: elevon={total*1000:.1f} mN*m; "
              f"servo={per_servo*1000:.1f} mN*m = "
              f"{nm_to_kgf_cm(per_servo):.3f} kgf*cm")

    worst_ideal = nm_to_kgf_cm(servo_torque_nm(max(CH_RANGE), speed))
    required = required_catalog_torque_kgf_cm()
    print("\n  Selection check")
    print(f"    Worst ideal demand={worst_ideal:.3f} kgf*cm")
    print(f"    Required catalog torque={required:.3f} kgf*cm "
          f"(SF={TORQUE_SAFETY_FACTOR:.2f}, linkage eta={LINKAGE_EFFICIENCY:.2f})")
    print(f"    MG90S 1.8 kgf*cm: ideal margin={MG90S_TORQUE_KGFCM/worst_ideal:.2f}x")
    print(f"    Article #1 Corona 2.5 kgf*cm: factored margin="
          f"{CORONA_TORQUE_KGFCM/required:.2f}x")
    print("    Static torque passes; backlash, holding stiffness, current and "
          "linkage freeplay remain independent acceptance gates.")

    checks = {
        "1 N*m converts to 10.19--10.20 kgf*cm":
            10.19 < nm_to_kgf_cm(1.0) < 10.20,
        "one elevon area is 0.0198--0.0200 m2": 0.0198 < area < 0.0200,
        "worst hinge moment is 0.085--0.087 N*m":
            0.085 < hinge_moment(max(CH_RANGE), speed) < 0.087,
        # Exercises the lever-arm algebra rather than restating the current
        # constants: doubling the actuators must halve the per-servo demand,
        # and halving the horn ratio must halve it again.
        "two actuators halve the per-servo torque": isclose(
            servo_torque_nm(max(CH_RANGE), speed, n_servos=2),
            0.5 * servo_torque_nm(max(CH_RANGE), speed, n_servos=1),
            rel_tol=1e-12),
        "halving the horn ratio halves the per-servo torque": isclose(
            servo_torque_nm(max(CH_RANGE), speed, horn_ratio=0.5),
            0.5 * servo_torque_nm(max(CH_RANGE), speed, horn_ratio=1.0),
            rel_tol=1e-12),
        "the released linkage puts the whole hinge moment on one servo":
            N_SERVOS_PER_ELEVON == 1 and isclose(HORN_RADIUS_RATIO, 1.0),
        "MG90S exceeds the unfactored 180 km/h demand":
            MG90S_TORQUE_KGFCM / worst_ideal >= 1.8,
        "Article #1 Corona passes factored 180 km/h demand by at least 1.5x":
            CORONA_TORQUE_KGFCM / required >= 1.5,
    }
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
