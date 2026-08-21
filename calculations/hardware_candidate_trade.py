#!/usr/bin/env python3
"""MP-04 catalog screen for Article #1 motor and ESC procurement candidates.

This module does not select a flight powertrain.  It converts current manufacturer
data into repeatable voltage, Kv/RPM, mass and packaging screens so that physical
specimens can be purchased without treating catalog performance as a bench map.

The propeller target is the APC E 8x8 O1 power-boundary RPM from
``propulsion_match.py``.  Its equilibrium remains unknown until E2 supplies measured
aircraft drag.  The 0.70--0.85 loaded/no-load ratio and 5% explicit ESC overvoltage
headroom are declared procurement heuristics [E], not component ratings.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from math import isclose

import battery_pack_layout
import propulsion_match


CONFIG_6S = "6S"
CONFIG_8S = "8S-STUDY"
LOADED_RATIO_BAND = (0.70, 0.85)  # [E], purchase-screen heuristic
MIN_EXPLICIT_ESC_VOLTAGE_MARGIN_FRACTION = 0.05  # [E], transient headroom screen


@dataclass(frozen=True)
class MotorCandidate:
    identifier: str
    configuration: str
    manufacturer: str
    model: str
    procurement_rank: str
    kv_rpm_per_v: float
    minimum_cells: int
    maximum_cells: int
    mass_including_cables_g: float
    body_lwh_mm: tuple[float, float, float]
    cable_length_mm: float
    maximum_current_a_180s: float
    maximum_power_w_180s: float
    source_url: str
    source_note: str


@dataclass(frozen=True)
class EscCandidate:
    identifier: str
    configuration: str
    manufacturer: str
    model: str
    procurement_rank: str
    minimum_cells: int
    maximum_cells: int
    explicit_maximum_voltage_v: float | None
    continuous_current_a: float
    burst_current_a: float
    catalog_mass_g: float
    body_lwh_mm: tuple[float, float, float]
    telemetry: str
    source_url: str
    source_note: str


@dataclass(frozen=True)
class PropellerCandidate:
    identifier: str
    manufacturer: str
    model: str
    procurement_rank: str
    diameter_in: float
    pitch_in: float
    catalog_mass_g: float
    hub_diameter_in: float
    hub_thickness_in: float
    source_url: str


MOTORS = (
    MotorCandidate(
        "tmotor_mn3110_kv470", CONFIG_6S, "T-Motor", "MN3110 KV470",
        "PRIMARY-PROCUREMENT", 470.0, 3, 6, 98.0, (28.5, 37.7, 37.7),
        600.0, 15.0, 330.0,
        "https://store.tmotor.com/product/mn3110-motor-navigator-type.html",
        "Manufacturer table; body is axial length x diameter x diameter; mass includes 600 mm leads.",
    ),
    MotorCandidate(
        "tmotor_mn4010_kv475", CONFIG_6S, "T-Motor", "MN4010 KV475",
        "ROBUST-ALTERNATE", 475.0, 4, 8, 137.0, (30.5, 44.7, 44.7),
        600.0, 30.0, 540.0,
        "https://store.tmotor.com/product/mn4010-kv580-motor-navigator-type.html",
        "Manufacturer table; body is axial length x diameter x diameter; mass includes 600 mm leads.",
    ),
    MotorCandidate(
        "tmotor_mn4010_kv370", CONFIG_8S, "T-Motor", "MN4010 KV370",
        "PRIMARY-STUDY", 370.0, 4, 8, 137.0, (30.5, 44.7, 44.7),
        600.0, 20.0, 450.0,
        "https://store.tmotor.com/product/mn4010-kv580-motor-navigator-type.html",
        "Manufacturer table; 4--8S rating. No manufacturer 8x8 propeller map is transferred.",
    ),
    MotorCandidate(
        "tmotor_mn4012_kv400", CONFIG_8S, "T-Motor", "MN4012 KV400",
        "ROBUST-STUDY-ALTERNATE", 400.0, 4, 8, 155.0, (32.5, 44.7, 44.7),
        600.0, 25.0, 750.0,
        "https://store.tmotor.com/product/mn4012-kv480-motor-navigator-type.html",
        "Manufacturer table; body is axial length x diameter x diameter; mass includes 600 mm leads.",
    ),
)


ESCS = (
    EscCandidate(
        "apd_80f3x_v2_6s", CONFIG_6S, "Advanced Power Drives", "80F3[X]v2",
        "PRIMARY-PROCUREMENT", 4, 8, 34.0, 80.0, 140.0, 20.0,
        (44.0, 22.0, 12.0), "DShot/ProShot and telemetry; PWM path requires bench proof",
        "https://powerdrives.net/80f3",
        "Used only on 6S here; 8S full charge leaves only 0.4 V to the published maximum.",
    ),
    EscCandidate(
        "hobbywing_flyfun_60a_v5", CONFIG_6S, "Hobbywing", "FlyFun 60A V5",
        "BENCH-BACKUP", 3, 6, None, 60.0, 80.0, 73.0,
        (69.0, 35.0, 18.0), "PWM; no propulsion telemetry claimed",
        "https://www.hobbywing.com/uploads/file/20220817/308d789701a8209b133476865a0ac754.pdf",
        "Manufacturer specifies 3--6S categorically but no separate absolute-voltage limit.",
    ),
    EscCandidate(
        "apd_120f3x_v2_8s", CONFIG_8S, "Advanced Power Drives", "120F3[X]v2",
        "PRIMARY-STUDY", 4, 12, 50.4, 120.0, 200.0, 20.0,
        (70.0, 30.0, 20.0), "DShot/ProShot and telemetry; PWM path requires bench proof",
        "https://powerdrives.net/120f3",
        "12S voltage class preserves explicit headroom over a fully charged 8S pack.",
    ),
    EscCandidate(
        "hobbywing_flyfun_80a_v5", CONFIG_8S, "Hobbywing", "FlyFun 80A V5",
        "BENCH-BACKUP", 3, 8, None, 80.0, 100.0, 92.0,
        (70.0, 35.0, 19.0), "PWM; no propulsion telemetry claimed",
        "https://www.hobbywing.com/uploads/file/20220817/308d789701a8209b133476865a0ac754.pdf",
        "Manufacturer specifies 3--8S categorically but no separate absolute-voltage limit.",
    ),
    EscCandidate(
        "apd_40f3_boundary_reject", CONFIG_6S, "Advanced Power Drives", "40F3",
        "REJECT-VOLTAGE-HEADROOM", 3, 6, 25.5, 40.0, 100.0, 3.0,
        (30.0, 16.0, 5.0), "DShot/ProShot and telemetry",
        "https://powerdrives.net/40f3",
        "A 25.2 V full 6S pack leaves only 0.3 V to the published maximum.",
    ),
    EscCandidate(
        "apd_80f3x_boundary_reject", CONFIG_8S, "Advanced Power Drives", "80F3[X]v2",
        "REJECT-VOLTAGE-HEADROOM", 4, 8, 34.0, 80.0, 140.0, 20.0,
        (44.0, 22.0, 12.0), "DShot/ProShot and telemetry",
        "https://powerdrives.net/80f3",
        "A 33.6 V full 8S pack leaves only 0.4 V to the published maximum.",
    ),
)


PROPELLERS = (
    PropellerCandidate(
        "apc_8x8e", "APC", "8x8E", "REFERENCE-DATUM", 8.0, 8.0,
        0.53 * 28.349523125, 0.80, 0.40,
        "https://www.apcprop.com/product/8x8e/",
    ),
    PropellerCandidate(
        "apc_8x6e", "APC", "8x6E", "PITCH-SENSITIVITY", 8.0, 6.0,
        0.49 * 28.349523125, 0.80, 0.37,
        "https://www.apcprop.com/product/8x6e/",
    ),
    PropellerCandidate(
        "apc_9x7_5e", "APC", "9x7.5E", "DIAMETER-SENSITIVITY-CONDITIONAL",
        9.0, 7.5, 0.63 * 28.349523125, 0.80, 0.39,
        "https://www.apcprop.com/product/9x7-5e/",
    ),
)


def series_count(configuration: str) -> int:
    if configuration == CONFIG_6S:
        return 6
    if configuration == CONFIG_8S:
        return 8
    raise ValueError(f"unknown configuration {configuration!r}")


def pack_voltages(configuration: str) -> tuple[float, float]:
    cells = series_count(configuration)
    nominal = cells * battery_pack_layout.CELLS["Molicel P42A"][2]
    full = cells * battery_pack_layout.P42A_VOLTAGE_FULL_V
    return nominal, full


def motor_screen(candidate: MotorCandidate) -> dict[str, float | bool]:
    cells = series_count(candidate.configuration)
    nominal_v, full_v = pack_voltages(candidate.configuration)
    target_rpm = propulsion_match.o1_boundary().rpm
    ratio = target_rpm / (candidate.kv_rpm_per_v * nominal_v)
    full_no_load_rpm = candidate.kv_rpm_per_v * full_v
    return {
        "target_rpm": target_rpm,
        "nominal_voltage_v": nominal_v,
        "full_voltage_v": full_v,
        "loaded_no_load_ratio": ratio,
        "full_charge_no_load_rpm": full_no_load_rpm,
        "cell_count_compatible": candidate.minimum_cells <= cells <= candidate.maximum_cells,
        "loaded_ratio_in_planning_band": LOADED_RATIO_BAND[0] <= ratio <= LOADED_RATIO_BAND[1],
        "full_charge_no_load_below_apc_limit": full_no_load_rpm < propulsion_match.APC_MAX_RPM,
    }


def esc_screen(candidate: EscCandidate) -> dict[str, float | bool | None]:
    cells = series_count(candidate.configuration)
    _nominal_v, full_v = pack_voltages(candidate.configuration)
    margin_v = None
    margin_fraction = None
    explicit_margin_pass = None
    if candidate.explicit_maximum_voltage_v is not None:
        margin_v = candidate.explicit_maximum_voltage_v - full_v
        margin_fraction = margin_v / full_v
        explicit_margin_pass = margin_fraction >= MIN_EXPLICIT_ESC_VOLTAGE_MARGIN_FRACTION
    return {
        "full_voltage_v": full_v,
        "cell_count_compatible": candidate.minimum_cells <= cells <= candidate.maximum_cells,
        "explicit_voltage_margin_v": margin_v,
        "explicit_voltage_margin_fraction": margin_fraction,
        "explicit_voltage_margin_pass": explicit_margin_pass,
    }


def propeller_screen(candidate: PropellerCandidate) -> dict[str, float | bool]:
    rpm_limit = 150_000.0 / candidate.diameter_in
    maximum_shortlist_no_load_rpm = max(
        motor_screen(motor)["full_charge_no_load_rpm"] for motor in MOTORS
    )
    return {
        "diameter_mm": candidate.diameter_in * 25.4,
        "pitch_mm": candidate.pitch_in * 25.4,
        "apc_thin_electric_rpm_limit": rpm_limit,
        "maximum_shortlist_full_charge_no_load_rpm": maximum_shortlist_no_load_rpm,
        "no_load_rpm_below_apc_limit": maximum_shortlist_no_load_rpm < rpm_limit,
    }


def procurement_shortlist() -> dict[str, list[str]]:
    return {
        CONFIG_6S: [
            "tmotor_mn3110_kv470", "tmotor_mn4010_kv475",
            "apd_80f3x_v2_6s", "hobbywing_flyfun_60a_v5",
        ],
        CONFIG_8S: [
            "tmotor_mn4010_kv370", "tmotor_mn4012_kv400",
            "apd_120f3x_v2_8s", "hobbywing_flyfun_80a_v5",
        ],
    }


def export_data() -> dict[str, object]:
    return {
        "authority": "CATALOG-SCREEN-NOT-FLIGHT-SELECTION",
        "loaded_ratio_band_estimate": list(LOADED_RATIO_BAND),
        "minimum_explicit_esc_voltage_margin_fraction_estimate": (
            MIN_EXPLICIT_ESC_VOLTAGE_MARGIN_FRACTION
        ),
        "motors": [
            {**asdict(candidate), "screen": motor_screen(candidate)}
            for candidate in MOTORS
        ],
        "escs": [
            {**asdict(candidate), "screen": esc_screen(candidate)}
            for candidate in ESCS
        ],
        "propellers": [
            {**asdict(candidate), "screen": propeller_screen(candidate)}
            for candidate in PROPELLERS
        ],
        "shortlist": procurement_shortlist(),
    }


def validation_checks() -> dict[str, bool]:
    motor_ids = {candidate.identifier for candidate in MOTORS}
    esc_ids = {candidate.identifier for candidate in ESCS}
    propeller_ids = {candidate.identifier for candidate in PROPELLERS}
    shortlisted = {
        identifier
        for identifiers in procurement_shortlist().values()
        for identifier in identifiers
    }
    selected_motor_screens = [
        motor_screen(candidate) for candidate in MOTORS
        if "REJECT" not in candidate.procurement_rank
    ]
    apd_6s = next(candidate for candidate in ESCS
                  if candidate.identifier == "apd_80f3x_v2_6s")
    apd_8s = next(candidate for candidate in ESCS
                  if candidate.identifier == "apd_120f3x_v2_8s")
    rejected = [candidate for candidate in ESCS
                if candidate.procurement_rank == "REJECT-VOLTAGE-HEADROOM"]
    return {
        "candidate identifiers are unique": (
            len(motor_ids) == len(MOTORS) and len(esc_ids) == len(ESCS)
            and len(propeller_ids) == len(PROPELLERS)
            and not motor_ids.intersection(esc_ids | propeller_ids)
            and not esc_ids.intersection(propeller_ids)
        ),
        "shortlist names only controlled candidates": shortlisted <= motor_ids | esc_ids,
        "all shortlisted motors pass cell, Kv/RPM and APC-limit screens": all(
            screen["cell_count_compatible"]
            and screen["loaded_ratio_in_planning_band"]
            and screen["full_charge_no_load_below_apc_limit"]
            for screen in selected_motor_screens
        ),
        "6S primary ESC preserves at least 5 percent explicit voltage headroom": (
            esc_screen(apd_6s)["explicit_voltage_margin_pass"] is True
        ),
        "8S primary ESC preserves at least 5 percent explicit voltage headroom": (
            esc_screen(apd_8s)["explicit_voltage_margin_pass"] is True
        ),
        "boundary-rated APD alternatives are rejected by the voltage policy": all(
            esc_screen(candidate)["explicit_voltage_margin_pass"] is False
            for candidate in rejected
        ),
        "all propeller sensitivity articles stay below the APC RPM rule": all(
            propeller_screen(candidate)["no_load_rpm_below_apc_limit"]
            for candidate in PROPELLERS
        ),
        "P42A pack voltage model is 21.6/25.2 V for 6S": (
            all(isclose(a, b, abs_tol=1e-12)
                for a, b in zip(pack_voltages(CONFIG_6S), (21.6, 25.2)))
        ),
        "P42A pack voltage model is 28.8/33.6 V for 8S": (
            all(isclose(a, b, abs_tol=1e-12)
                for a, b in zip(pack_voltages(CONFIG_8S), (28.8, 33.6)))
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit all candidate data")
    args = parser.parse_args()
    if args.json:
        print(json.dumps(export_data(), indent=2, sort_keys=True))
        return 0

    target = propulsion_match.o1_boundary().rpm
    print("SALAMANDRA MP-04 — MOTOR/ESC PROCUREMENT SCREEN")
    print(f"O1 boundary target: {target:.0f} rpm (not an aircraft equilibrium)")
    print("\nMotors")
    for candidate in MOTORS:
        screen = motor_screen(candidate)
        print(
            f"  {candidate.model:16s} {candidate.configuration:8s} "
            f"ratio={screen['loaded_no_load_ratio']:.3f}; "
            f"full no-load={screen['full_charge_no_load_rpm']:.0f} rpm; "
            f"mass={candidate.mass_including_cables_g:.0f} g; "
            f"{candidate.procurement_rank}"
        )
    print("\nESCs")
    for candidate in ESCS:
        screen = esc_screen(candidate)
        margin = screen["explicit_voltage_margin_v"]
        margin_text = "categorical cell rating" if margin is None else f"{margin:+.1f} V"
        print(
            f"  {candidate.model:16s} {candidate.configuration:8s} "
            f"full-charge margin={margin_text}; mass={candidate.catalog_mass_g:.0f} g; "
            f"{candidate.procurement_rank}"
        )
    print("\nPropellers")
    for candidate in PROPELLERS:
        screen = propeller_screen(candidate)
        print(
            f"  {candidate.model:16s} mass={candidate.catalog_mass_g:.1f} g; "
            f"limit={screen['apc_thin_electric_rpm_limit']:.0f} rpm; "
            f"{candidate.procurement_rank}"
        )
    print("\nValidation")
    checks = validation_checks()
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        return 1
    print("\nRESULT: procurement shortlist is numerically consistent; D2 bench selection remains open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
