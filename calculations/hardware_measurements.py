#!/usr/bin/env python3
"""Machine-readable MP-04 H01--H22 physical-measurement record contract.

The repository ships a synchronized blank template, not invented measurements.
Pending records are valid planning data; only a separate completed record with every
gate accepted and traceable evidence can close M1.
"""
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import isfinite
from pathlib import Path

import hardware_manifest


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = (
    ROOT / "tests" / "MP04-hardware-characterisation" / "measurement-template.json"
)
ALLOWED_STATUSES = {"pending", "measured", "accepted", "rejected"}


@dataclass(frozen=True)
class Field:
    name: str
    unit: str
    kind: str = "number"


@dataclass(frozen=True)
class Gate:
    identifier: str
    hardware_ids: tuple[str, ...]
    objective: str
    fields: tuple[Field, ...]


def _n(name: str, unit: str) -> Field:
    return Field(name, unit)


def _s(name: str) -> Field:
    return Field(name, "text", "string")


GATES = (
    Gate("H01", ("pack_6s1p_p42a",), "Complete 6S pack geometry, mass properties and usable energy",
         (_n("mass_g", "g"), _n("length_mm", "mm"), _n("width_mm", "mm"),
          _n("height_mm", "mm"), _n("mass_centre_from_forward_face_mm", "mm"),
          _n("connector_sweep_length_mm", "mm"), _n("usable_energy_wh", "Wh"))),
    Gate("H02", ("pack_8s1p_p42a",), "Complete 8S study pack or inert hard-dummy geometry",
         (_n("mass_or_ballasted_mass_g", "g"), _n("length_mm", "mm"),
          _n("width_mm", "mm"), _n("height_mm", "mm"),
          _n("mass_centre_from_forward_face_mm", "mm"),
          _n("connector_sweep_length_mm", "mm"))),
    Gate("H03", ("propeller_8x8",), "Reference propeller/adapter mass and multi-prop bench artifact",
         (_n("tested_propeller_count", "count"), _n("reference_propeller_mass_g", "g"),
          _n("adapter_mass_g", "g"), _n("maximum_test_rpm", "rpm"),
          _n("maximum_test_current_a", "A"), _n("maximum_test_temperature_c", "degC"))),
    Gate("H04", ("motor_6s_class",), "6S motor specimen geometry and electrical constants",
         (_s("selected_model"), _n("mass_g", "g"), _n("body_length_mm", "mm"),
          _n("body_diameter_mm", "mm"), _n("mass_centre_from_mount_mm", "mm"),
          _n("measured_kv_rpm_per_v", "rpm/V"), _n("phase_resistance_mohm", "mOhm"),
          _n("maximum_bench_temperature_c", "degC"))),
    Gate("H05", ("motor_8s_class",), "8S-study motor specimen and voltage/RPM/thermal proof",
         (_s("selected_model"), _n("mass_g", "g"), _n("body_length_mm", "mm"),
          _n("body_diameter_mm", "mm"), _n("measured_kv_rpm_per_v", "rpm/V"),
          _n("maximum_test_rpm", "rpm"), _n("maximum_bench_temperature_c", "degC"))),
    Gate("H06", ("esc_6s_class",), "6S ESC efficiency, control and thermal map",
         (_s("selected_model"), _n("installed_mass_g", "g"), _n("length_mm", "mm"),
          _n("width_mm", "mm"), _n("height_mm", "mm"),
          _n("efficiency_at_o1_boundary", "fraction"), _n("maximum_current_a", "A"),
          _n("maximum_temperature_c", "degC"))),
    Gate("H07", ("esc_8s_class",), "8S ESC voltage, efficiency and thermal proof",
         (_s("selected_model"), _n("installed_mass_g", "g"),
          _n("maximum_bus_voltage_v", "V"), _n("efficiency_at_o1_boundary", "fraction"),
          _n("maximum_current_a", "A"), _n("maximum_temperature_c", "degC"))),
    Gate("H08", ("fc_6s",), "FC hardware/firmware resources, mass and current calibration",
         (_s("hardware_revision"), _s("firmware_target_and_version"), _n("mass_g", "g"),
          _n("idle_current_ma", "mA"), _n("current_scale_error_pct", "%"),
          _n("available_uart_count", "count"), _n("available_servo_output_count", "count"))),
    Gate("H09", ("pdb_6s",), "6S PDB stack, every regulated rail, ripple and heat",
         (_n("stack_mass_g", "g"), _n("stack_height_mm", "mm"),
          _n("five_volt_rail_error_pct", "%"), _n("servo_rail_error_pct", "%"),
          _n("vtx_rail_error_pct", "%"), _n("maximum_ripple_mv_peak_to_peak", "mVpp"),
          _n("maximum_temperature_c", "degC"))),
    Gate("H10", ("fc_pdb_8s_class",), "Selected 8S-rated FC/PDB/BEC/logging assembly proof",
         (_s("selected_assembly"), _n("installed_mass_g", "g"),
          _n("maximum_test_voltage_v", "V"), _n("maximum_ripple_mv_peak_to_peak", "mVpp"),
          _n("current_scale_error_pct", "%"), _n("maximum_temperature_c", "degC"))),
    Gate("H11", ("elevon_servos",), "Two-servo batch deadband, stiffness, rate, current and heat",
         (_n("pair_mass_g", "g"), _n("maximum_deadband_deg", "deg"),
          _n("maximum_backlash_deg", "deg"), _n("minimum_rate_deg_per_s", "deg/s"),
          _n("minimum_output_stiffness_nm_per_rad", "N*m/rad"),
          _n("maximum_stall_current_a_each", "A"), _n("maximum_temperature_c", "degC"))),
    Gate("H12", ("rudder_servo_reserve",), "R-module actuator specimen after M5 sizing",
         (_s("selected_model"), _n("mass_g", "g"), _n("maximum_deadband_deg", "deg"),
          _n("minimum_rate_deg_per_s", "deg/s"), _n("maximum_stall_current_a", "A"))),
    Gate("H13", ("o4_camera",), "Camera/lens datum, mount mass and optical keep-out",
         (_n("camera_with_mount_mass_g", "g"), _n("lens_datum_x_mm", "mm"),
          _n("lens_datum_y_mm", "mm"), _n("lens_datum_z_mm", "mm"),
          _n("connector_keepout_length_mm", "mm"), _n("minimum_unobstructed_fov_deg", "deg"))),
    Gate("H14", ("o4_vtx_antenna",), "VTX/coax/antenna installed route, power and cooling",
         (_n("installed_mass_g", "g"), _n("minimum_coax_bend_radius_mm", "mm"),
          _n("maximum_current_a", "A"), _n("maximum_power_w", "W"),
          _n("maximum_temperature_c", "degC"))),
    Gate("H15", ("gps_mag",), "GNSS harness/current and installed magnetic-interference proof",
         (_n("installed_mass_g", "g"), _n("harness_length_mm", "mm"),
          _n("current_ma", "mA"), _n("maximum_compass_deviation_deg", "deg"),
          _n("minimum_satellite_count", "count"))),
    Gate("H16", ("pitot_sensor",), "Differential-pressure board envelope, zero, scale and leak proof",
         (_n("installed_mass_g", "g"), _n("length_mm", "mm"), _n("width_mm", "mm"),
          _n("height_mm", "mm"), _n("zero_offset_pa", "Pa"),
          _n("scale_error_pct", "%"), _n("leak_rate_pa_per_s", "Pa/s"),
          _n("current_ma", "mA"))),
    Gate("H17", ("pitot_probe_tubing",), "Probe, fittings and tube-route installed measurement",
         (_n("installed_mass_g", "g"), _n("probe_length_mm", "mm"),
          _n("tube_route_length_mm", "mm"), _n("maximum_outer_diameter_mm", "mm"),
          _n("assembled_leak_rate_pa_per_s", "Pa/s"))),
    Gate("H18", ("receiver",), "Receiver hardware/firmware, current, failsafe and range proof",
         (_s("firmware_version"), _n("installed_mass_g", "g"), _n("current_ma", "mA"),
          _n("failsafe_latency_ms", "ms"), _n("ground_range_m", "m"))),
    Gate("H19", ("receiver_antenna",), "Chosen antenna/pigtail geometry and installed RF result",
         (_n("installed_mass_g", "g"), _n("route_length_mm", "mm"),
          _n("minimum_bend_radius_mm", "mm"), _n("range_test_minimum_lq_pct", "%"))),
    Gate("H20", ("buzzer",), "Buzzer part, mass, current and through-shell function",
         (_s("selected_model"), _n("installed_mass_g", "g"), _n("current_ma", "mA"),
          _n("sound_level_at_1m_dba", "dBA"))),
    Gate("H21", ("blackbox_card",), "Card identity and complete-rate logging integrity",
         (_s("selected_card"), _n("capacity_gb", "GB"), _n("logging_rate_hz", "Hz"),
          _n("test_duration_s", "s"), _n("dropped_frame_pct", "%"),
          _n("decode_error_count", "count"))),
    Gate("H22", ("installation_reserve",), "Replace distributed reserve with weighed installation line items",
         (_n("wire_mass_g", "g"), _n("connector_mass_g", "g"),
          _n("mount_and_strain_relief_mass_g", "g"), _n("service_loop_mass_g", "g"),
          _n("measured_installation_total_g", "g"),
          _n("catalog_reserve_delta_g", "g"))),
)


def template_data() -> dict[str, object]:
    return {
        "schema": "salamandra-mp04-hardware-measurements-v1",
        "authority": "BLANK-TEMPLATE-NOT-MEASURED-EVIDENCE",
        "article": "SALAMANDRA Article #1",
        "created_utc": None,
        "measurement_environment": {
            "location": None,
            "ambient_temperature_c": None,
            "ambient_pressure_pa": None,
            "instruments_file": None,
        },
        "gates": [
            {
                "gate_id": gate.identifier,
                "hardware_ids": list(gate.hardware_ids),
                "objective": gate.objective,
                "status": "pending",
                "specimen_ids": [],
                "operator": None,
                "measured_utc": None,
                "evidence_files": [],
                "measurements": {
                    field.name: {"value": None, "unit": field.unit}
                    for field in gate.fields
                },
            }
            for gate in GATES
        ],
    }


def rendered_template() -> str:
    return json.dumps(template_data(), indent=2, ensure_ascii=False) + "\n"


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.utcoffset() == timedelta(0)


def _nonempty_string_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _completed_self_test_record() -> dict[str, object]:
    """Return synthetic schema data used only to prove the validator can pass."""
    data = deepcopy(template_data())
    data["authority"] = "SCHEMA-SELF-TEST-NOT-MEASURED-EVIDENCE"
    data["created_utc"] = "2026-08-21T00:00:00Z"
    for record, gate in zip(data["gates"], GATES):
        record["status"] = "accepted"
        record["specimen_ids"] = [f"SELF-TEST-{gate.identifier}"]
        record["operator"] = "schema-self-test"
        record["measured_utc"] = "2026-08-21T00:00:00Z"
        record["evidence_files"] = [f"self-test/{gate.identifier}.txt"]
        for field in gate.fields:
            record["measurements"][field.name]["value"] = (
                1.0 if field.kind == "number" else "schema-self-test"
            )
    return data


def validate_record(data: dict[str, object], require_closure: bool = False) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "salamandra-mp04-hardware-measurements-v1":
        errors.append("schema identifier is missing or unsupported")
    records = data.get("gates")
    if not isinstance(records, list):
        return errors + ["gates must be a list"]
    by_id = {record.get("gate_id"): record for record in records if isinstance(record, dict)}
    expected_ids = [gate.identifier for gate in GATES]
    if list(by_id) != expected_ids or len(records) != len(GATES):
        errors.append("record must contain H01--H22 exactly once and in order")
    for gate in GATES:
        record = by_id.get(gate.identifier)
        if not isinstance(record, dict):
            continue
        status = record.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{gate.identifier}: invalid status")
            continue
        if record.get("hardware_ids") != list(gate.hardware_ids):
            errors.append(f"{gate.identifier}: hardware ownership changed")
        measurements = record.get("measurements")
        if not isinstance(measurements, dict):
            errors.append(f"{gate.identifier}: measurements must be an object")
            continue
        if list(measurements) != [field.name for field in gate.fields]:
            errors.append(f"{gate.identifier}: measurement field set/order is stale")
            continue
        for field in gate.fields:
            datum = measurements.get(field.name)
            if not isinstance(datum, dict) or datum.get("unit") != field.unit:
                errors.append(f"{gate.identifier}.{field.name}: unit contract changed")
                continue
            value = datum.get("value")
            if value is not None:
                kind_ok = (
                    field.kind == "number" and isinstance(value, (int, float))
                    and not isinstance(value, bool) and isfinite(value)
                ) or (field.kind == "string" and isinstance(value, str) and bool(value.strip()))
                if not kind_ok:
                    errors.append(f"{gate.identifier}.{field.name}: wrong value type")
        if status in {"measured", "accepted", "rejected"}:
            if not _nonempty_string_list(record.get("specimen_ids")):
                errors.append(f"{gate.identifier}: physical status lacks specimen IDs")
            operator = record.get("operator")
            if not isinstance(operator, str) or not operator.strip():
                errors.append(f"{gate.identifier}: physical status lacks operator")
            if not _valid_timestamp(record.get("measured_utc")):
                errors.append(f"{gate.identifier}: physical status lacks UTC timestamp")
            if not _nonempty_string_list(record.get("evidence_files")):
                errors.append(f"{gate.identifier}: physical status lacks evidence files")
        if status == "accepted" and any(
            measurements[field.name]["value"] is None for field in gate.fields
        ):
            errors.append(f"{gate.identifier}: accepted gate has missing values")
        if require_closure and status != "accepted":
            errors.append(f"{gate.identifier}: M1 closure requires accepted status")
    return errors


def validation_checks() -> dict[str, bool]:
    manifest_ids = {item.identifier for item in hardware_manifest.HARDWARE}
    controlled_ids = {identifier for gate in GATES for identifier in gate.hardware_ids}
    completed = _completed_self_test_record()
    malformed = deepcopy(completed)
    malformed["gates"][0]["measured_utc"] = "2026-08-21T00:00:00"
    malformed["gates"][0]["evidence_files"] = "not-a-list"
    malformed["gates"][0]["measurements"]["mass_g"]["value"] = float("inf")
    return {
        "H01--H22 are present exactly once": (
            [gate.identifier for gate in GATES]
            == [f"H{number:02d}" for number in range(1, 23)]
        ),
        "every MP-03 hardware row has one MP-04 measurement owner": (
            controlled_ids == manifest_ids
            and sum(len(gate.hardware_ids) for gate in GATES) == len(manifest_ids)
        ),
        "blank template is schema-valid but does not claim M1 closure": (
            not validate_record(template_data())
            and bool(validate_record(template_data(), require_closure=True))
        ),
        "complete self-test record can close the schema contract": (
            not validate_record(completed, require_closure=True)
        ),
        "non-UTC, non-list and non-finite evidence is rejected": (
            len(validate_record(malformed, require_closure=True)) >= 3
        ),
        "published blank template is current": (
            TEMPLATE_PATH.is_file()
            and TEMPLATE_PATH.read_text(encoding="utf-8") == rendered_template()
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-template", action="store_true")
    parser.add_argument("--write-template", action="store_true")
    parser.add_argument("--record", type=Path, default=TEMPLATE_PATH)
    parser.add_argument("--require-closure", action="store_true")
    parser.add_argument("--check", action="store_true", help="check the repository template")
    args = parser.parse_args()
    if args.render_template:
        print(rendered_template(), end="")
        return 0
    if args.write_template:
        TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        TEMPLATE_PATH.write_text(rendered_template(), encoding="utf-8")
        print(f"Wrote {TEMPLATE_PATH.relative_to(ROOT)}")
        return 0
    if args.check:
        checks = validation_checks()
        for name, passed in checks.items():
            print(f"[{'PASS' if passed else 'FAIL'}] {name}")
        return 0 if all(checks.values()) else 1
    data = json.loads(args.record.read_text(encoding="utf-8"))
    errors = validate_record(data, require_closure=args.require_closure)
    print(f"MP-04 record: {args.record}")
    print(f"Schema errors: {len(errors)}")
    for error in errors:
        print(f"  [FAIL] {error}")
    accepted = sum(record.get("status") == "accepted" for record in data.get("gates", []))
    print(f"Accepted gates: {accepted}/{len(GATES)}")
    print("M1 status: CLOSED" if accepted == len(GATES) and not errors else "M1 status: OPEN")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
