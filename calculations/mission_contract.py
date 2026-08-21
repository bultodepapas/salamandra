#!/usr/bin/env python3
"""Machine-readable mission and configuration contract for Salamandra Article #1.

This module owns the redesign intent established at Gate M0.  It deliberately
does not own a planform, mass, motor, propeller, servo, range or endurance: all
of those are candidate-dependent outputs of later gates.  The released v0.6
numbers imported from :mod:`design_config` are labelled either as historical
comparators or as provisional screening assumptions; importing them here does
not promote them into final redesign requirements.

Efficiency is a vector of total battery energy per distance at named mission
states.  A candidate may be declared better only by Pareto dominance unless a
later, explicit decision supplies stakeholder weights.  This prevents an
undocumented scalar score from hiding a material loss at one operating state.
"""
from dataclasses import dataclass
from math import isclose, isfinite
from typing import Mapping

import design_config


# Historical v0.6 anchors.  These aliases keep one numerical owner and make
# their reduced redesign authority explicit in the variable name.
LEGACY_COMPARATOR_SPEED_KMH = design_config.CRUISE_SPEED_KMH
LEGACY_COMPARATOR_LIMIT_WH_PER_KM = design_config.O1_ENERGY_LIMIT_WH_PER_KM
PROVISIONAL_STALL_SCREEN_KMH = design_config.STALL_SPEED_LIMIT_KMH
PROVISIONAL_POSITIVE_LIMIT_LOAD = design_config.POSITIVE_LIMIT_LOAD_FACTOR
PROVISIONAL_NEGATIVE_LIMIT_LOAD = design_config.NEGATIVE_LIMIT_LOAD_FACTOR
PROVISIONAL_ULTIMATE_FACTOR = design_config.ULTIMATE_SAFETY_FACTOR
STANDARD_COMPARISON_DENSITY_KG_M3 = design_config.RHO_SL

# Article #1 platform requirements owned by the Gate-M0 specification.
MINIMUM_PRINTER_BED_MM = 256.0
MINIMUM_BATTERY_TRAVEL_TOTAL_MM = 20.0
BATTERY_CELL_FORMAT = "21700"
PRIMARY_PRINT_MATERIAL = "PETG"
MOTOR_COUNT = 1

# Launch_speed.py owns the inherited 1.20 post-release acceleration target.
# The release gate itself remains V_release >= V_s.  The approach multiplier is
# an engineering planning value, not a certification rule, and must be replaced
# by flight-test evidence before an operational landing-speed card is released.
LAUNCH_RELEASE_MINIMUM_VS_RATIO = 1.0
PROVISIONAL_APPROACH_VS_RATIO = 13.0 / 10.0

# Retained v0.6 control-travel screen from ADR-0047: nominal trim was bounded at
# 15 deg inside a 20 deg mechanical travel.  The redesign must rederive the
# actual angles, but a candidate cannot consume the final quarter of mechanical
# travel merely to trim in the mission-state matrix.
MAXIMUM_TRIM_FRACTION_OF_MECHANICAL_TRAVEL = 0.75
MINIMUM_TRIM_ONLY_RESERVE_FRACTION = 0.25

FIXED_RANGE_REQUIREMENT_KM = None
FIXED_ENDURANCE_REQUIREMENT_MIN = None
FIXED_ROLL_RATE_REQUIREMENT_DEG_S = None

OBJECTIVE_PRIORITY = (
    "safety_and_controllability",
    "total_energy_efficiency",
    "practical_handling",
    "durability_and_repairability",
    "simplicity_and_open_reproducibility",
    "aesthetic_preference",
)


@dataclass(frozen=True)
class Configuration:
    """One controlled Article #1 configuration."""

    identifier: str
    purpose: str
    series_cells: int
    directional_module: str
    flight_release_order: int | None
    first_flight_authorized: bool


CONFIGURATIONS = (
    Configuration(
        identifier="6S-R",
        purpose="first-flight development and directional-evidence baseline",
        series_cells=6,
        directional_module="rudder-capable removable vertical module",
        flight_release_order=1,
        first_flight_authorized=True,
    ),
    Configuration(
        identifier="6S-CLEAN",
        purpose="post-baseline experiment without the vertical module",
        series_cells=6,
        directional_module="none",
        flight_release_order=2,
        first_flight_authorized=False,
    ),
    Configuration(
        identifier="8S-STUDY",
        purpose="separate voltage/energy architecture study",
        series_cells=8,
        directional_module="not released",
        flight_release_order=None,
        first_flight_authorized=False,
    ),
)


@dataclass(frozen=True)
class MissionState:
    """A named operating state used to compare candidate architectures."""

    identifier: str
    purpose: str
    speed_basis: str
    speed_value: float | None
    metric: str
    authority: str


MISSION_STATES = (
    MissionState(
        identifier="L0_RELEASE",
        purpose="hand-launch separation gate",
        speed_basis="multiple_of_candidate_stall_speed",
        speed_value=LAUNCH_RELEASE_MINIMUM_VS_RATIO,
        metric="release_speed_margin_and_post_release_acceleration",
        authority="requirement plus I-14 method",
    ),
    MissionState(
        identifier="L1_APPROACH",
        purpose="low-speed approach and handling evaluation",
        speed_basis="multiple_of_candidate_stall_speed",
        speed_value=PROVISIONAL_APPROACH_VS_RATIO,
        metric="trim_control_margin_and_stall_recovery",
        authority="provisional engineering state",
    ),
    MissionState(
        identifier="E0_BEST_RANGE",
        purpose="candidate-specific minimum energy per distance",
        speed_basis="candidate_derived",
        speed_value=None,
        metric="total_battery_Wh_per_km",
        authority="primary efficiency state",
    ),
    MissionState(
        identifier="E1_REPORT_65",
        purpose="low-cruise common comparison",
        speed_basis="true_airspeed_km_h_at_standard_comparison_density",
        speed_value=65.0,
        metric="total_battery_Wh_per_km",
        authority="common reporting state",
    ),
    MissionState(
        identifier="E2_NOMINAL_80",
        purpose="normal FPV-cruise design state",
        speed_basis="true_airspeed_km_h_at_standard_comparison_density",
        speed_value=80.0,
        metric="total_battery_Wh_per_km",
        authority="provisional design state",
    ),
    MissionState(
        identifier="E3_LEGACY_95",
        purpose="continuity comparison with the released v0.6 programme",
        speed_basis="true_airspeed_km_h_at_standard_comparison_density",
        speed_value=LEGACY_COMPARATOR_SPEED_KMH,
        metric="total_battery_Wh_per_km",
        authority="historical comparator only",
    ),
)

EFFICIENCY_STATE_ORDER = (
    "E0_BEST_RANGE",
    "E1_REPORT_65",
    "E2_NOMINAL_80",
    "E3_LEGACY_95",
)


def configuration(identifier: str) -> Configuration:
    """Return a configuration by identifier; fail visibly on unknown input."""
    for item in CONFIGURATIONS:
        if item.identifier == identifier:
            return item
    raise KeyError(f"unknown Article #1 configuration: {identifier}")


def mission_state(identifier: str) -> MissionState:
    """Return a mission state by identifier; fail visibly on unknown input."""
    for item in MISSION_STATES:
        if item.identifier == identifier:
            return item
    raise KeyError(f"unknown mission state: {identifier}")


def state_speed_kmh(identifier: str, candidate_stall_speed_kmh: float) -> float:
    """Resolve a fixed or stall-relative state speed.

    ``E0_BEST_RANGE`` intentionally has no prescribed speed and therefore
    raises: its speed is an output of the candidate performance model.
    """
    if not isfinite(candidate_stall_speed_kmh) or candidate_stall_speed_kmh <= 0:
        raise ValueError("candidate stall speed must be finite and positive")
    state = mission_state(identifier)
    if state.speed_basis == "multiple_of_candidate_stall_speed":
        return candidate_stall_speed_kmh * float(state.speed_value)
    if state.speed_value is not None:
        return state.speed_value
    raise ValueError(f"{identifier} speed is candidate-derived")


def efficiency_vector(values: Mapping[str, float]) -> tuple[float, ...]:
    """Return the ordered total-energy vector used for Pareto comparison."""
    missing = [key for key in EFFICIENCY_STATE_ORDER if key not in values]
    if missing:
        raise KeyError(f"missing efficiency states: {', '.join(missing)}")
    result = tuple(float(values[key]) for key in EFFICIENCY_STATE_ORDER)
    if any(not isfinite(value) or value <= 0.0 for value in result):
        raise ValueError("each total-energy result must be finite and positive")
    return result


def pareto_dominates(
    candidate: Mapping[str, float],
    reference: Mapping[str, float],
    tolerance_wh_per_km: float = 0.0,
) -> bool:
    """Whether ``candidate`` is no worse everywhere and better somewhere."""
    if not isfinite(tolerance_wh_per_km) or tolerance_wh_per_km < 0.0:
        raise ValueError("tolerance must be finite and non-negative")
    candidate_vector = efficiency_vector(candidate)
    reference_vector = efficiency_vector(reference)
    no_worse = all(
        trial <= baseline + tolerance_wh_per_km
        for trial, baseline in zip(candidate_vector, reference_vector)
    )
    materially_better = any(
        trial < baseline - tolerance_wh_per_km
        for trial, baseline in zip(candidate_vector, reference_vector)
    )
    return no_worse and materially_better


def validation_checks() -> dict[str, bool]:
    """Executable invariants for the Gate-M0 mission contract."""
    reference = dict.fromkeys(EFFICIENCY_STATE_ORDER, 1.0)
    improvement = dict(reference)
    improvement["E0_BEST_RANGE"] = 0.9
    trade = dict(reference)
    trade["E0_BEST_RANGE"] = 0.9
    trade["E3_LEGACY_95"] = 1.1
    fixed_reporting_speeds = tuple(
        float(mission_state(key).speed_value)
        for key in EFFICIENCY_STATE_ORDER[1:]
    )
    flight_release_order = tuple(
        item.flight_release_order for item in CONFIGURATIONS
        if item.flight_release_order is not None
    )
    first_flight = tuple(
        item.identifier for item in CONFIGURATIONS
        if item.first_flight_authorized
    )
    return {
        "safety precedes performance objectives": (
            OBJECTIVE_PRIORITY[0] == "safety_and_controllability"
        ),
        "range and endurance remain candidate outputs": (
            FIXED_RANGE_REQUIREMENT_KM is None
            and FIXED_ENDURANCE_REQUIREMENT_MIN is None
        ),
        "no arbitrary roll-rate requirement is declared": (
            FIXED_ROLL_RATE_REQUIREMENT_DEG_S is None
        ),
        "fixed efficiency reporting speeds are strictly ordered": (
            fixed_reporting_speeds
            == tuple(sorted(fixed_reporting_speeds))
        ),
        "95 km/h remains the v0.6 comparator": isclose(
            mission_state("E3_LEGACY_95").speed_value,
            design_config.CRUISE_SPEED_KMH,
        ),
        "1.15 Wh/km remains a historical limit only": isclose(
            LEGACY_COMPARATOR_LIMIT_WH_PER_KM,
            design_config.O1_ENERGY_LIMIT_WH_PER_KM,
        ),
        "approach planning speed exceeds release gate": (
            PROVISIONAL_APPROACH_VS_RATIO
            > LAUNCH_RELEASE_MINIMUM_VS_RATIO
        ),
        "trim-only travel fractions close": isclose(
            MAXIMUM_TRIM_FRACTION_OF_MECHANICAL_TRAVEL
            + MINIMUM_TRIM_ONLY_RESERVE_FRACTION,
            1.0,
        ),
        "flight release order is unique and increasing": (
            flight_release_order
            == tuple(sorted(set(flight_release_order)))
        ),
        "6S-R is the only first-flight configuration": (
            first_flight == ("6S-R",)
            and configuration("6S-R").series_cells == 6
        ),
        "CLEAN follows the rudder-capable baseline": (
            configuration("6S-CLEAN").flight_release_order
            > configuration("6S-R").flight_release_order
        ),
        "8S remains a study, not a first-flight release": (
            configuration("8S-STUDY").series_cells == 8
            and not configuration("8S-STUDY").first_flight_authorized
            and configuration("8S-STUDY").flight_release_order is None
        ),
        "Pareto comparison accepts an unambiguous improvement": (
            pareto_dominates(improvement, reference)
        ),
        "Pareto comparison rejects a hidden trade": (
            not pareto_dominates(trade, reference)
        ),
    }


def main() -> None:
    print("SALAMANDRA ARTICLE #1 — GATE-M0 MISSION CONTRACT")
    print("\nConfigurations")
    for item in CONFIGURATIONS:
        if item.first_flight_authorized:
            release = "flight order 1"
        elif item.flight_release_order is None:
            release = "study only"
        else:
            release = f"flight order {item.flight_release_order}"
        print(
            f"  {item.identifier:10s} {item.series_cells}S  "
            f"{release}: {item.purpose}"
        )
    print("\nMission states")
    for item in MISSION_STATES:
        value = "derived" if item.speed_value is None else f"{item.speed_value:g}"
        print(
            f"  {item.identifier:16s} {value:>7s}  "
            f"{item.metric}: {item.purpose}"
        )
    print("\nValidation")
    checks = validation_checks()
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print(f"\nGATE-M0 CONTRACT: {'PASS' if all(checks.values()) else 'FAIL'}")
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
