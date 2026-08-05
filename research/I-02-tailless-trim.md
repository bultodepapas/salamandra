# I-02 — Tailless trim and forward sweep

**Status:** Closed · **Feeds:** ADR-0001, ADR-0003, ADR-0027

## Question

How is a tailless wing trimmed, and what does forward sweep gain or lose versus aft sweep?

## Trim mechanism

A tailless wing requires positive pitching moment. **There are only two paths:** an airfoil with positive C_m0 (reflex), or a combination of sweep and twist.

For sweep, the two solutions are **symmetric**:

| Planform | Required twist | Tip loading at zero lift |
|---|---|---|
| Aft sweep | **Wash-out** (tip down) | Downward — subtracts lift |
| **Forward sweep** | **Wash-in** (tip up) | Upward — adds lift |

In forward sweep the tips go **ahead of** the CG: wash-in generates more lift ahead → nose-up moment. It is the natural trim source of this planform.

> **Correction C2.** It was initially claimed that forward sweep depends exclusively on the airfoil C_m0 because twist could not be used. **False: it can and should use wash-in.**
>
> Consequence of great practical value: **the airfoil can be lightly reflexed or not reflexed at all**, with better C_Lmax and better L/D than the classic reflexed airfoils — if the wash-in suffices to close the trim.

## Advantage 1 — trim drag

In forward sweep the balance force acts **upward and ahead of the CG**: the total lift required is essentially equal to the weight. In aft sweep, balance requires negative tip loading and the wing must generate **more** than the aircraft weighs.

Documented in US 4.545.552 and US 4.674.709.

⚠️ Patents, not peer-reviewed literature. The physical argument is correct and verifiable; **the magnitude of the benefit is not quantified by an independent source.**

## Advantage 2 — stall behavior

The spanwise flow runs from tip to root. **The root stalls first**, and the outer elevons keep effectiveness by remaining in high-energy air. `[M]`, multiple independent sources.

For a flying wing this weighs double: **the elevons are the entirety of the control.**

## Risk — aeroelastic divergence

See [I-05](I-05-divergence-flutter.md) for the full treatment.

### Dangerous coupling `[I]`

The tailless forward-swept wing **needs wash-in for trim**, and aeroelastic divergence **also produces wash-in**. The two effects add up, and the second grows with dynamic pressure.

**Consequence: the trim state shifts with speed.** An aft-swept wing has the opposite sign and self-damps.

This explains three TBS Mojito characteristics that previously had no explanation: extremely forward CG, recommendation to move it even further forward, and deliberately short elevon deflections.

Additional documented risk: with sufficient aeroelastic deflection, **the tips can stall first, cancelling the main advantage** — precisely when it is most needed `[M]`.

## The torsion window — Phase 1 central problem

    minimum trim  ≤  ε_wash-in  ≤  tip stall limit

| Limit | Origin | Effect of violating it |
|---|---|---|
| Lower | Enough C_m is needed at cruise CL | No compensation without permanent deflection → trim drag and loss of authority |
| Upper | Wash-in raises the tip incidence | **The root-stall advantage is cancelled** |

And room must be **left for elastic wash-in**, which grows with speed.

**If the window is empty, reflex must be added** — and reflex costs C_Lmax, which is already a requirement due to hand launch.

## Relevant empirical datum `[M]`

The Peregrine 840 mm documentation indicates adjusting in INAV **"level flight pitch: 0 → 3°"**. It means the aircraft needs 3° of nose-up attitude for level flight: **its built incidence/twist falls 3° short**.

It is the only available datum on the real trim state of an in-service printed forward-swept wing.

## Sources

- US 4.545.552 and US 4.674.709 — tailless forward-sweep configuration *(patents)*
- X-29 program documentation
- aerodesign.de — airfoil database for flying and tailless wings
- Peregrine 840 mm technical datasheet
