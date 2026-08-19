# Material mass variants — Salamandra weight budget (F2-class tool)

**Revision 1.3** · 18 August 2026 · Tool: `calculations/mass_budget.py` (reproducible,
validated) · Companion to guide §7.1 and `docs/05-master-plan.md` F2 (P1/P2)

---

## 1. Purpose

Weight budget of the reference aircraft (Cruise, Article #1) under **three material
policies** — all PETG (the guide §7.1 baseline), wings + wingtips in **AERO PLA**
(LW-PLA foamed, Bambu PLA-Aero class), and all **PLA+** — plus a **per-part material
selection** for any mixture. Article #1 is 6S1P; other packs remain calculation options
for future platform modules. The tool also covers the FC catalog, FPV, propulsion,
servo and V1-fin options.

The printed-part mass fractions are `[E]` placeholders to be replaced by CAD mass
properties in F2/P2 (OP-28); everything else is anchored to measured data.

## 2. Data model (all tagged)

| Item | Model | Tag |
|---|---|---|
| Materials (ρ, g/cm³) | PETG **1.27** · PLA 1.24 · PLA+ 1.24 · AERO PLA **0.68** (foamed, flow 0.60) | `[M]` (I-04) / `[E]` band 0.55–0.70 for AERO |
| Printed parts | v0.2 raw estimate 600 g is retained as a regression input. Article #1 CLEAN applies a **550 g PETG CAD cap**: core 150.1 + wings/fixed trailing-edge bridges 314.8 + tips 40.0 + moving elevons 45.0. V1a adds 40.85 g for two shells/mounts, 7.67 g for two external LE spars and 10.68 g for two aft carbon booms | ADR-0038/0043/0045, I-29 `[E]` |
| Hybrid nose boom | Current ≈322 mm support span + 50 mm CORE insertion + printed cradle = **37.4 g** allocation | `[D]`/`[E]` ADR-0043 / `balance_cg.py` |
| Material scaling | m_part(mat) = m_part(PETG) × ρ_mat/ρ_PETG (same geometry) | `[D]` |
| Elevon balance mass | m_b = 1.2 × m_elevons (ADR-0025/0045: 22.5 g moving surface, 24 mm offset, 20 mm horn → 27 g/elevon) | `[D]` |
| Battery pack | n_cells × cell + 25 g packaging; P42A 70 g / 50E 68 g per cell | `[D]` (I-16, validated vs 445/433/305/297 g) |
| FC | Article #1 SpeedyBee F405 WING = **20.3 g** (8.9 FC + mandatory 11.4 PDB/current board; wireless omitted). Avionics row = 110 + (20.3 − 17.4) = 112.9 g | I-17 `[M]`/`[D]` |
| FPV | Article #1 **DJI O4 Air Unit 8.95 g installed** = E18 camera 3.10 g + E19 VTX/attached-antenna assembly 5.85 g; the antenna is not a separate layout body. O4 Pro is 36.2 g installed. | I-19 `[M]`/`[D]` |
| Fixed rows | motor 170 `[E]` · ESC 35 `[E]` · 2× Corona servo 25 `[M]` · APC E 8×8 assembly 25 (15 blade `[M]` + 10 adapter `[E]`) · carbon 70 `[E]` · hardware 20 `[E]` | ADR-0043 |
| Stall speed | V_stall = √(2W/(ρ·S·CL_max)), CL_max = 0.589 (I-07), S = 0.282 m² | `[D]` |

> **Reference mass:** 1553.25 g CLEAN uses the I-16 P42A pack (445 g), selected
> Article #1 equipment and the coupled 37.4 g boom. The released 1685.2 g v0.2 case is
> retained as an automated regression, not as the current build.

## 3. Results — the material policies (6S1P P42A · Article #1 equipment · CLEAN)

| Config | AUW (g) | g/dm² | V_stall (km/h) | Printed (g) | Printed cost (€) `[E]` | Verdict |
|---|---:|---:|---:|---:|---:|---|
| **ALL PETG** (guide baseline) | **1553.25** | 55.1 | **44.1** | 550 | ≈ 11 | **Article #1 CLEAN; compliant** |
| **AERO WINGS** (CORE+rest PETG) | **1388.4** | 49.2 | **41.7** | 385 | ≈ 12 | Mass passes; **divergence rejects it** |
| **AERO MAX** (wings+tips+elevons AERO) | **1342.4** | 47.6 | **41.0** | 364 | ≈ 12 | Structure not cleared |
| **PLA+** (all printed parts) | **1539.0** | 54.6 | **43.9** | 537 | ≈ 13 | ADR-0016 rejected material |

Example option combinations (all validated runs of `mass_budget.py`):

| Scenario | AUW (g) | V_stall (km/h) |
|---|---:|---:|
| ALL PETG · Article #1 CLEAN | 1553.25 | 44.1 |
| ALL PETG · V1 allocation target | 1613.25 | 44.9 |
| **ALL PETG · V1 current lower model** | **1612.45** | **44.9 — analytical PASS; 7.9 g below exact stall-mass ceiling** |

Per-part × material matrix (mass, g, from the PETG base):

| part | PETG | PLA | PLA+ | AERO_PLA |
|---|---:|---:|---:|---:|
| core | 150.1 | 146.6 | 146.6 | 80.4 |
| wings + fixed TE bridges | 314.8 | 307.4 | 307.4 | 168.6 |
| tips (2) | 40.0 | 39.1 | 39.1 | 21.4 |
| moving elevons (2) | 45.0 | 43.9 | 43.9 | 24.1 |
| fin (V1) | 37.3 | 36.4 | 36.4 | 20.0 |

## 4. Engineering flags (honest, not silent)

1. **AERO PLA wings are structurally softer** (E ≈ 1.0 GPa vs PETG 1.94 — I-04). The
   wing shell carries torsion (ADR-0015/0030) and the divergence criterion is
   V_div ≥ 1.5×V_NE on a forward-swept wing (I-05). **AERO WINGS / AERO MAX require a
   re-verification of G4/G6**. Revision 4 gives **V_div = 91.6 km/h** at the
   conservative end, below the 95 km/h cruise point: the present AERO wing is **not
   airworthy** despite its real mass benefit. Tracked in OP-28.
2. **PLA+ is rejected by ADR-0016** (softer than PLA, no thermal gain) — the PLA+
   column is computed for experimentation only and is not a recommendation. Its mass
   gain over PETG is negligible anyway (ρ 1.24 vs 1.27 → −2.4 %).
3. **Printing workflow:** AERO PLA requires **flow ratio ≈ 0.60** (docs/02 §1.7), never
   the PETG 0.95; mixed-material builds need per-part slicer profiles (by-part
   filament assignment). Print time scales with deposited *volume*, so the AERO wings
   save mass, not time.
4. **Elevon balance mass follows the elevon mass** (ADR-0025/0045, derived): AERO elevons
   (24.1 g) need only 28.9 g of balance mass instead of 54 g — the aero_max gain
   includes this consistency.
5. **Battery note:** 4S2P P42A = 585 g and **6S2P = 865 g** (I-16 model) vs the old
   docs/00 `[E]` values — the
   script uses the measured-cell model; 6S2P stays out of the cruise envelope
   regardless (R-CG, OP-23).

## 5. Recommendation (engineering)

- **ALL PETG at the 550 g shell cap** remains the reference and closes C16 without
  introducing the divergence penalty of a softer wing.
- **AERO WINGS is not cleared for flight:** the −164.8 g return does not compensate for
  V_div = 91.6 km/h in the conservative model. It remains a coupon/section experiment,
  not the first aircraft material policy.
- **AERO MAX** (−210.8 g) additionally lightens the elevons and their balance mass —
  only after the elevon-flutter chain (ADR-0025/0026, G7) is re-checked with the
  lighter, softer surface.
- **PLA+**: not recommended (ADR-0016); the column exists for completeness.

## 6. Reproduction

```bash
python3 calculations/mass_budget.py --config all          # the 4 policies
python3 calculations/mass_budget.py --config matrix       # per-part × material
python3 calculations/mass_budget.py --config aero_wings --battery 4S1P --fin
python3 calculations/mass_budget.py --config all_petg --fc F765-WING --fpv O4-Air-Unit
```

Validation preserves the v0.2 1685.2 g / 45.9 km/h regression and checks the current
CLEAN and V1 target/model separation, pack masses, material scaling and balance rule.
The V1 analytical lower model is 5.83 g above the allocation target yet remains 24.6 g
below the exact 45 km/h mass limit. Its exact battery target is 2.72 mm outside the
allowed travel, while the achieved CG remains inside the R-CG band; that physical
closure remains open.

## 7. Evolution path

| Item | Today | Replaced by | At |
|---|---|---|---|
| Printed-part caps (150.1/314.8/40.0/45.0 g) | `[E]` | CAD mass properties (Fusion 360, P2) | F2 |
| AERO E / G data | `[E]` 1.0 GPa | Measured coupon (I-04 extension) or flight | F4/E5 |
| Pack masses 4S2P/6S2P | `[D]` model | Measured packs (E-series bench) | F2 |
| FC/FPV/motor catalogs | `[M]`/`[E]` | Component additions as PRs | continuous |

**OP-28** tracks the open items (CAD fractions, AERO divergence re-check).
