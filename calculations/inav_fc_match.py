#!/usr/bin/env python3
"""
INAV flight-controller compatibility check for the Salamandra.

Cross-checks each candidate FC (from research/I-17) against the avionics
requirements of the Salamandra (guide §11 / docs/00 §3.5):

    - INAV 9.1+ firmware target exists
    - >= 5 PWM/servo outputs  (4x digital servos + 1x ESC)
    - >= 2 UARTs (RX + GPS), 3 desired (telemetry/VTX)
    - >= 1 I2C (digital pitot MS4525 + compass)
    - blackbox (SD or flash) MANDATORY (E2/E7 instrumentation)
    - current sensor (onboard or external input) for the O1 energy claim
    - barometer (INAV RTH)
    - input voltage must cover 6S: up to ~25.2 V

Outputs are [D] derived from the declared board specs [M] (sources in I-17).
This is a reference for the designer, not a decision; every board listed is a
real, purchasable/legacy product.
"""
import json

# --- Salamandra avionics requirements (guide §11, docs/00 §3.5) ------------
REQ = {
    "inav_target": "INAV 9.1+ target exists",
    "pwm":         5,     # 4x servos + 1x ESC
    "uart":        2,     # RX + GPS
    "uart_des":    3,     # + telemetry / VTX control
    "i2c":         1,     # digital pitot (MS4525) + compass
    "blackbox":    True,  # SD or flash, mandatory
    "current":     True,  # O1 energy measurement
    "baro":        True,
    "v_max":       25.2,  # V, 6S fully charged
}

# --- candidate boards (specs [M]; price [E]/[M] marked) ---------------------
# fields: name, mcu, imu, baro, osd, bb, uarts, i2c, pwm, current_ok, baro_ok,
#         vmin, vmax, bec5v, bec_servo, size_mm, mount, weight_g, target,
#         price_usd, status
BOARDS = [
    dict(name="Matek F405-WING (v1)", mcu="STM32F405 168MHz", imu="MPU6000",
         baro="BMP280", osd="AT7456E", bb="MicroSD", uarts=6, i2c=2, pwm=9,
         current=True, vmin=9, vmax=30, bec5v="2A", bec_servo="5A/6A pk",
         size=(56, 36, 13), mount="30.5x30.5", weight=25, target="MATEKF405SE",
         price=45, status="EOL"),
    dict(name="Matek F405-WING-V2", mcu="STM32F405 168MHz 1MB", imu="ICM42688P",
         baro="DPS310", osd="AT7456E", bb="MicroSD", uarts=6, i2c=2, pwm=10,
         current=True, vmin=9, vmax=30, bec5v="2A", bec_servo="5A/6A pk",
         size=(54, 36, 13), mount="30.5x30.5", weight=25, target="MATEKF405SE",
         price=50, status="Current"),
    dict(name="Matek F765-WING", mcu="STM32F765 216MHz 2MB", imu="MPU6000+ICM20602",
         baro="BMP280", osd="AT7456E", bb="MicroSD (SDIO)", uarts=7, i2c=2, pwm=12,
         current=True, vmin=9, vmax=36, bec5v="2A", bec_servo="8A/10A pk",
         size=(54, 36, 13), mount="30.5x30.5", weight=26, target="MATEKF765",
         price=80, status="EOL"),
    dict(name="Matek F722-WING", mcu="STM32F722 216MHz", imu="MPU6000",
         baro="BMP280", osd="AT7456E", bb="MicroSD", uarts=5, i2c=2, pwm=8,
         current=True, vmin=9, vmax=36, bec5v="2A", bec_servo="5A",
         size=(54, 36, 13), mount="30.5x30.5", weight=25, target="MATEKF722SE",
         price=70, status="EOL"),
    dict(name="Matek F411-WING", mcu="STM32F411 100MHz", imu="MPU6000",
         baro="BMP280", osd="AT7456E", bb=None, uarts=2, i2c=2, pwm=7,
         current=True, vmin=9, vmax=30, bec5v="2A", bec_servo="3A",
         size=(41, 28, None), mount="30.5x30.5", weight=12, target="MATEKF411",
         price=20, status="EOL"),
    dict(name="Matek F411-WSE", mcu="STM32F411 100MHz", imu="MPU6000",
         baro="BMP280", osd="AT7456E", bb=None, uarts=2, i2c=2, pwm=6,
         current=True, vmin=9, vmax=30, bec5v="2A", bec_servo="3.5A/5A pk",
         size=(28, 28, None), mount="30.5x30.5", weight=8.5, target="MATEKF411SE",
         price=15, status="EOL"),
    dict(name="Foxeer F405 V2", mcu="STM32F405RGT6 168MHz", imu="ICM42688-P",
         baro="DPS310", osd="AT7456E", bb="16MB flash", uarts=6, i2c=1, pwm=6,
         current=False, vmin=14, vmax=34, bec5v="3A", bec_servo="--",
         size=(37, 37, None), mount="30.5x30.5", weight=8.4, target="FOXEERF405V2",
         price=39.9, status="Current"),
    dict(name="SpeedyBee F405 WING APP", mcu="STM32F405 168MHz 1MB",
         imu="ICM42688-P", baro="SPL06-001", osd="AT7456E", bb="MicroSD",
         uarts=6, i2c=1, pwm=12, current=True, vmin=7, vmax=36, bec5v="2.4A",
         bec_servo="4.5A/5.5A pk", size=(36.5, 36.5, 7), mount="30.5x30.5",
         weight=8.9, target="SPEEDYBEEF405WING", price=39.99, status="Current"),
]


def check(b, req):
    """Return (ok, reasons) for a board vs the Salamandra requirements."""
    fails = []
    if b["target"] is None:
        fails.append("no INAV target")
    if b["pwm"] < req["pwm"]:
        fails.append(f"{b['pwm']} PWM < {req['pwm']}")
    if b["uarts"] < req["uart"]:
        fails.append(f"{b['uarts']} UARTs < {req['uart']}")
    if b["i2c"] < req["i2c"]:
        fails.append(f"{b['i2c']} I2C < {req['i2c']}")
    if not b["bb"]:
        fails.append("no blackbox (mandatory)")
    if not b["current"]:
        fails.append("no current sensor input")
    if not b["baro"]:
        fails.append("no barometer")
    if b["vmax"] < req["v_max"]:
        fails.append(f"Vmax {b['vmax']}V < 25.2V (6S)")
    tight = b["uarts"] == req["uart"]
    return (not fails, fails, tight)


def main():
    print("=" * 78)
    print("INAV FC COMPATIBILITY — Salamandra avionics requirements")
    print("=" * 78)
    print("Requirements (guide §11 / docs/00 §3.5):")
    print(f"  PWM outputs >= {REQ['pwm']} (4x servos + 1x ESC) | "
          f"UARTs >= {REQ['uart']} (>= {REQ['uart_des']} desired) | "
          f"I2C >= {REQ['i2c']}")
    print("  blackbox MANDATORY | current sensor | barometer | "
          f"input >= {REQ['v_max']} V (6S)")
    print()

    hdr = (f"{'board':>24} {'MCU':>20} {'UART':>4} {'I2C':>3} {'PWM':>3} "
           f"{'BB':>6} {'cur':>4} {'baro':>4} {'Vmax':>5} {'mass':>5} "
           f"{'target':>18} {'OK':>3}")
    print(hdr)
    print("-" * 78)
    for b in BOARDS:
        ok, fails, tight = check(b, REQ)
        tag = "YES" if ok else "no"
        tag = tag + "*" if (ok and tight) else tag
        bb = str(b["bb"]).replace("MicroSD", "SD")
        print(f"{b['name']:>24} {b['mcu'][:20]:>20} {b['uarts']:>4} {b['i2c']:>3} "
              f"{b['pwm']:>3} {bb:>6} {str(bool(b['current'])):>4} "
              f"{str(bool(b['baro'])):>4} {b['vmax']:>5.0f} {b['weight']:>5.1f} "
              f"{b['target']:>18} {tag:>3}")
    print()

    print("-" * 78)
    print("DETAIL")
    print("-" * 78)
    for b in BOARDS:
        ok, fails, tight = check(b, REQ)
        print(f"\n{b['name']}  ({b['status']})")
        print(f"  {b['mcu']} | IMU {b['imu']} | baro {b['baro']} | OSD {b['osd']} | "
              f"BB {b['bb']}")
        print(f"  {b['uarts']} UART | {b['i2c']} I2C | {b['pwm']} PWM | "
              f"input {b['vmin']}-{b['vmax']} V | BEC 5V {b['bec5v']} / "
              f"servo {b['bec_servo']}")
        sz = b['size']
        print(f"  size {sz[0]}x{sz[1]}{('x'+str(sz[2])) if sz[2] else ''} mm | "
              f"mount {b['mount']} | {b['weight']} g | "
              f"INAV target {b['target']} | ~US${b['price']}")
        if ok:
            note = "OK — meets all requirements" + (" (UART budget exactly met)" if tight else "")
            print(f"  -> {note}")
        else:
            print(f"  -> MISSES: {', '.join(fails)}")

    print("\n" + "=" * 78)
    print("OBSERVATIONS (reference, not a verdict)")
    print("=" * 78)
    print(" - F411-class boards fail the MANDATORY blackbox requirement; usable")
    print("   only with an external SD logger (adds mass/wiring).")
    print(" - All F405/F722/F765/H7 boards satisfy the servo + UART budget.")
    print(" - Foxeer F405 V2 has no onboard current input; needs an external")
    print("   current sensor for the O1 energy claim.")
    print(" - Every board's PWM outputs are shared between servos and motor;")
    print("   the wing wiring must respect the INAV servo/motor mapping.")
    print(" - Voltage: 6S fully charged is 25.2 V; every board listed covers it.")

    # --- footprint summary for the CORE avionics station -------------------
    print("\n" + "=" * 78)
    print("FOOTPRINT SUMMARY FOR THE CORE AVIONICS STATION")
    print("=" * 78)
    ls = sorted(b["size"][0] for b in BOARDS)
    ws = sorted(b["size"][1] for b in BOARDS)
    hs = sorted(b["size"][2] for b in BOARDS if b["size"][2])
    ms = sorted(b["weight"] for b in BOARDS)
    l_min, l_max, l_avg = ls[0], ls[-1], sum(ls) / len(ls)
    w_min, w_max, w_avg = ws[0], ws[-1], sum(ws) / len(ws)
    h_min, h_max, h_avg = hs[0], hs[-1], sum(hs) / len(hs)
    m_min, m_max, m_avg = ms[0], ms[-1], sum(ms) / len(ms)
    print(f"  Mounting pattern (all boards): 30.5 x 30.5 mm, Phi4 mm  [M]")
    print(f"  MINIMUM (per-dimension floor): {l_min:.0f} x {w_min:.0f} mm "
          f"({h_min:.0f} mm h)  - {m_min:.1f} g smallest board")
    print(f"  AVERAGE board envelope : {l_avg:.0f} x {w_avg:.0f} mm "
          f"({h_avg:.0f} mm h)  - {m_avg:.1f} g  (all 8 surveyed)")
    print(f"  MAXIMUM (per-dimension ceiling): {l_max:.0f} x {w_max:.0f} mm "
          f"({h_max:.0f} mm h)  - {m_max:.0f} g heaviest board")
    rec = (l_max + 8, w_max + 8, h_max + 8)
    print(f"  RECOMMENDED station cavity (largest board + 8 mm clearance "
          f"+ cables):")
    print(f"      {rec[0]:.0f} x {rec[1]:.0f} x {rec[2]:.0f} mm  ->  "
          f"accepts every board in this survey")
    print(f"  Mass budget absorbed: worst board {m_max:.0f} g << 110 g "
          f"avionics allowance (balance_cg.py)")


if __name__ == "__main__":
    main()
