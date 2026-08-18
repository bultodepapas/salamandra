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
import numpy as np
from design_config import (
    G0,
    RHO_SL,
    ROOT_CHORD,
    STRUCTURAL_DESIGN_SPEED_KMH,
    TAPER,
    B,
    speed_mps,
)

ELEVON_CHORD_FRAC = 1.0 - 0.72
ETA_IN, ETA_OUT = 0.30, 0.90
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


def elevon_chord_avg(samples=200):
    """Mean elevon chord [m] over the 30--90 % semi-span interval."""
    if samples < 2:
        raise ValueError("at least two span samples are required")
    eta = np.linspace(ETA_IN, ETA_OUT, samples)
    local_chord = ROOT_CHORD * (1.0 - (1.0 - TAPER) * eta)
    return ELEVON_CHORD_FRAC * float(local_chord.mean())


def control_geometry():
    """Return mean chord, span and planform area of one elevon [SI]."""
    mean_chord = elevon_chord_avg()
    span = B / 2.0 * (ETA_OUT - ETA_IN)
    return mean_chord, span, span * mean_chord


def hinge_moment(ch, speed=STRUCTURAL_SPEED_MPS):
    """Aerodynamic hinge moment of one elevon [N*m]."""
    if ch < 0.0 or speed <= 0.0:
        raise ValueError("Ch must be non-negative and speed positive")
    mean_chord, _, area = control_geometry()
    q = 0.5 * RHO_SL * speed**2
    return q * area * mean_chord * ch


def servo_torque_nm(ch, speed=STRUCTURAL_SPEED_MPS):
    """Ideal torque demand per servo [N*m] before efficiency and safety factor."""
    return hinge_moment(ch, speed) * HORN_RADIUS_RATIO / N_SERVOS_PER_ELEVON


def nm_to_kgf_cm(torque_nm):
    """Convert N*m to kgf*cm."""
    return torque_nm / (G0 * 0.01)


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
        "one elevon area is 0.0220--0.0222 m2": 0.0220 < area < 0.0222,
        "worst hinge moment is 0.095--0.097 N*m":
            0.095 < hinge_moment(max(CH_RANGE), speed) < 0.097,
        "single actuator carries the complete elevon hinge moment": abs(
            servo_torque_nm(max(CH_RANGE), speed)
            - hinge_moment(max(CH_RANGE), speed)) < 1e-12,
        "MG90S exceeds the unfactored 180 km/h demand":
            MG90S_TORQUE_KGFCM / worst_ideal >= 1.8,
        "Article #1 Corona passes factored 180 km/h demand by at least 1.3x":
            CORONA_TORQUE_KGFCM / required >= 1.3,
    }
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
