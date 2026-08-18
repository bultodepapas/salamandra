# Objectives and requirements — Phase 0 specification

**Revision 1.3** · 17 August 2026 · **Phase 0 closed**
Defines **what is built and why**. No geometry line precedes this document.

This is an **open, community-driven, modular 3D-printed FPV aircraft platform**. The core
design principles are developed largely through **AI-assisted research**, while the final
aircraft and its 3D models are created collaboratively by humans and AI. The forward-swept
flying wing below is the **first, reference design**; the platform is intended to grow into
a family of airframes, parts and configurations contributed by the community (see §2.4).

---

# 1. The central tension, resolved

The initial analysis showed that **the TBS Mojito is not energy-efficient**: 0.74 Wh/(km·kg), the same as a USD 40 foam wing. Its achievement is sustaining that consumption at 2–3× the speed.

Therefore "efficient" and "Mojito-like" are only compatible if efficiency is sought **where the Mojito is leaving it on the table**:

| Source of improvement | Potential | Basis |
|---|---|---|
| **Propeller matching** (η 0.50 → 0.60) | **+20 %** | [I-03](../research/I-03-propulsion-chain.md) `[D]` |
| Surface finish and C_D0 | +5–8 % | `[E]` |
| Optimized aspect ratio and twist | +3–5 % | `[E]` |

**Target: ≤ 1.15 Wh/km.** An 18 % improvement justifiable **only with the propulsion chain**. It is falsifiable: measured with E2 and E3.

---

# 2. Objectives

## 2.1 Must-haves

| # | Objective | Acceptance criterion |
|---|---|---|
| **O1** | Demonstrated efficiency | ≤ 1.15 Wh/km at 95 km/h, measured with blackbox |
| **O2** | Flexible 4S–6S platform | The platform may host 4S and 6S power modules without changing the wing/CORE interface. Each module has its own matched motor and carrier; Article #1 is 6S1P only (ADR-0042) |
| **O3** | Printable on a 256 mm machine | Bambu P1S class. No active chamber. No exotic filament |
| **O4** | PETG as the single structural material | Price, availability, thermal tolerance, ease |
| **O5** | Easy to manufacture | ≤ 20 h of printing per wing half · ≤ 3 h of assembly · **no fiber lamination** |
| **O6** | Published rationale | Every figure with a confidence tag and a source |
| **O11** | Modularity | Standard center + interchangeable panels with a common NP |

## 2.2 Desirable

| # | Objective |
|---|---|
| O7 | Repairable by reprinting a segment |
| O8 | Structure cost < €60 against the USD 189.95 reference kit |
| O9 | Transportable — detachable wing halves, 700 mm case |
| O10 | Compatible with INAV and ArduPlane without firmware-dependent geometry |

## 2.3 Non-goals

- **Not a single fixed design.** This is a platform, not one aircraft. The reference
  design is a forward-swept flying wing, but the platform is not limited to it; future
  directions may include conventional fuselages, V-tails, and tractor or pusher layouts.
- **Not a speed-record aircraft.** The Eliminator covers that, same lineage, 360 km/h.
- **Not a thermal glider.** Pure endurance requires AR 8–12 and 25–35 g/dm², incompatible with PETG at this scale.
- **Not a first aircraft.** No tail, forward sweep, hand launch.
- **Not seeking minimum mass at any cost.** Torsional stiffness rules.
- **Not prescribing motor or battery.** See [ADR-0033](../decisions/ADR-0033-electronics-out.md).

## 2.4 Platform and community objectives

These are the objectives that define the *platform*, as opposed to the reference design:

| # | Objective | Criterion |
|---|---|---|
| **O12** | Open and free | Fully free to use, build and share; no paywall or locked files |
| **O13** | Community-driven | Contributions (PRs) with modifications, improvements and new variants are encouraged |
| **O14** | Modular and extensible | Replaceable wings; fuselage, wingtip, rudder and control-surface variants; entirely different configurations over time |
| **O15** | AI-assisted research, human-built parts | AI does aerodynamic/theoretical research and design exploration; the community creates the actual 3D parts (CAD/STL), experiments and manufacturing know-how |
| **O16** | Hardware archive | Central archive for adapters and mounts for FPV equipment, electronics, propulsion and related hardware |
| **O17** | Reciprocal licensing | Hardware/design under CERN-OHL-S-2.0; documentation under CC BY-SA 4.0 |

---

# 3. Requirements

## 3.1 Mission

| Requirement | Value | Confidence |
|---|---|---|
| Design range | 80 km with 20 % reserve | `[E]` |
| Extended target range | 100 km, contingent on E3 | `[E]` |
| Endurance | 60 min at minimum-power speed | `[E]` |
| Cruise speed | 90–105 km/h | Decided |
| Design V_NE | 180 km/h | Decided |
| **V_NE article #1** | **160 km/h** | Conservative until E7 |
| n_max / n_min | +6 / −3, later +9 | `[E]`, gust-dominated |
| **Stall speed** | **≤ 45 km/h** | See correction C16 |
| Required C_Lmax | ≥ 0.65 | `[D]` |

> **Correction C16.** The original requirement was ≤ 40 km/h, derived with AUW 1350 g (4S1P, 48 g/dm²). When the AUW rose to 1620 g (6S1P, 57 g/dm²) **the calculation was not re-done**. With C_Lmax 0.65 the real stall speed is **42.7 km/h**; reaching 40 would require C_Lmax 0.74, outside the realistic range (0.55–0.70, Ananda et al.).
>
> **Relaxed to ≤ 45 km/h**, justified by precedent: the Peregrine at 52 g/dm² and the Mojito at ~60 are hand-launched.

## 3.2 Requirements derived from modularity

See [ADR-0032](../decisions/ADR-0032-modularity.md) for the full development.

- **R-NP** — common family neutral point. **Arbitrary panels are not admitted.**
- **R-JOINT** — joint torsional stiffness ≥ 5× that of the adjacent section. Joint at 30 % of half-span, two pins.

## 3.3 R-CG — Article #1 balance and future battery modules

| Pack | Cells | Energy | Mass | AUW | Wing loading |
|---|---|---|---|---|---|
| **6S1P P42A (Article #1)** | 6 | **90.7 Wh** | **445 g** | **1583.5 g CLEAN** | **56.2 g/dm²** |

> **R-CG:** the Article #1 carrier shall hold CG within ±5 mm with the 6S1P pack. The
> current solution places it at x = −359.6 mm (band −377.4…−341.9). A 4S aircraft
> requires approximately 713 Kv rather than the 500–550 Kv 6S motor and therefore is a
> separate power module. The former requirement to interchange 4S1P/4S2P/6S1P/6S2P in
> one cradle is superseded by ADR-0042.

- The 21700 cells **do not stack**: single 21 mm layer. At 13.5 % t/c and c_root 260 mm there is ~35 mm — roomy. **At 11 % it did not fit.**
- Future 4S/2P modules must re-close propulsion, fit, CG, mass and stall independently.

## 3.4 Structure

| Requirement | Value |
|---|---|
| Material | Conventional PETG, light color |
| Perimeters / infill | 2 (0.9 mm) / **gyroid 5 %** |
| Section | Three cells: D-box + center + hinge |
| Carbon | Bending tube + joint pin. **Not primary torsional** |
| Divergence criterion | V_div ≥ 1.5 × V_NE |
| Joints | Tenon + specific PETG adhesive, area ≥ 3× the skin section |
| Elevons | **Mass balancing mandatory**, no-freeplay linkage |

## 3.5 Avionics

| Requirement | Value |
|---|---|
| Controller | INAV 9.1+ or ArduPlane. Geometry-agnostic |
| **Pitot** | **Mandatory.** Without it, E2 and E7 are not valid |
| Blackbox | SD or flash. Instrument of the whole test program |
| GPS and magnetometer | Out of the root current path |
| Launch | Autolaunch via acceleration detection |

## 3.6 Directional configuration (ADR-0038)

The platform publishes **two directional configurations** for the reference design,
differing only in an optional fixed centreline fin (a CORE component — no servo, no
linkage, no FC change):

| | SALAMANDRA-CLEAN | SALAMANDRA-V1 |
|---|---|---|
| Vertical stabilizer | None | Fixed centreline fin (passive), S_v ≈ 2.1 dm² (V1a) |
| Cnβ total | **−0.0006…−0.0014/deg — negative** (FC recovery unproven; not the first-flight configuration, G10/C31) | **−0.00005…+0.00095/deg** (nominal +0.0005) `[D]`/`[E]` |
| Role | O1 efficiency build (≤ 1.15 Wh/km) | Recommended build for the Article #1 test programme |
| Cost | — | 36–60 g `[E]` · ΔCD0 +0.0014 (+9.6 % energy `[E]`) · V_stall +0.6 km/h (OP-24 lever) |

**Rudder (movable): not required** — authority analysis shows it cannot hold a 20 km/h
crosswind slip at stall and the mission coordinates turns through roll (I-20 §5.4;
Mojito precedent `[M]` carries a fixed stabilizer and no rudder servo). Reopened as a
future variant only if the E-flight programme (E8) demonstrates a yaw-handling failure
mode.

Full analysis: [I-20](../research/I-20-yaw-stability-centerline-fin.md),
[ADR-0038](../decisions/ADR-0038-fixed-fin-variant.md), `calculations/yaw_stability.py`.
Closure of the directional gap (G10) is by flight test (E8).

---

# 4. Dominant risk

**It is not aerodynamic. It is structural: torsional stiffness against aeroelastic divergence.**

Full development in [I-05](../research/I-05-divergence-flutter.md).

**Open risk unverified: flutter** (G7). The identified critical mode is the elevon's, and **it is not solved with stiffness** — it is inertial. See [ADR-0025](../decisions/ADR-0025-elevon-balancing.md).
