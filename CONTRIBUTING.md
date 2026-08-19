# How to contribute

This is a **community-driven, open 3D-printed FPV aircraft platform**. Contributions of all
kinds are welcome — not only research and structures, but also parts, variants,
adapters and creative work.

The most valuable contributions raise the **confidence level** of the project: they turn
estimates into measurements and reasoning into parts that fly.

## Order of value

| Priority | Type | Example |
|---|---|---|
| **1** | **Measurements** | Convert an `[E]` or `[I]` into `[M]` with a published method |
| **2** | **Corrections** | A better source overturns an existing conclusion |
| **3** | **Replications** | Independent build with blackbox data |
| **4** | **Geometry & parts** | Wings, fuselages, wingtips, control surfaces, mounts, adapters — based on the research |
| **5** | **Creative & decorative** | Visual improvements, equipment mounts, and other modifications |

Everything is welcome. Parts do not need to be strictly aerodynamic or structural; the
platform explicitly accepts decorative parts, visual improvements, equipment mounts and
other creative modifications.

## The AI–human collaboration

Much of the aerodynamic and theoretical research is AI-assisted. The community brings the
3D parts (Fusion 360 / CAD), experimentation, manufacturing experience and engineering
intuition. You can contribute:

- **Research and analysis** — new studies, cross-validation, design exploration.
- **3D parts** — turning the AI-assisted research into reliable CAD/STL, using your own
  engineering knowledge, the research, or both.
- **New variants and configurations** — different wings, fuselages, control surfaces,
  propulsion layouts, and entirely new aircraft configurations beyond the flying wing.
- **Adapters and mounts** — for FPV equipment, electronics, propulsion systems and
  related hardware. This repository is the central archive for them.

## The confidence convention

Every quantitative claim in the technical record carries a tag:

| Tag | Meaning | Example |
|---|---|---|
| `[M]` | Measured and published by a primary source | "C_Lmax between 0.55 and 0.70 (Ananda et al. 2015)" |
| `[D]` | Derived by calculation from `[M]` | "Aerodynamic L/D ≈ 7.4, solved from flight data" |
| `[E]` | Estimated on declared assumptions | "Shell mass 550–650 g, by wetted area and mean thickness" |
| `[I]` | Reasoned inference, not verified | "Torsional stiffness governs divergence in this construction" |

Numbers without a source are not accepted in the technical record, even if correct.
Irreversible decisions supported by `[E]` or `[I]` must be explicitly declared.

## Contribution flow

1. **Open an issue** describing what you want to add or which gap (G) or decision (ADR) it
   touches.
2. **Work on the documents, parts, or both.** A part submitted without its reasoning is
   still welcome; a part with its reasoning is even better.
3. **Fill in the PR template.** It asks you to declare affected decisions and gaps, and the
   confidence level of any new datum.
4. **If you invalidate a previous claim, add an entry to the [CHANGELOG](CHANGELOG.md)**
   with a correction number C.

Maintainers packaging accepted work must use the
[New Release Guide](docs/15-how-to-publish-a-release.md). A release is a separate,
reviewed integration step; merging a contribution does not automatically release it.

## About corrections

**The correction register is part of the product, not a list of embarrassments.** The
current record runs through C34; several entries correct errors in earlier analysis after
better data or integration checks. Documenting them is what allows trust in what remains
standing.

If you find an error, **do not silence it by editing the text**: fix it and record it.

## Writing a new ADR

Copy [`decisions/TEMPLATE.md`](decisions/TEMPLATE.md). Sequential numbering. One decision
per file.

A good ADR answers: **what forced the decision? what was discarded and why? what does this
decision require downstream? what datum would make you reconsider it?**

## Writing a research thread

Copy the format of `research/I-0X`. A thread documents **what was searched, what was found,
with what sources, and what decisions it feeds** — not what was decided.

## Submitting parts and variants

- Provide the CAD/STL together with any build notes. State the configuration it was
  designed for (e.g. panel, fuselage, propulsion layout).
- If your part depends on a particular neutral point, CG or trim, reference the relevant
  ADR or research thread (e.g. [ADR-0032](decisions/ADR-0032-modularity.md)).
- Parts are welcome as "as-is" community offerings, but documenting the reasoning makes
  them far more useful to others.

## Test data

They must declare the **complete configuration**: pack, motor, propeller, takeoff mass,
material, perimeters, infill, firmware version. Without that they are not comparable across
builders.

## Source quality

Order of preference: peer-reviewed → experimental databases → controlled test with declared
method → manufacturer documentation → patents → own measurement.

**Source marked as unusable:** Grokipedia, for contradicting all primary sources consulted
on forward-sweep divergence.

## Licence

This is free and open hardware:

- **Hardware design and 3D models** (CAD/STL), geometry and the analysis/design scripts:
  **CERN-OHL-S-2.0** (see [`LICENSE`](LICENSE)).
- **Documentation**: **CC BY-SA 4.0** (see [`LICENSE-docs.md`](LICENSE-docs.md)).

By submitting a contribution you agree that it is released under these licences. Both are
reciprocal, so derivatives of the community's work stay open.
