# Salamandra — Design Guide

**Version 0.15** · 6 August 2026 · Status: **RELEASED (tag v0.1.0) — CAD baseline.**
The geometry, structure and integration are frozen for the designer; the values still
flagged `PROVISIONAL` or **PENDING** (airfoil §5, CORE outer shape §6.7) are the only
items expected to change, each with a defined trigger (OP-02, OP-21).

This document is the working specification handed to the **CAD designer**. It defines the
reference configuration (Cruise, Article #1) of the Salamandra modular 3D-printed FPV
aircraft platform with every value needed to model it in Fusion 360 or any other 3D
modeling program. **The guide tells you WHAT to model and WHERE; it does not justify
values** — the why lives in
[`Design-Guide-Justification-v0.1.md`](Design-Guide-Justification-v0.1.md), the open
questions in [`Design-Guide-Open-Points-v0.1.md`](Design-Guide-Open-Points-v0.1.md).

All values are derived from the project's research ([`research/`](../research/)),
decisions ([`decisions/`](../decisions/)) and measured data
([`docs/02-measured-references.md`](../docs/02-measured-references.md)); where data were
missing, the best available assumption was made and is flagged `PROVISIONAL`.

**Directional variants (ADR-0038):** this guide covers the **finless baseline**
(`SALAMANDRA-CLEAN`) and the **fixed-fin variant** (`SALAMANDRA-V1`) — the fin is an
optional CORE component, specified in §4.4. Everything else is identical between the two.

Image-generation prompts (render, blueprint, realistic photo, creative) bound to this
version live in [`prompts/`](prompts/).

---

## 1. Document control

| | |
|---|---|
| Designation | Salamandra — Design Guide |
| Version | 0.15 |
| Date | 2026-08-06 |
| Status | **RELEASED (tag v0.1.0) — CAD baseline**; OP-02 (airfoil) and OP-21 (CORE outer shape) remain open with defined triggers |
| Reference configuration | **Cruise — Article #1** |
| Inputs | ADR-0001…ADR-0039, I-01…I-20, docs/00, docs/02, docs/03, docs/04, docs/05, docs/06, docs/07 |
| Intended reader | CAD designer (Fusion 360 or equivalent) |

**How this guide evolves.** The design is expected to change as Phase 1 closes (airfoil
selection, stability verification) and as the designer iterates. Each published revision
bumps the version number (0.1 → 0.2 → … → 1.0 at first prototype). Revisions are recorded
in §14 of this document and in the [CHANGELOG](../CHANGELOG.md). Values marked
`PROVISIONAL` are the ones most likely to change. The corrections that drove past
revisions (C-series) are in the CHANGELOG.

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

### 2.3 Units and confidence tags

Millimeters and grams in this document. SI in all calculations. Confidence tags per
[`docs/04-conventions.md`](../docs/04-conventions.md): `[M]` measured, `[D]` derived,
`[E]` estimated, `[I]` inferred. **PROVISIONAL** = value assumed because no project datum
exists yet; it will be updated by the open point listed.

---

## 3. Design summary (one-page specification)

| Parameter | Value | Status |
|---|---|---|
| Configuration | Forward-swept tailless flying wing (FSW), modular CORE + PANEL | ADR-0001, ADR-0032 |
| **Directional configuration** | **SALAMANDRA-CLEAN** (finless — O1 efficiency build) **or SALAMANDRA-V1** (fixed centreline fin, no rudder — recommended for the test programme) | **ADR-0038**, I-20; §4.4 |
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
| Geometric twist ε | **+3.0° wash-in** (linear root→tip) — **working value**; target ≈ +0.5° once the designed airfoil closes trim; keep parametric (C5) | PROVISIONAL (§4.3) |
| Dihedral Γ | **2.0° total** (polyhedral at segment joints: 0 / 1.07 / 1.53 / 2.0°) | PROVISIONAL |
| Airfoil | Reflexed; provisional: MH 60-12 % scaled (root 13.5 %, tip 9 % camber-compensated); final pending B3 screening (G2) | **PENDING** — §5 |
| Neutral point NP | **26.7 % MAC** (= −101 mm from root c/4) | `[D]` I-07 · **C2 cross-check −98.3 mm / 28.0 % MAC (Weissinger-L, I-15)** |
| Target CG | **18.7 % MAC** (= −119 mm from root c/4, SM 8 %) | `[D]` I-07; see OP-01 |
| All-up weight (6S1P) | **1697 g** current budget (§7.1); 1620 g design reference (C16) | §7.1 |
| Wing loading (6S1P) | 57 g/dm² (design ref.) / 60 g/dm² (current) | derived |
| Cruise speed / CL | **95 km/h** / CL 0.132 | docs/00, I-07 |
| Stall speed | **≤ 45 km/h required**; ≈ 46.1 km/h at the current budget — the tightest margin (OP-24) | docs/00 (C16), §11 |
| V_NE (article #1) | **160 km/h** (design 180) | docs/00 |
| **V_limit (first flights)** | **110 km/h** (conservative V_div 151.5 × 0.9; ≈ 160 if S3 confirms G_XY ≈ 0.69 GPa) | docs/07, §11 |
| Load factors | +6 / −3 (later +9), gust-dominated | docs/00 |
| Skin / infill | 0.9 mm (2 perimeters) / gyroid 5 % | ADR-0028 |
| Panel carbon | Bending tube Ø12×1.0 + anti-rotation pin Ø6 | PROVISIONAL (ADR-0015), §6.3 |
| **Battery boom (prototype)** | Aluminium tube **Ø8 / int Ø6** + printed cradle, ≈ **41 g**, two-support arrangement | §6.7, §8 |
| Reference propeller | APC-E 8×8 (J_opt 0.784, η 0.731) | ADR-0007 |
| Reference motor | 28-class, 500–550 KV, ~170 g | PROVISIONAL (ADR-0033) |
| Battery (reference) | 6S1P Li-Ion 21700, ~455 g (P42A 90.7 Wh / 50E 108 Wh) | docs/00, I-16 |

---

## 4. Reference planform (Cruise, Article #1)

### 4.1 Overall geometry

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
- Twist: ε = +3.0° wash-in, linear from root (0°) to tip (+3.0°) — **working value, keep
  parametric** (§4.3)
- Dihedral: Γ = 2.0° total at the tip, polyhedral at the segment joints (§4.3)
- Chord distribution: **linear** c(y) = 289.2 − 0.2225·y [mm]
- Wing tips (y = ±650): **flat end caps** closing the section, no winglet in v0.2
  (PROVISIONAL — see OP-20).

### 4.2 Station table (design stations)

All x-values from the root c/4 origin; chord and thickness in mm.

| y (mm) | y/(b/2) | Station | c (mm) | t/c (%) | t (mm) | x_LE (mm) | x_c/4 (mm) | x_TE (mm) |
|---|---|---:|---:|---|---:|---:|---:|---:|
| 0 | 0.00 | Centerline (root) | 289.2 | 13.5 | 39.0 | −72.3 | 0.0 | +216.9 |
| 130 | 0.20 | In-CORE station (fixed TE) | 260.3 | 12.6 | 32.8 | −112.4 | −47.3 | +147.9 |
| 195 | 0.30 | CORE joiner / joint | 245.8 | 12.2 | 29.9 | −132.4 | −71.0 | +113.4 |
| 325 | 0.50 | Mid half-span | 216.9 | 11.3 | 24.4 | −172.5 | −118.3 | +44.4 |
| 347 | 0.53 | Segment cut 1 | 212.0 | 11.1 | 23.5 | −179.3 | −126.3 | +32.7 |
| 487.5 | 0.75 | 75 % half-span | 180.8 | 10.1 | 18.3 | −222.6 | −177.4 | −41.8 |
| 498 | 0.77 | Segment cut 2 | 178.4 | 10.1 | 17.9 | −225.9 | −181.3 | −47.5 |
| 585 | 0.90 | Elevon outer end / spar end | 159.0 | 9.5 | 15.1 | −252.7 | −212.9 | −93.7 |
| 650 | 1.00 | Tip | 144.6 | 9.0 | 13.0 | −272.7 | −236.6 | −128.1 |

### 4.3 Planform control values for CAD

| Control | Value |
|---|---|
| Root chord | 289.2 mm at y = 0, LE at x = −72.3 |
| Tip chord | 144.6 mm at y = 650, LE at x = −272.7 |
| c/4 line | Straight line from (0, 0) to (−236.6, 650); slope −0.3640 (= tan 20°) |
| LE line | Straight line from (−72.3, 0) to (−272.7, 650); slope −0.3084 |
| TE line | Straight line from (+216.9, 0) to (+108.5, 650); slope −0.5308 |
| t/c schedule | Linear: 13.5 % at y = 0 → 9.0 % at y = 650 |
| Twist schedule | Linear: ε = 0° at y = 0 → **+3.0°** at y = 650 (wash-in, trailing edge down); applied as a rotation of each section about the **spanwise axis through the local c/4 point**. **Keep parametric**: the value is re-derived when the airfoil is fixed (C5); with the provisional MH60→13.5 % profile the required wash-in at SM 8 % is 2.6–3.7° (working value 3.0°, residual ≤ 0.6° closed by permanent elevon reflex — `elevon_authority.py` `[D]`); with a designed section (cm0 ≥ +0.008) the target falls to ≈ 0.5°. **R-TWIST cap = 3.0°** (at 3.0° the stall criterion holds: load peak 56 % b/2, margin +0.017; at 4° it drops to +0.009 — `ventana_torsion.py`) |
| Dihedral | **Polyhedral, piecewise-linear**; cumulative at the outboard end of each segment: CORE 0° (y 0–195) / seg 1 +1.07° (195–347) / seg 2 +1.53° (347–498) / seg 3 +2.0° (498–650). Values generated by Γ(y) = 2.0° × (y/650) sampled at the joints. Tip rise ≈ **12 mm** |
| Dihedral — CAD recipe | Each printed segment is modeled **flat** (all its sections in one plane). In the assembly, each segment is rotated about the **chordwise (x) axis — through its inboard joint line, at the section mid-plane (z = 0)** — by its **cumulative** angle (seg 1 +1.07° at y = 195, seg 2 +1.53° at y = 347, seg 3 +2.0° at y = 498). Kinks occur at **every** segment joint (y = 195, 347, 498), including the CORE↔PANEL joint; the CORE stays at 0°. Within a segment the dihedral is constant, not continuous |

### 4.4 Directional variants (ADR-0038, I-20)

The platform publishes **two directional configurations**. They share the planform, the
panels, the elevons, the mass balance, the servos and the flight controller — **the only
difference is an optional fixed centreline fin on the CORE** (no servo, no linkage, no
FC change).

| | **SALAMANDRA-CLEAN** | **SALAMANDRA-V1** |
|---|---|---|
| Vertical stabilizer | **None** | **Fixed centreline fin** (passive) |
| Role | O1 efficiency build (≤ 1.15 Wh/km) | **Recommended build for the Article #1 test programme** |
| Cnβ total | **−0.0006…−0.0015 /deg — negative** (statically unstable yaw `[E]`; FC-stabilized bank-to-turn, documented risk G10) | **+0.0001…+0.0010 /deg nominal +0.0005 (V1a)**; V1b +0.0005…+0.0015 `[D]` on `[E]` bands (I-20) |
| Yaw mode | Divergence τ ≈ 0.7 s `[E]` | Damped subsidence τ ≈ 1.5 s; Cnr doubled `[E]` |
| Fin geometry (V1a) | — | S_v ≈ **2.1 dm²**; trapezoid **b_v ≈ 250 mm, c_r ≈ 105, c_t ≈ 63 mm**, AR_v ≈ 3.0; swept tip; root t ≥ **2.5 mm** solid (σ ≈ 39 MPa, FS 1.29 at V_NE); fin AC ≈ **x = +285 mm** (l_v = 404 mm from CG −119); **rear-pod extension ≈ 30 mm** aft of x ≈ +265 |
| **Fin section (CAD question Q4, answered 2026-08-06)** | **Symmetric biconvex plate** (Mojito-pattern `[M]`): local thickness t_v(y) = 2.5 mm (root) → 1.5 mm (tip), linear; LE radius ≈ 1.5 mm; TE ≈ 0.8 mm; no camber. **Prototype: Ø3 mm Al spar in a Ø3.2 channel along the LE**, root to tip (EI ×2.05, `boom_flexion.py`). Mount: slot in the rear-pod extension (105 mm wide × 3 mm deep) + 1× Ø1.75 mm filament dowel + 1× M2 screw (ADR-0039/Mojito pattern) | — |
| Fin mass | — | **36–60 g** `[E]` (solid 1.2–2.0 mm PETG + mount) |
| Drag / energy | — | ΔCD0 ≈ **+0.0014** → **+9.6 % drag ≈ 1.26 Wh/km** `[E]` (still < Mojito 1.40 `[M]`) |
| V_stall impact | 46.1 km/h (current budget) | +48 g → **46.7 km/h** — OP-24 lever to F2 |
| Rudder | None | **None — not justified** (I-20 §5.4: cannot hold a 20 km/h crosswind slip at stall; bank-to-turn suffices; Mojito precedent `[M]` has no rudder servo) |

Installation (V1): the fin mounts on the rear-pod extension, centreline, in the pusher
slipstream (η ≈ 1.25 — maximum effectiveness at low speed, where launch and stall
handling need it); **1× Ø1.75 mm filament alignment dowel + screw** (ADR-0039 practice,
Mojito pattern `[M]`); optional antenna/ESC housing inside (Mojito pattern `[M]`). The fin is
a **CORE component**: removable, printed separately, no effect on the panels or the
balance table of §7.1 beyond its own mass at x ≈ +285 (≈ 4 mm forward CG shift from
−119 mm — absorbed by the battery slide). Full analysis: I-20, `yaw_stability.py`.

> **Rudder (movable) is rejected in this analysis** and documented as a *future* variant,
> reopened only if the E-flight programme (E8, yaw perturbation) demonstrates a
> yaw-handling failure mode that a surface would fix (I-20 §6, ADR-0038).

---

## 5. Airfoil

**Status: PENDING — G2 (B3 screening). The coordinates below are provisional working
candidates, not the final airfoil.** The profile is the single most likely item to change;
all other geometry is defined independently of the exact profile except the twist value
(§4.3), which is re-derived when the airfoil is fixed (C5).

### 5.1 Design requirements (binding)

| Requirement | Value | Source |
|---|---|---|
| t/c root / tip | **13.5 % / 9 %** (linear) | ADR-0027 |
| Reflex (C_m0) | **≥ +0.008**, target **+0.010…+0.015** | R-AIRFOIL (I-07) |
| C_Lmax (section) | **≥ 0.65** | docs/00, Ananda et al. `[M]` |
| Reynolds range | **Re(MAC) ≈ 3–5×10⁵**; root up to ≈ 5.2×10⁵ at cruise, ≈ 2.5×10⁵ at stall | I-01 |
| Family | Reflexed low-Re flying-wing airfoils | B3 (docs/03) |
| **Stall character** | **Gentle, root-first; no tip stall before the root** — a criterion of the designed section, not a hope: the thickness-separation evidence shows thick sections can transition local → massive separation | I-02, I-15/A5 |
| L/D at cruise CL | As high as possible at CL = 0.132 | B2 |

> Flags (analysis in justification §4, I-15, I-11): **R-AIRFOIL feasibility at 13.5 % t/c
> is an open B3 question** — no published reflexed section reaches that thickness
> (closest: MH 60-12 % at 12.0 %, cm0 +0.0030); the root section is expected to be
> **designed, not selected**. **Trim-closure at SM 8 %:** no off-the-shelf candidate fits
> the torsion window unaided (required wash-in 2.6–3.7° vs R-TWIST ≤ 3.0°); the residual
> ≤ 0.6° is closed by permanent elevon reflex (`elevon_authority.py` `[D]`), or by a
> designed section (cm0 ≥ +0.008) or a reduced SM target (F1).

### 5.2 CAD instructions and provisional coordinates

1. Model the airfoil **parametrically**: t/c = 13.5 % (root) and 9 % (tip) as the driving
   constraints, reflex magnitude per R-AIRFOIL.
2. Keep the airfoil as a **swappable component** (external coordinates file): when B3
   releases the calibrated polar and final coordinates, only the profile and the twist
   setting change. Place the coordinate files under `geometry/` and reference them from
   the CAD model.
3. **Provisional coordinates for the v0.2 CAD** (to be replaced by the B3 output, OP-02):

   | Station | Provisional candidate | Note |
   |---|---|---|
   | Root | **MH 60-12 %** coordinates (aerodesign.de), scaled to t/c = 13.5 % | Closest reflexed family member (12.0 %, cm0 +0.0030 published `[M]`). **MH 45 is 9.85 % thick, not 13 % (C28)** and is documented for 15–40 g/dm², below the project's 57 g/dm² |
   | Tip | **MH 60-12 % thickness-scaled to t/c = 9 % with camber compensation** | Do **not** apply pure affine y-scaling — thinning reflexed sections costs clmax and hardens the stall (MH 45-8 % precedent, I-11). Final tip profile selected in B3 |
   | Reference (not a candidate) | PW51 — in-service FSW airfoil of the Nemesis (I-08) | **Not in the UIUC database** (I-11); coordinates/polars must be sourced elsewhere. **E205 was discarded on its polar** (cm0 ≈ −0.07 at Re 3–5×10⁵, fails R-AIRFOIL by ≈ 0.08 — I-15 §6.2 `[D]`) |

4. The tip station (y = 650) is the thinnest section (13.0 mm max thickness); verifying
   servo and hinge-structure fit there is not required — servos sit inboard (§6.6).

---

## 6. Structure and parts

### 6.1 Component map (what to model)

| Part | Count | Role | Mates with |
|---|---|---|---|
| CORE (centre module) | 1 | Shared, non-reprinted module; avionics, servos, motor pod, boom socket | Panels (removable), boom, fin (V1), motor |
| PANEL — segment 1 | 2 (1/half) | y = 195 → 347, glued | CORE (removable), segment 2 |
| PANEL — segment 2 | 2 (1/half) | y = 347 → 498, glued | Segment 1, segment 3 |
| PANEL — segment 3 | 2 (1/half) | y = 498 → 650, glued | Segment 2 |
| Elevon | 2 (1/half) | Control surface, y = 195 → 585, **separate part** (§6.6) | Panel seat (TPU hinge) |
| Fin (V1, optional) | 1 | Centreline fin, removable CORE component (§4.4) | Rear-pod extension |
| Battery cradle | 2 halves | Wraps pack + boom tube (§8) | Boom tube, pack |
| Skid | 1 | Nose tip crush zone (§6.7) | Boom tip |
| Balance tabs | 2 | CORE underside, CG verification (§6.7) | CORE |

The wing surface is continuous across all parts (same planform and t/c schedule, §4).
The CORE span is y = 0 → ±195; each half-span has 3 segments (cuts at y = 347, 498).
Elevons are **panel components** (no control surface on the CORE — C23).

### 6.2 Cross-section (three cells)

| Cell | Span x/c | Function |
|---|---|---|
| D-box | 0.00 → 0.30 | Closed leading-edge torsion box; houses main spar tube |
| Center cell | 0.30 → 0.72 | Main closed box (Bredt-Batho section); shear web at 0.30 |
| Hinge cell | 0.72 → 1.00 | Elevon structure and hinge line at **0.72 c** |

- Skin: **0.9 mm** (2 perimeters × 0.45 mm), gyroid **5 %** infill throughout
  (ADR-0028). Without infill the skin buckles and the closed section fails (C12).
- Front shear web (D-box web) at **x/c = 0.30** (PROVISIONAL).
- Hinge line at **x/c = 0.72** (ADR-0002): the closed torsion box ends here.

### 6.3 Spars, channels and inserts (ADR-0015 — bending, not torsion)

| Element | Spec | Position | Note |
|---|---|---|---|
| Main spar tube | Pultruded carbon **Ø12 × 1.0 mm**, per panel | At **x/c = 0.25** (the c/4 line), from the CORE joiner (y = 195) to y = 585 | PROVISIONAL sizing; bending only |
| Anti-rotation pin | Solid carbon **Ø6 mm** | **65 mm aft** of the tube axis, in the CORE joiner region | R-JOINT couple; PROVISIONAL |
| Tube spanwise extent | y = 195 → 585 (390 mm) | — | — |
| **Tube physical length** | ≈ **485 mm**: ≈ 415 mm bonded in the panel along the swept c/4 line + ≈ 70 mm protruding into the CORE socket (no adhesive) | — | C27; cut length to be confirmed on the CAD geometry |
| **Tube channel (panel)** | **Straight bore Ø12.4–12.6** in each flat segment, along the segment's local c/4 line; the dihedral kinks (1.07° at y = 195, 0.46° at 347, 0.47° at 498) deviate the tube ≤ 0.19 mm across each joint face — **inside the 0.2–0.3 mm radial clearance** (`boom_flexion.py` §6 `[D]`); no bending needed, the tube is bonded per segment and free in the CORE socket | — | CAD question Q2, answered 2026-08-06 |
| **Pin channel (panel)** | Straight bore **Ø6.3–6.5** along the pin line (65 mm aft of the tube), same clearance rationale | — | — |
| **Pin physical length** | ≈ **140 mm**: ≈ 70 mm bonded in the panel root + ≈ 70 mm protruding into the CORE socket (no adhesive) | — | matches the ≈ 70 mm socket depth |

> Torsion is carried by the closed shell, not the carbon (ADR-0015, C11). The braided
> torsion tube remains documented option B (ADR-0030), not used in v0.2.

### 6.4 Modular joints

- **CORE↔PANEL joint at y = ±195 (30 % half-span)** (ADR-0032):
  - Wing joiner sockets ("muñones") in the CORE: main tube socket + anti-rotation pin
    socket, spaced 65 mm apart. Socket centerlines at the joint face: tube at
    x = −9.6 mm (x/c = 0.25 at that station, on the c/4 line), pin at x = +55.4 mm.
  - Socket bores: tube Ø12.2–12.4 mm, pin Ø6.1–6.2 mm (sliding fit, removable joint),
    depth ≈ 70 mm each.
  - **Removable** (no adhesive): panels swap for Range/Sport configurations. The tube and
    pin are bonded in the PANEL and protrude ≈ 70 mm (tube) / ≈ 70 mm (pin) into the CORE
    sockets.
  - **Pin material is fixed: carbon Ø6** — the filament-pin alternative was evaluated
    and rejected on stiffness (≈ 9000× softer, R-JOINT collapses, −29 % V_div;
    `joint_pin_trade.py`, ADR-0031).
  - R-JOINT: joint torsional stiffness ≥ **5×** the adjacent section (ADR-0032).
- **Segment joints** (within a panel): tenon + PETG adhesive, bond area ≥ **3× the skin
  section** (ADR-0023). Adhesive: 3D-Gloop PETG or 30-min epoxy (I-04; not E6000).
  **Plus 2 × Ø1.75 mm filament dowels per joint** (ADR-0039): alignment during glue
  cure + shear redundancy (FS ≈ 11, `filament_dowel_pins.py` `[D]`); holes Ø1.8–1.9 mm
  at x/c = 0.40/0.60 on the joint face with a solid collar Ø8 × 4 mm; PETG scraps,
  ≈ 2.6 g/aircraft, zero cost.

### 6.5 Segmentation and printing (ADR-0024)

| Item | Value |
|---|---|
| Segments per wing half | **3** (plus the CORE) |
| Segment cuts | y = **347 mm** and **498 mm** (53.3 % / 76.7 % half-span) |
| Segment spans | **152 mm** (y 195–347) · **151 mm** (y 347–498) · **152 mm** (y 498–650) — C24 |
| Print orientation | **45° roll of the airfoil plane about the spanwise axis** (airfoil at 45° to the bed, leading edge low). Footprint: span 152 mm × chord·cos 45° ≈ 174 mm (panel root segment) — fits the 256 mm bed (C24). Do not lay the span axis at 45° in the bed plane: segments 1–2 would need ≈ 280 mm |
| Printer class | 256 mm bed (Bambu P1S class), no active chamber (O3) |
| Material | Conventional PETG, **light color** (ADR-0012, ADR-0021) |
| Profile | 0.4 mm nozzle, 0.2 mm layer, 0.45 mm wall width, **2 perimeters (0.9 mm)**, gyroid **5 %** |
| Flow ratio | **0.95** — never the 0.60 LW-PLA value (docs/02 §1.7) |
| Joint faces | **Dowel holes Ø1.8–1.9 mm with solid collars Ø8 × 4 mm** (4+ perimeters) at x/c 0.40/0.60, both mating faces (ADR-0039) |
| Temperatures | Nozzle 240–250 °C, bed 70–80 °C, fan ≈ 30 % (PETG; PROVISIONAL) |
| Print budget | ≤ 20 h per wing half (O5) |

### 6.6 Elevons

| Parameter | Value | Status |
|---|---|---|
| Hinge line | **x/c = 0.72**, full chord-wise boundary | ADR-0002 |
| Elevon chord | **0.28 c** (constant fraction) | ADR-0002 |
| Elevon span | y = **195 → 585 mm** (30 % → 90 % half-span); length **390 mm**. The elevon is a **PANEL component**: its inner end is the panel root at the CORE↔PANEL joint; the CORE trailing edge is fixed (no control surface on the shared CORE, C23) | PROVISIONAL |
| Travel | ±20° (provisional; authority to be verified, C6) | PROVISIONAL |
| Mass balance | **Mandatory**: elevon assembly CG **on the hinge line**; ~30 g balance mass per elevon in a forward pocket | ADR-0025 |
| Actuation | **Dual actuation** (2 points per elevon), no-freeplay linkage, digital servos. Retained for flutter margin even though 390 mm is below the 400 mm rule-of-thumb (ADR-0026); authority to be confirmed | ADR-0026 |
| Servos | 4× digital **12–15 g metal-gear class** (I-18): Emax ES09MD, Corona DS-939MG, TowerPro MG90S, Savox SH-0255MG+ meet the 60 g budget; the 17–21 g class (TBS Mojito servo, KST DS115MG, MKS DS92A+, JX PDI-1181MG) exceeds it unless the balance allowance is re-allocated | PROVISIONAL; catalog I-18 `[M]` |
| Servo torque | **NOT the binding constraint** (I-18 §2, `servo_torque.py` `[D]`): hinge moment 19–96 mN·m per elevon (Ch 0.01–0.05 `[E]`) → 10–48 mN·m per servo with dual actuation; the most modest catalog servo has ≥ 3.7× margin (≥ 7× dual). Selection is dominated by **stiffness, mass, deadband and price** (ADR-0025) | verified (OP-06 partial) |
| Servo bay cavity | **≈ 34 × 16 × 39 mm** per servo at y ≈ 195 and y ≈ 390 (per half, panel center cell): accepts every servo in the I-18 catalog (largest: KST DS115MG 30×10×35 + ~4 mm/axis); standard mini-servo width ~11–12 mm → one pocket width fits all | I-18 §3.3 `[M]` |
| Servo current | 4 servos: **avg 1.2–2.8 A, peaks 5–9 A** on simultaneous reversal `[M]` (I-18 §5). Covered by the FC Vx BEC (≥ 4.5 A avg); **add capacitance near the servos** (peak alignment can brown-out a tired pack); **dual-actuation balance must be current-measured** (two servos fighting draw ~150 mA extra each, silent) | I-18 §5 `[M]` |
| Hinges | TPU-printed (glued or live-hinge), ADR-0035 | PROVISIONAL |
| **Elevon as a part (CAD question Q3, answered 2026-08-06)** | **Separate component**, modelled solid (skin 0.9 mm, gyroid 5 % by the slicer) from x/c 0.72 to 1.00; **TPU hinge strip 4 × 6 mm × 390 mm** (TPU 95A), glued into the panel seat and the elevon groove (groove **4.2 × 6.2 mm** continuous along x/c 0.72), exterior relief notches every 30 mm; **balance pocket** centred at local x/c 0.74, **40 × 14 × 12 mm**, lid 1× M2, capacity 40 g (lead); the exact balance (elevon CG on the hinge line, ADR-0025) is closed in CAD by the lead amount, not by geometry | ADR-0025/0035 |
| Hinge alternative | Polyester (mylar) tape hinges, 25×30 mm, glued in slots — flight-proven on 900–1340 mm printed FPV (Pico Talon, Stallion, I-09) | acceptable if TPU results disappoint; stiffness to be characterized (OP-10) |

### 6.7 CORE (center module) — outer mold constraints

The CORE is the shared, non-reprinted module (ADR-0032). Its outer mold is defined by the
following **binding constraints**; the final body shape is designer's choice within them
(PROVISIONAL until F2 closes — OP-21).

| Constraint | Value | Note |
|---|---|---|
| Spanwise extent | y = 0 → **±195** (30 % half-span) | The wing surface continues across the CORE (same planform and t/c schedule, §4) |
| Centerline section | Root airfoil (c = 289.2 mm, t/c 13.5 %) at y = 0, mid-plane z = 0 | Same airfoil family as the panels (pending OP-02) |
| Trailing edge | **Fixed** from y = 0 to ±195 (no hinge line on the CORE, C23) | The torsion box may run closed to the TE inboard of the panel root (PROVISIONAL) |
| **Nose boom (battery)** | **PROTOTYPE 0.1 (user decision 2026-08-06):** aluminium tube **Ø8 / int Ø6 (wall 1.0 mm)** as the longitudinal beam from x ≈ −132 to ≈ −516 (≈ 385 mm) + **printed cradle** (≈ 15 g) wrapping the pack and the tube; the pack sits BETWEEN two supports (nose tip ≈ x −516 and the CORE socket ≈ x −132) — **two-support arrangement is a structural requirement** (`boom_flexion.py` `[D]`: pure cantilever FAILS at +6 g — σ 322 MPa vs 276 yield, δ 57 mm, 5.2 Hz; two-support PASSES — σ 60 MPa FS 4.6, δ 2.0 mm, 21 Hz); FPV camera on a short cantilever at the tip (≈ x −450); **printed skid at the tip as the crush zone** (bare tube must not see tip impacts > 3 g); carbon optimisation PENDING (deferred, ADR-0015) | Required so the 6S1P pack CG reaches x ≈ −415 (OP-01 resolution, `balance_cg.py` `[D]`); structure ≈ 41 g (tube 26 + cradle 15, `boom_flexion.py`; OP-24 target 40 + 2 absorbed) |
| **Battery cradle** | **Replaces the internal bay (CAD question Q1, answered 2026-08-06).** Printed cradle, 2 halves, walls 1.2 mm, mass ≤ 15 g: inner envelope **155 × 66 × 24 mm** (pack 153.2 × 64.5 × 22.2, I-16 + 0.5 clearance), length 200 mm from x ≈ −516 to −316, **lower Ø8.2 channel gripping the tube** (the pack rests on the tube; the cradle transmits the load to the two supports); **2× 12 mm velcro straps + spring-lock hatch** (§8 pattern); camera mount (2× M2/16 mm) on the tip support piece | The pack is centred at x ≈ −415 (CG band −434…−397) by the cradle position; PROVISIONAL until F2 |
| **Boom socket (CORE)** | Ø8.2 straight bore in the CORE nose face at x ≈ −132, **centered z = 0** on the centreline, with a 4-perimeter collar; the tube is bonded into the cradle and slips into the socket (no adhesive in the CORE) | — |
| **Rear pod (motor)** | Extends **48 mm aft of the root TE** (to x ≈ +265); **lower surface at the prop plane ≤ z = −111.6 mm** (≈ 92 mm below the wing lower surface) | Required so the 8×8 prop (Ø203, axis at z = 0) keeps ≥ 10 mm tip ground clearance (C26); PROVISIONAL |
| **Fin mount (V1 variant, ADR-0038)** | **Optional** rear-pod extension ≈ 30 mm (to x ≈ +295) with a fixed centreline fin: S_v ≈ 2.1 dm², b_v ≈ 250 mm, c_r 105 / c_t 63 mm (trapezoid, swept tip), root t ≥ 2.5 mm solid, fin AC ≈ +285 mm; no servo, no linkage. **PROTOTYPE 0.1: Ø3 mm aluminium spar along the fin leading edge** (near the TE region, aft stiffener — user decision 2026-08-06): doubles the root stiffness (EI 0.278 + 0.265 N·m², `boom_flexion.py`), load path vs pusher-slipstream buffeting (OP-26), 5.7 g; carbon pending. CORE component — panels untouched | I-20 `[D]`/`[E]`; `yaw_stability.py`; in-service Mojito pattern `[M]`; PROVISIONAL until F2 (flutter, stall arbitration) |
| Motor mount | Face at x ≈ +230; motor body from ≈ +195 to +230 (28-class, 35 mm long, CG ≈ +212); prop disk plane at **x ≈ +235** (≥ 10 mm aft of the root TE at +216.9) | C25; PROVISIONAL |
| Joint sockets | At y = ±195: tube socket Ø12.2–12.4, pin socket Ø6.1–6.2, depth ≈ 70 mm; centerlines x = −9.6 / +55.4 | §6.4 |
| Avionics stations | FC/RX/blackbox ≈ x = 0…+40 (aft of the boom socket); ESC ≈ x = +60 (rear pod, beside the motor); GPS/mag on the nose pedestal ≈ x = −120. **Station cavity 64 × 45 × 21 mm with a 30.5 × 30.5 mm (Φ4 mm) boss/tray** — accepts the entire I-17 catalog (min 28×28×7, avg 45×34×12, max 56×37×13 mm) | Matches the §7.1 balance; PROVISIONAL; I-17 §4.1 `[M]` |
| **FPV camera mount** | In the **nose boom front** (≈ x = −450): 2× M2, **16 mm spacing**, cavity for the DJI O4 camera module **25.55 × 20 × 23.30 mm** (O4/Pro) or **13.44 × 12.36 × 16.50 mm** (Lite); clear forward view (155° FOV); coaxial cable run (130 mm, no bending at the base) to the VTX. **Legacy O3 Air Unit** (I-19 §2.4): camera 21.2 × 20 × 19.5 mm **fits the same cavity**; hole spacing to verify (2× M2/16 mm) before use | I-19 §2/§6 `[M]`; PROVISIONAL |
| **FPV VTX** | DJI O4/Pro transmission module **33.5 × 33.5 × 13 mm** (Lite 30×30×6; **legacy O3 32.5 × 30.5 × 14.5 fits the tray — I-19 §2.4**), tray with **20 × 20 / 25.5 × 25.5 mm M2** holes (Lite: 25.5 only), in the CORE **with airflow** (shell runs hot — do not enclose; thermal pad to the frame); antennas **≥ 5 cm from VTX/camera/carbon/current path**, outside the shell, the two Pro antennas at **90°** | I-19 §2/§3 `[M]`; PROVISIONAL |
| Hand launch | Grip area on the CORE sides; designer's choice within the OML | — |
| Balance tabs | Small printed tabs on the CORE underside to rest the aircraft on a balance edge for CG verification (Pico Talon practice, I-09) | PROVISIONAL |

### 6.8 CAD method and modelling checklist (question Q5, answered 2026-08-06)

The designer has full freedom for the CORE outer shape within the constraints of §6.7.
**Modelling convention:**

1. **Panels and CORE are modelled as solid bodies** of the wing shape; the slicer
   generates the 0.9 mm skin (2 perimeters) and the 5 % gyroid infill (ADR-0028).
2. **The model must include EXPLICITLY** (the slicer will not create them):
   - the D-box web (0.9 mm wall at x/c 0.30);
   - the tube/pin channels (Ø12.4–12.6 / Ø6.3–6.5, §6.3);
   - the dowel holes + solid collars Ø8 × 4 mm (§6.4);
   - the servo bays (§6.6) and the elevon balance pocket;
   - the avionics cavities, the boom socket Ø8.2 and the CORE joint sockets
     (Ø12.2–12.4 / Ø6.1–6.2, depth 70, centers x = −9.6 / +55.4 at z = 0, §6.4).
3. **CORE torsion box**: the closed box runs to the TE inboard of the panel root
   (no hinge line on the CORE, C23) — the centre section has no elevon.
4. **Print orientation is a slicer task** (45° airfoil roll, §6.5): model in
   aircraft coordinates.

### 6.9 Bought-in items and consumables (per aircraft)

| Item | Spec | Use | Source row |
|---|---|---|---|
| Carbon tube | Pultruded Ø12 × 1.0 mm, **2 × ≈ 485 mm** | Main spar, bonded in each panel | §6.3 |
| Carbon pin | Solid Ø6 mm, **2 × ≈ 140 mm** | Anti-rotation couple, bonded in each panel | §6.3 |
| Aluminium boom | Tube **Ø8 / int Ø6** (wall 1.0 mm), ≈ 385 mm | Nose boom, prototype | §6.7 |
| Aluminium spar (V1) | Ø3 mm, ≈ 300 mm | Fin leading edge | §4.4 |
| PETG adhesive | 3D-Gloop PETG or 30-min epoxy (never E6000) | Segment joints (tenon), tube/pin bonding | §6.4 (I-04) |
| TPU hinge strips | TPU 95A, 4 × 6 mm × 390 mm, **2×** | Elevon hinges | §6.6 |
| Velcro straps | 12 mm wide, **2×** | Cradle retention | §6.7/§8 |
| Filament dowels | Ø1.75 mm PETG scraps, **2 per segment joint + 1 (V1 fin)** | Glue alignment + shear redundancy | §6.4 (ADR-0039) |
| Screws | **2× M2×16** (camera), **2× M2** (elevon pocket lids), **1× M2** (fin, V1); threaded inserts for the cradle hatch (pattern I-09, size designer's choice) | Mounting | §6.6/§6.7 |
| Balance mass | Lead, ~30 g per elevon (final amount from CAD balance) | Elevon mass balance (ADR-0025) | §6.6 |
| Filament | Conventional PETG, light colour (printed structure) + TPU 95A (hinges) | Printing | §6.5 (ADR-0012/0021) |
| Motor/prop hardware | Adapter, collet/spinner per the selected 28-class motor | Propulsion mounting | §9.1 |

> The mass-budget "Hardware" row (20 g, §7.1) covers screws, TPU strips and adhesive.

---

## 7. Mass budget and CG

### 7.1 Mass budget (Cruise, 6S1P) — sums to 1697 g AUW

| Component | Mass (g) | Status |
|---|---:|---|
| Printed shell (CORE + 6 segments) | 600 | `[E]` (docs: 550–650) |
| Carbon (tubes + pins) | 70 | `[E]` |
| Motor (28-class) | 170 | `[E]` |
| ESC (6S 30 A) | 35 | `[E]` |
| Avionics (FC, pitot, GPS, RX, wiring) | 110 | `[E]` (I-17: heaviest FC 26 g is 24 % of the allowance) |
| Servos (4 × 15 g) | 60 | `[E]`; I-18: the 12–15 g digital metal-gear class fits (48–60 g); 17–21 g class exceeds |
| Propeller + hub/spinner | 40 | `[E]` |
| Elevon balance mass | 60 | `[E]` (ADR-0025) |
| **FPV DJI O4/Pro (camera + VTX + 2 antennas)** | **37** | `[M]` (I-19: 33 g + 2×2.1 g; Lite 8.2 g; **legacy O3 ≈ 39 g** — 36.4 g + 3 g antenna, I-19 §2.4 `[M]`) |
| **Battery boom structure** | **41** | `[E]` PROTOTYPE: Al tube Ø8/int6 (26 g) + cradle (15 g) (`boom_flexion.py`); carbon optimisation pending (ADR-0015) |
| Hardware (screws, TPU hinges, adhesive, misc) | 20 | `[E]` |
| **Battery 6S1P (21700)** | **455** | `[E]` (I-16: P42A 445 g / 50E 433 g) |
| **Total** | **1697** | **60 g/dm²** |

> **V1 variant (ADR-0038):** + fin 36–60 g `[E]` at x ≈ +285 (I-20) → AUW ≈ 1733–1757 g;
> ≈ 4 mm forward CG shift, absorbed by the battery slide; V_stall 46.7–47.0 km/h —
> OP-24/OP-26 lever to F2. Finless CLEAN budget is the table above.
>
> **Material variants:** per-part mass with PETG / AERO-PLA wings / PLA+ policies in
> `mass_budget.py` (docs/06): ALL PETG 1687 g (I-16 pack `[D]` 445 g, −10 g vs the
> `[E]` 455 row above) · AERO WINGS 1508 g (stall-compliant, **not airworthy under the
> divergence model** — docs/07) · PLA+ 1670 g (ADR-0016 rejected material).

### 7.2 CG target

| Quantity | Value |
|---|---|
| Neutral point | **26.7 % MAC** = −101 mm from root c/4 (VLM `[D]`, I-07); **independent Weissinger-L: 28.0 % MAC = −98.3 mm — 3 mm agreement (I-15 §6.3)**; central-body effect unquantified, moves the NP forward (margin applied in F2) |
| **Target CG** | **18.7 % MAC** = **−119 mm from root c/4** (8 % static margin) |
| CG vs root LE | 47 mm **forward** of the root leading edge |
| R-CG | CG within **±5 mm** of target (reference config 6S1P; other configs do not reach the band — OP-23) |
| Adjustment | **Cradle longitudinal slide** along the boom (see §8); pack stations per config in `balance_cg.py` `[D]`; verify with the CORE underside balance tabs (§6.7) |

> ⚠️ **OP-01 (critical) — resolution adopted (2026-08-05):** the reachable-CG analysis
> (`balance_cg.py` `[D]`) shows the −119 mm target requires the 6S1P pack CG at
> **x ≈ −415 mm** — unreachable with the v0.2 nose pod (reachable band was −24…+9 mm).
> **Adopted: nose boom** carrying the pack from x ≈ −516 (≈ 385 mm forward of the
> nose pod tip), Mojito pattern (I-02). Pack stations: 4S1P −568 / **6S1P −415
> (reference)** / 4S2P −342 / 6S2P −267 (`balance_cg.py` `[D]`). **Fit (I-16 `[D]`): the
> 6S1P pack (153 × 64.5 × 22.2 mm) is the only one that fits the cradle and reaches the
> band; 4S1P needs x ≈ −568 (outside); 4S2P/6S2P do not fit at all — the R-CG
> four-config requirement is re-derived in F2 (OP-23).** The central-body effect moves
> the NP forward — direction known, margin applied in F2. Full analysis: justification
> §3.1–3.2; the boom is part of the CORE outer mold (§6.7).

---

## 8. Battery and cradle

| Parameter | Value | Status |
|---|---|---|
| Cells | Li-Ion **21700**, Ø21 × 70 mm, **single layer** (never stacked) | docs/00 |
| **Cradle (CAD question Q1)** | **Replaces the internal bay.** Printed, 2 halves, walls 1.2 mm, ≤ 15 g: inner envelope **155 × 66 × 24 mm** (pack 153.2 × 64.5 × 22.2 + 0.5 clearance), length 200 mm from x ≈ −516 to −316, **lower Ø8.2 channel gripping the boom tube**; 2× 12 mm velcro straps + spring-lock hatch (Flightory pattern, I-09); camera mount (2× M2/16 mm) on the tip support piece; threaded inserts + reinforcement collar for repeated opening | PROVISIONAL until F2 |
| Cradle position | Centres the pack at **x ≈ −415** (CG band −434…−397), between the two supports (nose tip x ≈ −516 and CORE socket x ≈ −132) — **structural requirement** (§6.7) | `[D]` |
| Longitudinal adjustment | Pack slide along x inside the cradle; range sized to keep CG within ±5 mm (reference 6S1P) | docs/00 R-CG; re-derived in F2 (OP-23) |
| Pack configs | 4S1P ~300 g / 6S1P ~455 g / 4S2P ~605 g / 6S2P ~910 g (out of cruise envelope). Pack stations for CG −119 mm: −568 / **−415** / −342 / −267 (`balance_cg.py` `[D]`, incl. FPV). **Fit (I-16 `[D]`): only the 6S1P pack fits the 155×66×24 single-layer cradle and reaches the band; 4S2P/6S2P fit no n_z = 1 arrangement; 4S1P fits but needs x ≈ −568 (outside the cradle)** | docs/00 |

---

## 9. Propulsion

### 9.1 Reference configuration (recommended, not prescribed — ADR-0033)

| Element | Reference | Basis |
|---|---|---|
| Layout | **Single pusher** at the CORE rear center | PROVISIONAL (ADR-0006 under dispute) |
| Propeller | **APC-E 8×8** — P/D 1.00, η_max 0.731, J_opt 0.784 | ADR-0007, UIUC `[D]` |
| Cruise operating point | ~**9,900 rpm** at 95 km/h (J = 0.784) | derived from J_opt |
| Motor | 28-class (Ø28 mm), **500–550 KV**, ~170 g, ≥ 400 W peak | PROVISIONAL, derived |
| ESC | 6S, **30 A** (cruise ≈ 5 A, peak ≈ 20 A) | derived |
| Alternatives | APC-E 9×6, 10×7 (matching table, D3/D4) | ADR-0007 |
| Battery energy (reference) | 6S1P P42A **90.7 Wh** / 50E **108 Wh** (pack 445/433 g, I-16 §6.1 `[D]`) | I-16; supersedes the docs/00 97 Wh estimate |

> With the prop disk behind the root TE (x ≈ +235), the slipstream does **not** wash the
> wing: the open G5/ADR-0006 question is bounded to the CORE rear-pod wake and the
> elevon inner end at large deflections (I-13).

### 9.2 Motor mount

| Parameter | Value | Status |
|---|---|---|
| Location | Integrated in the CORE rear pod, centerline (§6.7) | ADR-0032 |
| Motor axis | At the section mid-plane height (z = 0) | PROVISIONAL |
| Motor station | Mount face x ≈ +230; motor body ≈ +195…+230; prop disk plane at **x ≈ +235** (≥ 10 mm aft of the root TE at +216.9) | PROVISIONAL (C25) |
| Thrust angle | **0.8° up** (upthrust) | PROVISIONAL — Peregrine precedent `[M]`, ADR-0034 |
| Thrust line | Through the CG plane (z = 0) to minimize pitch coupling | PROVISIONAL |
| Prop clearance | Prop disk aft of the root TE; **CORE rear pod lower surface at the prop plane ≤ z = −111.6 mm** (≈ 92 mm below the wing lower surface) so the 8 in (203 mm) prop keeps ≥ 10 mm tip-to-ground clearance (C26) | PROVISIONAL |

---

## 10. Avionics and systems

| Item | Requirement | Source |
|---|---|---|
| Flight controller | INAV 9.1+ or ArduPilot; geometry-agnostic. **Reference class (I-17 `[M]`):** Matek F405-WING-V2 or SpeedyBee F405 WING (both meet the full requirement set; 30.5 × 30.5 mm mount). Exclusions: F411 class (no blackbox — mandatory), Foxeer F405 V2 (no current input — O1 needs it), **Matek H7A3-WING has no INAV target (ArduPilot only)** | docs/00 §3.5; I-17 §3 |
| **Pitot** | **Mandatory** — without it E2/E7 are invalid; probe at y ≈ 260 mm (40 % half-span) leading edge, out of prop wash. Note: the probe is in the PANEL — its pressure lines cross the CORE↔PANEL joint at y = 195; provide a dedicated channel clear of the tube/pin sockets (PROVISIONAL). Digital MS4525 on I2C (every surveyed board has ≥ 1 I2C) | docs/00; I-17 §5 |
| Blackbox | SD or flash, mandatory | docs/00 |
| GPS / magnetometer | **Out of the root current path** (battery wires); nose pedestal position | docs/00 |
| Launch | Autolaunch via acceleration detection | docs/00 |
| Servos | 4× digital, no freeplay, dual actuation per elevon (§6.6; class and current in I-18) | ADR-0026 |
| Wiring | Current path (ESC→battery) separated from GPS/mag, pitot and FPV runs | docs/00 |
| Avionics power | **≈ 6.6 W** = ≈ 6 % of cruise (5 V rail 300–555 mA vs 2 A BEC; servo rail 1.2–2.8 A avg vs ≥ 4.5 A Vx BEC) → **≈ 7.3 % of the 6S1P P42A pack per flight-hour** (I-17 §6 `[D]`) | I-17 |
| FPV (video) | DJI O4 Air Unit series reference (I-19): O4/Pro (33 g, 7.4–26.4 V) or Lite (8.2 g, 3.7–13.2 V); camera in the nose boom, VTX in the CORE (§6.7). **Legacy O3 Air Unit** (36.4 g, 7.4–26.4 V) fits the mounts — camera hole spacing and measured current pending (I-19 §2.4). **Power:** Pro 7.4–10.4 W (max 1200 mW) — feed from the **9 V/2 A rail (≥ 13.5 W DJI minimum); do NOT power the Pro from the 5 V rail** (10.4 W @ 5 V ≈ 2.1 A > 2 A); O4 Lite fits the 5 V rail (1.2 A, 60 %) | I-19 §4–5 `[M]`/`[D]` |
| Total electronics | Avionics + FPV = **17.0 W with O4 Pro** (15.5 % of cruise; 18.8 % of pack per flight-hour) / 12.6 W with Lite. Fly the lowest usable power level (CE legal limit is 14 dBm, not the FCC number) | I-19 §5 `[D]` |

---

## 11. Flight envelope and limitations

### 11.1 Mission and design envelope

| Requirement | Value | Source |
|---|---|---|
| Design range | 80 km + 20 % reserve (extended 100 km, contingent on E3) | docs/00 |
| Endurance | 60 min at minimum-power speed | docs/00 |
| Cruise speed | 90–105 km/h; design point **95 km/h** | docs/00 |
| V_NE article #1 | **160 km/h** (design V_NE 180) | docs/00 |
| **V_limit (first test flights)** | **110 km/h** (conservative V_div 151.5 × 0.9 joint-aware margin); ≈ 160 km/h if S3 confirms G_XY ≈ 0.69 GPa (210.5 × 0.9) | docs/07, §11.3 |
| Stall speed | **≤ 45 km/h** | docs/00 (C16) |
| Required C_Lmax | ≥ 0.65 | docs/00 |
| n_max / n_min | +6 / −3 (later +9) | docs/00 |
| Launch | Hand launch, autolaunch via acceleration detection | docs/00 |
| Battery configs | 4S1P, 6S1P, 4S2P, 6S2P (21700); 6S2P out of cruise envelope | docs/00 (R-CG) |
| Divergence criterion | V_div ≥ 1.5 × V_NE (= 240 km/h) | docs/00 |

### 11.2 Stall margin (the tightest in the design — OP-24)

> ≈ **46.1 km/h** at the current budget (1697 g, `balance_cg.py` `[D]`) vs the 45 km/h
> requirement — a 0.4–1.1 km/h tension. **Declared levers:** shell at the low end of its
> band (550 g instead of 600) + servos at the real 12–15 g class (48 g instead of 60)
> → AUW ≈ 1625 g → ≈ 45.1 km/h — borderline; F2 must arbitrate the mass budget against
> C16. **(The V1 fin variant adds 36–60 g → 46.7 km/h; §4.4, OP-26.)** Do not relax the
> CL_max chain without re-deriving this requirement (C16 history).

### 11.3 Divergence and V_limit (docs/07, `divergence.py` — G6)

> V_div vs the **240 km/h criterion**: nominal **275.6 km/h (1.15× — PASS, barely)**;
> **conservative end 151.5 km/h (0.63× — FAIL, below V_NE 160)**; AERO LW-PLA wings
> **107.1 km/h (0.45× — not airworthy)**: the ADR-0030 "criterion met" claim is
> **falsified** on the conservative end (OP-29). **Real-print sensitivity:** in-plane
> G_XY 0.69–0.72 GPa (E 1.94 `[M]`, ν 0.35–0.40) → 210.5 km/h; even the combined best
> case (G in-plane + gyroid + wall 1.1 mm) only touches 242 km/h. **Operating rule:**
> V_limit **110 km/h** for first flights (160 if the S3 coupon confirms G_XY ≈ 0.69 GPa);
> levers: 3 perimeters (+22 % V_div, +200 g), I-12 sweep factor, S3 GJ/EI verification
> (mandatory), E7 Southwell in flight. Full analysis: docs/07; OP-29.

### 11.4 Launch envelope (I-14 rev. 2 executed — `launch_speed.py` `[D]`)

> **Hand launch FEASIBLE.** Release gate: **V_suelta ≥ V_stall** (45.9–46.1 km/h) with
> elevon-up attitude — the k = 1.20 margin is built by motor acceleration in < 0.5 s
> (T/W ≈ 1.0). Typical throw (10.5 m/s + ref idle): **48.4 km/h at release, k = 1.20 in
> 0.39 s**; firm throw: **62.4 km/h (k = 1.36)**; a weak 8 m/s throw releases below stall
> (9.8 km/h) — the technique is part of the specification (§12, step 0). Anchored on the
> configuration class `[M]`: the TBS Mojito (1300 mm, 1800 g, higher reported stall) is
> hand-launched in service. **The CL_max chain (R-AIRFOIL, OP-02) stays double-critical:
> it lowers V_stall and raises the release margin.**

Salamandra is a modular platform: this guide specifies the **Cruise** configuration
(1300 mm). The Range (1600 mm) and Sport (1100 mm) configurations share the CORE and
follow the same rules via R-NP ([ADR-0032](../decisions/ADR-0032-modularity.md)); they are
out of scope for this version.

---

## 12. Assembly and control setup

0. **Launch rules (I-14 rev. 2, `launch_speed.py`):** **firm throw (V_hand ≥ 10 m/s),
   release at 0–5° pitch** — the gate is V_suelta ≥ V_stall (45.9 km/h at 1687 g); the
   k = 1.20 margin is reached by motor acceleration in < 0.5 s (typical throw:
   48.4 km/h at release, k = 1.20 in 0.39 s). INAV autolaunch: `nav_fw_launch_thr`
   = hover throttle (bench: nose-up until "about to fly out of your hand"),
   `nav_fw_launch_idle_thr` 1350–1450 (0.5–0.67 × launch, wing-throw band),
   `nav_fw_launch_motor_delay` 200 ms (pusher: never 0), `nav_fw_launch_spinup_time`
   200 ms (8-inch prop), `nav_fw_launch_climb_angle` 18–25°. ArduPlane equivalents:
   `TKOFF_THR_MINACC` 15 m/s², `TKOFF_THR_DELAY` ≥ 0.2 s, `TKOFF_THR_MINSPD` 4 m/s.

1. Print CORE + 6 segments (3 per half) per §6.5. Light-color PETG.
2. Glue segment joints (tenon + adhesive, area ≥ 3× skin section): insert the
   **2 Ø1.75 filament dowels per joint** (adhesive dab on one side, sliding fit on the
   other — alignment during cure, ADR-0039); do **not** glue the CORE↔panel joint.
3. Insert carbon tube (x/c = 0.25) and anti-rotation pin; **bond both inside the PANEL**
   (y = 195 → 585 for the tube) with continuous adhesive (ADR-0015 §3.3: continuous
   bonding, not housed), leaving ≈ 70 mm protruding at the panel root; the protruding ends
   insert into the CORE sockets **without adhesive** (removable joint).
4. Install elevons with TPU hinges at x/c = 0.72; **mass-balance each elevon** (CG on
   hinge line) before installing servos (ADR-0025).
5. Install 4 servos, zero-freeplay linkage, dual actuation points.
6. Mount motor (0.8° upthrust), ESC, prop; battery in the cradle on slide rails; FPV
   camera in the nose boom and VTX on the CORE tray (9 V rail for O4/Pro, §10); antennas
   outside the shell ≥ 5 cm, at 90° (I-19).
7. **(V1 variant only, ADR-0038 §4.4):** install the fixed centreline fin on the
   rear-pod extension (no servo, no linkage, no FC change); optional antenna/ESC housing
   inside the fin (Mojito pattern `[M]`).
8. Balance: target CG **−119 mm from root c/4** (47 mm forward of root LE); verify in the
   **reference 6S1P config** using the CORE underside balance tabs (§6.7); 4S1P/4S2P/6S2P
   do not reach the band in the cradle — see OP-23.
9. Avionics per §10; pitot, GPS/mag wiring clear of the current path.

---

## 13. Governing references

| Set | Documents |
|---|---|
| Decisions | ADR-0001…ADR-0039 ([`decisions/`](../decisions/)) |
| Research | I-01…I-20 ([`research/`](../research/)); **directional stability: I-20** (`yaw_stability.py`); **launch: I-14 executed** (`launch_speed.py`) |
| Specification | [`docs/00-objectives-and-requirements.md`](../docs/00-objectives-and-requirements.md) |
| Measured data | [`docs/02-measured-references.md`](../docs/02-measured-references.md) |
| Plans | [`docs/03-phase-1-plan.md`](../docs/03-phase-1-plan.md), [`docs/05-master-plan.md`](../docs/05-master-plan.md) |
| Conventions | [`docs/04-conventions.md`](../docs/04-conventions.md) |
| Material variants | [`docs/06-material-mass-variants.md`](../docs/06-material-mass-variants.md) (`mass_budget.py`) |
| Divergence | [`docs/07-divergence-margin.md`](../docs/07-divergence-margin.md) (`divergence.py`) |

> ✅ **All ADRs cited in this guide have published files** (OP-22 closed 2026-08-06).

---

## 14. Revision log

| Version | Date | Change |
|---|---|---|
| 0.15 | 2026-08-06 | **First release (tag v0.1.0).** Status → RELEASED (CAD baseline); segment spans added (§6.5, C24); new §6.9 bought-in items and consumables table; the remaining open items are named with their triggers (OP-02 airfoil, OP-21 CORE shape). Release notes: [`docs/08-release-v0.1.md`](../docs/08-release-v0.1.md). |
| 0.14 | 2026-08-06 | **Reorganized as a CAD designer's guide** (§4 geometry → §5 airfoil → §6 structure/parts → §7 mass → §8 battery → §9–10 subsystems → §11 envelope → §12 assembly): component map (§6.1); long analysis notes compressed into one-line flags with pointers to the justification doc and I-docs (no data lost — full rationale remains in `Design-Guide-Justification-v0.1.md` and the CHANGELOG). **Corrections (values reconciled to the canonical scripts):** twist working value +0.5° → **+3.0°** (parametric, C5); divergence numbers updated to docs/07 rev. 2 (nominal 275.6 / conservative 151.5 / AERO 107.1, V_limit 110); the internal battery bay superseded by the cradle throughout (§8); AUW row reconciled (1697 current / 1620 design ref.); assembly step 8 verifies balance in 6S1P only. |
| 0.13 | 2026-08-06 | CAD questions Q1–Q5 answered (cradle replaces the bay; straight channels vs kinks; elevon as a part; biconvex fin; CAD method) — CHANGELOG [1.25] |
| 0.12 | 2026-08-06 | PROTOTYPE 0.1 materials: Al boom Ø8/int6 + cradle, Ø3 fin spar (`boom_flexion.py`) — CHANGELOG [1.24] |
| 0.11 | 2026-08-06 | Launch verdict corrected (I-14 rev. 2: feasible, gate V_suelta ≥ V_stall) — CHANGELOG [1.22] |
| 0.10 | 2026-08-06 | Divergence falsified on the conservative end + launch investigated (v0.10) — CHANGELOG [1.20]–[1.23] |
| 0.9 | 2026-08-06 | Material mass variants tool integrated (docs/06, OP-28) — CHANGELOG [1.19] |
| 0.8 | 2026-08-06 | Filament dowel pins adopted (ADR-0039) — CHANGELOG [1.18] |
| 0.7 | 2026-08-06 | Legacy DJI O3 integrated; all 14 missing ADR files published (OP-22) — CHANGELOG [1.17] |
| 0.6 | 2026-08-06 | Dual directional configuration (ADR-0038, I-20) — CHANGELOG [1.16] |
| 0.5 | 2026-08-05 | Component catalogs integrated (I-16/17/18/19) — CHANGELOG [1.14] |
| 0.4 | 2026-08-05 | Bay re-derived with the real pack envelope (I-16) — CHANGELOG [1.13] |
| 0.3 | 2026-08-05 | OP-01 resolution: battery nose boom; R-TWIST 3.0°; elevon authority verified — CHANGELOG [1.12] |
| 0.2 | 2026-08-05 | Designer-review release (dihedral kinks, elevon span, print orientation, motor station, CORE spec) — CHANGELOG [1.11] |
| 0.1 | 2026-08-05 | First release — CHANGELOG [1.10] |
