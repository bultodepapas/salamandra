# I-08 — StuntDouble family: compared geometry

**Status:** Open — primary sources acquired, base comparison published
**Feeds:** A4 of the Phase 1 plan, R3 and R4 of measured references
**Does not close:** G1 or G2

---

# 1. Question

What can be learned from comparing a forward-swept wing with two *planks*
from the same designer and the same constructive family?

The working hypothesis of A4 was to treat Nemesis, Stinger and Stormbird as a "controlled natural
experiment". Reviewing the primary files shows that formulation was
too strong: the airfoil, the propulsion and part of the geometry change. The comparison
remains useful, but it is **quasi-controlled** and serves to generate geometric priors, not
to attribute causality to the sweep.

# 2. Primary sources

Files downloaded and reviewed on 28 July 2026:

- **Nemesis:** build manual, revision 27 September 2025, and the designer's STL.
  Public source: [Thingiverse 6644675](https://www.thingiverse.com/thing:6644675).
- **Stinger V2:** datasheet and designer's STL, package dated 21 June 2025.
  Public source: [Thingiverse 6760208](https://www.thingiverse.com/thing:6760208).
- **Stormbird:** build manual, revision 18 September 2023, and the designer's STL.
  Public source: [Thingiverse 6174038](https://www.thingiverse.com/thing:6174038).

The values in the following table are those published by the designer `[M]`.

# 3. Published comparison `[M]`

| Model | Planform / propulsion | b | Length | Airfoil | S | AUW | Wing loading |
|---|---|---|---:|---:|---|---:|---:|---:|
| **Nemesis** | Forward sweep / two tractors | 1200 mm | 600 mm | PW51 | 22 dm² | 1100–1400 g | 50–64 g/dm² |
| **Stinger V2** | *Plank* / two tractors | 1300 mm | 630 mm | PW75 | 26 dm² | 1200–1600 g | 46–62 g/dm² |
| **Stormbird** | *Plank* / one pusher | 1100 mm | 580 mm | PW75 | 20 dm² | 900–1200 g | 45–60 g/dm² |

## 3.1 Derived quantities `[D]`

Calculated directly from `AR = b²/S` and `c_mean = S/b`:

| Model | AR `[D]` | Geometric mean chord `[D]` |
|---|---|---:|
| Nemesis | 6.55 | 183 mm |
| Stinger V2 | 6.50 | 200 mm |
| Stormbird | 6.05 | 182 mm |

**Useful result:** the three designs converge on AR ≈ 6.0–6.6 `[D]`, despite their different
planforms. It is evidence of design practice compatible with [ADR-0004](../decisions/ADR-0004-aspect-ratio.md),
but it does not validate it by itself: the three examples come from the same designer.

# 4. What is and is not controlled

| Variable | Nemesis vs. Stinger | Nemesis vs. Stormbird |
|---|---|---|
| Designer and manufacturing family | Same | Same |
| Order of AR and wing loading | Comparable | Comparable |
| Number and position of motors | Same: two tractors | Different: two tractors / one pusher |
| Airfoil | **Different: PW51 / PW75** | **Different: PW51 / PW75** |
| Wingspan and area | Different | Different |
| Fuselage | Not shown identical | Identical per the Nemesis manual `[M]` |

Therefore:

- **Yes**, recurring geometric decisions of the family can be compared.
- **No**, a difference in efficiency, stability or stall cannot be attributed to the sweep:
  the PW51↔PW75 change is a first-order aerodynamic confounder.
- **No**, Stormbird cannot be used to isolate the sweep effect on propulsion:
  it changes from twin tractor to a single pusher.

# 5. Published trim data `[M]`

| Model | Published adjustment |
|---|---|
| Nemesis | 2 mm of upward elevon reflex |
| Stormbird | 1–2 mm of upward elevon reflex |

Both need control reflex. The figure is in millimeters, not degrees, and the local elevon
chord still needs measuring to convert it into angle `[D]`. This datum **does not allow**
concluding that forward sweep closes the trim without cost; it reinforces that A4 must measure airfoil,
built twist and elevon geometry before feeding R-TWIST.

# 6. Transfer limits

- The STLs are the designer's nominal geometry, not a measurement of a printed part.
- A single author family is not independent replication.
- The manual's qualitative performance does not replace polars or *blackbox*.
- PW51 and PW75 prevent isolating the planform effect.
- The published reflex is a flight adjustment; without elevon chord it is not a comparable angle.
- **Data availability (2026-08-05):** PW51 is **not in the UIUC airfoil database**
  (404 confirmed); its coordinates/polars must come from other sources (German
  nurflügel material, Unverferth's "Faszination Nurflügel", airfoiltools when
  reachable) before it can enter a measured-data path — see I-15/A3.

# 7. Next extraction

1. Reconstruct each model's assembled planform: chords, taper and c/4 sweep.
2. Slice the meshes at equivalent stations and measure `t/c`.
3. Measure the twist distribution and the elevon chord.
4. Convert the published linear reflex into angle.
5. Only then compare the I-07 torsion window with published hardware.

Until these steps are complete, **A4 stays partial** and freezes no project geometry.
