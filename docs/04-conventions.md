# Conventions and nomenclature

## Confidence tags

| Tag | Meaning |
|---|---|
| `[M]` | Measured and published by a primary source |
| `[D]` | Derived by calculation from `[M]` data |
| `[E]` | Estimated on declared assumptions |
| `[I]` | Reasoned inference, not verified |

**Hard rule:** no `[E]` or `[I]` datum supports an irreversible decision without prior verification.

## Identifiers

| Prefix | Meaning | Lives in |
|---|---|---|
| `ADR-XXXX` | Design decision | `decisions/` |
| `I-XX` | Research thread | `research/` |
| `GX` | Data gap | `gaps/` |
| `EX` | Test | `tests/` |
| `OX` | Objective | `docs/00-...` |
| `R-XXX` | Derived requirement | `docs/00-...` |
| `CX` | Recorded correction | `CHANGELOG.md` |
| `FX` | Project phase | `docs/` |

## Symbols

| Symbol | Quantity | Unit |
|---|---|---|
| b | Wingspan | m |
| S | Wing area | m² |
| AR | Aspect ratio, b²/S | — |
| c | Chord | m |
| c̄ | Mean aerodynamic chord | m |
| t/c, h/c | Relative thickness | % |
| ε | Geometric twist (positive wash-in) | ° |
| Λ | c/4 sweep (negative = forward) | ° |
| q | Dynamic pressure | Pa |
| GJ | Torsional stiffness | N·m² |
| EI | Bending stiffness | N·m² |
| J | Torsion constant / propeller advance ratio | m⁴ / — |
| e_i | Non-viscous span efficiency | — |
| e_v | Oswald factor (**not to use alone** — see I-01) | — |
| η | Propulsive efficiency | — |
| V_div | Divergence speed | km/h |
| ω_h, ω_α, ω_β | Bending, torsion, elevon frequencies | Hz |

## Sign conventions

- **Sweep:** negative forward. This project uses Λ ≈ −20°.
- **Twist:** positive wash-in (tip at higher incidence). This project uses wash-in.
- **Load factor:** positive upward.

## Units

SI in calculations. In presentation tables, km/h for speed and g/dm² for wing loading are allowed, as they are the common units in the field.

## Writing conventions

- Every quantitative figure carries a confidence tag the first time it appears in a document.
- Ranges are written `a–b`, not `a-b`.
- Important warnings go with ⚠️ and explain **the consequence**, not just the fact.
- Corrections **are not silenced by editing**: fix the text and record it in the CHANGELOG.
