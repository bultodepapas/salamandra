#!/usr/bin/env python3
"""Provisional parametric OML contract for Salamandra Article #1.

This module owns only fuselage-model parameters. Shared aircraft quantities stay
in ``design_config`` and installed component geometry stays in
``equipment_layout``. Keeping this module standard-library-only lets every
other calculation import the types even when the optional geometry stack is
unavailable.

All geometry produced from this contract is ``[I]`` and remains
``DRAFT - NOT FOR MANUFACTURE`` until OP-21/F2 and the physical gates close.
Coordinates are millimetres in aircraft axes: x aft, y starboard, z up.
"""
from __future__ import annotations

from dataclasses import dataclass, replace


SCHEMA_VERSION = 2
AUTHORITY = "[I]"
WARNING = "DRAFT - NOT FOR MANUFACTURE"
DEFAULT_FAMILY = "integrated_spindle"


@dataclass(frozen=True)
class EnvelopePolicy:
    """Provisional installation inflation used by the OML audit.

    The wall and clearance remain independent because a future CAD wall offset
    must not be mistaken for equipment/service clearance. The lens face is a
    deliberate aperture and receives no forward longitudinal inflation.
    """

    wall_mm: float = 1.2
    installation_clearance_mm: float = 1.0
    numerical_reserve_mm: float = 0.25
    nose_extension_mm: float = 22.0
    aft_recovery_mm: float = 35.0
    normal_exponent_max: float = 3.2
    maximum_area_root_band_mm: tuple[float, float] = (-115.0, 45.0)
    maximum_parallel_fraction: float = 0.08
    lens_face_component: str = "o4_camera"

    @property
    def radial_margin_mm(self) -> float:
        return self.wall_mm + self.installation_clearance_mm


@dataclass(frozen=True)
class FamilyDefinition:
    """Bounded styling law sampled by the NumPy geometry backend."""

    identifier: str
    display_name: str
    station_control_xi: tuple[float, ...]
    half_width_control_mm: tuple[float, ...]
    top_control_mm: tuple[float, ...]
    bottom_control_mm: tuple[float, ...]
    waist_z_control_mm: tuple[float, ...]
    exponent_control: tuple[float, ...]
    source: str = "I-28 revision 3 [I]"

    def __post_init__(self) -> None:
        lengths = {
            len(self.station_control_xi),
            len(self.half_width_control_mm),
            len(self.top_control_mm),
            len(self.bottom_control_mm),
            len(self.waist_z_control_mm),
            len(self.exponent_control),
        }
        if len(lengths) != 1 or next(iter(lengths)) < 7:
            raise ValueError("every OML family law must share at least seven controls")
        if self.station_control_xi[0] != 0.0 or self.station_control_xi[-1] != 1.0:
            raise ValueError("family stations must span normalized x=[0, 1]")
        if any(
            second <= first
            for first, second in zip(
                self.station_control_xi, self.station_control_xi[1:]
            )
        ):
            raise ValueError("family stations must be strictly increasing")
        if min(self.half_width_control_mm) <= 0.0:
            raise ValueError("half-width controls must be positive")
        if min(self.top_control_mm) <= 0.0 or min(self.bottom_control_mm) <= 0.0:
            raise ValueError("dorsal and ventral controls must be positive")
        if not all(2.0 <= value <= 3.2 for value in self.exponent_control):
            raise ValueError("section exponents must remain in [2.0, 3.2]")


@dataclass(frozen=True)
class OmlDesignVector:
    """Small set of bounded modifiers; station samples are derived outputs."""

    family: str = DEFAULT_FAMILY
    width_scale: float = 1.0
    dorsal_scale: float = 1.0
    ventral_scale: float = 1.0
    waist_shift_mm: float = 0.0
    tail_scale: float = 1.0

    def __post_init__(self) -> None:
        if self.family not in FAMILY_BY_ID:
            raise ValueError(f"unknown OML family {self.family!r}")
        for name in ("width_scale", "dorsal_scale", "ventral_scale", "tail_scale"):
            value = getattr(self, name)
            if not 0.85 <= value <= 1.20:
                raise ValueError(f"{name}={value} is outside [0.85, 1.20]")
        if not -5.0 <= self.waist_shift_mm <= 5.0:
            raise ValueError("waist_shift_mm is outside [-5, 5]")

    def perturbed(self, **changes: float | str) -> OmlDesignVector:
        return replace(self, **changes)


# Revision 3 global shape priors. Installed items are enforced only as sampled
# inequalities by fuselage_geometry; they are never pointwise-maxed into these
# laws. Each family grows continuously through the payload and reaches its sole
# dominant maximum in the wing-root load-transfer band.
FAMILIES: tuple[FamilyDefinition, ...] = (
    FamilyDefinition(
        "slender_spindle",
        "A - low-area integrated spindle",
        (0.0, 0.03, 0.06, 0.16, 0.27, 0.49, 0.62, 0.78, 0.90, 1.0),
        (5.0, 23.0, 44.0, 45.0, 46.0, 50.0, 52.0, 46.0, 33.0, 15.0),
        (5.0, 31.0, 49.0, 46.0, 39.0, 32.0, 30.0, 28.0, 26.0, 15.0),
        (5.0, 26.0, 30.0, 28.0, 24.0, 21.0, 22.0, 23.0, 25.0, 15.0),
        (-5.0, -4.0, 1.0, 4.0, 5.0, 4.0, 2.0, 1.0, 0.0, 0.0),
        (2.05, 2.10, 2.25, 2.55, 2.75, 2.85, 2.75, 2.55, 2.30, 2.10),
    ),
    FamilyDefinition(
        "integrated_spindle",
        "B - reference integrated spindle",
        (0.0, 0.03, 0.06, 0.16, 0.27, 0.49, 0.62, 0.78, 0.90, 1.0),
        (5.0, 25.0, 47.0, 53.0, 60.0, 70.0, 76.0, 60.0, 38.0, 16.0),
        (5.0, 34.0, 52.0, 48.0, 43.0, 39.0, 40.0, 34.0, 30.0, 16.0),
        (5.0, 28.0, 32.0, 30.0, 27.0, 27.0, 30.0, 28.0, 30.0, 16.0),
        (-5.0, -4.0, 1.0, 4.0, 5.0, 4.0, 2.0, 1.0, 0.0, 0.0),
        (2.05, 2.10, 2.30, 2.65, 2.85, 3.00, 2.85, 2.60, 2.35, 2.10),
    ),
    FamilyDefinition(
        "service_spindle",
        "C - service-volume integrated spindle",
        (0.0, 0.03, 0.06, 0.16, 0.27, 0.49, 0.62, 0.78, 0.90, 1.0),
        (5.0, 28.0, 50.0, 52.0, 54.0, 58.0, 60.0, 54.0, 38.0, 18.0),
        (5.0, 24.0, 47.0, 45.0, 41.0, 36.0, 34.0, 32.0, 25.0, 18.0),
        (5.0, 23.0, 30.0, 28.0, 25.0, 24.0, 26.0, 27.0, 23.0, 18.0),
        (-5.0, -4.0, 1.0, 4.0, 5.0, 4.0, 2.0, 1.0, 0.0, 0.0),
        (2.05, 2.15, 2.35, 2.70, 2.95, 3.10, 2.95, 2.70, 2.40, 2.15),
    ),
)
FAMILY_BY_ID = {family.identifier: family for family in FAMILIES}


# Central skeleton volumes owned by the body OML. Items intentionally installed
# inside the controlled wing (servos, ESC, GPS, receiver and pitot probe) stay
# under equipment_layout.section_limits and are not allowed to inflate the body.
BODY_ENVELOPE_COMPONENT_IDS: tuple[str, ...] = (
    "o4_camera",
    "o4_vtx",
    "battery_6s1p",
    "nose_boom_tube",
    "fc",
    "pdb",
    "pitot_sensor",
    "buzzer",
    "motor",
)

STRUCTURAL_CORRIDOR_COMPONENT_IDS: tuple[str, ...] = (
    "battery_cradle",
    "nose_boom_tube",
)

WING_INSTALLATION_COMPONENT_IDS: tuple[str, ...] = (
    "servo_left_406",
    "servo_right_406",
    "esc",
    "gps_mag",
    "receiver",
    "receiver_antenna",
    "pitot_probe_tube",
)


DEFAULT_POLICY = EnvelopePolicy()
DEFAULT_DESIGN = OmlDesignVector()


def validation_checks() -> dict[str, bool]:
    """Software-contract checks independent of NumPy and installed hardware."""
    identifiers = [family.identifier for family in FAMILIES]
    return {
        "three deliberately different families exist": len(FAMILIES) == 3,
        "family identifiers are unique": len(identifiers) == len(set(identifiers)),
        "default family is registered": DEFAULT_FAMILY in FAMILY_BY_ID,
        "central and wing installation ownership do not overlap": not (
            set(BODY_ENVELOPE_COMPONENT_IDS) & set(WING_INSTALLATION_COMPONENT_IDS)
        ),
        "body family is non-cylindrical by construction": all(
            len(set(family.half_width_control_mm)) > 4 for family in FAMILIES
        ),
        "installation margin separates wall and clearance": (
            DEFAULT_POLICY.wall_mm > 0.0
            and DEFAULT_POLICY.installation_clearance_mm > 0.0
            and DEFAULT_POLICY.numerical_reserve_mm > 0.0
        ),
        "rejected revision 2 family is unavailable": "lifting_saddle" not in FAMILY_BY_ID,
        "cradle is a structural corridor, not an OML-driving box": (
            "battery_cradle" in STRUCTURAL_CORRIDOR_COMPONENT_IDS
            and "battery_cradle" not in BODY_ENVELOPE_COMPONENT_IDS
        ),
        "actual battery envelope drives payload containment": (
            "battery_6s1p" in BODY_ENVELOPE_COMPONENT_IDS
        ),
        "all generated geometry remains provisional": AUTHORITY == "[I]",
    }


def main() -> None:
    print("=" * 78)
    print("SALAMANDRA PROVISIONAL FUSELAGE CONTRACT")
    print("=" * 78)
    for family in FAMILIES:
        print(f"  {family.identifier:24s} {family.display_name} {AUTHORITY}")
    print(
        f"\n  body-owned envelopes: {', '.join(BODY_ENVELOPE_COMPONENT_IDS)}"
    )
    print(
        f"  wing-owned installations: {', '.join(WING_INSTALLATION_COMPONENT_IDS)}"
    )
    print(f"  wall={DEFAULT_POLICY.wall_mm:.1f} mm + installation "
          f"clearance={DEFAULT_POLICY.installation_clearance_mm:.1f} mm [I]")
    print(f"\n  {WARNING}")
    checks = validation_checks()
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
