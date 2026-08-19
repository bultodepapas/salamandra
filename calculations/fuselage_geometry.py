#!/usr/bin/env python3
"""NumPy-only provisional fuselage OML generator and containment audit.

The generated body is an analytical superelliptic loft around the central
equipment/structural skeleton. It is not native CAD and it takes zero primary
structural credit. Its purpose is to replace unrelated 2-D styling curves with
one reproducible 3-D source for review meshes, drawings and feasibility gates.

Authority: all OML dimensions and transitions are [I]. Component envelopes
retain their authority from equipment_layout. DRAFT - NOT FOR MANUFACTURE.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from functools import cache
from math import pi
from typing import Iterable

import numpy as np

import design_config
import equipment_layout
import fuselage_contract


@dataclass(frozen=True)
class EnvelopeVolume:
    identifier: str
    minimum_mm: tuple[float, float, float]
    maximum_mm: tuple[float, float, float]
    authority: str
    source: str


@dataclass(frozen=True)
class SectionParameters:
    x_mm: float
    half_width_mm: float
    waist_z_mm: float
    top_radius_mm: float
    bottom_radius_mm: float
    exponent: float

    @property
    def z_top_mm(self) -> float:
        return self.waist_z_mm + self.top_radius_mm

    @property
    def z_bottom_mm(self) -> float:
        return self.waist_z_mm - self.bottom_radius_mm


@dataclass(frozen=True)
class Mesh:
    vertices_mm: np.ndarray
    faces: np.ndarray


@dataclass(frozen=True)
class MeshMetrics:
    area_m2: float
    volume_m3: float
    centroid_mm: tuple[float, float, float]
    signed_volume_m3: float
    watertight: bool
    boundary_edges: int
    nonmanifold_edges: int


@dataclass(frozen=True)
class EnvelopeAudit:
    identifier: str
    passed: bool
    minimum_margin_mm: float
    limiting_point_mm: tuple[float, float, float]
    authority: str


@dataclass(frozen=True)
class FuselageModel:
    design: fuselage_contract.OmlDesignVector
    family: fuselage_contract.FamilyDefinition
    policy: fuselage_contract.EnvelopePolicy
    x_min_mm: float
    x_max_mm: float
    envelopes: tuple[EnvelopeVolume, ...]

    @property
    def length_mm(self) -> float:
        return self.x_max_mm - self.x_min_mm


def open_uniform_knots(control_count: int, degree: int = 3) -> np.ndarray:
    """Return the clamped open-uniform knot vector on [0, 1]."""
    if degree < 1 or control_count <= degree:
        raise ValueError("control_count must exceed the positive spline degree")
    interior_count = control_count - degree - 1
    interior = (
        np.arange(1, interior_count + 1, dtype=float) / (interior_count + 1)
        if interior_count
        else np.empty(0)
    )
    return np.concatenate((np.zeros(degree + 1), interior, np.ones(degree + 1)))


def bspline_basis(xi: np.ndarray | float, control_count: int, degree: int = 3) -> np.ndarray:
    """Cox-de Boor basis matrix for a clamped one-dimensional B-spline."""
    values = np.atleast_1d(np.asarray(xi, dtype=float))
    if np.any((values < 0.0) | (values > 1.0)):
        raise ValueError("normalized spline coordinates must be in [0, 1]")
    knots = open_uniform_knots(control_count, degree)
    basis = np.zeros((len(values), control_count + degree), dtype=float)
    for index in range(control_count + degree):
        basis[:, index] = (
            (values >= knots[index]) & (values < knots[index + 1])
        ).astype(float)
    basis[values == 1.0, :] = 0.0
    basis[values == 1.0, control_count - 1] = 1.0
    for order in range(1, degree + 1):
        next_basis = np.zeros_like(basis)
        for index in range(control_count + degree - order):
            left_denominator = knots[index + order] - knots[index]
            right_denominator = knots[index + order + 1] - knots[index + 1]
            if left_denominator > 0.0:
                next_basis[:, index] += (
                    (values - knots[index]) / left_denominator * basis[:, index]
                )
            if right_denominator > 0.0:
                next_basis[:, index] += (
                    (knots[index + order + 1] - values)
                    / right_denominator
                    * basis[:, index + 1]
                )
        basis = next_basis
    return basis[:, :control_count]


def bspline_value(controls: tuple[float, ...], xi: np.ndarray | float) -> np.ndarray:
    return bspline_basis(xi, len(controls)) @ np.asarray(controls, dtype=float)


def _smoothstep(value: np.ndarray | float) -> np.ndarray:
    clipped = np.clip(np.asarray(value, dtype=float), 0.0, 1.0)
    return clipped * clipped * (3.0 - 2.0 * clipped)


def _envelope_weight(
    x_mm: float,
    envelope: EnvelopeVolume,
    transition_mm: float,
) -> float:
    if envelope.minimum_mm[0] <= x_mm <= envelope.maximum_mm[0]:
        return 1.0
    if x_mm < envelope.minimum_mm[0]:
        distance = envelope.minimum_mm[0] - x_mm
    else:
        distance = x_mm - envelope.maximum_mm[0]
    return float(_smoothstep(1.0 - distance / transition_mm))


def _smooth_max(values: Iterable[float], power: float) -> float:
    array = np.asarray(tuple(values), dtype=float)
    if len(array) == 0 or np.any(array < 0.0) or power <= 1.0:
        raise ValueError("smooth maximum needs non-negative values and power > 1")
    return float(np.sum(array**power) ** (1.0 / power))


def _component_envelopes(
    layout: equipment_layout.Layout3D,
    policy: fuselage_contract.EnvelopePolicy,
) -> tuple[EnvelopeVolume, ...]:
    volumes: list[EnvelopeVolume] = []
    margin = policy.radial_margin_mm
    lens_min_x = layout.component(policy.lens_face_component).aabb()[0][0]
    for identifier in fuselage_contract.BODY_ENVELOPE_COMPONENT_IDS:
        component = layout.component(identifier)
        minimum, maximum = component.aabb()
        # Camera, cradle and boom share the controlled forward plane. Inflating
        # any one of them through that aperture creates an impossible nose
        # station; only the x-forward allowance is waived there.
        x_margin_forward = (
            0.0 if abs(minimum[0] - lens_min_x) <= 1e-6 else margin
        )
        volumes.append(
            EnvelopeVolume(
                identifier=identifier,
                minimum_mm=(
                    float(minimum[0] - x_margin_forward),
                    float(minimum[1] - margin),
                    float(minimum[2] - margin),
                ),
                maximum_mm=(
                    float(maximum[0] + margin),
                    float(maximum[1] + margin),
                    float(maximum[2] + margin),
                ),
                authority=component.authority,
                source=component.source,
            )
        )
    return tuple(volumes)


def build_model(
    design: fuselage_contract.OmlDesignVector | None = None,
    policy: fuselage_contract.EnvelopePolicy | None = None,
) -> FuselageModel:
    if design is None:
        design = fuselage_contract.DEFAULT_DESIGN
    if policy is None:
        policy = fuselage_contract.DEFAULT_POLICY
    layout = equipment_layout.reference_layout("clean")
    envelopes = _component_envelopes(layout, policy)
    camera = next(item for item in envelopes if item.identifier == policy.lens_face_component)
    motor = next(item for item in envelopes if item.identifier == "motor")
    # The camera lens is a deliberate flush aperture. The aft 35 mm recovery
    # reproduces the guide's +265 mm provisional pod end from the motor face.
    x_min = camera.minimum_mm[0]
    x_max = motor.maximum_mm[0] - policy.radial_margin_mm + 35.0
    return FuselageModel(
        design=design,
        family=fuselage_contract.FAMILY_BY_ID[design.family],
        policy=policy,
        x_min_mm=x_min,
        x_max_mm=x_max,
        envelopes=envelopes,
    )


@cache
def reference_model() -> FuselageModel:
    return build_model()


def section_parameters(model: FuselageModel, x_mm: float) -> SectionParameters:
    tolerance = 1e-9
    if not model.x_min_mm - tolerance <= x_mm <= model.x_max_mm + tolerance:
        raise ValueError("x station is outside the body OML")
    xi = min(max((x_mm - model.x_min_mm) / model.length_mm, 0.0), 1.0)
    family = model.family
    design = model.design
    tail_start_xi = 72.0 / 100.0
    tail_weight = float(_smoothstep((xi - tail_start_xi) / (1.0 - tail_start_xi)))
    tail_multiplier = 1.0 + (design.tail_scale - 1.0) * tail_weight
    width_base = float(bspline_value(family.half_width_control_mm, xi)[0])
    top_base = float(bspline_value(family.top_control_mm, xi)[0])
    bottom_base = float(bspline_value(family.bottom_control_mm, xi)[0])
    waist = (
        float(bspline_value(family.waist_z_control_mm, xi)[0])
        + design.waist_shift_mm
    )
    exponent = float(bspline_value(family.exponent_control, xi)[0])
    corner_factor = 2.0 ** (1.0 / exponent)
    width_terms = [width_base * design.width_scale * tail_multiplier]
    top_terms = [top_base * design.dorsal_scale * tail_multiplier]
    bottom_terms = [bottom_base * design.ventral_scale * tail_multiplier]
    for envelope in model.envelopes:
        weight = _envelope_weight(
            x_mm,
            envelope,
            model.policy.longitudinal_transition_mm,
        )
        if weight <= 0.0:
            continue
        lateral = max(abs(envelope.minimum_mm[1]), abs(envelope.maximum_mm[1]))
        dorsal = max(envelope.maximum_mm[2] - waist, 0.0)
        ventral = max(waist - envelope.minimum_mm[2], 0.0)
        width_terms.append(lateral * corner_factor * weight)
        top_terms.append(dorsal * corner_factor * weight)
        bottom_terms.append(ventral * corner_factor * weight)
    power = model.policy.smooth_max_power
    return SectionParameters(
        x_mm=float(x_mm),
        half_width_mm=_smooth_max(width_terms, power),
        waist_z_mm=waist,
        top_radius_mm=_smooth_max(top_terms, power),
        bottom_radius_mm=_smooth_max(bottom_terms, power),
        exponent=exponent,
    )


def section_points(
    model: FuselageModel,
    x_mm: float,
    count: int = 72,
) -> np.ndarray:
    if count < 12 or count % 4:
        raise ValueError("circumferential count must be a multiple of four >= 12")
    parameters = section_parameters(model, x_mm)
    theta = np.linspace(0.0, 2.0 * pi, count, endpoint=False)
    cosine = np.cos(theta)
    sine = np.sin(theta)
    exponent_power = 2.0 / parameters.exponent
    y_mm = (
        parameters.half_width_mm
        * np.sign(cosine)
        * np.abs(cosine) ** exponent_power
    )
    vertical_radius = np.where(
        sine >= 0.0,
        parameters.top_radius_mm,
        parameters.bottom_radius_mm,
    )
    z_mm = (
        parameters.waist_z_mm
        + vertical_radius
        * np.sign(sine)
        * np.abs(sine) ** exponent_power
    )
    return np.column_stack((np.full(count, x_mm), y_mm, z_mm))


def plan_outline_mm(model: FuselageModel, stations: int = 161) -> tuple[tuple[float, float], ...]:
    x_values = np.linspace(model.x_min_mm, model.x_max_mm, stations)
    half_widths = [section_parameters(model, float(x)).half_width_mm for x in x_values]
    positive = [(float(x), float(y)) for x, y in zip(x_values, half_widths)]
    negative = [(float(x), float(-y)) for x, y in zip(x_values[::-1], half_widths[::-1])]
    return tuple(positive + negative)


def side_outline_mm(model: FuselageModel, stations: int = 161) -> tuple[tuple[float, float], ...]:
    x_values = np.linspace(model.x_min_mm, model.x_max_mm, stations)
    parameters = [section_parameters(model, float(x)) for x in x_values]
    upper = [(float(x), item.z_top_mm) for x, item in zip(x_values, parameters)]
    lower = [(float(x), item.z_bottom_mm) for x, item in zip(x_values[::-1], parameters[::-1])]
    return tuple(upper + lower)


def build_mesh(
    model: FuselageModel,
    longitudinal: int = 81,
    circumferential: int = 72,
) -> Mesh:
    if longitudinal < 9:
        raise ValueError("longitudinal resolution must be >= 9")
    x_values = np.linspace(model.x_min_mm, model.x_max_mm, longitudinal)
    rings = [section_points(model, float(x), circumferential) for x in x_values]
    vertices = np.vstack(rings)
    faces: list[tuple[int, int, int]] = []
    for station in range(longitudinal - 1):
        start = station * circumferential
        next_start = (station + 1) * circumferential
        for index in range(circumferential):
            following = (index + 1) % circumferential
            # theta increases counter-clockwise in the y-z plane. These orders
            # put the side normals outward; the previous order produced a
            # topologically closed but inconsistently oriented mesh whose
            # signed volume changed under translation.
            faces.append((start + index, next_start + following, next_start + index))
            faces.append((start + index, start + following, next_start + following))
    front_parameters = section_parameters(model, model.x_min_mm)
    rear_parameters = section_parameters(model, model.x_max_mm)
    front_center = len(vertices)
    rear_center = front_center + 1
    vertices = np.vstack(
        (
            vertices,
            (model.x_min_mm, 0.0, front_parameters.waist_z_mm),
            (model.x_max_mm, 0.0, rear_parameters.waist_z_mm),
        )
    )
    rear_start = (longitudinal - 1) * circumferential
    for index in range(circumferential):
        following = (index + 1) % circumferential
        faces.append((front_center, following, index))
        faces.append((rear_center, rear_start + index, rear_start + following))
    mesh = Mesh(vertices.astype(float), np.asarray(faces, dtype=np.int64))
    if mesh_metrics(mesh).signed_volume_m3 < 0.0:
        mesh = Mesh(mesh.vertices_mm, mesh.faces[:, ::-1].copy())
    return mesh


def _edge_topology(faces: np.ndarray) -> tuple[bool, int, int]:
    counts: dict[tuple[int, int], int] = {}
    for face in faces:
        for first, second in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            edge = tuple(sorted((int(first), int(second))))
            counts[edge] = counts.get(edge, 0) + 1
    boundary = sum(count == 1 for count in counts.values())
    nonmanifold = sum(count > 2 for count in counts.values())
    return boundary == 0 and nonmanifold == 0, boundary, nonmanifold


def mesh_metrics(mesh: Mesh) -> MeshMetrics:
    triangles = mesh.vertices_mm[mesh.faces]
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    area_mm2 = 0.5 * np.linalg.norm(cross, axis=1).sum()
    tetrahedra_mm3 = np.einsum(
        "ij,ij->i", triangles[:, 0], np.cross(triangles[:, 1], triangles[:, 2])
    ) / 6.0
    signed_volume_mm3 = float(tetrahedra_mm3.sum())
    volume_mm3 = abs(signed_volume_mm3)
    if volume_mm3 <= 1e-12:
        raise ValueError("mesh has zero enclosed volume")
    centroid_mm = (
        (triangles[:, 0] + triangles[:, 1] + triangles[:, 2])
        * tetrahedra_mm3[:, None]
        / 4.0
    ).sum(axis=0) / signed_volume_mm3
    watertight, boundary_edges, nonmanifold_edges = _edge_topology(mesh.faces)
    return MeshMetrics(
        area_m2=float(area_mm2 * 1e-6),
        volume_m3=float(volume_mm3 * 1e-9),
        centroid_mm=tuple(float(value) for value in centroid_mm),
        signed_volume_m3=float(signed_volume_mm3 * 1e-9),
        watertight=watertight,
        boundary_edges=boundary_edges,
        nonmanifold_edges=nonmanifold_edges,
    )


def point_margin_mm(model: FuselageModel, point_mm: tuple[float, float, float]) -> float:
    x_mm, y_mm, z_mm = point_mm
    if x_mm < model.x_min_mm:
        return x_mm - model.x_min_mm
    if x_mm > model.x_max_mm:
        return model.x_max_mm - x_mm
    parameters = section_parameters(model, x_mm)
    vertical_radius = (
        parameters.top_radius_mm
        if z_mm >= parameters.waist_z_mm
        else parameters.bottom_radius_mm
    )
    normalized = (
        (abs(y_mm) / parameters.half_width_mm) ** parameters.exponent
        + (abs(z_mm - parameters.waist_z_mm) / vertical_radius) ** parameters.exponent
    ) ** (1.0 / parameters.exponent)
    return float((1.0 - normalized) * min(parameters.half_width_mm, vertical_radius))


def _audit_envelope(model: FuselageModel, envelope: EnvelopeVolume) -> EnvelopeAudit:
    axes = tuple(
        np.linspace(envelope.minimum_mm[axis], envelope.maximum_mm[axis], 7 if axis == 0 else 3)
        for axis in range(3)
    )
    minimum_margin = float("inf")
    limiting_point = (0.0, 0.0, 0.0)
    for x_mm in axes[0]:
        for y_mm in axes[1]:
            for z_mm in axes[2]:
                point = (float(x_mm), float(y_mm), float(z_mm))
                margin = point_margin_mm(model, point)
                if margin < minimum_margin:
                    minimum_margin = margin
                    limiting_point = point
    return EnvelopeAudit(
        identifier=envelope.identifier,
        passed=minimum_margin >= -1e-8,
        minimum_margin_mm=minimum_margin,
        limiting_point_mm=limiting_point,
        authority=envelope.authority,
    )


def audit_envelopes(model: FuselageModel) -> tuple[EnvelopeAudit, ...]:
    return tuple(_audit_envelope(model, envelope) for envelope in model.envelopes)


def projected_metrics(model: FuselageModel, stations: int = 401) -> dict[str, float]:
    x_values = np.linspace(model.x_min_mm, model.x_max_mm, stations)
    parameters = [section_parameters(model, float(x)) for x in x_values]
    widths = np.asarray([2.0 * item.half_width_mm for item in parameters])
    heights = np.asarray([item.z_top_mm - item.z_bottom_mm for item in parameters])
    plan_area_m2 = float(np.trapezoid(widths, x_values) * 1e-6)
    side_area_m2 = float(np.trapezoid(heights, x_values) * 1e-6)
    return {
        "plan_projected_area_m2": plan_area_m2,
        "side_projected_area_m2": side_area_m2,
        "maximum_width_mm": float(widths.max()),
        "maximum_height_mm": float(heights.max()),
        "fineness_length_over_max_width": float(model.length_mm / widths.max()),
    }


def fairness_diagnostics(model: FuselageModel, stations: int = 401) -> dict[str, float]:
    x_values = np.linspace(0.0, 1.0, stations)
    actual_x = model.x_min_mm + x_values * model.length_mm
    parameters = [section_parameters(model, float(x)) for x in actual_x]
    laws = {
        "width": np.asarray([item.half_width_mm for item in parameters]),
        "top": np.asarray([item.top_radius_mm for item in parameters]),
        "bottom": np.asarray([item.bottom_radius_mm for item in parameters]),
        "waist": np.asarray([item.waist_z_mm for item in parameters]),
    }
    result: dict[str, float] = {}
    for name, values in laws.items():
        scale = max(float(np.ptp(values)), float(np.max(np.abs(values))), 1.0)
        second = np.gradient(np.gradient(values / scale, x_values), x_values)
        result[f"{name}_curvature_energy"] = float(np.trapezoid(second**2, x_values))
    result["total_curvature_energy"] = sum(result.values())
    return result


def battery_state(variant: str) -> dict[str, float | bool]:
    """Return the unclamped requirement and the stop-limited diagnostic state."""
    layout = equipment_layout.reference_layout(variant)
    required = equipment_layout.required_battery_x(layout)
    battery = layout.component(equipment_layout.PRIMARY_CG_ADJUSTER)
    reachable = bool(
        battery.bounds.minimum_mm[0] <= required <= battery.bounds.maximum_mm[0]
    )
    placed = min(max(required, battery.bounds.minimum_mm[0]), battery.bounds.maximum_mm[0])
    solved = layout.moved(
        equipment_layout.PRIMARY_CG_ADJUSTER,
        (placed, battery.position_mm[1], battery.position_mm[2]),
    )
    return {
        "reachable": bool(reachable),
        "required_x_mm": float(required),
        "placed_x_mm": float(placed),
        "travel_min_x_mm": float(battery.bounds.minimum_mm[0]),
        "travel_max_x_mm": float(battery.bounds.maximum_mm[0]),
        "cg_x_mm": float(solved.cg_mm()[0]),
    }


def report_as_dict(
    model: FuselageModel,
    longitudinal: int = 81,
    circumferential: int = 72,
) -> dict[str, object]:
    mesh = build_mesh(model, longitudinal, circumferential)
    metrics = mesh_metrics(mesh)
    refined = mesh_metrics(
        build_mesh(model, 2 * longitudinal - 1, 2 * circumferential)
    )
    audits = audit_envelopes(model)
    projected = projected_metrics(model)
    fairness = fairness_diagnostics(model)
    gross_skin_mass_g = (
        metrics.area_m2 * 0.0009 * design_config.PETG_DENSITY_KG_M3 * 1000.0
    )
    clean_state = battery_state("clean")
    v1_state = battery_state("v1")
    reserve_mass_g = sum(
        component.mass_g
        for component in equipment_layout.reference_layout("clean").components
        if component.reserve
    )
    geometry_feasible = (
        all(audit.passed for audit in audits)
        and metrics.watertight
        and metrics.volume_m3 > 0.0
    )
    project_blockers: dict[str, bool] = {
        "clean_battery_reachable": bool(clean_state["reachable"]),
        "v1_battery_reachable": bool(v1_state["reachable"]),
        "mass_reserves_located": bool(reserve_mass_g <= 1e-9),
        "net_union_mass_ownership_closed": False,
        "body_inclusive_np_trim_closed": False,
        "wing_installation_audit_closed": False,
    }
    return {
        "schema": fuselage_contract.SCHEMA_VERSION,
        "authority": fuselage_contract.AUTHORITY,
        "warning": fuselage_contract.WARNING,
        "coordinate_system": "mm; x aft, y starboard, z up; root c/4 origin",
        "family": model.family.identifier,
        "family_name": model.family.display_name,
        "design_vector": asdict(model.design),
        "policy": asdict(model.policy),
        "x_range_mm": [model.x_min_mm, model.x_max_mm],
        "mesh": {
            "longitudinal": longitudinal,
            "circumferential": circumferential,
            "vertices": len(mesh.vertices_mm),
            "faces": len(mesh.faces),
            **asdict(metrics),
            "gross_0p9_mm_skin_mass_g": gross_skin_mass_g,
            "mass_scope": (
                "gross body operand only; overlap, cavities, ribs, supports and base wing "
                "are not resolved and this value must not be added to the mass ledger"
            ),
        },
        "resolution_convergence": {
            "area_relative_change": abs(refined.area_m2 - metrics.area_m2) / refined.area_m2,
            "volume_relative_change": abs(refined.volume_m3 - metrics.volume_m3) / refined.volume_m3,
        },
        "projected": projected,
        "fairness": fairness,
        "envelope_audits": [asdict(audit) for audit in audits],
        "geometry_feasible": geometry_feasible,
        "battery": {"clean": clean_state, "v1": v1_state},
        "unresolved_reserve_mass_g": reserve_mass_g,
        "wing_installation_ownership": list(
            fuselage_contract.WING_INSTALLATION_COMPONENT_IDS
        ),
        "project_blockers": project_blockers,
        "aircraft_feasible": geometry_feasible and all(project_blockers.values()),
    }


def manifest_json(report: dict[str, object]) -> str:
    """ASCII-safe, stable machine output for Windows and CI."""
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def mesh_obj(mesh: Mesh, report: dict[str, object]) -> str:
    lines = [
        "# Salamandra provisional fuselage OML",
        f"# {fuselage_contract.WARNING}",
        f"# family={report['family']} authority={report['authority']}",
        "# units=millimetres axes=x_aft,y_starboard,z_up",
    ]
    lines.extend(
        f"v {x:.6f} {y:.6f} {z:.6f}" for x, y, z in mesh.vertices_mm
    )
    lines.extend(
        f"f {a + 1} {b + 1} {c + 1}" for a, b, c in mesh.faces
    )
    return "\n".join(lines) + "\n"


def _uv_sphere(radius: float = 10.0, latitude: int = 40, longitude: int = 80) -> Mesh:
    vertices = [(0.0, 0.0, -radius)]
    for row in range(1, latitude):
        phi = -0.5 * pi + pi * row / latitude
        ring_radius = radius * np.cos(phi)
        z = radius * np.sin(phi)
        for column in range(longitude):
            theta = 2.0 * pi * column / longitude
            vertices.append((ring_radius * np.cos(theta), ring_radius * np.sin(theta), z))
    top = len(vertices)
    vertices.append((0.0, 0.0, radius))
    faces: list[tuple[int, int, int]] = []
    for column in range(longitude):
        following = (column + 1) % longitude
        faces.append((0, 1 + column, 1 + following))
    for row in range(latitude - 2):
        first = 1 + row * longitude
        second = first + longitude
        for column in range(longitude):
            following = (column + 1) % longitude
            faces.append((first + column, second + column, second + following))
            faces.append((first + column, second + following, first + following))
    last_ring = 1 + (latitude - 2) * longitude
    for column in range(longitude):
        following = (column + 1) % longitude
        faces.append((top, last_ring + following, last_ring + column))
    mesh = Mesh(np.asarray(vertices, dtype=float), np.asarray(faces, dtype=np.int64))
    if mesh_metrics(mesh).signed_volume_m3 < 0.0:
        mesh = Mesh(mesh.vertices_mm, mesh.faces[:, ::-1].copy())
    return mesh


def validation_checks(full: bool = True) -> dict[str, bool]:
    """Return fast interface checks or the complete analytical validation set.

    The mutation harness calls the fast tier repeatedly. The standalone module
    and all-scripts verifier retain the high-resolution sphere, translation and
    convergence evidence exactly once per validation campaign.
    """
    model = reference_model()
    basis = bspline_basis(np.linspace(0.0, 1.0, 101), 9)
    mesh = build_mesh(model, 61 if full else 17, 64 if full else 24)
    metrics = mesh_metrics(mesh)
    audits = audit_envelopes(model)
    vtx = next(envelope for envelope in model.envelopes if envelope.identifier == "o4_vtx")
    penetrated = replace(
        vtx,
        minimum_mm=(vtx.minimum_mm[0], vtx.minimum_mm[1], vtx.minimum_mm[2] + 200.0),
        maximum_mm=(vtx.maximum_mm[0], vtx.maximum_mm[1], vtx.maximum_mm[2] + 200.0),
    )
    penetration_caught = not _audit_envelope(model, penetrated).passed
    widths = np.asarray(
        [
            section_parameters(model, float(x)).half_width_mm
            for x in np.linspace(model.x_min_mm, model.x_max_mm, 101)
        ]
    )
    v1_state = battery_state("v1")
    checks = {
        **{
            f"contract: {name}": passed
            for name, passed in fuselage_contract.validation_checks().items()
        },
        "B-spline basis is non-negative and partitions unity": (
            np.min(basis) >= -1e-12
            and np.max(np.abs(basis.sum(axis=1) - 1.0)) < 1e-12
        ),
        "reference section dimensions and exponents stay physical": all(
            (
                (item := section_parameters(model, float(x))).half_width_mm > 0.0
                and item.top_radius_mm > 0.0
                and item.bottom_radius_mm > 0.0
                and 2.0 <= item.exponent <= 5.0
            )
            for x in np.linspace(model.x_min_mm, model.x_max_mm, 81)
        ),
        "reference body is non-cylindrical": float(np.ptp(widths)) > 10.0,
        "reference mesh is closed and manifold": metrics.watertight,
        "reference mesh has positive volume and finite centroid": (
            metrics.signed_volume_m3 > 0.0
            and np.all(np.isfinite(metrics.centroid_mm))
        ),
        "all central inflated envelopes are contained": all(audit.passed for audit in audits),
        "camera lens face equals the forward OML plane": abs(
            next(item for item in model.envelopes if item.identifier == "o4_camera").minimum_mm[0]
            - model.x_min_mm
        ) < 1e-9,
        "seeded VTX penetration is detected": penetration_caught,
        "V1 battery travel miss remains visible and unclamped in the report": (
            not v1_state["reachable"]
            and v1_state["required_x_mm"] < v1_state["travel_min_x_mm"]
        ),
    }
    if not full:
        return checks

    refined = mesh_metrics(build_mesh(model, 121, 128))
    sphere_radius_mm = 10.0
    sphere_metrics = mesh_metrics(_uv_sphere(sphere_radius_mm))
    exact_sphere_area = 4.0 * pi * sphere_radius_mm**2 * 1e-6
    exact_sphere_volume = 4.0 / 3.0 * pi * sphere_radius_mm**3 * 1e-9
    translated = Mesh(mesh.vertices_mm + np.array((123.0, -41.0, 17.0)), mesh.faces)
    translated_metrics = mesh_metrics(translated)
    report = report_as_dict(model, 41, 48)
    checks.update(
        {
            "sphere mesh reproduces analytical area within 0.2 percent": abs(
                sphere_metrics.area_m2 / exact_sphere_area - 1.0
            ) < 0.002,
            "sphere mesh reproduces analytical volume within 0.3 percent": abs(
                sphere_metrics.volume_m3 / exact_sphere_volume - 1.0
            ) < 0.003,
            "closed-mesh area and volume are translation invariant": (
                abs(translated_metrics.area_m2 - metrics.area_m2) < 1e-12
                and abs(translated_metrics.volume_m3 - metrics.volume_m3) < 1e-12
            ),
            "reference mesh converges under doubled resolution": (
                abs(refined.area_m2 - metrics.area_m2) / refined.area_m2 < 0.005
                and abs(refined.volume_m3 - metrics.volume_m3) / refined.volume_m3 < 0.003
            ),
            "machine manifest is deterministic and ASCII-safe": (
                manifest_json(report) == manifest_json(report)
                and manifest_json(report).isascii()
            ),
        }
    )
    return checks


def main() -> None:
    model = reference_model()
    report = report_as_dict(model)
    print("=" * 78)
    print("SALAMANDRA PROVISIONAL FUSELAGE OML - NUMPY GEOMETRY AUDIT")
    print("=" * 78)
    print(f"  family            : {report['family_name']} {report['authority']}")
    print(f"  x range           : {model.x_min_mm:+.2f} .. {model.x_max_mm:+.2f} mm")
    print(f"  gross wetted area : {report['mesh']['area_m2']:.4f} m2")
    print(f"  gross volume      : {report['mesh']['volume_m3']*1e3:.3f} L")
    print(f"  gross 0.9 mm skin : {report['mesh']['gross_0p9_mm_skin_mass_g']:.1f} g [screen]")
    print("\nCENTRAL ENVELOPE AUDIT")
    for audit in report["envelope_audits"]:
        print(
            f"  [{'PASS' if audit['passed'] else 'FAIL'}] "
            f"{audit['identifier']:20s} margin={audit['minimum_margin_mm']:+.3f} mm"
        )
    print("\nPROJECT BLOCKERS (not software failures)")
    for name, passed in report["project_blockers"].items():
        print(f"  [{'PASS' if passed else 'OPEN'}] {name}")
    print(f"\n  geometry feasible : {report['geometry_feasible']}")
    print(f"  aircraft feasible : {report['aircraft_feasible']}")
    print(f"  {fuselage_contract.WARNING}")
    checks = validation_checks()
    print("\nSOFTWARE VALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS; OPEN DESIGN GATES REMAIN")


if __name__ == "__main__":
    main()
