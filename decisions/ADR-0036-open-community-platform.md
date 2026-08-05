# ADR-0036 — Community-driven open aircraft platform

**Status:** ✅ Active · **Date:** 2026-08-05 · **Confidence:** Decided · **Reversible:** No
**Related decisions:** ADR-0032 (modularity), ADR-0037 (licence)

## Context

The project had been framed as a single forward-swept flying-wing design. In reality its
value is larger and more durable: an **open, community-driven 3D-printed aircraft platform**
whose core design principles are developed largely through **AI-assisted research**, while
the final aircraft and its 3D models are created collaboratively by humans and AI.

Two facts drove this decision:

1. **AI is strong at research, weak at CAD.** AI is effective at aerodynamic analysis,
   theoretical research, data cross-validation, design exploration and trade studies — but
   today it is still not reliable at directly creating parametric Fusion 360 models or
   native CAD files. The community must create the actual 3D parts, using the research,
   their own engineering knowledge, or both.
2. **Community value comes from extension.** A single, finished design is a static
   artifact. A modular platform that accepts new wings, fuselages, control surfaces,
   mounts and complete new configurations keeps evolving and keeps its contributors.

## Alternatives considered

| Option | For | Against | Why discarded |
|---|---|---|---|
| Keep a single closed design | Simpler, self-contained | Static; no community growth; hides the reasoning | Against the project's founding principle ("no decision without declared rationale") |
| Closed-source platform | Captures the design value | Contradicts the goal of being free and community-driven | Discarded |
| **Open, AI-assisted, community platform** | Reasoning as product; continuous evolution; broad contribution base; free and reciprocal | Requires coordination and clear roles | **Adopted** |

## Decision

**The repository is an open, community-driven, modular 3D-printed FPV aircraft platform.** AI
performs the aerodynamic/theoretical research and design exploration; the community creates
the 3D parts, experiments and manufacturing know-how. The platform is free, encourages pull
requests, and is not limited to the current forward-swept flying wing.

## Rationale

- **Reasoning as the product.** Every decision carries its rationale, source and confidence
  level; the repository remains the archive of *why*.
- **Complementary strengths.** AI scales the analysis and exploration; humans provide
  experimentation, practical judgment, manufacturing experience and engineering intuition.
- **Broad contributions.** Parts do not need to be aerodynamic or structural. Decorative
  parts, visual improvements, equipment mounts, adapters and creative modifications are
  welcome — and this repository is the central archive for adapters and mounts for FPV
  equipment, electronics and propulsion.
- **Extensibility.** Replaceable wings, fuselage variants, different wingtips, alternative
  rudders and control surfaces, and entirely different aircraft configurations (conventional
  fuselages, V-tails, tractor or pusher layouts) are all in scope over time.

## Consequences

- The README, CONTRIBUTING, specification and agent documentation now describe this
  positioning.
- Modularity requirements (ADR-0032) apply to every new configuration contributed to the
  platform, so the common-neutral-point discipline is preserved.
- A licence that keeps the community's work open is required → **ADR-0037**.

## Review conditions

Reconsidered only if the community contribution model fails in practice (e.g. no external
contributions over a sustained period), which would be reviewed rather than reversed.
