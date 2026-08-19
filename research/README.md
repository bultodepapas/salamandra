# Research threads

Here lives **the why**. Each thread documents what was searched, what was found, with what sources, and **what decisions it feeds**.

Separated from `decisions/` on purpose: an ADR says *what was decided*; a research thread says *what we know and how we know it*. One research effort can feed several decisions, and one decision can rest on several research efforts.

| # | Thread | Status | Feeds |
|---|---|---|---|
| [I-01](I-01-aspect-ratio-reynolds.md) | Aspect-ratio / Reynolds frontier | Closed | ADR-0004, ADR-0009 |
| [I-02](I-02-tailless-trim.md) | Tailless trim and forward sweep | Closed | ADR-0001, ADR-0003 |
| [I-03](I-03-propulsion-chain.md) | Propulsion chain | Closed | ADR-0007, ADR-0008, O1 |
| [I-04](I-04-printing-materials.md) | Printing materials | Closed | ADR-0016, ADR-0018, ADR-0021 |
| [I-05](I-05-divergence-flutter.md) | Aeroelastic divergence and flutter | **Open** | ADR-0002, ADR-0025, ADR-0028 |
| [I-06](I-06-reflexed-airfoils.md) | Reflexed airfoils at Re 3–5×10⁵ | **Open — B1 partial** | Gap G2 |
| [I-07](I-07-neutral-point-torsion-window.md) | **Neutral point, static margin and torsion window** | **Open — preliminary result** | ADR-0003, ADR-0032, G8, G2 |
| [I-08](I-08-stuntdouble-family.md) | **StuntDouble family: compared geometry** | **Open — base comparison** | A4, R3, R4 |
| [I-09](I-09-flightory-inspiration.md) | **Flightory Pico Talon & Stallion: geometry and construction** | **Open — base comparison** | B3/G2 (E205), CORE design (guide §6.7), docs/02 |
| [I-10](I-10-control-authority-static-margin.md) | **Tailless pitch control authority and minimum static margin** | 🔄 **Partial — VLM executed; measured/envelope closure open** | C6/S5, OP-01, OP-06, G8 |
| [I-11](I-11-reflexed-airfoil-database.md) | **Reflexed-airfoil database for the B3 shortlist** | 🔄 **Partial — aerodesign.de reviewed** | B3/G2, OP-02, C28 |
| [I-12](I-12-x29-divergence-sweep-factor.md) | **X-29 divergence data and sweep-factor bounds** | ↪ **Partially superseded by I-21; X-29 follow-on remains open** | G6, G4, S4 |
| [I-13](I-13-pusher-tractor-slipstream.md) | **Pusher vs tractor slipstream at low Re** | ⬜ **Proposed** | G5, ADR-0006, OP-14 |
| [I-14](I-14-hand-launch-stall-margin.md) | **Hand-launch and stall-margin practice** | ⬜ **Proposed** | O1 (stall), C16, launch, D1/D2 |
| [I-15](I-15-airfoil-evidence-campaign.md) | **Airfoil evidence campaign (root + tip)** | 🔄 **Computational closure — Salamandra r1 released; E2 measured acceptance open** | B3/G2, OP-02, R-AIRFOIL |
| [I-16](I-16-battery-pack-layout.md) | **Battery pack layout: physical envelope of 4S / 6S · 21700** | 🔄 **Sizing baseline — open** | Guide §9, `balance_cg.py` OP-01/OP-23, R-CG |
| [I-17](I-17-inav-flight-controllers.md) | **INAV flight controllers: popular boards and data sheets** | 🔄 **Reference catalog — open** | Guide §11, CORE avionics station, O2/O10 |
| [I-18](I-18-servo-catalog.md) | **Elevon servos: popular models and data sheets** | 🔄 **Reference catalog — open** | Guide §5.3/§7.5, ADR-0025, ADR-0026, CORE servo bays |
| [I-19](I-19-fpv-system-dji-o4.md) | **DJI O4 FPV system: O4 / Pro / Lite — data sheets + electrical data** | 🔄 **Reference catalog — open** | Guide §11, nose-pod/camera, O1, I-17 |
| [I-20](I-20-yaw-stability-centerline-fin.md) | **Directional (yaw) stability and the superseded centreline-fin concept** | ↪ **Architecture superseded by I-29; method retained as history** | I-29, ADR-0038, G10 |
| [I-21](I-21-sweep-trade-and-elastic-axis-correction.md) | **Sweep trade and elastic-axis correction** | 🔄 **Executed — design selected; material tests open** | ADR-0040, OP-01, OP-03, OP-23, OP-29 |
| [I-22](I-22-high-roi-v0.3-audit.md) | **High-ROI v0.3 audit: airfoil, propulsion and mass/CG** | ✅ **Executed — corrected by I-23/C29; physical gates retained** | ADR-0041…0043, guide v0.19, release v0.3.0 |
| [I-23](I-23-calculation-system-integration-audit.md) | **Calculation-system integration and physics audit** | ✅ **Executed — contracts and C29–C32 corrected; V1 mass gate reopened** | Guide v0.19, ADR-0042/0043, OP-06/12/13/23/24/28/29 |
| [I-24](I-24-flight-load-envelope.md) | **Article #1 manoeuvre and regulatory-reference gust envelope** | 🔄 **Partial — limit/ultimate semantics and positive V-n branch closed; dynamic gust/CLmin open** | ADR-0044, guide v0.21, release v0.4.0, F4/S1–S2, G11/E9 |
| [I-25](I-25-svg-technical-drawing-workflow.md) | **Reproducible SVG technical-drawing workflow** | ✅ **Executed — two A3 design-review sheets; manufacturing authority remains open** | `generate_blueprints.py`, `geometry/drawings/`, wiki drawing guide, future CAD ICDs |
| [I-26](I-26-codex-svg-agent-toolchain.md) | **Codex, VS Code and agent toolchain for controlled SVG drawings** | ✅ **Executed — repository workflow hardened; optional renderer/schema gates open** | repository SVG skill, VS Code tasks, generator verification, drawing guide |
| [I-27](I-27-elevon-geometry-trade.md) | **Article #1 elevon span, chord and tip-clearance trade** | 🔄 **Computational selection executed; E2/E5/G7 physical closure open** | ADR-0045, OP-06, guide §6.6, F2 |
| [I-28](I-28-coupled-parametric-fuselage-oml.md) | **Senior master plan for an automatic parametric fuselage around the coupled skeleton** | 🔴 **Revision 2 OML rejected; Revision 3 executable plan controls replacement** | OP-21, F1/F2, G10, future fuselage-generator ADR |
| [I-29](I-29-twin-fin-architecture-correction.md) | **Directional-surface architecture correction: twin aft-CORE fins** | 🔄 **Geometry corrected; F2/E8 physical closure open** | ADR-0038, SLM-GA-002, SLM-FIN-001, G10 |
| [I-30](I-30-fin-station-mass-cg-and-connected-scene-closure.md) | **Fin station, volume/mass, CG, forward packaging and connected SVG scene** | 🔄 **Analytical coupling executed; F2/E8 physical closure open** | ADR-0038, I-29, SLM-GA-002, SLM-FIN-001, SLM-EQP-001 |

## Source quality

Order of preference:

1. Peer-reviewed
2. Experimental databases (UIUC)
3. Controlled test published with a declared method (e.g. CNC Kitchen)
4. Manufacturer documentation
5. Patents — verifiable argument, magnitude not independent
6. Own measurement on in-service articles

### Source marked as unusable

**Grokipedia** claims that forward sweep *delays* aeroelastic divergence. **It contradicts all the primary and peer-reviewed sources consulted, including the X-29 program documentation. It must not be used.**
