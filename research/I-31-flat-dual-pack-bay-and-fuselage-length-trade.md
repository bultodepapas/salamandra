# I-31 — Flat dual-pack bay and fuselage forebody-length trade

**Status:** Executed screening — physical pack requirement captured; coupled CG/OML
closure open · **Feeds:** I-16, I-28, OP-01/OP-21/OP-23/OP-24, future fuselage ADR

> **Engineering answer.** Salamandra should retain the selected flat, long-axis
> layouts—4S1P `2x2x1-A` and 6S1P `3x2x1-A`—because they share a low
> `44.0 x 22.6 mm` pack cross-section. It should **not** yet adopt a long nose merely
> to let the battery be the only CG-adjustment device. Under the current aggregate
> mass model, doing so requires approximately `327 mm` of common usable rail and
> pushes the 4S pack envelope at least `84.7 mm` ahead of the current provisional
> body nose. For the stated priorities—efficiency and agility—the correct design
> prior is the **shortest forebody that closes both real mass configurations**, paired
> with an adequately gradual aft recovery into the pusher propeller. Forebody length,
> aft-body recovery length and vertical-tail arm are separate variables and shall not
> be traded as one scalar “fuselage length.”

All dimensions are millimetres unless stated otherwise. Coordinates follow the
project convention: `x` is positive aft and the origin is the root quarter chord.
Evidence tags retain the repository meaning: measured/manufacturer `[M]`, derived
`[D]`, estimate/engineering interpretation `[E]` and provisional geometry `[I]`.

## 1. Question and requirements captured

The requested aircraft shall accept either of two P42A 21700 packs in a **single
flat layer**:

1. 4S1P: four cells in a `2 x 2 x 1` array, cell axes longitudinal;
2. 6S1P: six cells in a `3 x 2 x 1` array, cell axes longitudinal;
3. one common fuselage bay/carrier architecture;
4. at least `10 mm` additional longitudinal allowance for cable accommodation,
   CG adjustment or small mass changes;
5. an FPV camera installed at the front; and
6. compatibility with the rudder-equipped and rudderless experimental variants.

The phrase “10 mm additional” has two legitimate mechanical interpretations. This
thread preserves both instead of silently choosing one:

- **literal minimum:** `10 mm` total extra channel length `[E]`;
- **recommended interpretation:** `+/-10 mm` battery travel about the solved station
  `[E]`, because the sign of a future mass-property error is not known in advance.

The P42A envelope already includes the I-16 `12 mm` one-end lead projection. Neither
interpretation includes bay wall thickness, assembly clearance, a retainer, an
extraction path, connector bend-radius validation or tolerance from a measured
finished pack. Those remain separate CAD inputs; counting the `12 mm` projection as
all cable/service clearance would be false closure.

## 2. Reproducible method

The calculation is:

```bash
python3 calculations/fuselage_length_trade.py
python3 calculations/fuselage_length_trade.py --json
```

It consumes the maximum sleeved P42A cell dimensions and assembly allowances from
`battery_pack_layout.py`, the current aggregate non-battery mass and moment from
`balance_cg.py`, the canonical cruise speed/kinematic viscosity from
`design_config.py`, and only the longitudinal extent of the provisional I-28 body.
It does **not** modify the released battery reference layout or generate a new OML.

The maximum-dimension pack relation is

\[
  L_p=n_x L_{cell}+2t_{outer}+L_{lead},\qquad
  W_p=n_y D_{cell}+2t_{outer},
\]

\[
  H_p=n_z D_{cell}+2t_{outer}+t_{nickel},
\]

using `L_cell=70.2 mm`, `D_cell=21.7 mm` `[M]`, `t_outer=0.3 mm/side`,
`L_lead=12 mm` and `t_nickel=0.3 mm` `[E]`. Installed pack mass is the I-16
cell maximum plus its `25 g` hardware allowance.

For each pack, the station required by the frozen aggregate model is

\[
 x_b=\frac{x_{CG}(m_0+m_b)-M_0}{m_b}.
\]

Holding `m_0` and `M_0` fixed deliberately exposes the battery-mass effect. It is a
like-for-like screen, not a new component-level balance solution.

## 3. Flat-pack result

| Pack | Selected array | Maximum installed envelope L x W x H `[D]` | Installed mass `[D]` | Nominal energy `[D]` |
|---|---|---:|---:|---:|
| 4S1P P42A | `2x2x1-A` | **153.0 x 44.0 x 22.6** | **305 g** | **60.5 Wh** |
| 6S1P P42A | `3x2x1-A` | **223.2 x 44.0 x 22.6** | **445 g** | **90.7 Wh** |
| Current compact 6S comparator | `2x3x1-A` | 153.0 x 65.7 x 22.6 | 445 g | 90.7 Wh |

The selected packs have the same cross-section; the 6S adds exactly one maximum
cell length, `70.2 mm`, along `x`. Relative to the compact 6S envelope, the long 6S
reduces pack width and pack-envelope frontal area by **33.0%**. That is a genuine
packaging advantage and supports a flatter/narrower **battery region**.

It does not prove a 33% reduction in aircraft frontal area. The current provisional
body reaches `152 mm` width at the wing-root blend, where wing thickness, structure
and junction geometry—not the battery alone—control the OML. The benefit must
therefore enter the future optimizer as a local containment opportunity rather than
as a promised aircraft-drag reduction.

### 3.1 Physical channel, before CG closure

| Interpretation | Minimum channel length `[D]/[E]` | Contained pack cross-section |
|---|---:|---:|
| Literal user minimum: 6S length + 10 mm total | **233.2 mm** | 44.0 x 22.6 mm |
| Recommended: 6S length + 10 mm each way | **243.2 mm** | 44.0 x 22.6 mm |

These are analytical pack-corridor dimensions, **not released internal bay
dimensions**. Wall, installation and removal clearances shall be added only once and
after a finished pack, connector and retainer are measured.

## 4. The physical-fit/CG-fit distinction

The current aggregate balance model produces:

| Quantity | 4S1P | 6S1P |
|---|---:|---:|
| Required pack-centre `x` | **-472.9 mm** | **-353.7 mm** |
| Aircraft-CG change from 10 mm pack motion | 2.16 mm | 2.87 mm |
| Pack pitch-inertia proxy about target CG | **0.04445 kg m²** | **0.03192 kg m²** |

Consequences:

- Required pack centres are **119.3 mm apart**. A 10 mm slot cannot absorb the
  electrical-configuration mass change.
- The union of both physical pack intervals is `307.4 mm`; adding the recommended
  `+/-10 mm` travel for both gives **-559.4 to -232.1 mm**, or **327.4 mm**.
- The current provisional body spans `-474.7 to +265.0 mm`. Even before wall and
  optical-nose allowance, the battery-compatible forward limit is therefore at least
  **84.7 mm ahead** of that body.
- If the aft extent were frozen, this creates a lower-bound body length of roughly
  `824 mm`, **11.5% longer** than the provisional `739.7 mm` body. The OML itself is
  `[I]` and rejected as aircraft-feasible, so this is a sensitivity—not a dimension.
- A lighter pack is not automatically more agile. Because the 4S must sit much farther
  from the CG in this model, its own parallel-axis pitch-inertia contribution is about
  **39% greater** than that of the 6S, even after including a cuboid centroidal proxy.

Co-locating the 4S at the present aggregate 6S station would require a fixed-mass
moment change of `-0.03638 kg m`. For scale, that is equivalent to moving `140 g`
approximately `260 mm` forward. Adding roughly `100 g` of nose ballast would create a
similar moment but directly contradict the efficiency/agility objectives and is not a
recommended solution.

There is also an unresolved model-interface issue. The aggregate model gives the 6S
station as `-353.7 mm`, while the component-level CLEAN layout currently gives
`-337.74 mm` and V1 gives `-363.27 mm`. These values answer different model questions,
but a new fuselage cannot be released while they remain separate packaging truths.
The repair must make both packs first-class component-level configurations and use one
mass/station contract.

## 5. What a longer forebody actually changes

### 5.1 Potential advantages

1. **Lower local pack-region cross-section.** The long 6S exchanges `21.7 mm` of pack
   width for `70.2 mm` of length relative to the current compact layout. Where battery
   containment controls the OML, this can reduce local frontal and wetted area.
2. **Gentler area gradients.** A longer body can provide lower local slopes and a finer
   afterbody angle for the same volume. NACA tests of six fineness-ratio-5 bodies found
   tail angle to be the most important single body-form characteristic and sharper,
   finer-ended bodies to have lower drag. The tests covered `Re_L` from approximately
   `1.5e6` to `25e6`; Salamandra's present screen is `1.30e6` at 95 km/h, near but just
   below the tested lower bound. [NACA TN-614](https://ntrs.nasa.gov/citations/19930081378)
3. **Packaging leverage.** More forebody travel can close CG without dead ballast and
   may provide a clean, forward camera aperture if the three-dimensional arrangement
   remains unobstructed.
4. **Forward-swept-wing packaging compatibility.** A NASA forward-swept-wing study
   noted that locating the wing root aft can permit useful volume forward near the CG.
   That observation supports integrated forward packaging, not unlimited nose length.
   The tested fighter had much greater sweep and Mach number, so only the architectural
   trend transfers. [NASA TM-85795](https://ntrs.nasa.gov/citations/19840018599)

### 5.2 Fundamental penalties

1. **More wetted area and skin friction.** With cross-section approximately fixed and
   an axial stretch ratio `r`, wetted area scales approximately as `r`. Using the NASA
   fully turbulent flat-plate screen `Cf=0.074/Re_L^0.2`, friction force scales as
   approximately `r^0.8`; the small decrease in `Cf` does not cancel the added area.
   Transition is especially uncertain on a 3D-printed surface, so this is a conservative
   trend model, not a drag prediction. [NASA/TP-2006-213486](https://ntrs.nasa.gov/citations/20060053240)
2. **More destabilizing side area ahead of CG.** A NACA free-flight/wind-tunnel study
   found considerably greater unstable yawing moment for its longer fuselage, with the
   increase approximately proportional to fuselage length. Increased tail arm did not
   cure an underlying directional-stability deficiency because fuselage instability and
   tail contribution both grew. The exact magnitude is configuration-specific, but the
   sign is directly relevant. [NACA ARR 3D17](https://ntrs.nasa.gov/citations/19930092574)
3. **The nose is not tail arm.** Extending the nose does not increase rudder or fin arm.
   NACA fin tests found area behind the CG beneficial and area forward of it harmful at
   large yaw. For the rudder-equipped variant, an **aft** extension may permit a smaller
   vertical surface only after positive stability exists. For the rudderless variant,
   a longer nose retains the destabilizing body contribution without buying rudder
   authority; any passive-fin benefit still depends on aft area and arm.
   [NACA TN-785](https://ntrs.nasa.gov/citations/19930081581)
4. **Pitch stability and trim coupling.** Classical fuselage theory and experiments
   identify an unstable body contribution to longitudinal static stability and strong
   wing-body interference. A longer or fuller nose must therefore be included in the
   aircraft neutral-point and elevon-trim calculation; an isolated body drag trade is
   insufficient. [NACA TM-1036](https://ntrs.nasa.gov/citations/20000004246)
5. **Pitch/yaw inertia.** Agility depends on total mass moment of inertia, not mass
   alone. Moving a fixed mass farther from CG increases its rotational inertia with
   distance squared. The present 4S result demonstrates the effect directly.
6. **Structural mass and compliance.** A longer printed shell adds material, seams and
   local buckling exposure. If the supported battery-boom geometry scales with length,
   a first-order bending-deflection sensitivity scales as `r^3`. The current two-support
   boom passes its own load case, but a new forward support span must be re-solved; the
   existing result cannot be extrapolated as a pass.
7. **Pusher inflow quality.** The propeller operates in the upstream fuselage/wing wake.
   NASA-sponsored pusher work explicitly requires attached upstream flow and a minimal
   wake, while full-scale testing states that aft-fuselage shaping and matching the
   propeller to the fuselage flow field can improve efficiency. This makes **aft recovery
   length and shape** more important to the pusher than nose length by itself.
   [Virginia Tech/NASA PAVE report](https://ntrs.nasa.gov/citations/20020057966),
   [NASA TP-2382](https://ntrs.nasa.gov/citations/19850011615)

## 6. Interaction with Salamandra's forward-swept wing

Forward sweep makes the inboard/root flow and the body junction a first-order risk.
NASA's forward-swept-wing tests describe rootward spanwise flow and inboard separation
occurring before tip separation. On Salamandra, this is qualitatively consistent with
the existing root-separation concern; it does **not** prove the same separation angle
because sweep, Reynolds number, airfoil, Mach number and body geometry differ.
[NASA TM-85795](https://ntrs.nasa.gov/citations/19840018599)

The practical implication is that nose length cannot be optimized from body drag alone:

- a slim, gradual forebody may reduce blockage approaching the root;
- a longer/full-width body can add boundary-layer thickness and sidewash before the
  inboard wing;
- a poor maximum-area location or adverse recovery through the root can intensify the
  already vulnerable junction flow; and
- visual smoothness does not demonstrate attached flow.

NASA's Juncture Flow programme was created because even modern RANS models can disagree
on wing-body corner separation; its experiments target the onset and growth of the
trailing-edge junction bubble. This supports the project's existing hierarchy: geometry
metrics first, then coupled viscous analysis and physical flow visualization—not an OML
decision from fineness ratio alone.
[NASA Juncture Flow Experiment](https://ntrs.nasa.gov/citations/20160007544)

## 7. Quantitative length sensitivities

The following screen holds characteristic cross-section constant. `Df/Df0` combines
the axial wetted-area proxy with the fully turbulent `Cf`; yaw moment assumes forward
side area and its centroid arm both scale with length; beam deflection uses a similar
supported-span `L^3` sensitivity. The last two columns are warning metrics, not
`Cn_beta` or a stress-analysis result.

| `L/L0` | Length `[I]` | `Re_L` at 95 km/h | `Cf_turb` | `Df/Df0` | Forward side-area moment proxy | Beam-deflection proxy |
|---:|---:|---:|---:|---:|---:|---:|
| 0.85 | 628.7 | 1.106e6 | 0.00458 | 0.878 | 0.722 | 0.614 |
| 0.90 | 665.7 | 1.171e6 | 0.00452 | 0.919 | 0.810 | 0.729 |
| 1.00 | 739.7 | 1.301e6 | 0.00443 | 1.000 | 1.000 | 1.000 |
| 1.10 | 813.7 | 1.431e6 | 0.00435 | 1.079 | 1.210 | 1.331 |
| 1.20 | 887.6 | 1.562e6 | 0.00427 | 1.157 | 1.440 | 1.728 |

Applying only the battery-derived lower-bound ratio `r=1.115` gives approximately:

- **+9.1%** constant-section skin-friction force;
- **+24.2%** uniform forward side-area moment; and
- **+38.5%** similar-span beam deflection.

These are deliberately conservative sensitivities. A real local nose extension does not
uniformly scale the whole body, and a narrower optimized nose may recover some wetted
area. Conversely, junction pressure drag, separation or pusher-wake loss can exceed the
simple friction increment. Only a coupled geometry can resolve the net sign.

## 8. Architecture trade and recommendation

| Architecture | Benefit | Fundamental cost | Disposition |
|---|---|---|---|
| 327 mm battery-only CG rail / long nose | Both current aggregate stations fit without moving other equipment | Long forebody, camera conflict risk, higher yaw/pitch inertia and structure/friction penalties | **Do not select now** |
| 243.2 mm physical common channel plus coupled equipment redistribution | Preserves flat low cross-section and constrains nose growth | Requires a new component-level balance; current station gap is too large | **Preferred development path** |
| Short bay plus nose ballast for 4S | Mechanically simple | Roughly 0.1 kg class dead mass at a very forward station; damages efficiency and agility | **Reject as baseline** |
| Separate external fuselages for 4S and 6S | Each OML can be optimized | Defeats the requested common fuselage and experimental comparability | **Out of scope** |

The preferred design hypothesis is therefore:

> Use one flat `44.0 x 22.6 mm` pack corridor sized first to the long 6S and real
> service hardware; keep the nose only as long as required after the 4S and 6S are
> solved in one component-level mass model; preserve a separately optimized, gradual
> aft recovery into the pusher. Do not use nose length as a substitute for mass-system
> design or directional-stability closure.

This is a hypothesis for the next coupled iteration, not an ADR.

## 9. Repair and validation plan

### WP1 — close the physical battery requirement

1. Build both selected packs or dimensionally representative hard dummies.
2. Measure finished maximum `L/W/H`, lead exit, connector swept volume, minimum safe
   cable bend and extraction path `[M]`.
3. Convert the `+/-10 mm` recommendation into an explicit rail/retainer interface.
4. Keep wall thickness, equipment clearance and trim travel as separate dimensions.

**Gate:** both packs install/remove without cable crushing, cell abrasion or using OML
wall tolerance as assembly clearance.

### WP2 — unify the mass and configuration model

1. Add 4S1P and long 6S1P as explicit component-level equipment configurations.
2. Reconcile `balance_cg.py` and `equipment_layout.py` so one source owns each mass and
   station.
3. Include the camera, VTX, FC/PDB, wiring, retainers, boom and both vertical-control
   variants; propagate measured mass uncertainty.
4. Solve a shared-rail position and any legitimate movable equipment simultaneously,
   with no baseline ballast.

**Gate:** both packs reach the CG band with the required adjustment reserve and the
camera remains the forward optical installation in the full 3-D collision/FOV model.

### WP3 — trade forebody, afterbody and tail arm independently

The next fuselage design vector shall include at least:

- forebody tip and camera station;
- pack-rail forward/aft stops;
- maximum-area station;
- root-junction width/height and recovery gradients;
- aft-body recovery length and propeller-plane section; and
- vertical-surface station for rudder-equipped and rudderless variants.

For every candidate compute wetted/frontal/projected area, area-gradient/fairness,
component-level CG and inertia, body-inclusive NP/trim, yaw contribution, boom loads,
printed shell mass, camera FOV and propeller-plane wake proxies.

**Gate:** select a Pareto set; do not prescribe a universal fineness ratio.

### WP4 — falsify the low-order result

1. Run coupled VSPAERO/potential-flow trends only for attached-flow screening.
2. Use transition-bracketed viscous CFD for shortlisted OMLs, with special resolution
   at the forward-swept root junction and aft recovery.
3. Print root/junction and aft-body test articles; use tufts/oil flow and a prop-plane
   velocity survey at cruise and high-lift incidence.
4. Measure mass, support deflection and modal response of the complete battery carrier.
5. Flight-test the rudder-equipped variant first; release the rudderless experiment
   only after measured yaw damping/control margins are acceptable.

**Gate:** measured flow remains acceptably attached at the root/afterbody, pusher inflow
nonuniformity is within the propulsion margin, structure passes the load/modal gates and
both configurations close mass/CG without hidden ballast.

## 10. Decision boundaries

This research freezes only the following conceptual facts:

- both intended packs are one-layer, longitudinal-cell arrays;
- 4S is `2x2x1-A`; 6S is `3x2x1-A`;
- their maximum P42A analytical envelopes are `153.0 x 44.0 x 22.6` and
  `223.2 x 44.0 x 22.6 mm` before measured-build correction;
- one common carrier must provide at least 10 mm additional longitudinal allowance;
  `+/-10 mm` is the engineering recommendation pending confirmation; and
- pack fit alone does not set fuselage length.

It does **not** freeze the final rail length, pack stations, camera station, nose tip,
maximum-area station, aft recovery, wall thickness, OML or fin/rudder geometry.

## 11. Sources and transfer limits

1. Abbott, I. H., *Fuselage-Drag Tests in the Variable-Density Wind Tunnel:
   Streamline Bodies of Revolution, Fineness Ratio of 5*, NACA TN-614, 1937.
   Experimental body-shape/drag trend near the upper edge of Salamandra's body Reynolds
   number; axisymmetric isolated bodies, so no direct wing-junction coefficient
   transfers. <https://ntrs.nasa.gov/citations/19930081378>
2. Draper, J. W., *Free-Flight-Tunnel Investigation of the Effect of Fuselage Length
   and the Aspect Ratio and Size of the Vertical Tail on Lateral Stability and
   Control*, NACA ARR 3D17, 1943. Direct experimental sign of fuselage-length/yaw
   coupling; geometry and powered installation differ. <https://ntrs.nasa.gov/citations/19930092574>
3. NACA, *Wind-Tunnel Investigation of Fuselage Stability in Yaw with Various
   Arrangements of Fins*, NACA TN-785, 1940. Supports forward/aft side-area sign at
   large yaw, not a Salamandra fin size. <https://ntrs.nasa.gov/citations/19930081581>
4. Multhopp, H., *Aerodynamics of the Fuselage*, NACA TM-1036, 1942. Analytical and
   experimental body-moment/interference framework; use for model structure, not final
   low-Re coefficients. <https://ntrs.nasa.gov/citations/20000004246>
5. Gainer, T. G., Mann, M. J., and Huffman, J. K., *Low-Speed Investigation of Effects
   of Wing Leading- and Trailing-Edge Flap Deflections and Canard Incidence on a
   Fighter Configuration Equipped With a Forward-Swept Wing*, NASA TM-85795, 1984.
   Qualitative forward-sweep flow/packaging evidence only. <https://ntrs.nasa.gov/citations/19840018599>
6. Rumsey, C. L., Neuhart, D. H., and Kegerise, M. A., *The NASA Juncture Flow
   Experiment: Goals, Progress, and Preliminary Testing*, 2016. Establishes
   wing-body-corner separation and CFD-validation risk; its geometry/Reynolds number
   are not Salamandra's. <https://ntrs.nasa.gov/citations/20160007544>
7. Marchman, J. F. III et al., *An Investigation of CTOL Dual-Mode PAVE Concepts*,
   Virginia Tech AOE Report 276 for NASA Langley, 2002. Pusher-wake design method and
   flow-attachment requirement; vehicle scale differs. <https://ntrs.nasa.gov/citations/20020057966>
8. Yip, L. P., *Wind-Tunnel Investigation of a Full-Scale Canard-Configured General
   Aviation Airplane*, NASA TP-2382, 1985. Full-scale evidence that aft-body/propeller
   matching matters; no direct efficiency increment transfers to Salamandra.
   <https://ntrs.nasa.gov/citations/19850011615>
9. Rivell, T., *Notes on Earth Atmospheric Entry for Mars Sample Return Missions*,
   NASA/TP-2006-213486, 2006. Used only for the documented flat-plate skin-friction
   correlations and transition caution, not entry-vehicle geometry.
   <https://ntrs.nasa.gov/citations/20060053240>

