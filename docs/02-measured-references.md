# Measured references — primary data

`[M]` data obtained by direct measurement on reference articles. **This is the project's original contribution**: figures that were not published anywhere.

---

# 1. Peregrine 840 mm

3D-printed forward-swept flying wing, with support for DJI O4. **In service, flying.** The only verified comparable article of this configuration.

Sources: Bambu Studio project file `Peregrine_body_LWPLA.3mf` and the designer's datasheet. Measured 28 July 2026.

## 1.1 Published datasheet `[M]`

| Parameter | Value |
|---|---|
| Wingspan | 840 mm |
| Length | 500 mm |
| **Printed weight** | **315 g** (in LW-PLA) |
| **Takeoff weight** | **720 g** |
| **Stall speed** | **35 km/h** |
| Main carbon tube | Ø8 × 654 mm |
| Secondary tube | Ø4 × 194 mm |
| Suggested motor | 2208 kv2000 / 2207 kv1980 |
| Suggested propeller | 5146 three-blade or APC 6×4 |
| Battery | 4S LiPo or 18650 |
| FC | SpeedyBee F405 WING MINI (INAV 8.1) |
| Servos | 13 g digital |
| **Motor mount tilt** | **0.8° up** |
| Hinges | TPU printed, glued |

## 1.2 Designer's print profile `[M]`

```
filament_type          PLA-AERO (Bambu PLA Aero) — foamed LW-PLA
wall_loops             1
sparse_infill_density  4 %
sparse_infill_pattern  gyroid
filament_flow_ratio    0.60          ← foaming compensation
layer_height           0.20 mm
outer / inner wall     0.42 / 0.45 mm
nozzle / bed           247 °C / 55 °C
fan                    30 %
spiral_mode            off
```

**A single 0.42 mm perimeter and 4 % gyroid.** That is what flies.

## 1.3 Measured geometry `[M]`

Sections extracted from the inner panel:

| Relative station | Chord | Max thickness | **t/c** |
|---|---|---|---|
| 0.15 | 125.6 mm | 17.0 mm | **13.5 %** |
| 0.55 | 140.6 mm | 19.3 mm | **13.8 %** |
| 0.90 | 160.1 mm | 21.3 mm | **13.3 %** |

**t/c essentially constant at 13.5 %**, with taper in chord.

## 1.4 Reconstructed planform `[D]`

The file's objects fit: per wing half, inner panel 222.5 mm + outer 157.4 mm = 380 mm, plus ~118 mm of body → **840 mm**. Matches the datasheet.

| | Value |
|---|---|
| Estimated area | **0.140 m²** |
| Mean chord | 166 mm |
| **Aspect ratio** | **5.05** |
| **Wing loading (720 g)** | **51.6 g/dm²** |
| Structural fraction | 315/720 = **43.8 %** |

⚠️ The published stall speed (35 km/h) would imply C_Lmax ≈ 0.87 with this area — above the measured range for flat plates and reflexed airfoils at low Re (0.55–0.70, Ananda et al.). **The published figure is probably optimistic**; a realistic C_Lmax of 0.65 would give ~41 km/h.

## 1.5 Consequences for the project

1. **Independent convergence on t/c.** ADR-0027 set 13 % by a divergence argument and by housing the 21700 cell. The flying article sits at 13.5 %. Two paths, same result.

2. **One perimeter flies** — correction C15.

3. **Infill is part of the structure.** The designer specifies 4 % gyroid, not zero infill — correction C12.

4. **Trim datum `[M]`.** The recommended INAV adjustment of **"level flight pitch: 0 → 3°"** indicates the aircraft needs 3° of nose-up attitude for level flight: its built incidence falls 3° short. It is the only available datum on the real trim state of an in-service printed FSW wing. It feeds the **torsion window** of [I-02](../research/I-02-tailless-trim.md).

5. **Operational risk `[M]`.** The datasheet documents *porpoising* in RTH / Cruise / Loiter modes, with corrective adjustments. **Direct threat to the validity of E7** → gap G9.

6. **The Ø8 tube is a bending spar.** Torsional contribution ~1 N·m², versus ~70 from the skin. Confirms [ADR-0015](../decisions/ADR-0015-carbon-non-torsional.md).

## 1.6 Example printed in PETG — estimate `[E]`

An example printed in PETG with the geometry of an airfoil calculated for LW-PLA:

| | LW-PLA design | PETG example |
|---|---|---|
| Printed | 315 g | **~690 g** |
| AUW | 720 g | **~1095 g** |
| Wing loading | 51.6 g/dm² | **~78 g/dm²** |
| V_stall | 35 km/h (declared) | **~43 km/h** |
| G in shear | 0.35 GPa | **0.55 GPa** (×1.6) |

**It is stronger structural evidence than it appears:** more mass at the same geometry means more cruise speed and more dynamic pressure — and it still does not diverge.

## 1.7 Reproduction warning

⚠️ The profile carries `filament_flow_ratio = 0.60`, which compensates for LW-PLA foaming. **When switching to PETG it must be raised to ~0.95.** Otherwise 40 % less material is deposited: an actual wall of ~0.25 mm instead of 0.42 mm.

## 1.8 Transfer limits

- The available file is the **body**, not the outer panels. Full planform (c/4 sweep, taper, **twist**) is still pending.
- No data on the real maximum speed achieved.
- 840 mm scale versus 1300 mm: **trends transfer, magnitudes do not** without the scaling law of [I-05](../research/I-05-divergence-flutter.md).

---

# 2. Data pending measurement

| # | What | How |
|---|---|---|
| R1 | Peregrine panel planform: c/4 sweep, taper, **twist** | Wing files |
| R2 | Airfoil coordinates at several stations | Mesh slicing |
| R3 | StuntDouble family geometry | **Partial** — datasheet compared in [I-08](../research/I-08-stuntdouble-family.md); planform and twist of the STLs still to reconstruct |
| R4 | **Quasi-controlled planform comparison**: forward sweep vs *plank* | **Partial** — same author and comparable AR, but PW51/PW75 and propulsion confound the sweep effect |
