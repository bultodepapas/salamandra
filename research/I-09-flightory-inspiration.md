# I-09 — Flightory Pico Talon and Stallion: compared geometry and construction

**Status:** Open — primary sources acquired, base comparison published
**Feeds:** B3/G2 (E205 as a flight-proven low-Re section), CORE design patterns
(guide §7.6), docs/02 measured-references register, ADR-0035 review (hinge alternatives)
**Sources:** Flightory (Szymon Wójcik) user manuals V.1 2023 —
`INSPIRATION/PICO TALON MANUAL.pdf`, `INSPIRATION/STALLION MANUAL.pdf`

---

# 1. Question

The two manuals in `INSPIRATION/` are from the same designer family as the Peregrine
(docs/02): thin-wall printed FPV aircraft. What do they contribute that the Peregrine
does not? Two things: (a) a **second airfoil in service** (Eppler E205, on two aircraft)
and (b) a **tailed, pod-and-boom construction** with modularity patterns relevant to the
Salamandra CORE — plus (c) a data-quality lesson of the same type as the Peregrine stall
speed (docs/02 §1.4).

Both aircraft are **conventional tailed designs (pod + V-tail)** — not tailless, not
forward-swept. Their aerodynamics do not transfer to the Salamandra; their construction
and integration practice do. The comparison below is therefore **constructive, not
causal** (same discipline as I-08).

# 2. Primary sources

- Pico Talon user manual V.1, © 2023 Flightory by Szymon Wójcik — 35 pages.
- Stallion user manual V.1, © 2023 Flightory by Szymon Wójcik — 54 pages.
- Values below are those published by the designer `[M]`. The STL files are not present
  in this repository, so no geometric measurement was possible (unlike R1/R2).

# 3. Published data `[M]`

| Parameter | Pico Talon | Stallion |
|---|---|---:|
| Wingspan | 900 mm | 1340 mm |
| Wing area | 13 dm² | 26.5 dm² |
| Length | 570 mm | 990 mm |
| CG from LE (at wing root) | 44 mm | 60 mm |
| AUW | 800 g (max 1500 g) | 1500–3000 g |
| Optimal cruise | 55–75 km/h | 60–70 km/h |
| Airfoil | Eppler E205 | Eppler E205 |
| Root chord | 169 mm | 255 mm |
| MAC | 145 mm | 211 mm |
| Aspect ratio | 6.2 | 5.6 |
| Wing loading | 60–115 g/dm² | 55–115 g/dm² |
| Configuration | Single tractor, pod, V-tail | Twin tractor, tail boom, V-tail, winglets |
| Motor (reference) | T-Motor F90 1300 KV | 2× T-Motor F60 1750 KV / F90 1300 KV |
| Propeller | 7×4 / 7×5 / 7×6 | 7×4 / 7×5 / 7×6 (CW + CCW) |
| ESC | 40 A | 2× BlHeliS 40 A |
| Battery | Li-Ion 21700 4S1P (~300 g); 4S2P fits | 4S up to 4S6P 21 Ah; 3S possible |
| Servos | 2× 929MG + 2× CS239MG | 4× 929MG |
| FC / GPS | SpeedyBee F405 WING / Matek M10Q | SpeedyBee F405 WING / Matek M10Q |
| Reported endurance | ~2 h (4S2P) | > 4 h (4S6P, ~4 A at ~40 % throttle) |

# 4. Derived checks `[D]`

- **Pico Talon:** AR = b²/S = 0.81/0.13 = **6.23** ✓ (published 6.2). Taper implied by
  MAC 145 and c_root 169: λ ≈ 0.70, c_tip ≈ 118 mm. CG = 44/169 = **26 % root chord**.
  Re(MAC) at cruise: 55 km/h ≈ 1.5×10⁵, 75 km/h ≈ **2.1×10⁵**.
- **Stallion: internally inconsistent datasheet.** AR = b²/S = 1.7956/0.265 = **6.78**,
  not the published 5.6. MAC 211 mm with c_root 255 implies λ ≈ 0.63 and S ≈ 0.278 m²,
  again not 26.5 dm². Three published numbers (AR, S, MAC) describe three different
  wings. Same failure mode as the Peregrine stall speed (docs/02 §1.4): a published
  datasheet carries an internal contradiction that only a `[D]` cross-check exposes.
  CG = 60/255 = **23.5 % root chord**. Re(MAC) ≈ 2.6–3.0×10⁵.
- **Wing loading bands** (55–115 g/dm²) agree with the AUW ranges in both manuals —
  that part is consistent.
- **E205 geometry** (UIUC e205.dat `[M]`): t/c = **10.6 % at 30 % chord**, camber
  **2.9 % at 34 % chord**; the mean line stays positive through 90 % chord
  (≈ +0.006 at 0.9 c) — a **moderately cambered, lightly reflexed** section, not a
  strong-reflex flying-wing profile.

# 5. Construction and printing practice `[M]`

| Practice | Pico Talon | Stallion | Relevance to Salamandra |
|---|---|---|---|
| Shell material | LW-PLA, single wall 0.4 mm, 3 % gyroid, 235 °C, flow 60 %, fan 0, layer 0.25 | Same; wings 3–4 % **cubic subdivision**; hard parts PETG/PLA 20 % grid | Same family practice as the Peregrine (docs/02 §1.2): 3–5 % gyroid flight-proven. Salamandra's PETG 2×0.45 + 5 % gyroid (ADR-0028) is the scaled analog; flow-ratio warning applies (docs/02 §1.7) |
| Bed size | 200×200 mm, no supports | 220×220 mm, no supports; fuselage split L/R for small beds | Supports the 256 mm-bed constraint (O3) and Salamandra's segmentation (ADR-0024) |
| Bending spars | 8×500 main + 6×490 + 4×220; V-tail 4×130 | 10×800 main + 2× 8×600 + 2× 6×430; tail boom 16×435; V-tail 4×260 | Multi-tube bending practice; the 6×430 wing tube is explicitly inserted **unglued** ("no need to glue, just insert into the designed slot") — the "housed" case ADR-0015 warns against **for torsion**. Not contradictory: these are non-swept wings with no divergence requirement |
| Hinges | Polyester (mylar) 20×25/25×30, glued | Same, 25×30 | Flight-proven alternative to TPU-printed hinges (ADR-0035); lighter, cheaper; stiffness is the unknown for both — feeds OP-10 |
| Modularity | Detachable nose (threaded inserts + printed reinforcement collar); hatch locks with pen springs; removable wings with M3 into inserts; STEP files | Same + removable tail boom (printed drill guides "BOOM DRILL" for drilling the carbon tube) | Direct pattern source for the CORE (§7.6): nose pod retention, battery hatch lock, battery pad, insert-reinforced roots, STEP for community customization (O12/O14/O15) |
| Balance aids | **Tabs on the underside of the wings** to balance on | — | Cheap CAD feature; adopt for the Salamandra CG verification (§12 step 7) |
| Launch | — | Hand throw, "grab the fuselage under the wings, slight AoA" | Grip location under the wing at the CORE — consistent with the CORE-side grip in guide §7.6 |

# 6. What transfers and what does not

**Does not transfer:** anything aerodynamic. Both aircraft are tailed
(pod + V-tail), tractor, non-swept; their trim, stability and stall behavior are not
comparable to a tailless forward-swept wing. E205's good in-service behavior says nothing
about its Cm0 (the V-tail trims it) — E205 cannot be admitted to B3 on these manuals
alone (R-AIRFOIL needs Cm0 ≥ +0.008, and E205's camber suggests the opposite sign; only
a calibrated XFOIL run can decide).

**Transfers:** the construction system (thin shell + low gyroid + inserted carbon
bending spars + glued modular joints), the integration patterns (detachable nose,
spring-hatch locks, insert-reinforced roots, printed drill guides, balance tabs), the
electronics ecosystem (SpeedyBee F405 WING + Matek M10Q + ELRS — the same components as
docs/00 §3.5 and OP-18), and the 21700 4S1P battery precedent (the Pico Talon flies on
the same cell format Salamandra's platform is built around).

# 7. Consequences for Salamandra

1. **B3/G2:** E205 is a candidate for the screening list **only as a tip-airfoil data
   point** — 10.6 % t/c against the 9 % tip target, and flight-proven at
   Re 1.5–3×10⁵, which brackets the Salamandra's stall-to-cruise root range. Its Cm0
   must come from the calibrated Ncrit 10–12 band (I-06) before it is admitted or
   discarded; the moderate camber supports the "lightly reflexed" direction of I-02 (C2).
2. **CORE design (guide §7.6):** adopt the Flightory patterns where they fit the
   removable-joint philosophy: nose pod retention with threaded inserts + reinforcement
   collar, spring-loaded hatch lock for the battery bay, battery pad, and balance tabs
   on the CORE underside. These are `[M]`-proven details; their adoption is a design
   choice (OP-21), not a new datum.
3. **Data-quality lesson:** the Stallion's AR/S/MAC contradiction is the second instance
   of the Peregrine-type datasheet error in the measured-reference set. It re-confirms
   the docs/04 rule: `[M]` is the *source* tag, not an *accuracy* guarantee — every
   published figure still gets a `[D]` cross-check before it feeds a decision.
4. **Performance context:** the Stallion's ~4 A at ~40 % throttle (≈ 60 W) for a
   1.5–3 kg aircraft at 60–70 km/h shows the Flightory family operates at lower speed
   and power than the Salamandra cruise point (95 km/h, ≈ 110 W, 1.62 kg). The
   Salamandra's O1 target (≤ 1.15 Wh/km at 95 km/h) remains at the fast end of proven
   printed-FPV practice — no relaxation of the propulsion-matching work (D3/D4).

# 8. Data pending

- STL files of both aircraft (planform reconstruction, t/c measurement at stations) —
  would turn R3-style data into `[M]` geometry. Not present in this repository.
- Flightory print profiles (full Cura profiles) — the manuals reference them on the
  website; if acquired, they extend docs/02 §1.2.

# 9. Transfer limits

- A single-author family, like the StuntDouble set (I-08): recurring design practice of
  one designer is not independent replication.
- The manuals are nominal design data, not measurements of printed parts.
- E205 polars are not published in the manuals; nothing here replaces the B3 screening.
