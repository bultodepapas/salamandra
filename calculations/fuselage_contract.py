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


SCHEMA_VERSION = 1
AUTHORITY = "[I]"
WARNING = "DRAFT - NOT FOR MANUFACTURE"
DEFAULT_FAMILY = "lifting_saddle"


@dataclass(frozen=True)
class EnvelopePolicy:
    """Provisional installation inflation used by the OML audit.

    The wall and clearance remain independent because a future CAD wall offset
    must not be mistaken for equipment/service clearance. The lens face is a
    deliberate aperture and receives no forward longitudinal inflation.
    """

    wall_mm: float = 1.2
    installation_clearance_mm: float = 1.0
    longitudinal_transition_mm: float = 20.0
    smooth_max_power: float = 8.0
    lens_face_component: str = "o4_camera"

    @property
    def radial_margin_mm(self) -> float:
        return self.wall_mm + self.installation_clearance_mm


@dataclass(frozen=True)
class FamilyDefinition:
    """Bounded styling law sampled by the NumPy geometry backend."""

    identifier: str
    display_name: str
    half_width_control_mm: tuple[float, ...]
    top_control_mm: tuple[float, ...]
    bottom_control_mm: tuple[float, ...]
    waist_z_control_mm: tuple[float, ...]
    exponent_control: tuple[float, ...]
    source: str = "I-28 revision 2 [I]"

    def __post_init__(self) -> None:
        lengths = {
            len(self.half_width_control_mm),
            len(self.top_control_mm),
            len(self.bottom_control_mm),
            len(self.waist_z_control_mm),
            len(self.exponent_control),
        }
        if lengths != {9}:
            raise ValueError("every OML family law must have nine controls")
        if min(self.half_width_control_mm) <= 0.0:
            raise ValueError("half-width controls must be positive")
        if min(self.top_control_mm) <= 0.0 or min(self.bottom_control_mm) <= 0.0:
            raise ValueError("dorsal and ventral controls must be positive")
        if not all(2.0 <= value <= 5.0 for value in self.exponent_control):
            raise ValueError("section exponents must remain in [2, 5]")


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


# These are styling priors, not released dimensions. Envelope contributions in
# fuselage_geometry are combined conservatively with these bases, so reducing a
# styling control cannot make a hard component disappear from the audit.
FAMILIES: tuple[FamilyDefinition, ...] = (
    FamilyDefinition(
        "minimum_almond",
        "A - minimum-area almond",
        (8.0, 14.0, 22.0, 27.0, 29.0, 35.0, 35.0, 23.0, 15.0),
        (9.0, 16.0, 22.0, 25.0, 21.0, 21.0, 22.0, 18.0, 15.0),
        (14.0, 13.0, 11.0, 10.0, 11.0, 15.0, 17.0, 17.0, 15.0),
        (-5.0, -1.0, 5.0, 6.0, 3.0, 1.0, 0.0, 0.0, 0.0),
        (2.4, 2.8, 3.4, 3.6, 3.4, 3.0, 2.8, 2.6, 2.4),
    ),
    FamilyDefinition(
        "lifting_saddle",
        "B - lifting saddle-body",
        (9.0, 19.0, 27.0, 32.0, 32.0, 42.0, 44.0, 27.0, 17.0),
        (10.0, 20.0, 25.0, 28.0, 23.0, 23.0, 24.0, 20.0, 16.0),
        (15.0, 14.0, 12.0, 11.0, 12.0, 17.0, 19.0, 18.0, 16.0),
        (-5.0, -1.0, 5.0, 6.0, 3.0, 1.0, 0.0, 0.0, 0.0),
        (2.5, 3.0, 3.6, 4.0, 3.7, 3.2, 3.0, 2.7, 2.5),
    ),
    FamilyDefinition(
        "serviceable_shoulder",
        "C - serviceable broad shoulder",
        (10.0, 23.0, 32.0, 37.0, 36.0, 46.0, 47.0, 31.0, 19.0),
        (11.0, 23.0, 28.0, 31.0, 26.0, 26.0, 27.0, 22.0, 18.0),
        (16.0, 15.0, 13.0, 12.0, 13.0, 18.0, 20.0, 19.0, 17.0),
        (-5.0, 0.0, 5.0, 6.0, 3.0, 1.0, 0.0, 0.0, 0.0),
        (2.7, 3.2, 3.9, 4.3, 4.0, 3.5, 3.2, 2.9, 2.6),
    ),
)
FAMILY_BY_ID = {family.identifier: family for family in FAMILIES}


# Central skeleton volumes owned by the body OML. Items intentionally installed
# inside the controlled wing (servos, ESC, GPS, receiver and pitot probe) stay
# under equipment_layout.section_limits and are not allowed to inflate the body.
BODY_ENVELOPE_COMPONENT_IDS: tuple[str, ...] = (
    "o4_camera",
    "o4_vtx",
    "battery_cradle",
    "nose_boom_tube",
    "fc",
    "pdb",
    "pitot_sensor",
    "buzzer",
    "motor",
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
