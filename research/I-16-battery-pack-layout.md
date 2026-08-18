# I-16 — Battery pack layout: physical envelope of 4S / 6S · 21700 Li-Ion

**Status:** Open — reference sizing catalog · **Feeds:** guide §9 (battery and bay), `balance_cg.py` OP-01/OP-23, docs/00 §3.3 R-CG

> **This is a reference catalog, not a decision.** It reports the measured envelope
> of every possible rectangular arrangement so the designer can choose. Every pack
> described here is buildable; a configuration larger than the current *provisional*
> bay simply needs the bay (or the fuselage) sized accordingly. Nothing here forbids
> any arrangement.

## 1. Objective and scope

This thread establishes, from reproducible calculation (`[D]`), the **physical
dimensions of every admissible rectangular layout** of a 4-cell (4S) and a 6-cell
(6S) pack of cylindrical **21700 Li-Ion** cells, together with the assembly
allowances from wrapper, nickel interconnects and wiring/terminals.

It gives the designer the numbers for **4S1P, 6S1P, 4S2P and 6S2P** — and any other
arrangement — as a menu for future power modules. ADR-0042/0043 select **6S1P only for
Article #1**; the catalog does not imply that one motor or cradle must interchange all
packs. Current reference dimensions are reported for context, but this document does
not rule out a separately engineered module.

The calculator is `calculations/battery_pack_layout.py`. Every figure below
labelled `[D]` is produced by it and is reproducible in one command:

```bash
python3 calculations/battery_pack_layout.py
```

## 2. Cell input data (the source of every number)

A 21700 cell is a cylinder: **21.0 mm nominal diameter × 70.0 mm nominal length**
(`[M]`, manufacturer datasheets; the Molicel INR21700-P42A and Samsung INR21700-50E
are the two reference cells, see §9). Real cells measure 21.0–21.4 mm in diameter
and 70.0–70.8 mm in length depending on brand and wrapper.

| Input | Symbol | Value | Basis |
|---|---|---|---|
| Cell diameter (nominal) | `D_nom` | **21.0 mm** | `[M]` datasheet |
| Cell length (nominal) | `L_nom` | **70.0 mm** | `[M]` datasheet |
| Cell PVC wrapper | `t_wrap` | **+0.15 mm/side** | `[E]` declared |
| → wrapped diameter | `D` | **21.3 mm** | `[D]` |
| → wrapped length | `L` | **70.3 mm** | `[D]` |
| Cell mass (ref) | — | **≈ 68 g** | `[M]` P42A/50E |
| Cell energy (ref) | — | **≈ 18 Wh** (3.6 V × 5 Ah) | `[M]`/`[D]` |

The wrapped cylinder (D × L = 21.3 × 70.3 mm) is the building block of the whole
concept enumeration. It is **not** the fit-check envelope for E01.

### 2.1 E01 maximum-dimension CAD path

Molicel's P42A v4 data sheet gives **21.7 mm maximum diameter, 70.2 mm maximum
height and 70 g maximum mass** `[M]`. Because those maximum dimensions already
describe the sleeved cell, the CAD path does not add the nominal per-cell wrapper
a second time. For the released 2 × 3 × 1 layout:

- raw cell block = `2 × 70.2` by `3 × 21.7` by `1 × 21.7`
  = **140.4 × 65.1 × 21.7 mm** `[D]`;
- pack allowances = 0.3 mm outer wrap per side, 0.3 mm nickel height and
  12 mm lead projection `[E]`;
- **E01 installed CAD envelope = 153.0 × 65.7 × 22.6 mm** `[D]` on `[M]/[E]`;
- **E01 installed mass = 6 × 70 + 25 = 445 g** `[D]` on a 25 g hardware
  allowance `[E]`.

The older 153.2 × 64.5 × 22.2 mm result remains useful only as the nominal
generic-21700 enumeration; it shall not control the P42A cradle fit.

### 2.2 Reference cells compared — two starting points and an average

Two good reference cells bracket the 21700 design space for this aircraft:
**Molicel INR21700-P42A** (high-drain) and **Samsung INR21700-50E** (high-capacity).
Independent measured dimensions (lygte-info, `[M]`) are included; they confirm the
wrapped 21.3 × 70.3 mm block used above.

| Parameter | Molicel P42A `[M]` | Samsung 50E `[M]` | Average `[D]` |
|---|---|---|---|
| Mass | **70 g** | **68 g** | **69 g** |
| Nominal capacity | 4.2 Ah (typ) | 5.0 Ah (typ) | 4.6 Ah |
| Nominal voltage | 3.6 V | 3.6 V | 3.6 V |
| Max continuous discharge | **45 A** | **9.8 A** | 27.4 A |
| Max charge current | 8.4 A | 4.9 A | 6.65 A |
| Nominal energy | **15.1 Wh** | **18.0 Wh** | 16.6 Wh |
| Specific energy | 216 Wh/kg | **265 Wh/kg** | 240 Wh/kg |
| Measured Ø × L | 21.2 × 70.0 mm | 21.1 × 70.6 mm | — |
| Internal impedance | < 15 mΩ | — | — |
| Role | High-drain, handles peaks | High-capacity, low-drain | Compromise point |

> **Engineering note:** the two cells trade capacity against current. The P42A
> delivers up to 45 A continuous (≈ 3× the aircraft's ~20 A peak, guide §10.1) with
> margin to spare; the 50E caps at 9.8 A continuous / 14.7 A pulse, **below the
> ~20 A peak** — suitable only for a lower-power, long-range build. Both share the
> same 21700 envelope, so the physical layout analysis (§4–§6) is identical for
> either cell; only mass, energy and current rating differ.

## 3. Method — the layout model

A pack is an **N-cell rectangular block** of cells all lying with their axes
horizontal (standing the cells would put the 70 mm length on the vertical; that is
also possible and is noted where relevant, but the flat catalog below is what a
wing/fuselage battery bay uses). The block is described by three integers:

- `n_x` — cells along the pack **Length**,
- `n_y` — cells along the pack **Width**,
- `n_z` — stacked layers (height),

with `n_x · n_y · n_z = N`. The cylindrical axis can point along the Length or
along the Width, giving two orientations:

| Orientation | Cell axis | Block Length | Block Width | Block Height |
|---|---|---|---|---|
| **A** ("in-line") | parallel to Length | `n_x·L` | `n_y·D` | `n_z·D` |
| **B** ("transverse") | parallel to Width | `n_x·D` | `n_y·L` | `n_z·D` |

`factor_triples()` in the calculator enumerates every ordered `(n_x, n_y, n_z)`
triple with product N (the axes have distinct physical roles, so each ordered
triple is distinct). For N = 4 there are 6 arrangements; for N = 6, 9. Times two
orientations → **12 envelope candidates for 4S and 18 for 6S.**

### Assembly allowances `[E]`

Raw block → finished, wrapped pack:

| Allowance | Value | Applies to |
|---|---|---|
| Outer shrink/fiber wrap | **+0.3 mm/side** | all three axes (+0.6 mm each) |
| Nickel interconnects | **+0.3 mm** | height (stack face) |
| Balance + XT60 pigtail | **+12 mm** | one Length end |
| Inter-cell clearance | 0.0 mm (tight) | — |

### Bay reference (informational)

The Salamandra reference bay (guide §9, PROVISIONAL) is a horizontal channel
`190 × 70 × 32 mm` (x · y · z), single 21 mm layer. The "bay ok" column in the
tables below is a **factual check** against *this particular provisional bay*; it
is reported so the designer sees, at a glance, which envelopes fit the current bay
and which would require resizing it. It is **not** a statement that a pack is
impossible. The height check (pack Height ≤ 32 mm) encodes the current single-layer
bay; a stacked pack needs a taller bay.

## 4. Complete envelope table — 4S (4 cells)

`D` = derived from §2/§3 inputs. "Cell block" = raw array; "Pack" = finished with
assembly allowances. "Bay ok" = fits the current *provisional* `190 × 70 × 32` bay.

| Arrangement `n_x·n_y·n_z` | Orient. | Cell block L×W×H (mm) | **Pack L×W×H (mm)** | Bay ok |
|---|---|---|---|---|
| 2×2×1 | A | 140.6 × 42.6 × 21.3 | **153.2 × 43.2 × 22.2** | ✓ |
| 2×2×1 | B | 42.6 × 140.6 × 21.3 | **55.2 × 141.2 × 22.2** | ✓ |
| 4×1×1 | A | 281.2 × 21.3 × 21.3 | 293.8 × 21.9 × 22.2 | – |
| 4×1×1 | B | 85.2 × 70.3 × 21.3 | 97.8 × 70.9 × 22.2 | – |
| 1×4×1 | A | 70.3 × 85.2 × 21.3 | 82.9 × 85.8 × 22.2 | – |
| 1×4×1 | B | 21.3 × 281.2 × 21.3 | 33.9 × 281.8 × 22.2 | – |
| 2×1×2 | A | 140.6 × 21.3 × 42.6 | 153.2 × 21.9 × 43.5 | – (stacked) |
| 1×2×2 | A | 70.3 × 42.6 × 42.6 | 82.9 × 43.2 × 43.5 | – (stacked) |
| 2×1×2 | B | 42.6 × 70.3 × 42.6 | 55.2 × 70.9 × 43.5 | – (stacked) |
| 1×2×2 | B | 21.3 × 140.6 × 42.6 | 33.9 × 141.2 × 43.5 | – (stacked) |
| 1×1×4 | A | 70.3 × 21.3 × 85.2 | 82.9 × 21.9 × 86.1 | – (stacked) |
| 1×1×4 | B | 21.3 × 70.3 × 85.2 | 33.9 × 70.9 × 86.1 | – (stacked) |

All twelve are buildable. The **2×2** pack (both orientations) is the one that fits
the current provisional bay; the linear sticks (4×1, 1×4) and the stacked blocks
(2 high, 4 high) are equally valid pack shapes for a longer or taller bay.

## 5. Complete envelope table — 6S (6 cells)

| Arrangement `n_x·n_y·n_z` | Orient. | Cell block L×W×H (mm) | **Pack L×W×H (mm)** | Bay ok |
|---|---|---|---|---|
| 2×3×1 | A | 140.6 × 63.9 × 21.3 | **153.2 × 64.5 × 22.2** | ✓ |
| 3×2×1 | A | 210.9 × 42.6 × 21.3 | 223.5 × 43.2 × 22.2 | – |
| 2×3×1 | B | 42.6 × 210.9 × 21.3 | 55.2 × 211.5 × 22.2 | – |
| 3×2×1 | B | 63.9 × 140.6 × 21.3 | 76.5 × 141.2 × 22.2 | – |
| 6×1×1 | A | 421.8 × 21.3 × 21.3 | 434.4 × 21.9 × 22.2 | – |
| 6×1×1 | B | 127.8 × 70.3 × 21.3 | 140.4 × 70.9 × 22.2 | – |
| 1×6×1 | A | 70.3 × 127.8 × 21.3 | 82.9 × 128.4 × 22.2 | – |
| 1×6×1 | B | 21.3 × 421.8 × 21.3 | 33.9 × 422.4 × 22.2 | – |
| 3×1×2 | A | 210.9 × 21.3 × 42.6 | 223.5 × 21.9 × 43.5 | – (stacked) |
| 1×3×2 | A | 70.3 × 63.9 × 42.6 | 82.9 × 64.5 × 43.5 | – (stacked) |
| 3×1×2 | B | 63.9 × 70.3 × 42.6 | 76.5 × 70.9 × 43.5 | – (stacked) |
| 1×3×2 | B | 21.3 × 210.9 × 42.6 | 33.9 × 211.5 × 43.5 | – (stacked) |
| 2×1×3 | A | 140.6 × 21.3 × 63.9 | 153.2 × 21.9 × 64.8 | – (stacked) |
| 1×2×3 | A | 70.3 × 42.6 × 63.9 | 82.9 × 43.2 × 64.8 | – (stacked) |
| 2×1×3 | B | 42.6 × 70.3 × 63.9 | 55.2 × 70.9 × 64.8 | – (stacked) |
| 1×2×3 | B | 21.3 × 140.6 × 63.9 | 33.9 × 141.2 × 64.8 | – (stacked) |
| 1×1×6 | A | 70.3 × 21.3 × 127.8 | 82.9 × 21.9 × 128.7 | – (stacked) |
| 1×1×6 | B | 21.3 × 70.3 × 127.8 | 33.9 × 70.9 × 128.7 | – (stacked) |

All eighteen are buildable. Of these, the **2×3** pack (orient. A) is the one that
fits the current provisional bay — this is the physical envelope of the **6S1P
reference pack** (guide §9): **153 × 64 × 22 mm**. Every other shape is a valid
option for a bay sized to it: the sticks (6×1, 1×6) need a long bay, the 3×2 and
2×3-B need a wider bay, and the stacked blocks need a taller bay (heights up to
129 mm for a 6-stack).

## 6. Pack-level summary (single-layer candidates)

| Pack | Arrangement | Orientation | Pack L×W×H (mm) | Envelope (mL) | Mass (cells) | Nominal energy | Bay ok |
|---|---|---|---|---|---|---|---|
| 4S | 4×1×1 | A | 293.8 × 21.9 × 22.2 | 143 | 272 g | 72 Wh | – |
| 4S | **2×2×1** | **A** | **153.2 × 43.2 × 22.2** | 147 | 272 g | 72 Wh | ✓ |
| 4S | 4×1×1 | B | 97.8 × 70.9 × 22.2 | 154 | 272 g | 72 Wh | – |
| 4S | 1×4×1 | A | 82.9 × 85.8 × 22.2 | 158 | 272 g | 72 Wh | – |
| 4S | 2×2×1 | B | 55.2 × 141.2 × 22.2 | 173 | 272 g | 72 Wh | ✓ |
| 4S | 1×4×1 | B | 33.9 × 281.8 × 22.2 | 212 | 272 g | 72 Wh | – |
| 6S | 6×1×1 | A | 434.4 × 21.9 × 22.2 | 211 | 408 g | 108 Wh | – |
| 6S | 3×2×1 | A | 223.5 × 43.2 × 22.2 | 214 | 408 g | 108 Wh | – |
| 6S | **2×3×1** | **A** | **153.2 × 64.5 × 22.2** | 219 | 408 g | 108 Wh | ✓ |
| 6S | 6×1×1 | B | 140.4 × 70.9 × 22.2 | 221 | 408 g | 108 Wh | – |
| 6S | 1×6×1 | A | 82.9 × 128.4 × 22.2 | 236 | 408 g | 108 Wh | – |
| 6S | 3×2×1 | B | 76.5 × 141.2 × 22.2 | 240 | 408 g | 108 Wh | – |

For the current provisional bay, the **2×2 (4S)** and **2×3 (6S)** single-layer packs
are the volume-optimal options.

### 6.1 Mass, energy and discharge — three pack weights per configuration

Pack mass, energy, voltage and available current are computed per reference cell
(`[D]` from §2.1), for the physical layout that fits the bay (4S1P = 2×2, 6S1P =
2×3, orient. A). "Mass" is cell-only; "+ hw" adds **25 g** of pack hardware
(nickel, wiring, XT60, wrap) `[E]`. Energy is nominal at 3.6 V.

**4S1P (2×2, single layer — 153 × 43 × 22 mm):**

| Cell | Cells | Mass (+hw) | Wh | Ah | Vnom | Vmax | Wh/kg | I pack |
|---|---|---|---|---|---|---|---|---|
| Molicel P42A | 4 | **280 (305) g** | 60.5 | 16.8 | 14.4 | 16.8 | 198 | **45 A** |
| Samsung 50E | 4 | **272 (297) g** | 72.0 | 20.0 | 14.4 | 16.8 | 242 | 9.8 A |
| Average | 4 | **276 (301) g** | 66.2 | 18.4 | 14.4 | 16.8 | 220 | 27.4 A |

**6S1P (2×3, single layer — 153 × 64 × 22 mm):**

| Cell | Cells | Mass (+hw) | Wh | Ah | Vnom | Vmax | Wh/kg | I pack |
|---|---|---|---|---|---|---|---|---|
| Molicel P42A | 6 | **420 (445) g** | 90.7 | 25.2 | 21.6 | 25.2 | 204 | **45 A** |
| Samsung 50E | 6 | **408 (433) g** | 108.0 | 30.0 | 21.6 | 25.2 | 249 | 9.8 A |
| Average | 6 | **414 (439) g** | 99.4 | 27.6 | 21.6 | 25.2 | 226 | 27.4 A |

> **Comparison with the mission table (docs/00 §3.3):** the guide quotes 4S1P ≈ 300 g /
> 65 Wh and 6S1P ≈ 455 g / 97 Wh (`[E]`). The datasheet-derived numbers above put
> 4S1P ≈ 297–305 g (matching) but 6S1P ≈ 433–445 g at 91–108 Wh — the guide's 6S1P
> mass estimate is ~10–20 g high. Worth revisiting in F2 (OP-24 weight table).
>
> **Takeaway:** three pack weights are on the table per config — the P42A build
> (lightest energy but 3× current headroom), the 50E build (heaviest energy per gram,
> 20 % more Wh, but no peak-current margin), and the average as a neutral midpoint.
> The designer picks per mission: **P42A for this aircraft's ~20 A peaks, 50E for a
> low-power long-range variant.**

## 7. Wrapper, interconnects, wiring and terminals

### 7.1 Cell and pack wrapping

- **Cell PVC heat-shrink**: ≈ 0.10–0.15 mm per side `[E]`. Adds ≈ 0.2–0.3 mm to the
  nominal diameter. Adopted **+0.15 mm/side** (→ wrapped D = 21.3 mm).
- **Outer pack wrap**: fiber tape or shrink tube ≈ 0.2–0.3 mm per side `[E]`.
  Adopted **+0.3 mm/side** on all three axes.
- **Net effect on the block**: diameter grows 21.0 → **21.3 mm**; length grows
  70.0 → **70.3 mm**; finished pack adds **+0.6 mm** per axis (wrap) and **+0.3 mm**
  (nickel) on height, **+12 mm** (leads) on length.

### 7.2 Nickel interconnects (series welding)

- Nickel strip **0.10–0.20 mm thick, ~8 mm wide** `[E]`, spot-welded across the
  positive/negative poles. For series stringing (4S/6S) each cell pair needs a
  strip; 6S1P therefore has 5 series links plus the two main tabs.
- The weld stack adds ≈ **0.3 mm** to the pack height (adopted), negligible to
  length/width.

### 7.3 Main power path and terminals

- **Terminal**: XT60 (60 A), ≈ 28 × 18 × 14 mm, with **14 AWG** pigtails (≈ 2.1 mm²),
  typical free lead 80–100 mm `[E]`. The connector + folded pigtail is the "+12 mm
  Length" allowance in the calculator.
- **Wire gauge check `[D]`** against the guide §10.1 operating point (cruise ≈ 5 A,
  peak ≈ 20 A, 6S):

  | Condition | Current | 14 AWG (2.08 mm²) |
  |---|---|---|
  | Cruise | 5 A | 24 % of ~25 A chassis ampacity |
  | Peak | 20 A | 80 % of ~25 A — acceptable, generous margin vs 20 A |

  14 AWG is adequate with margin for this propulsion chain; balance leads are
  signal-only (26–30 AWG, < 1 A).

### 7.4 Balance (cell-tap) wiring

- 4S → **JST-XH 5-pin**, 6S → **JST-XH 6-pin**, 2.54 mm pitch `[E]`. Board/header
  ≈ 1.5–2 mm thick; adds only to the lead allowance already included.

## 8. Observations (for the designer)

1. **6S1P reference envelope = 153 × 64 × 22 mm** (2×3, orient. A). It fits the
   current provisional bay with 37 mm length, 6 mm width and 10 mm height to spare.
2. **Bay-fit menu:** of the 12 (4S) and 18 (6S) envelopes, the current *provisional*
   bay accommodates 2×2 (4S) and 2×3-A (6S). Every other envelope is equally
   buildable; the designer picks the bay/fuselage to match — e.g. a **super-flat**
   design can run cells side-by-side (n_y big, n_z = 1, height stays 22 mm) and just
   needs a wider/longer bay.
3. **Stacked packs (n_z ≥ 2)** are possible and are simply taller (43.5–128.7 mm);
   they need a bay deeper than the current 32 mm. If a taller fuselage section is
   acceptable, a "stack of 4/6" is a valid, compact-in-footprint option.
4. **Height floor:** for a flat (n_z = 1) pack the height is always **≈ 22 mm**
   (wrapped cell 21.3 mm + wrap/nickel). This is the thinnest achievable pack; the
   designer cannot go below it without a different cell format.
5. **Discrepancy note (OP-23 / F2):** `balance_cg.py` uses `PACK_LEN = 0.084 m`
   (84 mm) as the 6S1P pack length. The finished 6S1P pack measured here is
   **≈ 153 mm long**. If the reference layout stays 2×3, the pack-length placeholder
   used to size the bay and pack stations should be reviewed in F2.
6. **Cell choice is decoupled from geometry.** The P42A and 50E (and any other
   21700) share the same envelope, so swapping cells never changes the pack
   dimensions — only mass, energy and current rating (see §2.1 and §6.1). This
   makes the bay layout cell-agnostic.

## 9. Sources

1. Molicel — *INR21700-P42A* product page and v4 data sheet;
   **21.7 mm maximum diameter, 70.2 mm maximum height, 70 g maximum mass**,
   45 A and 4200 mAh. `[M]`
2. Samsung SDI — *INR21700-50E* datasheet; 21.0 × 70.0 mm, 5000 mAh, 9.8 A continuous. `[M]`
3. lygte-info.dk — *Molicel INR21700-P42A* and *Samsung INR21700-50E* test/review (cell identity, capacity, mass). `[M]`
4. Guide `design/Salamandra-Design-Guide-v0.1.md` §9 (bay 190 × 70 × 32 mm, PROVISIONAL) and §10.1 (cruise ≈ 5 A, peak ≈ 20 A). `[D]`
5. docs/00-objectives-and-requirements.md §3.3 (pack masses 300/455/605/910 g). `[E]`
6. Standard hobby practice for XT60/JST-XH/nickel/PVC values — declared `[E]`; to be re-measured on in-service articles (highest-value contribution).

**Confidence convention:** `[M]` measured/published, `[D]` derived by calculation, `[E]` estimated on declared assumptions. The wrapper, nickel and connector values are `[E]` and the single most useful verification is a calliper measurement of a real cell + connector (contributions welcome).
