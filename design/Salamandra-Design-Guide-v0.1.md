# Salamandra — Design Guide

**Version 0.2** · 5 August 2026 · Status: **DRAFT — for designer review**

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
| Version | 0.2 |
| Date | 2026-08-05 |
| Status | DRAFT — pending designer iteration and Phase 1 closure |
| Reference configuration | **Cruise — Article #1** |
| Inputs | ADR-0001…ADR-0037, I-01…I-15, docs/00, docs/02, docs/03, docs/04, docs/05 |
| Intended reader | CAD designer (Fusion 360 or equivalent) |

**How this guide evolves.** The design is expected to change as Phase 1 closes (airfoil
selection, stability verification) and as the designer iterates. Each published revision
bumps the version number (0.1 → 0.2 → … → 1.0 at first prototype). Revisions are recorded
in §14 of this document and in the [CHANGELOG](../CHANGELOG.md). Values marked
`PROVISIONAL` are the ones most likely to change. v0.2 changes from v0.1 are listed in
§14; the corrections that drove them are C22–C27 in the CHANGELOG.

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

> ⚠️ **Stall margin is the tightest in the design:** ≈ 44.6 km/h at CL_max 0.60 vs the
> 45 km/h requirement — a 0.4 km/h margin (I-07 §4.2). The launch is a mandatory hand
> throw; launch-speed feasibility is under investigation (I-14). Do not relax the
> CL_max chain without re-deriving this requirement (C16 history).

Salamandra is a modular platform: this guide specifies the **Cruise** configuration
(1300 mm). The Range (1600 mm) and Sport (1100 mm) configurations share the CORE and
follow the same rules via R-NP ([ADR-0032](../decisions/ADR-0032-modularity.md)); they are
out of scope for v0.2.

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
- Dihedral: Γ = 2.0° total at the tip, polyhedral at the segment joints (§5.3)
- Chord distribution: **linear** c(y) = 289.2 − 0.2225·y [mm]
- Wing tips (y = ±650): **flat end caps** closing the section, no winglet in v0.2
  (PROVISIONAL — see OP-20).

### 5.2 Station table (design stations)

All x-values from the root c/4 origin; chord and thickness in mm.

| y (mm) | y/(b/2) | Station | c (mm) | t/c (%) | t (mm) | x_LE (mm) | x_c/4 (mm) | x_TE (mm) |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| 0 | 0.00 | Centerline (root) | 289.2 | 13.5 | 39.0 | −72.3 | 0.0 | +216.9 |
| 130 | 0.20 | In-CORE station (fixed TE) | 260.3 | 12.6 | 32.8 | −112.4 | −47.3 | +147.9 |
| 195 | 0.30 | CORE joiner / joint | 245.8 | 12.2 | 29.9 | −132.4 | −71.0 | +113.4 |
| 325 | 0.50 | Mid half-span | 216.9 | 11.3 | 24.4 | −172.5 | −118.3 | +44.4 |
| 347 | 0.53 | Segment cut 1 | 212.0 | 11.1 | 23.5 | −179.3 | −126.3 | +32.7 |
| 487.5 | 0.75 | 75 % half-span | 180.8 | 10.1 | 18.3 | −222.6 | −177.4 | −41.8 |
| 498 | 0.77 | Segment cut 2 | 178.4 | 10.1 | 17.9 | −225.9 | −181.3 | −47.5 |
| 585 | 0.90 | Elevon outer end / spar end | 159.0 | 9.5 | 15.1 | −252.7 | −212.9 | −93.7 |
| 650 | 1.00 | Tip | 144.6 | 9.0 | 13.0 | −272.7 | −236.6 | −128.1 |

### 5.3 Planform control values for CAD

| Control | Value |
|---|---|---|
| Root chord | 289.2 mm at y = 0, LE at x = −72.3 |
| Tip chord | 144.6 mm at y = 650, LE at x = −272.7 |
| c/4 line | Straight line from (0, 0) to (−236.6, 650); slope −0.3640 (= tan 20°) |
| LE line | Straight line from (−72.3, 0) to (−272.7, 650); slope −0.3084 |
| TE line | Straight line from (+216.9, 0) to (+108.5, 650); slope −0.5308 |
| t/c schedule | Linear: 13.5 % at y = 0 → 9.0 % at y = 650 |
| Twist schedule | Linear: ε = 0° at y = 0 → +0.5° at y = 650 (wash-in, trailing edge down); applied as a rotation of each section about the **spanwise axis through the local c/4 point** |
| Dihedral | Polyhedral, piecewise-linear; cumulative at the outboard end of each segment: CORE 0° (y 0–195) / seg 1 +1.07° (195–347) / seg 2 +1.53° (347–498) / seg 3 +2.0° (498–650) |

> **Dihedral — exact CAD recipe (PROVISIONAL, C22).** Each printed segment is modeled
> **flat** (all its sections in one plane). In the assembly, each segment is rotated about
> the chordwise (x) axis — through its inboard joint line, at the section mid-plane
> (z = 0) — by its **cumulative** dihedral angle: segment 1 +1.07° at y = 195, segment 2
> +1.53° at y = 347, segment 3 +2.0° at y = 498. Kinks occur at **every** segment joint
> (y = 195, 347, 498), including the CORE↔PANEL joint; the CORE stays at 0°. Tip rise
> ≈ **12 mm**. The joint values are generated by Γ(y) = 2.0° × (y/650) sampled at the
> joints; within a segment the dihedral is constant, not continuous.

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
| Reynolds range | **Re(MAC) ≈ 3–5×10⁵**; root up to ≈ 5.2×10⁵ at cruise, ≈ 2.5×10⁵ at stall | I-01 |
| Family | Reflexed low-Re flying-wing airfoils | B3 (docs/03) |
| **Stall character** | **Gentle, root-first; no tip stall before the root** — a criterion of the designed section, not a hope: the thickness-separation evidence shows thick sections can transition local → massive separation | I-02, I-15/A5 |
| L/D at cruise CL | As high as possible at CL = 0.132 | B2 |

> **R-AIRFOIL feasibility at 13.5 % t/c is an open B3 question (I-11, I-15):** no
> published reflexed section reaches that thickness (closest: MH 60-12 % at 12.0 %,
> cm0 +0.0030). The aerodynamic evidence indicates the root section must be **designed,
> not selected** (thickness-distribution and reflex evidence campaign, I-15); the
> requirement may alternatively be re-derived against the twist window (I-07). Until
> then the airfoil row is doubly provisional. **Confidence basis: no measured polar of a
> reflexed section exists at Re 3–5×10⁵ (I-15); the XFOIL screening is `[D]` anchored on
> measured LSB data (E387, NASA-CR-186263 — I-06), and the printed PETG skin transitions
> earlier than the smooth-tunnel calibration — E2 (flight polar) is the closer.**

### 6.2 Provisional candidates for the v0.2 CAD

| Station | Provisional candidate | Note |
|---|---|---|
| Root | Reflexed section scaled to t/c 13.5 % — **MH 60-12 %** (12.0 %, cm0 +0.0030 `[M]`) is the closest published family member; **MH 45 is 9.85 % thick, not 13 % (C28)** and is documented for 15–40 g/dm², below the project's 57 g/dm² | B3 candidate; no off-the-shelf reflexed section reaches 13.5 % — R-AIRFOIL feasibility at 13.5 % is an explicit B3 question (I-11) |
| Tip | Reflexed section at t/c 9 % with **camber compensation** — pure thickness scaling of a reflexed section is warned against (MH 45-8 % precedent: clmax loss, harsh stall `[M]`, I-11) | 9 % reflexed candidates are scarce; selection resolved in B3 |
| Tip (data point) | **E205** (t/c 10.6 %, camber 2.9 %, flight-proven at Re 1.5–3×10⁵ on the Pico Talon and Stallion, I-09) | **Not admitted on the manuals alone** — its Cm0 is unknown and likely negative (tailed planes trim it); include in the B3 XFOIL screening (Ncrit 10–12 band) and decide from the polar |
| Reference | PW51 (in-service FSW precedent, Nemesis) | I-08 quasi-controlled comparison `[M]`; **not in the UIUC database** (I-11) — coordinates/polars must be sourced elsewhere |

### 6.3 CAD instructions

1. Model the airfoil **parametrically**: t/c = 13.5 % (root) and 9 % (tip) as the driving
   constraints, reflex magnitude per R-AIRFOIL.
2. Keep the airfoil as a swappable component (external coordinates file): when B3 releases
   the calibrated polar and final coordinates, only the profile and the twist setting
   change.
3. **Provisional coordinates for the v0.2 CAD** (to be replaced by the B3 output, OP-02):
   - Root: **MH 60-12 %** coordinates (aerodesign.de), scaled to t/c = 13.5 %.
     (MH 45 is 9.85 % thick and documented for 15–40 g/dm² — not suitable as the root
     starting point, C28/I-11.)
   - Tip: **MH 60-12 % thickness-scaled to t/c = 9 % with camber compensation** — do not
     apply pure affine y-scaling (the reflexed-airfoil database warns that thinning
     reflexed sections costs clmax and hardens the stall, I-11). The final tip profile
     is selected in B3.
   - Place the coordinate files under `geometry/` and reference them from the CAD model
     (swappable).
4. The tip station (y = 650) is the thinnest section (13.0 mm max thickness); verifying
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
| Main spar tube | Pultruded carbon **Ø12 × 1.0 mm**, per panel | At **x/c = 0.25** (the c/4 line), from the CORE joiner (y = 195) to y = 585 | PROVISIONAL sizing; bending only |
| Anti-rotation pin | Solid carbon **Ø6 mm** | **65 mm aft** of the tube axis, in the CORE joiner region | R-JOINT couple; PROVISIONAL |
| Tube spanwise extent | y = 195 → 585 (390 mm) | — | — |
| **Tube physical length** | ≈ **485 mm**: ≈ 415 mm bonded in the panel along the swept c/4 line + ≈ 70 mm protruding into the CORE socket (no adhesive) | — | C27; cut length to be confirmed on the CAD geometry |
| **Pin physical length** | ≈ **140 mm**: ≈ 70 mm bonded in the panel root + ≈ 70 mm protruding into the CORE socket (no adhesive) | — | matches the ≈ 70 mm socket depth |

> Torsion is carried by the closed shell, not the carbon (ADR-0015, C11). The braided
> torsion tube remains documented option B (ADR-0030), not used in v0.2.

### 7.3 Modular joints

- **CORE↔PANEL joint at y = ±195 (30 % half-span)** (ADR-0032):
  - Wing joiner sockets ("muñones") in the CORE: main tube socket + anti-rotation pin
    socket, spaced 65 mm apart. Socket centerlines at the joint face: tube at
    x = −9.6 mm (x/c = 0.25 at that station, on the c/4 line), pin at x = +55.4 mm.
  - Socket bores: tube Ø12.2–12.4 mm, pin Ø6.1–6.2 mm (sliding fit, removable joint),
    depth ≈ 70 mm each.
  - **Removable** (no adhesive): panels swap for Range/Sport configurations. The tube and
    pin are bonded in the PANEL and protrude ≈ 70 mm (tube) / ≈ 70 mm (pin) into the CORE
    sockets.
  - R-JOINT: joint torsional stiffness ≥ **5×** the adjacent section (ADR-0032).
- **Segment joints** (within a panel): tenon + PETG adhesive, bond area ≥ **3× the skin
  section** (ADR-0023). Adhesive: 3D-Gloop PETG or 30-min epoxy (I-04; not E6000).

### 7.4 Segmentation and printing (ADR-0024)

| Item | Value |
|---|---|---|
| Segments per wing half | **3** (plus the CORE) |
| Segment cuts | y = **347 mm** and **498 mm** (53.3 % / 76.7 % half-span) |
| Print orientation | **45° roll of the airfoil plane about the spanwise axis** (airfoil at 45° to the bed, leading edge low). Footprint: span 152 mm × chord·cos 45° ≈ 174 mm (panel root segment) — fits the 256 mm bed (C24). Do not lay the span axis at 45° in the bed plane: segments 1–2 would need ≈ 280 mm |
| Printer class | 256 mm bed (Bambu P1S class), no active chamber (O3) |
| Material | Conventional PETG, **light color** (ADR-0012, ADR-0021) |
| Profile | 0.4 mm nozzle, 0.2 mm layer, 0.45 mm wall width, **2 perimeters (0.9 mm)**, gyroid **5 %** |
| Flow ratio | **0.95** — never the 0.60 LW-PLA value (docs/02 §1.7) |
| Temperatures | Nozzle 240–250 °C, bed 70–80 °C, fan ≈ 30 % (PETG; PROVISIONAL) |
| Print budget | ≤ 20 h per wing half (O5) |

### 7.5 Elevons

| Parameter | Value | Status |
|---|---|---|---|
| Hinge line | **x/c = 0.72**, full chord-wise boundary | ADR-0002 |
| Elevon chord | **0.28 c** (constant fraction) | ADR-0002 |
| Elevon span | y = **195 → 585 mm** (30 % → 90 % half-span); length **390 mm**. The elevon is a **PANEL component**: its inner end is the panel root at the CORE↔PANEL joint; the CORE trailing edge is fixed (no control surface on the shared CORE, C23) | PROVISIONAL |
| Travel | ±20° (provisional; authority to be verified, C6) | PROVISIONAL |
| Mass balance | **Mandatory**: elevon assembly CG **on the hinge line**; ~30 g balance mass per elevon in a forward pocket | ADR-0025 |
| Actuation | **Dual actuation** (2 points per elevon), no-freeplay linkage, digital servos. Retained for flutter margin even though 390 mm is below the 400 mm rule-of-thumb (ADR-0026, file pending — see OP-22); authority to be confirmed | ADR-0026 |
| Servos | 4× digital 13–15 g, at y ≈ 195 (panel root) and y ≈ 390 (per half), in the panel center cell | PROVISIONAL |
| Hinges | TPU-printed (glued or live-hinge), ADR-0035 | PROVISIONAL |
| Hinge alternative | Polyester (mylar) tape hinges, 25×30 mm, glued in slots — flight-proven on 900–1340 mm printed FPV (Pico Talon, Stallion, I-09) | acceptable if TPU results disappoint; stiffness to be characterized (OP-10) |

### 7.6 CORE (center module) — outer mold constraints

The CORE is the shared, non-reprinted module (ADR-0032). Its outer mold is defined by the
following **binding constraints**; the final body shape is designer's choice within them
(PROVISIONAL until F2 closes — OP-21).

| Constraint | Value | Note |
|---|---|---|
| Spanwise extent | y = 0 → **±195** (30 % half-span) | The wing surface continues across the CORE (same planform and t/c schedule, §5) |
| Centerline section | Root airfoil (c = 289.2 mm, t/c 13.5 %) at y = 0, mid-plane z = 0 | Same airfoil family as the panels (pending OP-02) |
| Trailing edge | **Fixed** from y = 0 to ±195 (no hinge line on the CORE, C23) | The torsion box may run closed to the TE inboard of the panel root (PROVISIONAL) |
| **Nose pod** | Extends **60 mm forward of the root LE** (to x ≈ −132); width ≈ 70 mm; rounded nose; GPS/magnetometer pedestal on top; retention via threaded inserts + printed reinforcement collar against pull-out (I-09 pattern) | Needed so the 6S1P pack CG can reach x ≈ −100 (OP-01 analysis); PROVISIONAL |
| Battery bay | Internal **180 × 70 × 32 mm** (x × y × z); forward end at x ≈ −131.5; centered on y = 0 at z = 0; slide rails along x for pack lengths 42–84 mm; single 21 mm layer, never stacked | §9; PROVISIONAL |
| **Rear pod (motor)** | Extends **48 mm aft of the root TE** (to x ≈ +265); **lower surface at the prop plane ≤ z = −111.6 mm** (≈ 92 mm below the wing lower surface) | Required so the 8×8 prop (Ø203, axis at z = 0) keeps ≥ 10 mm tip ground clearance (C26); PROVISIONAL |
| Motor mount | Face at x ≈ +230; motor body from ≈ +195 to +230 (28-class, 35 mm long, CG ≈ +212); prop disk plane at **x ≈ +235** (≥ 10 mm aft of the root TE at +216.9) | C25; PROVISIONAL |
| Joint sockets | At y = ±195: tube socket Ø12.2–12.4, pin socket Ø6.1–6.2, depth ≈ 70 mm; centerlines x = −9.6 / +55.4 | §7.3 |
| Avionics stations | FC/RX/blackbox ≈ x = 0…+40 (aft of or beside the bay); ESC ≈ x = +60 (rear pod, beside the motor); GPS/mag on the nose pedestal ≈ x = −120 | Matches the §8.1 balance; PROVISIONAL |
| Hand launch | Grip area on the CORE sides; designer's choice within the OML | — |
| Balance tabs | Small printed tabs on the CORE underside to rest the aircraft on a balance edge for CG verification (Pico Talon practice, I-09) | PROVISIONAL |

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
> reachable CG band (**≈ −24…+9 mm** with the 6S1P pack sliding the full v0.2 bay; across
> the four pack configs ≈ −36…+9 mm) does **not** reach the −119 mm target with the current
> planform and masses. The neutral point must be re-verified with an independent method
> (C2, I-07 §7.1) and the body effect (I-07 §6) assessed before the bay position is
> finalized. For v0.2, the bay is placed at the CORE nose (§7.6, OP-19) and the mass
> balance is the driving F2 task. Full analysis in the justification document, §3.1.

---

## 9. Battery and bay

| Parameter | Value | Status |
|---|---|---|
| Cells | Li-Ion **21700**, Ø21 × 70 mm, **single layer** (never stacked) | docs/00 |
| Bay internal dims (x × y × z) | **180 × 70 × 32 mm** | PROVISIONAL |
| Bay position | In the CORE nose pod (§7.6): forward end at x ≈ −131.5, centered on the centerline; see OP-01 | PROVISIONAL |
| Longitudinal adjustment | Pack slide rails along x; range sized to keep CG within ±5 mm for 4S1P, 6S1P, 4S2P, 6S2P | docs/00 R-CG |
| Pack configs | 4S1P ~300 g / 6S1P ~455 g / 4S2P ~605 g / 6S2P ~910 g (out of cruise envelope) | docs/00 |
| Bay height check | 21 mm cells + clearance ≈ 27 mm ≤ 32 mm; root thickness 39 mm at centerline | derived |
| Bay hatch | Spring-loaded lock (Flightory pattern, I-09); threaded inserts + reinforcement collar for repeated opening | PROVISIONAL |

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

> With the prop disk behind the root TE (x ≈ +235), the slipstream does **not** wash the
> wing: the open G5/ADR-0006 question is bounded to the CORE rear-pod wake and the
> elevon inner end at large deflections (I-13).

### 10.2 Motor mount

| Parameter | Value | Status |
|---|---|---|---|
| Location | Integrated in the CORE rear pod, centerline (§7.6) | ADR-0032 |
| Motor axis | At the section mid-plane height (z = 0) | PROVISIONAL |
| Motor station | Mount face x ≈ +230; motor body ≈ +195…+230; prop disk plane at **x ≈ +235** (≥ 10 mm aft of the root TE at +216.9) | PROVISIONAL (C25) |
| Thrust angle | **0.8° up** (upthrust) | PROVISIONAL — Peregrine precedent `[M]`, ADR-0034 |
| Thrust line | Through the CG plane (z = 0) to minimize pitch coupling | PROVISIONAL |
| Prop clearance | Prop disk aft of the root TE; **CORE rear pod lower surface at the prop plane ≤ z = −111.6 mm** (≈ 92 mm below the wing lower surface) so the 8 in (203 mm) prop keeps ≥ 10 mm tip-to-ground clearance (C26) | PROVISIONAL |

---

## 11. Avionics and systems

| Item | Requirement | Source |
|---|---|---|
| Flight controller | INAV 9.1+ or ArduPlane; geometry-agnostic | docs/00 §3.5 |
| **Pitot** | **Mandatory** — without it E2/E7 are invalid; probe at y ≈ 260 mm (40 % half-span) leading edge, out of prop wash. Note: the probe is in the PANEL — its pressure lines cross the CORE↔PANEL joint at y = 195; provide a dedicated channel clear of the tube/pin sockets (PROVISIONAL) | docs/00 (PROVISIONAL position) |
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
3. Insert carbon tube (x/c = 0.25) and anti-rotation pin; **bond both inside the PANEL**
   (y = 195 → 585 for the tube) with continuous adhesive (ADR-0015 §3.3: continuous
   bonding, not housed), leaving ≈ 70 mm protruding at the panel root; the protruding ends
   insert into the CORE sockets **without adhesive** (removable joint).
4. Install elevons with TPU hinges at x/c = 0.72; **mass-balance each elevon** (CG on
   hinge line) before installing servos (ADR-0025).
5. Install 4 servos, zero-freeplay linkage, dual actuation points.
6. Mount motor (0.8° upthrust), ESC, prop; battery on slide rails.
7. Balance: target CG **−119 mm from root c/4** (47 mm forward of root LE); verify in the
   four battery configs (R-CG, ±5 mm) using the CORE underside balance tabs (§7.6).
8. Avionics per §11; pitot, GPS/mag wiring clear of the current path.

---

## 13. Governing references

| Set | Documents |
|---|---|---|
| Decisions | ADR-0001, 0002, 0004, 0007, 0010, 0015, 0021–0028, 0032–0037 ([`decisions/`](../decisions/)) |
| Research | I-01…I-15 ([`research/`](../research/)) |
| Specification | [`docs/00-objectives-and-requirements.md`](../docs/00-objectives-and-requirements.md) |
| Measured data | [`docs/02-measured-references.md`](../docs/02-measured-references.md) |
| Plans | [`docs/03-phase-1-plan.md`](../docs/03-phase-1-plan.md), [`docs/05-master-plan.md`](../docs/05-master-plan.md) |
| Conventions | [`docs/04-conventions.md`](../docs/04-conventions.md) |

> ⚠️ Several ADRs cited above (0003, 0006, 0012, 0023, 0024, 0026, 0030, 0031, 0034,
> 0035) are listed in the decisions index but their **files have not been published**.
> Their values, as used in this guide, are binding for v0.2; the files must be published
> before v1.0 (OP-22).

---

## 14. Revision log

| Version | Date | Change |
|---|---|---|
| 0.2 | 2026-08-05 | Designer-review release. Dihedral defined piecewise (kinks at y = 195/347/498, C22); elevon span corrected to 30–90 % (panel component, C23); print orientation clarified as 45° airfoil roll (C24); motor station and prop-disk position fixed (C25); prop ground-clearance constraint defined (C26); carbon tube/pin physical lengths and socket specs added (C27); new §7.6 CORE outer-mold constraints (nose pod, rear pod, bay, sockets, avionics stations); OP-01 band re-derived (≈ −24…+9 mm, bay-limited); wing-tip treatment declared (OP-20); provisional airfoil coordinate recipe added. **I-09 additions:** E205 tip-airfoil data point (§6.2); mylar hinge alternative (§7.5); CORE balance tabs (§7.6, §12); nose-pod retention pattern and battery-hatch spring lock (§7.6, §9). **I-10…I-14:** threads opened; C28 (root/tip candidates corrected, §6.2/§6.3); stall-margin flag (§4); R-AIRFOIL feasibility flag (§6.1); pusher-slipstream note (§10.1). **I-15:** airfoil evidence campaign opened (11 investigations); root section to be designed, not selected (§6.1 note); **stall-character criterion added (§6.1) and confidence basis of the polar declared (§6.1)**. |
| 0.1 | 2026-08-05 | First release. Reference geometry per I-07/ADR-0027; provisional airfoil (B3 pending), dihedral, twist, carbon, motor, bay. OP-01 flagged. |
