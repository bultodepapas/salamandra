#!/usr/bin/env python3
"""Three-dimensional component and mass-properties model for Salamandra.

This module is the geometric source for equipment packaging before an outer
mould line (OML) is drawn.  Every component has a mass, an oriented envelope,
a centre-of-mass position, movement bounds and evidence authority.  The model
computes aircraft mass, x/y/z centre of gravity, rectangular-box inertia,
cable/separation constraints and the battery station required to close the
released longitudinal-CG target.

Coordinates are millimetres: x positive aft, y starboard and z up; the origin
is the root quarter-chord at the wing centreline.  Mass is in grams.  Outputs
are derived [D] from a mixture of measured [M], estimated [E] and provisional
[I] inputs.  This is a packaging model, not released CAD.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, replace
from functools import cache
from itertools import pairwise
from math import atan2, cos, degrees, dist, hypot, isclose, radians, sin, sqrt
from pathlib import Path

import balance_cg
import battery_pack_layout
import design_config
import equipment_catalog
import mass_budget

Vec3 = tuple[float, float, float]
Matrix3 = tuple[Vec3, Vec3, Vec3]

# Manufacturer-maximum P42A packaging model [M]/[E], centralized in I-16.
P42A_MAX_LENGTH_MM, P42A_MAX_DIAMETER_MM = (
    battery_pack_layout.CELL_MAX_DIMENSIONS_MM["Molicel P42A"]
)
PACK_OUTER_WRAP_MM = battery_pack_layout.PVC_OUTER
PACK_NICKEL_HEIGHT_MM = battery_pack_layout.NICKEL
PACK_LEAD_LENGTH_MM = battery_pack_layout.LEAD_ADD
PACK_6S1P_CAD_ENVELOPE_MM = battery_pack_layout.reference_pack_cad_envelope(
    "6S1P", "P42A"
)



@cache
def target_cg_mm() -> float:
    """Longitudinal CG target [mm], re-derived through `aero_contract`."""
    return balance_cg.cg_target() * 1000.0

CG_TOLERANCE_MM = balance_cg.R_CG * 1000.0
CRADLE_INNER_WIDTH_MM = 68.0
CRADLE_INNER_HEIGHT_MM = 25.0
MIN_INSTALL_CLEARANCE_MM = 2.0
O4_COAX_LENGTH_MM = equipment_catalog.DJI_O4_COAX_LENGTH_MM
GPS_POWER_SEPARATION_MM = 100.0
PRIMARY_CG_ADJUSTER = "battery_6s1p"

ELEVON_HINGE_XC = design_config.ELEVON_HINGE_XC
SERVO_STATION_MM = design_config.ELEVON_SERVO_STATION_M * 1000.0
SERVO_BODY_SIZE_MM = (22.5, 24.6, 11.5)
SERVO_SURFACE_CLEARANCE_MM = 1.5
SERVO_MIN_PUSHROD_PROJECTION_MM = 20.0
SERVO_SEARCH_FORWARD_XC = 0.35
AIRFOIL_DIRECTORY = Path(__file__).resolve().parent.parent / "geometry" / "airfoils"
AIRFOIL_STATIONS = (
    (0.0, "salamandra-root-r1.dat"),
    (130.0, "salamandra-r1-y130.dat"),
    (195.0, "salamandra-r1-y195.dat"),
    (325.0, "salamandra-r1-y325.dat"),
    (347.0, "salamandra-r1-y347.dat"),
    (488.0, "salamandra-r1-y488.dat"),
    (498.0, "salamandra-r1-y498.dat"),
    (585.0, "salamandra-r1-y585.dat"),
    (650.0, "salamandra-tip-r1.dat"),
)


def _identity() -> Matrix3:
    return ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def _matmul(a: Matrix3, b: Matrix3) -> Matrix3:
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
        for i in range(3)
    )  # type: ignore[return-value]


def _transpose(matrix: Matrix3) -> Matrix3:
    return tuple(
        tuple(matrix[j][i] for j in range(3)) for i in range(3)
    )  # type: ignore[return-value]


def _rotation_matrix(orientation_deg: Vec3) -> Matrix3:
    """Return Rz(yaw) @ Ry(pitch) @ Rx(roll)."""
    roll, pitch, yaw = (radians(value) for value in orientation_deg)
    rx: Matrix3 = (
        (1.0, 0.0, 0.0),
        (0.0, cos(roll), -sin(roll)),
        (0.0, sin(roll), cos(roll)),
    )
    ry: Matrix3 = (
        (cos(pitch), 0.0, sin(pitch)),
        (0.0, 1.0, 0.0),
        (-sin(pitch), 0.0, cos(pitch)),
    )
    rz: Matrix3 = (
        (cos(yaw), -sin(yaw), 0.0),
        (sin(yaw), cos(yaw), 0.0),
        (0.0, 0.0, 1.0),
    )
    return _matmul(_matmul(rz, ry), rx)


@dataclass(frozen=True)
class Bounds3D:
    """Allowed centre-position box, in millimetres."""

    minimum_mm: Vec3
    maximum_mm: Vec3

    def __post_init__(self) -> None:
        if any(low > high for low, high in zip(self.minimum_mm, self.maximum_mm)):
            raise ValueError("position-bound minimum exceeds maximum")

    @classmethod
    def fixed(cls, position_mm: Vec3) -> Bounds3D:
        return cls(position_mm, position_mm)

    def contains(self, position_mm: Vec3, tolerance: float = 1e-9) -> bool:
        return all(
            low - tolerance <= value <= high + tolerance
            for value, low, high in zip(
                position_mm, self.minimum_mm, self.maximum_mm
            )
        )

    def axis_span(self, axis: int) -> float:
        return self.maximum_mm[axis] - self.minimum_mm[axis]


@dataclass(frozen=True)
class Component3D:
    """One physical item or explicit unresolved mass allocation."""

    identifier: str
    label: str
    category: str
    mass_g: float
    size_mm: Vec3
    position_mm: Vec3
    bounds: Bounds3D
    authority: str
    source: str
    orientation_deg: Vec3 = (0.0, 0.0, 0.0)
    mass_sigma_g: float = 0.0
    position_sigma_mm: Vec3 = (0.0, 0.0, 0.0)
    budgeted: bool = True
    reserve: bool = False
    collidable: bool = True
    view_direction: Vec3 | None = None

    def __post_init__(self) -> None:
        if not self.identifier or any(char.isspace() for char in self.identifier):
            raise ValueError("component identifier must be non-empty and whitespace-free")
        if self.mass_g <= 0.0:
            raise ValueError(f"{self.identifier}: mass must be positive")
        if any(value <= 0.0 for value in self.size_mm):
            raise ValueError(f"{self.identifier}: envelope dimensions must be positive")
        if self.authority not in {"[M]", "[D]", "[E]", "[I]", "[D]/[E]"}:
            raise ValueError(f"{self.identifier}: invalid authority {self.authority}")
        if self.mass_sigma_g < 0.0 or any(
            value < 0.0 for value in self.position_sigma_mm
        ):
            raise ValueError(f"{self.identifier}: uncertainty cannot be negative")
        if self.view_direction is not None and not isclose(
            sqrt(sum(value**2 for value in self.view_direction)),
            1.0,
            abs_tol=1e-12,
        ):
            raise ValueError(f"{self.identifier}: view direction must be a unit vector")
        if not self.bounds.contains(self.position_mm):
            raise ValueError(f"{self.identifier}: reference position is outside bounds")

    def moved(self, position_mm: Vec3) -> Component3D:
        if not self.bounds.contains(position_mm):
            raise ValueError(
                f"{self.identifier}: position {position_mm} outside "
                f"{self.bounds.minimum_mm}..{self.bounds.maximum_mm}"
            )
        return replace(self, position_mm=position_mm)

    def rotation_matrix(self) -> Matrix3:
        if self.orientation_deg == (0.0, 0.0, 0.0):
            return _identity()
        return _rotation_matrix(self.orientation_deg)

    def aabb(self) -> tuple[Vec3, Vec3]:
        """World-axis bounding box of the oriented rectangular envelope."""
        rotation = self.rotation_matrix()
        half = tuple(value / 2.0 for value in self.size_mm)
        world_half = tuple(
            sum(abs(rotation[i][j]) * half[j] for j in range(3))
            for i in range(3)
        )
        minimum = tuple(
            self.position_mm[i] - world_half[i] for i in range(3)
        )
        maximum = tuple(
            self.position_mm[i] + world_half[i] for i in range(3)
        )
        return minimum, maximum  # type: ignore[return-value]

    def inertia_at_own_cg_g_mm2(self) -> Matrix3:
        """Oriented cuboid inertia tensor about the component CG."""
        dx, dy, dz = self.size_mm
        principal: Matrix3 = (
            (self.mass_g * (dy**2 + dz**2) / 12.0, 0.0, 0.0),
            (0.0, self.mass_g * (dx**2 + dz**2) / 12.0, 0.0),
            (0.0, 0.0, self.mass_g * (dx**2 + dy**2) / 12.0),
        )
        rotation = self.rotation_matrix()
        return _matmul(_matmul(rotation, principal), _transpose(rotation))


@dataclass(frozen=True)
class ServoPlacement:
    """Derived fixed servo station after section-fit and linkage checks."""

    y_mm: float
    x_fraction: float
    position_mm: Vec3
    pushrod_projection_mm: float
    minimum_surface_clearance_mm: float


@dataclass(frozen=True)
class LinkConstraint:
    name: str
    first: str
    second: str
    maximum_mm: float
    authority: str


@dataclass(frozen=True)
class SeparationConstraint:
    name: str
    first: str
    second: str
    minimum_mm: float
    authority: str


@dataclass(frozen=True)
class Layout3D:
    components: tuple[Component3D, ...]
    links: tuple[LinkConstraint, ...] = ()
    separations: tuple[SeparationConstraint, ...] = ()
    variant: str = "CLEAN"

    def __post_init__(self) -> None:
        identifiers = [component.identifier for component in self.components]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("component identifiers must be unique")
        known = set(identifiers)
        for constraint in (*self.links, *self.separations):
            if constraint.first not in known or constraint.second not in known:
                raise ValueError(f"{constraint.name}: unknown component reference")

    def component(self, identifier: str) -> Component3D:
        for component in self.components:
            if component.identifier == identifier:
                return component
        raise KeyError(identifier)

    def moved(self, identifier: str, position_mm: Vec3) -> Layout3D:
        replacement = self.component(identifier).moved(position_mm)
        return replace(
            self,
            components=tuple(
                replacement if item.identifier == identifier else item
                for item in self.components
            ),
        )

    def selected(self, budgeted_only: bool = False) -> tuple[Component3D, ...]:
        if not budgeted_only:
            return self.components
        return tuple(component for component in self.components if component.budgeted)

    def mass_g(self, budgeted_only: bool = False) -> float:
        return sum(
            component.mass_g for component in self.selected(budgeted_only)
        )

    def cg_mm(self, budgeted_only: bool = False) -> Vec3:
        components = self.selected(budgeted_only)
        total = sum(component.mass_g for component in components)
        if total <= 0.0:
            raise ValueError("layout mass must be positive")
        return tuple(
            sum(component.mass_g * component.position_mm[axis]
                for component in components) / total
            for axis in range(3)
        )  # type: ignore[return-value]

    def inertia_kg_m2(self, budgeted_only: bool = False) -> Matrix3:
        """Full assembly tensor at its CG, including parallel-axis terms."""
        components = self.selected(budgeted_only)
        cg = self.cg_mm(budgeted_only)
        tensor = [[0.0 for _ in range(3)] for _ in range(3)]
        for component in components:
            own = component.inertia_at_own_cg_g_mm2()
            offset = tuple(
                component.position_mm[axis] - cg[axis] for axis in range(3)
            )
            r2 = sum(value**2 for value in offset)
            for row in range(3):
                for column in range(3):
                    kronecker = 1.0 if row == column else 0.0
                    parallel = component.mass_g * (
                        r2 * kronecker - offset[row] * offset[column]
                    )
                    tensor[row][column] += own[row][column] + parallel
        return tuple(
            tuple(value * 1e-9 for value in row) for row in tensor
        )  # type: ignore[return-value]

    def cg_uncertainty_rss_mm(self) -> Vec3:
        """First-order 1-sigma CG uncertainty from declared input sigmas."""
        total = self.mass_g()
        cg = self.cg_mm()
        variance = [0.0, 0.0, 0.0]
        for component in self.components:
            for axis in range(3):
                mass_term = (
                    (component.position_mm[axis] - cg[axis])
                    / total
                    * component.mass_sigma_g
                )
                position_term = (
                    component.mass_g / total
                    * component.position_sigma_mm[axis]
                )
                variance[axis] += mass_term**2 + position_term**2
        return tuple(sqrt(value) for value in variance)  # type: ignore[return-value]

    def link_results(self) -> tuple[tuple[LinkConstraint, float, bool], ...]:
        return tuple(
            (
                link,
                dist(
                    self.component(link.first).position_mm,
                    self.component(link.second).position_mm,
                ),
                dist(
                    self.component(link.first).position_mm,
                    self.component(link.second).position_mm,
                ) <= link.maximum_mm + 1e-9,
            )
            for link in self.links
        )

    def separation_results(
        self,
    ) -> tuple[tuple[SeparationConstraint, float, bool], ...]:
        return tuple(
            (
                separation,
                dist(
                    self.component(separation.first).position_mm,
                    self.component(separation.second).position_mm,
                ),
                dist(
                    self.component(separation.first).position_mm,
                    self.component(separation.second).position_mm,
                ) + 1e-9 >= separation.minimum_mm,
            )
            for separation in self.separations
        )

    def collisions(self) -> tuple[tuple[str, str], ...]:
        collidable = [item for item in self.components if item.collidable]
        collisions: list[tuple[str, str]] = []
        for index, first in enumerate(collidable):
            first_min, first_max = first.aabb()
            for second in collidable[index + 1:]:
                second_min, second_max = second.aabb()
                overlap = all(
                    first_min[axis] < second_max[axis] - 1e-9
                    and second_min[axis] < first_max[axis] - 1e-9
                    for axis in range(3)
                )
                if overlap:
                    collisions.append((first.identifier, second.identifier))
        return tuple(collisions)


def _strip_centroid(
    y_start_m: float,
    y_end_m: float,
    chord_fraction: float,
    samples: int = 400,
) -> tuple[float, float]:
    """Area-weighted x/y centroid of a half-wing span strip."""
    if not 0.0 <= y_start_m < y_end_m <= design_config.HALF_SPAN:
        raise ValueError("invalid half-wing strip")
    if not 0.0 <= chord_fraction <= 1.0:
        raise ValueError("chord fraction must be in [0, 1]")
    dy = (y_end_m - y_start_m) / samples
    area = moment_x = moment_y = 0.0
    for index in range(samples):
        y = y_start_m + (index + 0.5) * dy
        chord = design_config.chord(y)
        x = design_config.x_le(y) + chord_fraction * chord
        strip_area = chord * dy
        area += strip_area
        moment_x += strip_area * x
        moment_y += strip_area * y
    return moment_x / area * 1000.0, moment_y / area * 1000.0


@cache
def _load_airfoil(filename: str) -> tuple[tuple[float, float], ...]:
    """Load one released r1 station profile from the repository."""
    path = AIRFOIL_DIRECTORY / filename
    points: list[tuple[float, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) != 2:
            continue
        try:
            points.append((float(fields[0]), float(fields[1])))
        except ValueError:
            continue
    if len(points) < 20:
        raise ValueError(f"airfoil file has too few coordinate rows: {path}")
    return tuple(points)


def _airfoil_limits(
    points: tuple[tuple[float, float], ...], x_fraction: float
) -> tuple[float, float]:
    """Interpolate normalized lower and upper ordinates at one x/c."""
    leading_edge = min(range(len(points)), key=lambda index: points[index][0])

    def interpolate(branch: tuple[tuple[float, float], ...]) -> float:
        ordered = sorted(branch)
        for first, second in pairwise(ordered):
            x0, y0 = first
            x1, y1 = second
            if x0 <= x_fraction <= x1 and x1 > x0:
                weight = (x_fraction - x0) / (x1 - x0)
                return y0 + weight * (y1 - y0)
        return min(ordered, key=lambda point: abs(point[0] - x_fraction))[1]

    first = interpolate(points[:leading_edge + 1])
    second = interpolate(points[leading_edge:])
    return min(first, second), max(first, second)


def section_limits(y_mm: float, x_fraction: float) -> tuple[float, float]:
    """Return interpolated r1 lower/upper ordinates for a span station."""
    if not 0.0 <= y_mm <= design_config.HALF_SPAN * 1000.0:
        raise ValueError("span station is outside the half-wing")
    if not 0.0 <= x_fraction <= 1.0:
        raise ValueError("chord fraction must be in [0, 1]")

    for station_mm, filename in AIRFOIL_STATIONS:
        if isclose(y_mm, station_mm, abs_tol=1e-12):
            return _airfoil_limits(_load_airfoil(filename), x_fraction)
    for first, second in pairwise(AIRFOIL_STATIONS):
        y0, filename0 = first
        y1, filename1 = second
        if y0 <= y_mm <= y1:
            lower0, upper0 = _airfoil_limits(
                _load_airfoil(filename0), x_fraction
            )
            lower1, upper1 = _airfoil_limits(
                _load_airfoil(filename1), x_fraction
            )
            weight = (y_mm - y0) / (y1 - y0)
            return (
                lower0 + weight * (lower1 - lower0),
                upper0 + weight * (upper1 - upper0),
            )
    raise RuntimeError("airfoil station interpolation failed")


def _servo_vertical_interval(y_mm: float, x_fraction: float) -> tuple[float, float]:
    """Allowed servo-centre z interval across the complete body footprint."""
    chord_mm = design_config.chord(y_mm / 1000.0) * 1000.0
    body_length_mm, _, body_height_mm = SERVO_BODY_SIZE_MM
    half_fraction = body_length_mm / (2.0 * chord_mm)
    lower_centres: list[float] = []
    upper_centres: list[float] = []
    for index in range(21):
        fraction = x_fraction - half_fraction + 2.0 * half_fraction * index / 20.0
        lower, upper = section_limits(y_mm, fraction)
        lower_centres.append(
            lower * chord_mm
            + SERVO_SURFACE_CLEARANCE_MM
            + body_height_mm / 2.0
        )
        upper_centres.append(
            upper * chord_mm
            - SERVO_SURFACE_CLEARANCE_MM
            - body_height_mm / 2.0
        )
    return max(lower_centres), min(upper_centres)


def _servo_candidate_feasible(y_mm: float, x_fraction: float) -> bool:
    chord_mm = design_config.chord(y_mm / 1000.0) * 1000.0
    if (
        x_fraction < SERVO_SEARCH_FORWARD_XC
        or (ELEVON_HINGE_XC - x_fraction) * chord_mm
        < SERVO_MIN_PUSHROD_PROJECTION_MM
    ):
        return False
    lower_centre, upper_centre = _servo_vertical_interval(y_mm, x_fraction)
    return lower_centre <= upper_centre


@cache
def solve_servo_placement(y_mm: float) -> ServoPlacement:
    """Place a flat servo as far aft as thickness and linkage permit.

    The servo body is held horizontal.  The search maximizes x/c, shortening
    the projected pushrod, while retaining the declared skin/cavity clearance
    over the complete rectangular footprint and a minimum mechanical run to
    the fixed x/c=0.72 hinge.  Its result is a fixed design station.
    """
    chord_mm = design_config.chord(y_mm / 1000.0) * 1000.0
    aft_limit = ELEVON_HINGE_XC - SERVO_MIN_PUSHROD_PROJECTION_MM / chord_mm
    best: tuple[float, float, float] | None = None
    samples = 5000
    for index in range(samples + 1):
        fraction = (
            SERVO_SEARCH_FORWARD_XC
            + (aft_limit - SERVO_SEARCH_FORWARD_XC) * index / samples
        )
        lower_centre, upper_centre = _servo_vertical_interval(y_mm, fraction)
        if lower_centre <= upper_centre:
            best = (fraction, lower_centre, upper_centre)
    if best is None:
        raise RuntimeError(f"servo does not fit released section at y={y_mm:.1f} mm")

    fraction, lower_centre, upper_centre = best
    z_centre = 0.5 * (lower_centre + upper_centre)
    x_mm = (
        design_config.x_le(y_mm / 1000.0)
        + fraction * design_config.chord(y_mm / 1000.0)
    ) * 1000.0
    body_length_mm, _, body_height_mm = SERVO_BODY_SIZE_MM
    half_fraction = body_length_mm / (2.0 * chord_mm)
    minimum_clearance = float("inf")
    for index in range(21):
        sample_fraction = (
            fraction - half_fraction + 2.0 * half_fraction * index / 20.0
        )
        lower, upper = section_limits(y_mm, sample_fraction)
        minimum_clearance = min(
            minimum_clearance,
            z_centre - body_height_mm / 2.0 - lower * chord_mm,
            upper * chord_mm - z_centre - body_height_mm / 2.0,
        )
    return ServoPlacement(
        y_mm=y_mm,
        x_fraction=fraction,
        position_mm=(x_mm, y_mm, z_centre),
        pushrod_projection_mm=(ELEVON_HINGE_XC - fraction) * chord_mm,
        minimum_surface_clearance_mm=minimum_clearance,
    )


def _component(
    identifier: str,
    label: str,
    category: str,
    mass_g: float,
    size_mm: Vec3,
    position_mm: Vec3,
    authority: str,
    source: str,
    *,
    bounds: Bounds3D | None = None,
    orientation_deg: Vec3 = (0.0, 0.0, 0.0),
    mass_sigma_g: float = 0.0,
    position_sigma_mm: Vec3 = (0.0, 0.0, 0.0),
    budgeted: bool = True,
    reserve: bool = False,
    collidable: bool = True,
    view_direction: Vec3 | None = None,
) -> Component3D:
    return Component3D(
        identifier=identifier,
        label=label,
        category=category,
        mass_g=mass_g,
        size_mm=size_mm,
        position_mm=position_mm,
        bounds=bounds or Bounds3D.fixed(position_mm),
        authority=authority,
        source=source,
        orientation_deg=orientation_deg,
        mass_sigma_g=mass_sigma_g,
        position_sigma_mm=position_sigma_mm,
        budgeted=budgeted,
        reserve=reserve,
        collidable=collidable,
        view_direction=view_direction,
    )


def _mass_rows() -> dict[str, float]:
    rows, totals = mass_budget.build("all_petg")
    if not isclose(
        totals["auw"], design_config.ARTICLE_CLEAN_MASS_KG * 1000.0,
        abs_tol=1e-8,
    ):
        raise RuntimeError("mass-budget default no longer matches design_config")
    return {row["part"]: row["m"] for row in rows}


@dataclass(frozen=True)
class CoupledPackagingSolution:
    """Converged V1 mass/balance/forward-packaging solution [D]/[E]/[I]."""

    layout: Layout3D
    required_battery_x_mm: float
    nose_extension_mm: float
    forward_extent_mm: float
    aft_extent_mm: float
    central_carrier_length_mm: float
    added_support_mass_g: float
    iterations: int


def reference_components(variant: str = "clean") -> tuple[Component3D, ...]:
    """Return the component-level Article #1 packaging candidate."""
    variant_key = variant.lower()
    if variant_key not in {"clean", "v1"}:
        raise ValueError("variant must be 'clean' or 'v1'")
    masses = _mass_rows()
    solved = balance_cg.solve_reference_layout()
    bay_fwd_mm = solved["bay_fwd"] * 1000.0
    bay_aft_mm = solved["bay_aft"] * 1000.0
    camera_station_mm = (
        bay_fwd_mm + balance_cg.CAMERA_FROM_BAY_FWD * 1000.0
    )

    core_x, _ = _strip_centroid(0.0, 0.195, 0.50)
    panel_x, panel_y = _strip_centroid(0.195, 0.585, 0.50)
    tip_x, tip_y = _strip_centroid(0.585, 0.650, 0.50)
    elevon_x, elevon_y = _strip_centroid(
        design_config.ELEVON_INBOARD_M,
        design_config.ELEVON_OUTBOARD_M,
        0.5 * (design_config.ELEVON_HINGE_XC + 1.0),
    )

    # Preserve the released 37.4 g boom+cradle allocation exactly.  The beam
    # calculation gives 22.39 g for the tube; the 0.01 g difference is merely
    # display rounding in that allocation, not a separate physical component.
    tube_mass_g = masses["boom"] - balance_cg.CRADLE_MASS * 1000.0
    tube_start_mm = bay_fwd_mm
    tube_end_mm = (
        balance_cg.NOSE_POD_TIP + balance_cg.TUBE_CORE_INSERTION
    ) * 1000.0
    tube_station_mm = 0.5 * (tube_start_mm + tube_end_mm)
    cradle_station_mm = bay_fwd_mm + balance_cg.CRADLE_LENGTH * 500.0

    pack_length, _, pack_height = PACK_6S1P_CAD_ENVELOPE_MM
    pack_x_min = bay_fwd_mm + pack_length / 2.0 + 5.0
    pack_x_max = bay_aft_mm - pack_length / 2.0 - 5.0
    if pack_x_min > pack_x_max:
        raise RuntimeError("maximum-dimension P42A pack does not fit cradle length")
    pack_z = 4.5 + pack_height / 2.0

    components: list[Component3D] = [
        _component(
            "core_shell", "CORE printed shell allocation", "structure",
            masses["core"], (290.0, 390.0, 39.0), (core_x, 0.0, 0.0),
            "[E]", "mass_budget.py; area-centroid station [D]",
            mass_sigma_g=15.0, position_sigma_mm=(15.0, 0.0, 3.0),
            collidable=False,
        ),
        _component(
            "panel_shell_left", "Left PANEL shell allocation", "structure",
            masses["wings"] / 2.0, (390.0, 390.0, 30.0),
            (panel_x, -panel_y, 0.0), "[E]",
            "mass_budget.py; area-centroid station [D]",
            mass_sigma_g=15.0, position_sigma_mm=(15.0, 5.0, 3.0),
            collidable=False,
        ),
        _component(
            "panel_shell_right", "Right PANEL shell allocation", "structure",
            masses["wings"] / 2.0, (390.0, 390.0, 30.0),
            (panel_x, panel_y, 0.0), "[E]",
            "mass_budget.py; area-centroid station [D]",
            mass_sigma_g=15.0, position_sigma_mm=(15.0, 5.0, 3.0),
            collidable=False,
        ),
        _component(
            "tip_shell_left", "Left TIP shell allocation", "structure",
            masses["tips"] / 2.0, (150.0, 65.0, 18.0),
            (tip_x, -tip_y, 0.0), "[E]",
            "mass_budget.py; area-centroid station [D]",
            mass_sigma_g=5.0, position_sigma_mm=(12.0, 3.0, 2.0),
            collidable=False,
        ),
        _component(
            "tip_shell_right", "Right TIP shell allocation", "structure",
            masses["tips"] / 2.0, (150.0, 65.0, 18.0),
            (tip_x, tip_y, 0.0), "[E]",
            "mass_budget.py; area-centroid station [D]",
            mass_sigma_g=5.0, position_sigma_mm=(12.0, 3.0, 2.0),
            collidable=False,
        ),
        _component(
            "elevon_left", "Left elevon", "control",
            masses["elevons"] / 2.0, (
                design_config.chord(design_config.ELEVON_INBOARD_M)
                * design_config.ELEVON_CHORD_FRACTION * 1000.0,
                design_config.ELEVON_SPAN_M * 1000.0,
                16.0,
            ),
            (elevon_x, -elevon_y, 0.0), "[D]/[E]",
            "ADR-0025/0045 mass; planform centroid [D]",
            mass_sigma_g=2.0, position_sigma_mm=(10.0, 5.0, 2.0),
            collidable=False,
        ),
        _component(
            "elevon_right", "Right elevon", "control",
            masses["elevons"] / 2.0, (
                design_config.chord(design_config.ELEVON_INBOARD_M)
                * design_config.ELEVON_CHORD_FRACTION * 1000.0,
                design_config.ELEVON_SPAN_M * 1000.0,
                16.0,
            ),
            (elevon_x, elevon_y, 0.0), "[D]/[E]",
            "ADR-0025/0045 mass; planform centroid [D]",
            mass_sigma_g=2.0, position_sigma_mm=(10.0, 5.0, 2.0),
            collidable=False,
        ),
        _component(
            "elevon_balance_left", "Left elevon balance", "control",
            masses["balance"] / 2.0, (70.0, 30.0, 12.0),
            (-5.0, -elevon_y, 0.0), "[D]/[E]",
            "ADR-0025/0045 allocation; physical x station open",
            mass_sigma_g=3.0, position_sigma_mm=(30.0, 20.0, 5.0),
            collidable=False,
        ),
        _component(
            "elevon_balance_right", "Right elevon balance", "control",
            masses["balance"] / 2.0, (70.0, 30.0, 12.0),
            (-5.0, elevon_y, 0.0), "[D]/[E]",
            "ADR-0025/0045 allocation; physical x station open",
            mass_sigma_g=3.0, position_sigma_mm=(30.0, 20.0, 5.0),
            collidable=False,
        ),
        _component(
            "carbon_left", "Left carbon tube and pins", "structure",
            masses["carbon"] / 2.0, (390.0, 12.0, 12.0),
            (design_config.x_c4(0.390) * 1000.0, -390.0, 0.0),
            "[E]", "mass_budget.py; c/4 station [D]",
            orientation_deg=(0.0, 0.0, 90.0), mass_sigma_g=8.0,
            position_sigma_mm=(5.0, 5.0, 3.0), collidable=False,
        ),
        _component(
            "carbon_right", "Right carbon tube and pins", "structure",
            masses["carbon"] / 2.0, (390.0, 12.0, 12.0),
            (design_config.x_c4(0.390) * 1000.0, 390.0, 0.0),
            "[E]", "mass_budget.py; c/4 station [D]",
            orientation_deg=(0.0, 0.0, 90.0), mass_sigma_g=8.0,
            position_sigma_mm=(5.0, 5.0, 3.0), collidable=False,
        ),
        _component(
            "nose_boom_tube", "Aluminium nose-boom tube", "structure",
            tube_mass_g, (tube_end_mm - tube_start_mm, 8.0, 8.0),
            (tube_station_mm, 0.0, 0.0), "[D]/[E]",
            "balance_cg.py / boom_flexion.py",
            mass_sigma_g=1.0, position_sigma_mm=(2.0, 1.0, 1.0),
            collidable=False,
        ),
        _component(
            "battery_cradle", "Printed two-support battery cradle", "structure",
            balance_cg.CRADLE_MASS * 1000.0,
            (balance_cg.CRADLE_LENGTH * 1000.0, 70.4, 30.0),
            (cradle_station_mm, 0.0, 12.0), "[E]",
            "ADR-0043 15 g allocation; CAD mass pending",
            mass_sigma_g=3.0, position_sigma_mm=(3.0, 1.0, 2.0),
            collidable=False,
        ),
        _component(
            "battery_6s1p", "6S1P Molicel P42A installed pack", "energy",
            masses["battery"], PACK_6S1P_CAD_ENVELOPE_MM,
            (solved["pack_station"] * 1000.0, 0.0, pack_z),
            "[D]/[E]",
            (
                "Molicel P42A max 70.2 x 21.7 mm [M]; pack-level wrap, "
                "nickel and leads [E]; 6 x 70 g max [M] + 25 g hardware [E]"
            ),
            bounds=Bounds3D(
                (pack_x_min, 0.0, pack_z),
                (pack_x_max, 0.0, pack_z),
            ),
            mass_sigma_g=10.0, position_sigma_mm=(2.0, 1.0, 1.0),
        ),
    ]

    servo_station_mm = SERVO_STATION_MM
    for side, sign in (("left", -1.0), ("right", 1.0)):
            placement = solve_servo_placement(servo_station_mm)
            position = (
                placement.position_mm[0],
                sign * servo_station_mm,
                placement.position_mm[2],
            )
            identifier = f"servo_{side}_{int(servo_station_mm)}"
            components.append(_component(
                identifier,
                f"Corona DS-939MG {side} y={servo_station_mm:.2f}",
                "actuator",
                masses["servos"] / 2.0,
                SERVO_BODY_SIZE_MM,
                position,
                "[D]/[E]",
                (
                    "r1 section-fit/linkage solution: "
                    f"x/c={placement.x_fraction:.4f}, pushrod projection "
                    f"{placement.pushrod_projection_mm:.1f} mm"
                ),
                bounds=Bounds3D.fixed(position),
                mass_sigma_g=0.5,
                position_sigma_mm=(1.0, 1.0, 1.0),
            ))

    components.extend([
        _component(
            "motor", "28-class reference motor", "propulsion",
            masses["motor"], (35.0, 28.0, 28.0), (212.5, 0.0, 0.0),
            "[E]", "guide motor class; exact product open",
            mass_sigma_g=30.0, position_sigma_mm=(5.0, 2.0, 2.0),
        ),
        _component(
            "prop_adapter", "Propeller adapter / collet", "propulsion",
            10.0, (12.0, 20.0, 20.0), (232.0, 0.0, 0.0),
            "[E]", "mass_budget.py 10 g allowance",
            mass_sigma_g=3.0, position_sigma_mm=(2.0, 1.0, 1.0),
            collidable=False,
        ),
        _component(
            "propeller", "APC 8x8EP pusher propeller", "propulsion",
            masses["prop"] - 10.0,
            (
                design_config.PROP_AXIAL_ENVELOPE_M * 1000.0,
                design_config.PROP_DIAMETER_M * 1000.0,
                design_config.PROP_DIAMETER_M * 1000.0,
            ),
            (design_config.PROP_PLANE_M * 1000.0, 0.0, 0.0), "[M]",
            "APC LP08080EP 0.53 oz; guide prop plane",
            mass_sigma_g=0.5, position_sigma_mm=(1.0, 1.0, 1.0),
            collidable=False,
        ),
        _component(
            "esc", "6S 30 A ESC envelope", "power",
            masses["esc"], (60.0, 30.0, 15.0), (60.0, -48.0, -8.0),
            "[E]", "guide class; exact product open",
            bounds=Bounds3D((40.0, -65.0, -12.0), (100.0, 65.0, 8.0)),
            mass_sigma_g=10.0, position_sigma_mm=(20.0, 15.0, 5.0),
        ),
        _component(
            "fc", "SpeedyBee F405 WING flight controller", "avionics",
            8.9, (36.5, 36.5, 7.0), (target_cg_mm(), 0.0, 5.0), "[M]",
            "SpeedyBee product data; CG-centred installation policy [I]",
            bounds=Bounds3D(
                (target_cg_mm() - 5.0, -5.0, 2.0),
                (target_cg_mm() + 5.0, 5.0, 10.0),
            ),
            mass_sigma_g=0.3, position_sigma_mm=(3.0, 2.0, 1.0),
        ),
        _component(
            "pdb", "SpeedyBee F405 WING PDB/current board", "power",
            11.4, (36.5, 36.5, 5.0), (10.0, 0.0, -4.0), "[M]",
            "SpeedyBee product mass; thickness envelope [E]",
            bounds=Bounds3D((0.0, -20.0, -10.0), (40.0, 20.0, -3.0)),
            mass_sigma_g=0.5, position_sigma_mm=(3.0, 2.0, 1.0),
        ),
        _component(
            "gps_mag", "Matek M10Q-5883 GPS/magnetometer", "sensor",
            8.0, (20.0, 20.0, 12.4), (-110.0, 150.0, 10.0),
            "[M]", "Matek M10Q-5883 product data",
            bounds=Bounds3D((-130.0, 110.0, 2.0), (-90.0, 170.0, 22.0)),
            mass_sigma_g=0.5, position_sigma_mm=(5.0, 8.0, 2.0),
        ),
        _component(
            "receiver", "Happymodel EP1 ELRS receiver", "avionics",
            0.42, (10.0, 10.0, 3.0), (5.0, -45.0, 3.0), "[M]",
            "Happymodel EP1 without antenna",
            bounds=Bounds3D((-20.0, -160.0, -8.0), (40.0, -25.0, 12.0)),
            mass_sigma_g=0.1, position_sigma_mm=(10.0, 20.0, 3.0),
        ),
        _component(
            "receiver_antenna", "ELRS receiver antenna allocation", "rf",
            0.8, (80.0, 4.0, 4.0), (-20.0, -110.0, 5.0), "[E]",
            "declared provisional mass/envelope; procurement open",
            bounds=Bounds3D((-100.0, -180.0, -15.0), (80.0, -70.0, 25.0)),
            mass_sigma_g=0.4, position_sigma_mm=(25.0, 25.0, 8.0),
            collidable=False,
        ),
        _component(
            "pitot_sensor", "Matek ASPD-4525 sensor board", "sensor",
            3.5, (30.0, 20.0, 10.0), (-50.0, 0.0, -10.0), "[M]",
            "Matek board mass; packaging envelope [E]",
            bounds=Bounds3D((-80.0, -30.0, -14.0), (20.0, 30.0, 10.0)),
            mass_sigma_g=0.5, position_sigma_mm=(15.0, 10.0, 5.0),
        ),
        _component(
            "pitot_probe_tube", "Pitot probe, tube and fittings allocation", "sensor",
            5.0, (360.0, 8.0, 8.0),
            (design_config.x_le(0.260) * 500.0 - 10.0, 130.0, 0.0),
            "[E]", "ASPD-4525 kit; installed mass pending",
            mass_sigma_g=3.0, position_sigma_mm=(30.0, 30.0, 5.0),
            collidable=False,
        ),
        _component(
            "buzzer", "5 V aircraft buzzer allocation", "avionics",
            2.0, (15.0, 15.0, 10.0), (30.0, 30.0, 5.0), "[E]",
            "I-17 provisional current/mass class",
            bounds=Bounds3D((-20.0, 20.0, -8.0), (50.0, 80.0, 12.0)),
            mass_sigma_g=1.0, position_sigma_mm=(15.0, 15.0, 4.0),
        ),
        _component(
            "avionics_installation_reserve",
            "Unresolved avionics wiring/connectors/mounts reserve",
            "reserve", 72.88, (180.0, 80.0, 25.0), (-10.0, 0.0, 0.0),
            "[E]", "remainder of the released 112.9 g avionics allocation",
            mass_sigma_g=40.0, position_sigma_mm=(50.0, 40.0, 10.0),
            reserve=True, collidable=False,
        ),
        _component(
            "o4_camera", "DJI O4 Air Unit camera module", "fpv",
            equipment_catalog.DJI_O4_CAMERA.mass_g,
            equipment_catalog.DJI_O4_CAMERA.envelope_mm,
            (camera_station_mm, 0.0, -5.0), "[D]",
            (
                "DJI LxWxH [M]; mass = 8.2 g air unit incl. camera "
                "minus 5.1 g transmission module [D]"
            ),
            # Lens faces forward (-x) and is flush with the cradle forward
            # plane; the body extends aft.  This is a fixed FPV installation
            # policy, not a movable balance item.
            bounds=Bounds3D.fixed((camera_station_mm, 0.0, -5.0)),
            view_direction=(-1.0, 0.0, 0.0),
            mass_sigma_g=0.3, position_sigma_mm=(5.0, 2.0, 2.0),
        ),
        _component(
            "o4_vtx", "DJI O4 Air Unit VTX + attached antenna", "fpv",
            equipment_catalog.DJI_O4_TRANSMISSION_ASSEMBLY_MASS_G,
            equipment_catalog.DJI_O4_TRANSMISSION_MODULE.envelope_mm,
            (-418.0, 0.0, 31.5), "[D]",
            (
                "30 x 30 x 6 mm VTX body [M]; 0.75 g antenna mass lumped at "
                "the VTX station [D]; 80 mm antenna route remains an assembly note"
            ),
            bounds=Bounds3D((-430.0, -20.0, 29.0), (-330.0, 20.0, 40.0)),
            mass_sigma_g=0.4, position_sigma_mm=(5.0, 3.0, 2.0),
        ),
        _component(
            "hardware_reserve", "Screws, adhesive, dowels and misc. reserve",
            "reserve", masses["hardware"], (220.0, 100.0, 30.0),
            (50.0, 0.0, 0.0), "[E]", "mass_budget.py allocation",
            mass_sigma_g=10.0, position_sigma_mm=(50.0, 40.0, 10.0),
            reserve=True, collidable=False,
        ),
    ])

    if variant_key == "v1":
        # Local import avoids a module cycle: yaw_stability obtains I_zz from
        # this layout lazily, while the layout consumes its single-source fin
        # planform only when the V1 variant is requested.
        from yaw_stability import (
            FIN_BOOM_HEIGHT_M,
            FIN_BOOM_WIDTH_M,
            FIN_ROOT_Z_M,
            fin_area_for_target,
            fin_geometry,
        )

        fin = fin_geometry(fin_area_for_target(0.0005))
        fin_shell_x_mm = (fin.root_te_x_m - 0.5 * fin.mac_m) * 1000.0
        fin_shell_z_mm = (FIN_ROOT_Z_M + fin.centroid_height_m) * 1000.0
        spar_dx_m = fin.tip_le_x_m - fin.root_le_x_m
        spar_length_mm = hypot(fin.span_m, spar_dx_m) * 1000.0
        spar_pitch_deg = degrees(atan2(spar_dx_m, fin.span_m))
        spar_x_mm = 0.5 * (fin.root_le_x_m + fin.tip_le_x_m) * 1000.0
        spar_z_mm = (FIN_ROOT_Z_M + 0.5 * fin.span_m) * 1000.0
        boom_length_mm = (fin.boom_x_end_m - fin.boom_x_start_m) * 1000.0
        boom_x_mm = 0.5 * (fin.boom_x_start_m + fin.boom_x_end_m) * 1000.0
        for side, sign in (("left", -1.0), ("right", 1.0)):
            y_mm = sign * fin.lateral_station_m * 1000.0
            components.extend([
                _component(
                    f"v1_fin_shell_mount_{side}",
                    f"V1a {side} fin shell and mount lower model",
                    "stability",
                    design_config.V1_FIN_SHELL_MOUNT_LOWER_KG * 500.0,
                    (
                        fin.root_chord_m * 1000.0,
                        3.0,
                        fin.span_m * 1000.0,
                    ),
                    (fin_shell_x_mm, y_mm, fin_shell_z_mm),
                    "[E]", "yaw_stability.py; twin-fin installation [I]",
                    mass_sigma_g=4.0, position_sigma_mm=(15.0, 2.0, 10.0),
                    collidable=False,
                ),
                _component(
                    f"v1_fin_spar_{side}",
                    f"V1a {side} aluminium leading-edge spar",
                    "stability",
                    design_config.V1_FIN_SPAR_MASS_KG * 500.0,
                    (3.0, 3.0, spar_length_mm),
                    (spar_x_mm, y_mm, spar_z_mm),
                    "[D]/[E]", "yaw_stability.py",
                    orientation_deg=(0.0, spar_pitch_deg, 0.0),
                    mass_sigma_g=0.5, position_sigma_mm=(10.0, 2.0, 10.0),
                    collidable=False,
                ),
                _component(
                    f"v1_fin_boom_{side}",
                    f"V1a {side} aft CORE carbon boom",
                    "stability",
                    design_config.V1_FIN_BOOM_MASS_KG * 500.0,
                    (
                        boom_length_mm,
                        FIN_BOOM_WIDTH_M * 1000.0,
                        FIN_BOOM_HEIGHT_M * 1000.0,
                    ),
                    (boom_x_mm, y_mm, 0.0),
                    "[E]", "yaw_stability.py; Ø6/4 carbon tube in fairing [I]",
                    mass_sigma_g=1.5, position_sigma_mm=(10.0, 2.0, 3.0),
                    collidable=False,
                ),
            ])

    return tuple(components)


def reference_layout(variant: str = "clean") -> Layout3D:
    return Layout3D(
        reference_components(variant),
        links=(
            LinkConstraint(
                "DJI O4 camera-to-VTX coax", "o4_camera", "o4_vtx",
                O4_COAX_LENGTH_MM, "[M]",
            ),
            LinkConstraint(
                "GPS harness to FC", "gps_mag", "fc", 200.0, "[M]",
            ),
            LinkConstraint(
                "Pitot pneumatic run", "pitot_probe_tube", "pitot_sensor",
                400.0, "[E]",
            ),
            LinkConstraint(
                "Receiver harness to FC", "receiver", "fc", 200.0, "[E]",
            ),
        ),
        separations=tuple(
            SeparationConstraint(
                f"GPS/mag from {component}", "gps_mag", component,
                GPS_POWER_SEPARATION_MM, "[M]",
            )
            for component in ("motor", "esc", "pdb", "battery_6s1p")
        ),
        variant=variant.upper(),
    )


def required_battery_x(
    layout: Layout3D,
    target_x_mm: float = target_cg_mm(),
    battery_identifier: str = PRIMARY_CG_ADJUSTER,
) -> float:
    """Return the unconstrained pack station required for target x-CG."""
    battery = layout.component(battery_identifier)
    others = [
        component for component in layout.components
        if component.identifier != battery_identifier
    ]
    other_mass = sum(component.mass_g for component in others)
    other_moment = sum(
        component.mass_g * component.position_mm[0] for component in others
    )
    return (
        target_x_mm * (other_mass + battery.mass_g) - other_moment
    ) / battery.mass_g


def solve_battery_x(
    layout: Layout3D,
    target_x_mm: float = target_cg_mm(),
    battery_identifier: str = PRIMARY_CG_ADJUSTER,
    *,
    clamp: bool = False,
) -> tuple[Layout3D, float]:
    """Move the pack analytically so the complete-layout x-CG hits target.

    When ``clamp`` is true, an unreachable solution is placed at the nearest
    physical travel limit while the returned value remains the unconstrained
    required station.  This lets the CLI report a design miss without hiding
    it or aborting the rest of the audit.
    """
    battery = layout.component(battery_identifier)
    required_x = required_battery_x(layout, target_x_mm, battery_identifier)
    requested_position = (required_x, battery.position_mm[1], battery.position_mm[2])
    if not battery.bounds.contains(
        requested_position
    ):
        if not clamp:
            raise ValueError(
                f"required battery x={required_x:.2f} mm is outside "
                f"{battery.bounds.minimum_mm[0]:.2f}.."
                f"{battery.bounds.maximum_mm[0]:.2f} mm"
            )
        placed_x = min(
            max(required_x, battery.bounds.minimum_mm[0]),
            battery.bounds.maximum_mm[0],
        )
    else:
        placed_x = required_x
    solved = layout.moved(
        battery_identifier,
        (placed_x, battery.position_mm[1], battery.position_mm[2]),
    )
    return solved, required_x


def solve_v1_packaging(max_iterations: int = 30) -> CoupledPackagingSolution:
    """Close V1 fin mass, CG, battery travel, O4 coax and nose length.

    The CLEAN camera policy and aft battery limit are retained.  If the V1 fin
    assembly requires a farther-forward battery station, the nose boom and
    cradle are extended forward.  Their added mass and shifted centres feed the
    next CG iteration.  The camera follows the new forward cradle plane and the
    O4 VTX moves only as far as necessary to retain the measured 50 mm coax
    constraint.  All extension geometry remains provisional `[I]` pending CAD.
    """
    extension_mm = 0.0
    base = reference_layout("v1")
    base_tube = base.component("nose_boom_tube")
    base_cradle = base.component("battery_cradle")
    base_battery = base.component(PRIMARY_CG_ADJUSTER)
    base_camera = base.component("o4_camera")
    base_vtx = base.component("o4_vtx")
    tube_linear_mass = base_tube.mass_g / base_tube.size_mm[0]
    cradle_linear_mass = base_cradle.mass_g / base_cradle.size_mm[0]

    def extended_layout(extension: float) -> Layout3D:
        tube_position = (
            base_tube.position_mm[0] - extension / 2.0,
            base_tube.position_mm[1],
            base_tube.position_mm[2],
        )
        tube = replace(
            base_tube,
            mass_g=base_tube.mass_g + tube_linear_mass * extension,
            size_mm=(base_tube.size_mm[0] + extension, *base_tube.size_mm[1:]),
            position_mm=tube_position,
            bounds=Bounds3D.fixed(tube_position),
        )
        cradle_position = (
            base_cradle.position_mm[0] - extension / 2.0,
            base_cradle.position_mm[1],
            base_cradle.position_mm[2],
        )
        cradle = replace(
            base_cradle,
            mass_g=base_cradle.mass_g + cradle_linear_mass * extension,
            size_mm=(base_cradle.size_mm[0] + extension, *base_cradle.size_mm[1:]),
            position_mm=cradle_position,
            bounds=Bounds3D.fixed(cradle_position),
        )
        battery_bounds = Bounds3D(
            (
                base_battery.bounds.minimum_mm[0] - extension,
                base_battery.position_mm[1],
                base_battery.position_mm[2],
            ),
            base_battery.bounds.maximum_mm,
        )
        battery_x = min(
            max(base_battery.position_mm[0], battery_bounds.minimum_mm[0]),
            battery_bounds.maximum_mm[0],
        )
        battery = replace(
            base_battery,
            position_mm=(battery_x, *base_battery.position_mm[1:]),
            bounds=battery_bounds,
        )
        camera_position = (
            base_camera.position_mm[0] - extension,
            base_camera.position_mm[1],
            base_camera.position_mm[2],
        )
        camera = replace(
            base_camera,
            position_mm=camera_position,
            bounds=Bounds3D.fixed(camera_position),
        )
        dz = abs(base_vtx.position_mm[2] - camera_position[2])
        maximum_dx = sqrt(max(O4_COAX_LENGTH_MM**2 - dz**2, 0.0))
        vtx_x = min(base_vtx.position_mm[0], camera_position[0] + maximum_dx)
        vtx_x = max(vtx_x, base_vtx.bounds.minimum_mm[0])
        vtx_position = (vtx_x, base_vtx.position_mm[1], base_vtx.position_mm[2])
        vtx = base_vtx.moved(vtx_position)
        replacements = {
            component.identifier: component
            for component in (tube, cradle, battery, camera, vtx)
        }
        return replace(
            base,
            components=tuple(
                replacements.get(component.identifier, component)
                for component in base.components
            ),
        )

    for iteration in range(1, max_iterations + 1):
        layout = extended_layout(extension_mm)
        required_x = required_battery_x(layout, target_cg_mm())
        battery_min = layout.component(PRIMARY_CG_ADJUSTER).bounds.minimum_mm[0]
        missing = max(0.0, battery_min - required_x)
        if missing <= 1e-7:
            solved, required_x = solve_battery_x(layout)
            break
        extension_mm += missing
    else:
        raise RuntimeError("V1 packaging iteration did not converge")

    minimum_x = min(component.aabb()[0][0] for component in solved.components)
    maximum_x = max(component.aabb()[1][0] for component in solved.components)
    rear_pod_end_mm = 265.0
    bay_forward_mm = balance_cg.solve_reference_layout()["bay_fwd"] * 1000.0
    added_mass = (
        solved.component("nose_boom_tube").mass_g - base_tube.mass_g
        + solved.component("battery_cradle").mass_g - base_cradle.mass_g
    )
    return CoupledPackagingSolution(
        layout=solved,
        required_battery_x_mm=float(required_x),
        nose_extension_mm=float(extension_mm),
        forward_extent_mm=float(minimum_x),
        aft_extent_mm=float(maximum_x),
        central_carrier_length_mm=float(
            rear_pod_end_mm - (bay_forward_mm - extension_mm)
        ),
        added_support_mass_g=float(added_mass),
        iterations=iteration,
    )


def parse_move(value: str) -> tuple[str, Vec3]:
    """Parse CLI ID=x,y,z movement syntax."""
    try:
        identifier, coordinates = value.split("=", 1)
        values = tuple(float(item) for item in coordinates.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "movement must use ID=x,y,z in millimetres"
        ) from exc
    if len(values) != 3:
        raise argparse.ArgumentTypeError(
            "movement must contain exactly three coordinates"
        )
    return identifier, values  # type: ignore[return-value]


def validation_checks() -> dict[str, bool]:
    clean = reference_layout("clean")
    solved, _ = solve_battery_x(clean)
    v1 = reference_layout("v1")
    coupled_v1 = solve_v1_packaging()
    checks = {
        "component identifiers are unique": (
            len(clean.components)
            == len({component.identifier for component in clean.components})
        ),
        "budgeted CLEAN mass reproduces the released contract": isclose(
            clean.mass_g(budgeted_only=True),
            design_config.ARTICLE_CLEAN_MASS_KG * 1000.0,
            abs_tol=1e-8,
        ),
        "installed and budgeted CLEAN masses include the O4 antenna": isclose(
            clean.mass_g(), clean.mass_g(budgeted_only=True), abs_tol=1e-12
        ),
        "E01 uses the P42A maximum-dimension CAD envelope": (
            all(
                isclose(actual, expected, abs_tol=1e-9)
                for actual, expected in zip(
                    clean.component("battery_6s1p").size_mm,
                    (153.0, 65.7, 22.6),
                )
            )
        ),
        "E18 camera and E19 VTX envelope reproduce the bought-in catalog": (
            clean.component("o4_camera").size_mm
            == equipment_catalog.DJI_O4_CAMERA.envelope_mm
            and clean.component("o4_vtx").size_mm
            == equipment_catalog.DJI_O4_TRANSMISSION_MODULE.envelope_mm
            and isclose(
                clean.component("o4_camera").mass_g,
                equipment_catalog.DJI_O4_CAMERA.mass_g,
                abs_tol=1e-12,
            )
            and isclose(
                clean.component("o4_vtx").mass_g,
                equipment_catalog.DJI_O4_TRANSMISSION_ASSEMBLY_MASS_G,
                abs_tol=1e-12,
            )
        ),
        "O4 two-body layout closes to the installed mass budget": isclose(
            sum(
                clean.component(identifier).mass_g
                for identifier in ("o4_camera", "o4_vtx")
            ),
            mass_budget.FPV["O4-Air-Unit"],
            abs_tol=1e-12,
        ),
        "O4 camera is fixed forward-facing on the aircraft centreline": (
            clean.component("o4_camera").view_direction == (-1.0, 0.0, 0.0)
            and isclose(
                clean.component("o4_camera").position_mm[1], 0.0, abs_tol=1e-12
            )
            and all(
                clean.component("o4_camera").position_mm[0]
                < clean.component(identifier).position_mm[0]
                for identifier in ("o4_vtx", "battery_6s1p", "fc")
            )
            and all(
                clean.component("o4_camera").bounds.axis_span(axis) == 0.0
                for axis in range(3)
            )
        ),
        "O4 camera lens face is flush with the forward cradle plane": isclose(
            clean.component("o4_camera").aabb()[0][0],
            balance_cg.solve_reference_layout()["bay_fwd"] * 1000.0,
            abs_tol=1e-9,
        ),
        "battery solve reaches the longitudinal-CG target": isclose(
            solved.cg_mm()[0], target_cg_mm(), abs_tol=1e-9
        ),
        "battery is the only automatic CG adjustment": all(
            before.position_mm == after.position_mm
            for before, after in zip(clean.components, solved.components)
            if before.identifier != PRIMARY_CG_ADJUSTER
        ),
        "airframe and fin masses have fixed stations": all(
            all(component.bounds.axis_span(axis) == 0.0 for axis in range(3))
            for component in (*clean.components, *v1.components)
            if component.category in {"structure", "stability"}
        ),
        "servo stations are fixed by the section-fit solution": all(
            all(component.bounds.axis_span(axis) == 0.0 for axis in range(3))
            and isclose(
                component.position_mm[0],
                solve_servo_placement(abs(component.position_mm[1])).position_mm[0],
                abs_tol=1e-9,
            )
            and isclose(
                component.position_mm[2],
                solve_servo_placement(abs(component.position_mm[1])).position_mm[2],
                abs_tol=1e-9,
            )
            for component in clean.components
            if component.category == "actuator"
        ),
        "servo bodies retain the required airfoil-surface clearance": all(
            solve_servo_placement(station).minimum_surface_clearance_mm
            >= SERVO_SURFACE_CLEARANCE_MM - 1e-9
            for station in (SERVO_STATION_MM,)
        ),
        "servo linkage retains the minimum projected pushrod run": all(
            solve_servo_placement(station).pushrod_projection_mm
            >= SERVO_MIN_PUSHROD_PROJECTION_MM - 1e-9
            for station in (SERVO_STATION_MM,)
        ),
        "servo solution is the aft-most feasible station": all(
            not _servo_candidate_feasible(
                station,
                solve_servo_placement(station).x_fraction + 1e-4,
            )
            for station in (SERVO_STATION_MM,)
        ),
        "FC reference station is the target CG": isclose(
            clean.component("fc").position_mm[0], target_cg_mm(), abs_tol=1e-12
        ) and isclose(clean.component("fc").position_mm[1], 0.0, abs_tol=1e-12),
        "reference equipment envelopes do not collide": not solved.collisions(),
        "O4 coax constraint passes": all(
            passed for link, _, passed in solved.link_results()
            if link.name.startswith("DJI O4")
        ),
        "GPS power-system separation constraints pass": all(
            passed for _, _, passed in solved.separation_results()
        ),
        "assembly inertia diagonal is positive": all(
            solved.inertia_kg_m2()[axis][axis] > 0.0 for axis in range(3)
        ),
        "V1 adds the complete C32 fin lower model": isclose(
            v1.mass_g() - clean.mass_g(),
            design_config.V1_FIN_MODEL_LOWER_KG * 1000.0,
            abs_tol=1e-9,
        ),
        "coupled V1 packaging closes CG without clamping the battery": (
            isclose(
                coupled_v1.layout.cg_mm()[0], target_cg_mm(), abs_tol=1e-9
            )
            and coupled_v1.layout.component(PRIMARY_CG_ADJUSTER).bounds.contains(
                coupled_v1.layout.component(PRIMARY_CG_ADJUSTER).position_mm
            )
        ),
        "coupled V1 nose extension is solved rather than prescribed": (
            0.0 < coupled_v1.nose_extension_mm < 30.0
            and coupled_v1.iterations <= 5
            and coupled_v1.added_support_mass_g > 0.0
        ),
        "coupled V1 camera/VTX placement retains measured O4 coax length": all(
            passed
            for link, _, passed in coupled_v1.layout.link_results()
            if link.name.startswith("DJI O4")
        ),
    }
    try:
        clean.moved("battery_6s1p", (0.0, 0.0, 0.0))
    except ValueError:
        checks["out-of-bounds movement is rejected"] = True
    else:
        checks["out-of-bounds movement is rejected"] = False
    return checks


def design_gates(layout: Layout3D) -> tuple[tuple[str, bool, str], ...]:
    lateral_clearance = CRADLE_INNER_WIDTH_MM - PACK_6S1P_CAD_ENVELOPE_MM[1]
    vertical_clearance = CRADLE_INNER_HEIGHT_MM - PACK_6S1P_CAD_ENVELOPE_MM[2]
    reserve_mass = sum(
        component.mass_g for component in layout.components if component.reserve
    )
    physical_delta = layout.mass_g() - layout.mass_g(budgeted_only=True)
    cg = layout.cg_mm()
    cg_sigma = layout.cg_uncertainty_rss_mm()
    fc_distance = dist(layout.component("fc").position_mm, cg)
    battery = layout.component("battery_6s1p")
    servo_placements = tuple(
        solve_servo_placement(station) for station in (SERVO_STATION_MM,)
    )
    exact_battery_x = required_battery_x(layout)
    battery_reachable = (
        battery.bounds.minimum_mm[0]
        <= exact_battery_x
        <= battery.bounds.maximum_mm[0]
    )
    return (
        (
            "exact longitudinal-CG target reachable by battery travel",
            battery_reachable,
            (
                f"required x={exact_battery_x:+.2f} mm; travel "
                f"{battery.bounds.minimum_mm[0]:+.2f}.."
                f"{battery.bounds.maximum_mm[0]:+.2f}"
            ),
        ),
        (
            "longitudinal CG inside released band",
            abs(cg[0] - target_cg_mm()) <= CG_TOLERANCE_MM,
            (
                f"xCG={cg[0]:+.2f} mm; band "
                f"{target_cg_mm()-CG_TOLERANCE_MM:+.2f}.."
                f"{target_cg_mm()+CG_TOLERANCE_MM:+.2f}"
            ),
        ),
        (
            "one-sigma longitudinal CG uncertainty inside half-band",
            cg_sigma[0] <= CG_TOLERANCE_MM,
            f"sigma_x={cg_sigma[0]:.2f} mm; half-band={CG_TOLERANCE_MM:.2f} mm",
        ),
        (
            "flight controller within 5 mm of three-dimensional aircraft CG",
            fc_distance <= 5.0,
            f"FC-to-CG distance={fc_distance:.2f} mm",
        ),
        (
            "fixed servo stations satisfy section fit and linkage projection",
            all(
                placement.minimum_surface_clearance_mm
                >= SERVO_SURFACE_CLEARANCE_MM - 1e-9
                and placement.pushrod_projection_mm
                >= SERVO_MIN_PUSHROD_PROJECTION_MM - 1e-9
                for placement in servo_placements
            ),
            "; ".join(
                f"y={placement.y_mm:.0f}: x/c={placement.x_fraction:.4f}, "
                f"rod={placement.pushrod_projection_mm:.1f} mm, "
                f"surface gap={placement.minimum_surface_clearance_mm:.2f} mm"
                for placement in servo_placements
            ),
        ),
        (
            "P42A lateral installation clearance >= 2 mm",
            lateral_clearance >= MIN_INSTALL_CLEARANCE_MM,
            (
                f"clearance={lateral_clearance:.2f} mm total; "
                f"cradle inner width {CRADLE_INNER_WIDTH_MM:.1f} mm"
            ),
        ),
        (
            "P42A vertical installation clearance >= 2 mm",
            vertical_clearance >= MIN_INSTALL_CLEARANCE_MM,
            (
                f"clearance={vertical_clearance:.2f} mm total; "
                f"cradle inner height {CRADLE_INNER_HEIGHT_MM:.1f} mm"
            ),
        ),
        (
            "all electronics/packaging envelopes clear",
            not layout.collisions(),
            "none" if not layout.collisions() else str(layout.collisions()),
        ),
        (
            "all declared cable limits pass",
            all(passed for _, _, passed in layout.link_results()),
            "; ".join(
                f"{constraint.name}={distance:.1f}/{constraint.maximum_mm:.1f} mm"
                for constraint, distance, _ in layout.link_results()
            ),
        ),
        (
            "all declared separation limits pass",
            all(passed for _, _, passed in layout.separation_results()),
            "; ".join(
                f"{constraint.second}={distance:.1f}/{constraint.minimum_mm:.1f} mm"
                for constraint, distance, _ in layout.separation_results()
            ),
        ),
        (
            "unresolved mass reserves eliminated",
            reserve_mass <= 1e-9,
            f"reserve={reserve_mass:.2f} g",
        ),
        (
            "installed mass equals released budget",
            abs(physical_delta) <= 1e-9,
            f"installed-minus-budget={physical_delta:+.2f} g",
        ),
    )


def layout_as_dict(layout: Layout3D) -> dict[str, object]:
    inertia = layout.inertia_kg_m2()
    battery = layout.component(PRIMARY_CG_ADJUSTER)
    return {
        "variant": layout.variant,
        "coordinate_system": "mm; x aft, y starboard, z up; root c/4 origin",
        "mass_g": layout.mass_g(),
        "budgeted_mass_g": layout.mass_g(budgeted_only=True),
        "cg_mm": layout.cg_mm(),
        "cg_sigma_mm": layout.cg_uncertainty_rss_mm(),
        "inertia_kg_m2": inertia,
        "cg_adjustment": {
            "primary_component": PRIMARY_CG_ADJUSTER,
            "placed_x_mm": battery.position_mm[0],
            "required_x_mm": required_battery_x(layout),
            "travel_min_x_mm": battery.bounds.minimum_mm[0],
            "travel_max_x_mm": battery.bounds.maximum_mm[0],
        },
        "components": [
            {
                "id": component.identifier,
                "label": component.label,
                "category": component.category,
                "mass_g": component.mass_g,
                "size_mm": component.size_mm,
                "position_mm": component.position_mm,
                "bounds_min_mm": component.bounds.minimum_mm,
                "bounds_max_mm": component.bounds.maximum_mm,
                "movement_class": (
                    "primary-cg-trim"
                    if component.identifier == PRIMARY_CG_ADJUSTER
                    else "fixed"
                    if all(component.bounds.axis_span(axis) == 0.0 for axis in range(3))
                    else "installation-limited"
                ),
                "orientation_deg": component.orientation_deg,
                "authority": component.authority,
                "source": component.source,
                "budgeted": component.budgeted,
                "reserve": component.reserve,
            }
            for component in layout.components
        ],
        "gates": [
            {"name": name, "passed": bool(passed), "detail": detail}
            for name, passed, detail in design_gates(layout)
        ],
    }


def _print_layout(layout: Layout3D, required_battery_x: float) -> None:
    cg = layout.cg_mm()
    sigma = layout.cg_uncertainty_rss_mm()
    inertia = layout.inertia_kg_m2()
    print("=" * 112)
    print(f"SALAMANDRA {layout.variant} - THREE-DIMENSIONAL COMPONENT LAYOUT")
    print("Coordinates [mm]: x aft, y starboard, z up; origin at root c/4")
    print("=" * 112)
    print(
        f"Budgeted mass {layout.mass_g(budgeted_only=True):.2f} g | "
        f"installed model {layout.mass_g():.2f} g | "
        f"battery x placed {layout.component('battery_6s1p').position_mm[0]:+.2f} mm "
        f"(required {required_battery_x:+.2f})"
    )
    print(
        f"CG = ({cg[0]:+.3f}, {cg[1]:+.3f}, {cg[2]:+.3f}) mm | "
        f"first-order sigma = ({sigma[0]:.2f}, {sigma[1]:.2f}, "
        f"{sigma[2]:.2f}) mm"
    )
    print(
        f"Inertia at CG [kg m2]: Ixx={inertia[0][0]:.5f} "
        f"Iyy={inertia[1][1]:.5f} Izz={inertia[2][2]:.5f}"
    )
    print("\nCOMPONENT LEDGER")
    print(
        "  id                              mass       x       y       z   "
        "dx    dy    dz  tag status"
    )
    print("  " + "-" * 106)
    for component in layout.components:
        status = "RESERVE" if component.reserve else (
            "UNBUDGETED" if not component.budgeted else ""
        )
        print(
            f"  {component.identifier:30s} {component.mass_g:6.2f} "
            f"{component.position_mm[0]:+7.1f} "
            f"{component.position_mm[1]:+7.1f} "
            f"{component.position_mm[2]:+7.1f} "
            f"{component.size_mm[0]:5.1f} {component.size_mm[1]:5.1f} "
            f"{component.size_mm[2]:5.1f} {component.authority:>6s} {status}"
        )

    print("\nCABLE / SEPARATION CHECKS")
    for constraint, distance, passed in layout.link_results():
        print(
            f"  [{'PASS' if passed else 'OPEN'}] {constraint.name}: "
            f"{distance:.1f} <= {constraint.maximum_mm:.1f} mm "
            f"{constraint.authority}"
        )
    for constraint, distance, passed in layout.separation_results():
        print(
            f"  [{'PASS' if passed else 'OPEN'}] {constraint.name}: "
            f"{distance:.1f} >= {constraint.minimum_mm:.1f} mm "
            f"{constraint.authority}"
        )

    print("\nDESIGN GATES")
    for name, passed, detail in design_gates(layout):
        print(f"  [{'PASS' if passed else 'OPEN'}] {name}: {detail}")

    checks = validation_checks()
    print("\nSOFTWARE / NUMERICAL VALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL SOFTWARE CHECKS PASS; OPEN DESIGN GATES REMAIN")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("clean", "v1"), default="clean")
    parser.add_argument(
        "--move", action="append", default=[], type=parse_move, metavar="ID=X,Y,Z",
        help="move a component within its declared bounds; repeatable",
    )
    parser.add_argument(
        "--hold-battery", action="store_true",
        help="do not re-solve battery x after user movements",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON",
    )
    args = parser.parse_args()

    layout = reference_layout(args.variant)
    for identifier, position in args.move:
        try:
            layout = layout.moved(identifier, position)
        except (KeyError, ValueError) as exc:
            parser.error(str(exc))

    battery_x = layout.component("battery_6s1p").position_mm[0]
    if not args.hold_battery:
        try:
            layout, battery_x = solve_battery_x(layout, clamp=True)
        except ValueError as exc:
            parser.error(str(exc))

    if args.json:
        print(json.dumps(layout_as_dict(layout), indent=2))
    else:
        _print_layout(layout, battery_x)


if __name__ == "__main__":
    main()
