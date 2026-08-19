#!/usr/bin/env python3
"""Connected 3-D scene, orthographic projections and propeller clearance.

The scene is the numerical bridge between the component ledger, the coupled V1
packaging solution, the directional-surface geometry and generated drawings.
Coordinates are millimetres: x aft, y starboard and z up.  The clearance stack
is an engineering envelope `[E]/[I]`, not a substitute for the F2 static and
powered physical tests.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import equipment_layout
from yaw_stability import (
    FIN_BOOM_WIDTH_M,
    FIN_ROOT_THICKNESS_M,
    fin_area_for_target,
    fin_geometry,
)

Vec2 = tuple[float, float]
Vec3 = tuple[float, float, float]


@dataclass(frozen=True)
class PropellerAllowance:
    """Radial/axial inflation terms in millimetres `[E]/[I]`."""

    blade_deflection_mm: float = 5.0
    shaft_runout_mm: float = 1.0
    support_deflection_mm: float = 3.0
    assembly_tolerance_mm: float = 2.0
    residual_margin_mm: float = 5.0
    axial_dynamic_mm: float = 5.0

    @property
    def radial_total_mm(self) -> float:
        return (
            self.blade_deflection_mm
            + self.shaft_runout_mm
            + self.support_deflection_mm
            + self.assembly_tolerance_mm
            + self.residual_margin_mm
        )


@dataclass(frozen=True)
class PropellerHazard:
    centre_mm: Vec3
    nominal_radius_mm: float
    nominal_axial_half_mm: float
    allowance: PropellerAllowance

    @property
    def inflated_radius_mm(self) -> float:
        return self.nominal_radius_mm + self.allowance.radial_total_mm

    @property
    def inflated_axial_half_mm(self) -> float:
        return self.nominal_axial_half_mm + self.allowance.axial_dynamic_mm


@dataclass(frozen=True)
class FinPropellerClearance:
    boom_nominal_mm: float
    boom_residual_mm: float
    fin_nominal_mm: float
    fin_residual_mm: float
    axial_overlap_mm: float
    axial_residual_mm: float
    controlling_object: str
    analytical_pass: bool
    physical_status: str


@dataclass(frozen=True)
class AircraftScene:
    variant: str
    layout: equipment_layout.Layout3D
    propeller: PropellerHazard
    fin: object | None
    clearance: FinPropellerClearance | None
    packaging: equipment_layout.CoupledPackagingSolution | None


def component_corners(component: equipment_layout.Component3D) -> tuple[Vec3, ...]:
    """Return the eight exact corners of an oriented component envelope."""
    rotation = component.rotation_matrix()
    half = tuple(value / 2.0 for value in component.size_mm)
    corners = []
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                local = (sx * half[0], sy * half[1], sz * half[2])
                world = tuple(
                    component.position_mm[i]
                    + sum(rotation[i][j] * local[j] for j in range(3))
                    for i in range(3)
                )
                corners.append(world)
    return tuple(corners)  # type: ignore[return-value]


def project_point(point_mm: Vec3, view: str) -> Vec2:
    """Project one physical point into a named orthographic physical plane."""
    x, y, z = point_mm
    if view == "top":
        return x, y
    if view == "side":
        return x, z
    if view == "rear":
        return y, z
    raise ValueError("view must be 'top', 'side' or 'rear'")


def projected_bounds(
    component: equipment_layout.Component3D, view: str
) -> tuple[Vec2, Vec2]:
    """Axis-aligned bounds of the exact oriented-box projection."""
    points = tuple(project_point(point, view) for point in component_corners(component))
    return (
        (min(point[0] for point in points), min(point[1] for point in points)),
        (max(point[0] for point in points), max(point[1] for point in points)),
    )


def propeller_hazard(layout: equipment_layout.Layout3D) -> PropellerHazard:
    propeller = layout.component("propeller")
    return PropellerHazard(
        centre_mm=propeller.position_mm,
        nominal_radius_mm=max(propeller.size_mm[1:]) / 2.0,
        nominal_axial_half_mm=propeller.size_mm[0] / 2.0,
        allowance=PropellerAllowance(),
    )


def fin_propeller_clearance(layout: equipment_layout.Layout3D):
    """Calculate controlling nominal and inflated V1 radial clearance."""
    propeller = propeller_hazard(layout)
    fin = fin_geometry(fin_area_for_target(0.0005))
    boom_inner_radius = (
        fin.lateral_station_m * 1000.0 - FIN_BOOM_WIDTH_M * 500.0
    )
    fin_inner_radius = (
        fin.lateral_station_m * 1000.0 - FIN_ROOT_THICKNESS_M * 500.0
    )
    boom_nominal = boom_inner_radius - propeller.nominal_radius_mm
    fin_nominal = fin_inner_radius - propeller.nominal_radius_mm
    boom_residual = boom_inner_radius - propeller.inflated_radius_mm
    fin_residual = fin_inner_radius - propeller.inflated_radius_mm
    hazard_min_x = propeller.centre_mm[0] - propeller.inflated_axial_half_mm
    hazard_max_x = propeller.centre_mm[0] + propeller.inflated_axial_half_mm
    fin_min_x = min(fin.root_le_x_m, fin.tip_le_x_m) * 1000.0
    fin_max_x = max(fin.root_te_x_m, fin.tip_te_x_m) * 1000.0
    axial_overlap = max(
        0.0, min(fin_max_x, hazard_max_x) - max(fin_min_x, hazard_min_x)
    )
    controlling = "boom fairing" if boom_residual <= fin_residual else "fin shell"
    axial_residual = hazard_min_x - fin_max_x
    passed = min(boom_residual, fin_residual, axial_residual) >= 0.0
    return FinPropellerClearance(
        boom_nominal_mm=float(boom_nominal),
        boom_residual_mm=float(boom_residual),
        fin_nominal_mm=float(fin_nominal),
        fin_residual_mm=float(fin_residual),
        axial_overlap_mm=float(axial_overlap),
        axial_residual_mm=float(axial_residual),
        controlling_object=controlling,
        analytical_pass=bool(passed),
        physical_status=(
            "ANALYTICAL PASS / F2 PHYSICAL OPEN"
            if passed else "ANALYTICAL FAIL"
        ),
    )


def reference_scene(variant: str = "clean") -> AircraftScene:
    key = variant.lower()
    if key == "clean":
        layout, _ = equipment_layout.solve_battery_x(
            equipment_layout.reference_layout("clean")
        )
        return AircraftScene(
            variant="CLEAN",
            layout=layout,
            propeller=propeller_hazard(layout),
            fin=None,
            clearance=None,
            packaging=None,
        )
    if key == "v1":
        packaging = equipment_layout.solve_v1_packaging()
        layout = packaging.layout
        return AircraftScene(
            variant="V1",
            layout=layout,
            propeller=propeller_hazard(layout),
            fin=fin_geometry(fin_area_for_target(0.0005)),
            clearance=fin_propeller_clearance(layout),
            packaging=packaging,
        )
    raise ValueError("variant must be 'clean' or 'v1'")


def validation_checks() -> dict[str, bool]:
    clean = reference_scene("clean")
    v1 = reference_scene("v1")
    clearance = v1.clearance
    assert clearance is not None
    prop = v1.layout.component("propeller")
    side_min, side_max = projected_bounds(prop, "side")
    rear_min, rear_max = projected_bounds(prop, "rear")
    return {
        "all three orthographic projections preserve component centre": all(
            project_point(prop.position_mm, view)
            == tuple(
                0.5 * (low + high)
                for low, high in zip(*projected_bounds(prop, view))
            )
            for view in ("top", "side", "rear")
        ),
        "propeller side and rear projections use the ledger diameter": (
            abs(side_max[1] - side_min[1] - prop.size_mm[2]) < 1e-9
            and abs(rear_max[0] - rear_min[0] - prop.size_mm[1]) < 1e-9
            and abs(rear_max[1] - rear_min[1] - prop.size_mm[2]) < 1e-9
        ),
        "V1 boom controls the inflated radial clearance": (
            clearance.controlling_object == "boom fairing"
            and clearance.boom_residual_mm < clearance.fin_residual_mm
        ),
        "V1 analytical envelope clears while physical verification stays open": (
            clearance.analytical_pass
            and clearance.physical_status.endswith("PHYSICAL OPEN")
        ),
        "side-view fin is separated from the inflated propeller slab": (
            clearance.axial_overlap_mm == 0.0
            and clearance.axial_residual_mm >= 0.0
        ),
        "CLEAN and V1 consume the same canonical propeller definition": (
            clean.propeller.centre_mm == v1.propeller.centre_mm
            and clean.propeller.nominal_radius_mm == v1.propeller.nominal_radius_mm
        ),
    }


def main() -> None:
    scene = reference_scene("v1")
    clearance = scene.clearance
    packaging = scene.packaging
    assert clearance is not None and packaging is not None
    print("SALAMANDRA CONNECTED AIRCRAFT SCENE")
    print(f"V1 mass: {scene.layout.mass_g():.2f} g")
    print(f"V1 CG: {scene.layout.cg_mm()[0]:+.3f} mm")
    print(f"Nose extension: {packaging.nose_extension_mm:.2f} mm")
    print(
        "Central carrier datum length: "
        f"{packaging.central_carrier_length_mm:.2f} mm"
    )
    print(f"Boom nominal/residual prop clearance: "
          f"{clearance.boom_nominal_mm:.1f}/{clearance.boom_residual_mm:.1f} mm")
    print(f"Fin-to-inflated-propeller axial residual: "
          f"{clearance.axial_residual_mm:.2f} mm "
          f"(overlap {clearance.axial_overlap_mm:.1f} mm)")
    for name, passed in validation_checks().items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    raise SystemExit(0 if all(validation_checks().values()) else 1)


if __name__ == "__main__":
    main()
