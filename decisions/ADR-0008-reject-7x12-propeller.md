# ADR-0008 — Reject the 7×12 propeller

**Status:** ✅ Active · **Date:** 2026-07-27 · **Confidence:** High · **Reversible:** Yes
**Research:** [I-03 — Propulsion chain](../research/I-03-propulsion-chain.md), first_investigation §5.3 (D8)

**Article #1 redesign:** `RETAINED-METHOD` · **Gate:** `M4` · [MP-02 ledger](REDESIGN-DISPOSITION.md)

## Context

The reference competitor (TBS Mojito) uses a 7×12 propeller. Its pitch/diameter is
**1.71**; the maximum P/D in UIUC propeller data vol. 1 is ≈ 1.25, and that case did not
even reach its efficiency peak within the measured range (first_investigation §5.3). The
7×12 operates **outside all published data**.

## Decision

**Reject the 7×12 propeller as reference**, unless experimentally validated. The
reference band stays P/D 0.8–1.0 matched by advance ratio at cruise ([ADR-0007](ADR-0007-propeller.md));
alternatives in the matching table: APC-E 9×6, 10×7 (guide §9.1).

## Rationale

Efficiency claims require data. No efficiency datum exists for P/D 1.71 in the UIUC
database; extrapolating the parabolic-polar behaviour is exactly the failure mode the
repo's confidence convention exists to prevent.

## Consequences

- No efficiency claim is made on the Mojito's propeller (its measured 1.40 Wh/km `[M]`
  is an *aircraft* datum, not a propeller datum).
- The experimental gate is **E3** (propeller-matching sweep): any propeller outside the
  data envelope can be re-admitted only with a measured polar (D8 wording).
