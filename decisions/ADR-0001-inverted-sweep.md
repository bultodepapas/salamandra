# ADR-0001 — Forward-swept flying wing

**Status:** ✅ Active · **Date:** 2026-07-27 · **Confidence:** High · **Reversible:** No
**Research:** [I-02 — Tailless trim and forward sweep](../research/I-02-tailless-trim.md)

## Context

The mission (FPV cruise, hand launch, compact transport) admits a flying wing or a tailed configuration. Within a flying wing, the sweep can be aft or forward.

## Alternatives considered

| Option | For | Against |
|---|---|---|
| Conventional tail | Trivial stability, free airfoil | More parts, more drag, more fragile on belly landing |
| Aft-swept flying wing | Majority solution, no divergence | Requires wash-out: the tip subtracts lift; tip-first stall |
| **Forward sweep** | More efficient trim, root-first stall | **Aeroelastic divergence** |

## Decision

**Forward-swept flying wing, without a tail.**

## Rationale

1. **Trim-drag advantage.** In forward sweep the balance force acts upward and ahead of the CG: the total lift required is essentially equal to the weight. In aft sweep, balance requires negative tip loading and the wing must generate **more** than the aircraft weighs. Documented in US 4.545.552 and US 4.674.709.
   ⚠️ They are patents, not peer-reviewed literature. The physical argument is verifiable; **the magnitude is not quantified by an independent source.**

2. **Stall behavior.** The spanwise flow runs from tip to root: **the root stalls first** and the outer elevons keep effectiveness. `[M]`, multiple independent sources. On a flying wing this weighs double: the elevons are the entirety of the control.

3. **Independent convergence.** Two designers reached the same planform with no relation to each other: the StuntDouble family (Interceptor / Eliminator / Nemesis) and the Peregrine 840 mm.

## Consequences

- **Opens the project's dominant risk:** aeroelastic divergence. See [I-05](../research/I-05-divergence-flutter.md).
- Requires **wash-in** type twist (ADR-0003), not wash-out.
- Requires prioritizing **torsional stiffness** over mass throughout the sizing.
- The CG and neutral point stop being intuitive: they require calculation (gap G8).

## Review conditions

Only reconsidered if test E7 measured an unacceptably low divergence speed and there were no structural solution within the mass budget.
