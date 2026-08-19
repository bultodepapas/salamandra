# I-19 — DJI O4 Air Unit / O4 Air Unit Pro — mechanical and electrical data

**Status:** Open — reference catalog · **Feeds:** guide §11 (FPV/video), CORE nose-pod/camera integration, O1 (Wh/km), avionics power budget (I-17)

> **This is a reference catalog, not a decision.** It reports the verified
> technical data of the DJI O4 Air Unit series so the
> builder can choose and the CAD designer can model the mounts. Every value is
> tagged `[M]` (DJI/manufacturer or measured review), `[D]` (derived) or `[E]`
> (estimate). Reproduction: `python3 calculations/fpv_power_budget.py`.

## 1. The series at a glance

DJI O4 Air Unit Series combines a separate camera module and transmission module
for recording and downlink. The Article #1 product is the lightweight **DJI O4
Air Unit**. Earlier project documents called it **“O4 Lite”**; that is a legacy
project/market alias, not DJI's product name. The audited products are:

| | **O4 Air Unit — Article #1** | **O4 Air Unit Pro** |
|---|---|---|
| Role | Lightweight | Premium / low-light |
| Sensor | 1/2" CMOS `[M]` | **1/1.3" CMOS** `[M]` |
| Recording | 4K/60 `[M]` | 4K/120, D-Log M `[M]` |
| Max TX power | **700 mW** `[M]` | **1200 mW** `[M]` |
| Air-unit mass, camera included | **8.2 g** `[M]` | **32.0 g** `[M]` |
| Required antenna mass | **1 × 0.75 g** `[M]` | **2 × 2.1 g** `[M]` |
| Installed bare mass | **8.95 g** `[D]` | **36.2 g** `[D]` |
| Input voltage | **3.7–13.2 V** `[M]` | 7.4–26.4 V `[M]` |

## 2. Full mechanical data sheet (for the CAD designer)

### 2.1 O4 Air Unit — Article #1 `[M]`/`[D]`

| Parameter | Value |
|---|---|
| VTX (transmission module) | **30 × 30 × 6 mm** (L×W×H), **5.1 g** |
| Camera module | **13.44 × 12.36 × 16.50 mm** (L×W×H), **3.1 g `[D]`** |
| Air-unit mass (camera included) | **8.2 g**; 9.2 g with optional lens mount |
| Antenna | one, **80 mm**, **0.75 g** |
| **Installed bare mass** | **8.95 g** = 8.2 + 0.75 `[D]` |
| Coaxial cable (VTX↔camera) | **50 mm** (do not force or sharply bend the base) |
| 3-in-1 cable (VTX↔FC) | **50 mm** |

### 2.2 O4 Air Unit Pro `[M]`

| Parameter | Value |
|---|---|
| VTX (transmission module) | **33.5 × 33.5 × 13 mm** |
| Camera module | **25.55 × 20 × 23.30 mm**, ≈ 16.4 g incl. cable |
| Air-unit mass (camera included) | **≈ 32 g** |
| Installed bare mass | **36.2 g** = 32.0 + 2 × 2.1 `[D]` |
| Coaxial cable | **130 mm** |
| 3-in-1 cable | 100 mm |
| Antenna | 2× coax u.fl, **110 mm**, 2.1 g each |
| Sensor / recording | 1/1.3" CMOS, **4K/120 fps**, D-Log M |
| VTX mounting | **20 × 20 and 25.5 × 25.5 mm, M2** |
| Camera mounting | 2× M2, **16 mm spacing** |
| Camera screws supplied | **M2 × 4** (4 pc) — for frames > 2 mm thick |
| BEC requirement | **≥ 13.5 W** (e.g. 9 V/1.5 A) per DJI |
| Heat | metal shell hot; **adhesive only on the side without fins**; DO NOT enclose |

### 2.3 Article #1 audit conclusion

The Python catalog stores the DJI body dimensions in manufacturer L×W×H order.
DJI publishes an 80 mm antenna length but no useful rigid-body envelope for it.
The aircraft layout therefore uses only two mass bodies: E18 camera (3.10 g) and
E19 VTX plus attached antenna (5.85 g). The antenna's 0.75 g is lumped at the VTX
station; its 80 mm length remains an assembly-routing note, not a third collision
body. This abstraction preserves the 8.95 g installed mass without false geometric
precision; the induced longitudinal-CG error is negligible at this design maturity.

### 2.4 DJI O3 Air Unit (legacy generation) — compatibility row `[M]`

The O3 Air Unit is the **previous generation** (2022, ecosystem: Goggles 2 / FPV Goggles
V2 / Goggles Integra). It is **not the project reference** (O4 series is), but it is the
system many builders already own — and the TBS Mojito (docs/02 §3) is marketed as
"O3 or O4" compatible. Data from DJI official support (dji.com/support/product/o3-air-unit,
accessed 2026-08-06):

| Parameter | Value |
|---|---|
| Transmission module | **32.5 × 30.5 × 14.5 mm** (L×W×H) |
| Camera module | **21.2 × 20 × 19.5 mm** (L×W×H), **≈ 8.3 g** incl. 115 mm coaxial cable |
| Air Unit mass (camera excluded / included) | ≈ **28 g / 36.4 g**; antenna ≈ 3 g |
| Coaxial cable | **115 mm** |
| Camera FOV | **155°** (12.7 mm equiv.) |
| Input voltage | **7.4–26.4 V** (2S–6S) |
| Camera screws | M2 × 4 (4 pc) supplied |
| TX power (EIRP) | FCC < 33 dBm · CE < 14 dBm |

**Compatibility check vs the Salamandra mounts (guide §7.6):** the O3 module
(32.5 × 30.5 × 14.5) fits the O4 VTX tray footprint (33.5 × 33.5) and the O3 camera
(21.2 × 20 × 19.5) fits inside the **O4 Pro** camera cavity
(25.55 × 20 × 23.30), not the smaller Article #1 O4 camera cavity. The O3
camera **hole spacing is not confirmed in the fetched sources** — verify against the
2× M2 / 16 mm mount before using it. Power: same voltage range as the O4 Pro (7.4–26.4 V);
measured current table pending (bench, D-series) — do not use the O4 Air Unit 5 V rail
assumption for the O3.

**Status:** O3 = accepted legacy option with declared verifications (camera hole
spacing, power draw); the reference and the mounts stay O4 series.

## 3. Mounting and installation details (DJI manual, `[M]`)

- **VTX:** install with the M2 screws; **M2 damping balls recommended** on the
  transmission-module holes. Do not overtighten (stripping).
- **Camera:** directional — distinguish the upward direction before fixing.
  Camera screws supplied fit frames **thicker than 2 mm**; otherwise use longer
  screws sized to the frame.
- **Coaxial cable:** never press or bend its base (image interruption/degradation).
- **Enclosure:** the VTX shell becomes **hot** when powered; it must **not** be
  installed in an enclosed area or in a position reachable by hand. Heat is
  dissipated to the frame/carbon plate (thermal pad).
- **Antennas:** keep **≥ 5 cm from the VTX module, camera, metal and carbon-fiber
  parts**; on the Pro, position the two antennas **at 90° to each other**; the
  antenna must extend **outside the frame** and be visible from front and rear.
- **Wiring (3-in-1 cable pinout) `[M]`:**

  | Wire | Color | Function |
  |---|---|---|
  | VCC | Red | Power — O4: 3.7–13.2 V · O4 Pro: 7.4–26.4 V |
  | GND | Black | Power ground |
  | Receiver | White | UART_RX → FC OSD TX (0–3.3 V) |
  | Transmitter | Grey | UART_TX → FC OSD RX (0–3.3 V) |
  | GND | Brown | Signal ground |
  | S.Bus | Yellow | DJI HDL → FC S.Bus (0–3.3 V) |

## 4. Electrical data

### 4.1 Input voltage, power levels, EIRP

| | O4 Air Unit — Article #1 | O4 Air Unit Pro |
|---|---|---|
| Input voltage | 3.7–13.2 V (1–3S) `[M]` | 7.4–26.4 V (2–6S) `[M]` |
| Selectable power | up to **700 mW** `[M]` | up to **1200 mW** `[M]` |
| EIRP 5.8 GHz (FCC) | < 30 dBm `[M]` | < 33 dBm `[M]` |
| EIRP 5.8 GHz (CE) | < 14 dBm `[M]` | < 14 dBm `[M]` |
| Min latency (racing, Goggles 3) | 20 ms `[M]` | 15 ms `[M]` |

### 4.2 Power consumption (measured, armed + recording)

**O4 Pro (measured at 9 V, Oscar Liang `[M]`):**

| Level | Current @ 9 V | Power `[D]` |
|---|---|---|
| 1200 mW | 1.16 A | **10.4 W** |
| 700 mW | 1.05 A | 9.5 W |
| 400 mW | 0.98 A | 8.8 W |
| 200 mW | 0.92 A | 8.3 W |
| 100 mW | 0.87 A | 7.8 W |
| 50 mW | 0.84 A | 7.6 W |
| 25 mW | 0.82 A | **7.4 W** |
| Disarmed (low power) | 0.33 A | 3.0 W |

Race mode: 25 mW/20 MHz 0.71 A; 1200 mW/40 MHz 1.02 A `[M]`. Power is roughly
constant vs input voltage (switched converter): at 25.2 V the 1200 mW draw is
≈ 0.42 A `[D]`.

**O4 Air Unit (measured at 5 V, Oscar Liang `[M]`):**

| State | Current @ 5 V | Power `[D]` |
|---|---|---|
| 700 mW (max) | 1.20 A | **6.0 W** |
| Disarmed (low power) | 0.60 A | 3.0 W |

## 5. Power budget and BEC margin for the Salamandra `[D]`

`python3 calculations/fpv_power_budget.py`. Reference pack: 6S1P P42A = 90.72 Wh
(I-16). O1 total battery power is 109.25 W. Two-servo avionics without FPV is 4.3875 W at
the regulated rails (I-17 §6); battery-side totals use 90 % BEC efficiency.

| Unit | Power range | Rail | I@max vs BEC | BEC margin |
|---|---|---|---|---|
| O4 Pro (1200 mW) | 7.4–10.4 W | 9 V (Matek 9V/2A) | 1.16 A / 2.0 A | 58 % |
| O4 Air Unit (700 mW) | 6.0 W | 5 V (Matek 5V/2A) | 1.20 A / 2.0 A | 60 % |

- **DJI requires ≥ 13.5 W BEC** for the O4 Pro (e.g. 9 V/1.5 A) `[M]` — the Matek
  F405/F765 **9 V/2 A** rail (18 W) satisfies it with headroom `[D]`.
- **Do not power the O4 Pro from the 5 V/2 A rail**: 10.4 W @ 5 V ≈ 2.1 A > 2 A `[D]`.
  The O4 Air Unit fits the 5 V rail (1.2 A, 60 %) or better a dedicated 9 V/1 A BEC.
- **Energy impact** `[D]`: 1 h at max power = **10.4 Wh (11.5 %)** for the Pro,
  or 6.0 Wh (6.6 %) for the Article #1 O4 Air Unit, of the 90.7 Wh pack.
- **Total electronics** `[D]`: avionics + FPV = **14.83 W rail / 16.48 W battery
  with O4 Pro**, and **10.39 W rail / 11.54 W battery with O4 Air Unit**. One hour is
  **18.2 % of the pack** (Pro) or **12.7 %** (Article #1) — material for the O1 efficiency
  claim; fly the
  lowest usable power level (25 mW indoors/near, max mW only when needed).

## 6. Integration notes for the Salamandra (nose pod / camera mount)

- **Camera mount:** the Article #1 camera is a **separate module from the VTX**
  joined by the 50 mm coaxial cable. Its body envelope is
  **13.44 × 12.36 × 16.50 mm L×W×H** and its derived mass is 3.1 g. The Pro
  camera is 25.55 × 20 × 23.30 mm and uses a 130 mm coaxial cable.
- **Article #1 installation policy `[D]`:** because aircraft forward is −x, E18 is
  fixed on y = 0 with its optical direction along −x. Its 13.44 mm body places the
  centre at x = −445.98 mm and the lens face at the forward cradle plane,
  x = −452.70 mm. E19 remains aft at x = −418.0 mm. The 3-D centre distance is
  45.99 mm versus the measured 50 mm coax length. This is a straight-line lower
  bound only; connector exits, bend radius and service loop remain an F2 CAD gate.
- **VTX placement:** Article #1 uses the **30 × 30 × 6 mm** transmission module.
  The Pro uses 33.5 × 33.5 × 13 mm. Both need **airflow** (the
  shell runs hot) and ≥ 5 cm antenna-to-structure clearance.
- **Antennas:** Article #1 carries one 80 mm antenna; the Pro carries two 110 mm
  antennas. Place Pro antennas **90° apart**, outside the
  printed shell, ≥ 5 cm from the VTX, camera, carbon and battery current path
  (matches guide §11 "GPS/mag out of the current path").
- **Power:** DJI requires >10 W BEC output for the O4 Air Unit and >13.5 W for
  the Pro. Use the 5 V/2 A rail only after closing the Article #1 peak-current
  margin; the Pro belongs on the 9 V/2 A rail.
  Keep the GPS/magnetometer and pitot wiring clear of the FPV power/UART runs.
- **Latency / band:** 5.1/5.8 GHz; CE power is limited to 14 dBm (25 mW) — range
  planning must use the local legal limit, not the FCC number.

## 7. Reproduction

```bash
python3 calculations/fpv_power_budget.py [input_V]
```

Self-validating: must print O4 Pro 1200 mW = 10.4 W, O4 Air Unit 6.0 W,
the 9 V rail utilization ≤ 58 %, and the total
electronics 14.83 W rail / 16.48 W battery / 18.2 % per hour (Pro) and
10.39 W rail / 11.54 W battery / 12.7 % (Article #1).

## 8. Sources

1. DJI — *DJI O4 Air Unit Series* specs (`dji.com/o4-air-unit/specs`). `[M]`

2. DJI — *DJI O4 Air Unit Series User Manual* v1.0 EN (PDF). `[M]`

3. DJI Store — *O4 Air Unit Pro Camera Module* (25.55×20×23.30 mm, 16.4 g, coax 130 mm, M2×4 screws). `[M]`

4. Oscar Liang — *DJI O4 Air Unit Pro* review (power/current table, mounting, 20×20 + 25.5×25.5). `[M]`

5. Oscar Liang — *DJI O4 Air Unit* review (power/current at 5 V and 700 mW cap). `[M]`

6. DJI — *O3 Air Unit support/specs page* (`dji.com/support/product/o3-air-unit`, accessed 2026-08-06). `[M]` — legacy generation (§2.4)
6. Confidence: DJI specs/manual `[M]`; measured current `[M]` (review); power/energy `[D]`; any remaining quantities `[E]`. The single most valuable verification is measuring the current draw of the actual unit with the chosen goggles/firmware on the bench.

**Designer checklist:** model the Article #1 camera and VTX manufacturer envelopes;
provide airflow; lump the attached antenna mass into E19; route its 80 mm length clear
of structure and the high-current path. The Pro option requires two antennas
at 90° and a ≥13.5 W BEC.
