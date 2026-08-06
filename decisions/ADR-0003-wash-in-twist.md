# ADR-0003 — Wash-in twist for trim (forward sweep)

**Status:** 🔄 Provisional · **Date:** 2026-07-27 · **Confidence:** High · **Reversible:** Partial
**Research:** [I-02 — Tailless trim and forward sweep](../research/I-02-tailless-trim.md), I-07, I-15

## Context

A tailless wing requires a positive pitching moment. There are only two paths: an airfoil
with positive Cm0 (reflex) or a combination of sweep and twist. The two sweep solutions are
symmetric: aft sweep needs **wash-out** (tip down, subtracts lift), forward sweep needs
**wash-in** (tip up, adds lift ahead of the CG — the natural trim source of this planform).

> **Correction C2:** it was initially claimed that forward sweep depends exclusively on the
> airfoil Cm0 because twist could not be used. **False — it can and should use wash-in**
> (I-02). This allows a lightly reflexed (or unreflexed) airfoil with better C_Lmax and L/D.

## Decision

**Geometric twist of the wash-in type** (project sign: ε positive = tip at higher
incidence), linear root → tip, applied as a rotation of each section about the spanwise
axis through the local c/4 point. Guide §5.3: **ε = +0.5° at the tip** (PROVISIONAL),
bounded by the torsion window **R-TWIST ≤ 3.0°** (raised from 2.5° in the OP-01 pass —
the stall criterion holds at 3.0°; `ventana_torsion.py`).

## Rationale `[D]`

Trim requirement at SM 8 %: Cm0_req = CL·SM = 0.132 × 0.08 = **0.0106**. With an airfoil
Cm0 of +0.010, twist needed ≈ 0.17°; with +0.008, ≈ 0.76° (yield 0.00338°/° wash-in, I-07;
0.00348°/° over the 30–90 % elevon span). Mid-band value **+0.5°**, far below the
R-TWIST cap that protects the tip-stall margin (I-02: wash-in raises the tip incidence —
if it exceeds the window, the root-first-stall advantage is cancelled). The B3 screening
(I-15 §6.2) shows the required wash-in at SM 8 % is 2.6–3.7° (MH60→13.5 %) — the
provisional +0.5° is confirmed to be on the conservative side, and the residual trim is
closed by ≤ 0.6° of permanent elevon reflex (`elevon_authority.py`).

## Consequences

- The trim drag advantage of forward sweep depends on this value (balance force acts up
  and ahead of the CG — I-02).
- **Elastic wash-in is dangerous:** aeroelastic divergence also produces wash-in (I-02,
  I-05). The two add up and grow with dynamic pressure — the value is a *setting*, not a
  fixed property; it is re-derived when the final airfoil Cm0 is fixed (**C5**) and
  verified in flight (E7).
- Keep the twist **parametric in CAD** (guide §6.3).

## Review conditions

C5 closure (torsion window with the B3 airfoil), then E2/E7 flight data.
