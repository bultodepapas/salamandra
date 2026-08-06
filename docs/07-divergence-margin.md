# Salamandra — Absolute Divergence Margin (G6 first pass)

**Revision 2.0** · 6 August 2026 · Tool: `calculations/divergence.py` (14 validation cases,
**ALL PASS**, two independent methods agree within 0.07 %; **real profile geometry**
from `geometry/airfoils/mh60-135.dat`)

---

## 1. Why this document exists

ADR-0030 states that *"the divergence criterion V_div ≥ 1.5 × V_NE is met with the shell
alone"* — but until now **no calculation produced the absolute value**: I-05 gives only a
RELATIVE scaling anchor to the Peregrine (GJ 6.45×, V_div 1.14×) and explicitly says *"it
does not give the absolute value"*. The divergence of a forward-swept wing is the
project's **dominant risk** (I-05, G4/G6 — declared the weakest link in the master plan,
S3/S4). This document is the first absolute, reproducible estimate of V_div.

## 2. Model (`divergence.py` — first pass, S3/CAD remains the closure trigger)

| Element | Model | Source |
|---|---|---|
| Section | Torsion box x/c 0 → 0.72 (D-box 0→0.30 + center cell 0.30→0.72, common web at 0.30); hinge cell excluded ("the closed torsion box ends here") | guide §6.2, ADR-0002 |
| **Geometry** | **REAL profile coordinates (mh60-135.dat): cell areas A1 = 0.0310c², A2 = 0.0415c², perimeters from the actual arcs, shear centre x/c = 0.353 → e = 0.103c, computed per station scaled to the local t/c** (the earlier k_h = 0.8 rectangle idealization validated within 0.4 % — area −6.7 % cancels against the shorter arc perimeters) | `geometry/airfoils/mh60-135.dat` |
| Skin | 0.9 mm (2 perimeters, ADR-0028); web 0.9 mm | ADR-0028 |
| J | Multi-cell Bredt-Batho, exact compatibility solution, real areas/perimeters | §5.2 station table |
| G_eff | **0.55 GPa `[M]`** printed PETG, band ±35 % `[E]` (G4). Literature: in-plane G ≈ E/2(1+ν) = 1.94/2.72 ≈ **0.69–0.72 GPa** (the wing skin loads torsion IN the layer plane; Sadaghian 2022's ~0.24 GPa applies to cylinders loaded ACROSS layers — the worst orientation, not this load path) | ADR-0021, ADR-0030, Özen 2021, CNC Kitchen E 1.9 GPa |
| Section lift slope a | 9.7 /rad nominal, band 6.28–11.2 `[D]` | in-repo XFOIL polars MH60→13.5 % |
| Solver | FEM weak form **cross-checked by an independent flux-form shooting method — 0.07 % agreement** (C2) | — |
| Sweep factor | k_sweep = 0.50–0.70 for −20° `[E]` (G6) | I-05, I-12 (open) |
| Joint | R-JOINT discrete spring at y = 195, k = 5× section (series compliance in the joint element) | ADR-0032 |
| Carbon tube | Ø12×1.0, G_12 pultruded UD 3–7 GPa `[E]` — quantified: +5.5 % max | ADR-0015 |

**Criterion:** V_div ≥ 1.5 × V_NE = 1.5 × 160 km/h = **240 km/h** (docs/00).

## 3. Results (real geometry)

| Case | V_div | Margin vs 240 km/h | Verdict |
|---|---:|---:|---|
| **Nominal** | **275.6 km/h** | **1.15×** | **PASS** (barely) |
| **Conservative end** (G −35 %, a 11.2, k_sweep 0.50, area −5 %, e 0.12) | **151.5 km/h** | **0.63×** | **FAIL** |
| Optimistic end | 521.1 km/h | 2.17× | PASS |
| **AERO LW-PLA wings** (conservative end) | **107.1 km/h** | **0.45×** | **FAIL — below the 95 km/h design cruise** |

The published claim (ADR-0030, "criterion met with the shell alone") is **falsified at
both the nominal and the conservative ends of the declared bands**. The nominal margin
of 1.15× is thin; the conservative corner fails by a factor of 1.6.

## 4. Real-print factors absent from the baseline (literature sensitivity)

Designer's empirical report ("printed PETG with thin walls and low infill feels much
stiffer than simple calculations") quantified against published data:

| Factor | Evidence | Effect on V_div (conservative end) |
|---|---|---|
| **G in the skin plane** | E 1.94 GPa `[M]`, ν 0.35–0.40 → G_XY ≈ 0.69–0.72 GPa; the 0.55 GPa anchor is the conservative measured value, the −35 % band floor (0.36 GPa) is the least likely for this load path | 151.5 → **210.5 km/h** (+39 %) |
| Gyroid 5 % infill | No published torsion data at 5 %; Kati 2025 (Polymers): gyroid raises stiffness at 40–100 %; community torsion practice (Ultimaker forum) | +5 % (assumed +10 % GJ `[E]`) |
| Real wall thickness | 0.4 mm nozzle @ 0.2 layer → measured extrusion 0.45–0.55 mm; 2 perimeters = 0.9–1.1 mm | +10 % (J ∝ t) |
| **Combined best case** (G in-plane + gyroid + wall 1.1 mm) | — | **242 km/h — passes 240 by 2 km/h** |

**What this means:** the designer's experience has a quantitative basis — the in-plane
shear modulus alone moves the conservative end from 151 to 210 km/h. BUT even with
EVERY real-print factor favourable, the criterion is only touched (242 vs 240), not
guaranteed. The dominant residual uncertainty is the **sweep factor 0.50–0.70 `[E]`**
(I-12), which no material measurement resolves. The verdict stands: the criterion is
not assured with current data; S3 (measured section GJ) + I-12 (sweep factor) + E7
(Southwell) are the closures — and S3 now has a concrete expectation: **G_XY ≈
0.65–0.72 GPa, wall ≈ 1.0 mm, gyroid contribution ≤ 10 % → V_div ≈ 200–240 km/h**.

## 5. Secondary findings

- **Joint penalty (R-JOINT, ADR-0032):** distributed model at the real wing gives
  **−12.0 % at k = 5×** and −37.6 % at 1× — the lumped table (−9 %/−29 %) is slightly
  optimistic for this geometry. The requirement **R-JOINT ≥ 5× stands**.
- **Carbon tube "bending only" (ADR-0015) holds, quantified:** GJ_tube = 5.3 N·m² vs
  shell 6–235 N·m²; fully bonded it raises V_div only +5.5 % (the eigenvalue is
  root-dominated and the tube is absent inboard of y = 195).
- **Method bug caught by C2:** a first shooting implementation (θ′ continuity) converged
  to the WRONG equation (drops the GJ′·θ′ term; 3× error on the tapered wing). The flux
  form agrees with the FEM weak form to 0.07 %. Recorded in the validation discipline.
- **Real-geometry validation:** the k_h = 0.8 rectangle idealization matches the real
  profile J within 0.4 % (area −6.7 % cancels against shorter arc perimeters); the real
  shear centre is x/c = 0.353 (e = 0.103 c), slightly forward of the assumed 0.36.

## 6. Sensitivity (what moves the verdict)

| Lever | Effect | Status |
|---|---|---|
| **G_XY in the skin plane (S3)** | 0.55 → 0.69 GPa: +39 % on the conservative end | Measurable on a printed coupon (torsion of a printed tube/box) |
| Sweep factor (I-12) | ±20 % — the dominant unresolved `[E]` | I-12 execution + E7 Southwell plot |
| Skin thickness (2 → 3 perimeters) | J ∝ t → +22 % V_div | ADR-0028 revision, mass cost ≈ +200 g `[E]` |
| V_NE article #1 (160 → 130 km/h) | criterion 240 → 195 km/h | flight-program decision |
| Bonded tube | +5.5 % | already counted |

**The conservative verdict (151.5 km/h) is below V_NE itself (160 km/h).** Until S3
verifies the real section GJ and the sweep factor is bounded by I-12/E7, the wing must
be flown inside a **declared V_limit** — see the recommendation below.

## 7. Recommendation for the first flights

1. **Immediate (no hardware):** I-12 execution (sweep factor on this section's EI/GJ) and
   S3 first pass on the Fusion 360 section + a **printed torsion coupon** (the two terms
   that dominate the band; the coupon resolves the G_XY expectation of §4).
2. **Before article #1 flies:** declare **V_limit = 110 km/h** for the first test flights
   (conservative V_div 151.5 × 0.9 joint-aware margin), logged in the flight rules; the
   95 km/h cruise point stays below it with margin, the 160 km/h V_NE does NOT. If the
   S3 coupon confirms G_XY ≈ 0.69 GPa, V_limit can rise to ≈ 160 km/h (210.5 × 0.9).
3. **Structural option on the table:** 3 perimeters (1.35 mm skin) for the panels if the
   S3-verified GJ confirms the conservative end — +22 % V_div, ≈ +200 g (mass_budget.py
   to re-run; the AERO experiment is off the table until this closes: 107.1 km/h).
4. **E7 (Southwell plot)** remains the closing measurement — the flight test that turns
   this `[D]` estimate into a `[M]` divergence datum.

## 8. Reproduction

```bash
python3 divergence.py
```

14 model-validation cases must pass (ALL PASS on 2026-08-06). The criterion verdict is a
printed finding, not a check. The profile file `geometry/airfoils/mh60-135.dat` is an
input: any change to the section (guide §6.2), the material (ADR-0021), the stations
(§5.2), the profile or the joint (ADR-0032) must reproduce the validation suite before
the numbers are quoted.
