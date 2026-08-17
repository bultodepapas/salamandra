# Phase 1 plan — Geometry and stability

**Revision 1.3** · 17 August 2026
Closes G1, the computational/CAD part of G2, and G8. **Exit gate: frozen OML and
verified static margin; E2 retains physical airfoil acceptance.**

---

# 1. Why this is not a sequence

The temptation is to go airfoil → planform → neutral point → CG → twist. **It does not work that way.** The four are a single coupled problem:

- The **neutral point** depends on planform *and* airfoil.
- The **CG** depends on where the battery fits, which depends on thickness, which depends on the airfoil.
- The **twist** must close the trim at the design CL, which depends on the static margin.
- **Reflex** and **twist** are **substitutes**: both provide the positive pitching moment.

Phase 1 is an iteration. What follows organizes it so it converges in a few loops.

---

# 2. The central trade: the torsion window

Development in [I-02](../research/I-02-tailless-trim.md).

    minimum trim  ≤  ε_wash-in  ≤  tip stall limit

| Limit | Origin | Effect of violating it |
|---|---|---|
| **Lower** | Enough C_m is needed at cruise CL | No compensation without permanent deflection → trim drag and loss of authority |
| **Upper** | Wash-in raises the tip incidence | **The main forward-sweep advantage is cancelled** |

And room must be **left for elastic wash-in**, which grows with dynamic pressure.

**If the window is empty, reflex must be added** — and reflex costs C_Lmax, a hard requirement due to hand launch. **This is the Phase 1 decision.**

**Starting datum `[M]`:** the Peregrine needs +3° of level-flight pitch in INAV — its built twist falls short. Suggests the window exists but is narrow.

---

# 3. Work streams

## A — Reference geometry *(blocker)*

| # | Task | Closes | Status |
|---|---|---|---|
| A1 | Peregrine panel planform: c/4 sweep, taper, chords | G1, R1 | Blocked — wing files missing |
| **A2** | **Peregrine twist distribution** | G1, validates ADR-0003 | Blocked |
| A3 | Airfoil coordinates at 3–5 stations | R2 | Partial — t/c done |
| A4 | StuntDouble family (Nemesis + Stinger/Stormbird) | R3, R4 | **Partial** — sources acquired and [I-08](../research/I-08-stuntdouble-family.md) published; planform and twist still to reconstruct |

**A2 is the highest-value task:** it empirically answers the §2 question before calculating anything.
**A4 provides a quasi-controlled comparison** between forward sweep and *plank*: same author,
constructive family and comparable AR, but PW51/PW75 airfoils and non-identical propulsion.
It serves to bound geometry; **it does not allow attributing causality to the sweep**. See
[I-08](../research/I-08-stuntdouble-family.md).

## B — Airfoil and polars *(CAD closure complete; measured G2 acceptance open)*

Solved by **calibration**, not by search.

| # | Task | Method |
|---|---|---|
| **B1** | **Calibrate XFOIL against measured data** | **Partial — [I-06](../research/I-06-reflexed-airfoils.md).** E387 (C) shows there is no single Ncrit; validate the 10–12 band against a second E387 model |
| B2 | Screening criteria | t/c 13.5/9 % · C_Lmax ≥ 0.65 · coupled SM 8 % trim within ±0.6° neutral elevon · L/D at cruise CL |
| B3 | Screen/design candidates with calibrated N_crit | **Executed computationally:** Salamandra r1 root/tip family (ADR-0041); E2 remains the measured closer |
| B4 | Publish polars with their calibration | `[D]` output, declare it |

⚠️ Without calibration, XFOIL at low Re is optimistic and systematically wrong in the laminar bubble. Output is always `[D]`; it becomes `[M]` with E2.

## C — Stability *(the gate, G8)*

| # | Task | Method |
|---|---|---|
| C1 | Neutral point with a panel method | XFLR5 VLM on the A1 planform with the B3 airfoil |
| C2 | Verify with an independent analytical method | Sweep correction on section AC. **Two methods that disagree = error in one** |
| C3 | Set the target static margin | 8–12 % of MAC. Not below 6 % even with FC |
| C4 | CG position and **adjustment window** | Must meet **R-CG ±5 mm** in the 6S1P Article #1 configuration; other packs are separate modules |
| C5 | Resolve the torsion window (§2) | Iterate twist and reflex until trim closes with tip-stall margin |
| **C6** | **Verify elevon authority** | Deflection needed across the whole envelope, including gust and extreme CG |
| C7 | Characterize TPU hinge stiffness | Enters ω_β and therefore the flutter analysis |
| **C8** | **Directional stability budget and flight closure (I-20)** | Cnβ budget `[D]`/`[E]` done (`yaw_stability.py`); the two published configurations (ADR-0038); **E8 (yaw perturbation, Dutch-roll decay) is the `[M]` closure of G10** |

> **C6 had never been done.** The hinge at 72 % was sized and its flutter and mass balancing were calculated **without checking that it gives enough authority**. Inverted order, corrected here.

**C4 may force a bay or CORE redesign.** That is where battery modularity is paid for or collected.

## D — Propulsion *(parallel, decoupled)*

**It depends on nothing above.** And it contains the project's central claim.

| # | Task | Note |
|---|---|---|
| D1 | Build the measurement chain: pitot + blackbox + current logging | Instrument of E2, E3 and E7 |
| **D2** | **Validate the method on an existing platform** | Stabilized flight, speed sweep, data reduction |
| D3 | Propeller-matching sweep | APC 8×8 equilibrium solved at O1 power; bench alternatives remain |
| D4 | Matching table per power module | 6S reference published; 4S requires ~730 Kv and its own carrier/CG closure |

**D2 is the most underrated step in the plan.** It validates the whole measurement chain on an aircraft that already flies, before the new one exists. If the method does not work there, it will not work later — and it would be far worse to discover that with article #1.

⚠️ **Verify before buying:** the SpeedyBee F405 WING **MINI** may lack a pitot input. Without it, E2 and E7 are not possible on that platform.

---

# 4. Sequence

```
NOW            A3 A4 (partial)  ──┐
               B1                ─┼──► can start today
               D1 D2             ─┘

BLOCKED        A1 A2  (requires wing files or route A4)

AFTER A+B      C1 C2 C3
               ↓
               C4 ──► does it meet R-CG?      NO ──► bay/CORE redesign
               ↓ YES
               C5 ──► torsion window?         NO ──► back to B3 with reflex
               ↓ YES
               C6 ──► enough authority?       NO ──► rethink hinge
               ↓ YES
        ═══ PHASE 1 GATE ═══

PARALLEL       D3 D4  (any time after D2)
```

## Exit criteria

- [ ] Planform defined: wingspan, chords, c/4 sweep, taper
- [ ] Airfoil selected with calibrated `[D]` polars
- [ ] Twist distribution defined
- [ ] Neutral point computed by **two methods** that agree
- [ ] Static margin 8–12 % with achievable CG
- [ ] **R-CG verified** in the 6S1P Article #1 configuration
- [ ] **Elevon authority verified** across the whole envelope
- [ ] Torsion window closed with tip-stall margin
- [ ] **Directional stability budget quantified and the yaw test defined (C8/I-20, ADR-0038)**

**None of this requires printing.**

---

# 5. Plan risks

| Risk | Prob. | Mitigation |
|---|---|---|
| **The torsion window comes out empty** | Medium | Accept reflex and lose C_Lmax → may force increasing area |
| Future 4S/2P module fails its propulsion/CG chain | Medium | Treat each as a separate variant ADR; do not promise drop-in packs |
| Calibrated XFOIL still unreliable in the bubble | Medium | Declare `[D]`, close with E2. Do not freeze irreversible decisions on B |
| Cannot get the Peregrine wing files | **High** | A4 (StuntDouble) as an alternative planform source |
| The test FC does not support pitot | Medium | Verify before buying; look for an alternative FC for the bench |
| **G9 prevents E7** | Medium | Adjust the altitude loop before testing |

---

# 6. What can start today

1. **B1** — complete the *holdout* of the Ncrit 10–12 band against E387 (C).
   The first reproducible calibration is already in [I-06](../research/I-06-reflexed-airfoils.md).
2. **D1** — order the pitot. Material with lead time; blocks E2, E3 and E7.
3. **A4** — complete the planform and twist reconstruction of the StuntDouble family.
   The sources are already acquired; the comparison is quasi-controlled, not causal.
