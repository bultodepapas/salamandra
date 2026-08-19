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

The current solution converges without a nose extension. No SVG contains an independent fin,
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
derivative reaches `Cnβ = +0.00050/deg`. Motor and propeller positions are not candidate
variables. The measured propeller slab begins at x = +229.9 mm; its 5.0 mm dynamic
inflation moves the analytical forward hazard face to +224.9 mm. Both the fin and support
must retain at least 8.0 mm beyond that face.

| `x_AC` (mm) | `l_v` (mm) | `S_v,total` (dm²) | lower assembly (g) | boom length (mm) | aft extent (mm) | first-order battery shift (mm) | Feasible |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 100.0 | 193.8 | 6.6351 | 51.39 | 48.95 | 204.95 | 25.09 | No: 257.6 mm print span |
| 110.0 | 203.8 | 6.3095 | 49.61 | 56.40 | 212.40 | 25.28 | No: 251.2 mm print span |
| **115.5** | **209.3** | **6.1437** | **48.73** | **60.57** | **216.57** | **25.39** | **Yes; selected** |
| 116.0 | 209.8 | 6.1290 | 48.65 | 60.95 | 216.95 | 25.41 | No: support residual 7.95 mm |
| 120.0 | 213.8 | 6.0144 | 48.04 | 64.02 | 220.02 | 25.50 | No: axial clearance |

The code scans every 0.5 mm from +80 to +280 mm. Feasibility is governed before scoring;
among feasible candidates, minimum installed mass selects the aft-most useful station.
`x_AC = +115.5 mm` is therefore a result of the fixed-propeller, stability, print, mass,
wing-root and clearance constraints, not a drawing coordinate.

## 4. Selected swept trapezoid

The selected planform is fully constrained by total area, count, aspect ratio, taper,
leading-edge sweep and AC station:

| Quantity | Result | Authority |
|---|---:|---|
| Count | 2 | `[D]` architecture |
| Total / each area | 6.1437 / 3.0718 dm² | `[D]` from nominal target `[E]` |
| Aspect ratio each / taper | 2.00 / 0.45 | `[E]` |
| Span each | 247.86 mm | `[D]` |
| Root / tip chord | 170.94 / 76.92 mm | `[D]` |
| Leading-edge / quarter-chord sweep | 20.0° / 15.064° | `[E]` / `[D]` |
| Root LE / TE | +43.63 / +214.57 mm | `[D]` |
| Tip LE / TE | +133.84 / +210.77 mm | `[D]` |
| MAC | 129.88 mm | `[D]` |
| AC | +115.50 mm | `[D]` on target `[E]` |
| Planar root datum | z = +15.550 mm | `[D]` from 101 local-airfoil samples + 0.500 mm clearance `[E]` |
| Carbon-support top / printed saddle | z = +7.000 mm / 8.550 mm height | `[D]` / `[I]` |

This removes the former vertical-trailing-edge constraint and the artificial narrow tip.
The root fillet is contained inside the credited planform, so it cannot appear ahead of the
fin or inflate stability area. The root datum is not the former arbitrary support
half-height. `equipment_layout.fin_root_interface_z_m()` samples the actual upper airfoil
ordinate over the root/wing overlap, takes the maximum OML height, and adds 0.500 mm. The
forward root therefore remains outside the wing skin, while an explicitly drawn printed
saddle connects the aft overhang to the unchanged carbon support centred on `z = 0`.

## 5. Material volume and mass

The lower LW-PLA-HT shell/mount model uses an 0.85 mm effective thickness and a 10%
local-mount factor. The conservative upper end of the supplier's maximum-foaming density
band is `ρ = 620 kg/m³`:

\[
V_{shell,lo}=S_v(0.00085)(1.10)=57.44\;\mathrm{cm^3},
\]

\[
m_{shell,lo}=35.61\;\mathrm{g}.
\]

Two solid Ø3 mm aluminium leading-edge rods follow the derived swept leading edges and
contribute 10.07 g. Two Ø6/4 mm carbon root supports use the derived 60.57 mm length and
contribute 3.04 g. Therefore:

\[
m_{module,lo}=35.61+10.07+3.04=48.73\;\mathrm{g}.
\]

The upper analytical band is 56.92 g. The lower model leaves 11.27 g below the 60 g
allocation, but coupon density, final fillets and measured printed mass remain F2 gates.

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

Residual radial support clearance is therefore 13.4 mm. Axially, the inflated propeller
hazard begins at +224.9 mm. The fin ends at +214.57 mm and the support at +216.57 mm,
leaving 10.33 and 8.33 mm residual respectively. Side-view axial overlap is zero. Status
remains **ANALYTICAL PASS / F2 PHYSICAL OPEN**.

## 7. Coupled mass, CG and fuselage result

Adding the selected fin module shifts the required battery station forward, but the
original battery travel remains sufficient. The solver therefore adds no nose or cradle
length and no associated support mass:

| Coupled result | Value |
|---|---:|
| Iterations | 1 |
| Nose boom/cradle extension | 0.0000 mm |
| Added forward-support mass | 0.0000 g |
| V1 AUW | 1601.9777 g |
| Solved CG x / target x | −93.78395 / −93.78395 mm |
| Battery x | −363.2712 mm |
| Camera x | −445.9802 mm |
| VTX x | −418.0000 mm |
| O4 straight-line lower bound / maximum | 45.99 / 50.0 mm |
| CLEAN / V1 body OML length | 739.70 / 739.70 mm |
| V1 nose-to-support longitudinal extent | 691.27 mm |
| Analytical stall speed | 44.74 km/h |

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
