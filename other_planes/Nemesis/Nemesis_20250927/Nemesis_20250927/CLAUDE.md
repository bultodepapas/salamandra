# CLAUDE.md

Context and working rules for AI assistants in this repository.

---

## What this project is

Forward-swept FPV flying wing, **modular**, printed in PETG. This is not an STL repository: **it is a reasoning repository**. The STL will come later.

The contribution is that **every decision carries its rationale, its source, and its confidence level**, and that **mistakes are recorded instead of erased**.

If at the end of a session the repository has more geometry but less traceability, the session was negative.

---

## The central rule — non-negotiable

Every quantitative claim carries a tag:

| Tag | Meaning |
|---|---|
| `[M]` | Measured and published by a primary source |
| `[D]` | Derived by calculation from `[M]` data |
| `[E]` | Estimated on declared assumptions |
| `[I]` | Reasoned inference, not verified |

> **No `[E]` or `[I]` datum supports an irreversible decision without prior verification.**

**Operational corollary:** if you are about to write a number, first decide its tag. If you do not know which tag to give it, do not write it yet.

**Numbers without a source are not accepted, even if they are correct.** An orphan figure that is correct today is an unverifiable figure tomorrow.

---

## Current status

**Phase 0 closed. Phase 1 (geometry and stability) in progress.**

Before proposing anything, read in this order:

1. [`README.md`](README.md) — status and navigation
2. [`docs/00-objectives-and-requirements.md`](docs/00-objectives-and-requirements.md) — the specification
3. [`gaps/README.md`](gaps/README.md) — **what we do not know**
4. [`docs/03-phase-1-plan.md`](docs/03-phase-1-plan.md) — what is due now

**The current blocker is in `gaps/`.** Do not assume it: read it, it changes.

---

## Repository map

| Folder | What it contains | When to write here |
|---|---|---|
| `docs/` | Specification, phase plan, conventions, measured data | A requirement or objective changes |
| `decisions/` | **ADR: one decision per file** | A decision is made, superseded or cancelled |
| `research/` | Research threads: what was searched and found | Something is researched, even if it decides nothing |
| `gaps/` | Register of unknowns G1–G9 | A gap is opened, bounded or closed |
| `tests/` | Experimental program and data | A test is defined or run |
| `calculations/` | Analysis scripts **with validation case** | A calculation is written or modified |
| `geometry/` `stl/` `cad/` | Phase 1 outputs and beyond | Not yet |

**`decisions/` and `research/` are separated on purpose.** An ADR says *what was decided*; a research thread says *what we know and how*. One piece of research feeds several decisions and one decision rests on several pieces of research. Merging them forces duplication or loss of traceability.

---

## How to work here

### When making a decision

Create an ADR from [`decisions/TEMPLATE.md`](decisions/TEMPLATE.md). Sequential numbering. It must answer:

- What forced the decision?
- What was discarded and why?
- What does this decision require downstream?
- **What datum would make you reconsider it?** ← this is what makes the repo evolutionary

Update the index of `decisions/README.md` with the status.

### When finding an error

**Do not silence it by editing the text.** Fix it **and** add an entry to the [`CHANGELOG.md`](CHANGELOG.md) with a `C` number. Someone who read the previous version needs to know that it changed and why.

There are 18 corrections so far. Several are errors of the original analysis overturned by later data. **Documenting them is what allows trust in what remains standing.**

### When cancelling a decision

**Keep the file**, mark it ❌ and explain what it proposed, why it is cancelled and **under what conditions it would return**. Deleting it means that in six months someone will propose it again without knowing it was already studied. Example: [`ADR-0022`](decisions/ADR-0022-carbon-veil-cancelled.md).

### When writing calculations

**Every script carries a validation case against a known analytical solution, and must pass it before use.** This is not ceremony: error C17 (missing MAC normalization in the VLM) was exactly what that caught.

```bash
python3 calculations/vlm_ala_volante.py    # includes the contrast case
```

---

## Known failure modes

Documented because **they already happened in this project**. Read them before working.

### 1. Inverted order — the most frequent and the most expensive

Structure was sized **without defining loads** (n_max did not exist). Elevons were sized and their flutter and mass balancing were computed **without ever having computed the neutral point or the control authority**.

> **Before sizing anything, ask what loads it and what constrains it. If it is not defined, that is the task.**

### 2. False precision

Flutter frequencies were computed with three significant figures on a wing whose area was `[E]` ±13 %, whose airfoil did not exist and whose sweep was a 4° range.

> **The significant figures of the output cannot exceed those of the worst input.**

### 3. Failing to re-derive downstream

- **C6** — a 231 mm chord was carried over from an old table after the aspect ratio changed.
- **C16** — the stall speed requirement was derived with 1350 g and **was not re-derived** when the AUW rose to 1620 g. The requirement itself stopped being met with our own C_Lmax.

> **When a number changes upstream, look for everything that depended on it. It is the most repeated correction in the project.**

### 4. Unwarranted transfer

- **C7** — the Eliminator evidence at 360 km/h was taken as valid for PETG. It validated **its** material.
- **C12** — infill 0 % was specified, inherited from LW-PLA vase-mode practice, on a PETG shell.

> **An endorsement applies to the material, the scale and the regime in which it was obtained. Declare the transfer limit.**

### 5. Generalizing from a single calculated case

- **C11** — "carbon tubes do not work for torsion", concluded from a 10 mm tube. In thin wall `J ∝ D³`: at 18 mm the result reverses.

> **Before turning a calculation into a rule, look at what it depends on and to what power.**

### 6. Categorical claims without data

- **C9** — "PETG cannot be glued". Three solutions exist.
- **C14** — a structural risk was communicated with more certainty than `[E]` ±35 % data supported.

> **The tone must carry the confidence tag. An `[E]` is not communicated like an `[M]`.**

### 7. Ignoring hardware that flies

- **C15** — "a single perimeter fails the criterion". Falsified by an in-service example.

> **A flying article beats an `[E]` calculation. If the model contradicts real hardware, the model is the suspect.**

### 8. Tests that do not discriminate

- **C13** — calibrating the model against an article was proposed, but that article turned out to be at a factor ~3 from the limit. It neither falsified nor validated.

> **Before proposing a test, ask what result would make it fail. If there is none, it measures nothing.**

---

## Before proposing anything, verify

- [ ] What phase are we in, and does this belong to this phase?
- [ ] Is it blocked by any open gap?
- [ ] What confidence tag does every number I am writing carry?
- [ ] Does it contradict any active ADR? Any already-recorded correction?
- [ ] If I change a number, what depends on it downstream?
- [ ] Is there flying hardware that says otherwise?
- [ ] What document needs updating besides the one I am touching?

---

## Technical conventions

Full detail in [`docs/04-conventions.md`](docs/04-conventions.md).

| Prefix | Meaning |
|---|---|
| `ADR-XXXX` | Decision · `I-XX` Research · `GX` Gap |
| `EX` | Test · `OX` Objective · `R-XXX` Requirement · `CX` Correction |

**Signs:** sweep negative forward (the project uses ≈ −20°) · positive twist = wash-in (tip at higher incidence) · in `calculations/`, `x` positive backward with origin at the root c/4.

**Units:** SI in calculations. Tables may use km/h and g/dm², as they are the common units.

**Never use** a single Oswald factor for drag. Always separate the viscous term from the induced one — see [`ADR-0009`](decisions/README.md) and [`I-01`](research/I-01-aspect-ratio-reynolds.md). It is a definition artifact that already caused correction C1.

---

## Source quality

Order of preference: peer-reviewed → experimental databases (UIUC) → controlled test with declared method → manufacturer documentation → patents → own measurement on in-service articles.

**Source marked as unusable:** Grokipedia, for contradicting all primary sources consulted on forward-sweep divergence.

---

## What not to do

- **Do not invent figures** to fill a gap. A declared gap is worth more than a plausible number.
- **Do not erase history.** Not cancelled ADRs, not corrections, not results that came out wrong.
- **Do not skip phases.** If Phase 1 has no closed gate, no detail geometry is designed.
- **Do not optimize one parameter** while another is undefined. It is failure mode #1.
- **Do not take an XFOIL polar as good** at low Re without calibrating against measured data. It is `[D]`, never `[M]`.
- **Do not prescribe motor or battery.** The project designs the airframe and recommends — [`ADR-0033`](decisions/ADR-0033-electronics-out.md).
