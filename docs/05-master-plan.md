# Master plan — roadmap to the first prototype

**Revision 1.1** · 17 August 2026 · Phase 1 in progress

This document **does not replace** [`03-phase-1-plan.md`](03-phase-1-plan.md), which remains the operational detail of Phase 1. This document is the orchestration layer: **it sequences phases 1→6 of the status table in the [README](../README.md) up to the first physical article flying**, points out which gap (`gaps/README.md`) and which ADR blocks each segment, and fixes where CAD modeling (Fusion 360) enters.

This plan covers the **reference design** (the forward-swept flying wing). It is the first
of a community-driven platform family: once the reference airframe is released, the same
modular CORE/PANEL discipline extends to new wings, fuselages, control surfaces and
configurations contributed by the community. The AI-assisted research produces the
reasoning; the community produces the 3D parts.

It sets no calendar dates. The repo has no `[M]` data on how long each task takes; putting weeks would be an `[I]` figure disguised as a plan. It is ordered by **dependency**, not by duration.

---

## 0. What "the first prototype" is

**Working definition, revisable:** the first prototype is **article #1** already described in the README — **Cruise (1300 mm, 6S1P)** configuration — printed, assembled, balanced according to [ADR-0025](../decisions/ADR-0025-elevon-balancing.md), with avionics and **pitot installed** (a requirement of [O1](00-objectives-and-requirements.md)), able to fly in a stabilized way to run **E2, E3 and E7**. **Recommended build: SALAMANDRA-V1 (fixed centreline fin, ADR-0038/I-20)** — the fin doubles Cnr and removes the finless yaw divergence, giving cleaner test data; the finless CLEAN build remains the O1-efficiency configuration.

The V1 recommendation is conditional on F2 closing the C32 mass gap; until then CLEAN
is the only mass-compliant configuration.

It is not "something that prints and flies once". It is the instrumented platform that **can generate the `[M]` data the project still lacks** (G2, G4, G6, G7 in `gaps/`). If it does not carry an operational pitot and blackbox, it does not count as the project's prototype — it counts as a mock-up.

If this definition is not the one you had in mind, tell me and I adjust the rest of the plan.

---

## 1. Global view — from Phase 1 to a flying article

| Phase | Objective | Exit gate | Blocked by | Detail |
|---|---|---|---|---|
| **F1 — Geometry and stability** | Frozen OML, airfoil chosen, NP verified | Checklist of [`03-phase-1-plan.md §4`](03-phase-1-plan.md) | G1, G2, G8 | Dedicated document |
| **F2 — Weights and balancing** | Real CG within R-CG in the 4 battery configurations | R-CG verified in CAD, not just on a table | Needs F1 OML | §3 of this doc |
| **F3 — Performance** | Complete aircraft polar, power curve, closed propeller matching | D3/D4 run, objective O1 with a closing path | Partially parallel to F1 (line D of `03-phase-1-plan.md`) | §4 |
| **F4 — Loads and structure** | n_max/n_min with a declared gust basis, V-n, verified GJ/EI, confirmed elevon authority | C6 and C7 of `03-phase-1-plan.md`, G4 and G6 bounded | Needs F2 CG and F3 polar | §5 |
| **F5 — Systems and propulsion** | Final bay, operational instrumentation chain (pitot+blackbox), firmware configured | D1/D2 completed, G9 resolved | Needs F4 structure | §6 |
| **F6 — Manufacturing and release** | Article #1 printed, assembled, balanced, flying | First stabilized flight with valid blackbox data | Needs F2–F5 closed | §7 |

Phase 0 (specification) is closed. This plan covers F1→F6; beyond F6 the full test program (E2, E3, E7 in depth) begins, which already lives in `tests/README.md` and is not repeated here.

---

## 2. Why the order matters — failure mode #1

`CLAUDE.md` documents the most expensive error in the project so far: sizing structure and elevons **without having defined loads or verified control authority**. This plan exists so that it does not repeat:

```
F1 (geometry, NP)
  └─► F2 (real CG)          ← needs geometry to compute per-component masses
        └─► F3 (polar, power)   ← parallelizable with F1/F2 via line D, does not depend on them
              └─► F4 (loads, GJ/EI, elevon authority)   ← needs CG (F2) and cruise CL (F3)
                    └─► F5 (final bay, instrumentation)    ← needs closed structure (F4)
                          └─► F6 (manufacturing, assembly, first flight)
```

**F3 (propulsion line D) can and should start now**, in parallel — it does not depend on the new wing geometry (`03-phase-1-plan.md §3.D`). Everything else is sequential because each phase consumes the verified output of the previous one, not its estimate.

---

## 3. F2 — Weights and balancing

| # | Task | Closes | Needed input |
|---|---|---|---|
| P1 | Per-component mass model (shell, carbon, servos, wiring, avionics) | Basis for real CG | Frozen OML (F1) |
| P2 | Parametric CAD model of CORE-1 and PANEL-1300 with per-material densities | Replaces the estimated mass table with real geometry | **Fusion 360** — see §8 |
| P3 | Verify R-CG and mass in CAD for the **6S1P Article #1**; record the station of every optional power module separately | R-CG (docs/00, §3.3), ADR-0043 | P1, P2 |
| P4 | If Article #1 fails: redesign cradle / move equipment relative to the NP | C4 of `03-phase-1-plan.md` | P3 |

**Known constraint:** Article #1 is 6S1P. A 4S or 2P installation is a separate power
module with its own motor, carrier and CG closure; the common airframe is not required
to interchange all historical packs (ADR-0042/0043).

---

## 4. F3 — Performance and propulsion chain

This is line D of `03-phase-1-plan.md` carried to closure. Only the sequence is repeated here; the detail lives there:

| # | Task | Note |
|---|---|---|
| D1 | Build pitot + blackbox + current logging | Blocks D2, D3, E2, E3, E7 |
| D2 | Validate the measurement chain on a platform **that already flies** | Do not wait for article #1 to discover the method fails |
| D3 | Propeller-matching sweep, 3–4 combinations | Against UIUC J |
| D4 | Matching table per pack | **Publishable output** — it is the demonstration of O1 |

**This does not block F1/F2.** It can and should be brought forward.

---

## 5. F4 — Loads and structure

| # | Task | Closes | Depends on |
|---|---|---|---|
| S1 | **Partial:** +6/−3 fixed as provisional manoeuvre limits and +9/−4.5 as ultimate loads. Close the Salamandra-specific dynamic gust basis; the legacy Part 23 result is a screen, not an adopted load. | Precondition of everything else; G11 | I-24/ADR-0044; E9/S3 |
| S2 | **Partial:** positive V-n branch computed (VA 109.0 CLEAN / 110.4 V1 km/h). Add the negative aerodynamic branch after a validated negative-polar analysis/test supplies CLmin; combine it with the dynamic gust envelope. | Load envelope | S1, B3 extension, E9 |
| S3 | Verify the real GJ/EI of the section (D-box + center cell + hinge) against ADR-0002/0015 | G4 | S1, F1 geometry, **Fusion 360** for section geometry (§8) |
| S4 | Sweep factor for divergence on the real EI/GJ ratio, not generic literature | **G6** — declared weakest link | S3 |
| S5 | Verify elevon authority across the whole envelope, including gust and extreme CG | **C6 — never done before**, see `03-phase-1-plan.md` | S2, F2 CG |
| S6 | TPU hinge stiffness (ω_β) | Enters the flutter analysis (G7) | S3 |
| S7 | Flutter verification with Southwell if prior flight data exist, otherwise preliminary analysis | G7 | S3, S6 |
| S8 | **V1 fin (ADR-0038):** strength at V_NE (root t ≥ 3.0 mm, FS 1.67 `[D]`, no spar credit), bending mode ≈ 7.9 Hz, wake buffeting from the pusher slipstream | OP-26; fin flutter/strength | S3, F2 CG |

⚠️ **S5 is the task that corrects failure mode #1.** No final hinge is sized and no mass balancing is computed without having passed S5.

---

## 6. F5 — Systems and propulsion (final integration)

| # | Task | Depends on |
|---|---|---|
| Y1 | Final battery bay with longitudinal adjustment (R-CG confirmed in CAD) | F2, F4 |
| Y2 | Pitot, blackbox, GPS/magnetometer installation out of the root current path (docs/00 §3.5) | D1 |
| Y3 | INAV 9.1+ / ArduPlane configuration | — |
| Y4 | **Resolve G9** (porpoising) — altitude/pitch PID adjustment before flying in automatic modes | Peregrine precedent (gaps/README) |
| Y5 | No-freeplay elevon linkage, one actuator per elevon (ADR-0026) | F4 (verified authority/modal response) |

**Y4 is an explicit prerequisite of E7** (already declared in `tests/README.md`). It is not optional for the test program, although it does not prevent the first uninstrumented flight.

---

## 7. F6 — Manufacturing and release (reaching article #1)

| # | Task | ADR / reference |
|---|---|---|
| M1 | Print-bed segmentation: 3 segments per wing half, 45° | ADR-0024 |
| M2 | Printing: 2 perimeters (0.9 mm), gyroid 5 % infill | ADR-0028 |
| M3 | Joints: tenon + specific PETG adhesive, area ≥ 3× skin section | ADR-0023 |
| M4 | Carbon pin in the joints | ADR-0031 |
| M5 | Full assembly, real-mass check against the F2 model | Closes P2 with an `[M]` datum |
| M6 | **Elevon mass balancing** — mandatory before flying | ADR-0025 |
| M7 | First flight — stabilized, no automatic conditions until G9 closes | Y4 |
| M8 | Release of the manufactured configuration (drawings, real vs. design adjustments) | Consistent with "published rationale" (O6) and the open platform (O12) |

**M7 is the first prototype per the §0 definition.** From here the test program (E2, E3, E5, E7) documented in `tests/README.md` starts.

---

## 8. Fusion 360 — where it enters and under what rules

### 8.1 Tool state

Installed in this session: add-in **`fusion360-mcp-server`** (faust-machines, Beta version, 84 tools) copied to the Fusion 360 Add-Ins folder and registered as this project's MCP server (`claude mcp add fusion360`). Architecture: MCP client ↔ Python server (stdio) ↔ TCP `localhost:9876` ↔ add-in inside Fusion (main thread).

**Pending on your side:** activate the add-in inside Fusion (Shift+S → Add-Ins → Fusion360MCP → Run) when you want it to start being used. It does not need to be running until the plan reaches a task that needs it (see below) — it is not needed for F1, which remains pure calculation (VLM, calibrated XFOIL).

### 8.2 When it enters the flow — not before time

The README already says it: `geometry/`, `stl/`, `cad/` are **Phase 1 outputs and beyond**. Fusion 360 has no task in F1: F1 is parametric geometry on paper/script (planform, airfoil, twist) validated by the in-house VLM, not a 3D solid. Introducing CAD before freezing the OML would be optimizing detail geometry without a closed gate — exactly what `CLAUDE.md` forbids ("Do not skip phases").

| Phase | Concrete Fusion 360 MCP use | Why there and not before |
|---|---|---|
| **F1 close** | Build the parametric CORE-1 + PANEL-1300-cruise solid from the already frozen planform (airfoil, chords, sweep Λ_c/4, twist) | Materializes an already-taken decision; decides nothing new |
| **F2 (P2)** | Mass properties of the assembly with per-material densities, for real CG and R-CG verification | Replaces the manual mass estimate with real geometry |
| **F4 (S3)** | Real section geometry (D-box, center cell, hinge) to check the physical fit of the carbon tube and wall thicknesses before computing GJ/EI | The G4/G6 calculation needs the real section, not an assumption |
| **F6 (M1)** | Print-bed segmentation, 45° orientation, final per-segment STL/STEP export | It is literally what CAD is for at the end of the process |

### 8.3 Confidence rule applied to CAD — the repo convention is not skipped

This is the point most easily overlooked with a new tool: **a figure coming out of Fusion is not automatically `[M]`.**

- Mass, CG, volume or moment of inertia computed on the parametric model are **`[D]`** — derived from a model that in turn assumes declared material densities and a geometry not yet printed.
- They only become `[M]` when **measured on the physical part** (scale, CG rocker) — just as was already done with the Peregrine t/c (G1).
- The add-in is third-party and in **Beta** — it is not a source of geometric truth. Any output critical to an irreversible decision (e.g. the structural GJ feeding S4) **is cross-checked against the repo's own analytical calculation**, not replaced by it. It is the same rule `03-phase-1-plan.md` already applies (C2: "two methods that disagree = error in one") — here the second method is CAD vs. analytical, not VLM vs. VLM.
- If the add-in returns a number and there is no way to tag it yet, **it is not written** (hard rule of `CLAUDE.md`) until the tag is decided.

### 8.4 Declared risk

The server is a third-party Beta project, not Autodesk. If it is abandoned or breaks with a new Fusion version, the parametric model must remain manually reconstructible from the parameters documented in `docs/04-conventions.md` — CAD is a representation of the decisions, not their record. The record remains `decisions/` and `research/`.

---

## 9. Exit gates — consolidated checklist

- [ ] **F1** — complete checklist of `03-phase-1-plan.md §4`
- [ ] **F2** — Article #1 6S1P R-CG and **1553.25 g CLEAN** verified; confirm the analytical **1596.26 g V1** lower model remains ≤1620.4 g using CAD/scale masses and recover or accept its **2.72 mm** forward battery-station shortfall
- [ ] **F3** — D3/D4 completed, matching table published
- [ ] **F4** — manoeuvre/ultimate semantics and positive V-n branch fixed; dynamic gust basis and negative CLmin branch closed, GJ/EI verified on the real section, elevon authority confirmed (S5), G6 sweep factor computed on the real section
- [ ] **F5** — instrumentation chain operational and validated on an existing platform (D2), G9 resolved
- [ ] **F6** — article #1 assembled, balanced, first stabilized flight with valid blackbox data

## 10. What this plan does not cover

- It sets no calendar dates — the repo has no `[M]` data to estimate them.
- It prescribes the Article #1 power-module envelope but keeps future modules open — see
  [ADR-0033](../decisions/ADR-0033-electronics-out.md) and ADR-0042/0043.
- It does not replace any existing ADR or research thread — it only sequences them.
- It does not authorize skipping F1: while G1/G2/G8 remain open, F2 onward has no valid input.
