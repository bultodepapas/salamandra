# ADR-0037 — Licence: CERN-OHL-S v2 + CC BY-SA 4.0

**Status:** ✅ Active · **Date:** 2026-08-05 · **Confidence:** Decided · **Reversible:** Yes
**Related decisions:** ADR-0036 (open community platform)

## Context

The project is free and as open as possible to the community. It mixes three kinds of
material that are usually licensed differently:

1. **Hardware design and 3D models** (CAD/STL) and the geometry/design data.
2. **Analysis and design scripts** (`calculations/*.py`).
3. **Documentation** (the `.md` files).

The licence must keep the community's work open (reciprocal) while being practical to use
and to contribute to.

## Alternatives considered

| Option | For | Against | Why discarded |
|---|---|---|---|
| No licence / "all rights reserved" | None | Contradicts the whole purpose | Discarded |
| **Permissive hardware licence** (CERN-OHL-P / Solderpad) | Maximum reuse, even closed | Allows closed derivatives of community work | Discarded — weaker protection of the platform |
| **Strongly reciprocal hardware licence** (CERN-OHL-S) + CC BY-SA docs | Derivatives and products of the community's work stay open; strong fit for a community platform | Less permissive for closed commercial reuse | **Adopted** |
| Single licence for everything | Simpler | Poor fit: hardware and documentation have different conventions | Discarded |

## Decision

- **Hardware design and 3D models** (CAD/STL), geometry and the analysis/design scripts:
  **CERN Open Hardware Licence Version 2 — Strongly Reciprocal** (SPDX `CERN-OHL-S-2.0`).
- **Documentation** (the `.md` files): **Creative Commons Attribution-ShareAlike 4.0**
  (SPDX `CC-BY-SA-4.0`).

The full licence text is in `LICENSE`; the documentation licence and scope are described in
`LICENSE-docs.md`.

## Rationale

- **Reciprocal, by design.** The project chose the copyleft philosophy: both licences
  require derivatives to be shared under the same terms, so every contribution benefits the
  whole community and cannot be enclosed.
- **Fits the hardware/documentation split.** CERN-OHL-S is the standard strongly-reciprocal
  licence for open-source hardware; CC BY-SA is the standard for documentation.
- **Aligns with ADR-0036.** An open, community-driven platform is best protected by licences
  that keep its work open.

## Consequences

- Contributors agree, by submitting, that their work is released under these licences
  (stated in `CONTRIBUTING.md`).
- Any product or derivative made from the design must make the Complete Source available
  (per CERN-OHL-S §4).
- Documentation reuse requires attribution and share-alike (per CC BY-SA 4.0).

## Review conditions

Reconsidered only if the strong copyleft proves to be a real barrier to community adoption;
a move to a permissive variant would then be evaluated against the risk of enclosing the
community's work.
