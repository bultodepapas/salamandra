# I-03 — Propulsion chain

**Status:** Closed · **Feeds:** ADR-0007, ADR-0008, and the project's **objective O1**

> **v0.3 clarification:** this thread established the value of propeller matching but
> did not solve the aircraft operating point. ADR-0042/I-22 correct the former use of
> peak propeller efficiency as a commanded cruise point.

## Why this thread is the most important in the project

The range equation decomposes into three independent multiplicative factors:

    R = (E_sp/g · m_bat/m_total) · η_total · (L/D)
        ────────────────────────    ───────    ─────
              energy              propulsion  aerodynamics

**Doubling any of the three doubles the range. None compensates the deficiency of another.**

Of the three, the propulsive one has the **immediate and demonstrable recoverable margin**. It is the basis of the project's central claim.

## The finding that defines the objective

### TBS Mojito cross-validation `[D]`

| Source | Energy | Distance | Wh/km |
|---|---|---|---|
| Waldner (measured) | 68.1 Wh (8S 2300 mAh LiPo) | 50 km | **1.36** |
| TBS (declared) | 144.0 Wh (8S1P 5000 mAh Li-Ion) | 100 km | **1.44** |

**Agreement within 5 %.** **1.40 Wh/km** is adopted as the reference.

### Specific-energy comparison `[D]`

| Platform | Wh/km | Mass | **Wh/(km·kg)** | Speed |
|---|---|---|---|---|
| Sonicmodell AR Wing 1000 | 0.78 `[E]` | 1.0 kg | **0.78** | ~55 km/h |
| **TBS Mojito** | 1.40 `[D]` | 1.9 kg | **0.74** | 100–150 km/h |
| Mini Talon | 1.20 `[M]` | 1.3 kg | **0.92** | 50 km/h |
| Solar Impulse 2 | 160 `[D]` | 2300 kg | **0.070** | 70 km/h |

> **The Mojito is not more efficient, it is faster.** It consumes the same energy per kilometer and kilogram as a USD 40 foam wing. Its achievement is not lowering specific consumption: it is **sustaining it at two or three times the speed**.

### L/D solved from real flight `[D]`

    (L/D)_aero = (1/η) · (L/D)_effective

| Platform | Effective L/D | Assumed η | **Aerodynamic L/D** |
|---|---|---|---|
| TBS Mojito | 3.7 | 0.50 `[E]` | **7.4** |
| AR Wing | 3.5 | 0.50 `[E]` | 7.0 |
| Solar Impulse 2 | 39.2 | 0.80 `[E]` | 49 |

The Mojito L/D in fast cruise is **≈ 7.4**, far below its maximum L/D.

## Primary propeller data

**Brandt & Selig, AIAA 2011-1255** — 79 propellers, 9–11 in, Re 50–100×10³ at 75 % blade:

- Peak efficiency between **0.65 (good) and 0.28 (bad)** — factor 2.3 `[M]`
- Efficiency **systematically improves as rpm rises**, via the Reynolds effect `[M]`
- Extreme case: the Master Airscrew G/F 11×4 **nearly doubles** its peak efficiency over the tested rpm range `[M]`
- Hobby propellers give **7.5–15 % less** than 36 in propellers with similar P/D `[M]`
- Very thin blades can enter **flutter** at high J `[M]`

**Own extraction from the UIUC database `[D]`** — see [ADR-0007](../decisions/ADR-0007-propeller.md) for the full table.

## The quantified gap

| Component | Range |
|---|---|
| Propeller at its optimal J | 0.65 – 0.73 |
| Well-sized motor + ESC | ≈ 0.85 |
| **Theoretical product** | **0.55 – 0.62** |
| **Real value solved from flight** | **≈ 0.50** |

The gap indicates that **the propeller does not operate at its optimal advance ratio**.

> **Recoverable margin: moving from 0.50 to 0.60 is +20 % range without modifying the aerodynamics.**

From there comes objective O1: **≤ 1.15 Wh/km** versus the Mojito's 1.40. An 18 % improvement justifiable **only with the propulsion chain**.

## Concrete case: the Mojito 7×12 propeller

Its P/D is **1.71**. The maximum of the UIUC vol. 1 database is around 1.25, and that case did not even reach its peak within the measured range. **It lacks data support** → ADR-0008.

## How it is verified

- **E3** — matching sweep: stabilized flight at fixed speed logging current, 3–4 diameter/pitch combinations, against the J predicted by UIUC.
- **E2** — glide polar: the only instrument that **separates propulsive losses from aerodynamic losses**.

## Sources

1. Brandt, J. B. & Selig, M. S. — *Propeller Performance Data at Low Reynolds Numbers*. AIAA 2011-1255.
2. UIUC Propeller Database, vols. 1–4.
3. Team BlackSheep — TBS Mojito datasheet and manual rev. 2025-11-04.
4. Waldner, N. — TBS Mojito test report, 3.5 months.
