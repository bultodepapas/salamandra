# Salamandra — Design Guide

**Version 0.1 (first release)** · 5 August 2026 · Status: **DRAFT — for designer review**

This document is the working specification handed to the CAD designer. It defines the
reference configuration (Cruise, Article #1) of the Salamandra modular 3D-printed FPV
aircraft platform with every value needed to model it in Fusion 360 or any other 3D
modeling program. All values are derived from the project's research
([`research/`](../research/)), decisions ([`decisions/`](../decisions/)) and measured data
([`docs/02-measured-references.md`](../docs/02-measured-references.md)); where data were
missing, the best available assumption was made and is flagged `PROVISIONAL`.

The justification for every value lives in
[`Design-Guide-Justification-v0.1.md`](Design-Guide-Justification-v0.1.md). Open points and
the expected evolution of this guide live in
[`Design-Guide-Open-Points-v0.1.md`](Design-Guide-Open-Points-v0.1.md).

Image-generation prompts (render, blueprint, realistic photo, creative) bound to this
version live in [`prompts/`](prompts/).

---

## 1. Document control

| | |
|---|---|
| Designation | Salamandra — Design Guide |
| Version | 0.1 (first release) |
| Date | 2026-08-05 |
| Status | DRAFT — pending designer iteration and Phase 1 closure |
| Reference configuration | **Cruise — Article #1** |
| Inputs | ADR-0001…ADR-0037, I-01…I-08, docs/00, docs/02, docs/03, docs/04, docs/05 |
| Intended reader | CAD designer (Fusion 360 or equivalent) |

**How this guide evolves.** The design is expected to change as Phase 1 closes (airfoil
selection, stability verification) and as the designer iterates. Each published revision
bumps the version number (0.1 → 0.2 → … → 1.0 at first prototype). Revisions are recorded
in §14 of this document and in the [CHANGELOG](../CHANGELOG.md). Values marked
`PROVISIONAL` are the ones most likely to change.

---

## 2. Conventions

### 2.1 Coordinate system (for CAD)

- Origin: **root quarter-chord point (root c/4)** at the centerline (y = 0), at the
  section mid-plane (z = 0).
- **x**: positive **backward** (toward the trailing edge).
- **y**: positive **right** (spanwise); the half-span is y ∈ [0, +650] mm.
- **z**: positive **up**; z = 0 is the section mid-plane (half-thickness).

### 2.2 Sign conventions

| Quantity | Symbol | Sign |
|---|---|---|
| Sweep | Λ | Negative = **forward** (tips ahead of root). Project uses Λ_c/4 = **−20°** |
| Twist | ε | Positive = **wash-in** (tip at higher incidence than root) |
| Dihedral | Γ | Positive = tips up |

### 2.3 Units

Millimeters and grams in this document. SI in all calculations. Confidence tags per
[`docs/04-conventions.md`](../docs/04-conventions.md): `[M]` measured, `[D]` derived,
`[E]` estimated, `[I]` inferred. **PROVISIONAL** = value assumed because no project datum
exists yet; it will be updated by the open point listed.

---

## 3. Design summary (one-page specification)

| Parameter | Value | Status |
|---|---|---|
| Configuration | Forward-swept tailless flying wing (FSW), modular CORE + PANEL | ADR-0001, ADR-0032 |
| Propulsion | Single pusher, electric | PROVISIONAL (ADR-0006 under dispute) |
| Wingspan b | **1300 mm** | ADR-0010, fixed |
| Wing area S | **0.282 m²** | ADR-0004 |
| Aspect ratio AR | **6.0** | ADR-0004 |
| Taper ratio λ | **0.50** | I-07 |
| Root chord c_root | **289 mm** | I-07 |
| Tip chord c_tip | **145 mm** | I-07 |
| Mean aerodynamic chord (MAC) | **225 mm** | I-07 |
| Sweep Λ_c/4 | **−20.0°** (LE −17.1°, TE −27.9°) | I-07 / derived |
| Relative thickness t/c | **13.5 % root → 9 % tip** (linear) | ADR-0027 |
| Geometric twist ε | **+0.5° wash-in** (linear root→tip) | PROVISIONAL (R-TWIST ≤ 2.5°) |
| Dihedral Γ | **2.0° total** (polyhedral at segment joints) | PROVISIONAL |
| Airfoil | Reflexed; root/tip candidates pending B3 screening (G2) | **PENDING** — §6 |
| Neutral point NP | **26.7 % MAC** (= −101 mm from root c/4) | `[D]` I-07 |
| Target CG | **18.7 % MAC** (= −119 mm from root c/4, SM 8 %) | `[D]` I-07; see OP-01 |
| All-up weight (6S1P) | **1620 g** | ADR-0010 / R-CG |
| Wing loading (6S1P) | **57 g/dm²** | derived |
| Cruise speed / CL | **95 km/h** / CL 0.132 | docs/00, I-07 |
| Stall speed | **≤ 45 km/h** (≈ 44.6 km/h at CL_max 0.60) | docs/00 (C16), I-07 |
| V_NE (article #1) | **160 km/h** (design 180) | docs/00 |
| Load factors | +6 / −3 (later +9), gust-dominated | docs/00 |
| Skin / infill | 0.9 mm (2 perimeters) / gyroid 5 % | ADR-0028 |
| Carbon | Bending tube Ø12×1.0 + anti-rotation pin Ø6 | PROVISIONAL (ADR-0015) |
| Reference propeller | APC-E 8×8 (J_opt 0.784, η 0.731) | ADR-0007 |
| Reference motor | 28-class, 500–550 KV, ~170 g | PROVISIONAL (ADR-0033) |
| Battery (reference) | 6S1P Li-Ion 21700, 97 Wh, ~455 g | docs/00 |

---

## 4. Mission and design envelope

| Requirement | Value | Source |
|---|---|---|
| Design range | 80 km + 20 % reserve (extended 100 km, contingent on E3) | docs/00 |
| Endurance | 60 min at minimum-power speed | docs/00 |
| Cruise speed | 90–105 km/h; design point **95 km/h** | docs/00 |
| V_NE article #1 | **160 km/h** (design V_NE 180) | docs/00 |
| Stall speed | **≤ 45 km/h** | docs/00 (C16) |
| Required C_Lmax | ≥ 0.65 | docs/00 |
| n_max / n_min | +6 / −3 (later +9) | docs/00 |
| Launch | Hand launch, autolaunch via acceleration detection | docs/00 |
| Battery configs | 4S1P, 6S1P, 4S2P, 6S2P (21700); 6S2P out of cruise envelope | docs/00 (R-CG) |
| Divergence criterion | V_div ≥ 1.5 × V_NE | docs/00 |

Salamandra is a modular platform: this guide specifies the **Cruise** configuration
(1300 mm). The Range (1600 mm) and Sport (1100 mm) configurations share the CORE and
follow the same rules via R-NP ([ADR-0032](../decisions/ADR-0032-modularity.md)); they are
out of scope for v0.1.

---

## 5. Reference planform (Cruise, Article #1)

### 5.1 Overall geometry

```
             y=650 (tip)              LE sweep −17.1°
               ┌─────────────────╮
              /        c/4 line Λ=−20°
             /                  ╲
            /        MAC 225    ╲
      y=0  ┼──────────────────────╮
        CORE  |←── c_root 289 ──→|  TE sweep −27.9°
       (joiners
      to 30%)
```

- b = 1300 mm; S = 0.282 m²; AR = 6.0; λ = 0.50
- c_root = 289.2 mm; c_tip = 144.6 mm; MAC = 224.9 mm
- Sweep: Λ_c/4 = −20.0°; Λ_LE = −17.1°; Λ_TE = −27.9° (derived)
- Twist: ε = +0.5° wash-in, linear from root (0°) to tip (+0.5°)
- Dihedral: Γ = 2.0° total at the tip, polyhedral at the segment joints
- Chord distribution: **linear** c(y) = 289.2 − 0.2225·y [mm]

### 5.2 Station table (design stations)

All x-values from the root c/4 origin; chord and thickness in mm.

| y (mm) | y/(b/2) | Station | c (mm) | t/c (%) | t (mm) | x_LE (mm) | x_c/4 (mm) | x_TE (mm) |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| 0 | 0.00 | Centerline (root) | 289.2 | 13.5 | 39.0 | −72.3 | 0.0 | +216.9 |
| 130 | 0.20 | Elevon inner end | 260.3 | 12.6 | 32.8 | −112.4 | −47.3 | +147.9 |
| 195 | 0.30 | CORE joiner / joint | 245.8 | 12.2 | 29.9 | −132.4 | −71.0 | +113.4 |
| 325 | 0.50 | Mid half-span | 216.9 | 11.3 | 24.4 | −172.5 | −118.3 | +44.4 |
| 347 | 0.53 | Segment cut 1 | 212.0 | 11.1 | 23.5 | −179.3 | −126.3 | +32.7 |
| 487.5 | 0.75 | 75 % half-span | 180.8 | 10.1 | 18.3 | −222.6 | −177.4 | −41.8 |
| 498 | 0.77 | Segment cut 2 | 178.4 | 10.1 | 17.9 | −225.9 | −181.3 | −47.5 |
| 585 | 0.90 | Elevon outer end / spar end | 159.0 | 9.5 | 15.1 | −252.7 | −212.9 | −93.7 |
| 650 | 1.00 | Tip | 144.6 | 9.0 | 13.0 | −272.7 | −236.6 | −128.1 |

### 5.3 Planform control values for CAD

| Control | Value |
|---|---|
| Root chord | 289.2 mm at y = 0, LE at x = −72.3 |
| Tip chord | 144.6 mm at y = 650, LE at x = −272.7 |
| c/4 line | Straight line from (0, 0) to (−236.6, 650); slope −0.3640 (= tan 20°) |
| LE line | Straight line from (−72.3, 0) to (−272.7, 650); slope −0.3084 |
| TE line | Straight line from (+216.9, 0) to (+108.5, 650); slope −0.5308 |
| t/c schedule | Linear: 13.5 % at y = 0 → 9.0 % at y = 650 |
| Twist schedule | Linear: ε = 0° at y = 0 → +0.5° at y = 650 (wash-in, trailing edge down) |
| Dihedral | Cumulative 2.0° at tip; segment rotations: 0° (CORE) / +1.07° (seg. 1) / +0.46° (seg. 2) / +0.47° (seg. 3) |

> **Segment rotation for polyhedral dihedral** (cumulative at joint, PROVISIONAL): inner
> joint (y = 347) +1.07°, outer joint (y = 498) +1.53°, tip +2.0°. Linear schedule
> Γ(y) = 2.0° × (y/650).

---

## 6. Airfoil

**Status: PENDING — G2 (B3 screening). The coordinates below are provisional working
candidates, not the final airfoil.** The profile is the single most likely item to change;
all other geometry is defined independently of the exact profile except the twist value
(§5.3), which is re-derived when the airfoil is fixed (C5).

### 6.1 Design requirements (binding)

| Requirement | Value | Source |
|---|---|---|
| t/c root / tip | **13.5 % / 9 %** (linear) | ADR-0027 |
| Reflex (C_m0) | **≥ +0.008**, target **+0.010…+0.015** | R-AIRFOIL (I-07) |
| C_Lmax (section) | **≥ 0.65** | docs/00, Ananda et al. `[M]` |
| Reynolds range | **Re ≈ 3–5×10⁵** (root) | I-01 |
| Family | Reflexed low-Re flying-wing airfoils | B3 (docs/03) |
| L/D at cruise CL | As high as possible at CL = 0.132 | B2 |

### 6.2 Provisional candidates for v0.1 CAD

| Station | Provisional candidate | Note |
|---|---|---|
| Root | **MH 45** (t/c ≈ 13 %, MH family, aerodesign.de) | B3 candidate; closest MH to 13.5 %; to be confirmed/scaled |
| Tip | MH-family profile thinned to 9 % t/c | 9 % reflexed candidates are scarce; selection resolved in B3 |
| Reference | PW51 (in-service FSW precedent, Nemesis) | I-08 quasi-controlled comparison `[M]` |

### 6.3 CAD instructions

1. Model the airfoil **parametrically**: t/c = 13.5 % (root) and 9 % (tip) as the driving
   constraints, reflex magnitude per R-AIRFOIL.
2. Keep the airfoil as a swappable component (external coordinates file): when B3 releases
   the calibrated polar and final coordinates, only the profile and the twist setting
   change.
3. The tip station (y = 650) is the thinnest section (13.0 mm max thickness); verifying
   servo and hinge-structure fit there is not required — servos sit inboard (§7.5).

---

## 7. Structure

### 7.1 Cross-section (three cells)

| Cell | Span x/c | Function |
|---|---|---|
| D-box | 0.00 → 0.30 | Closed leading-edge torsion box; houses main spar tube |
| Center cell | 0.30 → 0.72 | Main closed box (Bredt-Batho section); shear web at 0.30 |
| Hinge cell | 0.72 → 1.00 | Elevon structure and hinge line at **0.72 c** |

- Skin: **0.9 mm** (2 perimeters × 0.45 mm), gyroid **5 %** infill throughout
  (ADR-0028). Without infill the skin buckles and the closed section fails (C12).
- Front shear web (D-box web) at **x/c = 0.30** (PROVISIONAL).
- Hinge line at **x/c = 0.72** (ADR-0002): the closed torsion box ends here.

### 7.2 Carbon elements (ADR-0015 — bending, not torsion)

| Element | Spec | Position | Note |
|---|---|---|---|
| Main spar tube | Pultruded carbon **Ø12 × 1.0 mm**, per panel | At **x/c = 0.25** (≈ the c/4 line), from the CORE joiner (y = 195) to y = 585 | PROVISIONAL sizing; bending only |
| Anti-rotation pin | Solid carbon **Ø6 mm** | **65 mm aft** of the tube axis, in the CORE joiner region | R-JOINT couple; PROVISIONAL |
| Tube length | ~390 mm per panel | — | — |

> Torsion is carried by the closed shell, not the carbon (ADR-0015, C11). The braided
> torsion tube remains documented option B (ADR-0030), not used in v0.1.

### 7.3 Modular joints

- **CORE↔PANEL joint at y = ±195 (30 % half-span)** (ADR-0032):
  - Wing joiner sockets ("muñones") in the CORE: main tube socket + anti-rotation pin
    socket, spaced 65 mm apart.
  - **Removable** (no adhesive): panels swap for Range/Sport configurations.
  - R-JOINT: joint torsional stiffness ≥ **5×** the adjacent section (ADR-0032).
- **Segment joints** (within a panel): tenon + PETG adhesive, bond area ≥ **3× the skin
  section** (ADR-0023). Adhesive: 3D-Gloop PETG or 30-min epoxy (I-04; not E6000).

### 7.4 Segmentation and printing (ADR-0024)

| Item | Value |
|---|---|
| Segments per wing half | **3** (plus the CORE) |
| Segment cuts | y = **347 mm** and **498 mm** (53.3 % / 76.7 % half-span) |
| Print orientation | **45° on the bed** (segments) |
| Printer class | 256 mm bed (Bambu P1S class), no active chamber (O3) |
| Material | Conventional PETG, **light color** (ADR-0012, ADR-0021) |
| Profile | 0.4 mm nozzle, 0.2 mm layer, 0.45 mm wall width, **2 perimeters (0.9 mm)**, gyroid **5 %** |
| Flow ratio | **0.95** — never the 0.60 LW-PLA value (docs/02 §1.7) |
| Temperatures | Nozzle 240–250 °C, bed 70–80 °C, fan ≈ 30 % (PETG; PROVISIONAL) |
| Print budget | ≤ 20 h per wing half (O5) |

### 7.5 Elevons

| Parameter | Value | Status |
|---|---|---|
| Hinge line | **x/c = 0.72**, full chord-wise boundary | ADR-0002 |
| Elevon chord | **0.28 c** (constant fraction) | ADR-0002 |
| Elevon span | y = 130 → 585 mm (20 % → 90 % half-span); length **455 mm** | PROVISIONAL |
| Travel | ±20° (provisional; authority to be verified, C6) | PROVISIONAL |
| Mass balance | **Mandatory**: elevon assembly CG **on the hinge line**; ~30 g balance mass per elevon in a forward pocket | ADR-0025 |
| Actuation | **Dual actuation** (2 points per elevon, elevon > 400 mm), no-freeplay linkage, digital servos | ADR-0026 |
| Servos | 4× digital 13–15 g, at y ≈ 195 and y ≈ 390 (per half) | PROVISIONAL |
| Hinges | TPU-printed (glued or live-hinge), ADR-0035 | PROVISIONAL |

---

## 8. Mass budget and CG

### 8.1 Mass budget (Cruise, 6S1P) — sums to 1620 g AUW

| Component | Mass (g) | Status |
|---|---:|---|
| Printed shell (CORE + 6 segments) | 600 | `[E]` (docs: 550–650) |
| Carbon (tubes + pins) | 70 | `[E]` |
| Motor (28-class) | 170 | `[E]` |
| ESC (6S 30 A) | 35 | `[E]` |
| Avionics (FC, pitot, GPS, RX, wiring) | 110 | `[E]` |
| Servos (4 × 15 g) | 60 | `[E]` |
| Propeller + hub/spinner | 40 | `[E]` |
| Elevon balance mass | 60 | `[E]` (ADR-0025) |
| Hardware (screws, TPU hinges, adhesive, misc) | 20 | `[E]` |
| **Battery 6S1P (21700)** | **455** | `[E]` |
| **Total** | **1620** | **57 g/dm²** |

### 8.2 CG target

| Quantity | Value |
|---|---|
| Neutral point | **26.7 % MAC** = −101 mm from root c/4 (VLM `[D]`, I-07) |
| **Target CG** | **18.7 % MAC** = **−119 mm from root c/4** (8 % static margin) |
| CG vs root LE | 47 mm **forward** of the root leading edge |
| R-CG | CG within **±5 mm** of target in all four battery configs (docs/00 §3.3) |
| Adjustment | Battery bay longitudinal slide (see §9) |

> ⚠️ **OP-01 (critical):** a preliminary moment balance of the §8.1 budget shows the
> reachable CG band (≈ −27…+29 mm with the battery at the extreme forward position) does
> **not** reach the −119 mm target with the current planform and masses. The neutral point
> must be re-verified with an independent method (C2, I-07 §7.1) and the body effect
> (I-07 §6) assessed before the bay position is finalized. For v0.1, place the bay as far
> forward as structurally possible (nose section) and treat the mass balance as the
> driving F2 task. Full analysis in the justification document, §3.1.

---

## 9. Battery and bay

| Parameter | Value | Status |
|---|---|---|
| Cells | Li-Ion **21700**, Ø21 × 70 mm, **single layer** (never stacked) | docs/00 |
| Bay internal dims (x × y × z) | **180 × 70 × 32 mm** | PROVISIONAL |
| Bay position | In the CORE, centered on the centerline, **as far forward as possible** (nose section); see OP-01 | PROVISIONAL |
| Longitudinal adjustment | Pack slide rails along x; range sized to keep CG within ±5 mm for 4S1P, 6S1P, 4S2P, 6S2P | docs/00 R-CG |
| Pack configs | 4S1P ~300 g / 6S1P ~455 g / 4S2P ~605 g / 6S2P ~910 g (out of cruise envelope) | docs/00 |
| Bay height check | 21 mm cells + clearance ≈ 27 mm ≤ 32 mm; root thickness 39 mm at centerline | derived |

---

## 10. Propulsion

### 10.1 Reference configuration (recommended, not prescribed — ADR-0033)

| Element | Reference | Basis |
|---|---|---|
| Layout | **Single pusher** at the CORE rear center | PROVISIONAL (ADR-0006 under dispute) |
| Propeller | **APC-E 8×8** — P/D 1.00, η_max 0.731, J_opt 0.784 | ADR-0007, UIUC `[D]` |
| Cruise operating point | ~**9,900 rpm** at 95 km/h (J = 0.784) | derived from J_opt |
| Motor | 28-class (Ø28 mm), **500–550 KV**, ~170 g, ≥ 400 W peak | PROVISIONAL, derived |
| ESC | 6S, **30 A** (cruise ≈ 5 A, peak ≈ 20 A) | derived |
| Alternatives | APC-E 9×6, 10×7 (matching table, D3/D4) | ADR-0007 |

### 10.2 Motor mount

| Parameter | Value | Status |
|---|---|---|
| Location | Integrated in the CORE rear, centerline | ADR-0032 |
| Motor axis | At the section mid-plane height (z = 0) | PROVISIONAL |
| Thrust angle | **0.8° up** (upthrust) | PROVISIONAL — Peregrine precedent `[M]`, ADR-0034 |
| Thrust line | Intended to pass near the CG plane to minimize pitch coupling | PROVISIONAL |
| Prop clearance | Prop disk aft of the TE; 8 in (203 mm) diameter with ≥ 10 mm ground/tail clearance | PROVISIONAL |

---

## 11. Avionics and systems

| Item | Requirement | Source |
|---|---|---|
| Flight controller | INAV 9.1+ or ArduPlane; geometry-agnostic | docs/00 §3.5 |
| **Pitot** | **Mandatory** — without it E2/E7 are invalid; probe at y ≈ 260 mm (40 % half-span) leading edge, out of prop wash | docs/00 (PROVISIONAL position) |
| Blackbox | SD or flash, mandatory | docs/00 |
| GPS / magnetometer | **Out of the root current path** (battery wires); nose pedestal position | docs/00 |
| Launch | Autolaunch via acceleration detection | docs/00 |
| Servos | 4× digital, no freeplay, dual actuation per elevon | ADR-0026 |
| Wiring | Current path (ESC→battery) separated from GPS/mag and pitot runs | docs/00 |

---

## 12. Assembly and control setup

1. Print CORE + 6 segments (3 per half) per §7.4. Light-color PETG.
2. Glue segment joints (tenon + adhesive, area ≥ 3× skin section). Do **not** glue the
   CORE↔panel joint.
3. Insert carbon tube (x/c = 0.25) and anti-rotation pin; bond the tube inside the panel
   sockets with continuous adhesive (ADR-0015 §3.3: continuous bonding, not housed).
4. Install elevons with TPU hinges at x/c = 0.72; **mass-balance each elevon** (CG on
   hinge line) before installing servos (ADR-0025).
5. Install 4 servos, zero-freeplay linkage, dual actuation points.
6. Mount motor (0.8° upthrust), ESC, prop; battery on slide rails.
7. Balance: target CG **−119 mm from root c/4** (47 mm forward of root LE); verify in the
   four battery configs (R-CG, ±5 mm).
8. Avionics per §11; pitot, GPS/mag wiring clear of the current path.

---

## 13. Governing references

| Set | Documents |
|---|---|
| Decisions | ADR-0001, 0002, 0004, 0007, 0010, 0015, 0021–0028, 0032–0037 ([`decisions/`](../decisions/)) |
| Research | I-01…I-08 ([`research/`](../research/)) |
| Specification | [`docs/00-objectives-and-requirements.md`](../docs/00-objectives-and-requirements.md) |
| Measured data | [`docs/02-measured-references.md`](../docs/02-measured-references.md) |
| Plans | [`docs/03-phase-1-plan.md`](../docs/03-phase-1-plan.md), [`docs/05-master-plan.md`](../docs/05-master-plan.md) |
| Conventions | [`docs/04-conventions.md`](../docs/04-conventions.md) |

---

## 14. Revision log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-08-05 | First release. Reference geometry per I-07/ADR-0027; provisional airfoil (B3 pending), dihedral, twist, carbon, motor, bay. OP-01 flagged. |
