# ADR-0003 — Wash-in twist for trim (forward sweep)

**Status:** 🔄 Retained for r2a E2A; flight-wing closure held by ADR-0047 · **Date:** 2026-07-27 · **Reviewed:** 2026-08-21 · **Confidence:** Medium `[D]` · **Reversible:** Partial
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
axis through the local c/4 point. Guide §5.3: **ε = +3.0° at the tip**, bounded by the
torsion window. Keep the value parametric until E2 measures the released r1 sections.

## Rationale `[D]`

Trim requirement at SM 8 %: Cm0_req = CL·SM = 0.132 × 0.08 = **0.0106**. On the −15°
planform the VLM gives +0.00249 Cm per degree of full-span wash-in and +0.00256 Cm per
degree of equivalent elevon incidence over the former 30–90 % half-span reference.
ADR-0045 supersedes that control geometry with a 35–90 % hinged-flap model yielding
**+0.00183 Cm per physical degree**. ADR-0041 integrates the released r1
root/tip moments with c² weighting: +3.0° wash-in closes neutral trim at
**−0.14°…+0.50° physical elevon** at the corrected V1 lower-model mass over Ncrit
10/12. Five degrees of actuator travel provides about 10× the limiting residual
(`elevon_authority.py`).

## Consequences

- The trim drag advantage of forward sweep depends on this value (balance force acts up
  and ahead of the CG — I-02).
- **Elastic wash-in is dangerous:** aeroelastic divergence also produces wash-in (I-02,
  I-05). The two add up and grow with dynamic pressure — the value is a *setting*, not a
  fixed property; it is verified against the r1 section behavior in E2 and in flight E7.
- Keep the twist **parametric in CAD** (guide §5.2).

## Review conditions

Review if E2 moment/stall data move neutral trim outside ±0.6°, then verify in E7.

**2026-08-21 review:** ADR-0047 fired this condition before E2 flight testing. The
operating-`Cm(CL)`/deflected-section model reopens twist as a coupled variable. +3.0°
is retained in r2a coupon geometry only; the historical cruise intercept no longer
constitutes trim closure.
