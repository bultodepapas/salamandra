#!/usr/bin/env python3
"""Authoritative bought-in equipment catalog for Salamandra packaging models.

This module separates manufacturer product data from project-derived or estimated
installation envelopes. Aircraft position and movement authority remain in
``equipment_layout.py``; bought-in mass and body dimensions belong here so the mass
budget, packaging model and generated drawings cannot silently diverge.

Dimensions use the manufacturer's Length x Width x Height order in millimetres.
Masses are grams. Source pages were re-verified on 2026-08-18.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isclose

Vec3 = tuple[float, float, float]

DJI_O4_SOURCE_URL = "https://www.dji.com/support/product/o4-air-unit"


@dataclass(frozen=True)
class EquipmentSpec:
    """One purchased component with evidence kept per quantitative property."""

    product: str
    role: str
    mass_g: float
    envelope_mm: Vec3
    mass_authority: str
    envelope_authority: str
    source_url: str
    envelope_basis: str

    def __post_init__(self) -> None:
        if self.mass_g <= 0.0:
            raise ValueError(f"{self.product}: mass must be positive")
        if any(value <= 0.0 for value in self.envelope_mm):
            raise ValueError(f"{self.product}: envelope dimensions must be positive")


# DJI calls this product "DJI O4 Air Unit". "O4 Lite" is retained only as a
# legacy project/market alias; it is not the manufacturer product name.
DJI_O4_CAMERA = EquipmentSpec(
    product="DJI O4 Air Unit",
    role="camera module",
    mass_g=3.10,
    envelope_mm=(13.44, 12.36, 16.50),
    mass_authority="[D]",
    envelope_authority="[M]",
    source_url=DJI_O4_SOURCE_URL,
    envelope_basis=(
        "DJI LxWxH; mass derived as 8.20 g camera-included air unit minus "
        "5.10 g transmission module"
    ),
)

DJI_O4_TRANSMISSION_MODULE = EquipmentSpec(
    product="DJI O4 Air Unit",
    role="transmission module",
    mass_g=5.10,
    envelope_mm=(30.0, 30.0, 6.0),
    mass_authority="[M]",
    envelope_authority="[M]",
    source_url=DJI_O4_SOURCE_URL,
    envelope_basis="DJI LxWxH body envelope; installation requires cooling airflow",
)

DJI_O4_ANTENNA = EquipmentSpec(
    product="DJI O4 Air Unit",
    role="single antenna",
    mass_g=0.75,
    envelope_mm=(80.0, 5.0, 5.0),
    mass_authority="[M]",
    envelope_authority="[M]/[E]",
    source_url=DJI_O4_SOURCE_URL,
    envelope_basis=(
        "80 mm overall length from DJI; 5 x 5 mm transverse routing keep-out is "
        "a conservative project estimate, not a manufacturer body dimension"
    ),
)

DJI_O4_COAX_LENGTH_MM = 50.0
DJI_O4_AIR_UNIT_BODY_MASS_G = 8.20
DJI_O4_TRANSMISSION_ASSEMBLY_MASS_G = (
    DJI_O4_TRANSMISSION_MODULE.mass_g + DJI_O4_ANTENNA.mass_g
)
DJI_O4_INSTALLED_MASS_G = (
    DJI_O4_CAMERA.mass_g
    + DJI_O4_TRANSMISSION_ASSEMBLY_MASS_G
)


def validation_checks() -> dict[str, bool]:
    return {
        "camera and transmission masses close to DJI 8.2 g air-unit mass": isclose(
            DJI_O4_CAMERA.mass_g + DJI_O4_TRANSMISSION_MODULE.mass_g,
            DJI_O4_AIR_UNIT_BODY_MASS_G,
            abs_tol=1e-12,
        ),
        "installed O4 mass includes the separate DJI antenna": isclose(
            DJI_O4_INSTALLED_MASS_G, 8.95, abs_tol=1e-12
        ),
        "layout may lump antenna mass into the transmission assembly": isclose(
            DJI_O4_TRANSMISSION_ASSEMBLY_MASS_G, 5.85, abs_tol=1e-12
        ),
        "camera retains manufacturer LxWxH axis order": (
            DJI_O4_CAMERA.envelope_mm == (13.44, 12.36, 16.50)
        ),
        "transmission module retains manufacturer LxWxH axis order": (
            DJI_O4_TRANSMISSION_MODULE.envelope_mm == (30.0, 30.0, 6.0)
        ),
        "antenna transverse keep-out remains explicitly estimated": (
            DJI_O4_ANTENNA.envelope_authority == "[M]/[E]"
        ),
    }


def main() -> int:
    checks = validation_checks()
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
