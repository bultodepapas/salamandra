#!/usr/bin/env python3
"""I-31 flat-pack packaging and fuselage-length screening for Salamandra.

This is a first-order trade, not an OML generator.  It answers four questions
before a new fuselage is drawn:

1. what are the maximum-dimension envelopes of the selected flat 4S1P and
   6S1P P42A packs;
2. what longitudinal channel is required by the user's 10 mm adjustment
   request;
3. can both packs close the current aggregate CG model by battery movement
   alone; and
4. how do axial length changes scale skin-friction, forward side-area moment,
   beam flexibility and pack pitch inertia at screening level.

Coordinates use the project convention: x is positive aft and the origin is
the root quarter chord.  Pack dimensions are [D] from the P42A manufacturer
maxima [M] and the I-16 assembly allowances [E].  The 10 mm interpretation and
all scaling laws are explicitly [E].  No result in this file is manufacturing
authority and no OML or released battery-layout contract is changed.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from math import isclose

import balance_cg
import battery_pack_layout
import design_config
import fuselage_geometry


# The user asked for "1 cm additional" to accommodate cables and small mass
# changes.  The literal minimum is 10 mm TOTAL extra channel length.  Because
# the sign of a future CG error is unknown, the engineering recommendation is
# 10 mm travel in EACH direction.  Both are printed so the interpretation is
# never hidden in geometry.
USER_MINIMUM_TOTAL_RESERVE_MM = 10.0       # [E], stated requirement
RECOMMENDED_TRAVEL_EACH_WAY_MM = 10.0     # [E], symmetric trim recommendation


@dataclass(frozen=True)
class PackCase:
    configuration: str
    arrangement: str
    nx: int
    ny: int
    nz: int
    orientation: str


SELECTED_PACKS = (
    PackCase("4S1P", "2x2x1-A", 2, 2, 1, "A"),
    PackCase("6S1P", "3x2x1-A", 3, 2, 1, "A"),
)
CURRENT_COMPACT_6S = PackCase("6S1P", "2x3x1-A", 2, 3, 1, "A")


def maximum_cad_envelope_mm(case: PackCase) -> tuple[float, float, float]:
    """Installed L x W x H using manufacturer-maximum sleeved P42A cells.

    The calculation intentionally mirrors the generic I-16 model without
    changing its released reference layout.  The manufacturer maximum already
    includes the cell sleeve; only pack-level wrap, nickel and lead allowances
    are added here.
    """
    cell_length, cell_diameter = battery_pack_layout.CELL_MAX_DIMENSIONS_MM[
        "Molicel P42A"
    ]
    if case.orientation == "A":
        block = (
            case.nx * cell_length,
            case.ny * cell_diameter,
            case.nz * cell_diameter,
        )
    elif case.orientation == "B":
        block = (
            case.nx * cell_diameter,
            case.ny * cell_length,
            case.nz * cell_diameter,
        )
    else:
        raise ValueError(f"unsupported orientation {case.orientation!r}")
    length, width, height = block
    return (
        length
        + 2.0 * battery_pack_layout.PVC_OUTER
        + battery_pack_layout.LEAD_ADD,
        width + 2.0 * battery_pack_layout.PVC_OUTER,
        height
        + 2.0 * battery_pack_layout.PVC_OUTER
        + battery_pack_layout.NICKEL,
    )


def pack_record(case: PackCase) -> dict[str, object]:
    envelope = maximum_cad_envelope_mm(case)
    cell = battery_pack_layout.CELLS["Molicel P42A"]
    return {
        "configuration": case.configuration,
        "arrangement": case.arrangement,
        "cell_count": battery_pack_layout.cell_count(case.configuration),
        "mass_g": battery_pack_layout.pack_mass_g(case.configuration, "P42A"),
        "nominal_energy_Wh": case.nx * case.ny * case.nz * cell[5],
        "envelope_mm": envelope,
        "frontal_envelope_area_mm2": envelope[1] * envelope[2],
    }


def balance_screen() -> dict[str, object]:
    """Freeze the current non-battery aggregate and solve each pack station.

    This isolation is deliberate.  Re-solving the camera, boom and OML for
    each candidate would conceal how much fixed-mass redistribution is needed.
    The result is therefore a screening comparison, not a coupled closure.
    """
    reference = balance_cg.solve_reference_layout()
    target = balance_cg.cg_target()
    records: list[dict[str, object]] = []
    for case in SELECTED_PACKS:
        pack = pack_record(case)
        mass_kg = float(pack["mass_g"]) / 1000.0
        station_m = balance_cg.pack_station(
            reference["m0"], reference["moment0"], mass_kg, target
        )
        length_mm, width_mm, height_mm = pack["envelope_mm"]
        total_mass_kg = reference["m0"] + mass_kg
        orbital_pitch_inertia = mass_kg * (station_m - target) ** 2
        centroidal_pitch_inertia = mass_kg / 12.0 * (
            (length_mm / 1000.0) ** 2 + (height_mm / 1000.0) ** 2
        )
        records.append(
            {
                **pack,
                "required_station_mm": station_m * 1000.0,
                "cg_change_for_10_mm_pack_shift_mm": (
                    mass_kg / total_mass_kg * 10.0
                ),
                "pack_pitch_inertia_proxy_kg_m2": (
                    orbital_pitch_inertia + centroidal_pitch_inertia
                ),
                "physical_interval_mm": (
                    station_m * 1000.0 - length_mm / 2.0,
                    station_m * 1000.0 + length_mm / 2.0,
                ),
                "recommended_travel_interval_mm": (
                    station_m * 1000.0
                    - length_mm / 2.0
                    - RECOMMENDED_TRAVEL_EACH_WAY_MM,
                    station_m * 1000.0
                    + length_mm / 2.0
                    + RECOMMENDED_TRAVEL_EACH_WAY_MM,
                ),
            }
        )

    union_min = min(row["recommended_travel_interval_mm"][0] for row in records)
    union_max = max(row["recommended_travel_interval_mm"][1] for row in records)
    physical_min = min(row["physical_interval_mm"][0] for row in records)
    physical_max = max(row["physical_interval_mm"][1] for row in records)

    four_s, six_s = records
    four_s_mass_kg = four_s["mass_g"] / 1000.0
    six_s_station_m = six_s["required_station_mm"] / 1000.0
    required_fixed_moment = (
        target * (reference["m0"] + four_s_mass_kg)
        - four_s_mass_kg * six_s_station_m
    )
    fixed_moment_change = required_fixed_moment - reference["moment0"]

    body = fuselage_geometry.reference_model()
    lower_bound_length_mm = body.x_max_mm - min(body.x_min_mm, union_min)
    return {
        "model_scope": "current aggregate non-battery mass distribution held fixed",
        "target_cg_mm": target * 1000.0,
        "fixed_mass_kg": reference["m0"],
        "fixed_moment_kg_m": reference["moment0"],
        "packs": records,
        "required_station_separation_mm": abs(
            four_s["required_station_mm"] - six_s["required_station_mm"]
        ),
        "physical_union_mm": (physical_min, physical_max),
        "physical_union_length_mm": physical_max - physical_min,
        "recommended_union_mm": (union_min, union_max),
        "recommended_union_length_mm": union_max - union_min,
        "fixed_moment_change_to_colocate_4s_with_6s_kg_m": fixed_moment_change,
        "equivalent_140_g_forward_shift_mm": (
            -fixed_moment_change * 1.0e6 / 140.0
        ),
        "current_provisional_body_x_mm": (body.x_min_mm, body.x_max_mm),
        "current_provisional_body_length_mm": body.length_mm,
        "battery_only_forward_extension_beyond_current_body_mm": max(
            body.x_min_mm - union_min, 0.0
        ),
        "body_length_lower_bound_if_aft_end_fixed_mm": lower_bound_length_mm,
    }


def length_sensitivity() -> list[dict[str, float]]:
    """Constant-cross-section axial-stretch proxies relative to current OML.

    Wetted area is assumed proportional to length and the fully turbulent flat-
    plate coefficient follows Cf=0.074/Re_L**0.2.  The resulting friction-force
    ratio is r**0.8.  The r**2 side-area moment and r**3 supported-beam
    deflection relations are sensitivity flags, not Salamandra coefficients.
    """
    model = fuselage_geometry.reference_model()
    speed_m_s = design_config.CRUISE_SPEED_KMH / 3.6
    reference_re = speed_m_s * model.length_mm / 1000.0 / design_config.NU_SL
    reference_cf = 0.074 / reference_re ** 0.2
    rows = []
    for ratio in (0.85, 0.90, 1.00, 1.10, 1.20):
        length_mm = ratio * model.length_mm
        reynolds = speed_m_s * length_mm / 1000.0 / design_config.NU_SL
        cf = 0.074 / reynolds ** 0.2
        rows.append(
            {
                "length_ratio": ratio,
                "length_mm": length_mm,
                "Re_L": reynolds,
                "Cf_fully_turbulent": cf,
                "wetted_area_proxy": ratio,
                "skin_friction_force_proxy": ratio * cf / reference_cf,
                "forward_side_area_moment_proxy": ratio ** 2,
                "supported_beam_deflection_proxy": ratio ** 3,
            }
        )
    return rows


def results() -> dict[str, object]:
    selected = [pack_record(case) for case in SELECTED_PACKS]
    current = pack_record(CURRENT_COMPACT_6S)
    six_s = selected[1]
    physical_channel_length = max(row["envelope_mm"][0] for row in selected)
    balance = balance_screen()
    body_length_ratio = (
        balance["body_length_lower_bound_if_aft_end_fixed_mm"]
        / balance["current_provisional_body_length_mm"]
    )
    return {
        "authority": "[D] screening on [M]/[E]/[I]; not manufacturing authority",
        "selected_flat_packs": selected,
        "current_compact_6s_comparator": current,
        "packaging": {
            "same_selected_cross_section": (
                selected[0]["envelope_mm"][1:] == selected[1]["envelope_mm"][1:]
            ),
            "compact_to_long_6s_width_reduction_fraction": (
                1.0 - six_s["envelope_mm"][1] / current["envelope_mm"][1]
            ),
            "literal_minimum_channel_length_mm": (
                physical_channel_length + USER_MINIMUM_TOTAL_RESERVE_MM
            ),
            "recommended_symmetric_channel_length_mm": (
                physical_channel_length + 2.0 * RECOMMENDED_TRAVEL_EACH_WAY_MM
            ),
            "minimum_channel_cross_section_mm": six_s["envelope_mm"][1:],
            "warning": (
                "dimensions exclude bay wall, installation clearance, retainer, "
                "extraction path and measured cable-bend validation"
            ),
        },
        "balance": balance,
        "provisional_length_consequence": {
            "length_ratio": body_length_ratio,
            "constant_section_skin_friction_proxy": body_length_ratio ** 0.8,
            "uniform_forward_side_area_moment_proxy": body_length_ratio ** 2,
            "supported_beam_deflection_proxy": body_length_ratio ** 3,
            "warning": (
                "lower-bound sensitivity against a rejected/provisional OML; "
                "not a predicted drag or Cn_beta"
            ),
        },
        "length_sensitivity": length_sensitivity(),
    }


def validation_checks(data: dict[str, object] | None = None) -> dict[str, bool]:
    if data is None:
        data = results()
    four_s, six_s = data["selected_flat_packs"]
    compact = data["current_compact_6s_comparator"]
    balance = data["balance"]
    return {
        "selected layouts contain exactly four and six cells": (
            four_s["cell_count"] == 4 and six_s["cell_count"] == 6
        ),
        "selected flat packs share width and height": (
            four_s["envelope_mm"][1:] == six_s["envelope_mm"][1:]
        ),
        "long 6S is one maximum cell length longer than 4S": isclose(
            six_s["envelope_mm"][0] - four_s["envelope_mm"][0],
            battery_pack_layout.CELL_MAX_DIMENSIONS_MM["Molicel P42A"][0],
            abs_tol=1e-12,
        ),
        "new 6S is narrower than current compact 6S": (
            six_s["envelope_mm"][1] < compact["envelope_mm"][1]
        ),
        "recommended physical channel contains the longer pack plus travel": (
            data["packaging"]["recommended_symmetric_channel_length_mm"]
            >= six_s["envelope_mm"][0]
            + 2.0 * RECOMMENDED_TRAVEL_EACH_WAY_MM
        ),
        "current 4S balance station lies forward of 6S": (
            balance["packs"][0]["required_station_mm"]
            < balance["packs"][1]["required_station_mm"]
        ),
        "CG-compatible common rail exceeds physical-only channel": (
            balance["recommended_union_length_mm"]
            > data["packaging"]["recommended_symmetric_channel_length_mm"]
        ),
        "lighter 4S at its required station has greater pack pitch inertia proxy": (
            balance["packs"][0]["pack_pitch_inertia_proxy_kg_m2"]
            > balance["packs"][1]["pack_pitch_inertia_proxy_kg_m2"]
        ),
    }


def _fmt_triplet(values: tuple[float, float, float] | list[float]) -> str:
    return " x ".join(f"{value:.1f}" for value in values)


def print_report(data: dict[str, object]) -> None:
    print("=" * 78)
    print("SALAMANDRA I-31 - FLAT DUAL-PACK / FUSELAGE-LENGTH SCREEN")
    print("=" * 78)
    print("Selected maximum-dimension P42A pack envelopes:")
    for pack in data["selected_flat_packs"]:
        print(
            f"  {pack['configuration']:5s} {pack['arrangement']:8s}: "
            f"{_fmt_triplet(pack['envelope_mm'])} mm, "
            f"{pack['mass_g']:.0f} g, {pack['nominal_energy_Wh']:.1f} Wh"
        )
    compact = data["current_compact_6s_comparator"]
    width_reduction = (
        data["packaging"]["compact_to_long_6s_width_reduction_fraction"] * 100.0
    )
    print(
        f"  comparator current 6S {compact['arrangement']}: "
        f"{_fmt_triplet(compact['envelope_mm'])} mm"
    )
    print(f"  long/narrow 6S pack-envelope width reduction: {width_reduction:.1f} %")

    packaging = data["packaging"]
    print("\nPhysical common-channel screen (before walls/service evidence):")
    print(
        f"  literal +10 mm total: "
        f"{packaging['literal_minimum_channel_length_mm']:.1f} mm long"
    )
    print(
        f"  recommended +/-10 mm: "
        f"{packaging['recommended_symmetric_channel_length_mm']:.1f} mm long"
    )
    print(
        "  pack cross-section to contain: "
        + " x ".join(
            f"{value:.1f}"
            for value in packaging["minimum_channel_cross_section_mm"]
        )
        + " mm (width x height)"
    )

    balance = data["balance"]
    print("\nCurrent aggregate mass-balance screen (fixed non-battery layout):")
    for pack in balance["packs"]:
        print(
            f"  {pack['configuration']}: required x="
            f"{pack['required_station_mm']:+.1f} mm; 10 mm pack motion changes "
            f"aircraft CG by {pack['cg_change_for_10_mm_pack_shift_mm']:.2f} mm; "
            f"Iyy,pack~{pack['pack_pitch_inertia_proxy_kg_m2']:.5f} kg m^2"
        )
    print(
        f"  required pack-centre separation: "
        f"{balance['required_station_separation_mm']:.1f} mm"
    )
    print(
        f"  CG-compatible common rail with +/-10 mm per pack: "
        f"{balance['recommended_union_mm'][0]:+.1f}.."
        f"{balance['recommended_union_mm'][1]:+.1f} mm "
        f"({balance['recommended_union_length_mm']:.1f} mm)"
    )
    print(
        "  alternative fixed-mass redistribution to colocate pack centres: "
        f"{balance['fixed_moment_change_to_colocate_4s_with_6s_kg_m']:+.5f} "
        "kg m, equivalent to moving 140 g "
        f"{balance['equivalent_140_g_forward_shift_mm']:.0f} mm forward"
    )
    print(
        "  battery-only forward extension beyond current provisional body: "
        f">={balance['battery_only_forward_extension_beyond_current_body_mm']:.1f} mm"
    )

    consequence = data["provisional_length_consequence"]
    print("\nProvisional lower-bound consequence if the aft end is held fixed:")
    print(
        f"  body length ratio {consequence['length_ratio']:.3f}; "
        f"constant-section friction proxy "
        f"{consequence['constant_section_skin_friction_proxy']:.3f}; "
        f"uniform forward side-area-moment proxy "
        f"{consequence['uniform_forward_side_area_moment_proxy']:.3f}; "
        f"beam-deflection proxy "
        f"{consequence['supported_beam_deflection_proxy']:.3f}"
    )

    print("\nGeneric axial-length sensitivities at 95 km/h:")
    print("  L/L0     L (mm)       Re_L       Cf_turb   Df/Df0   yaw M/M0  beam d/d0")
    for row in data["length_sensitivity"]:
        print(
            f"  {row['length_ratio']:4.2f}   {row['length_mm']:8.1f}  "
            f"{row['Re_L']/1e6:7.3f}e6  {row['Cf_fully_turbulent']:.5f}   "
            f"{row['skin_friction_force_proxy']:7.3f}   "
            f"{row['forward_side_area_moment_proxy']:8.3f}   "
            f"{row['supported_beam_deflection_proxy']:9.3f}"
        )

    checks = validation_checks(data)
    print("\nValidation:")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    data = results()
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_report(data)


if __name__ == "__main__":
    main()
