# How to contribute

This project accepts contributions that **raise the confidence level of a datum**.

## Order of value

| Priority | Type | Example |
|---|---|---|
| **1** | **Measurements** | Convert an `[E]` or `[I]` into `[M]` with a published method |
| **2** | **Corrections** | A better source overturns an existing conclusion |
| **3** | **Replications** | Independent build with blackbox data |
| **4** | **Geometry** | Only after Phase 1 is closed |

## What is not accepted

**Numbers without a source, even if correct.** This is not bureaucratic rigidity: the value of this repository is that anyone can trace where each number comes from. An orphan figure that is correct today is an unverifiable figure tomorrow.

Irreversible decisions supported by `[E]` or `[I]` without explicitly declaring it are also not accepted.

## The confidence convention

| Tag | Meaning | Example |
|---|---|---|
| `[M]` | Measured and published by a primary source | "C_Lmax between 0.55 and 0.70 (Ananda et al. 2015)" |
| `[D]` | Derived by calculation from `[M]` | "Aerodynamic L/D ≈ 7.4, solved from flight data" |
| `[E]` | Estimated on declared assumptions | "Shell mass 550–650 g, by wetted area and mean thickness" |
| `[I]` | Reasoned inference, not verified | "Torsional stiffness governs divergence in this construction" |

## Contribution flow

1. **Open an issue** describing which gap (G) or decision (ADR) it touches.
2. **Work on the documents**, not only on the code or geometry.
3. **Fill in the PR template.** It asks you to declare affected decisions and gaps, and the confidence level of the new datum.
4. **If you invalidate a previous claim, add an entry to the [CHANGELOG](CHANGELOG.md)** with a correction number C.

## About corrections

**The correction register is part of the product, not a list of embarrassments.** There are 21, several of them errors of the original analysis corrected by later data. Documenting them is what allows trust in what remains standing.

If you find an error, **do not silence it by editing the text**: fix it and record it. Someone who read the previous version needs to know that it changed and why.

## Writing a new ADR

Copy [`decisions/TEMPLATE.md`](decisions/TEMPLATE.md). Sequential numbering. One decision per file.

A good ADR answers: **what forced the decision? what was discarded and why? what does this decision require downstream? what datum would make you reconsider it?**

## Writing a research thread

Copy the format of `research/I-0X`. A thread documents **what was searched, what was found, with what sources, and what decisions it feeds** — not what was decided.

## Test data

They must declare the **complete configuration**: pack, motor, propeller, takeoff mass, material, perimeters, infill, firmware version. Without that they are not comparable across builders.

## Source quality

Order of preference: peer-reviewed → experimental databases → controlled test with declared method → manufacturer documentation → patents → own measurement.

**Source marked as unusable:** Grokipedia, for contradicting all primary sources consulted on forward-sweep divergence.
