#!/usr/bin/env python3
"""
FPV system power budget — DJI O4 Air Unit / O4 Air Unit Pro (research/I-19).

Power draw values are measured [M] (Oscar Liang, armed + recording unless noted):
    O4 Air Unit Pro (@9V): 1200mW 1.16 A | 700mW 1.05 | 400mW 0.98 | 200mW 0.92
                   100mW 0.87 | 50mW 0.84 | 25mW 0.82 A | disarmed 0.33 A
    O4 Air Unit (@5V): 700mW 1.2 A (6 W) | disarmed 0.6 A (3 W)
The measured review called the lightweight product "O4 Lite"; DJI's official
name is "DJI O4 Air Unit". Input ranges and bought-in dimensions are [M].

Outputs [D]: per-level power and current at user-selected input voltage, BEC
margin against the Matek 9V/2A and 5V/2A rails, and energy impact on the
reference 6S1P P42A pack (90.7 Wh, I-16). Reference, not a verdict.
"""
import sys
from functools import cache

from battery_pack_layout import CELLS as PACK_CELL_SPECS
from design_config import REFERENCE_BEC_EFFICIENCY, electrical_power_limit_w
from equipment_catalog import (
    DJI_O4_CAMERA,
    DJI_O4_INSTALLED_MASS_G,
    DJI_O4_TRANSMISSION_MODULE,
)
from inav_fc_match import avionics_power_budget

# --- Salamandra FPV assumptions ---------------------------------------------
BEC_9V = (2.0, 3.0)      # A continuous / peak, Matek 9V BEC
BEC_5V = (2.0, 3.0)      # A continuous / peak, Matek 5V BEC
PACK_WH = 6.0 * PACK_CELL_SPECS["Molicel P42A"][5]
CRUISE_W = electrical_power_limit_w()  # W, total O1 battery-power ceiling

@cache
def reference_avionics_w():
    """Shared avionics rail power [W] from the I-17 FC budget.

    Lazy and cached: computing it at module scope charged every importer and
    made an upstream failure an import crash rather than a reported check.
    """
    return avionics_power_budget()[2]


# model : (measured voltage V, disarmed current A, {power_mW: current_A})
UNITS = {
    "O4 Air Unit Pro": {"v": 9.0, "disarmed": 0.33, "draw": {
        1200: 1.16, 700: 1.05, 400: 0.98, 200: 0.92,
        100: 0.87, 50: 0.84, 25: 0.82}},
    "O4 Air Unit": {"v": 5.0, "disarmed": 0.60, "draw": {700: 1.2}},
}

ALIASES = {"O4 Lite": "O4 Air Unit"}

# model : (input range V, installed weight g, VTX size, camera size, sensor)
# Body/input data are [M]; installed mass is [D] when antennas are added.
DIMS = {
    "O4 Air Unit Pro": ((7.4, 26.4), 36.2, "33.5x33.5x13", "25.55x20x23.30", "1/1.3 in"),
    "O4 Air Unit": (
        (3.7, 13.2),
        DJI_O4_INSTALLED_MASS_G,
        "x".join(
            f"{value:g}" for value in DJI_O4_TRANSMISSION_MODULE.envelope_mm
        ),
        "x".join(f"{value:g}" for value in DJI_O4_CAMERA.envelope_mm),
        "1/2 in",
    ),
}


def model_power(name, v_input=None):
    """Return list of (mW, W, I_at_input) at the given input voltage."""
    name = ALIASES.get(name, name)
    u = UNITS[name]
    v = u["v"] if v_input is None else v_input
    v_min, v_max = DIMS[name][0]
    if not v_min <= v <= v_max:
        raise ValueError(f"{name} input {v} V is outside {v_min}--{v_max} V")
    rows = []
    for mw, ia in sorted(u["draw"].items()):
        w = ia * u["v"]            # measured W (constant-power converter)
        rows.append((mw, w, w / v))
    # disarmed
    wd = u["disarmed"] * u["v"]
    rows.append((0, wd, wd / v))   # mW=0 marks disarmed
    return v, rows


def reference_hotel_load_w(fpv_name="O4 Air Unit", avionics_w=None,
                           bec_efficiency=REFERENCE_BEC_EFFICIENCY):
    """Continuous non-propulsion battery input for a selected FPV unit [W].

    ``avionics_w=None`` resolves to the shared budget at call time.  It is not
    a default argument: a module constant bound at definition time cannot be
    overridden by reassigning it, which silently defeats sensitivity studies.
    """
    if avionics_w is None:
        avionics_w = reference_avionics_w()
    if avionics_w < 0.0 or not 0.0 < bec_efficiency <= 1.0:
        raise ValueError("avionics power must be non-negative and BEC eta in (0, 1]")
    _, rows = model_power(fpv_name)
    fpv_max = max(w for level, w, _ in rows if level > 0)
    return (avionics_w + fpv_max) / bec_efficiency


def main():
    print("=" * 76)
    print("FPV SYSTEM POWER BUDGET — DJI O4 AIR UNIT SERIES")
    print("=" * 76)
    for name, (vr, w, vt, cam, sen) in DIMS.items():
        print(f"\n{name}  [M]/[D]: installed weight {w} g | VTX {vt} mm | camera {cam} mm | "
              f"sensor {sen} | input {vr[0]}-{vr[1]} V")
    print("\nMeasured draw anchors [M]: O4 Air Unit Pro and lightweight "
          "O4 Air Unit armed+recording.")

    default_v = 9.0
    if len(sys.argv) > 1:
        try:
            default_v = float(sys.argv[1])
        except ValueError:
            pass

    for name in UNITS:
        _, rows = model_power(name, default_v)
        print(f"\n--- {name}  (input {default_v:.1f} V) ---")
        current_header = f"I@{default_v:.1f}V"
        print(f"  {'level':>8} {'W':>7} {current_header:>10}")
        for mw, w, ia in rows:
            tag = "disarmed" if mw == 0 else f"{mw} mW"
            print(f"  {tag:>8} {w:>7.1f} {ia*1000:>9.0f} mA")

    print("\n" + "-" * 76)
    print("BEC CHECK AND ENERGY IMPACT [D]")
    print("-" * 76)
    # worst case per model: max power level
    for name in UNITS:
        _, rows = model_power(name)
        max_mw, max_w, _ = max((r for r in rows if r[0]), key=lambda r: r[0])
        min_mw, min_w, _ = min((r for r in rows if r[0]), key=lambda r: r[0])
        rail = "5V" if name == "O4 Air Unit" else "9V"
        bec = BEC_5V if name == "O4 Air Unit" else BEC_9V
        util = max_w / (bec[0] * 5.0 if rail == "5V" else bec[0] * 9.0) * 100
        print(f"\n  {name}: power range {min_w:.1f} ... {max_w:.1f} W "
              f"(max {max_mw} mW, min {min_mw} mW)")
        print(f"    powered from {rail} rail: I@max = "
              f"{max_w/(5.0 if rail=='5V' else 9.0):.2f} A vs "
              f"{bec[0]:.1f} A BEC  -> {util:.0f} % utilization")
        for h in (1.0, 0.5):
            wh_max = max_w * h
            pct = wh_max / PACK_WH * 100
            print(f"    {h:.1f} h at max: {wh_max:.1f} Wh = {pct:.1f} % of "
                  f"6S1P P42A ({PACK_WH:.1f} Wh)")

    print("\n" + "=" * 76)
    print("TOTAL ELECTRONICS BUDGET (avionics + FPV) [D]")
    print("=" * 76)
    for name in ("O4 Air Unit Pro", "O4 Air Unit"):
        _, rows = model_power(name)
        max_w = max(r[1] for r in rows if r[0])
        tot = reference_avionics_w() + max_w
        battery_w = tot / REFERENCE_BEC_EFFICIENCY
        print(f"  {name} at max: avionics {reference_avionics_w():.1f} W + FPV {max_w:.1f} W "
              f"= {tot:.1f} W rail / {battery_w:.1f} W battery "
              f"= {battery_w/CRUISE_W*100:.1f} % of O1 "
              f"({CRUISE_W:.0f} W)")
        print(f"    1 h of electronics = {battery_w:.1f} Wh battery = "
              f"{battery_w/PACK_WH*100:.1f} % "
              f"of the 6S1P P42A pack")

    checks = {
        "O4 Air Unit reference battery hotel load is 11.54 W": abs(
            reference_hotel_load_w() - 10.3875 / 0.90) < 1e-12,
        "O1 battery-power ceiling is 109.25 W": abs(CRUISE_W - 109.25) < 1e-12,
        "Article #1 hotel load is below 15 percent of O1 power":
            reference_hotel_load_w() / CRUISE_W < 0.15,
    }
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
