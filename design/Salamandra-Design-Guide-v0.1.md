# Salamandra — Design Guide

**Version 0.12** · 6 August 2026 · Status: **DRAFT — for designer review**

This document is the working specification handed to the CAD designer. It defines the
reference configuration (Cruise, Article #1) of the Salamandra modular 3D-printed FPV
aircraft platform with every value needed to model it in Fusion 360 or any other 3D
modeling program. All values are derived from the project's research
([`research/`](../research/)), decisions ([`decisions/`](../decisions/)) and measured data
([`docs/02-measured-references.md`](../docs/02-measured-references.md)); where data were
missing, the best available assumption was made and is flagged `PROVISIONAL`.

**Directional variants (ADR-0038):** this guide covers the **finless baseline**
(`SALAMANDRA-CLEAN`) and the **fixed-fin variant** (`SALAMANDRA-V1`) — the fin is an
optional CORE component, specified in §5.4. Everything else is identical between the two.

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
| Version | 0.12 |
| Date | 2026-08-06 |
| Status | DRAFT — pending designer iteration and Phase 1 closure |
| Reference configuration | **Cruise — Article #1** |
| Inputs | ADR-0001…ADR-0038, I-01…I-20, docs/00, docs/02, docs/03, docs/04, docs/05 |
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
| **Directional configuration** | **SALAMANDRA-CLEAN** (finless — O1 efficiency build) **or SALAMANDRA-V1** (fixed centreline fin, no rudder — recommended for the test programme) | **ADR-0038**, I-20; §5.4 |
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
| Geometric twist ε | **+0.5° wash-in** (linear root→tip) | PROVISIONAL (R-TWIST ≤ 3.0°, §5.3) |
| Dihedral Γ | **2.0° total** (polyhedral at segment joints) | PROVISIONAL |
| Airfoil | Reflexed; root/tip candidates pending B3 screening (G2) | **PENDING** — §6 |
| Neutral point NP | **26.7 % MAC** (= −101 mm from root c/4) | `[D]` I-07 · **C2 cross-check −98.3 mm / 28.0 % MAC (Weissinger-L, I-15)** |
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
> 45 km/h requirement — a 0.4 km/h margin (I-07 §4.2). The OP-01 boom (40 g) and the FPV
> unit (37 g, I-19) add mass: AUW 1697 g → V_stall ≈ **46.1 km/h** at the current budget
> (balance_cg.py `[D]`). **Declared levers:** shell at the low end of its band (550 g
> instead of 600) + boom ≤ 40 g + servos at the real 12–15 g class (48 g instead of 60)
> → AUW ≈ 1625 g → ≈ 45.1 km/h — borderline; F2 must arbitrate the mass budget against
> C16 (OP-24). **(The V1 fin variant adds 36–60 g → 46.7 km/h at the current budget;
> §5.4, OP-26.)** The launch is a mandatory hand throw; launch-speed feasibility is under
> investigation (I-14). Do not relax the CL_max chain without re-deriving this
> requirement (C16 history).
>
> 🚀 **Launch envelope (I-14 executed 2026-08-06, rev. 2 — `launch_speed.py` `[D]`):**
> **hand launch FEASIBLE.** Release gate: V_suelta ≥ V_stall (45.9 km/h at 1687 g) with
> elevon-up attitude — the k = 1.20 margin is built by motor acceleration in < 0.5 s
> (T/W ≈ 1.0). Typical throw (10.5 m/s + ref idle): **48.4 km/h at release, k = 1.20 in
> 0.39 s**; firm throw: 62.4 km/h (k = 1.36). Technique rule: firm throw (V_hand ≥
> 10 m/s), 0–5° pitch (higher → stall), launch throttle at the hover setting. Anchored
> on the configuration class `[M]`: the TBS Mojito (1300 mm, 1800 g, higher reported
> stall) is hand-launched in service. **Launch lever: CL_max chain (R-AIRFOIL, OP-02)
> stays double-critical for comfort — lowers V_stall and raises the release margin.**

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

> **Twist setting (C5 preview, I-15 §6.2):** the +0.5° value is the provisional placeholder.
> **R-TWIST raised to 3.0° (OP-01 resolution pass, 2026-08-05, `[D]`):** at 3.0° the stall
> criterion still holds — load peak at 56 % b/2, margin +0.017, same as at 0° (at 4° it
> drops to +0.009; `ventana_torsion.py`), and the B3 screening shows the required wash-in
> at SM 8 % is 2.6–3.7° (MH60→13.5 %). With ε = 3.0°, the worst-case residual trim is
> ≈ **0.6° of permanent elevon reflex** — elevon yield 0.00348 °/° over the 30–90 % span,
> 10° ≈ 4.8× the trim requirement (`elevon_authority.py` `[D]`); in-service practice
> (I-08). The twist is re-derived when the airfoil is fixed (C5); keep it **parametric**
> in CAD. Options that remove the reflex entirely: a designed section with cm0 ≥ +0.008
> at Re 4–5×10⁵, or a reduced static-margin target (F1).

> **Dihedral — exact CAD recipe (PROVISIONAL, C22).** Each printed segment is modeled
> **flat** (all its sections in one plane). In the assembly, each segment is rotated about
> the chordwise (x) axis — through its inboard joint line, at the section mid-plane
> (z = 0) — by its **cumulative** dihedral angle: segment 1 +1.07° at y = 195, segment 2
> +1.53° at y = 347, segment 3 +2.0° at y = 498. Kinks occur at **every** segment joint
> (y = 195, 347, 498), including the CORE↔PANEL joint; the CORE stays at 0°. Tip rise
> ≈ **12 mm**. The joint values are generated by Γ(y) = 2.0° × (y/650) sampled at the
> joints; within a segment the dihedral is constant, not continuous.

### 5.4 Directional variants (ADR-0038, I-20)

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
| Fin mass | — | **36–60 g** `[E]` (solid 1.2–2.0 mm PETG + mount) |
| Drag / energy | — | ΔCD0 ≈ **+0.0014** → **+9.6 % drag ≈ 1.26 Wh/km** `[E]` (still < Mojito 1.40 `[M]`) |
| V_stall impact | 46.1 km/h (current budget) | +48 g → **46.7 km/h** — OP-24 lever to F2 |
| Rudder | None | **None — not justified** (I-20 §5.4: cannot hold a 20 km/h crosswind slip at stall; bank-to-turn suffices; Mojito precedent `[M]` has no rudder servo) |

Installation (V1): the fin mounts on the rear-pod extension, centreline, in the pusher
slipstream (η ≈ 1.25 — maximum effectiveness at low speed, where launch and stall
handling need it); **1× Ø1.75 mm filament alignment dowel + screw** (ADR-0039 practice,
Mojito pattern `[M]`); optional antenna/ESC housing inside (Mojito pattern `[M]`). The fin is
a **CORE component**: removable, printed separately, no effect on the panels or the
balance table of §8.1 beyond its own mass at x ≈ +285 (≈ 4 mm forward CG shift from
−119 mm — absorbed by the battery slide). Full analysis: I-20, `yaw_stability.py`.

> **Rudder (movable) is rejected in this analysis** and documented as a *future* variant,
> reopened only if the E-flight programme (E8, yaw perturbation) demonstrates a
> yaw-handling failure mode that a surface would fix (I-20 §6, ADR-0038).

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
>
> **Trim-closure result (I-15 §6.2, `[D]`):** at SM 8 % (Cm0_req = 0.01056) **no
> off-the-shelf candidate fits the torsion window unaided**: required wash-in = 2.6–3.7°
> (MH60→13.5 %), 4.2–6.3° (MH60→12 %), ≥ 6.5° (S5010), ≈ 22° (E205) vs R-TWIST ≤ 3.0°
> (raised from 2.5° in the OP-01 pass, §5.3). With ε = 3.0° the residual is ≤ 0.6° of
> **permanent elevon reflex** (authority verified, `elevon_authority.py` `[D]`). A
> designed section (cm0 ≥ +0.008 at Re 4–5×10⁵) or a reduced SM target are the remaining
> closure paths.

### 6.2 Provisional candidates for the v0.2 CAD

| Station | Provisional candidate | Note |
|---|---|---|
| Root | Reflexed section scaled to t/c 13.5 % — **MH 60-12 %** (12.0 %, cm0 +0.0030 published `[M]`) is the closest family member; **MH 45 is 9.85 % thick, not 13 % (C28)** and is documented for 15–40 g/dm², below the project's 57 g/dm² | B3 candidate. Screening `[D]` (I-15): MH60→13.5 % gives cm0 = **+0.0016 at Re 5e5/Ncrit 10** (−0.0018 at Ncrit 12) — the published +0.0030 is not achieved at project Re; no off-the-shelf reflexed section reaches 13.5 % — R-AIRFOIL feasibility at 13.5 % is an explicit B3 question (I-11) |
| Tip | Reflexed section at t/c 9 % with **camber compensation** — pure thickness scaling of a reflexed section is warned against (MH 45-8 % precedent: clmax loss, harsh stall `[M]`, I-11) | 9 % reflexed candidates are scarce; selection resolved in B3 |
| Tip (data point) | **E205** (t/c 10.6 %, camber 2.9 %, flight-proven at Re 1.5–3×10⁵ on the Pico Talon and Stallion, I-09) | **DISCARDED on its polar (I-15 §6.2, `[D]`):** cm0 ≈ −0.07 at Re 3–5×10⁵ (fails R-AIRFOIL by ≈ 0.08; ≈ 22° of wash-in would be needed). Not a candidate for any station |
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
| Joint faces | **Dowel holes Ø1.8–1.9 mm with solid collars Ø8 × 4 mm** (4+ perimeters) at x/c 0.40/0.60, both mating faces (ADR-0039) |
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
| Servos | 4× digital **12–15 g metal-gear class** (I-18): Emax ES09MD, Corona DS-939MG, TowerPro MG90S, Savox SH-0255MG+ meet the 60 g budget; the 17–21 g class (TBS Mojito servo, KST DS115MG, MKS DS92A+, JX PDI-1181MG) exceeds it unless the balance allowance is re-allocated | PROVISIONAL; catalog I-18 `[M]` |
| Servo torque | **NOT the binding constraint** (I-18 §2, `servo_torque.py` `[D]`): hinge moment 19–96 mN·m per elevon (Ch 0.01–0.05 `[E]`) → 10–48 mN·m per servo with dual actuation; the most modest catalog servo has ≥ 3.7× margin (≥ 7× dual). Selection is dominated by **stiffness, mass, deadband and price** (ADR-0025) | verified (OP-06 partial) |
| Servo bay cavity | **≈ 34 × 16 × 39 mm** per servo at y ≈ 195 and y ≈ 390 (per half, panel center cell): accepts every servo in the I-18 catalog (largest: KST DS115MG 30×10×35 + ~4 mm/axis); standard mini-servo width ~11–12 mm → one pocket width fits all | I-18 §3.3 `[M]` |
| Servo current | 4 servos: **avg 1.2–2.8 A, peaks 5–9 A** on simultaneous reversal `[M]` (I-18 §5). Covered by the FC Vx BEC (≥ 4.5 A avg); **add capacitance near the servos** (peak alignment can brown-out a tired pack); **dual-actuation balance must be current-measured** (two servos fighting draw ~150 mA extra each, silent) | I-18 §5 `[M]` |
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
| **Nose boom (battery)** | **PROTOTYPE 0.1 (user decision 2026-08-06):** aluminium tube **Ø8 / int Ø6 (wall 1.0 mm)** as the longitudinal beam from x ≈ −132 to ≈ −516 (≈ 385 mm) + **printed cradle** (≈ 15 g) wrapping the pack and the tube; the pack sits BETWEEN two supports (nose tip ≈ x −516 and the CORE socket ≈ x −132) — **two-support arrangement is a structural requirement** (`boom_flexion.py` `[D]`: pure cantilever FAILS at +6 g — σ 322 MPa vs 276 yield, δ 57 mm, 5.2 Hz; two-support PASSES — σ 60 MPa FS 4.6, δ 2.0 mm, 21 Hz); FPV camera on a short cantilever at the tip (≈ x −450); **printed skid at the tip as the crush zone** (bare tube must not see tip impacts > 3 g); carbon optimisation PENDING (deferred, ADR-0015) | Required so the 6S1P pack CG reaches x ≈ −415 (OP-01 resolution, `balance_cg.py` `[D]`, bay re-derived with the real pack envelope of I-16); structure ≈ 41 g (tube 26 + cradle 15, `boom_flexion.py`; OP-24 target 40 + 2 absorbed) |
| Battery bay | Internal **200 × 70 × 32 mm** (x × y × z); forward end at x ≈ −516; centered on y = 0 at z = 0; slide rails along x; single 21 mm layer, never stacked | Sized for the 6S1P pack (153 × 64.5 × 22.2 mm, I-16 `[D]`) CG band **−434…−397 mm** (R-CG ±5 mm). **Only 6S1P fits and reaches the band**: 4S1P needs x ≈ −568 (outside the bay); 4S2P/6S2P do **not fit** the single-layer bay at all (I-16) — R-CG requirement re-derived in F2 (OP-23); §9; PROVISIONAL |
| **Rear pod (motor)** | Extends **48 mm aft of the root TE** (to x ≈ +265); **lower surface at the prop plane ≤ z = −111.6 mm** (≈ 92 mm below the wing lower surface) | Required so the 8×8 prop (Ø203, axis at z = 0) keeps ≥ 10 mm tip ground clearance (C26); PROVISIONAL |
| **Fin mount (V1 variant, ADR-0038)** | **Optional** rear-pod extension ≈ 30 mm (to x ≈ +295) with a fixed centreline fin: S_v ≈ 2.1 dm², b_v ≈ 250 mm, c_r 105 / c_t 63 mm (trapezoid, swept tip), root t ≥ 2.5 mm solid, fin AC ≈ +285 mm; no servo, no linkage. **PROTOTYPE 0.1: Ø3 mm aluminium spar along the fin leading edge** (near the TE region, aft stiffener — user decision 2026-08-06): doubles the root stiffness (EI 0.278 + 0.265 N·m², `boom_flexion.py`), load path vs pusher-slipstream buffeting (OP-26), 5.7 g; carbon pending. CORE component — panels untouched | I-20 `[D]`/`[E]`; `yaw_stability.py`; in-service Mojito pattern `[M]`; PROVISIONAL until F2 (flutter, stall arbitration) |
| Motor mount | Face at x ≈ +230; motor body from ≈ +195 to +230 (28-class, 35 mm long, CG ≈ +212); prop disk plane at **x ≈ +235** (≥ 10 mm aft of the root TE at +216.9) | C25; PROVISIONAL |
| Joint sockets | At y = ±195: tube socket Ø12.2–12.4, pin socket Ø6.1–6.2, depth ≈ 70 mm; centerlines x = −9.6 / +55.4 | §7.3 |
| Avionics stations | FC/RX/blackbox ≈ x = 0…+40 (aft of or beside the bay); ESC ≈ x = +60 (rear pod, beside the motor); GPS/mag on the nose pedestal ≈ x = −120. **Station cavity 64 × 45 × 21 mm with a 30.5 × 30.5 mm (Φ4 mm) boss/tray** — accepts the entire I-17 catalog (min 28×28×7, avg 45×34×12, max 56×37×13 mm) | Matches the §8.1 balance; PROVISIONAL; I-17 §4.1 `[M]` |
| **FPV camera mount** | In the **nose boom front** (≈ x = −450): 2× M2, **16 mm spacing**, cavity for the DJI O4 camera module **25.55 × 20 × 23.30 mm** (O4/Pro) or **13.44 × 12.36 × 16.50 mm** (Lite); clear forward view (155° FOV); coaxial cable run (130 mm, no bending at the base) to the VTX. **Legacy O3 Air Unit** (I-19 §2.4): camera 21.2 × 20 × 19.5 mm **fits the same cavity**; hole spacing to verify (2× M2/16 mm) before use | I-19 §2/§6 `[M]`; PROVISIONAL |
| **FPV VTX** | DJI O4/Pro transmission module **33.5 × 33.5 × 13 mm** (Lite 30×30×6; **legacy O3 32.5 × 30.5 × 14.5 fits the tray — I-19 §2.4**), tray with **20 × 20 / 25.5 × 25.5 mm M2** holes (Lite: 25.5 only), in the CORE **with airflow** (shell runs hot — do not enclose; thermal pad to the frame); antennas **≥ 5 cm from VTX/camera/carbon/current path**, outside the shell, the two Pro antennas at **90°** | I-19 §2/§3 `[M]`; PROVISIONAL |
| Hand launch | Grip area on the CORE sides; designer's choice within the OML | — |
| Balance tabs | Small printed tabs on the CORE underside to rest the aircraft on a balance edge for CG verification (Pico Talon practice, I-09) | PROVISIONAL |

---

## 8. Mass budget and CG

### 8.1 Mass budget (Cruise, 6S1P) — sums to 1697 g AUW

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
> `[E]` 455 row above) · AERO WINGS 1508 g (stall-compliant, conditional on the
> divergence re-check, OP-28) · PLA+ 1670 g (ADR-0016 rejected material).

### 8.2 CG target

| Quantity | Value |
|---|---|
| Neutral point | **26.7 % MAC** = −101 mm from root c/4 (VLM `[D]`, I-07); **independent Weissinger-L: 28.0 % MAC = −98.3 mm — 3 mm agreement (I-15 §6.3)**; central-body effect unquantified, moves the NP forward (margin applied in F2) |
| **Target CG** | **18.7 % MAC** = **−119 mm from root c/4** (8 % static margin) |
| CG vs root LE | 47 mm **forward** of the root leading edge |
| R-CG | CG within **±5 mm** of target (reference config 6S1P; 4S2P also in bay; 4S1P/6S2P outside — see OP-23) |
| Adjustment | Battery bay longitudinal slide (see §9); pack stations per config in `balance_cg.py` `[D]` |

> ⚠️ **OP-01 (critical) — resolution adopted (2026-08-05):** the reachable-CG analysis
> (`balance_cg.py` `[D]`) shows the −119 mm target requires the 6S1P pack CG at
> **x ≈ −415 mm** — unreachable with the v0.2 nose pod (reachable band was −24…+9 mm).
> **Adopted: nose boom** carrying the battery bay from x ≈ −516 (≈ 385 mm forward of the
> nose pod tip), Mojito pattern (I-02). Pack stations: 4S1P −568 / **6S1P −415
> (reference)** / 4S2P −342 / 6S2P −267. **Bay fit (I-16 `[D]`): the 6S1P pack
> (153 × 64.5 × 22.2 mm) is the only one that fits the single-layer bay and reaches the
> band; 4S1P needs x ≈ −568 (outside); 4S2P/6S2P do not fit at all — the R-CG
> four-config requirement is re-derived in F2 (OP-23).** The central-body effect moves
> the NP forward — direction known, margin applied in F2. Full analysis: justification
> §3.1–3.2; the boom is part of the CORE outer mold (§7.6).

---

## 9. Battery and bay

| Parameter | Value | Status |
|---|---|---|
| Cells | Li-Ion **21700**, Ø21 × 70 mm, **single layer** (never stacked) | docs/00 |
| Bay internal dims (x × y × z) | **200 × 70 × 32 mm** | PROVISIONAL |
| Bay position | In the CORE nose boom (§7.6): forward end at x ≈ −516; sized for the 6S1P pack CG band −434…−397; see OP-01 | PROVISIONAL |
| Longitudinal adjustment | Pack slide rails along x; range sized to keep CG within ±5 mm (reference 6S1P) | docs/00 R-CG; re-derived in F2 (OP-23) |
| Pack configs | 4S1P ~300 g / 6S1P ~455 g / 4S2P ~605 g / 6S2P ~910 g (out of cruise envelope). Pack stations for CG −119 mm: −568 / **−415** / −342 / −267 (`balance_cg.py` `[D]`, incl. FPV). **Bay fit (I-16 `[D]`): only the 6S1P pack (153 × 64.5 × 22.2 mm) fits the 200×70×32 single-layer bay; 4S2P/6S2P fit no n_z = 1 arrangement; 4S1P fits but needs x ≈ −568 (outside the bay)** | docs/00 |
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
| Battery energy (reference) | 6S1P P42A **90.7 Wh** / 50E **108 Wh** (pack 445/433 g, I-16 §6.1 `[D]`) | I-16; supersedes the docs/00 97 Wh estimate |

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
| Flight controller | INAV 9.1+ or ArduPilot; geometry-agnostic. **Reference class (I-17 `[M]`):** Matek F405-WING-V2 or SpeedyBee F405 WING (both meet the full requirement set; 30.5 × 30.5 mm mount). Exclusions: F411 class (no blackbox — mandatory), Foxeer F405 V2 (no current input — O1 needs it), **Matek H7A3-WING has no INAV target (ArduPilot only)** | docs/00 §3.5; I-17 §3 |
| **Pitot** | **Mandatory** — without it E2/E7 are invalid; probe at y ≈ 260 mm (40 % half-span) leading edge, out of prop wash. Note: the probe is in the PANEL — its pressure lines cross the CORE↔PANEL joint at y = 195; provide a dedicated channel clear of the tube/pin sockets (PROVISIONAL). Digital MS4525 on I2C (every surveyed board has ≥ 1 I2C) | docs/00; I-17 §5 |
| Blackbox | SD or flash, mandatory | docs/00 |
| GPS / magnetometer | **Out of the root current path** (battery wires); nose pedestal position | docs/00 |
| Launch | Autolaunch via acceleration detection | docs/00 |
| Servos | 4× digital, no freeplay, dual actuation per elevon (§7.5; class and current in I-18) | ADR-0026 |
| Wiring | Current path (ESC→battery) separated from GPS/mag, pitot and FPV runs | docs/00 |
| Avionics power | **≈ 6.6 W** = ≈ 6 % of cruise (5 V rail 300–555 mA vs 2 A BEC; servo rail 1.2–2.8 A avg vs ≥ 4.5 A Vx BEC) → **≈ 7.3 % of the 6S1P P42A pack per flight-hour** (I-17 §6 `[D]`) | I-17 |
| FPV (video) | DJI O4 Air Unit series reference (I-19): O4/Pro (33 g, 7.4–26.4 V) or Lite (8.2 g, 3.7–13.2 V); camera in the nose boom, VTX in the CORE (§7.6). **Legacy O3 Air Unit** (36.4 g, 7.4–26.4 V) fits the mounts — camera hole spacing and measured current pending (I-19 §2.4). **Power:** Pro 7.4–10.4 W (max 1200 mW) — feed from the **9 V/2 A rail (≥ 13.5 W DJI minimum); do NOT power the Pro from the 5 V rail** (10.4 W @ 5 V ≈ 2.1 A > 2 A); O4 Lite fits the 5 V rail (1.2 A, 60 %) | I-19 §4–5 `[M]`/`[D]` |
| Total electronics | Avionics + FPV = **17.0 W with O4 Pro** (15.5 % of cruise; 18.8 % of pack per flight-hour) / 12.6 W with Lite. Fly the lowest usable power level (CE legal limit is 14 dBm, not the FCC number) | I-19 §5 `[D]` |

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

1. Print CORE + 6 segments (3 per half) per §7.4. Light-color PETG.
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
6. Mount motor (0.8° upthrust), ESC, prop; battery on slide rails; FPV camera in the
   nose boom and VTX on the CORE tray (9 V rail for O4/Pro, §11); antennas outside the
   shell ≥ 5 cm, at 90° (I-19).
7. **(V1 variant only, ADR-0038 §5.4):** install the fixed centreline fin on the
   rear-pod extension (no servo, no linkage, no FC change); optional antenna/ESC housing
   inside the fin (Mojito pattern `[M]`).
8. Balance: target CG **−119 mm from root c/4** (47 mm forward of root LE); verify in the
   **reference 6S1P config** (and 4S2P) using the CORE underside balance tabs (§7.6);
   4S1P/6S2P fall outside the bay band — see OP-23.
9. Avionics per §11; pitot, GPS/mag wiring clear of the current path.

---

## 13. Governing references

| Set | Documents |
|---|---|
| Decisions | ADR-0001, 0002, 0004, 0007, 0010, 0015, 0021–0028, 0031–0039 ([`decisions/`](../decisions/)) |
| Research | I-01…I-20 ([`research/`](../research/)); **directional stability: I-20** (`yaw_stability.py`); **launch: I-14 executed** (`launch_speed.py`); **divergence: docs/07** (`divergence.py`) |
| Specification | [`docs/00-objectives-and-requirements.md`](../docs/00-objectives-and-requirements.md) |
| Measured data | [`docs/02-measured-references.md`](../docs/02-measured-references.md) |
| Plans | [`docs/03-phase-1-plan.md`](../docs/03-phase-1-plan.md), [`docs/05-master-plan.md`](../docs/05-master-plan.md) |
| Conventions | [`docs/04-conventions.md`](../docs/04-conventions.md) |

> ✅ **All ADRs cited in this guide now have published files** (0003, 0006, 0012, 0023,
> 0024, 0026, 0030, 0031, 0034, 0035 published 2026-08-06 — OP-22 closed).

---

## 14. Revision log

| Version | Date | Change |
|---|---|---|
| 0.12 | 2026-08-06 | **PROTOTYPE 0.1 materials (user decision):** nose boom = aluminium Ø8/int6 tube + printed cradle, two-support arrangement (boom_flexion.py: cantilever rejected — σ 322 MPa/δ 57 mm/5.2 Hz; two-support PASS — σ 60 MPa/δ 2.0 mm/21 Hz; ≈ 41 g); V1 fin + rear pod get an Ø3 aluminium spar near the TE (root stiffness ×2.05, 5.7 g); carbon optimisation deferred (ADR-0015). §7.6/§7.2/§5.4/§8.1 updated. |
| 0.11 | 2026-08-06 | **Launch verdict corrected (I-14 rev. 2):** hand launch **FEASIBLE** — release gate is V_suelta ≥ V_stall (not k=1.20 at the release instant, which rev. 1 wrongly demanded); typical throw 48.4 km/h at release (k=1.05), k=1.20 in 0.39 s; anchored on the Mojito configuration class `[M]` (heavier, higher reported stall, hand-launched in service) and published throwing biomechanics (van den Tillaar 2004). §4/§12 envelope updated. |
| 0.10 | 2026-08-06 | **Two weakest links closed with calculations: (1) absolute divergence (docs/07, `divergence.py`) — nominal 267.7 km/h (1.12×, barely PASS), conservative end 121.9 km/h (**FAIL** vs 240): ADR-0030's "criterion met" falsified, V_limit 110 km/h until S3/I-12/E7, OP-29; (2) hand launch (I-14 executed, `launch_speed.py`) — release ≥ 1.20 × V_stall at 0–5° pitch, typical throw releases BELOW stall (44.5 vs 45.9 km/h): launch envelope added to §4/§12 with INAV/ArduPlane autolaunch settings.** |
| 0.9 | 2026-08-06 | **Material mass variants tool integrated (§8.1 note, OP-28):** `mass_budget.py` — per-part materials (PETG / AERO-PLA wings / PLA+), battery 4S–6S × P42A/50E (I-16 `[D]` pack model: baseline 1687 g, −10 g vs the `[E]` 455 g row), FC (I-17), FPV (I-19), motor/prop/servo options, V1 fin; results in docs/06. |
| 0.8 | 2026-08-06 | **Filament dowel pins adopted (ADR-0039):** 2 × Ø1.75 mm filament per glued segment joint (alignment + shear redundancy, FS ≈ 11 `[D]`); holes Ø1.8–1.9 at x/c 0.40/0.60 with solid collars Ø8×4 (§7.3/§7.4/§12); fin root +1 dowel (§5.4); 2.6 g/aircraft, zero cost. Carbon Ø6 pin of the torque couple unchanged (pin-material trade, ADR-0031). |
| 0.7 | 2026-08-06 | **Legacy DJI O3 Air Unit integrated (I-19 §2.4 `[M]`):** camera 21.2×20×19.5 mm fits the §7.6 cavity, module 32.5×30.5×14.5 fits the VTX tray, mass ≈ 39 g (§8.1 note); **all 14 missing ADR files published** (OP-22 closed) and referenced in §13; guide v0.7. |
| 0.6 | 2026-08-06 | **Dual directional configuration (ADR-0038, I-20):** optional fixed centreline fin registered in §7.6 (rear-pod extension ≈ 30 mm, S_v ≈ 2.1 dm², b_v ≈ 250 mm, root t ≥ 2.5 mm, no rudder); finless baseline remains the O1 build; C16 stall tension with the fin mass flagged to F2 (OP-24); `yaw_stability.py` added |
| 0.5 | 2026-08-05 | **Component catalogs integrated (I-16/17/18/19):** FPV DJI O4 system in the mass budget (§8.1: +37 g → AUW 1697 g), balance re-run (`balance_cg.py` — pack 6S1P ≈ −415, bay −516…−315); servo class 12–15 g + cavity 34×16×39 + torque not binding + current data (§7.5, I-18); FC reference class F405-WING-V2 / SpeedyBee + station cavity 64×45×21 + avionics 6.6 W (§7.6, §11, I-17); FPV camera/VTX mounts in the CORE (§7.6) and FPV/video power in §11 (I-19); battery energy reference 90.7/108 Wh (§10.1, I-16); stall flag updated (46.1 km/h, OP-24). |
| 0.4 | 2026-08-05 | **Bay re-derived with the real pack envelope (I-16 `[D]`):** 6S1P = 153 × 64.5 × 22.2 mm (2×3, orient. A) → bay **200 × 70 × 32 mm**, forward end **x ≈ −521**, boom ≈ 390 mm (`balance_cg.py`). Fit verdict: only 6S1P fits and reaches the R-CG band; 4S1P fits but needs x ≈ −577 (outside); 4S2P/6S2P fit no single-layer arrangement (I-16) — OP-23 sharpened. |
| 0.3 | 2026-08-05 | **OP-01 resolution:** battery **nose boom** adopted (bay x ≈ −493…−304, 6S1P pack at ≈ −421 mm, `balance_cg.py` `[D]`); pack-station map per configuration; 4S1P/6S2P R-CG tension flagged (OP-23); boom structure ≤ 40 g target (OP-24). **R-TWIST raised 2.5° → 3.0°** (§5.3): stall criterion holds at 3.0° (load peak 56 % b/2, margin +0.017); residual trim ≤ 0.6° permanent elevon reflex. **Elevon authority verified** (`elevon_authority.py` `[D]`): yield 0.00348 °/° over 30–90 % span, 10° ≈ 4.8× the trim requirement. AUW 1660 g → V_stall ≈ 45.6 km/h flagged with the declared mass lever (§4, OP-24). |
| 0.2 | 2026-08-05 | Designer-review release. Dihedral defined piecewise (kinks at y = 195/347/498, C22); elevon span corrected to 30–90 % (panel component, C23); print orientation clarified as 45° airfoil roll (C24); motor station and prop-disk position fixed (C25); prop ground-clearance constraint defined (C26); carbon tube/pin physical lengths and socket specs added (C27); new §7.6 CORE outer-mold constraints (nose pod, rear pod, bay, sockets, avionics stations); OP-01 band re-derived (≈ −24…+9 mm, bay-limited); wing-tip treatment declared (OP-20); provisional airfoil coordinate recipe added. **I-09 additions:** E205 tip-airfoil data point (§6.2); mylar hinge alternative (§7.5); CORE balance tabs (§7.6, §12); nose-pod retention pattern and battery-hatch spring lock (§7.6, §9). **I-10…I-14:** threads opened; C28 (root/tip candidates corrected, §6.2/§6.3); stall-margin flag (§4); R-AIRFOIL feasibility flag (§6.1); pusher-slipstream note (§10.1). **I-15:** airfoil evidence campaign opened (11 investigations); root section to be designed, not selected (§6.1 note); stall-character criterion added (§6.1) and confidence basis of the polar declared (§6.1). **B3 screening + C2 executed (I-15 §6):** E205 discarded on its polar (§6.2); NP cross-checked — two methods agree within 3 mm (§3); twist note with trim-closure numbers (§5.3); trim-closure blockquote (§6.1). |
| 0.1 | 2026-08-05 | First release. Reference geometry per I-07/ADR-0027; provisional airfoil (B3 pending), dihedral, twist, carbon, motor, bay. OP-01 flagged. |
