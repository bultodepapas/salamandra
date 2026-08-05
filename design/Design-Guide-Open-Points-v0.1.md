# Salamandra — Design Guide: Open Points and Evolution

**Version 0.1** · 5 August 2026 · Companion to
[`Salamandra-Design-Guide-v0.1.md`](Salamandra-Design-Guide-v0.1.md)

This document lists everything in the Design Guide that is **not yet fixed**: assumptions
that need verification, values that will change when the corresponding research closes,
and the revision process. It is the "what to watch" map for the designer and for Phase 1.

Every open point names the trigger that resolves it. Until a trigger fires, the v0.1
value stands.

---

## 1. Open points

### Critical

| # | Item | v0.1 value | What changes it | Trigger |
|---|---|---|---|---|
| **OP-01** | **CG reachability** | Target CG −119 mm (18.7 % MAC); preliminary balance shows the reachable band ≈ −27…+29 mm | NP re-verification, body effect, static-margin target or planform | C2 (second independent NP method), F2 mass model (P1–P3); **highest priority** |
| **OP-02** | Airfoil profile | Provisional: MH 45-class root / thinned MH tip; criteria fixed (t/c 13.5/9, Cm0 ≥ +0.008, C_Lmax ≥ 0.65) | Final coordinates from the calibrated B3 screening | G2 closure (I-06 + B3 + E2) |

### Geometry and stability

| # | Item | v0.1 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-03 | Twist ε | +0.5° wash-in | Re-derived from the final airfoil Cm0 (0.17–0.76° band for SM 8 %) | C5 (torsion window closure) |
| OP-04 | Dihedral Γ | 2.0° (polyhedral) | Roll-stability verification; may be revised by the stability analysis | Phase 1 stability (C-series), first flights |
| OP-05 | Neutral point | 26.7 % MAC `[D]` (VLM only) | Independent method + central body | C2; body model (I-07 §7.4) |
| OP-06 | Elevon span / travel | 20–90 % half-span, ±20° | Authority verification across the envelope (gust, extreme CG) | C6 — never done before |
| OP-07 | Hinge line x/c | 0.72 | Fixed by structure (ADR-0002); keep unless section is redesigned | — |

### Structure and materials

| # | Item | v0.1 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-08 | Carbon tube Ø12×1.0 | Provisional (bending only) | Real GJ/EI verification on the section; final sizing | S3/F4 (G4 closure) |
| OP-09 | D-box web at x/c 0.30 | Provisional | Section optimization (cell layout) | S3 |
| OP-10 | TPU hinge stiffness | Characterized later | K_hinge enters ω_β (flutter); can be off by factor 3 | C7/S6 (G7) |
| OP-11 | Printing temperatures | 240–250 °C nozzle / 70–80 °C bed | First test prints | First real part |

### Propulsion

| # | Item | v0.1 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-12 | Motor | 28-class, 500–550 KV (reference only) | Matching table (prop–pack–speed) | D3/D4; E3 |
| OP-13 | Propeller | APC-E 8×8 reference | Matching sweep against UIUC J | D3/E3 |
| OP-14 | Pusher vs twin tractor | Single pusher (disputed ADR-0006) | Comparative wake data at Re 4×10⁵ | G5 |
| OP-15 | Thrust angle | 0.8° up (Peregrine precedent) | Flight trimming | First flights, E7 |

### Systems and integration

| # | Item | v0.1 value | What changes it | Trigger |
|---|---|---|---|---|
| OP-16 | Battery bay 180×70×32 mm | Provisional | R-CG verification in CAD with real packs | F2/P3 |
| OP-17 | Pitot probe position | y ≈ 260 mm LE | Install/test convenience | D1/D2 |
| OP-18 | FC pitot input | SpeedyBee F405 WING (not MINI) must be verified | Bench check before buying | D1 |
| OP-19 | Bay position (nose) | As far forward as possible | OP-01 resolution | C2 + F2 |

---

## 2. What is NOT expected to change

- Wingspan 1300 mm, S = 0.282 m², AR 6.0 (ADR-0004, ADR-0010 — branch A is material-forced)
- t/c 13.5 % / 9 % (ADR-0027 — one of the best-supported decisions)
- Sweep Λ_c/4 = −20° (I-07 family alignment; ±2–4° adjustment is the compensation knob)
- Skin 0.9 mm / gyroid 5 % (ADR-0028), three-cell section (ADR-0002)
- Elevon mass balancing (ADR-0025 — non-negotiable), dual actuation (ADR-0026)
- Joint at 30 % half-span, R-JOINT ≥ 5×, R-NP (ADR-0032)
- Confidence convention, traceability rules (docs/04)

---

## 3. How this guide evolves

1. Each resolved open point produces a **new version** of the Design Guide (0.1 → 0.2 → …)
   with the value updated and the justification annotated.
2. Version bumps are recorded in the guide's §14 and in the [CHANGELOG](../CHANGELOG.md).
3. The designer works from the latest version; the repository always keeps the history
   (no silent edits — project rule).
4. **v1.0** = the configuration actually built as Article #1 (printed, assembled, balanced,
   flying with valid blackbox data; per `docs/05-master-plan.md` §0).

Suggested workflow: the designer raises issues against this document for any value that
cannot be realized in CAD (clearance, printability, servo fit, balance), and the open
point that forced the change is closed with the resolution.

---

## 4. Revision log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-08-05 | First release. OP-01 (CG reachability) identified from a preliminary moment balance; all other open points carried from Phase 1 plan. |
