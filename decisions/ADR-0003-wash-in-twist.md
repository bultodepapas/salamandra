# ADR-0003 — Wash-in twist for trim (forward sweep)

**Status:** 🔄 Provisional · **Date:** 2026-07-27 · **Reviewed:** 2026-08-17 · **Confidence:** Medium · **Reversible:** Partial
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
axis through the local c/4 point. Guide §5.3: **ε = +3.0° at the tip** (PROVISIONAL
cap), bounded by the torsion window: the section-Cl screen retains 0.012 margin at the
1.620 kg O1 design mass (`ventana_torsion.py`). Keep the value parametric.

## Rationale `[D]`

Trim requirement at SM 8 %: Cm0_req = CL·SM = 0.132 × 0.08 = **0.0106**. On the −15°
planform the VLM gives +0.00249 Cm per degree of full-span wash-in and +0.00256 Cm per
degree of elevon incidence over 30–90 % half-span. The favourable provisional
MH60→13.5 % moment (cm0 +0.0016) therefore needs 3.60° equivalent: 3.0° printed wash-in
plus ≈ 0.6° permanent reflex. The adverse Ncrit-12 polar (cm0 −0.0018) requires ≈ 1.9°
reflex and fails the cap (`elevon_authority.py`). Final B3 polars are a CAD-freeze gate,
even though 5° of actuator travel provides 2.6× the limiting trim deficit.

## Consequences

- The trim drag advantage of forward sweep depends on this value (balance force acts up
  and ahead of the CG — I-02).
- **Elastic wash-in is dangerous:** aeroelastic divergence also produces wash-in (I-02,
  I-05). The two add up and grow with dynamic pressure — the value is a *setting*, not a
  fixed property; it is re-derived when the final airfoil Cm0 is fixed (**C5**) and
  verified in flight (E7).
- Keep the twist **parametric in CAD** (guide §5.2).

## Review conditions

C5 closure (torsion window with the B3 airfoil), then E2/E7 flight data.
