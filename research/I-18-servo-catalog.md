# I-18 — Servos for the elevons: popular models, technical data sheets

**Status:** Open — reference catalog · **Feeds:** guide §5.3 (elevon control), §7.5 (actuation), ADR-0025 (mass balancing), ADR-0026 (single actuation / no freeplay), PANEL servo bays

> **Correction C30 (2026-08-17):** the former N·m conversion displayed kgf·cm
> magnitudes with a g·cm label, a factor-1000 unit error, and then double-counted the
> benefit of two servos. The SI calculation and physical pass verdict remain; the
> corrected values and factored margins are below and in `servo_torque.py` revision 2.

> **This is a reference catalog, not a decision.** It reports the verified
> technical data and current prices of the most common servos used on
> **3D-printed FPV flying wings of the Salamandra class** (1.1–1.6 m, elevon
> control) so the builder can choose. Every servo listed is a real, purchasable
> product. The hinge-moment estimate and the margin comparison are **facts for the
> designer**, not rulings — a servo that "misses" a target is still usable if the
> builder accepts the consequence (e.g. extra mass, more play, less stiffness).

## 1. Scope and what the aircraft demands

The reference aircraft now uses **2 digital servos** (one per elevon) on **390 mm
elevons** (30–90 % half-span, 0.28 c, hinge at 0.72 c). ADR-0026 was corrected on
2026-08-18 after the former dual-actuation flutter credit was found unverified.
The constraints that matter for servo choice come from the ADRs:

| Requirement | Source | Note |
|---|---|---|
| **Digital** | ADR-0025 | Digital required for high holding stiffness; "static torque matters less than stiffness" |
| **Zero freeplay** in linkage | ADR-0026 | Freeplay is the #1 cause of limit-cycle flutter in models |
| **High holding stiffness** | ADR-0025 | More important than static torque |
| **Mass ≈ 15 g/servo** | guide §7.5 / justification | Budget is ~30 g total for 2 servos (`[E]`, class-typical) |
| V_NE design 180 km/h | guide §4 | Hinge moment estimated at 180 km/h |

The servo torque requirement (hinge moment) is quantified in `calculations/servo_torque.py` — see §2.

## 2. How much torque is actually needed (the hinge moment)

Reproducible: `python3 calculations/servo_torque.py`. Hinge-moment model (common
practice): `Mh = 0.5 · ρ · V² · S_control · c_control · Ch`; with one actuator per
elevon the complete hinge moment is carried by that servo (ADR-0026). Geometry from the guide §5.3/§7.5; `Ch`
(elevon hinge-moment coefficient) taken over the practical range 0.01–0.05 `[E]`.

| Quantity | Value | Basis |
|---|---|---|
| Root / tip chord | 289 / 145 mm | `[D]` from B=1.3 m, S=0.282 m², taper 0.5 |
| Elevon: mean chord / span | 57 mm / 390 mm | `[D]` |
| Control area S_control (each elevon) | ≈ 221 cm² | `[D]` |
| Design speed V | 180 km/h (50 m/s) | `[D]` (guide design 180) |
| **Hinge moment per elevon** | **19–96 mN·m** (Ch 0.01–0.05) | `[D]`+`[E]` |
| **Per servo (one complete elevon)** | **19–96 mN·m (0.20–0.98 kgf·cm)** | `[D]`+`[E]` |

> **Fact for the designer:** even the most modest catalog servo below
> (MG90S ≈ 1.8 kgf·cm) has **1.84× ideal margin** on the worst per-servo
> hinge-moment case. With a 1.5 safety factor and 80 % linkage efficiency, the
> required catalog torque is 1.834 kgf·cm; the Article #1 Corona DS-939MG at
> 2.5 kgf·cm has **1.36× factored margin at 180 km/h** and about 4.0× at the
> initial 105 km/h limit. **Static torque passes but is no longer a large-margin item**;
> constraint** — mass, holding stiffness, reliability, deadband and price dominate
> the choice. This is exactly why ADR-0025 emphasises stiffness over torque.

### 2.1 Model validation against published methods `[D]`

The hinge-moment model used here (`Mh = 0.5·ρ·V²·S·c·Ch`) is the same non
-dimensional form published by independent sources:

- **Basic Air Data** (basicairdata.eu, XFOIL-based elevator-hinge-moment sizing for
  RC models) defines exactly `C_He ≡ H_e / (0.5·ρ·V²·S_e·c̄_e)` — the model of
  `servo_torque.py` — and notes that control-surface sizing is *"not a critical
  issue"* for typical RC servos. `[M]`
- **FliteTest forum** (Ben Harber *Control Surface Torque Maths*) gives an
  equivalent force-and-moment spreadsheet; a stability-and-control engineer
  cross-checked it against **AVL** and confirmed the approach (flagging only a
  sin-projection detail in the surface-area transform). `[I]`
- **NASA NTRS 19780023100** and **Aerade ARC R&M 3485** document the same
  hinge-moment-derivative method for full-scale ailerons/elevators; the published
  derivative values fall in the `Ch` 0.01–0.05 band used here. `[M]`

No published source disputes the conclusion of §2: the aerodynamic hinge moment of
a ~0.28 c elevon on this class of wing is approximately 0.98 kgf·cm per elevon at
the conservative Ch endpoint, within the capability of two digital micro servos.

## 3. Servo catalog (verified data sheets)

Dimensions L×W×H mm. Torque quoted at the stated supply voltage. Prices are
street/store prices at the survey date (2026-08); `[M]` = list/manufacturer price,
`[E]` = store estimate.

### 3.1 Summary table

| # | Servo | Type | Torque (kg·cm) | Speed (s/60°) | Mass (g) | Dims (mm) | Gear | V op (V) | Price | Basis |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **TBS Mojito servo** (reference a/c) | Digital | 3.2 @ 6 V | 0.24–0.26 | 19 | 30×13.25×28 | metal | 4.8–6 | €20.6 / $23.7 `[M]` | `[M]` |
| 2 | **TowerPro MG90S** | Digital | 1.8 @4.8 / 2.2 @6 | 0.10 / 0.08 | 13.4 | 22.8×12.2×28.5 | metal | 4.8–6.6 | US$2.5–5 `[M]` | `[M]` |
| 3 | **Emax ES09MD (HV)** | Digital | 2.3 @4.8 / 2.6 @6 | 0.10 / 0.08 | 13.5–14.8 | 23×12×24.5 | metal, dual bearing | 5–8.4 (HV) | US$12.5–18 `[M]` | `[M]` |
| 4 | **Corona DS-939MG** | Digital | 2.5 @4.8 / 2.7 @6 | 0.14 / 0.13 | 12.5 | 22.5×11.5×24.6 | metal, ball bearing | 4.8–6 | US$12.5 `[M]` | `[M]` |
| 5 | **Hitec HS-5055MG** | Digital | 1.3–1.6 | 0.14 @6 | 9.5 | 22.6×11.4×22.6 | metal | 4.8–6 | — | `[M]` |
| 6 | **Savox SH-0255MG+** | Digital | 3.1 @4.8 / 3.9 @6 | 0.16 / 0.13 | 15.8 | 22.8×12×29.4 | metal | 4.8–6 | — | `[M]` |
| 7 | **KST DS115MG** | Digital | 3.0–3.2 @6 | 0.06 | 20–21 | 30×10×35 | metal | 4.5–6 | — | `[M]` |
| 8 | **MKS DS92A+** | Digital | 2.95 @6 | 0.058–0.070 | 17.4 | 23×12×27.25 | Ti (coreless) | 4.8–6 | — | `[M]` |
| 9 | **JX PDI-1181MG** | Digital | 3.0 @4.8 / 3.6 @6 | — | 17.5–18 | — | metal (coreless) | 4.8–6 | — | `[M]` |

### 3.2 Notes per model (from sources in §8)

- **TBS Mojito servo** — the servo shipped for the market-reference aircraft
  (guide §4). 3.2 kg·cm at 6 V, ≤0.26 s/60°, 19 g, 4.8–6 V, stall current
  specified at 4.8 V. The Mojito kit offers **optional airbrake servos** (brake for
  landings); Mojito owners also run **KST X10 servo bays** (RCG thread) as a
  drop-in alternative — evidence that the 19 g / 3 kg·cm class is the ecosystem
  norm for this exact airframe.
- **TowerPro MG90S** — the archetypal budget 9 g micro. **Digital** (per TowerPro
  and TowerPro-spec retailers), metal gear, 1.8–2.2 kg·cm, 13.4 g. Widely used on
  wings as the cheapest usable elevon servo. Note: budget deadband/quality
  variation between batches is common.
- **Emax ES09MD (HV)** — 13.5–14.8 g digital metal-gear, dual-bearing, 2.3–2.6
  kg·cm, and a **high-voltage (up to 8.4 V)** variant; commonly cited on fixed-wing
  builds. $12.5–18.
- **Corona DS-939MG** — 12.5 g digital metal-gear, 2.5–2.7 kg·cm, ball bearing,
  ≤3 µs deadband, 200–240 mA running current; a long-time FPV-wing budget staple.
- **Hitec HS-5055MG** — premium-brand **economy** digital feather (9.5 g), 1.3–1.6
  kg·cm. Lower torque than the rest; lightweight if the builder is mass-limited.
- **Savox SH-0255MG+** — 15.8 g digital metal-gear, 3.1–3.9 kg·cm, soft-start and
  Sanwa SSR protocol support; a step up in torque/stiffness for ~same mass.
- **KST DS115MG** — 20–21 g digital metal-gear, 3.0–3.2 kg·cm, 0.06 s/60°; fast and
  strong, but **above the 15 g/servo mass budget** — must be traded against the
  mass-balance allowance (ADR-0025).
- **MKS DS92A+** — 17.4 g coreless, **titanium-gear** digital, 2.95 kg·cm, 0.058 s
  (6 V); premium stiffness/low-play, helicopter-origin, also above the mass budget.
- **JX PDI-1181MG** — 17.5–18 g coreless digital metal-gear, 3.0–3.6 kg·cm; budget
  high-torque coreless micro, also above the 15 g budget.

### 3.3 Size envelope for the CORE/servo bay

| Statistic | Length × Width × Height (mm) | Mass (g) |
|---|---|---|
| **Minimum** (HS-5055MG / MG90S) | ~23 × 11–12 × 22.6–28.5 | 9.5 |
| **Median of surveyed** | ~23 × 12 × 26–29 | 15.8 |
| **Maximum** (KST DS115MG) | 30 × 10 × 35 | 21 |
| **Recommended servo cavity** (largest + clearance) | ~34 × 16 × 39 | — |

A cavity sized to the **largest (KST 30 × 10 × 35 mm)** plus ~4 mm per axis
accepts **every servo in this catalog**; the two axis layouts are all ~11–12 mm
wide (standard mini-servo width), so one pocket width fits all listed servos.

## 4. Comparison vs the aircraft constraints (factual)

| Servo | Meets 15 g/servo? | Digital | Meets 1.834 kgf·cm factored demand @ 180 km/h | Price class |
|---|---|---|---|---|
| TBS Mojito (reference) | no (19 g) | ✓ | ✓ (≥3.2×) | ~€20 |
| TowerPro MG90S | ✓ (13.4 g) | ✓ | No at 4.8 V (1.8); yes nominally at 6 V (2.2) | US$2.5–5 |
| Emax ES09MD | ✓ (13.5–14.8 g) | ✓ | ✓ | US$12.5–18 |
| Corona DS-939MG | ✓ (12.5 g) | ✓ | ✓ | US$12.5 |
| Hitec HS-5055MG | ✓ (9.5 g) | ✓ | 2.7–3.3× ideal, voltage-dependent | — |
| Savox SH-0255MG+ | ✓ (15.8 g) | ✓ | ✓ | — |
| KST DS115MG | no (20–21 g) | ✓ | ✓ | — |
| MKS DS92A+ | no (17.4 g) | ✓ | ✓ | — |
| JX PDI-1181MG | no (17.5–18 g) | ✓ | ✓ | — |

> Interpretation is left to the designer. The **mass budget is the discriminating
> column**: the digital-metal-gear 12–15 g class (Emax ES09MD, Corona DS-939MG,
> TowerPro MG90S, Savox SH-0255MG+) fits the ~60 g total budget; the 17–21 g class
> (TBS, KST, MKS, JX) exceeds it unless the builder accepts a heavier wing or
> re-allocates the balance allowance (ADR-0025).

## 5. Current draw vs the FC servo BEC

The static-torque analysis (§2) says the load is small; the *power* question is
separate and answered by **measured** digital-servo current data, not estimates:

| Measurement | Value | Source |
|---|---|---|
| Digital micro servo, holding vs high torque | **avg 0.3 A, peak 5 A** | Model Aviation, current-probe `[M]` |
| Same, very aggressive torque | avg 0.5 A, peak 5 A | `[M]` |
| Same, repeated reversals (worst case) | **avg 1.3 A, peak 9.3 A** | `[M]` |
| Dual servos on one surface, no-buzz setup | **up to 180 mA/servo static no-load** vs ~30 mA nominal idle | Model Aviation, servo balancing `[M]` |
| 4 micro servos, max simultaneous load | **2.78 A ≈ 700 mA/servo** | bench measurement (YouTube) `[M]` |
| Full-size high-end digital (JR8717-class) | 3–5 A under heavy load | HeliFreak `[I]` |

Reading: **typical flight load for 4 elevon servos ≈ 1.2–2.8 A** with
**sub-millisecond current spikes of 5–9 A** when several servos reverse together
`[M]`/`[D]`. Every INAV board in the companion catalog I-17 carries a **servo BEC
of ≥ 4.5 A** (SpeedyBee F405 WING 4.5 A / 5.5 A pk; Matek F405/F722/F765 Vx 5–8 A),
so the *average* is comfortably covered. Two power caveats for the designer
(Model Aviation, `[M]`):

1. **Peak alignment is the risk:** when all servos reverse in unison, their pulses
   can align; a tired battery or high-resistance wiring can then brown-out the FC
   mid-flight. Capacitance near the servos (or a capacitor at the receiver)
   shaves the peaks.
2. **Dual-actuation balancing (ADR-0026) must be current-measured:** two servos
   fighting each other can draw ~150 mA *extra* per servo with no buzz if the
   builder uses the "silence" rule — telemetry/current probe recommended, not just
   listening.

## 6. Supplementary research — 10 additional investigations

Ten further Firecrawl searches/scrapes (2026-08-05) on servo topics adjacent to the
catalog, with the facts each produced. Sources numbered per §7.

| # | Investigation | Key findings | Source(s) |
|---|---|---|---|
| S1 | **How servo torque is measured / stiffness test method** | Torque is measured as force × distance (kg·cm / oz·in). Stiffness is measured statically: apply known load to the horn, measure deflection. An open-source **backlash test stand** (PMC, 2025) applies repeatable loads to a servo lever and measures displacement — a directly applicable method to characterize the freeplay that ADR-0026 forbids | RCGroups, hlt-cnc, PMC `[M]` |
| S2 | **Deadband specifications** | Digital servos have low deadband; the cheap class rarely publishes it. Test method: set trim step to 1 µs and find the first step that moves the output. Published micro-digital deadbands in the low-µs class (Corona DS-939MG ≤ 3 µs); Spektrum lists "low deadband" as a digital-servo differentiator | RCGroups, Spektrum `[M]` |
| S3 | **ES09MD vs DS939 vs MG90S — comparative** | Independent test (YouTube *Servo Comparison*): **EMAX servos recommended overall**; **MG90S was fastest but jittery at 6 V**; **Corona DS939HV "a total let down"**. RCGroups alert: **the Emax ES09MD, sold as metal-gear, contains one plastic gear in the train** — verify on the batch received. Eclipson-recommended MG90S: users report losing servos during setup | YouTube, RCGroups, FB `[I]` |
| S4 | **Hinge-moment / servo sizing methods** | Same model as §2.1 (basicairdata XFOIL, FliteTest spreadsheet cross-checked vs AVL, NASA NTRS, Aerade flight data). Consensus: for RC surfaces the servo sizing is not critical; mechanical/hinge design dominates | §7.15–18 `[M]` |
| S5 | **Digital-servo current & BEC** | See §5: measured avg 0.3–1.3 A, peak 5–9.3 A per servo class; capacitance near servos cuts peaks; 2 A BECs manage most small models | Model Aviation, FliteTest, HeliFreak `[M]`/`[I]` |
| S6 | **HV servos at 8.4 V (2S/6S compatibility)** | HV servos tolerate a direct 8.4 V supply; run at lower voltage they lose speed/torque. On a 6S airframe the servo rail is a BEC output, so HV capability is a headroom/availability factor, not a wiring requirement. HV claims (reduced glitching/spikes) are common but not independently measured here | RCGroups, rchelicopterfun, Reddit `[I]` |
| S7 | **Flying-wing elevon servo practice** | Ecosystem practice confirms the 9–19 g class: Dan Wing EPP uses **Hitec HS-85MG**; DW Hobby Rainbow V2 flies elevons on **Emax ES9051 (4.1 g digital mini)**; Eclipson airframes use **MG90S**. Elevon wiring is 2 channels + radio mixing | RCGroups, supermotoxl, FliteTest, FB `[I]` |
| S8 | **Motor/gear technology trade-offs** | Coreless (brushed, no iron core): faster/lower inertia than cored, **lower torque, wears out** (brushes). Brushless: longest life, most expensive. Metal gears survive loads; plastic/mixed trains are the common failure point (ES09MD S3; MG90S S9). For this application (4 small servos, budget) coreless/metal is a luxury, cored/metal is the norm | Hitec UK, Reddit, eurorc `[I]` |
| S9 | **MG90S reliability** | "**MG90S is not a reference servo anymore**": batch quality/consistency issues; **cannot assume genuine/all-metal until disassembled**; jitter reports at 6 V (S3); stripped gears and wire strain-relief breaks are the typical failure modes | FB, kpower, OpenRCForums, YouTube `[I]` |
| S10 | **Mounting in 3D-printed wings / horns** | Printable servo-mount + control-horn kits exist for the exact Corona DS-939MG (yeggi/Thingiverse ecosystem). Community practice: glue servo blocks to the inside of the top skin, horns on the control surface with clearance slots; flightory (FPV-printed-wing community) discusses horn attachment methods for printed surfaces | yeggi, Aloft, Flightory, Du-Bro `[I]` |

## 7. Popularity basis

Ranking/review reflects cross-referencing of: (a) the **TBS Mojito** ecosystem
(the market-reference 1300 mm wing, guide §4) — its bundled servo is 19 g/3.2 kg·cm
and its community uses **KST X10** bays; (b) repeated appearance in **FPV-wing
build guides** (SYNAPSE build uses "EXI digital metal gear 9g" — "any servo in this
size range with robust torque, decent speed, good reliability"; RCG; YouTube wing
builds); (c) forum/budget-servo consensus (Savox/Pro-Modeler recommended on RCG,
with Savox as the value pick). The 9–15 g **digital metal-gear micro** is the
de-facto class for elevons on 1.1–1.6 m printed FPV wings.

## 8. Sources

1. TBS — Mojito servo product page (rotorama.com, diyfpv.com): 19 g, 0.24–0.26 s/60°, 3.2 kg·cm, 30×13.25×28 mm, €20.6 / $23.7. `[M]`
2. TBS — Mojito kit product page (team-blacksheep.com): optional airbrake servos; electronics bundle. `[M]`
3. RCGroups — *New Product TBS Mojito* thread: **KST X10 servo bays**; 4025 motor builds. `[I]`
4. TowerPro — MG90S product page (towerpro.com.tw); TowerPro-spec retailers (readymaderc.com, ednc.com): 13.4 g, 22.8×12.2×28.5, 1.8/2.2 kg·cm, 0.10/0.08 s, digital, metal gear, US$2.5–5. `[M]`
5. Emax — ES09MD HV product page (emax-usa.com); retailers (readymaderc.com, alofthobbies.com, icare-icarus): 13.5–14.8 g, 23×12×24.5, 2.3/2.6 kg·cm, 5–8.4 V HV, dual bearing, US$12.5–18. `[M]`
6. Corona — DS-939MG (hobbyking.com, icare-icarus, servodatabase.com): 12.5 g, 2.5/2.7 kg·cm, 0.14/0.13 s, ≤3 µs deadband, 200/240 mA, 22.5×11.5×24.6, US$12.5. `[M]`
7. Hitec — HS-5055MG product page (hiteccs.com, hitecrcd.com): 9.5 g, 1.3–1.6 kg·cm, 0.14 s @6 V, digital metal gear, 4.8–6 V. `[M]`
8. Savox — SH-0255MG+ product page (savox-servo.com, teamsavox.com, servodatabase.com): 15.8 g, 3.1/3.9 kg·cm, 0.16/0.13 s, soft start. `[M]`
9. KST — DS115MG (snhobbies.com, himodel.com, kstservos.com): 20–21 g, 3.0–3.2 kg·cm, 0.06 s, 30×10×35. `[M]`
10. MKS — DS92A+ (amainhobbies.com, scaleflying.com): 17.4 g, 2.95 kg·cm, 0.058–0.070 s, titanium gear, coreless. `[M]`
11. JX — PDI-1181MG (rees52.com, aliexpress, amazon): 17.5–18 g, 3.0/3.6 kg·cm, coreless. `[M]`
12. SYNAPSE wing build (YouTube) — elevon servos: "EXI digital metal gear 9 g, or any servo in this size range with robust torque." `[I]`
13. RCGroups — budget-servo recommendation thread: Savox and Pro-Modeler as value/quality picks. `[I]`
14. Hinge-moment model and margins — `calculations/servo_torque.py`. `[D]`/`[E]`
15. Basic Air Data — *Elevator Hinge Moment* (basicairdata.eu): `C_He ≡ H_e/(0.5·ρ·V²·S_e·c̄_e)`, XFOIL-based RC servo sizing. `[M]`
16. FliteTest forum — *Calculating Hinge & Servo Torque* (Mid7night/Ben Harber): control-surface torque spreadsheet cross-checked vs AVL. `[I]`
17. NASA NTRS 19780023100 — *Control-Surface Hinge-Moment Calculations for a High-Aspect-Ratio Wing* (Perry III, 1978). `[M]`
18. Aerade ARC R&M 3485 — *Flight Measurements of the Elevator and Aileron Hinge-Moment Derivatives* (Rose, 1965). `[M]`
19. Model Aviation — *Digital Servos* (Buxton, 2017): current-probe measurements avg 0.3–1.3 A, peaks 5–9.3 A; capacitance mitigates peaks. `[M]`
20. Model Aviation — *Flight Control Servo Balancing* (Richardson, 2025): dual-servo no-buzz setup ≤180 mA/servo static vs ~30 mA idle. `[M]`
21. RCGroups — *Servo torque (How is it measured)*; *Servo Resolution/DeadBand Test* (1 µs trim-step method). `[M]`/`[I]`
22. YouTube — *Servo Comparison* (EMAX vs MG90S vs Corona DS939HV): EMAX recommended; MG90S fastest but jittery at 6 V; Corona disappointing. `[I]`
23. RCGroups — *Alert: Emax ES09MD — not all gears are metal* (one plastic gear in the train). `[I]`
24. Hitec UK — *Explainer: motor types* (coreless vs cored brushed vs brushless trade-offs). `[M]`
25. Community practice — Dan Wing EPP build (Hitec HS-85MG), DW Hobby Rainbow V2 (Emax ES9051), Eclipson (MG90S), MG90S quality thread, printable DS-939MG servo mount + horn kits (yeggi), Flightory horn-attachment thread. `[I]`

**Confidence:** servo specs and prices are `[M]` (manufacturer/datasheet/store).
The hinge-moment requirement is `[D]` (geometry) over an `[E]` range of `Ch`, with
the model form independently corroborated `[M]` (§2.1). The current-draw figures
in §5 are `[M]` (published oscilloscope/current-probe measurements). Mass budget
(30 g / 2 servos) is `[E]` class-typical. Community/practice findings (S3, S7, S9,
S10) are `[I]` — forum consensus, not primary data. The single most valuable
verification is **measuring a real servo** (mass, deadband, holding stiffness,
actual stall torque and current draw at the FC's BEC voltage) with the batch the
builder actually buys.
