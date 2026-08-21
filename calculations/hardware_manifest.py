#!/usr/bin/env python3
"""MP-03 candidate hardware and electrical-power manifest for Article #1.

The manifest is the machine-readable M1 interface used before the redesigned
mass skeleton exists.  It distinguishes a named reference part from a bounded
reference class and from a packaging reservation.  None of those statuses is a
released production part: MP-04 must measure the procured batch and MP-05 must
close the complete instrumentation chain.

Dimensions use manufacturer L x W x H order in millimetres unless an envelope
explicitly says that it is an installation or distributed-allocation bound.
Masses are grams.  Electrical values are volts, amperes and watts.  The 6S and
8S configurations are imported from the Gate-M0 mission contract so a hardware
row cannot silently invent another aircraft configuration.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from math import isclose, sqrt
from pathlib import Path

import battery_6s_8s_trade
import equipment_catalog
import fpv_power_budget
import mission_contract


ROOT = Path(__file__).resolve().parent.parent
DOCUMENT_PATH = ROOT / "docs" / "17-article-1-hardware-manifest.md"

BEGIN_MARKER = (
    "<!-- BEGIN GENERATED: MP-03 hardware manifest · "
    "calculations/hardware_manifest.py · do not edit by hand -->"
)
END_MARKER = "<!-- END GENERATED: MP-03 hardware manifest -->"

REFERENCE_PART = "REFERENCE-PART"
REFERENCE_CLASS = "REFERENCE-CLASS"
RESERVED_ENVELOPE = "RESERVED-ENVELOPE"
STUDY_CLASS = "STUDY-CLASS"
ALLOWED_STATUSES = {
    REFERENCE_PART,
    REFERENCE_CLASS,
    RESERVED_ENVELOPE,
    STUDY_CLASS,
}

CONFIG_6S_R = "6S-R"
CONFIG_6S_CLEAN = "6S-CLEAN"
CONFIG_8S_STUDY = "8S-STUDY"
CONFIGURATION_IDS = tuple(
    configuration.identifier for configuration in mission_contract.CONFIGURATIONS
)

BATTERY_TRAVEL_TOTAL_MM = mission_contract.MINIMUM_BATTERY_TRAVEL_TOTAL_MM
BEC_EFFICIENCY = 0.90  # [E], shared with the current power models


@dataclass(frozen=True)
class EnvelopeOption:
    """One sourced or bounded physical envelope for a hardware item."""

    name: str
    dimensions_mm: tuple[float, float, float]
    authority: str
    basis: str

    def __post_init__(self) -> None:
        if not self.name or any(value <= 0.0 for value in self.dimensions_mm):
            raise ValueError("hardware envelopes require a name and positive dimensions")


@dataclass(frozen=True)
class HardwareItem:
    """One installed item, repeated item, or explicit unresolved allocation."""

    identifier: str
    category: str
    identity: str
    status: str
    configurations: tuple[str, ...]
    quantity: int
    mass_each_g: float
    mass_sigma_each_g: float
    mass_authority: str
    envelopes: tuple[EnvelopeOption, ...]
    input_voltage_range_v: tuple[float, float] | None
    continuous_current_a: float | None
    peak_current_a: float | None
    interfaces: str
    installation_constraints: str
    source: str
    closure: str

    def __post_init__(self) -> None:
        if not self.identifier or any(char.isspace() for char in self.identifier):
            raise ValueError("hardware identifier must be non-empty and whitespace-free")
        if self.status not in ALLOWED_STATUSES:
            raise ValueError(f"{self.identifier}: uncontrolled status {self.status}")
        if not self.configurations or not set(self.configurations) <= set(
            CONFIGURATION_IDS
        ):
            raise ValueError(f"{self.identifier}: invalid configuration membership")
        if self.quantity < 1 or self.mass_each_g <= 0.0:
            raise ValueError(f"{self.identifier}: quantity and mass must be positive")
        if self.mass_sigma_each_g < 0.0 or not self.envelopes:
            raise ValueError(f"{self.identifier}: uncertainty/envelope is invalid")
        if self.input_voltage_range_v is not None:
            low, high = self.input_voltage_range_v
            if low <= 0.0 or high < low:
                raise ValueError(f"{self.identifier}: voltage range is invalid")
        currents = (self.continuous_current_a, self.peak_current_a)
        if any(value is not None and value < 0.0 for value in currents):
            raise ValueError(f"{self.identifier}: current cannot be negative")
        if (
            self.continuous_current_a is not None
            and self.peak_current_a is not None
            and self.peak_current_a < self.continuous_current_a
        ):
            raise ValueError(f"{self.identifier}: peak current is below continuous")

    @property
    def installed_mass_g(self) -> float:
        return self.quantity * self.mass_each_g

    @property
    def installed_mass_sigma_g(self) -> float:
        # Conservative within one repeated batch: its item errors are correlated.
        return self.quantity * self.mass_sigma_each_g


@dataclass(frozen=True)
class PowerLoad:
    """One downstream hotel-load branch at reference, design and brief peak."""

    identifier: str
    configurations: tuple[str, ...]
    rail: str
    voltage_v: float
    reference_current_a: float
    design_current_a: float
    brief_peak_current_a: float
    authority: str
    basis: str

    def __post_init__(self) -> None:
        if not set(self.configurations) <= set(CONFIGURATION_IDS):
            raise ValueError(f"{self.identifier}: invalid power-load configuration")
        if not (
            self.voltage_v > 0.0
            and 0.0 <= self.reference_current_a <= self.design_current_a
            <= self.brief_peak_current_a
        ):
            raise ValueError(f"{self.identifier}: invalid current ladder")


@dataclass(frozen=True)
class PowerRail:
    """Installed 6S rail or minimum required 8S-study rail capacity."""

    identifier: str
    configurations: tuple[str, ...]
    rail: str
    source_hardware: str
    voltage_v: float
    continuous_capacity_a: float
    peak_capacity_a: float
    status: str
    authority: str

    def __post_init__(self) -> None:
        if not set(self.configurations) <= set(CONFIGURATION_IDS):
            raise ValueError(f"{self.identifier}: invalid rail configuration")
        if not (
            self.voltage_v > 0.0
            and 0.0 < self.continuous_capacity_a <= self.peak_capacity_a
        ):
            raise ValueError(f"{self.identifier}: invalid rail capacity")


def _envelope(
    name: str,
    dimensions_mm: tuple[float, float, float],
    authority: str,
    basis: str,
) -> EnvelopeOption:
    return EnvelopeOption(name, dimensions_mm, authority, basis)


CONFIGS_6S = (CONFIG_6S_R, CONFIG_6S_CLEAN)
CONFIGS_ALL = CONFIGURATION_IDS

PACK_6S_MASS_G = battery_6s_8s_trade.pack_mass_g(6)
PACK_8S_MASS_G = battery_6s_8s_trade.pack_mass_g(8)
PACK_MASS_SIGMA_G = battery_6s_8s_trade.PACK_HARDWARE_UNCERTAINTY_G


HARDWARE = (
    HardwareItem(
        "pack_6s1p_p42a", "energy", "6S1P Molicel INR-21700-P42A pack",
        REFERENCE_PART, CONFIGS_6S, 1, PACK_6S_MASS_G, PACK_MASS_SIGMA_G,
        "[D]/[E]",
        (
            _envelope("flat-narrow", (223.2, 44.0, 22.6), "[D]",
                      "3x2x1-A; maximum cells plus wrap, nickel and folded-lead allowance"),
            _envelope("flat-moderate", (142.8, 70.8, 22.6), "[D]",
                      "6x1x1-B; maximum cells plus wrap, nickel and folded-lead allowance"),
        ),
        None, None, None, "XT60-class main connector; balance harness; removable rail",
        "Envelope options exclude bay walls, extraction clearance and the separate "
        "20 mm total CG travel.",
        "I-32; Molicel P42A v4 product data", "MP-04 H01: build and measure pack, leads, connector sweep, mass centre and usable energy.",
    ),
    HardwareItem(
        "pack_8s1p_p42a", "energy", "8S1P Molicel INR-21700-P42A study pack",
        STUDY_CLASS, (CONFIG_8S_STUDY,), 1, PACK_8S_MASS_G, PACK_MASS_SIGMA_G,
        "[D]/[E]",
        (
            _envelope("flat-narrow", (293.4, 44.0, 22.6), "[D]",
                      "4x2x1-A; maximum cells plus wrap, nickel and folded-lead allowance"),
            _envelope("flat-moderate", (186.2, 70.8, 22.6), "[D]",
                      "8x1x1-B; maximum cells plus wrap, nickel and folded-lead allowance"),
        ),
        None, None, None, "Separate 8S main connector, balance harness and power module",
        "Not a 6S carrier or power-chain swap; travel and service volumes remain separate.",
        "I-32; Molicel P42A v4 product data", "MP-04 H02: build a hard dummy or pack and measure the complete 8S installation.",
    ),
    HardwareItem(
        "propeller_8x8", "propulsion", "APC Thin Electric 8x8 datum plus adapter",
        REFERENCE_PART, CONFIGS_ALL, 1, 25.0, 3.0, "[M]/[E]",
        (_envelope("rotating-disk", (25.4, 203.2, 203.2), "[M]/[E]",
                   "8-inch disk; 25.4 mm axial hazard bound pending measured hub/adapter"),),
        None, None, None, "Motor shaft/adapter; fixed pusher plane",
        "Rotating hazard, ground clearance and pusher inflow are external keep-outs.",
        "APC product/RPM data and UIUC APC 8x8 curve; I-03/I-32", "MP-04 H03: weigh blade/adapter and bench-map at least two credible propeller alternatives.",
    ),
    HardwareItem(
        "motor_6s_class", "propulsion", "28-class 500-550 Kv, approximately 400 W or greater",
        REFERENCE_CLASS, CONFIGS_6S, 1, 170.0, 30.0, "[E]",
        (_envelope("class-bound", (35.0, 28.0, 28.0), "[E]",
                   "historical packaging class; shaft, wires and mount excluded"),),
        (14.8, 25.2), None, None, "Three-phase ESC output; centreline pusher mount",
        "Shaft, connector, cooling and rotating-bell clearances remain unmeasured.",
        "Master Plan section 3; I-03/I-32 voltage/Kv screen", "MP-04 H04: shortlist real motors, then measure mass, Kv, winding resistance, envelope and thermal map.",
    ),
    HardwareItem(
        "motor_8s_class", "propulsion", "8S 375-413 Kv starting class, approximately 400 W or greater",
        STUDY_CLASS, (CONFIG_8S_STUDY,), 1, 170.0, 30.0, "[E]",
        (_envelope("class-bound", (35.0, 28.0, 28.0), "[E]",
                   "provisional equality bound; no product selected"),),
        (19.8, 33.6), None, None, "Separate 8S ESC and centreline pusher mount",
        "No credit for 8S efficiency until the complete motor/ESC/propeller map exists.",
        "I-32 voltage/Kv screen", "MP-04 H05: select and bench an 8S motor candidate without exceeding propeller RPM or temperature limits.",
    ),
    HardwareItem(
        "esc_6s_class", "power", "6S ESC, 30 A continuous minimum, telemetry preferred",
        REFERENCE_CLASS, CONFIGS_6S, 1, 35.0, 10.0, "[E]",
        (_envelope("class-bound", (60.0, 30.0, 15.0), "[E]",
                   "historical 6S packaging estimate; wires/capacitor excluded"),),
        (14.8, 25.2), 30.0, 40.0, "6S pack bus; motor phases; throttle/telemetry",
        "Cooling airflow, capacitor, lead bends and braking behavior are open.",
        "Master Plan section 3; existing mass/layout model", "MP-04 H06: select with the motor and measure efficiency, current, rpm, temperature and failure behavior.",
    ),
    HardwareItem(
        "esc_8s_class", "power", "8S ESC, 30 A continuous minimum, telemetry preferred",
        STUDY_CLASS, (CONFIG_8S_STUDY,), 1, 45.0, 15.0, "[E]",
        (_envelope("class-bound", (70.0, 35.0, 18.0), "[E]",
                   "study allowance; wires/capacitor excluded"),),
        (19.8, 33.6), 30.0, 40.0, "8S pack bus; motor phases; throttle/telemetry",
        "Must be an explicitly 8S-rated part; the 6S ESC is not reused by assumption.",
        "I-32 separate-power-module requirement", "MP-04 H07: select and bench with the 8S motor, PDB/BEC and propeller.",
    ),
    HardwareItem(
        "fc_6s", "flight-control", "SpeedyBee F405 WING FC board",
        REFERENCE_PART, CONFIGS_6S, 1, 8.9, 0.3, "[M]",
        (_envelope("body", (36.5, 36.5, 7.0), "[M]", "manufacturer LxWxH"),),
        (5.0, 5.2), 0.250, 0.250, "5.2 V FC rail; MicroSD; PWM/UART/I2C",
        "30.5 mm mounting pattern, IMU near dynamic centre and USB/SD service access.",
        "SpeedyBee F405 WING official specification; I-17", "MP-04 H08: procure board, verify resources/firmware and measure mass/current/current-sensor calibration.",
    ),
    HardwareItem(
        "pdb_6s", "power-distribution", "SpeedyBee F405 WING PDB/current/BEC board",
        REFERENCE_PART, CONFIGS_6S, 1, 11.4, 0.5, "[M]",
        (_envelope("body-bound", (36.5, 36.5, 5.0), "[M]/[E]",
                   "planform and mass manufacturer data; thickness is an installation estimate"),),
        (7.0, 25.2), 90.0, 215.0, "6S pack bus and measured current; 5.2 V, 5 V VTX and 6 V servo rails",
        "Official categorical limit is 2-6S; the numerical 36 V line does not qualify 8S use.",
        "SpeedyBee F405 WING official specification; I-17/I-32", "MP-04 H09: measure complete board stack, rail regulation, ripple, current calibration and thermal margin.",
    ),
    HardwareItem(
        "fc_pdb_8s_class", "flight-control", "8S-qualified FC/PDB/BEC/current-logging assembly",
        STUDY_CLASS, (CONFIG_8S_STUDY,), 1, 40.0, 15.0, "[E]",
        (_envelope("station-bound", (64.0, 45.0, 21.0), "[D]/[E]",
                   "I-17 all-board service cavity; not a component body"),),
        (19.8, 33.6), 30.0, 40.0, "8S pack bus; blackbox; calibrated current; low-voltage and servo rails",
        "No product selected. It must preserve pitot, GPS/mag, receiver, O4 and servo resources.",
        "I-17 catalog envelope and I-32 8S requirement", "MP-04 H10: select an 8S-rated logging/power assembly and bench every rail at 33.6 V.",
    ),
    HardwareItem(
        "elevon_servos", "actuation", "Corona DS-939MG reference pair",
        REFERENCE_PART, CONFIGS_ALL, 2, 12.5, 0.5, "[M]",
        (_envelope("body", (22.5, 11.5, 24.6), "[M]", "catalog LxWxH per servo"),),
        (4.8, 6.0), 0.300, 1.000, "One regulated PWM servo per elevon",
        "Final count, pocket and linkage follow M5; no freeplay/stiffness credit before bench test.",
        "I-18 catalog; ADR-0026 is candidate-only", "MP-04 H11: measure both servos for mass, travel, rate, deadband, backlash, stiffness, current and heat at 6 V.",
    ),
    HardwareItem(
        "rudder_servo_reserve", "actuation", "Digital metal-gear rudder servo, 15 g maximum class",
        RESERVED_ENVELOPE, (CONFIG_6S_R,), 1, 12.5, 2.5, "[E]",
        (_envelope("reserved-pocket", (34.0, 16.0, 39.0), "[D]/[E]",
                   "I-18 catalog maximum plus clearance; deliberately larger than the reference part"),),
        (4.8, 6.0), 0.300, 1.000, "Regulated servo rail; removable R-module harness",
        "Reservation is not purchase authority; movable area, torque and rate remain M5 outputs.",
        "Master Plan section 1.4 and I-18 class envelope", "MP-04 H12/M5: replace the reserve with a selected actuator after rudder hinge-load and rate closure.",
    ),
    HardwareItem(
        "o4_camera", "fpv", "DJI O4 Air Unit camera module",
        REFERENCE_PART, CONFIGS_ALL, 1, equipment_catalog.DJI_O4_CAMERA.mass_g, 0.3,
        "[D]",
        (_envelope("body", equipment_catalog.DJI_O4_CAMERA.envelope_mm, "[M]", "DJI LxWxH"),),
        None, None, None, "50 mm coax to transmission module; forward optical aperture",
        "Fixed front-facing centreline station; preserve true FOV and service access.",
        "DJI O4 official specification; equipment_catalog.py; I-19", "MP-04 H13: measure camera/lens-mount mass, true lens datum, connector and FOV keep-out.",
    ),
    HardwareItem(
        "o4_vtx_antenna", "fpv", "DJI O4 Air Unit transmission module plus antenna",
        REFERENCE_PART, CONFIGS_ALL, 1,
        equipment_catalog.DJI_O4_TRANSMISSION_ASSEMBLY_MASS_G, 0.4, "[M]/[D]",
        (_envelope("vtx-body", equipment_catalog.DJI_O4_TRANSMISSION_MODULE.envelope_mm,
                   "[M]", "DJI transmission-module LxWxH; antenna route separate"),),
        (3.7, 13.2), 1.200, 1.200, "5 V VTX rail; 50 mm camera coax; 80 mm antenna route; UART",
        "Forced cooling and RF clearance required; antenna volume is not hidden in the VTX body.",
        "DJI O4 official specification; I-19 measured power", "MP-04 H14: mock connector/coax/antenna routes and measure current/temperature at selected settings.",
    ),
    HardwareItem(
        "gps_mag", "navigation", "Matek M10Q-5883 GNSS/magnetometer",
        REFERENCE_PART, CONFIGS_ALL, 1, 8.0, 0.5, "[M]",
        (_envelope("body", (20.0, 20.0, 12.4), "[M]", "manufacturer LxWxH"),),
        (4.0, 9.0), 0.013, 0.060, "5 V rail; UART GNSS; I2C compass",
        "External sky view and separation from battery, PDB, ESC, motor and carbon/current paths.",
        "Matek M10Q-5883 official specification; I-17", "MP-04 H15: measure harness/current and run installed magnetic-interference tests.",
    ),
    HardwareItem(
        "pitot_sensor", "air-data", "Matek ASPD-4525 differential-pressure board",
        REFERENCE_PART, CONFIGS_ALL, 1, 3.5, 0.5, "[M]",
        (_envelope("board-bound", (30.0, 20.0, 10.0), "[E]",
                   "existing packaging bound; manufacturer mass but no released body dimensions in source"),),
        (4.0, 5.5), 0.005, 0.015, "5 V rail; shared I2C; two pneumatic ports",
        "Short, leak-free tubing and serviceable zero/calibration access.",
        "Matek ASPD-4525 official specification; existing equipment layout", "MP-04 H16: measure board/harness envelope, leak rate, zero, scale and current.",
    ),
    HardwareItem(
        "pitot_probe_tubing", "air-data", "Pitot probe, 400 mm tubing and fittings allowance",
        RESERVED_ENVELOPE, CONFIGS_ALL, 1, 5.0, 3.0, "[E]",
        (_envelope("route-bound", (360.0, 8.0, 8.0), "[E]",
                   "distributed route allocation; not a rigid-body envelope"),),
        None, None, None, "Probe to ASPD-4525 pressure ports",
        "Route outside prop wash and separated from wiring pinch/heat sources.",
        "ASPD-4525 kit contents and existing equipment layout", "MP-04 H17: assemble and measure the real probe, fittings, tube route and installed mass.",
    ),
    HardwareItem(
        "receiver", "radio-control", "Happymodel EP1 2.4 GHz ELRS receiver",
        REFERENCE_PART, CONFIGS_ALL, 1, 0.42, 0.10, "[M]",
        (_envelope("body", (10.0, 10.0, 3.0), "[M]", "manufacturer LxWxH without antenna"),),
        (5.0, 5.0), 0.200, 0.200, "5 V rail; CRSF UART; external antenna",
        "Failsafe and RF installation must be verified in the complete airframe.",
        "Happymodel EP1 official specification; ExpressLRS", "MP-04 H18: procure, update firmware, measure current and perform range/failsafe tests.",
    ),
    HardwareItem(
        "receiver_antenna", "radio-control", "EP1 omnidirectional antenna installation allowance",
        RESERVED_ENVELOPE, CONFIGS_ALL, 1, 0.8, 0.4, "[E]",
        (_envelope("route-bound", (90.0, 4.0, 4.0), "[M]/[E]",
                   "manufacturer 90 mm supplied option; transverse keep-out estimated"),),
        None, None, None, "U.FL-class receiver connection and RF keep-out",
        "Keep clear of carbon, VTX, current path and propeller hazard.",
        "Happymodel EP1 supplied antenna; existing equipment layout", "MP-04 H19: measure chosen antenna/pigtail and validate installed RSSI/LQ.",
    ),
    HardwareItem(
        "buzzer", "recovery", "5 V self-driven buzzer class",
        REFERENCE_CLASS, CONFIGS_ALL, 1, 2.0, 1.0, "[E]",
        (_envelope("class-bound", (15.0, 15.0, 10.0), "[E]", "existing packaging allowance"),),
        (5.0, 5.0), 0.030, 0.030, "5 V rail and FC buzzer output",
        "Audible aperture and service access required.",
        "I-17 power budget; existing equipment layout", "MP-04 H20: select and measure part, current and sound function through the shell.",
    ),
    HardwareItem(
        "blackbox_card", "instrumentation", "SDSC/SDHC MicroSD blackbox card",
        REFERENCE_CLASS, CONFIGS_ALL, 1, 0.5, 0.5, "[E]",
        (_envelope("card", (15.0, 11.0, 1.0), "[M]", "MicroSD form factor"),),
        None, None, None, "FC MicroSD slot; synchronized flight log",
        "Card must be retention-safe, serviceable and validated for sustained logging.",
        "I-17 blackbox requirement and SpeedyBee manual", "MP-04 H21: select card and verify complete-rate logging without dropped samples.",
    ),
    HardwareItem(
        "installation_reserve", "installation", "Distributed avionics wiring/connectors/mounts reserve",
        RESERVED_ENVELOPE, CONFIGS_ALL, 1, 72.38, 30.0, "[E]",
        (_envelope("distributed-allocation", (180.0, 80.0, 25.0), "[E]",
                   "mass-budget allocation only; explicitly not one cavity or rigid body"),),
        None, None, None, "Power/signal harnesses, connectors, mounts and strain relief",
        "Must be decomposed into real items before MP-06; it cannot justify empty volume.",
        "Remainder of historical 112.9 g avionics allocation after explicit items", "MP-04 H22: weigh every harness, connector, mount and service loop; retire this reserve row.",
    ),
)


POWER_LOADS = (
    PowerLoad(
        "avionics_5v", CONFIGS_ALL, "FC-5V", 5.0, 0.4275, 0.555, 0.555,
        "[D]/[E]", "I-17 FC+RX+GPS+pitot+buzzer 300-555 mA; midpoint is reference",
    ),
    PowerLoad(
        "o4_5v", CONFIGS_ALL, "VTX-5V", 5.0, 1.200, 1.200, 1.200,
        "[M]", "O4 Air Unit at 700 mW, armed and recording",
    ),
    PowerLoad(
        "two_elevon_servos", CONFIGS_ALL, "SERVO-6V", 6.0, 0.375, 0.600, 2.000,
        "[D]/[E]", "I-17 pair: 300-600 mA active and 1.4-2.0 A brief stall",
    ),
    PowerLoad(
        "rudder_servo_reserve", (CONFIG_6S_R,), "SERVO-6V", 6.0, 0.1875, 0.300, 1.000,
        "[E]", "one-servo half of the current two-servo class budget",
    ),
)


POWER_RAILS = (
    PowerRail("pdb6_fc", CONFIGS_6S, "FC-5V", "pdb_6s", 5.2, 2.4, 3.0,
              REFERENCE_PART, "[M]"),
    PowerRail("pdb6_vtx", CONFIGS_6S, "VTX-5V", "pdb_6s", 5.0, 1.8, 2.3,
              REFERENCE_PART, "[M]"),
    PowerRail("pdb6_servo", CONFIGS_6S, "SERVO-6V", "pdb_6s", 6.0, 4.5, 5.5,
              REFERENCE_PART, "[M]"),
    PowerRail("study8_fc", (CONFIG_8S_STUDY,), "FC-5V", "fc_pdb_8s_class",
              5.2, 2.4, 3.0, STUDY_CLASS, "[E] minimum"),
    PowerRail("study8_vtx", (CONFIG_8S_STUDY,), "VTX-5V", "fc_pdb_8s_class",
              5.0, 1.8, 2.3, STUDY_CLASS, "[E] minimum"),
    PowerRail("study8_servo", (CONFIG_8S_STUDY,), "SERVO-6V", "fc_pdb_8s_class",
              6.0, 4.5, 5.5, STUDY_CLASS, "[E] minimum"),
)


def hardware_for(configuration: str) -> tuple[HardwareItem, ...]:
    if configuration not in CONFIGURATION_IDS:
        raise KeyError(configuration)
    return tuple(item for item in HARDWARE if configuration in item.configurations)


def equipment_mass(configuration: str) -> tuple[float, float]:
    """Return candidate bought-in/electrical mass and RSS input uncertainty."""
    items = hardware_for(configuration)
    mass = sum(item.installed_mass_g for item in items)
    sigma = sqrt(sum(item.installed_mass_sigma_g**2 for item in items))
    return mass, sigma


def power_loads_for(configuration: str) -> tuple[PowerLoad, ...]:
    if configuration not in CONFIGURATION_IDS:
        raise KeyError(configuration)
    return tuple(load for load in POWER_LOADS if configuration in load.configurations)


def hotel_power(configuration: str) -> dict[str, float]:
    """Return rail-output and battery-input power for three electrical cases."""
    loads = power_loads_for(configuration)
    result: dict[str, float] = {}
    for name, field in (
        ("reference", "reference_current_a"),
        ("design_continuous", "design_current_a"),
        ("brief_peak", "brief_peak_current_a"),
    ):
        rail_w = sum(load.voltage_v * getattr(load, field) for load in loads)
        result[f"{name}_rail_w"] = rail_w
        result[f"{name}_battery_w"] = rail_w / BEC_EFFICIENCY
    series = 8 if configuration == CONFIG_8S_STUDY else 6
    nominal_voltage = battery_6s_8s_trade.pack_electrical(series)["voltage_nominal_V"]
    result["pack_nominal_voltage_v"] = nominal_voltage
    result["design_continuous_pack_current_a"] = (
        result["design_continuous_battery_w"] / nominal_voltage
    )
    return result


def _load_current(configuration: str, rail: str, field: str) -> float:
    return sum(
        getattr(load, field)
        for load in power_loads_for(configuration)
        if load.rail == rail
    )


def _rail_for(configuration: str, rail: str) -> PowerRail:
    matches = [
        item for item in POWER_RAILS
        if configuration in item.configurations and item.rail == rail
    ]
    if len(matches) != 1:
        raise ValueError(f"{configuration}/{rail}: expected one rail, got {len(matches)}")
    return matches[0]


def configuration_summary() -> dict[str, dict[str, float | int]]:
    result: dict[str, dict[str, float | int]] = {}
    for configuration in CONFIGURATION_IDS:
        mass, sigma = equipment_mass(configuration)
        power = hotel_power(configuration)
        result[configuration] = {
            "installed_rows": len(hardware_for(configuration)),
            "candidate_equipment_mass_g": mass,
            "mass_uncertainty_rss_g": sigma,
            **power,
        }
    return result


def manifest_as_dict() -> dict[str, object]:
    return {
        "schema": "salamandra.article1.hardware-manifest.v1",
        "gate": "M1 candidate baseline; MP-04/MP-05 closure pending",
        "battery_travel_total_mm": BATTERY_TRAVEL_TOTAL_MM,
        "bec_efficiency_assumption": BEC_EFFICIENCY,
        "configurations": [asdict(item) for item in mission_contract.CONFIGURATIONS],
        "hardware": [asdict(item) for item in HARDWARE],
        "power_loads": [asdict(item) for item in POWER_LOADS],
        "power_rails": [asdict(item) for item in POWER_RAILS],
        "summary": configuration_summary(),
    }


def _configuration_label(configurations: tuple[str, ...]) -> str:
    return ", ".join(configurations)


def _mass_label(item: HardwareItem) -> str:
    total = item.installed_mass_g
    sigma = item.installed_mass_sigma_g
    return f"{total:.2f} +/- {sigma:.2f} g"


def _envelope_label(item: HardwareItem) -> str:
    return "<br>".join(
        f"{envelope.name}: {envelope.dimensions_mm[0]:g} x "
        f"{envelope.dimensions_mm[1]:g} x {envelope.dimensions_mm[2]:g} mm "
        f"{envelope.authority}"
        for envelope in item.envelopes
    )


def render_hardware_table() -> str:
    lines = [
        "| ID | Configuration | Status | Reference identity | Qty | Installed mass | Envelope option(s) | MP-04/05 closure |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for item in HARDWARE:
        lines.append(
            f"| `{item.identifier}` | {_configuration_label(item.configurations)} | "
            f"**{item.status}** | {item.identity} | {item.quantity} | "
            f"{_mass_label(item)} {item.mass_authority} | {_envelope_label(item)} | "
            f"{item.closure} |"
        )
    return "\n".join(lines)


def render_summary_table() -> str:
    lines = [
        "| Configuration | Installed rows | Candidate equipment mass | RSS input uncertainty | Reference hotel power | Design-continuous hotel power | Brief hotel peak |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for configuration, values in configuration_summary().items():
        lines.append(
            f"| **{configuration}** | {values['installed_rows']} | "
            f"{values['candidate_equipment_mass_g']:.2f} g | "
            f"{values['mass_uncertainty_rss_g']:.2f} g | "
            f"{values['reference_battery_w']:.2f} W | "
            f"{values['design_continuous_battery_w']:.2f} W | "
            f"{values['brief_peak_battery_w']:.2f} W |"
        )
    return "\n".join(lines)


def render_rail_table() -> str:
    lines = [
        "| Configuration | Rail | Source | Voltage | Continuous load / capacity | Brief load / capacity | Status |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for configuration in CONFIGURATION_IDS:
        for rail_name in ("FC-5V", "VTX-5V", "SERVO-6V"):
            rail = _rail_for(configuration, rail_name)
            continuous = _load_current(configuration, rail_name, "design_current_a")
            peak = _load_current(configuration, rail_name, "brief_peak_current_a")
            lines.append(
                f"| **{configuration}** | `{rail_name}` | `{rail.source_hardware}` | "
                f"{rail.voltage_v:.1f} V | {continuous:.3f} / "
                f"{rail.continuous_capacity_a:.1f} A | {peak:.3f} / "
                f"{rail.peak_capacity_a:.1f} A | {rail.status} {rail.authority} |"
            )
    return "\n".join(lines)


def generated_block() -> str:
    return "\n\n".join((
        BEGIN_MARKER,
        "### Configuration totals",
        render_summary_table(),
        "### Component manifest",
        render_hardware_table(),
        "### Low-voltage rail budget",
        render_rail_table(),
        END_MARKER,
    ))


def _document_block_is_current() -> bool:
    if not DOCUMENT_PATH.exists():
        return False
    text = DOCUMENT_PATH.read_text(encoding="utf-8")
    if text.count(BEGIN_MARKER) != 1 or text.count(END_MARKER) != 1:
        return False
    start = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER, start) + len(END_MARKER)
    return text[start:end] == generated_block()


def validation_checks() -> dict[str, bool]:
    hardware_ids = [item.identifier for item in HARDWARE]
    config_categories = {
        configuration: {item.category for item in hardware_for(configuration)}
        for configuration in CONFIGURATION_IDS
    }
    required_categories = {
        "energy", "propulsion", "power", "flight-control", "actuation", "fpv",
        "navigation", "air-data", "radio-control", "instrumentation",
    }
    six_pdb = next(item for item in HARDWARE if item.identifier == "pdb_6s")
    eight_power = next(
        item for item in HARDWARE if item.identifier == "fc_pdb_8s_class"
    )
    clean_mass, _ = equipment_mass(CONFIG_6S_CLEAN)
    r_mass, _ = equipment_mass(CONFIG_6S_R)
    clean_hotel = hotel_power(CONFIG_6S_CLEAN)

    rails_pass = True
    for configuration in CONFIGURATION_IDS:
        for rail_name in ("FC-5V", "VTX-5V", "SERVO-6V"):
            rail = _rail_for(configuration, rail_name)
            rails_pass &= (
                _load_current(configuration, rail_name, "design_current_a")
                <= rail.continuous_capacity_a
                and _load_current(
                    configuration, rail_name, "brief_peak_current_a"
                ) <= rail.peak_capacity_a
            )

    return {
        "configuration identity comes only from the Gate-M0 mission contract": (
            CONFIGURATION_IDS == (CONFIG_6S_R, CONFIG_6S_CLEAN, CONFIG_8S_STUDY)
        ),
        "hardware identifiers are unique": len(hardware_ids) == len(set(hardware_ids)),
        "every configuration carries the complete minimum hardware-category set": all(
            required_categories <= categories
            for categories in config_categories.values()
        ),
        "6S and 8S use separate packs, motors, ESCs and power-distribution rows": (
            set(six_pdb.configurations) == set(CONFIGS_6S)
            and eight_power.configurations == (CONFIG_8S_STUDY,)
            and six_pdb.input_voltage_range_v is not None
            and six_pdb.input_voltage_range_v[1] == 25.2
            and eight_power.input_voltage_range_v is not None
            and eight_power.input_voltage_range_v[1] >= 33.6
        ),
        "P42A pack masses reproduce the I-32 6S/8S calculation": (
            isclose(PACK_6S_MASS_G, 445.0, abs_tol=1e-12)
            and isclose(PACK_8S_MASS_G, 585.0, abs_tol=1e-12)
        ),
        "battery travel remains a separate 20 mm requirement": isclose(
            BATTERY_TRAVEL_TOTAL_MM, 20.0, abs_tol=1e-12
        ),
        "6S-CLEAN candidate equipment subtotal reconciles the historical rows": isclose(
            clean_mass, 821.85, abs_tol=1e-9
        ),
        "6S-R adds exactly one reserved rudder-servo mass": isclose(
            r_mass - clean_mass, 12.5, abs_tol=1e-9
        ),
        "CLEAN and 8S-STUDY do not carry the rudder-servo reserve": all(
            "rudder_servo_reserve"
            not in {item.identifier for item in hardware_for(configuration)}
            for configuration in (CONFIG_6S_CLEAN, CONFIG_8S_STUDY)
        ),
        "reference CLEAN hotel load reproduces the existing power model": isclose(
            clean_hotel["reference_battery_w"],
            fpv_power_budget.reference_hotel_load_w(),
            abs_tol=1e-12,
        ),
        "every 6S and study low-voltage rail carries continuous and brief loads": rails_pass,
        "8S remains study-only and has no first-flight authority": not next(
            item for item in mission_contract.CONFIGURATIONS
            if item.identifier == CONFIG_8S_STUDY
        ).first_flight_authorized,
        "human-readable MP-03 manifest is current": _document_block_is_current(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="emit the complete machine-readable manifest"
    )
    parser.add_argument(
        "--render-markdown", action="store_true",
        help="print the generated Markdown block for docs/17",
    )
    args = parser.parse_args()

    if args.json:
        print(json.dumps(manifest_as_dict(), indent=2, sort_keys=True))
        return 0
    if args.render_markdown:
        print(generated_block())
        return 0

    print("SALAMANDRA MP-03 — CANDIDATE HARDWARE AND POWER MANIFEST")
    print()
    print(f"Hardware rows: {len(HARDWARE)}")
    for configuration, values in configuration_summary().items():
        print(
            f"  {configuration:10s} {values['installed_rows']:2d} rows; "
            f"equipment {values['candidate_equipment_mass_g']:.2f} +/- "
            f"{values['mass_uncertainty_rss_g']:.2f} g RSS; "
            f"hotel {values['reference_battery_w']:.2f} W reference / "
            f"{values['design_continuous_battery_w']:.2f} W design / "
            f"{values['brief_peak_battery_w']:.2f} W brief"
        )
    print()
    print("Validation")
    checks = validation_checks()
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        print("\nMP-03 MANIFEST: FAIL")
        return 1
    print("\nMP-03 MANIFEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
