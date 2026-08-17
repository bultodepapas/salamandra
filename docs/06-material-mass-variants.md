# Material mass variants — Salamandra weight budget (F2-class tool)

**Revision 1.1** · 17 August 2026 · Tool: `calculations/mass_budget.py` (reproducible,
validated) · Companion to guide §7.1 and `docs/05-master-plan.md` F2 (P1/P2)

---

## 1. Purpose

Weight budget of the reference aircraft (Cruise, Article #1) under **three material
policies** — all PETG (the guide §7.1 baseline), wings + wingtips in **AERO PLA**
(LW-PLA foamed, Bambu PLA-Aero class), and all **PLA+** — plus a **per-part material
selection** for any mixture. The tool also covers the battery options (4S1P / 6S1P /
4S2P / 6S2P × Molicel P42A / Samsung 50E), the FC catalog (I-17), the FPV options
(I-19), motor, propeller, servo class and the V1 fin variant (ADR-0038).

The printed-part mass fractions are `[E]` placeholders to be replaced by CAD mass
properties in F2/P2 (OP-28); everything else is anchored to measured data.

## 2. Data model (all tagged)

| Item | Model | Tag |
|---|---|---|
| Materials (ρ, g/cm³) | PETG **1.27** · PLA 1.24 · PLA+ 1.24 · AERO PLA **0.68** (foamed, flow 0.60) | `[M]` (I-04) / `[E]` band 0.55–0.70 for AERO |
| Printed parts (PETG base) | core 165 g (30 %) + wings 341 g (62 %, 6 segments) + tips 44 g (8 %) + elevons 50 g (`[D]` ADR-0025, 2×25 g) = **600 g**; fin 48 g optional | `[E]` fractions / `[D]` elevons |
| Hybrid nose boom | 341 mm support span + 50 mm CORE insertion + printed cradle = **38.2 g**; fixed across material policies | `[E]` ADR-0040 / `balance_cg.py` |
| Material scaling | m_part(mat) = m_part(PETG) × ρ_mat/ρ_PETG (same geometry) | `[D]` |
| Elevon balance mass | m_b = 1.2 × m_elevons (ADR-0025: 25 g, 24 mm offset, 20 mm horn → 30 g/elevon) | `[D]` |
| Battery pack | n_cells × cell + 25 g packaging; P42A 70 g / 50E 68 g per cell | `[D]` (I-16, validated vs 445/433/305/297 g) |
| FC | I-17 catalog `[M]`: F405-WING-V2 25 g · F765-WING 26 g · F722-WING 25 g · SpeedyBee F405 12 g · F411-WSE 8.5 g · Foxeer 8.4 g; avionics row = 110 g + (m_FC − 17.4 g survey avg) | `[M]`/`[D]` |
| FPV | O4 32 g · **O4 Pro 37 g (reference)** · O4 Lite 8.2 g · legacy O3 39.4 g | `[M]` (I-19) |
| Fixed rows | motor 170 g (28-class, option) · ESC 35 g · servos 60 g (4×15, class 12–15; heavy 17–21 = 76 g, exceeds budget) · prop 40 g (APC-E 8×8; 9×6 45, 10×7 55) · carbon 70 g · hardware 20 g | `[E]` (guide §7.1) |
| Stall speed | V_stall = √(2W/(ρ·S·CL_max)), CL_max = 0.589 (I-07), S = 0.282 m² | `[D]` |

> **Baseline mass:** 1685.2 g uses the I-16 `[D]` P42A pack mass (445 g) and the
> ADR-0040 38.2 g hybrid boom. The guide and this document now use the same values.

## 3. Results — the three policies (6S1P P42A · O4 Pro · CLEAN)

| Config | AUW (g) | g/dm² | V_stall (km/h) | Printed (g) | Printed cost (€) `[E]` | Verdict |
|---|---:|---:|---:|---:|---:|---|
| **ALL PETG** (guide baseline) | **1685.2** | 59.8 | **45.9** | 600 | ≈ 12 | Stall over 45 — OP-24 lever required |
| **AERO WINGS** (CORE+rest PETG) | **1506.3** | 53.4 | **43.4** | 421 | ≈ 13 | Stall compliant; **divergence rejects it** |
| **AERO MAX** (wings+tips+elevons AERO) | **1455.2** | 51.6 | **42.6** | 398 | ≈ 13 | Stall compliant; structure not cleared |
| **PLA+** (all printed parts) | **1669.6** | 59.2 | **45.7** | 586 | ≈ 14 | Stall over 45; **ADR-0016 rejected material** |

Example option combinations (all validated runs of `mass_budget.py`):

| Scenario | AUW (g) | V_stall (km/h) |
|---|---:|---:|
| AERO WINGS · 4S1P P42A · V1 fin | 1414 | 42.0 |
| ALL PETG · 6S1P · O4 Lite | 1656 | 45.5 |
| AERO WINGS · 4S2P 50E | 1630 | 45.1 |
| AERO MAX · 6S1P · O3 legacy · V1 fin | 1506 | 43.4 |

Per-part × material matrix (mass, g, from the PETG base):

| part | PETG | PLA | PLA+ | AERO_PLA |
|---|---:|---:|---:|---:|
| core | 165.0 | 161.1 | 161.1 | 88.3 |
| wings (6 seg) | 341.0 | 332.9 | 332.9 | 182.6 |
| tips (2) | 44.0 | 43.0 | 43.0 | 23.6 |
| elevons (2) | 50.0 | 48.8 | 48.8 | 26.8 |
| fin (V1) | 48.0 | 46.9 | 46.9 | 25.7 |

## 4. Engineering flags (honest, not silent)

1. **AERO PLA wings are structurally softer** (E ≈ 1.0 GPa vs PETG 1.94 — I-04). The
   wing shell carries torsion (ADR-0015/0030) and the divergence criterion is
   V_div ≥ 1.5×V_NE on a forward-swept wing (I-05). **AERO WINGS / AERO MAX require a
   re-verification of G4/G6**. Revision 3 gives **V_div = 91.1 km/h** at the
   conservative end, below the 95 km/h cruise point: the present AERO wing is **not
   airworthy** despite its real mass benefit. Tracked in OP-28.
2. **PLA+ is rejected by ADR-0016** (softer than PLA, no thermal gain) — the PLA+
   column is computed for experimentation only and is not a recommendation. Its mass
   gain over PETG is negligible anyway (ρ 1.24 vs 1.27 → −2.4 %).
3. **Printing workflow:** AERO PLA requires **flow ratio ≈ 0.60** (docs/02 §1.7), never
   the PETG 0.95; mixed-material builds need per-part slicer profiles (by-part
   filament assignment). Print time scales with deposited *volume*, so the AERO wings
   save mass, not time.
4. **Elevon balance mass follows the elevon mass** (ADR-0025, derived): AERO elevons
   (26.8 g) need only 32.1 g of balance mass instead of 60 g — the aero_max gain
   includes this consistency.
5. **Battery note:** 4S2P P42A = 585 g and **6S2P = 865 g** (I-16 model) vs the old
   docs/00 `[E]` values — the
   script uses the measured-cell model; 6S2P stays out of the cruise envelope
   regardless (R-CG, OP-23).

## 5. Recommendation (engineering)

- **ALL PETG** remains the reference and the O1-efficiency baseline.
- **AERO WINGS is not cleared for flight:** the −179 g return does not compensate for
  V_div = 91.1 km/h in the conservative model. It remains a coupon/section experiment,
  not the first aircraft material policy.
- **AERO MAX** (−230 g) additionally lightens the elevons and their balance mass —
  only after the elevon-flutter chain (ADR-0025/0026, G7) is re-checked with the
  lighter, softer surface.
- **PLA+**: not recommended (ADR-0016); the column exists for completeness.

## 6. Reproduction

```bash
python3 calculations/mass_budget.py --config all          # the 4 policies
python3 calculations/mass_budget.py --config matrix       # per-part × material
python3 calculations/mass_budget.py --config aero_wings --battery 4S1P --fin
python3 calculations/mass_budget.py --config all_petg --fc F765-WING --fpv O4-Lite
```

Twelve validation cases (baseline 1685 g / 45.9 km/h, I-16 pack masses, material
scaling, shell sum, balance rule, stall compliance) — ALL PASS; a change that breaks
them is not accepted.

## 7. Evolution path

| Item | Today | Replaced by | At |
|---|---|---|---|
| Printed-part fractions (165/341/44 g) | `[E]` | CAD mass properties (Fusion 360, P2) | F2 |
| AERO E / G data | `[E]` 1.0 GPa | Measured coupon (I-04 extension) or flight | F4/E5 |
| Pack masses 4S2P/6S2P | `[D]` model | Measured packs (E-series bench) | F2 |
| FC/FPV/motor catalogs | `[M]`/`[E]` | Component additions as PRs | continuous |

**OP-28** tracks the open items (CAD fractions, AERO divergence re-check).
