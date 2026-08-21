# I-33 — MP-04 propulsion procurement and hardware-characterisation campaign

**Status:** executable catalog screen complete; procurement and H01–H22 physical evidence
open  
**Evidence date:** 2026-08-21  
**Feeds:** M1, MP-04, MP-05, D2, E2, MP-06 mass skeleton and future propulsion ADR  
**Calculation owners:** `hardware_candidate_trade.py`, `hardware_measurements.py`,
`generate_hardware_dummies.py`, `propulsion_match.py`

## 1. Question and authority boundary

MP-03 established a complete candidate equipment manifest but intentionally left the motor,
ESC and installation measurements open. This thread converts that open class into a small,
buyable and testable set. It does **not** select a flight powertrain and it does not close M1.

The selection order is:

1. screen present manufacturer data for voltage, Kv/RPM, envelope and mass;
2. buy or print physical articles that span the credible choices;
3. measure H01–H22 with traceable specimens and instruments;
4. map motor/ESC/propeller performance on the bench; and
5. select the flight chain only after E2 supplies aircraft drag and D2 supplies measured
   thrust, input power, RPM and temperature.

Catalog maximum power is a survival/thermal rating under the manufacturer's conditions. It
is not the aircraft operating point. Conversely, passing the present RPM arithmetic does not
prove launch thrust, controller startup, efficiency or cooling.

## 2. Correction C59: the P42A baseline is not a 22.2 V LiPo

The legacy `propulsion_match.py` reporting loop used 3.7 V/cell and printed 22.2 V for 6S.
The selected Molicel P42A data sheet specifies **3.6 V nominal and 4.2 V charge voltage**;
the correct pack values are therefore **21.6/25.2 V for 6S** and **28.8/33.6 V for 8S**.
The central calculation now imports those cell values from `battery_pack_layout.py`.

At the existing O1 comparator boundary:

- total battery power is 109.25 W at 95 km/h;
- the current reference hotel load is 11.54 W;
- motor/ESC battery input is 97.71 W;
- APC 8x8E speed is 8,484 rpm;
- shaft power is 83.1 W and torque is 0.0935 N·m; and
- nominal 6S motor/ESC bus current is 4.52 A.

These are a **maximum-power/drag boundary**, not a predicted cruise equilibrium. The exact
motor rating must also cover launch, climb, static loading and credible transient cases.

The corrected 80%-loaded planning points are **491 Kv for 6S** and **368 Kv for 8S**. The
accepted purchase-screen bands, declared as estimates, are 0.70–0.85 loaded/no-load RPM and
at least 5% explicit ESC voltage headroom above full pack charge. The latter is a procurement
policy for switching and regenerative transients, not a published component standard.

## 3. Motor shortlist

| Configuration | Candidate | Manufacturer data | O1 loaded/no-load ratio | Full-charge no-load RPM | Procurement use |
|---|---|---|---:|---:|---|
| 6S | **T-Motor MN3110 KV470** | 3–6S; 98 g with 600 mm leads; 28.5 mm axial body × 37.7 mm diameter; 15 A/330 W for 180 s | 0.836 | 11,844 | **Primary** lightweight article |
| 6S | **T-Motor MN4010 KV475** | 4–8S; 137 g with 600 mm leads; 30.5 × Ø44.7 mm; 30 A/540 W for 180 s | 0.827 | 11,970 | Robust alternate and mass/envelope upper article |
| 8S study | **T-Motor MN4010 KV370** | 4–8S; 137 g with leads; 30.5 × Ø44.7 mm; 20 A/450 W for 180 s | 0.796 | 12,432 | **Primary 8S study** article |
| 8S study | **T-Motor MN4012 KV400** | 4–8S; 155 g with leads; 32.5 × Ø44.7 mm; 25 A/750 W for 180 s | 0.736 | 13,440 | Robust 8S alternate |

All four no-load speeds remain below the APC Thin Electric RPM rule. That is only a blade
speed screen: the manufacturers tested these motors with substantially larger, lower-pitch
propellers, so none of their published thrust/temperature rows transfers to an APC 8x8.

The MN3110 is the first specimen because it removes 72 g from the former 170 g planning
motor allocation while retaining 3.38 times the O1 motor/ESC electrical-power boundary as a
catalog power ratio. The ratio is not a flight margin; the 8x8 map and launch case may expose
losses or heating that the catalog cannot predict.

The SunnySky X2820 V3 KV500 remains an acquisition fallback, not a controlled shortlist
row. Its current page identifies a 6S fixed-wing KV500 variant, but the accessible table mixes
variant tabs and did not expose a complete, unambiguous KV500 mass/resistance/current record.
Data printed for the KV860 variant shall not be copied onto KV500.

## 4. ESC shortlist and voltage decision

| Configuration | Candidate | Published limit | Full-pack explicit margin | Catalog envelope/mass | Disposition |
|---|---|---:|---:|---|---|
| 6S | **APD 80F3[X]v2** | 8S / 34.0 V; 80 A continuous; 140 A burst | **+8.8 V / 34.9%** | 44×22×12 mm; product page 20 g | **Primary** |
| 6S | Hobbywing FlyFun 60A V5 | categorical 3–6S; 60/80 A | no separate absolute maximum published | 69×35×18 mm; 73 g | PWM bench backup |
| 8S study | **APD 120F3[X]v2** | 12S / 50.4 V; 120/200 A | **+16.8 V / 50.0%** | 70×30×20 mm; 20 g | **Primary study** |
| 8S study | Hobbywing FlyFun 80A V5 | categorical 3–8S; 80/100 A | no separate absolute maximum published | 70×35×19 mm; 92 g | PWM bench backup |
| 6S | APD 40F3 | 25.5 V | **+0.3 V / 1.2%** | 30×16×5 mm; 3 g | **Reject for voltage headroom** |
| 8S study | APD 80F3[X]v2 | 34.0 V | **+0.4 V / 1.2%** | 44×22×12 mm; product page 20 g | **Reject for voltage headroom** |

The APD product page gives 20 g for the packaged 80F3[X]v2 while the general F-Series
documentation gives 10 g without cables. The manifest therefore carries **20 ±10 g** until
H06 weighs the actual board, capacitor, insulation and installed leads. The same principle
applies to the 600 mm T-Motor leads: catalog mass is retained now; H04/H05 and H22 separate
the installed motor from shortened wiring and connectors.

APD's continuous current claims require strong airflow, and its quick-start guide requires
the supplied input capacitor plus additional capacitance when the battery lead exceeds
12 cm. Salamandra shall therefore map ESC temperature at the actual duct flow and actual
lead length. High current rating does not remove that test.

## 5. Propeller articles

Buy the following APC Thin Electric articles from the same traceable source and weigh every
blade with its actual adapter:

| Article | Purpose | Catalog mass | APC RPM limit | Constraint |
|---|---|---:|---:|---|
| **8x8E** | retained datum and UIUC-correlated geometry | 15.0 g | 18,750 rpm | primary measured curve exists only for this geometry |
| **8x6E** | pitch/load sensitivity at the same disk diameter | 13.9 g | 18,750 rpm | cannot replace 8x8 without measured efficiency/mission result |
| **9x7.5E** | diameter/advance-ratio sensitivity | 17.9 g | 16,667 rpm | test only after physical pusher, ground and body clearance is proved |

Reverse-rotation `EP` versions also exist. Handedness is an installation decision tied to
motor rotation, adapter retention and torque response; the nomenclature does not make an
`EP` blade aerodynamically mandatory merely because the propeller sits behind the wing.

## 6. Flight-controller and logging regression matrix

INAV 9.1.0 is the current stable release found during this review. Release notes include
SDIO blocking fixes for problematic SD cards, which reinforces H21 rather than eliminating
it. INAV documents PWM and DShot ESC outputs and records battery, current, commands and
servo fields in blackbox. Those documented capabilities are necessary but not sufficient.

Before any propeller is fitted, the exact procured SpeedyBee board and exact stable firmware
build shall pass this regression matrix:

1. full-chip erase, configuration export and exact target/version record;
2. receiver/failsafe test while moving sticks rapidly through every corner;
3. elevons allocated and exercised through their complete commanded range in Manual, Acro
   and Angle, without enabling automatic trim in flight;
4. blackbox decode proving that both real elevon outputs—not only command inputs—appear and
   follow the physical channels;
5. at least a 30-minute complete-rate SD logging test with dropped-frame and decode-error
   counts reported;
6. pitot, GNSS/magnetometer, O4 display, CRSF, buzzer and current/voltage resources operated
   simultaneously;
7. PWM and DShot motor control tested separately with propeller removed; and
8. brownout/failsafe injection while servo transients and the O4 load are present.

This matrix deliberately responds to public reports on earlier SpeedyBee/INAV builds of
servo/CMS behavior, automatic-level-trim loss of pitch control and incomplete logging of
non-zero/one servo indices. An issue report is not proof that INAV 9.1.0 fails; it is a
specific regression test that Salamandra must retire on its own specimen.

## 7. Procurement sequence

### Tranche A — no energized propulsion

1. print the OpenSCAD battery, motor, ESC, FC, O4 and sensor envelope shells;
2. ballast each shell to its manifest mass and record the ballast station;
3. execute packaging, removal, camera FOV and 20 mm battery-travel trials; and
4. buy exact avionics/servos/sensors for H08–H21.

### Tranche B — 6S bench chain

1. MN3110 KV470 and MN4010 KV475;
2. APD 80F3[X]v2 plus its required capacitors/programming interface;
3. FlyFun 60A V5 only as a protocol/thermal fallback;
4. APC 8x8E, 8x6E and conditional 9x7.5E plus correct adapter hardware; and
5. guarded thrust stand, optical RPM, calibrated voltage/current/power, thermocouples and
   a controllable cooling-air source.

### Tranche C — 8S only after review

Do not buy the 8S propulsion chain merely to complete a table. Release this tranche only if
the 6S map or later aircraft trade identifies a quantified benefit capable of paying the
8S pack's 140 g penalty and separate power-module cost. If released, procure MN4010 KV370,
MN4012 KV400 and APD 120F3[X]v2.

Molicel warned in November 2025 that counterfeit P42A cells were circulating. Cells shall
come from Molicel or an authorized distributor with batch traceability. The first packaging
work should use inert dummies; a live flight pack requires a separate reviewed interconnect,
insulation, balancing, protection, charging and fire-response procedure.

## 8. Bench data grid and acceptance logic

For every motor/ESC/propeller combination, record at minimum:

- pack voltage, bus current and input power;
- RPM, thrust and torque or independently calibrated thrust-arm geometry;
- ESC command/protocol and motor direction;
- motor winding, bearing and case temperatures plus ESC component/case temperature;
- ambient temperature, pressure, test duration and cooling-air velocity;
- current-sensor/blackbox values on the same time base; and
- shutdown, restart, desynchronization, braking and fault behavior.

Use a guarded, remotely operated stand. Increase command in bounded steps, stop on the first
temperature, vibration, current, RPM or control anomaly, and never infer a continuous rating
from a brief sweep. The raw time series is the evidence; a chart or fitted efficiency surface
is a reduction artifact.

The final powertrain decision requires all of the following:

- measured operating points bracket the E2-required cruise thrust and the launch/climb case;
- total battery power, not motor power alone, is used for the efficiency objective;
- every propeller point respects measured vibration and the manufacturer's RPM limit;
- temperature reaches an accepted steady or explicitly bounded transient condition;
- the controller retains command and produces valid synchronized logs; and
- mass, envelope, connectors, service loops and cooling volumes are returned to H04–H07,
  H22 and then the MP-06 mass skeleton.

## 9. Reproducible artifacts

```bash
python3 calculations/hardware_candidate_trade.py
python3 calculations/hardware_candidate_trade.py --json
python3 calculations/hardware_measurements.py --check
python3 calculations/hardware_measurements.py --record <completed-record.json> --require-closure
python3 calculations/generate_hardware_dummies.py --check
```

The blank record contains every required H01–H22 output but has no fabricated values.
The OpenSCAD file selects one external-envelope shell through its `PART` variable and leaves
an open ballast cavity. Neither artifact closes a physical gate by existing.

## 10. Primary sources and transfer limits

- [Molicel INR-21700-P42A](https://www.molicel.com/product/inr-21700-p42a/) and
  [P42A v4 data sheet](https://www.molicel.com/wp-content/uploads/INR21700P42A-V4-80092.pdf):
  voltage, capacity, current, maximum cell dimensions and mass.
- [Molicel counterfeit-product statement](https://www.molicel.com/newsroom/molicel-counterfeit-certification-and-product-statement/):
  procurement traceability warning; it does not qualify any third-party pack design.
- T-Motor [MN3110](https://store.tmotor.com/product/mn3110-motor-navigator-type.html),
  [MN4010](https://store.tmotor.com/product/mn4010-kv580-motor-navigator-type.html) and
  [MN4012](https://store.tmotor.com/product/mn4012-kv480-motor-navigator-type.html):
  motor dimensions, mass with leads, voltage class, resistance, current and power.
- Advanced Power Drives [40F3](https://powerdrives.net/40f3),
  [80F3[X]v2](https://powerdrives.net/80f3),
  [120F3[X]v2](https://powerdrives.net/120f3) and
  [F-Series quick-start guide](https://docs.powerdrives.net/products/f_series/quick-start-guide):
  voltage/current limits, envelope, mass, protocol, cooling and capacitor instructions.
- Hobbywing [FlyFun V5 manufacturer manual](https://www.hobbywing.com/uploads/file/20220817/308d789701a8209b133476865a0ac754.pdf):
  cell count, current, mass, dimensions and fixed-wing control functions.
- APC [8x8E](https://www.apcprop.com/product/8x8e/),
  [8x6E](https://www.apcprop.com/product/8x6e/),
  [9x7.5E](https://www.apcprop.com/product/9x7-5e/) and
  [RPM limits](https://www.apcprop.com/wp-content/uploads/2022/03/APC-Propeller-RPM-Limits-rev5.pdf):
  product geometry/mass and the Thin Electric RPM rule.
- INAV [9.1.0 release](https://github.com/iNavFlight/inav/releases),
  [ESC/servo output documentation](https://github.com/iNavFlight/inav/blob/master/docs/ESC%20and%20servo%20outputs.md) and
  [blackbox documentation](https://github.com/iNavFlight/inav/blob/master/docs/Blackbox.md):
  current software capability; exact board behavior remains H08/H21 evidence.
- INAV issue reports [#11427](https://github.com/inavflight/inav/issues/11427),
  [#11320](https://github.com/iNavFlight/inav/issues/11320) and
  [#11546](https://github.com/inavflight/inav/issues/11546): regression-test inputs only,
  not generalized proof of present-firmware failure.

## 11. Decision

**Procure the two 6S motors and APD 80F3[X]v2 as the first propulsion bench set, with the
Hobbywing 60A V5 only as a fallback. Keep 8S study-only.** The former generic motor envelope
was too small for the credible candidates and its 170 g allocation was unnecessarily high;
the MP-03 manifest now carries the actual shortlist envelopes and catalog-mass band.

M1 remains open. Production fuselage and wing CAD remain held until a completed record,
bench map and synchronized measurement chain support MP-06.
