# I-19 — DJI O4 FPV system: O4 / O4 Pro / O4 Lite — data sheets and electrical data

**Status:** Open — reference catalog · **Feeds:** guide §11 (FPV/video), CORE nose-pod/camera integration, O1 (Wh/km), avionics power budget (I-17)

> **This is a reference catalog, not a decision.** It reports the verified
> technical data of the DJI O4 Air Unit series (O4, O4 Pro, O4 Lite) so the
> builder can choose and the CAD designer can model the mounts. Every value is
> tagged `[M]` (DJI/manufacturer or measured review), `[D]` (derived) or `[E]`
> (estimate). Reproduction: `python3 calculations/fpv_power_budget.py`.

## 1. The series at a glance

DJI O4 Air Unit Series = camera + video transmitter (VTX) in one, recording and
downlink (no separate action camera needed). Three models share the same 5.8 GHz
O4/04 digital video ecosystem (Goggles 2/3/N3/Integra):

| | **O4 Air Unit** | **O4 Air Unit Pro** | **O4 Air Unit Lite** |
|---|---|---|---|
| Role | Standard | Premium (better low light) | Micro/lightweight |
| Sensor | 1/2" CMOS `[M]` | **1/1.3" CMOS** `[M]` | 1/2" CMOS `[M]` |
| Recording | 4K/60, D-Log M `[M]` | 4K/120, D-Log M `[M]` | 4K/60 (no 2.7K) `[M]` |
| Max TX power (selectable) | **700 mW** `[M]` | **1200 mW** `[M]` | **700 mW** `[M]` |
| Total mass | 32 g `[M]` | 33 g `[M]` | **8.2 g** (9.2 w/ mount) `[M]` |
| Input voltage | 7.4–26.4 V `[M]` | 7.4–26.4 V `[M]` | **3.7–13.2 V** `[M]` |

## 2. Full mechanical data sheet (for the CAD designer)

### 2.1 O4 Air Unit (standard) `[M]`

| Parameter | Value |
|---|---|
| VTX (transmission module) | **33.5 × 33.5 × 13 mm** |
| Camera module | **25.55 × 20 × 23.30 mm** (L×W×H) |
| Total mass (with camera) | **≈ 32 g** (15.6 g VTX without camera + ~16.4 g camera) |
| Coaxial cable (VTX↔camera) | **130 mm** (do not bend the base) |
| 3-in-1 cable (VTX↔FC) | **100 mm** |
| Antenna | 2× coax u.fl, **110 mm**, **2.1 g each** |
| Camera FOV / lens | **155°** / 12 mm equivalent |
| VTX mounting | **20 × 20 mm and 25.5 × 25.5 mm, M2** |
| Camera mounting | 2× M2, **16 mm hole spacing** (frames > 2 mm thick) |
| microSD | yes (recording) |

### 2.2 O4 Air Unit Pro `[M]`

| Parameter | Value |
|---|---|
| VTX (transmission module) | **33.5 × 33.5 × 13 mm** |
| Camera module | **25.55 × 20 × 23.30 mm**, ≈ 16.4 g incl. cable |
| Total mass (with camera) | **≈ 33 g** |
| Coaxial cable | **130 mm** |
| 3-in-1 cable | 100 mm |
| Antenna | 2× coax u.fl, **110 mm**, 2.1 g each |
| Sensor / recording | 1/1.3" CMOS, **4K/120 fps**, D-Log M |
| VTX mounting | **20 × 20 and 25.5 × 25.5 mm, M2** |
| Camera mounting | 2× M2, **16 mm spacing** |
| Camera screws supplied | **M2 × 4** (4 pc) — for frames > 2 mm thick |
| BEC requirement | **≥ 13.5 W** (e.g. 9 V/1.5 A) per DJI |
| Heat | metal shell hot; **adhesive only on the side without fins**; DO NOT enclose |

### 2.3 O4 Air Unit Lite `[M]`

| Parameter | Value |
|---|---|
| VTX (transmission module) | **30 × 30 × 6 mm** (30.5×30.5×5 per review) |
| Camera module | **13.44 × 12.36 × 16.50 mm** |
| Total mass | **8.2 g** (9.2 g with lens mount) |
| Coaxial cable | **50 mm** |
| 3-in-1 cable | **50 mm** |
| Antenna | single dipole, **80 mm**, **0.75 g** |
| VTX mounting | **25.5 × 25.5 mm, M2** (no 20×20) |
| Camera mounting | 2× M2, **16 mm spacing** |
| microSD | yes |

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
(21.2 × 20 × 19.5) fits inside the O4/Pro camera cavity (25.55 × 20 × 23.30). The O3
camera **hole spacing is not confirmed in the fetched sources** — verify against the
2× M2 / 16 mm mount before using it. Power: same voltage range as the O4 Pro (7.4–26.4 V);
measured current table pending (bench, D-series) — do not use the O4 Lite 5 V rail
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

| | O4 | O4 Pro | O4 Lite |
|---|---|---|---|
| Input voltage | 7.4–26.4 V (2–6S) | 7.4–26.4 V (2–6S) | 3.7–13.2 V (1–3S) `[M]` |
| Selectable power | 25·50·100·200·400·**700** mW | …·700·**1200** mW `[M]` | up to **700** mW `[M]` |
| EIRP 5.8 GHz (FCC) | < 33 dBm `[M]` | < 33 dBm `[M]` | < 30 dBm `[M]` |
| EIRP 5.8 GHz (CE) | < 14 dBm `[M]` | < 14 dBm `[M]` | < 14 dBm `[M]` |
| Auto power > 700 mW | — | adjusts 700↔1200 by environment `[M]` | — |
| Min latency (racing, Goggles 3) | 15 ms `[M]` | 15 ms `[M]` | 20 ms `[M]` |
| Low-power mode (disarmed) | auto `[M]` | auto `[M]` | auto `[M]` |

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

**O4 (standard):** same transmission module, power levels capped at 700 mW →
range **7.4–9.5 W** `[D]`.

**O4 Lite (measured at 5 V, Oscar Liang `[M]`):**

| State | Current @ 5 V | Power `[D]` |
|---|---|---|
| 700 mW (max) | 1.20 A | **6.0 W** |
| Disarmed (low power) | 0.60 A | 3.0 W |

## 5. Power budget and BEC margin for the Salamandra `[D]`

`python3 calculations/fpv_power_budget.py`. Reference pack: 6S1P P42A = 90.7 Wh
(I-16). Cruise ≈ 110 W (guide §10.1). Avionics without FPV ≈ 6.6 W (I-17 §6).

| Unit | Power range | Rail | I@max vs BEC | BEC margin |
|---|---|---|---|---|
| O4 Pro (1200 mW) | 7.4–10.4 W | 9 V (Matek 9V/2A) | 1.16 A / 2.0 A | 58 % |
| O4 (700 mW) | 7.4–9.5 W | 9 V | 1.05 A / 2.0 A | 52 % |
| O4 Lite (700 mW) | 6.0 W | 5 V (Matek 5V/2A) | 1.20 A / 2.0 A | 60 % |

- **DJI requires ≥ 13.5 W BEC** for the O4 Pro (e.g. 9 V/1.5 A) `[M]` — the Matek
  F405/F765 **9 V/2 A** rail (18 W) satisfies it with headroom `[D]`.
- **Do not power the O4 Pro from the 5 V/2 A rail**: 10.4 W @ 5 V ≈ 2.1 A > 2 A `[D]`.
  The O4 Lite fits the 5 V rail (1.2 A, 60 %) or better a dedicated 9 V/1 A BEC.
- **Energy impact** `[D]`: 1 h at max power = **10.4 Wh (11.5 %)** for the Pro,
  9.5 Wh (10.4 %) for the O4, 6.0 Wh (6.6 %) for the Lite, of the 90.7 Wh pack.
- **Total electronics** `[D]`: avionics + FPV = **17.0 W with O4 Pro (15.5 % of
  cruise)**, 12.6 W with O4 Lite (11.5 %). One flight-hour of electronics =
  **18.8 % of the pack** (Pro) — material for the O1 efficiency claim; fly the
  lowest usable power level (25 mW indoors/near, max mW only when needed).

## 6. Integration notes for the Salamandra (nose pod / camera mount)

- **Camera mount:** the O4 camera is a **separate module from the VTX** joined by
  the 130 mm coaxial cable — the camera sits at the nose, the VTX in the CORE
  body. Mounting: 2× M2 with **16 mm spacing**; design the nose pod for a
  25.55 × 20 × 23.30 mm camera (16.4 g) for O4/Pro, or 13.44 × 12.36 × 16.50 mm
  (3 g) for the Lite.
- **VTX placement:** 33.5 × 33.5 × 13 mm (O4/Pro) with **20 × 20 / 25.5 × 25.5 M2**
  mount; O4 Lite 30 × 30 × 6 mm with 25.5 × 25.5 only. Needs **airflow** (the
  shell runs hot) and ≥ 5 cm antenna-to-structure clearance.
- **Antennas:** the Pro carries two — place them **90° apart**, outside the
  printed shell, ≥ 5 cm from the VTX, camera, carbon and battery current path
  (matches guide §11 "GPS/mag out of the current path").
- **Power:** the O4/Pro can be fed from the Matek 9 V/2 A BEC (DJI min 13.5 W).
  Keep the GPS/magnetometer and pitot wiring clear of the FPV power/UART runs.
- **Latency / band:** 5.1/5.8 GHz; CE power is limited to 14 dBm (25 mW) — range
  planning must use the local legal limit, not the FCC number.

## 7. Reproduction

```bash
python3 calculations/fpv_power_budget.py [input_V]
```

Self-validating: must print O4 Pro 1200 mW = 10.4 W, O4 standard max 9.5 W
(700 mW cap), O4 Lite 6.0 W, the 9 V rail utilization ≤ 58 %, and the total
electronics 17.0 W / 18.8 % per flight-hour (Pro) and 12.6 W / 13.9 % (Lite).

## 8. Sources

1. DJI — *DJI O4 Air Unit Series* specs (`dji.com/o4-air-unit/specs`). `[M]`

2. DJI — *DJI O4 Air Unit Series User Manual* v1.0 EN (PDF). `[M]`

3. DJI Store — *O4 Air Unit Pro Camera Module* (25.55×20×23.30 mm, 16.4 g, coax 130 mm, M2×4 screws). `[M]`

4. Oscar Liang — *DJI O4 Air Unit Pro* review (power/current table, mounting, 20×20 + 25.5×25.5). `[M]`

5. Oscar Liang — *DJI O4 Air Unit Lite* review (power/current at 5 V, dims, 700 mW cap). `[M]`

6. DJI — *O3 Air Unit support/specs page* (`dji.com/support/product/o3-air-unit`, accessed 2026-08-06). `[M]` — legacy generation (§2.4)
6. Confidence: DJI specs/manual `[M]`; measured current `[M]` (review); power/energy `[D]`; any remaining quantities `[E]`. The single most valuable verification is measuring the current draw of the actual unit with the chosen goggles/firmware on the bench.

**Designer checklist:** model camera mount (M2, 16 mm) in the nose pod; VTX tray
(20×20/25.5×25.5 M2) with airflow; 2× antenna at 90° outside the shell; power via
9 V/2 A BEC (≥ 13.5 W); keep 5 cm separation from structure and current path.
