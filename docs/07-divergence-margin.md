# Salamandra — Absolute divergence margin

**Revision 3.0** · 17 August 2026 · Tool: `calculations/divergence.py`
**Configuration:** ADR-0040 planform, Λc/4 = −15°
**Validation:** all internal numerical and regression cases pass; FEM and independent
flux-form shooting solutions agree within 0.1 % on the real tapered wing.

---

## 1. Design status

The structural criterion is **Vdiv ≥ 1.5 VNE = 240 km/h**. The nominal model passes,
but the conservative unmeasured structure fails. Therefore the criterion is **not
closed**, and the first-flight operating limit is **105 km/h**. A 150 km/h limit is
conditional on measured in-plane stiffness. Neither number replaces E7 flight-envelope
expansion.

Revision 3 also corrects a conceptual error in revision 2: the centroid of the enclosed
cell areas is not the shear centre of this multicell printed section. It is retained only
as a geometry diagnostic. The elastic axis is now an explicit uncertainty that must be
measured.

## 2. Model and evidence

| Element | Revision-3 model | Evidence/status |
|---|---|---|
| Planform | b = 1.300 m, S = 0.282 m², taper 0.50, Λc/4 = −15° | `design_config.py`, ADR-0040 |
| Section | Closed box x/c 0→0.72, web at 0.30; hinge cell excluded | guide §6.2, ADR-0002 |
| Geometry | Real `mh60-135.dat`; multicell Bredt-Batho compatibility; J = 3.17×10⁻⁷ m⁴ root to 1.81×10⁻⁸ m⁴ tip | `[D]` |
| Skin/web | 0.9 mm, 2 perimeters | ADR-0028 |
| G_eff | 0.55 GPa nominal; ±35 % band | `[M]` anchor / `[E]` transfer, G4 |
| Elastic axis | xEA/c = 0.35 nominal; 0.30 optimistic; 0.45 conservative | `[E]`, replaces false shear-centre claim |
| Cell-area centroid | x/c = 0.353 | Geometry diagnostic only; **not** an elastic axis |
| Lift slope | 9.7 rad⁻¹ nominal; 6.28–11.2 band | in-repo provisional-profile polars `[D]` |
| Forward-sweep factor | 0.70 nominal; 0.55 conservative; 0.85 optimistic at −15° | NASA TP-1685 trend; numerical transfer `[E]` |
| Joint | Discrete spring at y = 195 mm, k = 5× local section | ADR-0032 |
| Carbon tube | Ø12×1.0 mm, pultruded-UD G12 = 3–7 GPa | `[E]`; eigenvalue effect quantified |

NASA TP-1685 tested/calculated aspect-ratio 4 and 8 forward-swept wings and shows that
reducing the magnitude of forward sweep increases divergence dynamic pressure/speed.
That evidence supports the direction and ranking used in ADR-0040, not a direct transfer
of the NASA configurations' absolute values. Primary source:
[NASA NTRS 19800020786](https://ntrs.nasa.gov/citations/19800020786).

## 3. Results

| Case | Vdiv (km/h) | Margin to 240 km/h | Verdict |
|---|---:|---:|---|
| **Nominal** | **325.3** | **1.36×** | PASS as a sensitivity reference |
| **Conservative, unmeasured baseline** | **128.8** | **0.54×** | **FAIL — governing pre-test case** |
| Optimistic | 847.0 | 3.53× | Non-design case |
| Conservative + fully bonded carbon tube | 135.9 | 0.57× | FAIL; only +5.5 % |
| **AERO LW-PLA panels, conservative** | **91.1** | **0.38×** | **FAIL — below design cruise** |

The broad range is not statistical confidence. It is a sensitivity envelope over
unmeasured G, elastic-axis location, section lift slope and the forward-sweep factor.
Quoting 325.3 km/h without the 128.8 km/h case is prohibited.

## 4. Real-print sensitivities

| Lever at the conservative end | Vdiv | Change |
|---|---:|---:|
| Baseline | 128.8 km/h | — |
| Gyroid contribution, +10 % GJ `[E]` | 135.1 km/h | +5 % |
| Wall 0.9 → 1.1 mm | 141.1 km/h | +10 % |
| In-plane GXY = 0.69 GPa `[D]` | 179.0 km/h | +39 % |
| GXY + gyroid + 1.1 mm wall | 206 km/h | +60 %; **still below 240** |

The previous revision's 242 km/h combined result is superseded. The new result is lower
because the conservative elastic-axis arm is no longer replaced by the enclosed-area
centroid. This is the correct treatment until S3 measures the section.

Secondary findings remain useful:

- The fully bonded carbon tube raises conservative Vdiv by only 5.5 %; treating it as a
  bending member for the system-level eigenvalue remains justified.
- The distributed y = 195 mm joint gives a 12.0 % penalty at k = 5× and 37.7 % at k = 1×.
  R-JOINT ≥ 5× remains binding.
- AERO LW-PLA panels cannot be accepted on mass benefit alone. Their conservative
  91.1 km/h result is below the 95 km/h cruise design point.

## 5. Operating limit derivation

Use a pre-measurement clearance factor of **0.85** and round downward to the next
5 km/h increment:

```text
unmeasured baseline: 0.85 × 128.8 = 109.5 km/h → V_limit = 105 km/h
GXY validated:       0.85 × 179.0 = 152.1 km/h → V_limit = 150 km/h
```

The 105 km/h limit covers the 95 km/h design cruise with 10 km/h of operational
headroom. It does not clear the 160 km/h article VNE. Do not raise the limit from a
favourable material data sheet alone: the coupon orientation, wall process and geometry
must represent the actual wing.

## 6. Closure tests

1. **S3 coupon:** measure GXY on the actual printer/material/process and compare with the
   0.69 GPa conditional model.
2. **Section/wing torsion:** measure GJ on a representative closed cell including web,
   gyroid, seams and bonded tube.
3. **Elastic axis:** apply known transverse loads at several chord stations and locate
   the no-twist load line; replace the xEA/c bracket with measured data.
4. **E7 flight expansion:** pitot + blackbox, incremental speed gates and Southwell
   extrapolation. This is the final divergence closure.

If the conservative recalculation after S3 remains below the required 240 km/h, the
available design levers are: thicker/tailored panel walls, a torsion member sized for GJ,
or a lower VNE. The −15° sweep has already captured the highest-return planform change
that stays inside the declared trim-authority cap.

## 7. Reproduction

From the repository root:

```powershell
python calculations\design_config.py
python calculations\divergence.py
python calculations\sweep_trade.py --full
```

All validation lines must report `PASS`. Any change to sweep, section, material, wall,
station geometry, joint stiffness or elastic-axis evidence requires rerunning the suite
and updating this document before the result is cited.
