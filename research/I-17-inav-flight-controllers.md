# I-17 — INAV flight controllers: popular boards and technical data sheets

**Status:** Open — reference catalog · **Feeds:** guide §11 (avionics), CORE avionics station (§7.6), docs/00 §3.5

> **This is a reference catalog, not a decision.** It reports the verified
> technical data of the most popular INAV-capable flight controllers so the
> builder can choose. Every board listed is a real product (current or legacy).
> The compatibility check against the Salamandra avionics requirements
> (`calculations/inav_fc_match.py`) is factual data for the designer, not a
> prohibition — a board that "misses" a requirement is still usable if the
> builder accepts the consequence (e.g. an external logger).

## 1. Scope and method

The aircraft uses **INAV 9.1+** and requires (guide §11 / docs/00 §3.5): 4× digital
servos, **pitot mandatory**, blackbox (SD or flash, mandatory — the instrument of
tests E2/E7), GPS + magnetometer, RX, autolaunch, current sensor. The survey
identified the most popular INAV fixed-wing boards from manufacturer pages,
official stores and the INAV firmware target list, and verified each spec against
**primary sources** (manufacturer product pages / datasheets). Every spec carries
its confidence tag and source in §9.

The full list of supported boards is authoritative from the INAV source tree
`src/main/target` (`[M]`, GitHub iNavFlight/inav @ master). Target names quoted
below are exactly as they appear there.

### Popularity ranking (consensus, reasoning in §8)

| # | Board | INAV target | Role |
|---|---|---|---|
| 1 | **Matek F405-WING / -V2** | `MATEKF405SE` | The classic fixed-wing INAV board; the reference of the whole ecosystem |
| 2 | **SpeedyBee F405 WING** | `SPEEDYBEEF405WING` | Current budget fixed-wing board with BLE/WiFi app setup |
| 3 | **Matek F765-WING** | `MATEKF765` | Premium legacy (EOL); most UARTs/PWM in the WING family |
| 4 | **Matek F722-WING** | `MATEKF722SE` | Legacy mid-range (EOL) |
| 5 | **Foxeer F405 V2** | `FOXEERF405V2` | Popular budget F4 (multirotor-oriented, INAV-capable) |
| 6 | **Matek F411-WING / F411-WSE** | `MATEKF411` / `MATEKF411SE` | Small/cheap (EOL); minimal UARTs, no blackbox |
| 7 | **Omnibus F4 Pro** | `OMNIBUSF4PRO` | Legacy classic, still supported |
| 8 | **JHEMCU GF405 Wing / GF722** | `JHEMCUF405WING` / `JHEMCUF722` | Budget wing boards (specs UNVERIFIED in this pass) |

> **Notable exclusion:** the Matek **H7A3-WING** (current premium wing board) does
> **not** have an INAV target in `src/main/target` — it is ArduPilot-only. If INAV
> is the firmware, it is not an option; if ArduPilot enters scope it is. This is
> exactly the kind of datum the builder needs before buying.

## 2. Board data sheets (verified)

Dimensions are L×W×H mm. Mount = hole pattern. BEC = built-in regulators.

### 2.1 Matek F405-WING v1 (EOL) — target `MATEKF405SE` `[M]`

| Parameter | Value |
|---|---|
| MCU | STM32F405, 168 MHz |
| IMU | MPU6000 (SPI) |
| Baro | BMP280 |
| OSD | INAV OSD / AT7456E |
| Blackbox | MicroSD slot |
| UART / I2C | 6 UART (+1 softserial) / 2 I2C |
| PWM outputs | 9 (2 motor + 7 servo) |
| Current sensor | 104 A onboard (60 A continuous sense resistor) |
| Input | 9–30 V (3–6S) |
| BEC | 5 V/2 A · 9/12 V/2 A · Vx 5 A (6 A pk) · 3.3 V/500 mA |
| Size / mount / mass | 56 × 36 × 13 mm / 30.5×30.5 (Φ4 mm) / **25 g** |
| Price | ~US$45 `[E]` |

### 2.2 Matek F405-WING-V2 (current) — target `MATEKF405SE` (≥ 6.0) `[M]`

| Parameter | Value |
|---|---|
| MCU | STM32F405RGT6, 168 MHz, 1 MB flash |
| IMU / Baro | ICM42688-P / DPS310 |
| OSD / Blackbox | AT7456E / MicroSD |
| UART / I2C | 6 UART + 1 softserial / 2 I2C |
| PWM outputs | 10 (9 + LED) |
| Current sensor | 220 A peak (100 A continuous) |
| Input | 9–30 V (3–6S) |
| BEC | 5 V/2 A · 9/12 V/2 A · Vx 5 A/6 A pk · 3.3 V/200 mA |
| Size / mount / mass | 54 × 36 × 13 mm / 30.5×30.5 / **25 g** |
| Price | ~US$50 `[E]` |
| Diff vs v1 | Type-C USB, ICM42688-P, DPS310, higher current range |

### 2.3 Matek F765-WING (EOL) — target `MATEKF765` `[M]`

| Parameter | Value |
|---|---|
| MCU | STM32F765VI, 216 MHz, 2 MB flash / 512 KB RAM |
| IMU | MPU6000 + ICM20602 (dual) |
| Baro / OSD | BMP280 / AT7456E |
| Blackbox | MicroSD (SDIO) |
| UART / I2C | 7 UART (all invertible) / 2 I2C + SPI breakout |
| PWM outputs | 12 (S1–S10 DShot-capable) |
| Current sensor | 132 A (60 A continuous) |
| Input | 9–36 V (3–8S) |
| BEC | 5 V/2 A · 9/12 V/2 A · Vx 8 A/10 A pk · 3.3 V/200 mA |
| Extras | Dual camera input, 5V/9V switcher, analog+digital airspeed inputs |
| Size / mount / mass | 54 × 36 × 13 mm / 30.5×30.5 / **26 g** |
| Price | ~US$80 `[E]` |

### 2.4 Matek F722-WING (EOL) — target `MATEKF722SE` `[M]`

| Parameter | Value |
|---|---|
| MCU | STM32F722, 216 MHz, 512 KB flash |
| IMU / Baro | MPU6000 / BMP280 |
| OSD / Blackbox | AT7456E / MicroSD |
| UART / I2C | 5 UART (all invertible) / 2 I2C |
| PWM outputs | 8 (2 motor + 6 servo) |
| Current sensor | 132 A |
| Input | 9–36 V (3–8S) |
| BEC | 5 V/2 A · 9/12 V/2 A · Vx 5 A |
| Size / mount / mass | 54 × 36 × 13 mm / 30.5×30.5 / **25 g** |
| Price | ~US$70 `[E]` |

### 2.5 Matek F411-WING and F411-WSE (EOL) — `MATEKF411` / `MATEKF411SE` `[M]`

| Parameter | F411-WING | F411-WSE |
|---|---|---|
| MCU | STM32F411, 100 MHz, 512 KB | same |
| IMU / Baro | MPU6000 / BMP280 | same |
| OSD | AT7456E | same |
| **Blackbox** | **none** | **none** |
| UART / I2C | 2 / 2 | 2 / 2 |
| PWM | 7 (2 motor + 5 servo) | 6 (2 motor + 4 servo) |
| Current | 78 A | 78 A |
| Input | 9–30 V | 9–30 V |
| BEC | 5 V/2 A · Vx 3 A | 5 V/2 A · Vx 3.5 A/5 A pk |
| Size / mount / mass | 41 × 28 mm / 30.5×30.5 / **12 g** | 28 × 28 mm / 30.5×30.5 / **8.5 g** |
| Price | ~US$20 `[E]` | ~US$15 `[E]` |

### 2.6 Foxeer F405 V2 (current) — target `FOXEERF405V2` `[M]`

| Parameter | Value |
|---|---|
| MCU | STM32F405RGT6, 168 MHz |
| IMU / Baro | ICM42688-P / DPS310 |
| OSD / Blackbox | AT7456E / 16 MB flash |
| UART / I2C | 6 UART / 1 I2C |
| PWM outputs | 6 (X8-capable output limiters) |
| **Current sensor** | **none onboard** (ADC ×3 available) |
| Input | 4–8S (14–34 V) |
| BEC | 5 V/3 A · 10 V/3 A |
| Size / mount / mass | 37 × 37 mm / 30.5×30.5 / **8.4 g** |
| Price | US$39.9 `[M]` |
| Notes | Multirotor-oriented; flight firmware shipped is BetaFlight, INAV via `FOXEERF405V2` |

### 2.7 SpeedyBee F405 WING APP (current) — target `SPEEDYBEEF405WING` `[M]`

| Parameter | Value |
|---|---|
| System | FC + PDB + wireless (BLE/WiFi) board |
| MCU | STM32F405, 168 MHz, 1 MB flash |
| IMU / Baro | ICM42688-P / SPL06-001 |
| OSD / Blackbox | AT7456E / MicroSD |
| UART / I2C | 6 UART (U6 dedicated to wireless board) / 1 I2C |
| PWM outputs | 12 (11 motor + 1 LED) |
| Current sensor | 90 A continuous / 215 A peak |
| Input | 7–36 V (2–6S) |
| BEC | FC 5.2 V/2.4 A · VTX 9 V/1.8 A · Servo 4.9 V/4.5 A (5.5 A pk) |
| Size / mass | FC 36.5 × 36.5 × 7 mm / 30.5×30.5 / **8.9 g** (+11.4 g PDB + 4.2 g wireless) |
| Price | US$39.99 `[M]` |
| Notes | Wireless board = SpeedyBee APP config over BLE/WiFi; LED strip driver |

## 3. Compatibility vs the Salamandra requirements `[D]`

Reproducible with `python3 calculations/inav_fc_match.py`. Requirements: ≥5 PWM
(4 servos + 1 ESC), ≥2 UART (RX + GPS; 3 desired), ≥1 I2C (pitot + compass),
blackbox mandatory, current sensor, barometer, input ≥25.2 V (6S).

| Board | PWM | UART | I2C | BB | Current | Vmax | Meets all |
|---|---|---|---|---|---|---|---|
| F405-WING v1 | 9 | 6 | 2 | SD | ✓ | 30 V | **YES** |
| F405-WING-V2 | 10 | 6 | 2 | SD | ✓ | 30 V | **YES** |
| F765-WING | 12 | 7 | 2 | SDIO | ✓ | 36 V | **YES** |
| F722-WING | 8 | 5 | 2 | SD | ✓ | 36 V | **YES** |
| F411-WING | 7 | 2 | 2 | — | ✓ | 30 V | no (no blackbox) |
| F411-WSE | 6 | 2 | 2 | — | ✓ | 30 V | no (no blackbox) |
| Foxeer F405 V2 | 6 | 6 | 1 | 16 MB | — | 34 V | no (no current input) |
| SpeedyBee F405 WING | 12 | 6 | 1 | SD | ✓ | 36 V | **YES** |

Interpretation (reference): the **F405/F722/F765** class and the **SpeedyBee F405
WING** satisfy the full requirement set for the reference aircraft. The F411-class
boards are usable only with an external SD logger (the mandatory blackbox). The
Foxeer F405 V2 needs an external current sensor for the O1 energy claim. These are
facts for the designer, not rulings.

## 4. Footprint and mounting for the CORE

- **30.5 × 30.5 mm** (Φ4 mm, M3 grommets) is the de-facto standard across every
  board in this survey `[M]` — one mounting pattern covers the whole catalog.
- Board envelope range: **28×28** (smallest, F411-WSE) to **56×36 mm**
  (F405-WING v1). Thickness ~7–13 mm.
- Mass range: **8.4 g** (Foxeer) to **26 g** (F765-WING); the reference avionics
  mass budget in `balance_cg.py` (110 g total avionics incl. pitot/GPS/RX) absorbs
  any of them with room.
- BEC output for servos: F405/F722/F765-class boards carry a **Vx servo BEC**
  (5 A, up to 8 A on the F765). With 4 digital servos at ~13–15 g class, current is
  low single-digit amps — any listed board suffices `[D]`.

### 4.1 Size summary — minimum / average / recommended (for the designer)

Computed by `calculations/inav_fc_match.py` from the 8 surveyed boards `[D]`
(board specs `[M]`). The **minimum** and **maximum** are per-dimension floors and
ceilings across the survey (they do not correspond to a single board); the
**average** is the arithmetic mean of all 8.

| Size | Length × Width × Height | Board mass | Interpretation |
|---|---|---|---|
| **Minimum** (per-dimension floor) | **28 × 28 × 7 mm** | 8.4 g | Smallest class (F411-WSE / 20-mm-ish slim boards) |
| **Average** (8 surveyed) | **45 × 34 × 12 mm** | 17.4 g | Typical INAV fixed-wing board |
| **Maximum** (per-dimension ceiling) | **56 × 37 × 13 mm** | 26 g | Largest class (F405-WING v1 / F765-WING) |
| **Recommended station cavity** | **64 × 45 × 21 mm** | — | Largest board + 8 mm clearance per axis + cable/bend room; accepts every board in this survey |

> **Design guidance:** model the CORE avionics station to the **recommended
> cavity 64 × 45 × 21 mm** with a **30.5 × 30.5 mm, Φ4 mm** boss/tray — that one
> pattern accepts the entire catalog, past and present. A station sized only for
> the **average** (45 × 34 × 12 mm) accepts most boards but not the largest
> (F405-WING v1); a station at the **minimum** (28 × 28) commits the builder to a
> specific tiny board. The reference guide §11 avionics mass (110 g) absorbs any
> board: the heaviest (26 g) is 24 % of the allowance `[D]`.

## 5. Wiring notes for this aircraft

- **Pitot (mandatory):** digital MS4525 on **I2C** — every board here has ≥1 I2C.
  The F405-WING/F765-WING also offer an analog airspeed ADC input `[M]`.
- **GPS + magnetometer:** GPS on a free UART (boards have 2–7), compass on I2C.
  Keep the compass away from the battery current path (guide §11).
- **RX:** SBUS/CRSF on a UART with built-in inversion where needed (F405-WING
  UART2-RX has an SBUS inverter) `[M]`.
- **Blackbox:** mandatory; the F411 boards have none — external logger required.
- **Servo/motor PWM mapping:** S1–S2 are motors in the Matek WING targets; the
  elevons use the servo outputs. Respect the INAV mixer/mapping (guide §12).

## 6. Electrical power consumption

### 6.1 Per-component consumption

Values from web research; `[M]` = measured/published, `[E]` = declared estimate.
Computed budget: `python3 calculations/inav_fc_match.py`.

| Component | Min mA | Max mA | Rail | Basis |
|---|---|---|---|---|
| FC board — INAV F4 wing (OSD+SD) | 150 | 250 | 5 V | scaled from measured F4 ≈ 93 mA `[M]` (quadmeup) + OSD/SD overhead `[E]` |
| RX — ELRS 2.4G (EP1 class) | 100 | 200 | 5 V | `[E]` (measured 8ch FM RX ≈ 100 mA `[M]`) |
| GPS M10 + compass | 25 | 60 | 5 V | `[M]` (BN-220 35 / BN-880 45 / M10 25 mA) |
| Pitot MS4525 (I2C) | 5 | 15 | 5 V | `[E]` |
| Buzzer (transient) | 20 | 30 | 5 V | `[E]` |
| 4× servo 13–15 g digital — idle | 40 | 80 | Vx | `[E]` |
| 4× servo — active/mixed | 600 | 1200 | Vx | `[E]` |
| 4× servo — stall (brief) | 2800 | 4000 | Vx | `[E]` |

Measured anchors `[M]`: F4-class FC ≈ 93 mA, FC ≈ 100 mA, 8ch RX ≈ 100 mA,
GPS modules 25–45 mA. Modern F4 wing boards with OSD + SD + baro draw about
150–250 mA in practice; F7/H7 slightly more (200–350 mA) `[E]`.

### 6.2 Total budget, BEC margin and energy impact `[D]`

| Rail | Load | BEC available | Utilization |
|---|---|---|---|
| 5 V avionics (FC+RX+GPS+pitot+buzzer) | **300–555 mA** | 2 A (F405/F765 5V BEC) | 15–28 % |
| Servo rail (4 servos active) | **600–1200 mA** | 5 A Vx (8 A F765) | 12–24 % |
| Servo rail (4 servos stall, brief) | **2800–4000 mA** | 5 A Vx | ≤ 80 % |

- **Total avionics rail power = 6.64 W** (≈2.1 W 5 V rail + ≈4.5 W servos) `[D]`.
- **Battery-side power = 7.38 W** at the shared 90 % BEC efficiency, or 6.75 % of
  O1's 109.25 W total battery-power ceiling `[D]`.
- **Energy impact:** 1 h burns **≈7.38 Wh = 8.1 %** of a 6S1P P42A pack
  (90.72 Wh, I-16 §6.1) `[D]`. Not negligible for the O1 efficiency
  claim, but small enough that the range equation is dominated by propulsion.
- **BEC sizing conclusion:** the 2 A 5 V BEC and 5 A servo BEC of the F405/F765
  class carry the full avionics + servo load with 3–4× margin `[D]`. The F411 class
  (Vx 3 A) also suffices for the servo load but fails on blackbox (see §3).

## 7. Observations (for the builder)

1. **The Matek F405-WING-V2 is the least-risk choice**: current, every resource
   needed, the classic INAV target `MATEKF405SE`, Type-C, and the same footprint
   as the rest of the family.
2. **SpeedyBee F405 WING** is the strongest current budget option: app-based
   setup (BLE/WiFi), 12 PWM, 90 A current sensor, same 30.5×30.5 footprint, and
   it is fixed-wing-first (unlike the Foxeer).
3. **H7A3-WING has no INAV target** — if the firmware is INAV, exclude it.
4. **Price band:** US$15–80; the requirement-complete set starts at ~US$40.
5. **UART budget is not a constraint** for any F405+ board (5–7 UARTs vs 2–3
   needed); it only binds on the F411 class (exactly 2), and there the blackbox
   absence is the harder constraint.

## 8. Reproduction

```bash
python3 calculations/inav_fc_match.py
```

Self-validating: the printed matrix must show **YES** for the five
F405/F722/F765/SpeedyBee entries and the stated MISS reasons for F411 (no
blackbox) and Foxeer (no current input); the footprint summary must print
**min 28×28×7 / avg 45×34×12 / max 56×37×13 mm / recommended 64×45×21 mm**; and
the power budget must print **5 V rail 300–555 mA, avionics 6.64 W at the rails,
7.38 W at the battery and 8.1 % of a 6S1P P42A pack per hour**. A change to the requirement
set, board specs, or consumption values must reproduce these lines.

## 9. Popularity basis

Ranking from cross-reference of: the INAV supported-target list (which boards
are actively maintained in 2026), manufacturer product availability, and the
presence of these boards in fixed-wing build guides/forums (Oscar Liang, RCG
Matek F405-WING thread, INAV Facebook community). Matek WING series dominates
fixed-wing INAV by volume of guides and aftermarket parts; SpeedyBee is the
fastest-growing current alternative.

## 10. Sources

1. INAV — supported targets list, `src/main/target` (GitHub iNavFlight/inav @ master). `[M]`
2. MATEKSYS — F405-WING product page (`?portfolio=f405-wing`), F405-WING-V2 (`?portfolio=f405-wing-v2`), F765-WING (`?portfolio=f765-wing`), WING-series comparison table (F722-WING, F411-WSE, F411-WING). `[M]`
3. Foxeer — F405 V2 product page (SKU MR1836). `[M]`
4. SpeedyBee — F405 WING APP product page. `[M]`
5. Prices marked `[E]` are store-price estimates; `[M]` prices are the quoted list price on the manufacturer page.
6. Power consumption anchors: quadmeup.com — *How much power a flight controller consumes* (measured: F1 44 mA, F3 55 mA, F4 93 mA). `[M]`
7. dronehitech.com — *How many amps a flight controller and receiver draw* (measured: FC 100 mA, RX 100 mA). `[M]`
8. uavmodel.com — FPV GPS module comparison BN-220/BN-880/M10 (current draw 35/45/25 mA). `[M]`
9. oscarliang.com — F1/F3/F4 flight-controller comparison (F405/F411 distinction, flash/RAM notes). `[M]`
10. inavfixedwinggroup.com — *Servos for INAV* (servo classes for fixed-wing INAV, digital vs analog). `[M]`
11. ExpressLRS docs — ELRS receiver wiring/power (EP1 HM2400). `[M]`

**Confidence:** MCU/IMU/baro/UART/PWM/BEC/dimensions are `[M]` (manufacturer
specs). The compatibility matrix, footprint summary and power budget are `[D]`.
Consumption values are `[M]` where measured (FC/RX/GPS) and `[E]` otherwise;
prices and the popularity rank are `[E]`/`[I]`. The single most valuable
verification is measuring a real board (mass, footprint, current) with the batch
the builder actually buys.

