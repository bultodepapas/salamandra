#!/usr/bin/env python3
"""
FPV system power budget — DJI O4 / O4 Pro / O4 Lite (research/I-19).

Power draw values are measured [M] (Oscar Liang, armed + recording unless noted):
    O4 Pro (@9V):  1200mW 1.16 A | 700mW 1.05 | 400mW 0.98 | 200mW 0.92
                   100mW 0.87 | 50mW 0.84 | 25mW 0.82 A | disarmed 0.33 A
    O4 Lite (@5V): 700mW 1.2 A (6 W) | disarmed 0.6 A (3 W)
The O4 (standard) shares the same transmission module as the O4 Pro, so its
power draw is taken as identical [I]. Input ranges and weights are [M] (DJI).

Outputs [D]: per-level power and current at user-selected input voltage, BEC
margin against the Matek 9V/2A and 5V/2A rails, and energy impact on the
reference 6S1P P42A pack (90.7 Wh, I-16). Reference, not a verdict.
"""
import sys

# --- Salamandra FPV assumptions ---------------------------------------------
BEC_9V = (2.0, 3.0)      # A continuous / peak, Matek 9V BEC
BEC_5V = (2.0, 3.0)      # A continuous / peak, Matek 5V BEC
PACK_WH = 90.7            # Wh, 6S1P P42A (I-16 §6.1)
CRUISE_W = 110.0          # W, guide §10.1 (5 A @ 22 V, 6S)
AVIONICS_W = 6.6          # W, I-17 §6.2 (avionics without FPV)

# model : (measured voltage V, disarmed current A, {power_mW: current_A})
UNITS = {
    "O4 Pro": dict(v=9.0, disarmed=0.33, draw={
        1200: 1.16, 700: 1.05, 400: 0.98, 200: 0.92,
        100: 0.87, 50: 0.84, 25: 0.82}),
    "O4 (standard)": dict(v=9.0, disarmed=0.33, draw={
        700: 1.05, 400: 0.98, 200: 0.92,
        100: 0.87, 50: 0.84, 25: 0.82}),
    "O4 Lite": dict(v=5.0, disarmed=0.60, draw={700: 1.2}),
}

# model : (input range V, weight g, VTX size, camera size, sensor)  [M]
DIMS = {
    "O4 Pro": ((7.4, 26.4), 33, "33.5x33.5x13", "25x23x20", "1/1.3 in"),
    "O4 (standard)": ((7.4, 26.4), 32, "33.5x33.5x13", "25.55x20x23.30", "1/2 in"),
    "O4 Lite": ((3.7, 13.2), 8.2, "30x30x6", "13.44x12.36x16.50", "1/2 in"),
}


def model_power(name, v_input=None):
    """Return list of (mW, W, I_at_input) at the given input voltage."""
    u = UNITS[name]
    v = v_input or u["v"]
    rows = []
    for mw, ia in sorted(u["draw"].items()):
        w = ia * u["v"]            # measured W (constant-power converter)
        rows.append((mw, w, w / v))
    # disarmed
    wd = u["disarmed"] * u["v"]
    rows.append((0, wd, wd / v))   # mW=0 marks disarmed
    return v, rows


def main():
    print("=" * 76)
    print("FPV SYSTEM POWER BUDGET — DJI O4 / O4 Pro / O4 Lite")
    print("=" * 76)
    for name, (vr, w, vt, cam, sen) in DIMS.items():
        print(f"\n{name}  [M]: weight {w} g | VTX {vt} mm | camera {cam} mm | "
              f"sensor {sen} | input {vr[0]}-{vr[1]} V")
    print(f"\nMeasured draw anchors [M]: O4 Pro/Lite armed+recording. "
          f"O4 (standard) = same TX module as Pro [I].")

    default_v = 9.0
    if len(sys.argv) > 1:
        try:
            default_v = float(sys.argv[1])
        except ValueError:
            pass

    for name in UNITS:
        v, rows = model_power(name, default_v)
        print(f"\n--- {name}  (input {default_v:.1f} V) ---")
        print(f"  {'level':>8} {'W':>7} {'I@%.1fV' % default_v:>10}")
        for mw, w, ia in rows:
            tag = "disarmed" if mw == 0 else f"{mw} mW"
            print(f"  {tag:>8} {w:>7.1f} {ia*1000:>9.0f} mA")

    print("\n" + "-" * 76)
    print("BEC CHECK AND ENERGY IMPACT [D]")
    print("-" * 76)
    # worst case per model: max power level
    for name in UNITS:
        v, rows = model_power(name)
        max_mw, max_w, _ = max((r for r in rows if r[0]), key=lambda r: r[0])
        min_mw, min_w, _ = min((r for r in rows if r[0]), key=lambda r: r[0])
        rail = "9V" if name != "O4 Lite" else "5V"
        bec = BEC_9V if name != "O4 Lite" else BEC_5V
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
    for name in ("O4 Pro", "O4 Lite"):
        _, rows = model_power(name)
        max_w = max(r[1] for r in rows if r[0])
        tot = AVIONICS_W + max_w
        print(f"  {name} at max: avionics {AVIONICS_W:.1f} W + FPV {max_w:.1f} W "
              f"= {tot:.1f} W  = {tot/CRUISE_W*100:.1f} % of cruise "
              f"({CRUISE_W:.0f} W)")
        print(f"    1 h of electronics = {tot:.1f} Wh = {tot/PACK_WH*100:.1f} % "
              f"of the 6S1P P42A pack")


if __name__ == "__main__":
    main()
