# ADR-0032 — Modular CORE + PANEL architecture

**Status:** ✅ Active · **Date:** 2026-07-28 · **Confidence:** High · **Reversible:** No

**Article #1 redesign:** `REOPENED` · **Gate:** `M2/M3/M6` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## Context

The project must support different uses (range, cruise, sport) and different batteries (4S–6S) without redesigning the aircraft. The natural path is to modularize. **On a tailless aircraft that path has a trap.**

## The trap

On a conventional aircraft you change wings and the tail still governs stability. **Here the wing *is* the stability.** A longer panel changes the aspect ratio, the MAC and the **neutral point position**. A different airfoil changes the C_m0 and with it the trim.

**Consequence: arbitrary panels cannot be offered.** A set that moves the neutral point 15 mm turns an 8 % static margin into 15 % — or negative.

## Decision

**Standard center module (CORE) + interchangeable panels (PANEL)**, with two mandatory derived requirements.

```
CORE-1          Wing joiners up to ~30 % of half-span,
                battery bay with longitudinal adjustment, avionics, motor mount.
                Sized for the most demanding panel.

PANEL-xxxx-y    xxxx = resulting total wingspan · y = airfoil family
```

## R-NP — common family neutral point

**Each panel set is designed against a common target neutral point.** Long panels compensate with different sweep or twist to bring the NP back into the band.

There is no panel freedom: there is a **validated catalog that shares the balance**.

## R-JOINT — interface stiffness

The joint is a **torsional spring in series** with the wing:

```text
1/k_eff = 1/k_wing + 1/k_joint
```

| Joint stiffness | Effective GJ | Penalty in V_div |
|---|---|---|
| Same as the section | 50 % | −29 % ❌ |
| 3× | 75 % | −13 % ⚠️ |
| **5×** | **83 %** | **−9 %** ✅ |

**Requirement: joint torsional stiffness ≥ 5× that of the adjacent section.**

Two design consequences:

1. **The joint is not at the root** — that is where the torque is maximum. The CORE carries joiners up to ~30 % of half-span, where the torque has fallen to half. That is what modular gliders do, and for this reason.
2. **Two pins, not one.** A single tube transmits bending but leaves torsion to the sleeve fit. Two separate pins transmit the torque **as a couple**, with the arm entering linearly: main tube + anti-rotation pin 60–80 mm behind.

## Consequences

- The CORE is **oversized** for the short panel. That is the price, and it is acceptable: it is the part that is not reprinted.
- Modularity is also the project's **iteration strategy**: if a panel comes out soft or badly balanced, the panel is reprinted and the CORE survives.
- Forces publishing **validated configurations**, not loose parts.

## Published configurations

| Config | Panels | Suggested battery | Use |
|---|---|---|---|
| Range | 1600 | 4S2P Li-Ion 21700 | Maximum range |
| **Cruise** | 1300 | 6S1P Li-Ion 21700 | **Article #1** |
| Sport | 1100 | 6S LiPo | Fast flight |
