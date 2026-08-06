# Decision record (ADR)

One decision, one file. Each ADR declares **context, alternatives considered, decision, consequences and confidence**.

## States

| State | Meaning |
|---|---|
| ✅ **Active** | In force |
| 🔄 **Provisional** | In force but supported by `[E]`/`[I]`; reviewed when the associated gap closes |
| ⬜ **Superseded** | Replaced by another ADR |
| ❌ **Cancelled** | Withdrawn without replacement |
| ⚠️ **Under dispute** | No data to resolve |

---

## Index

| # | Decision | State | Confidence | Reversible |
|---|---|---|---|---|
| [0001](ADR-0001-inverted-sweep.md) | Forward-swept flying wing | ✅ | High | No |
| [0002](ADR-0002-closed-shell.md) | Closed three-cell shell structure | ✅ | Medium `[I]` | No |
| 0003 | Wash-in type twist | 🔄 | High | Partial |
| [0004](ADR-0004-aspect-ratio.md) | Aspect ratio 6.0 | 🔄 | Medium `[E]` | No |
| 0005 | Reflexed and thin airfoil | ⬜ | — | — |
| 0006 | Single pusher motor preferred | ⚠️ | Low `[I]` | Yes |
| [0007](ADR-0007-propeller.md) | Propeller P/D 0.8–1.0 matched by J | ✅ | High | Yes |
| 0008 | Reject the 7×12 propeller | ✅ | High | Yes |
| 0009 | Separate drag decomposition; never a single Oswald | ✅ | High | No |
| [0010](ADR-0010-mission-branch.md) | Branch A — fast cruise | ✅ | Decided | No |
| 0012 | Light color mandatory | ✅ | High | Yes |
| [0015](ADR-0015-carbon-non-torsional.md) | Carbon as bending and pin, not torsion | ✅ | High `[D]` | Yes |
| 0016 | Reject PLA+ | ✅ | High `[M]` | — |
| 0018 | Reject ABS due to UV degradation | ✅ | High `[M]` | — |
| [0021](ADR-0021-base-material.md) | PETG as the base material | ✅ | High | Partial |
| [0022](ADR-0022-carbon-veil-cancelled.md) | Carbon veil ±45° | ❌ **Cancelled** | — | — |
| 0023 | Joints: tenon + PETG adhesive, area ≥ 3× | 🔄 | Medium | Yes |
| 0024 | 3 segments per wing half, 45° on bed | ✅ | High | Yes |
| [0025](ADR-0025-elevon-balancing.md) | Elevon mass balancing | ✅ | High | No |
| 0026 | No-freeplay linkage, dual actuation | ✅ | High | Yes |
| [0027](ADR-0027-relative-thickness.md) | t/c 13.5 % root / 9 % tip | ✅ | High `[M]` | No |
| [0028](ADR-0028-gyroid-infill.md) | Gyroid 5 % infill | ✅ | Medium `[M]` | Yes |
| 0030 | Plastic path as base; torsion tube option B | 🔄 | Medium | Yes |
| 0031 | Carbon pin in the joints | ✅ | High | Yes |
| [0032](ADR-0032-modularity.md) | Modular CORE + PANEL architecture | ✅ | High | No |
| [0033](ADR-0033-electronics-out.md) | Motor and battery out of the design | ✅ | Decided | — |
| 0034 | Motor mount angle as a design parameter | 🔄 | Medium | Yes |
| 0035 | TPU-printed hinges | 🔄 | Medium | Yes |
| [0036](ADR-0036-open-community-platform.md) | Open, community-driven aircraft platform (AI-assisted research) | ✅ | Decided | No |
| [0037](ADR-0037-licence.md) | Licence: CERN-OHL-S-2.0 + CC BY-SA 4.0 | ✅ | Decided | Yes |
| [0038](ADR-0038-fixed-fin-variant.md) | Dual directional config: finless baseline + fixed-fin variant V1 (no rudder) | 🔄 | Medium `[D]`/`[E]` | Yes |

### Superseded or cancelled

| # | Reason |
|---|---|
| 0005 | Replaced by [0027](ADR-0027-relative-thickness.md). The airfoil moved from "thin" to 13.5 % |
| 0011, 0013, 0014, 0017, 0019, 0020 | Replaced by [0021](ADR-0021-base-material.md) after evaluating five materials |
| 0022 | **Cancelled** by project decision — see [ADR-0022](ADR-0022-carbon-veil-cancelled.md) |
| 0029 | Absorbed into [0002](ADR-0002-closed-shell.md) |

> **0015 was corrected, not cancelled.** The original version claimed that carbon tubes add no torsion. See correction C11 in the [CHANGELOG](../CHANGELOG.md).
