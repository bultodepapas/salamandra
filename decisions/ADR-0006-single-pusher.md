# ADR-0006 — Single pusher motor preferred

**Status:** ⚠️ Under dispute · **Date:** 2026-07-27 · **Confidence:** Low `[I]` · **Reversible:** Yes
**Research:** [I-13 — Pusher vs tractor slipstream at low Re](../research/I-13-pusher-tractor-slipstream.md) (proposed), [I-02](../research/I-02-tailless-trim.md)
**Gap:** [G5](../gaps/README.md)

## Context

The reference layout of the Salamandra is a single rear pusher. The alternative is a twin
tractor, which has legitimate arguments in its favor (first_investigation §6.1):

- Larger total disk area;
- **Yaw control via differential thrust** (relevant to the directional configuration,
  I-20/ADR-0038, where the finless baseline has no yaw effector);
- Redundancy;
- Mass distribution against flutter.

And the wash over the wing has an **ambiguous sign**: it may *suppress the laminar
separation bubble*, the mechanism Hepperle identifies as the main penalty of reflexed
airfoils. **There is no data to resolve it** — it is the open question of highest
experimental value.

## Decision

**Single rear pusher as the reference layout** (guide §10.1), PROVISIONAL and under
dispute. The pusher keeps the wing unwashed by the propeller disk (disk plane at
x ≈ +235, aft of the root TE at +216.9 — C25/C26).

## Consequences

- The G5 question reduces to the CORE rear-pod wake and the elevon inner end at large
  deflections (I-13) — bounded scope.
- With the V1 fin behind the disk (ADR-0038/I-20), the fin operates in the slipstream
  (η ≈ 1.25): maximum yaw effectiveness at low speed, where launch and stall handling
  need it.
- If the directionally unstable finless baseline (G10) proves unacceptable in flight,
  twin tractor with differential thrust becomes a candidate resolution — the dispute
  and the directional question are linked (I-20 §8).

## Review conditions

Comparative wake data at Re 4×10⁵ (I-13) or a comparative in-flight test; OP-14.
