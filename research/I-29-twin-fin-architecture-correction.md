# I-29 — Directional-surface architecture correction: twin aft-CORE fins

**Date:** 2026-08-19  
**Status:** Engineering correction; geometry remains `[D]` on aerodynamic/structural inputs `[E]`  
**Applies to:** SALAMANDRA-V1a/V1b, ADR-0038, SLM-GA-002 and SLM-FIN-001

## 1. Finding

The former single-fin drawing was not a physically credible aircraft installation. Its
calculated planform had been placed behind the centreline pusher propeller and supported by
a notional carrier. In side projection the fin root ran from x = +244.4 to +349.1 mm while
the body OML ended near x = +265 mm and the propeller plane was x = +235 mm. Therefore:

- 84.1 mm of root chord lay behind the body OML;
- the proposed centreline load path intersected the rotating-propeller plane;
- the fin appeared as a large unsupported plate rather than an integrated vertical surface;
- its 0.60 taper, 7.125° quarter-chord sweep and 251.1 mm height produced a visually blunt,
  lightly swept planform without solving the structural contradiction.

This was not an SVG styling defect. It was an architecture defect.

## 2. Primary-source review

### 2.1 Flying-wing precedents

NASA's X-48B used wingtip-mounted vertical fins. The X-48C configuration then moved twin
vertical fins inboard to the aft body region while also relocating propulsion-system
elements. The relevant transferable lesson is not a universal fin position; it is that fin
placement follows available aft moment arm, wake environment and structural integration.

Sources:

- NASA, *X-48B*: <https://www.nasa.gov/aeronautics/x-48b/>
- NASA, *X-48C Hybrid/Blended Wing Body*:  
  <https://www.nasa.gov/image-article/x-48c-hybrid-blended-wing-body-3/>
- NACA/NASA, *Design and Flight Tests of a Tailless Glider*:  
  <https://ntrs.nasa.gov/search.jsp?R=20090026465>

The historical NACA tailless-glider work indicates that satisfactory lateral qualities
were associated with `Cnβ` of approximately +0.002 per degree. This is used only as a
warning reference: SALAMANDRA-V1a's nominal +0.0005/deg screen must not be described as a
handling-quality closure.

### 2.2 Comparable small pusher aircraft

Visual inspection of the official TBS manuals corrects the earlier interpretation:

- Chupito integrates a swept/tapered fin into the main body ahead of the motor/propeller.
- Mojito integrates the vertical surface with the aft body/motor-support assembly; it does
  not demonstrate an unsupported fin on a carrier extending through the propeller disk.

Sources:

- TBS Chupito manual: <https://www.team-blacksheep.com/media/files/tbs-chupito-manual.pdf>
- TBS Mojito manual: <https://www.team-blacksheep.com/media/files/tbs-mojito-manual.pdf>

## 3. Architecture trade

All values below are reproducible from `calculations/yaw_stability.py`,
`calculations/equipment_layout.py` and the shared geometry contract.

| Candidate | Aerodynamic consequence | Installation consequence | Decision |
|---|---|---|---|
| Existing-prop centre fin, ahead of disk | Short `l_v`; approximately 340 mm height required for the V1a nominal target | Fits no credible compact dorsal envelope | Reject |
| Centre fin with propulsion moved aft ≈130 mm | Restores aft arm | Moves the 195 g propulsion group aft; first-order battery shift ≈57 mm forward, about 61 mm beyond V1 travel | Reject for Article 1 |
| Wingtip fins | Tips are forward because of forward sweep; yaw arm is poor or adverse | Simple local attachment but wrong longitudinal station | Reject |
| Split drag rudders | Control moment only when deployed; no closed-surface passive `Cnβ` | Two actuators and FC dependency | Defer |
| Twin fixed fins on aft CORE booms | Python sweep resizes area at every AC station; first mass-feasible knee is x_ac = +280 mm | Direct load paths at y = ±140 mm, outside inflated prop envelope analytically | Select provisionally |

## 4. Selected V1a geometry

The selected planform is a conventional tapered, low-aspect-ratio vertical surface. There
are two identical fins; stability equations use their total area while section and strength
calculations use one fin.

| Quantity | V1a value | Basis |
|---|---:|---|
| Count | 2 | architecture `[D]` |
| Total area | 3.4737 dm² | nominal `Cnβ = +0.00050/deg` target `[E]` |
| Area each | 1.7368 dm² | derived |
| Span each | 186.4 mm | `AR_each = 2.0` |
| Root / tip chord | 128.5 / 57.8 mm | taper 0.45 |
| Leading-edge / quarter-chord sweep | 25.0° / 20.379° | swept trapezoid |
| Aerodynamic-centre station | x = +280 mm | first mass-feasible knee in +225…+325 mm sweep |
| Boom station | y = ±140 mm | propeller-clearance geometry |
| Boom envelope | 18 × 14 mm; x = +156…+372.4 mm | provisional structure `[I]` |
| Inner radial propeller clearance | 29.4 mm nominal; 13.4 mm residual | Ø203.2 mm propeller plus 16.0 mm radial allowance `[E]/[I]` |

Why this shape:

- **AR 2.0** avoids the excessive height and bending moment of the former AR 3.0 surface.
- **Taper 0.45** reduces tip loading without the former narrow 42.8 mm tip and retains a
  credible printed free-edge chord.
- **Swept trapezoid** uses a controlled 25° leading edge and a naturally swept trailing
  edge. The geometry is derived from area, aspect ratio and taper rather than a vertical-TE
  drawing constraint.
- **Dorsal root fillet** remains wholly inside the credited planform. It does not project
  forward into the propeller region or receive additional `S_v`/`Cnβ` credit.
- **External Ø3 mm aluminium leading-edge spar** follows the swept leading edge and avoids
  the impossible former claim of a Ø3.2 mm enclosed bore inside a 3.0→1.5 mm plate.

## 5. Aerodynamic, mass and structural screen

V1a results:

- `Cnβ` independent corners, power on/off: **−0.00029…+0.00119 /deg**;
- nominal `Cnβ`: **+0.00050 /deg**;
- estimated `ΔCD0`: **+0.0019**, or approximately **+13.1%** against CLEAN;
- complete lower analytical assembly: **59.97 g** versus a **60.00 g** allocation;
- coupled forward-support addition: **2.40 g**; solved AUW/stall: **1615.63 g / 44.93 km/h**;
- solved battery/camera/VTX stations: **−386.74 / −463.79 / −429.61 mm**;
- nose extension / V1 body OML length: **17.81 / 757.51 mm**;
- load per fin at 180 km/h: **26.6 N**;
- root bending moment per fin: **2.17 N·m**;
- 3.0 mm PETG root analytical yield FS: **4.45**, without spar credit;
- estimated first bending mode: **14.6 Hz**.

The negative lower `Cnβ` corner and 0.03 g fin-module mass margin prevent design release. V1a is a
geometry-correct marginal test article. V1b raises total area to approximately 4.63 dm² and
its independent lower corner to +0.00017/deg, but its mass/stall consequences require a
separate F2 decision.

## 6. Required closure

1. F2: print two representative fins, saddles and boom fairings; measure complete mass.
2. F2: static-load each root to the factored design load and inspect the boom/wing load path.
3. Propulsion test: confirm clearance, vibration and wake interaction through the complete
   throttle range; no slipstream benefit is credited in the current model.
4. E8: excite yaw and measure modal decay with motor on and off.
5. Recompute `Cnβ`, `Cnr`, stall speed and flutter margin using measured geometry/mass before
   changing the drawing status from `DRAFT · NOT FOR MANUFACTURE`.
