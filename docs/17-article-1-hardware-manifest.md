# Article #1 candidate hardware and power manifest

**Revision 1.0** · 21 August 2026 · **MP-03 complete; Gate M1 remains open**

**Document role:** canonical pre-measurement equipment, configuration and electrical
interface for SALAMANDRA-6S-R, SALAMANDRA-6S-CLEAN and SALAMANDRA-8S-STUDY.

**Machine-readable owner:**
[`calculations/hardware_manifest.py`](../calculations/hardware_manifest.py). The tables
inside the generated block are checked byte-for-byte by the repository verification
suite. Change the Python owner first, then republish this document.

**Authorization:** this manifest authorizes procurement comparison, hard dummies,
electronics integration and bench fixtures. It does not release a bought-in component,
equipment station, battery bay, OML, production CAD or flight article. MP-04 replaces
catalog and estimated inputs with measurements; MP-05 closes the measurement chain.

---

## 1. MP-03 result

The first functional prototype remains **6S1P**. The candidate baseline is now explicit:

- Molicel P42A cells in a one-layer 6S1P pack, retaining both flat-narrow and
  flat-moderate envelope options for the M2 packaging trade;
- one centreline pusher motor in the 500–550 Kv / approximately 400 W or greater class,
  an APC Thin Electric 8x8 datum and a 6S, 30 A-minimum ESC class;
- the SpeedyBee F405 WING FC and its 6S PDB/current/BEC board as reference parts;
- two Corona DS-939MG elevon servos as reference parts, plus a bounded but unselected
  rudder-servo pocket only in 6S-R;
- the DJI O4 Air Unit, Matek M10Q-5883, Matek ASPD-4525, Happymodel EP1, buzzer and
  MicroSD logging chain; and
- a visible 72.38 g historical installation reserve that MP-04 must decompose instead of
  hiding it in an “avionics” lump.

The exact motor and ESC are deliberately **not named**. Existing evidence defines a
credible voltage/Kv/current/mass class but does not contain a measured motor/ESC/propeller
map. Naming a product now would add false precision and could bias the later propulsion
trade.

The 8S overlay is a **separate study architecture**: its own pack, 375–413 Kv starting
motor class, explicitly 8S-rated ESC and an 8S-qualified FC/PDB/BEC/current-logging
assembly. The SpeedyBee PDB is officially a 2–6S product and is not accepted at 8S merely
because the same page also prints a 36 V numerical input range.

### 1.1 Status vocabulary

| Status | Meaning |
|---|---|
| `REFERENCE-PART` | Named product used for the candidate ledger and procurement; actual batch still requires measurement and bench acceptance |
| `REFERENCE-CLASS` | Bounded capability/mass/envelope used for architecture work; exact product intentionally open |
| `RESERVED-ENVELOPE` | Packaging, mass or route allowance; not purchase authority and not necessarily one rigid body |
| `STUDY-CLASS` | 8S-only architecture input; neither interchangeable with 6S nor authorized for first flight |

No status above means `RELEASED-PART`. That status may be assigned only after the M1
physical exit evidence exists and the final equipment freeze at M7 confirms the actual
batch.

---

## 2. Configuration and power architecture

The low-voltage loads are the complete measurement boundary: FC, receiver, GPS/compass,
pitot, buzzer, blackbox, FPV and every installed servo. Propulsion power remains separate
at the ESC input, while total battery-terminal energy combines both branches.

```text
SALAMANDRA-6S-R / 6S-CLEAN

6S1P P42A pack (21.6 V nominal; 25.2 V full)
  +-- main-current path --> 6S ESC class --> 500-550 Kv motor class --> APC 8x8 datum
  `-- SpeedyBee PDB/current sensor
        +-- 5.2 V FC rail --> FC + RX + GPS/mag + pitot + buzzer + MicroSD
        +-- 5.0 V VTX rail --> DJI O4 transmission module/camera
        `-- 6.0 V servo rail --> two elevons [+ one reserved rudder servo in 6S-R]

SALAMANDRA-8S-STUDY

8S1P P42A pack (28.8 V nominal; 33.6 V full)
  +-- separate 8S ESC --> 375-413 Kv starting motor class --> remapped propeller candidates
  `-- unselected 8S-qualified PDB/BEC/current logger --> equivalent low-voltage loads
```

The rail table below compares the conservative design-continuous and brief peak currents
against installed 6S capacity or the minimum capacity demanded from the future 8S power
assembly. It does not claim that catalog current limits close heat, ripple, brownout or
simultaneous transient behavior; those are MP-04/MP-05 bench results.

<!-- BEGIN GENERATED: MP-03 hardware manifest · calculations/hardware_manifest.py · do not edit by hand -->

### Configuration totals

| Configuration | Installed rows | Candidate equipment mass | RSS input uncertainty | Reference hotel power | Design-continuous hotel power | Brief hotel peak |
|---|---:|---:|---:|---:|---:|---:|
| **6S-R** | 18 | 834.35 g | 44.19 g | 12.79 W | 15.75 W | 29.75 W |
| **6S-CLEAN** | 17 | 821.85 g | 44.12 g | 11.54 W | 13.75 W | 23.08 W |
| **8S-STUDY** | 16 | 991.55 g | 47.92 g | 11.54 W | 13.75 W | 23.08 W |

### Component manifest

| ID | Configuration | Status | Reference identity | Qty | Installed mass | Envelope option(s) | MP-04/05 closure |
|---|---|---|---|---:|---:|---|---|
| `pack_6s1p_p42a` | 6S-R, 6S-CLEAN | **REFERENCE-PART** | 6S1P Molicel INR-21700-P42A pack | 1 | 445.00 +/- 5.00 g [D]/[E] | flat-narrow: 223.2 x 44 x 22.6 mm [D]<br>flat-moderate: 142.8 x 70.8 x 22.6 mm [D] | MP-04 H01: build and measure pack, leads, connector sweep, mass centre and usable energy. |
| `pack_8s1p_p42a` | 8S-STUDY | **STUDY-CLASS** | 8S1P Molicel INR-21700-P42A study pack | 1 | 585.00 +/- 5.00 g [D]/[E] | flat-narrow: 293.4 x 44 x 22.6 mm [D]<br>flat-moderate: 186.2 x 70.8 x 22.6 mm [D] | MP-04 H02: build a hard dummy or pack and measure the complete 8S installation. |
| `propeller_8x8` | 6S-R, 6S-CLEAN, 8S-STUDY | **REFERENCE-PART** | APC Thin Electric 8x8 datum plus adapter | 1 | 25.00 +/- 3.00 g [M]/[E] | rotating-disk: 25.4 x 203.2 x 203.2 mm [M]/[E] | MP-04 H03: weigh blade/adapter and bench-map at least two credible propeller alternatives. |
| `motor_6s_class` | 6S-R, 6S-CLEAN | **REFERENCE-CLASS** | 28-class 500-550 Kv, approximately 400 W or greater | 1 | 170.00 +/- 30.00 g [E] | class-bound: 35 x 28 x 28 mm [E] | MP-04 H04: shortlist real motors, then measure mass, Kv, winding resistance, envelope and thermal map. |
| `motor_8s_class` | 8S-STUDY | **STUDY-CLASS** | 8S 375-413 Kv starting class, approximately 400 W or greater | 1 | 170.00 +/- 30.00 g [E] | class-bound: 35 x 28 x 28 mm [E] | MP-04 H05: select and bench an 8S motor candidate without exceeding propeller RPM or temperature limits. |
| `esc_6s_class` | 6S-R, 6S-CLEAN | **REFERENCE-CLASS** | 6S ESC, 30 A continuous minimum, telemetry preferred | 1 | 35.00 +/- 10.00 g [E] | class-bound: 60 x 30 x 15 mm [E] | MP-04 H06: select with the motor and measure efficiency, current, rpm, temperature and failure behavior. |
| `esc_8s_class` | 8S-STUDY | **STUDY-CLASS** | 8S ESC, 30 A continuous minimum, telemetry preferred | 1 | 45.00 +/- 15.00 g [E] | class-bound: 70 x 35 x 18 mm [E] | MP-04 H07: select and bench with the 8S motor, PDB/BEC and propeller. |
| `fc_6s` | 6S-R, 6S-CLEAN | **REFERENCE-PART** | SpeedyBee F405 WING FC board | 1 | 8.90 +/- 0.30 g [M] | body: 36.5 x 36.5 x 7 mm [M] | MP-04 H08: procure board, verify resources/firmware and measure mass/current/current-sensor calibration. |
| `pdb_6s` | 6S-R, 6S-CLEAN | **REFERENCE-PART** | SpeedyBee F405 WING PDB/current/BEC board | 1 | 11.40 +/- 0.50 g [M] | body-bound: 36.5 x 36.5 x 5 mm [M]/[E] | MP-04 H09: measure complete board stack, rail regulation, ripple, current calibration and thermal margin. |
| `fc_pdb_8s_class` | 8S-STUDY | **STUDY-CLASS** | 8S-qualified FC/PDB/BEC/current-logging assembly | 1 | 40.00 +/- 15.00 g [E] | station-bound: 64 x 45 x 21 mm [D]/[E] | MP-04 H10: select an 8S-rated logging/power assembly and bench every rail at 33.6 V. |
| `elevon_servos` | 6S-R, 6S-CLEAN, 8S-STUDY | **REFERENCE-PART** | Corona DS-939MG reference pair | 2 | 25.00 +/- 1.00 g [M] | body: 22.5 x 11.5 x 24.6 mm [M] | MP-04 H11: measure both servos for mass, travel, rate, deadband, backlash, stiffness, current and heat at 6 V. |
| `rudder_servo_reserve` | 6S-R | **RESERVED-ENVELOPE** | Digital metal-gear rudder servo, 15 g maximum class | 1 | 12.50 +/- 2.50 g [E] | reserved-pocket: 34 x 16 x 39 mm [D]/[E] | MP-04 H12/M5: replace the reserve with a selected actuator after rudder hinge-load and rate closure. |
| `o4_camera` | 6S-R, 6S-CLEAN, 8S-STUDY | **REFERENCE-PART** | DJI O4 Air Unit camera module | 1 | 3.10 +/- 0.30 g [D] | body: 13.44 x 12.36 x 16.5 mm [M] | MP-04 H13: measure camera/lens-mount mass, true lens datum, connector and FOV keep-out. |
| `o4_vtx_antenna` | 6S-R, 6S-CLEAN, 8S-STUDY | **REFERENCE-PART** | DJI O4 Air Unit transmission module plus antenna | 1 | 5.85 +/- 0.40 g [M]/[D] | vtx-body: 30 x 30 x 6 mm [M] | MP-04 H14: mock connector/coax/antenna routes and measure current/temperature at selected settings. |
| `gps_mag` | 6S-R, 6S-CLEAN, 8S-STUDY | **REFERENCE-PART** | Matek M10Q-5883 GNSS/magnetometer | 1 | 8.00 +/- 0.50 g [M] | body: 20 x 20 x 12.4 mm [M] | MP-04 H15: measure harness/current and run installed magnetic-interference tests. |
| `pitot_sensor` | 6S-R, 6S-CLEAN, 8S-STUDY | **REFERENCE-PART** | Matek ASPD-4525 differential-pressure board | 1 | 3.50 +/- 0.50 g [M] | board-bound: 30 x 20 x 10 mm [E] | MP-04 H16: measure board/harness envelope, leak rate, zero, scale and current. |
| `pitot_probe_tubing` | 6S-R, 6S-CLEAN, 8S-STUDY | **RESERVED-ENVELOPE** | Pitot probe, 400 mm tubing and fittings allowance | 1 | 5.00 +/- 3.00 g [E] | route-bound: 360 x 8 x 8 mm [E] | MP-04 H17: assemble and measure the real probe, fittings, tube route and installed mass. |
| `receiver` | 6S-R, 6S-CLEAN, 8S-STUDY | **REFERENCE-PART** | Happymodel EP1 2.4 GHz ELRS receiver | 1 | 0.42 +/- 0.10 g [M] | body: 10 x 10 x 3 mm [M] | MP-04 H18: procure, update firmware, measure current and perform range/failsafe tests. |
| `receiver_antenna` | 6S-R, 6S-CLEAN, 8S-STUDY | **RESERVED-ENVELOPE** | EP1 omnidirectional antenna installation allowance | 1 | 0.80 +/- 0.40 g [E] | route-bound: 90 x 4 x 4 mm [M]/[E] | MP-04 H19: measure chosen antenna/pigtail and validate installed RSSI/LQ. |
| `buzzer` | 6S-R, 6S-CLEAN, 8S-STUDY | **REFERENCE-CLASS** | 5 V self-driven buzzer class | 1 | 2.00 +/- 1.00 g [E] | class-bound: 15 x 15 x 10 mm [E] | MP-04 H20: select and measure part, current and sound function through the shell. |
| `blackbox_card` | 6S-R, 6S-CLEAN, 8S-STUDY | **REFERENCE-CLASS** | SDSC/SDHC MicroSD blackbox card | 1 | 0.50 +/- 0.50 g [E] | card: 15 x 11 x 1 mm [M] | MP-04 H21: select card and verify complete-rate logging without dropped samples. |
| `installation_reserve` | 6S-R, 6S-CLEAN, 8S-STUDY | **RESERVED-ENVELOPE** | Distributed avionics wiring/connectors/mounts reserve | 1 | 72.38 +/- 30.00 g [E] | distributed-allocation: 180 x 80 x 25 mm [E] | MP-04 H22: weigh every harness, connector, mount and service loop; retire this reserve row. |

### Low-voltage rail budget

| Configuration | Rail | Source | Voltage | Continuous load / capacity | Brief load / capacity | Status |
|---|---|---|---:|---:|---:|---|
| **6S-R** | `FC-5V` | `pdb_6s` | 5.2 V | 0.555 / 2.4 A | 0.555 / 3.0 A | REFERENCE-PART [M] |
| **6S-R** | `VTX-5V` | `pdb_6s` | 5.0 V | 1.200 / 1.8 A | 1.200 / 2.3 A | REFERENCE-PART [M] |
| **6S-R** | `SERVO-6V` | `pdb_6s` | 6.0 V | 0.900 / 4.5 A | 3.000 / 5.5 A | REFERENCE-PART [M] |
| **6S-CLEAN** | `FC-5V` | `pdb_6s` | 5.2 V | 0.555 / 2.4 A | 0.555 / 3.0 A | REFERENCE-PART [M] |
| **6S-CLEAN** | `VTX-5V` | `pdb_6s` | 5.0 V | 1.200 / 1.8 A | 1.200 / 2.3 A | REFERENCE-PART [M] |
| **6S-CLEAN** | `SERVO-6V` | `pdb_6s` | 6.0 V | 0.600 / 4.5 A | 2.000 / 5.5 A | REFERENCE-PART [M] |
| **8S-STUDY** | `FC-5V` | `fc_pdb_8s_class` | 5.2 V | 0.555 / 2.4 A | 0.555 / 3.0 A | STUDY-CLASS [E] minimum |
| **8S-STUDY** | `VTX-5V` | `fc_pdb_8s_class` | 5.0 V | 1.200 / 1.8 A | 1.200 / 2.3 A | STUDY-CLASS [E] minimum |
| **8S-STUDY** | `SERVO-6V` | `fc_pdb_8s_class` | 6.0 V | 0.600 / 4.5 A | 2.000 / 5.5 A | STUDY-CLASS [E] minimum |

<!-- END GENERATED: MP-03 hardware manifest -->

---

## 3. Interpretation of the totals

The configuration masses are **equipment-only**, not aircraft AUW. They include battery,
propulsion, actuation, avionics, FPV and the unresolved installation reserve; they exclude
the printed airframe, control surfaces, directional-module structure, carbon, adhesives
and general structural hardware. MP-06 will combine measured hardware with candidate
airframe allocations and solve CG/inertia.

The `+/-` value is an RSS propagation of declared input uncertainties, assuming different
rows are independent and repeated items from one batch are correlated. It is a planning
quantity, not a confidence interval. The 30 g uncertainty attached to the installation
reserve dominates the result and is itself evidence that MP-04 decomposition matters.

The power columns are battery-input estimates using a 0.90 conversion-efficiency
assumption:

- **reference** reproduces the existing two-elevon 11.54 W hotel-load model for CLEAN;
- **design continuous** uses the upper active-current bounds for avionics and servos; and
- **brief peak** substitutes the provisional simultaneous servo-stall current.

The peak is a BEC/brownout screen, not an energy-use state. The propulsion allocation at
any mission speed must be solved from measured drag and a motor/ESC/propeller map; it is
not inferred from the ESC's current rating.

---

## 4. MP-04 measurement order

The generated manifest assigns H01–H22 closure tasks. Execute them in dependency order:

1. **Physical configuration:** H01/H02 packs and H13/H14 O4 parts/dummies establish the
   longest optical, extraction and cable constraints.
2. **Power chain:** H04–H10 selects and benches the 6S motor/ESC and the separate 8S study
   chain while calibrating current and every BEC rail.
3. **Actuation:** H11/H12 characterizes the complete elevon batch and bounds the R-module
   servo without treating catalog torque as stiffness or freeplay evidence.
4. **Measurement chain:** H15–H21 closes GNSS/magnetic interference, airspeed plumbing,
   ELRS/failsafe, buzzer and complete-rate blackbox logging.
5. **Installation reconciliation:** H22 replaces the 72.38 g allocation with a line item
   for every wire, connector, mount, strain relief and service loop.

MP-04 is complete only when the machine-readable rows contain the measured batch values
and photographs/dimension records identify the hardware. MP-05 then proves that pitot,
current, voltage and blackbox data are synchronized and usable on an existing aircraft or
representative iron bird.

---

## 5. Primary evidence and transfer limits

- Molicel — [INR-21700-P42A product data](https://www.molicel.com/product/inr-21700-p42a/):
  3.6 V, 4.2 Ah, 45 A, 21.7 x 70.2 mm maximum and 70 g maximum per cell `[M]`.
- SpeedyBee — [F405 WING APP specification](https://www.speedybee.com/speedybee-f405-wing-app-fixed-wing-flight-controller/):
  FC/PDB masses, body dimensions, resources, rail capacities and the categorical 2–6S
  limit `[M]`. No 8S qualification is transferred.
- DJI — [O4 Air Unit specification](https://www.dji.com/o4-air-unit/specs): camera/VTX
  dimensions, masses, 50 mm coax, 80 mm antenna and input range `[M]`; actual Salamandra
  current and cooling remain bench measurements.
- Matek — [M10Q-5883](https://www.mateksys.com/?portfolio=m10q-5883) and
  [ASPD-4525](https://www.mateksys.com/?portfolio=aspd-4525): navigation and air-data
  electrical/body data `[M]`; installed magnetic and pneumatic accuracy do not transfer
  from catalog data.
- Happymodel — [EP1 receiver specification](https://www.happymodel.cn/index.php/2021/04/10/happymodel-2-4g-expresslrs-elrs-nano-series-receiver-module-pp-rx-ep1-rx-ep2-rx/):
  receiver body and mass `[M]`; airframe range/failsafe remain physical gates.
- Repository evidence: [I-16](../research/I-16-battery-pack-layout.md),
  [I-17](../research/I-17-inav-flight-controllers.md),
  [I-18](../research/I-18-servo-catalog.md),
  [I-19](../research/I-19-fpv-system-dji-o4.md),
  [I-32](../research/I-32-6s-8s-p42a-pack-and-aircraft-trade.md) and
  [ADR-0048](../decisions/ADR-0048-article-1-mission-and-configurations.md).

Reproduce and export the complete data structure with:

```bash
python3 calculations/hardware_manifest.py
python3 calculations/hardware_manifest.py --json
```
