# I-04 — Printing materials

**Status:** Closed · **Feeds:** ADR-0016, ADR-0018, ADR-0021

## Question

Which filament maximizes torsional stiffness per gram, and what other criteria compete with it?

## Figure of merit

In a closed section, `GJ ∝ G·t` and `mass ∝ ρ·t`. Therefore the figure of merit is **G/ρ**.

| Material | E printed | G_eff | ρ | **G/ρ** | Relative |
|---|---|---|---|---|---|
| **Normal PLA** | 3.00 GPa `[M]` | 0.90 | 1.24 | **0.73** | **1.00** |
| PLA+ | 2.20 GPa `[M]` | 0.66 | 1.24 | 0.53 | 0.73 |
| ASA | 1.9–2.2 GPa `[E]` | 0.58 | 1.07 | 0.53 | 0.73 |
| LW-PLA | ~1.0 GPa `[E]` | 0.35 | 0.68 | 0.51 | 0.70 |
| **PETG** | **1.94 GPa** `[M]` | **0.55** | **1.27** | **0.43** | **0.59** |

**PETG is the worst of the five in specific torsional stiffness.** It is adopted anyway — see [ADR-0021](../decisions/ADR-0021-base-material.md).

## Primary data

### PLA vs PLA+ `[M]` — same manufacturer, same bench

Polymaker PolyLite (PLA) versus PolyMax (PLA+), controlled test:

| Test | PLA | PLA+ | Δ |
|---|---|---|---|
| Flat tensile | 57 MPa | 43 MPa | −25 % |
| Layer adhesion | 43 MPa (75 % of normal strength) | 75 % too | = |
| **Flexural modulus** | **3000 MPa** | **2200 MPa** | **−27 %** |
| Impact | 5 kJ/m², clean break | ~4× tougher | +300 % |
| **Thermal failure under load** | **65 °C** | **65 °C** | **0** |

Three counterintuitive conclusions:

1. **PLA+ is softer, not stiffer.** It sits at the level of PETG and ABS.
2. **It gains nothing in temperature.** It removes the only argument that would allow leaving PETG without losing thermal margin.
3. **Normal PLA layer adhesion is exceptional** — 75 % retention, when most materials show at least a 50 % penalty.

⚠️ A couple of brands, not the whole PLA+ universe. Solid trends; exact magnitudes of other brands may differ.

### PLA vs PETG `[M]` — paired dataset

Ultimaker, ASTM D3039, 100 % infill, 0.15 mm layer:

- XY modulus: **PLA 3250 ± 119 MPa · PETG 1939 ± 28 MPa**
- PETG notched Charpy: 7.9 ± 0.6 kJ/m² versus 3.9 ± 0.4 for PLA

### Z-direction retention `[M]` — same bench, same hooks

| Material | Flat | Standing | **Z retention** |
|---|---|---|---|
| PLA | 72 kg | 40 kg | **55 %** |
| PETG | 54 kg | 25 kg | **46 %** |
| ASA | 59 kg | 17 kg | **29 %** |

> **Correction C8.** It was claimed that PETG has better layer adhesion than PLA. **It is the opposite.** PETG wins on toughness, not adhesion.

### Does Z adhesion matter? `[D]`

Bredt torsion loads the layer joints in **interlaminar shear**. Calculation of the root torque at V_NE with a 5 g pull:

    τ = T / (2·A·t) ≈ 5 / (2 · 2.75×10⁻³ · 9×10⁻⁴) ≈ 1.0 MPa

Versus ~20 MPa of PETG interlaminar strength: **×20 margin**.

**Layer adhesion is not binding. The problem is stiffness, not strength.** This saved ASA from being discarded for its 29 %, and discarded it for another reason.

## Why each alternative is rejected

| Material | Reason for rejection |
|---|---|
| **PLA+** | −27 % stiffness with no thermal gain. An intermediate point that solves no constraint → ADR-0016 |
| **ABS** | Yellows and embrittles in the sun in a few months `[M]`. A wing lives outdoors → ADR-0018 |
| **ASA** | Real advantages (Tg 105 °C, acetone-weldable, sandable). **Rejected for warping**: geometric twist is a trim parameter, and a poorly repeatable material corrupts the variable that governs the balance |
| **LW-PLA** | Light but soft, expensive and delicate to handle. Reserved for non-structural parts |
| **Normal PLA** | Best stiffness of all. Discarded for Tg 55–60 °C and belly-landing brittleness. **It is the technical alternative if stiffness tightens** |

## Adhesives for PETG

> **Correction C9.** It was claimed that PETG cannot be glued. Too categorical.

| Option | Verdict |
|---|---|
| **3D-Gloop PETG** | Specific chemical weld. Outperformed cyanoacrylate **under torsion** with the parts held tight — which is the project's load case |
| **30-min epoxy** | Better raw strength. The 5-min ones are notably worse |
| DCM (dichloromethane) | True solvent weld, but **cat. 2 carcinogen and restricted by REACH in the EU**. Not recommended |
| Cyanoacrylate | Only a surface bond. Not structural on PETG |
| E6000 | **Fails.** The only one that could be separated by hand after curing |

## Reproduction warning

⚠️ LW-PLA print profiles carry `flow_ratio ≈ 0.60` to compensate for foaming. **When switching to PETG it must be raised to ~0.95**, or 40 % less material is deposited.

An example of the 840 mm Peregrine printed in PETG with the LW-PLA profile comes out **~1.6× stiffer in shear** than the intended design (G 0.55 versus 0.35) and **~2.2× heavier**.

## Sources

- CNC Kitchen — *The difference of PLA and PLA+ tested (feat. Polymaker)*
- CNC Kitchen — *Comparing PLA, PETG & ASA (feat. Prusament)*
- Ultimaker — paired PLA/PETG dataset, ASTM D3039 / ISO 179-1
- 3D-Fuel — comparative adhesive test
- 3DLabPrint — *Materials for 3D printing planes*
