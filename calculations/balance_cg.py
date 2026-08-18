#!/usr/bin/env python3
"""Mass balance and battery-cradle layout for Salamandra Article #1.

The layout is solved self-consistently: changing sweep moves the neutral point,
the shell centroid and the carbon-tube centroid; shortening the cradle boom also
changes boom mass, boom centroid and camera station. The reference pack is the
I-16 6S1P P42A pack (445 g), consistent with ``mass_budget.py``.

Coordinates: x aft, origin at the root quarter chord. Outputs are [D] on [E]
component locations until CAD mass properties replace the table in F2/P1-P3.
"""
import numpy as np
from battery_pack_layout import reference_pack_envelope
from design_config import (
    ARTICLE_CLEAN_MASS_KG,
    MAC,
    STATIC_MARGIN,
    SWEEP_C4_DEG,
    planform_centroid,
    stall_speed,
    x_c4,
)
from mass_budget import build, pack_mass

NP_VLM = -75.8e-3       # m, VLM 40x6, I-21 [D]
NP_WL = -72.9e-3        # m, Weissinger-L ny=100, I-21 [D]
CG_TARGET = NP_VLM - STATIC_MARGIN * MAC
R_CG = 5e-3             # m, docs/00 section 3.3
NOSE_POD_TIP = -132e-3  # unchanged root-geometry datum

# I-16 P42A pack model: n cells x 70 g + 25 g packaging.
PACKS = [(name, pack_mass(name, "P42A") / 1000.0)
         for name in ("4S1P", "6S1P", "4S2P", "6S2P")]
PACK_LEN = {name: reference_pack_envelope(name)[0] / 1000.0
            for name in ("4S1P", "6S1P")}
REFERENCE_PACK = pack_mass("6S1P", "P42A") / 1000.0
PACK_CLEARANCE = 0.005

# Prototype 0.1 calibration: the old structural check gave 26 g over the
# 384 mm support span plus 50 mm inserted aft of the CORE support. The cradle
# is modelled at its own centroid instead of being lumped at the tube midpoint.
TUBE_CORE_INSERTION = 0.050
AL_TUBE_LINEAR_MASS = 2700.0 * np.pi / 4.0 * (0.008 ** 2 - 0.006 ** 2)
CRADLE_MASS = 0.015
CRADLE_LENGTH = 0.201
CAMERA_FROM_BAY_FWD = 0.066  # reproduces the old -450 mm station


def reference_mass_breakdown():
    """Return the canonical CLEAN mass rows in kilograms, keyed by part."""
    rows, totals = build("all_petg")
    masses = {row["part"]: row["m"] / 1000.0 for row in rows}
    if abs(totals["auw"] / 1000.0 - ARTICLE_CLEAN_MASS_KG) > 1e-8:
        raise RuntimeError("mass_budget default no longer matches the design contract")
    return masses


REFERENCE_MASSES = reference_mass_breakdown()


def pack_station(m_no_batt, moment_no_batt, m_pack, cg):
    """Pack station required for a target aircraft CG."""
    return (cg * (m_no_batt + m_pack) - moment_no_batt) / m_pack


def component_table(sweep_deg, bay_fwd):
    """Non-battery components for one sweep and iterated bay position."""
    extension = max(NOSE_POD_TIP - bay_fwd, 0.0)
    tube_mass = AL_TUBE_LINEAR_MASS * (extension + TUBE_CORE_INSERTION)
    tube_station = 0.5 * (bay_fwd + NOSE_POD_TIP + TUBE_CORE_INSERTION)
    cradle_station = bay_fwd + 0.5 * CRADLE_LENGTH
    boom_mass = CRADLE_MASS + tube_mass
    boom_station = (CRADLE_MASS * cradle_station + tube_mass * tube_station) / boom_mass
    camera_station = bay_fwd + CAMERA_FROM_BAY_FWD
    printed_shell = sum(REFERENCE_MASSES[name]
                        for name in ("core", "wings", "tips", "elevons"))
    camera_mass = 0.0030
    return [
        ("PETG shell (ADR-0043 cap)", printed_shell,
         planform_centroid(sweep_deg)),
        ("Carbon (mean c/4, y=195..585)", REFERENCE_MASSES["carbon"],
         x_c4(0.390, sweep_deg)),
        ("Motor + APC 8x8 assembly",
         REFERENCE_MASSES["motor"] + REFERENCE_MASSES["prop"], +217e-3),
        ("ESC", REFERENCE_MASSES["esc"], +40e-3),
        ("Avionics (SpeedyBee FC+PDB etc.)", REFERENCE_MASSES["avionics"],
         -10e-3),
        ("Corona servos + elevon balance",
         REFERENCE_MASSES["servos"] + REFERENCE_MASSES["balance"], -5e-3),
        ("Hardware", REFERENCE_MASSES["hardware"], +50e-3),
        ("FPV DJI O4 Lite - camera", camera_mass, camera_station),
        ("FPV DJI O4 Lite - VTX/antenna",
         REFERENCE_MASSES["fpv"] - camera_mass, +10e-3),
        ("Battery boom + cradle", boom_mass, boom_station),
    ]


def solve_reference_layout(sweep_deg=SWEEP_C4_DEG, np_x=NP_VLM,
                           pack_mass=REFERENCE_PACK):
    """Iterate boom mass/camera station and the 6S1P R-CG cradle envelope."""
    cg_target = np_x - STATIC_MARGIN * MAC
    bay_fwd = -0.47
    for _ in range(100):
        components = component_table(sweep_deg, bay_fwd)
        m0 = sum(m for _, m, _ in components)
        moment0 = sum(m * x for _, m, x in components)
        forward_pack_station = pack_station(
            m0, moment0, pack_mass, cg_target - R_CG)
        updated = forward_pack_station - PACK_LEN["6S1P"] / 2.0 - PACK_CLEARANCE
        if abs(updated - bay_fwd) < 1e-10:
            bay_fwd = updated
            break
        bay_fwd = 0.5 * (bay_fwd + updated)
    else:
        raise RuntimeError("battery-cradle iteration did not converge")

    components = component_table(sweep_deg, bay_fwd)
    m0 = sum(m for _, m, _ in components)
    moment0 = sum(m * x for _, m, x in components)
    bay_aft = pack_station(m0, moment0, pack_mass, cg_target + R_CG) \
        + PACK_LEN["6S1P"] / 2.0 + PACK_CLEARANCE
    return {
        "sweep": sweep_deg,
        "np": np_x,
        "cg_target": cg_target,
        "components": components,
        "m0": m0,
        "moment0": moment0,
        "pack_station": pack_station(m0, moment0, pack_mass, cg_target),
        "bay_fwd": bay_fwd,
        "bay_aft": bay_aft,
        "extension": max(NOSE_POD_TIP - bay_fwd, 0.0),
    }


def main():
    layout = solve_reference_layout()
    m0, moment0 = layout["m0"], layout["moment0"]
    print("=" * 76)
    print("SALAMANDRA MASS BALANCE - ADR-0043, 6S1P P42A REFERENCE")
    print("=" * 76)
    print(f"  sweep c/4 = {SWEEP_C4_DEG:+.1f} deg  MAC = {MAC*1000:.1f} mm")
    print(f"  NP VLM / Weissinger = {NP_VLM*1000:+.1f} / {NP_WL*1000:+.1f} mm")
    print(f"  target CG = {CG_TARGET*1000:+.1f} mm (SM {STATIC_MARGIN*100:.0f} % MAC)")

    print("\n  Mass table without pack:")
    for name, mass, station in layout["components"]:
        print(f"    {name:42s} {mass*1000:6.1f} g  x={station*1000:+7.1f} mm")
    print(f"    {'Subtotal':42s} {m0*1000:6.1f} g  "
          f"CG={moment0/m0*1000:+7.1f} mm")

    print("\n  Required pack stations at target CG:")
    for name, mass in PACKS:
        target = pack_station(m0, moment0, mass, CG_TARGET)
        forward = pack_station(m0, moment0, mass, CG_TARGET - R_CG)
        aft = pack_station(m0, moment0, mass, CG_TARGET + R_CG)
        print(f"    {name:5s} {mass*1000:5.0f} g: x={target*1000:+7.1f} mm  "
              f"band {forward*1000:+7.1f}..{aft*1000:+7.1f} mm")

    print("\n  Reference 6S1P cradle:")
    print(f"    pack center x={layout['pack_station']*1000:+.1f} mm")
    print(f"    cradle envelope {layout['bay_fwd']*1000:+.1f}.."
          f"{layout['bay_aft']*1000:+.1f} mm "
          f"({(layout['bay_aft']-layout['bay_fwd'])*1000:.1f} mm)")
    print(f"    forward extension from nose pod={layout['extension']*1000:.1f} mm")

    print("\n  Envelope checks:")
    for name, mass in PACKS:
        auw = m0 + mass
        target = pack_station(m0, moment0, mass, CG_TARGET)
        physical = name in PACK_LEN
        fits = physical and (
            layout["bay_fwd"] + PACK_LEN[name] / 2.0 <= target
            <= layout["bay_aft"] - PACK_LEN[name] / 2.0)
        reason = "IN" if fits else (
            "OUT: station" if physical else "OUT: no one-layer pack envelope")
        v_stall = 3.6 * stall_speed(auw)
        print(f"    {name:5s}: AUW={auw*1000:.0f} g  V_stall={v_stall:.1f} km/h  {reason}")

    checks = {
        "canonical shell centroid": abs(planform_centroid()*1000 + 21.17) < 0.2,
        "VLM/Weissinger NP agreement < 5 mm": abs(NP_VLM - NP_WL) < 0.005,
        "SM is 8 percent MAC": abs((NP_VLM - CG_TARGET) / MAC - 0.08) < 1e-12,
        "reference pack station is inside cradle": (
            layout["bay_fwd"] + PACK_LEN["6S1P"] / 2.0
            <= layout["pack_station"]
            <= layout["bay_aft"] - PACK_LEN["6S1P"] / 2.0),
        "boom estimate 36-40 g": 0.036 <= layout["components"][-1][1] <= 0.040,
        "balance CLEAN mass equals mass_budget": abs(
            m0 + REFERENCE_PACK - ARTICLE_CLEAN_MASS_KG) < 5e-5,
    }
    print("\n  Validation:")
    for name, passed in checks.items():
        print(f"    [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\n  VALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
