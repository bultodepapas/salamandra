# ADR-0040 — Quarter-chord sweep reduced to −15°

**Status:** ⬜ Superseded for the redesigned Article #1 by
[ADR-0048](ADR-0048-article-1-mission-and-configurations.md); retained as the v0.6
forward-sweep candidate · **Date:** 2026-08-17 · **Confidence:** Medium `[D]`/`[E]`
**Reversible:** Yes, before the first production CAD release
**Research:** [I-21 — Sweep trade and elastic-axis correction](../research/I-21-sweep-trade-and-elastic-axis-correction.md)
**Calculation:** [sweep_trade.py](../calculations/sweep_trade.py)
**Feeds:** guide §§3/5/9, OP-01, OP-03, OP-23, OP-29, ADR-0003

**2026-08-21 reset:** -15 degrees is candidate A inside the M3 architecture trade, not
the canonical redesigned planform. Existing calculations remain valid for that candidate.

> **2026-08-18 update:** the sweep selection remains active. The trade has been rerun
> with ADR-0041/0045 and the 1.59626 kg V1 lower model. Current physical-elevon trim is
> −0.14°…+0.50° and the CLEAN component-layout 6S1P station is −337.74 mm.
>
> **2026-08-21 ADR-0047 correction:** that trim statement is a historical cruise-only
> result. The −15° planform and wing-only neutral point remain the analytical baseline,
> but r1 and the 8% CG target are held. r2a tests a 5% nominal target at xCG −87.035 mm.

**Article #1 redesign:** `CANDIDATE-ONLY` · **Gate:** `M3` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## Context

The −20° quarter-chord sweep was inherited from the concept geometry. It had not been
selected against the coupled neutral-point, trim, battery-packaging and aeroelastic
constraints. It also amplified the project's dominant uncertainty: forward-sweep
divergence. A repository audit found a second problem in the previous divergence
calculation: it labelled the enclosed-area centroid as a shear centre. That identity is
not valid for this multicell printed section and made the apparent precision misleading.

## Alternatives considered

All candidates retain the fixed 1.300 m span, 0.282 m² area, taper ratio 0.50 and the
same root/tip airfoils. The full-resolution comparison uses a 32 × 5 horseshoe VLM,
100-station Weissinger calculation and the self-consistent mass/balance model. The
section-Cl screen uses the current **1.59626 kg V1 analytical lower model** at 45 km/h.
Physical mass, CLmax and battery travel remain explicit F2/E2/OP-24 closures.

| Λc/4 | VLM NP (mm) | Twist + permanent reflex | Peak section Cl | 6S1P station (mm) | Relative divergence speed `[E]` | Result |
|---:|---:|---:|---:|---:|---:|---|
| −20° | −101.5 | 2.45° + 0.00° | 0.624 | −399.5 | 1.00 | Feasible, lowest aeroelastic return |
| −16° | −80.9 | 3.11° + 0.11° | 0.628 | −363.3 | 1.10 | Feasible |
| **−15°** | **−75.9** | **3.33° + 0.33°** | **0.629** | **−354.4** | **1.15** | **Selected** |
| −12° | −60.9 | 4.22° + 1.22° | 0.632 | −327.7 | 1.23 | Reject: exceeds trim-authority cap |
| −10° | −51.0 | 5.11° + 2.11° | 0.634 | −309.9 | 1.28 | Reject: exceeds trim-authority cap |

The trim-authority cap is 3.0° of printed twist plus 0.6° of equivalent permanent
elevon reflex. It is deliberately treated as a design constraint, not an invitation to
consume flight-control travel in steady trim.

## Decision

Set the canonical planform to **Λc/4 = −15.0°**. At the fixed taper this gives
**ΛLE = −11.99°**, **ΛTE = −23.50°** and a tip quarter-chord station of **x = −174.2 mm**
relative to the root leading edge.

Use the full-resolution VLM neutral point, **xNP = −75.8 mm** from the root quarter-chord
datum, for balance sizing. With an 8 % MAC static margin, set the target CG to
**xCG = −93.8 mm**. The independent Weissinger result is −72.9 mm; the 2.9 mm spread is
retained as method uncertainty, not averaged away.

## Rationale

−15° is the least-negative sweep that remains inside every declared constraint. Relative
to −20°, it moves the 6S1P pack aft by about 48 mm, shortens the required forward
extension by about 47 mm and improves the literature-anchored divergence-speed trend by
approximately 15 %. Moving to −12° would add only a further 7 % trend improvement while
violating the trim cap by 0.62°; that is a poor exchange of control margin for structure.

The divergence trend is anchored to NASA TP-1685's measured and calculated
forward-swept-wing results. Only the trend is transferred: its numerical scale is not
portable to this PETG wing. Printed-shell GJ and elastic-axis location remain `[E]` until
coupon/wing measurements close E7.

## Consequences

- [design_config.py](../calculations/design_config.py) is the single numerical source for
  span, area, taper, sweep, thickness schedule and planform stations.
- With the released r1 family, ADR-0045 elevons and C32 V1 lower mass, 3.0° printed
  wash-in historically left −0.14°…+0.50° physical-elevon trim at cruise. ADR-0047
  supersedes that as a whole-envelope claim; E2A owns measured aerodynamic acceptance.
- Under the current ADR-0043/0045 allocation, the CLEAN component-layout 6S1P P42A pack station is −337.74 mm and
  lies inside the one-layer cradle. Other packs require separate module closure.
- The conservative unmeasured divergence case supports an initial limit of **105 km/h**.
  If the Gxy-plane stiffness coupon validates the corresponding model, the calculated
  limit becomes **150 km/h**. These are test gates, not structural promises.

## Review conditions

Review the angle if any of the following occurs: (1) final XFOIL/CFD polars require more
than 0.6° permanent reflex at 3° twist; (2) measured neutral point differs by more than
5 mm; (3) the one-layer 6S1P pack cannot be placed at the calculated station; or (4)
measured GJ/elastic-axis data change the conservative divergence ranking.
