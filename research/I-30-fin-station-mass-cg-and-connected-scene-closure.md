# I-30 — Fin station, mass, CG and connected-scene closure

**Date:** 2026-08-19  
**Status:** Reproducible analytical closure `[D]` on aerodynamic, material and installation
inputs `[E]/[I]`; F2 and E8 remain open  
**Applies to:** SALAMANDRA-V1a, ADR-0038, SLM-GA-002, SLM-FIN-001 and SLM-EQP-001

## 1. Purpose and correction sequence

This investigation implements the required dependency order. It does not choose a fin by
eye and then force the aircraft around the drawing.

1. Sweep fin aerodynamic-centre station relative to the released wing CG.
2. At each station, resize total vertical area to the same nominal `Cnβ` target.
3. Derive the trapezoid, booms, material volume, mass and assembly CG.
4. Select a mass- and extent-feasible station from the complete trade.
5. Add that assembly to the three-dimensional aircraft mass ledger.
6. Solve battery station. If physical travel is insufficient, extend the nose boom and
   cradle and feed their added mass into the next iteration.
7. Move the camera with the new forward cradle datum and move the O4 VTX only as far as
   required by the measured 50 mm camera-to-VTX coax constraint.
8. Rebuild the V1 fuselage OML from the resulting layout and project the same objects into
   the top, side and rear SVG views.

The current solution converges in two iterations. No SVG contains an independent fin,
propeller, battery, camera or VTX position.

## 2. Evidence boundary

Primary sources support the method, not a copied universal fin location:

- NACA's tailless-aircraft work shows that vertical-surface placement and directional
  stability must be evaluated for the actual tailless configuration. It is a warning
  against treating a generic tail-volume coefficient as proof of closure:
  <https://ntrs.nasa.gov/citations/19930092526>.
- NASA powered-model testing reports that propulsion can materially alter directional
  derivatives and does not provide a general preliminary-design correction applicable to
  every geometry. SALAMANDRA therefore retains the motor-off case and credits no
  unmeasured pusher-slipstream benefit:
  <https://ntrs.nasa.gov/citations/19730002289>.
- The X-48 programme demonstrates that a flying-wing vertical-tail arrangement is an
  airframe-specific integration decision rather than a decorative appendage:
  <https://www.nasa.gov/aeronautics/x-48b/>.
- FAA propeller installation guidance treats the propeller as an installation system with
  defined limitations. For this provisional model, a documented inflated hazard envelope
  is therefore used in addition to the nominal blade disk:
  <https://www.faa.gov/aircraft/air_cert/design_approvals/engine_prop/prop_prop_sa/prop_inst_req>.

The 16.0 mm radial allowance used below is a Salamandra engineering assumption, not an FAA
prescription. It remains `[E]/[I]` until runout, structural deflection and assembly
tolerances are measured at F2.

## 3. Aerodynamic station/area calculation

The released target CG is

\[
x_{CG}=-93.78395\;\mathrm{mm}.
\]

For each trial aerodynamic-centre station, the vertical-tail moment arm is

\[
l_v=x_{AC}-x_{CG}.
\]

`calculations/yaw_stability.py` solves total area `S_v` so the nominal complete-aircraft
derivative reaches `Cnβ = +0.00050/deg`. Thus moving the fin aft reduces required area but
increases boom length, aft extent, assembly-CG arm and forward battery demand. The trade is
not monotonic when all penalties are included.

| `x_AC` (mm) | `l_v` (mm) | `S_v,total` (dm²) | lower assembly (g) | boom length (mm) | aft extent (mm) | first-order battery shift (mm) | Feasible |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 225 | 318.8 | 4.0730 | 65.32 | 168.2 | 324.2 | 49.56 | No: mass |
| 250 | 343.8 | 3.7768 | 62.58 | 189.9 | 345.9 | 50.57 | No: mass |
| 275 | 368.8 | 3.5208 | 60.36 | 211.9 | 367.9 | 51.68 | No: mass |
| **280** | **373.8** | **3.4737** | **59.97** | **216.4** | **372.4** | **51.92** | **Yes; selected knee** |
| 300 | 393.8 | 3.2972 | 58.58 | 234.3 | 390.3 | 52.90 | Yes; higher coupled penalty |
| 325 | 418.8 | 3.1004 | 57.14 | 256.8 | 412.8 | 54.21 | No: aft extent |

The code scans every 5 mm from +225 to +325 mm, normalises area, lower mass, boom length,
aft extent and battery-shift penalties, and applies hard 60 g and +410 mm extent gates.
`x_AC = +280 mm` is the first mass-feasible point and the minimum-score feasible knee. It
is not inherited from the old drawing.

## 4. Selected swept trapezoid

The selected planform is fully constrained by total area, count, aspect ratio, taper,
leading-edge sweep and AC station:

| Quantity | Result | Authority |
|---|---:|---|
| Count | 2 | `[D]` architecture |
| Total / each area | 3.4737 / 1.7368 dm² | `[D]` from nominal target `[E]` |
| Aspect ratio each / taper | 2.00 / 0.45 | `[E]` |
| Span each | 186.38 mm | `[D]` |
| Root / tip chord | 128.54 / 57.84 mm | `[D]` |
| Leading-edge / quarter-chord sweep | 25.0° / 20.379° | `[E]` / `[D]` |
| Root LE / TE | +217.62 / +346.16 mm | `[D]` |
| Tip LE / TE | +304.53 / +362.38 mm | `[D]` |
| MAC | 97.66 mm | `[D]` |
| AC | +280.00 mm | `[D]` on target `[E]` |

This removes the former vertical-trailing-edge constraint and the artificial narrow tip.
The root fillet is contained inside the credited planform, so it cannot appear ahead of the
fin or inflate stability area.

## 5. Material volume and mass

The lower PETG shell/mount model uses an 0.85 mm effective thickness and a 10% local-mount
factor. With `ρ_PETG = 1270 kg/m³`:

\[
V_{PETG,lo}=S_v(0.00085)(1.10)=32.48\;\mathrm{cm^3},
\]

\[
m_{PETG,lo}=41.25\;\mathrm{g}.
\]

Two solid Ø3 mm aluminium leading-edge rods follow the derived 205.65 mm swept-edge
length and contribute 7.85 g. Two Ø6/4 mm carbon tubes use the derived 216.38 mm boom
length and contribute 10.88 g. Therefore:

\[
m_{module,lo}=41.25+7.85+10.88=59.97\;\mathrm{g}.
\]

The upper analytical band is 87.22 g. The lower model leaves only 0.03 g below the 60 g
allocation, so measured printed mass remains a mandatory F2 gate.

## 6. Propeller interference calculation

The propeller ledger defines an APC 8×8EP envelope at `x = +235 mm`, diameter 203.2 mm and
10.2 mm axial thickness. The boom centre is at `|y| = 140 mm`; its 18 mm width places the
inner boom face at radius 131.0 mm. Hence

\[
C_{nom}=131.0-101.6=29.4\;\mathrm{mm}.
\]

The provisional radial allowance is explicit and additive:

| Allowance | mm | Status |
|---|---:|---|
| blade/manufacturer geometry | 5 | `[E]` |
| shaft/runout | 1 | `[E]` |
| support deflection | 3 | `[E]` |
| assembly tolerance | 2 | `[E]` |
| residual reserve | 5 | `[I]` |
| **Total** | **16** | `[E]/[I]` |

Residual boom clearance is therefore 13.4 mm. The fin plane has 36.9 mm nominal and
20.9 mm residual clearance. The side projection has 20.2 mm axial overlap, but that is not
a collision: the rear projection proves the objects are laterally outside the inflated
disk. Status remains **ANALYTICAL PASS / F2 PHYSICAL OPEN**.

## 7. Coupled mass, CG and fuselage result

Adding the selected fin module shifts the required battery station forward. The original
travel is insufficient, so the iterative solver extends the nose tube and cradle. Their
linear mass is derived from the existing component ledger and fed back into CG:

| Coupled result | Value |
|---|---:|
| Iterations | 2 |
| Nose boom/cradle extension | 17.8065 mm |
| Added forward-support mass | 2.4048 g |
| V1 AUW | 1615.6288 g |
| Solved CG x / target x | −93.78395 / −93.78395 mm |
| Battery x | −386.7422 mm |
| Camera x | −463.7867 mm |
| VTX x | −429.6143 mm |
| O4 straight-line lower bound / maximum | 50.0 / 50.0 mm |
| CLEAN / V1 body OML length | 739.70 / 757.51 mm |
| V1 nose-to-aft-boom longitudinal extent | 864.88 mm |
| Analytical stall speed | 44.93 km/h |

The 50.0 mm O4 value is a centre-to-centre straight-line lower bound. Connector bends and
service routing remain open. The exact equality intentionally prevents the drawing from
claiming unused coax margin.

## 8. Connected drawing contract

`calculations/aircraft_scene.py` owns the shared propeller hazard, orthographic projection
and three-dimensional clearance result. `calculations/generate_blueprints.py` consumes that
scene:

- SLM-GA-002 rebuilds CLEAN and V1 OMLs from their respective layouts, shows the complete
  electronics skeleton and includes a rear propeller-clearance proof;
- SLM-FIN-001 consumes the same planform vertices and shows top/rear installation views;
- SLM-EQP-001 shows CLEAN equipment plus the coupled V1 battery/camera/VTX/coax overlay.

Changing fin station, propeller diameter, mass, battery bounds or O4 geometry in Python now
changes the calculations and every dependent SVG on regeneration.

## 9. Open gates

1. Measure propeller static and powered runout.
2. Load the complete boom/fin installation through the F2 structural case.
3. Weigh both printed fin assemblies, spars, saddles and booms.
4. Verify actual O4 connector bend radii and service routing.
5. Repeat yaw-decay testing motor on and motor off; no slipstream credit is permitted until
   measured.

