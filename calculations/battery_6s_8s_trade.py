#!/usr/bin/env python3
"""I-32 P42A 6S1P/8S1P geometry, balance and electrical trade.

The calculation enumerates every rectangular arrangement of six and eight
horizontal 21700 cells.  CAD envelopes use the Molicel P42A manufacturer
maximum cell dimensions.  Pack wrap, nickel, cable, hardware mass and travel
are declared estimates; no result is manufacturing authority.

Coordinates follow the project convention: x is positive aft and the origin
is the root quarter chord.  The electrical comparison holds total aircraft
power constant.  The aerodynamic sensitivity uses the current estimated clean
polar and is not a substitute for E2 drag or D2 propulsion measurements.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isclose

import balance_cg
import battery_pack_layout
import design_config
import drag_model
import propulsion_match


# Current Molicel INR-21700-P42A v4 product-data values [M], centralized in
# I-16's battery module.  The data sheet reports energy separately from
# nominal-voltage x capacity, so all three representations remain visible.
(
    CELL_MASS_MAX_G,
    CELL_CAPACITY_TYPICAL_AH,
    CELL_VOLTAGE_NOMINAL_V,
    CELL_CURRENT_CONTINUOUS_A,
    _CELL_CHARGE_CURRENT_A,
    CELL_ENERGY_ARITHMETIC_WH,
) = battery_pack_layout.CELLS["Molicel P42A"]
CELL_CAPACITY_MINIMUM_AH = battery_pack_layout.P42A_CAPACITY_MINIMUM_AH
CELL_VOLTAGE_FULL_V = battery_pack_layout.P42A_VOLTAGE_FULL_V
CELL_VOLTAGE_CUTOFF_V = battery_pack_layout.P42A_VOLTAGE_CUTOFF_V
CELL_ENERGY_TYPICAL_WH = battery_pack_layout.P42A_ENERGY_TYPICAL_WH
CELL_ENERGY_MINIMUM_WH = battery_pack_layout.P42A_ENERGY_MINIMUM_WH
CELL_DC_RESISTANCE_OHM = battery_pack_layout.P42A_DC_RESISTANCE_OHM

# I-16 pack-level estimates [E].  Hardware mass is retained unchanged so that
# 6S reproduces the released 445 g mass.  Its uncertainty is exposed because
# an eight-cell pack has not yet been built and weighed.
PACK_HARDWARE_MASS_G = 25.0
PACK_HARDWARE_UNCERTAINTY_G = 5.0
OUTER_WRAP_EACH_SIDE_MM = battery_pack_layout.PVC_OUTER
NICKEL_HEIGHT_MM = battery_pack_layout.NICKEL
LEAD_PROJECTION_MM = battery_pack_layout.LEAD_ADD

# The user requested 10 mm for cables/CG correction.  The engineering screen
# preserves 10 mm of pack-centre motion in both directions.  The existing
# 12 mm one-end folded-lead envelope remains separate and is not double-counted.
TRAVEL_EACH_WAY_MM = 10.0
CROSS_AXIS_INSTALLATION_CLEARANCE_TOTAL_MM = 2.0  # [E], before bay walls

# P42A maximum sleeved dimensions [M].
CELL_LENGTH_MAX_MM, CELL_DIAMETER_MAX_MM = (
    battery_pack_layout.CELL_MAX_DIMENSIONS_MM["Molicel P42A"]
)


@dataclass(frozen=True)
class Layout:
    series: int
    nx: int
    ny: int
    nz: int
    orientation: str

    @property
    def name(self) -> str:
        return f"{self.nx}x{self.ny}x{self.nz}-{self.orientation}"

    @property
    def cell_count(self) -> int:
        return self.nx * self.ny * self.nz

    def raw_block_mm(self) -> tuple[float, float, float]:
        """Cell block L x W x H before pack-level allowances."""
        if self.orientation == "A":
            return (
                self.nx * CELL_LENGTH_MAX_MM,
                self.ny * CELL_DIAMETER_MAX_MM,
                self.nz * CELL_DIAMETER_MAX_MM,
            )
        if self.orientation == "B":
            return (
                self.nx * CELL_DIAMETER_MAX_MM,
                self.ny * CELL_LENGTH_MAX_MM,
                self.nz * CELL_DIAMETER_MAX_MM,
            )
        raise ValueError(f"unsupported orientation {self.orientation!r}")

    def envelope_mm(self) -> tuple[float, float, float]:
        """Installed pack envelope using maximum cells and I-16 allowances."""
        length, width, height = self.raw_block_mm()
        return (
            length + 2.0 * OUTER_WRAP_EACH_SIDE_MM + LEAD_PROJECTION_MM,
            width + 2.0 * OUTER_WRAP_EACH_SIDE_MM,
            height + 2.0 * OUTER_WRAP_EACH_SIDE_MM + NICKEL_HEIGHT_MM,
        )

    def x_bounds_from_mass_centre_mm(
        self, centre_x_mm: float, travel_each_way_mm: float = 0.0
    ) -> tuple[float, float]:
        """Physical x bounds with the one-end cable envelope routed aft.

        The mass centre is approximated by the cell-block centre, not by the
        midpoint of the asymmetric lead envelope.  Hardware mass properties
        remain a physical measurement gate.
        """
        block_length = self.raw_block_mm()[0]
        forward = (
            centre_x_mm
            - block_length / 2.0
            - OUTER_WRAP_EACH_SIDE_MM
            - travel_each_way_mm
        )
        aft = (
            centre_x_mm
            + block_length / 2.0
            + OUTER_WRAP_EACH_SIDE_MM
            + LEAD_PROJECTION_MM
            + travel_each_way_mm
        )
        return forward, aft


def layouts(series: int) -> tuple[Layout, ...]:
    """Every ordered rectangular arrangement and horizontal cell orientation."""
    if series not in (6, 8):
        raise ValueError("this trade is limited to 6S1P and 8S1P")
    rows = []
    for nx, ny, nz in battery_pack_layout.factor_triples(series):
        for orientation in ("A", "B"):
            rows.append(Layout(series, nx, ny, nz, orientation))
    return tuple(sorted(
        rows,
        key=lambda row: (
            row.nz,
            row.envelope_mm()[2],
            row.envelope_mm()[0],
            row.envelope_mm()[1],
            row.name,
        ),
    ))


def get_layout(series: int, name: str) -> Layout:
    for row in layouts(series):
        if row.name == name:
            return row
    raise KeyError(f"unknown {series}S layout {name!r}")


def pack_mass_g(series: int) -> float:
    return series * CELL_MASS_MAX_G + PACK_HARDWARE_MASS_G


def pack_electrical(series: int) -> dict[str, float]:
    """Series-pack electrical values; capacity and current do not multiply."""
    voltage_nominal = series * CELL_VOLTAGE_NOMINAL_V
    total_power = design_config.electrical_power_limit_w()
    current = total_power / voltage_nominal
    resistance = series * CELL_DC_RESISTANCE_OHM
    return {
        "capacity_typical_Ah": CELL_CAPACITY_TYPICAL_AH,
        "capacity_minimum_Ah": CELL_CAPACITY_MINIMUM_AH,
        "voltage_nominal_V": voltage_nominal,
        "voltage_full_V": series * CELL_VOLTAGE_FULL_V,
        "voltage_cutoff_V": series * CELL_VOLTAGE_CUTOFF_V,
        "energy_arithmetic_Wh": series * CELL_ENERGY_ARITHMETIC_WH,
        "energy_datasheet_typical_Wh": series * CELL_ENERGY_TYPICAL_WH,
        "energy_datasheet_minimum_Wh": series * CELL_ENERGY_MINIMUM_WH,
        "continuous_current_A": CELL_CURRENT_CONTINUOUS_A,
        "current_at_O1_power_A": current,
        "cell_C_rate_at_O1_power": current / CELL_CAPACITY_TYPICAL_AH,
        "pack_DC_resistance_Ohm": resistance,
        "DC_voltage_sag_at_O1_power_V": current * resistance,
        "DC_heat_at_O1_power_W": current**2 * resistance,
        "ideal_duration_at_O1_power_min": (
            series * CELL_ENERGY_ARITHMETIC_WH / total_power * 60.0
        ),
        "ideal_range_at_O1_limit_km": (
            series
            * CELL_ENERGY_ARITHMETIC_WH
            / design_config.O1_ENERGY_LIMIT_WH_PER_KM
        ),
    }


def pack_station_mm(series: int) -> float:
    """Pack mass-centre station in the frozen current aggregate balance model."""
    reference = balance_cg.solve_reference_layout()
    return 1000.0 * balance_cg.pack_station(
        reference["m0"],
        reference["moment0"],
        pack_mass_g(series) / 1000.0,
        balance_cg.cg_target(),
    )


def aircraft_case(series: int, fin: bool = False) -> dict[str, float | bool]:
    """Mass, stall and current-polar cruise sensitivity for one pack."""
    fixed_clean_mass = (
        design_config.ARTICLE_CLEAN_MASS_KG - pack_mass_g(6) / 1000.0
    )
    mass = fixed_clean_mass + pack_mass_g(series) / 1000.0
    if fin:
        mass += design_config.V1_FIN_MODEL_LOWER_KG
    speed = design_config.speed_mps(design_config.CRUISE_SPEED_KMH)
    cl = design_config.lift_coefficient(mass, speed)
    cd_profile, cd_induced = drag_model.clean_cd(cl)
    drag = drag_model.drag_newton(cd_profile + cd_induced, speed)
    propeller = propulsion_match.solve_thrust(drag)
    total_power = propeller.electrical_w + propulsion_match.reference_hotel_load()
    return {
        "mass_kg": mass,
        "wing_loading_g_dm2": design_config.wing_loading_g_dm2(mass),
        "stall_speed_kmh": 3.6 * design_config.stall_speed(mass),
        "stall_requirement_pass": (
            3.6 * design_config.stall_speed(mass)
            <= design_config.STALL_SPEED_LIMIT_KMH
        ),
        "CL_at_95_kmh": cl,
        "estimated_CD_profile": cd_profile,
        "estimated_CD_induced": cd_induced,
        "estimated_drag_N": drag,
        "estimated_total_power_W": total_power,
        "estimated_energy_Wh_per_km": (
            total_power / design_config.CRUISE_SPEED_KMH
        ),
        "estimated_propeller_rpm": propeller.rpm,
    }


def propulsion_voltage_case(series: int) -> dict[str, float]:
    """Voltage/Kv consequences at the existing O1 propeller boundary."""
    rpm = propulsion_match.o1_boundary().rpm
    voltage_nominal = series * CELL_VOLTAGE_NOMINAL_V
    return {
        "boundary_rpm": rpm,
        "Kv_at_80_percent_loaded_ratio": rpm / (0.80 * voltage_nominal),
        "rpm_fraction_at_500Kv": rpm / (voltage_nominal * 500.0),
        "rpm_fraction_at_550Kv": rpm / (voltage_nominal * 550.0),
        "full_charge_no_load_rpm_at_500Kv": (
            series * CELL_VOLTAGE_FULL_V * 500.0
        ),
        "full_charge_no_load_rpm_at_550Kv": (
            series * CELL_VOLTAGE_FULL_V * 550.0
        ),
        "propeller_rpm_limit": propulsion_match.APC_MAX_RPM,
    }


def pack_pitch_inertia_proxy(series: int, layout: Layout) -> float:
    """Pack contribution to Iyy about aircraft CG, rectangular-envelope proxy."""
    mass = pack_mass_g(series) / 1000.0
    x = pack_station_mm(series) / 1000.0
    target = balance_cg.cg_target()
    length, _width, height = layout.envelope_mm()
    centroidal = mass / 12.0 * (
        (length / 1000.0) ** 2 + (height / 1000.0) ** 2
    )
    orbital = mass * (x - target) ** 2
    return centroidal + orbital


def common_bay(
    layout_6s: Layout, layout_8s: Layout
) -> dict[str, float | str]:
    """Union needed by both pack envelopes at their solved CG stations."""
    if layout_6s.series != 6 or layout_8s.series != 8:
        raise ValueError("common bay requires one 6S and one 8S layout")
    bounds_6s = layout_6s.x_bounds_from_mass_centre_mm(
        pack_station_mm(6), TRAVEL_EACH_WAY_MM
    )
    bounds_8s = layout_8s.x_bounds_from_mass_centre_mm(
        pack_station_mm(8), TRAVEL_EACH_WAY_MM
    )
    forward = min(bounds_6s[0], bounds_8s[0])
    aft = max(bounds_6s[1], bounds_8s[1])
    width = max(layout_6s.envelope_mm()[1], layout_8s.envelope_mm()[1])
    height = max(layout_6s.envelope_mm()[2], layout_8s.envelope_mm()[2])
    return {
        "layout_6s": layout_6s.name,
        "layout_8s": layout_8s.name,
        "rail_forward_x_mm": forward,
        "rail_aft_x_mm": aft,
        "rail_length_mm": aft - forward,
        "pack_union_width_mm": width,
        "pack_union_height_mm": height,
        "minimum_inner_width_with_clearance_mm": (
            width + CROSS_AXIS_INSTALLATION_CLEARANCE_TOTAL_MM
        ),
        "minimum_inner_height_with_clearance_mm": (
            height + CROSS_AXIS_INSTALLATION_CLEARANCE_TOTAL_MM
        ),
        "pack_union_frontal_area_mm2": width * height,
        "rectangular_bay_volume_proxy_ml": (aft - forward) * width * height / 1000.0,
    }


SHORTLIST_LAYOUTS = {
    6: (
        "3x2x1-A",  # flat, narrow, long
        "2x3x1-A",  # flat, compact
        "6x1x1-B",  # flat, moderate width
        "1x3x2-A",  # two layers, compact
        "3x1x2-B",  # two layers, shortest within 71 mm width
    ),
    8: (
        "4x2x1-A",  # flat, narrow, long
        "8x1x1-B",  # flat, moderate width
        "2x4x1-A",  # flat, wide, short
        "2x2x2-A",  # two layers, narrow
        "4x1x2-B",  # two layers, compact
    ),
}


COMMON_BAY_CASES = (
    ("flat_narrow", "3x2x1-A", "4x2x1-A"),
    ("flat_moderate", "6x1x1-B", "8x1x1-B"),
    ("flat_short_wide", "2x3x1-A", "2x4x1-A"),
    ("hybrid_narrow", "3x2x1-A", "2x2x2-A"),
    ("stacked_compact", "1x3x2-A", "2x2x2-A"),
)


def results() -> dict[str, object]:
    all_layouts = {
        series: [
            {
                "layout": row.name,
                "layers": row.nz,
                "envelope_mm": row.envelope_mm(),
                "envelope_volume_ml": (
                    row.envelope_mm()[0]
                    * row.envelope_mm()[1]
                    * row.envelope_mm()[2]
                    / 1000.0
                ),
                "frontal_area_mm2": row.envelope_mm()[1] * row.envelope_mm()[2],
            }
            for row in layouts(series)
        ]
        for series in (6, 8)
    }
    packs = {}
    for series in (6, 8):
        packs[series] = {
            "mass_g": pack_mass_g(series),
            "mass_uncertainty_g": PACK_HARDWARE_UNCERTAINTY_G,
            "station_mm": pack_station_mm(series),
            "electrical": pack_electrical(series),
            "clean_aircraft": aircraft_case(series, fin=False),
            "v1_aircraft": aircraft_case(series, fin=True),
            "propulsion_voltage": propulsion_voltage_case(series),
            "shortlist": [
                {
                    "layout": name,
                    "envelope_mm": get_layout(series, name).envelope_mm(),
                    "pack_Iyy_proxy_kg_m2": pack_pitch_inertia_proxy(
                        series, get_layout(series, name)
                    ),
                }
                for name in SHORTLIST_LAYOUTS[series]
            ],
        }
    bay_cases = {
        label: common_bay(get_layout(6, six), get_layout(8, eight))
        for label, six, eight in COMMON_BAY_CASES
    }
    return {
        "authority": "[D] screen on [M]/[E]; not manufacturing authority",
        "cell": {
            "model": "Molicel INR-21700-P42A v4",
            "maximum_dimensions_mm": (
                CELL_LENGTH_MAX_MM,
                CELL_DIAMETER_MAX_MM,
            ),
            "maximum_mass_g": CELL_MASS_MAX_G,
            "typical_capacity_Ah": CELL_CAPACITY_TYPICAL_AH,
            "typical_datasheet_energy_Wh": CELL_ENERGY_TYPICAL_WH,
            "minimum_datasheet_energy_Wh": CELL_ENERGY_MINIMUM_WH,
            "arithmetic_nominal_energy_Wh": CELL_ENERGY_ARITHMETIC_WH,
        },
        "all_layouts": all_layouts,
        "packs": packs,
        "station_separation_mm": pack_station_mm(8) - pack_station_mm(6),
        "common_bay_cases": bay_cases,
    }


def validation_checks(data: dict[str, object] | None = None) -> dict[str, bool]:
    if data is None:
        data = results()
    e6 = data["packs"][6]["electrical"]
    e8 = data["packs"][8]["electrical"]
    flat_narrow = data["common_bay_cases"]["flat_narrow"]
    return {
        "complete rectangular catalogs contain 18 6S and 20 8S layouts": (
            len(data["all_layouts"][6]) == 18
            and len(data["all_layouts"][8]) == 20
        ),
        "every layout contains exactly its declared series cell count": all(
            row.cell_count == series
            for series in (6, 8)
            for row in layouts(series)
        ),
        "series connection preserves P42A Ah": (
            e6["capacity_typical_Ah"] == CELL_CAPACITY_TYPICAL_AH
            and e8["capacity_typical_Ah"] == CELL_CAPACITY_TYPICAL_AH
        ),
        "8S has exactly four-thirds the 6S nominal energy": isclose(
            e8["energy_arithmetic_Wh"] / e6["energy_arithmetic_Wh"],
            4.0 / 3.0,
            abs_tol=1e-12,
        ),
        "8S current at equal power is exactly three-quarters of 6S": isclose(
            e8["current_at_O1_power_A"] / e6["current_at_O1_power_A"],
            3.0 / 4.0,
            abs_tol=1e-12,
        ),
        "8S cell ohmic heat at equal power is three-quarters of 6S": isclose(
            e8["DC_heat_at_O1_power_W"] / e6["DC_heat_at_O1_power_W"],
            3.0 / 4.0,
            abs_tol=1e-12,
        ),
        "current 6S CLEAN passes and 8S CLEAN fails the 45 km/h stall gate": (
            data["packs"][6]["clean_aircraft"]["stall_requirement_pass"]
            and not data["packs"][8]["clean_aircraft"]["stall_requirement_pass"]
        ),
        "8S balance station is aft of 6S": data["station_separation_mm"] > 0.0,
        "flat narrow pair shares a 44.0 x 22.6 mm pack cross-section": (
            isclose(flat_narrow["pack_union_width_mm"], 44.0, abs_tol=0.05)
            and isclose(flat_narrow["pack_union_height_mm"], 22.6, abs_tol=0.05)
        ),
        "flat narrow common rail contains both packs plus symmetric travel": (
            flat_narrow["rail_length_mm"]
            >= get_layout(8, "4x2x1-A").envelope_mm()[0]
            + 2.0 * TRAVEL_EACH_WAY_MM
        ),
    }


def _dimensions(values: tuple[float, float, float]) -> str:
    return " x ".join(f"{value:.1f}" for value in values)


def print_report(data: dict[str, object]) -> None:
    print("=" * 92)
    print("SALAMANDRA I-32 - MOLICEL P42A 6S1P / 8S1P COMPLETE PACK TRADE")
    print("=" * 92)
    print(
        "Cell [M]: 70.2 mm max length x 21.7 mm max diameter, 70 g max; "
        "4.2 Ah typical, 45 A continuous"
    )
    print(
        "Energy [M]/[D]: 15.5 Wh typical / 14.7 Wh minimum data-sheet; "
        "3.6 V x 4.2 Ah = 15.12 Wh arithmetic nominal"
    )
    print(
        "Pack [E]: +0.3 mm outer wrap each side, +0.3 mm nickel height, "
        "+12 mm aft lead, 25 +/-5 g hardware"
    )

    print("\nPACK-LEVEL COMPARISON")
    print(
        f"{'Pack':<6} {'mass':>10} {'V nom/full':>14} {'Ah':>7} "
        f"{'Wh arith':>10} {'Wh M typ/min':>15} {'I@109.25W':>11} "
        f"{'DC heat':>9}"
    )
    for series in (6, 8):
        pack = data["packs"][series]
        electrical = pack["electrical"]
        print(
            f"{series}S1P  {pack['mass_g']:6.0f}+/-{pack['mass_uncertainty_g']:.0f} g "
            f"{electrical['voltage_nominal_V']:5.1f}/{electrical['voltage_full_V']:4.1f} V "
            f"{electrical['capacity_typical_Ah']:5.1f} "
            f"{electrical['energy_arithmetic_Wh']:9.2f} "
            f"{electrical['energy_datasheet_typical_Wh']:6.1f}/"
            f"{electrical['energy_datasheet_minimum_Wh']:5.1f} "
            f"{electrical['current_at_O1_power_A']:9.2f} A "
            f"{electrical['DC_heat_at_O1_power_W']:7.2f} W"
        )

    print("\nAIRCRAFT CONSEQUENCES (current airframe mass and estimated clean polar)")
    print(
        f"{'Case':<10} {'AUW':>8} {'W/S':>9} {'Vstall':>9} {'R-stall':>8} "
        f"{'x_pack':>10} {'CL95':>8} {'D95 [E]':>9} {'Wh/km [E]':>11}"
    )
    for series in (6, 8):
        pack = data["packs"][series]
        for label, key in (("CLEAN", "clean_aircraft"), ("V1", "v1_aircraft")):
            case = pack[key]
            print(
                f"{series}S {label:<5} {case['mass_kg']*1000:7.1f} g "
                f"{case['wing_loading_g_dm2']:7.2f} "
                f"{case['stall_speed_kmh']:7.2f} "
                f"{'PASS' if case['stall_requirement_pass'] else 'FAIL':>8} "
                f"{pack['station_mm']:+8.1f} "
                f"{case['CL_at_95_kmh']:7.4f} "
                f"{case['estimated_drag_N']:8.3f} "
                f"{case['estimated_energy_Wh_per_km']:10.3f}"
            )
    print(
        f"  8S pack centre moves {data['station_separation_mm']:.1f} mm aft "
        "relative to 6S in the frozen current aggregate balance model."
    )

    print("\nPRACTICAL LAYOUT SHORTLIST - maximum-cell installed envelopes")
    for series in (6, 8):
        print(f"  {series}S1P:")
        for row in data["packs"][series]["shortlist"]:
            print(
                f"    {row['layout']:9s}  {_dimensions(row['envelope_mm'])} mm  "
                f"pack-Iyy proxy {row['pack_Iyy_proxy_kg_m2']:.5f} kg m2"
            )

    print("\nCOMMON 6S/8S BAY OPTIONS")
    print(
        "  Rail includes the asymmetric +12 mm aft lead and +/-10 mm movement "
        "for each pack; W/H are pack union before bay walls."
    )
    print(
        f"{'case':<18} {'6S layout':>10} {'8S layout':>10} "
        f"{'rail L':>9} {'pack W':>9} {'pack H':>9} {'inner W/H*':>17}"
    )
    for label, _six, _eight in COMMON_BAY_CASES:
        row = data["common_bay_cases"][label]
        print(
            f"{label:<18} {row['layout_6s']:>10} {row['layout_8s']:>10} "
            f"{row['rail_length_mm']:8.1f} "
            f"{row['pack_union_width_mm']:8.1f} "
            f"{row['pack_union_height_mm']:8.1f} "
            f"{row['minimum_inner_width_with_clearance_mm']:7.1f}/"
            f"{row['minimum_inner_height_with_clearance_mm']:.1f}"
        )
    print("  * +2 mm total cross-axis installation clearance [E], before walls.")

    print("\nALL RECTANGULAR LAYOUTS")
    for series in (6, 8):
        print(f"  {series}S1P ({len(data['all_layouts'][series])} arrangements):")
        for row in data["all_layouts"][series]:
            print(
                f"    {row['layout']:9s} layers={row['layers']}  "
                f"{_dimensions(row['envelope_mm'])} mm  "
                f"frontal={row['frontal_area_mm2']:.0f} mm2  "
                f"box={row['envelope_volume_ml']:.1f} mL"
            )

    print("\nVOLTAGE / MOTOR SCREEN")
    for series in (6, 8):
        row = data["packs"][series]["propulsion_voltage"]
        print(
            f"  {series}S: {row['Kv_at_80_percent_loaded_ratio']:.0f} Kv at "
            f"80% loaded/no-load ratio; existing 500--550 Kv needs "
            f"{row['rpm_fraction_at_550Kv']*100:.0f}--"
            f"{row['rpm_fraction_at_500Kv']*100:.0f}% of nominal no-load rpm; "
            f"550 Kv at full charge -> {row['full_charge_no_load_rpm_at_550Kv']:.0f} rpm"
        )
    print(
        f"  APC 8x8E published limit: {propulsion_match.APC_MAX_RPM:.0f} rpm. "
        "Voltage compatibility and D2 mapping remain mandatory."
    )

    checks = validation_checks(data)
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


def main() -> None:
    print_report(results())


if __name__ == "__main__":
    main()
