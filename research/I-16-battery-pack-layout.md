# I-16 — Battery pack layout: physical envelope of 4S / 6S · 21700 Li-Ion

**Status:** Open — sizing baseline · **Feeds:** guide §9 (battery and bay), `balance_cg.py` OP-01/OP-23, docs/00 §3.3 R-CG

## 1. Objective and scope

This thread establishes, from reproducible calculation (`[D]`), the **physical
dimensions of every admissible rectangular layout** of a 4-cell (4S) and a 6-cell
(6S) pack of cylindrical **21700 Li-Ion** cells, together with the assembly
allowances from wrapper, nickel interconnects and wiring/terminals.

It answers, with numbers, the question "which physical arrangements of the cells
are possible, and which ones fit the reference battery bay?" for the four packs
of the mission table (docs/00 §3.3): **4S1P, 6S1P, 4S2P, 6S2P**.

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
analysis.

## 3. Method — the layout model

A pack is an **N-cell rectangular block** of cells all lying with their axes
horizontal (never standing, which would put the 70 mm length on the vertical and
is unusable in a 32 mm bay). The block is described by three integers:

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

### Fit test against the reference bay

The Salamandra reference bay (guide §9, PROVISIONAL) is a horizontal channel
`190 × 70 × 32 mm` (x · y · z), **single 21 mm layer, never stacked**. A pack fits
iff:

1. pack **Height ≤ 32 mm** (vertical envelope → enforces `n_z = 1`), and
2. the horizontal footprint (Length, Width) fits in `190 × 70`, allowing
   Length/Width swap (rotation in the horizontal plane only).

This is implemented in `fits()` in the calculator.

## 4. Complete envelope table — 4S (4 cells)

`D` = derived from §2/§3 inputs. "Cell block" = raw array; "Pack" = finished with
assembly allowances. "Fits" = fits the `190 × 70 × 32` reference bay.

| Arrangement `n_x·n_y·n_z` | Orient. | Cell block L×W×H (mm) | **Pack L×W×H (mm)** | Fits bay |
|---|---|---|---|---|
| 2×2×1 | A | 140.6 × 42.6 × 21.3 | **153.2 × 43.2 × 22.2** | ✅ |
| 2×2×1 | B | 42.6 × 140.6 × 21.3 | **55.2 × 141.2 × 22.2** | ✅ |
| 4×1×1 | A | 281.2 × 21.3 × 21.3 | 293.8 × 21.9 × 22.2 | ❌ |
| 4×1×1 | B | 85.2 × 70.3 × 21.3 | 97.8 × 70.9 × 22.2 | ❌ |
| 1×4×1 | A | 70.3 × 85.2 × 21.3 | 82.9 × 85.8 × 22.2 | ❌ |
| 1×4×1 | B | 21.3 × 281.2 × 21.3 | 33.9 × 281.8 × 22.2 | ❌ |
| 2×1×2 | A | 140.6 × 21.3 × 42.6 | 153.2 × 21.9 × 43.5 | ❌ (stacked) |
| 1×2×2 | A | 70.3 × 42.6 × 42.6 | 82.9 × 43.2 × 43.5 | ❌ (stacked) |
| 2×1×2 | B | 42.6 × 70.3 × 42.6 | 55.2 × 70.9 × 43.5 | ❌ (stacked) |
| 1×2×2 | B | 21.3 × 140.6 × 42.6 | 33.9 × 141.2 × 43.5 | ❌ (stacked) |
| 1×1×4 | A | 70.3 × 21.3 × 85.2 | 82.9 × 21.9 × 86.1 | ❌ (stacked) |
| 1×1×4 | B | 21.3 × 70.3 × 85.2 | 33.9 × 70.9 × 86.1 | ❌ (stacked) |

**Only two 4S layouts fit the reference bay**, both single-layer:

- **4S 2×2×1 orient. A** → **153 × 43 × 22 mm** (2 cells end-to-end along length,
  2 across width). The compact square pack. **Recommended 4S1P geometry.**
- **4S 2×2×1 orient. B** → 55 × 141 × 22 mm (rotated in the bay). Same 2×2 block
  read on its side.

The linear sticks (4×1 and 1×4) exceed either the 190 mm length or the 70 mm width
and do not fit.

## 5. Complete envelope table — 6S (6 cells)

| Arrangement `n_x·n_y·n_z` | Orient. | Cell block L×W×H (mm) | **Pack L×W×H (mm)** | Fits bay |
|---|---|---|---|---|
| 2×3×1 | A | 140.6 × 63.9 × 21.3 | **153.2 × 64.5 × 22.2** | ✅ |
| 3×2×1 | A | 210.9 × 42.6 × 21.3 | 223.5 × 43.2 × 22.2 | ❌ |
| 2×3×1 | B | 42.6 × 210.9 × 21.3 | 55.2 × 211.5 × 22.2 | ❌ |
| 3×2×1 | B | 63.9 × 140.6 × 21.3 | 76.5 × 141.2 × 22.2 | ❌ |
| 6×1×1 | A | 421.8 × 21.3 × 21.3 | 434.4 × 21.9 × 22.2 | ❌ |
| 6×1×1 | B | 127.8 × 70.3 × 21.3 | 140.4 × 70.9 × 22.2 | ❌ |
| 1×6×1 | A | 70.3 × 127.8 × 21.3 | 82.9 × 128.4 × 22.2 | ❌ |
| 1×6×1 | B | 21.3 × 421.8 × 21.3 | 33.9 × 422.4 × 22.2 | ❌ |
| 3×1×2 | A | 210.9 × 21.3 × 42.6 | 223.5 × 21.9 × 43.5 | ❌ (stacked) |
| 1×3×2 | A | 70.3 × 63.9 × 42.6 | 82.9 × 64.5 × 43.5 | ❌ (stacked) |
| 3×1×2 | B | 63.9 × 70.3 × 42.6 | 76.5 × 70.9 × 43.5 | ❌ (stacked) |
| 1×3×2 | B | 21.3 × 210.9 × 42.6 | 33.9 × 211.5 × 43.5 | ❌ (stacked) |
| 2×1×3 | A | 140.6 × 21.3 × 63.9 | 153.2 × 21.9 × 64.8 | ❌ (stacked) |
| 1×2×3 | A | 70.3 × 42.6 × 63.9 | 82.9 × 43.2 × 64.8 | ❌ (stacked) |
| 2×1×3 | B | 42.6 × 70.3 × 63.9 | 55.2 × 70.9 × 64.8 | ❌ (stacked) |
| 1×2×3 | B | 21.3 × 140.6 × 63.9 | 33.9 × 141.2 × 64.8 | ❌ (stacked) |
| 1×1×6 | A | 70.3 × 21.3 × 127.8 | 82.9 × 21.9 × 128.7 | ❌ (stacked) |
| 1×1×6 | B | 21.3 × 70.3 × 127.8 | 33.9 × 70.9 × 128.7 | ❌ (stacked) |

**Exactly one 6S layout fits the reference bay:**

- **6S 2×3×1 orient. A** → **153 × 64 × 22 mm** (2 cells end-to-end along length,
  3 across width). This is the physical envelope of the **6S1P reference pack**
  (guide §9). Its length **153 mm** is comfortably inside the 190 mm bay, its width
  64 mm inside 70 mm, height 22 mm inside 32 mm.

All stacked arrangements (any `n_z ≥ 2`) exceed the 32 mm vertical envelope and
are excluded by the single-layer rule — the "stack of 4 / stack of 6" pack shapes
are geometrically valid (heights 43.5–128.7 mm) but **cannot be installed in this
bay**; they belong to a different, taller fuselage.

## 6. Pack-level summary (single-layer candidates)

| Pack | Arrangement | Orientation | Pack L×W×H (mm) | Envelope (mL) | Mass (cells) | Nominal energy |
|---|---|---|---|---|---|---|
| 4S | 4×1×1 | A | 293.8 × 21.9 × 22.2 | 143 | 272 g | 72 Wh |
| 4S | **2×2×1** | **A** | **153.2 × 43.2 × 22.2** | 147 | 272 g | 72 Wh ✅ |
| 4S | 4×1×1 | B | 97.8 × 70.9 × 22.2 | 154 | 272 g | 72 Wh |
| 4S | 1×4×1 | A | 82.9 × 85.8 × 22.2 | 158 | 272 g | 72 Wh |
| 4S | 2×2×1 | B | 55.2 × 141.2 × 22.2 | 173 | 272 g | 72 Wh ✅ |
| 4S | 1×4×1 | B | 33.9 × 281.8 × 22.2 | 212 | 272 g | 72 Wh |
| 6S | 6×1×1 | A | 434.4 × 21.9 × 22.2 | 211 | 408 g | 108 Wh |
| 6S | 3×2×1 | A | 223.5 × 43.2 × 22.2 | 214 | 408 g | 108 Wh |
| 6S | **2×3×1** | **A** | **153.2 × 64.5 × 22.2** | 219 | 408 g | 108 Wh ✅ |
| 6S | 6×1×1 | B | 140.4 × 70.9 × 22.2 | 221 | 408 g | 108 Wh |
| 6S | 1×6×1 | A | 82.9 × 128.4 × 22.2 | 236 | 408 g | 108 Wh |
| 6S | 3×2×1 | B | 76.5 × 141.2 × 22.2 | 240 | 408 g | 108 Wh |

The **2×2 (4S)** and **2×3 (6S)** single-layer packs are the volume-optimal layouts
that also satisfy the bay; the square/rectangular 2-cell-deep footprint is what the
current 190 × 70 bay was sized for. Mass shown is cell-only; finished packs add
≈ 20–40 g of nickel, wiring, connector and wrap, consistent with docs/00 §3.3
(4S1P ≈ 300 g, 6S1P ≈ 455 g).

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

## 8. Findings and open points

1. **6S1P reference envelope = 153 × 64 × 22 mm** (2×3, orient. A). Fits the
   current bay with 37 mm length, 6 mm width and 10 mm height to spare.
2. **Only one 6S layout and two 4S layouts fit the 190 × 70 × 32 bay.** The bay
   shape is optimal for exactly the 2-cells-deep rectangular footprint.
3. **Stacked packs (n_z ≥ 2) do not fit** a 32 mm bay — the "stack of 4/6" shapes
   require a taller fuselage (43.5–128.7 mm height).
4. **Discrepancy note (OP-23 / F2):** `balance_cg.py` uses `PACK_LEN = 0.084 m`
   (84 mm) as the 6S1P pack length. The finished 6S1P pack measured here is
   **≈ 153 mm long**. The bay (190 mm) is long enough, but the pack-length
   placeholder used to size the bay and pack stations should be updated to the
   real 153 mm (or kept at 84 mm only if a different single-file arrangement is
   intended, which §5 shows does not fit the 70 mm width). **Re-derive bay length
   and pack-station map in F2.**
5. **4S1P fit:** the 2×2 (153 × 43 × 22 mm) pack is shorter but the 43 mm width
   vs the 70 mm bay leaves room; it fits. The 4S2P (2×2×2, two layers) does **not**
   fit the 32 mm single-layer bay (height 43.5 mm) — consistent with docs/00
   §3.3 (4S2P flagged for F2) and OP-23.

## 9. Sources

1. Molicel — *INR21700-P42A* product page / datasheet; 21.0 × 70.0 mm, 45 A, 4200 mAh. `[M]`
2. Samsung SDI — *INR21700-50E* datasheet; 21.0 × 70.0 mm, 5000 mAh, 9.8 A continuous. `[M]`
3. lygte-info.dk — *Molicel INR21700-P42A* and *Samsung INR21700-50E* test/review (cell identity, capacity, mass). `[M]`
4. Guide `design/Salamandra-Design-Guide-v0.1.md` §9 (bay 190 × 70 × 32 mm) and §10.1 (cruise ≈ 5 A, peak ≈ 20 A). `[D]`
5. docs/00-objectives-and-requirements.md §3.3 (pack masses 300/455/605/910 g). `[E]`
6. Standard hobby practice for XT60/JST-XH/nickel/PVC values — declared `[E]`; to be re-measured on in-service articles (highest-value contribution).

**Confidence convention:** `[M]` measured/published, `[D]` derived by calculation, `[E]` estimated on declared assumptions. The wrapper, nickel and connector values are `[E]` and the single most useful verification is a calliper measurement of a real cell + connector (contributions welcome).
