# I-32 — 6S1P/8S1P P42A pack geometry and aircraft trade

**Status:** Quantitative screening complete; no pack layout or 8S power module released ·
**Feeds:** I-16, I-31, OP-01/21/23/24, future propulsion and fuselage ADRs

> **Decision boundary.** This thread calculates the alternatives. It does not freeze a
> bay, outer mould line, motor, ESC or 8S variant. All pack and bay dimensions remain
> pre-CAD sizing values. A manufactured pack, cable bend, retention system and extraction
> path must still be measured in F2.

## 1. Question and direct result

The design question is whether Salamandra should retain its 6S1P Molicel P42A pack or
adopt/also accommodate an 8S1P pack, and which physical 21700 arrangements make each
choice credible.

The reproducible result is:

- **6S1P:** **445 ± 5 g**, 21.6 V nominal / 25.2 V full, **4.2 Ah**, 90.72 Wh by
  `V_nom Q`, and 93.0/88.2 Wh manufacturer typical/minimum energy `[D]` on `[M]/[E]`.
- **8S1P:** **585 ± 5 g**, 28.8 V nominal / 33.6 V full, **4.2 Ah**, 120.96 Wh by
  `V_nom Q`, and 124.0/117.6 Wh manufacturer typical/minimum energy `[D]` on `[M]/[E]`.
- The eight-cell pack adds **140 g and 33.3 % energy**, moves its required mass centre
  **62.2 mm aft**, but raises CLEAN stall speed from **44.06 to 46.00 km/h**. It therefore
  fails the current 45 km/h requirement by **72.9 g of CLEAN mass**.
- A common **flat and narrow** pack union is possible, but its rail is approximately
  **340.5 × 44.0 × 22.6 mm** before cross-axis clearance and walls. A common flat bay can
  be shortened to **246.7 mm** if pack width grows to **70.8 mm**, or to **235.2 mm** at
  **87.4 mm** pack width.
- The current Article #1 power system is **not 8S-compatible as a released system**:
  the guide specifies a 6S ESC, the selected SpeedyBee board is officially labelled
  2–6S despite a contradictory 36 V numerical input line, and the motor/propeller has no
  8S D2 map.

These numbers keep **6S as the lower-risk Article #1 baseline**. They do not reject a
future 8S variant; they define the mass reduction, packaging and electrical work needed
to make it real.

## 2. Reproduction and evidence convention

Run:

```bash
python3 calculations/battery_6s_8s_trade.py
```

The script enumerates all **18** rectangular six-cell layouts and all **20** rectangular
eight-cell layouts, derives pack/electrical values, solves the current aggregate CG model,
propagates mass into stall and the estimated cruise polar, and checks five representative
common bays.

Evidence labels follow repository policy:

- `[M]`: manufacturer or measured source;
- `[D]`: direct calculation from declared inputs;
- `[E]`: explicit engineering estimate pending measurement.

The current estimated drag polar is not E2 evidence. Its power values are sensitivity
results, not measured performance predictions.

## 3. Cell and pack inputs

The current [Molicel P42A product page](https://www.molicel.com/product/inr-21700-p42a/)
and [v4 product data sheet](https://www.molicel.com/wp-content/uploads/INR21700P42A-V4-80092.pdf)
give the controlled cell values.

| Quantity | Value | Authority |
|---|---:|---|
| Maximum sleeved cell dimensions | **70.2 × Ø21.7 mm** | P42A v4 `[M]` |
| Maximum cell mass | **70 g** | P42A v4 `[M]` |
| Typical / minimum capacity | **4.2 / 4.0 Ah** | P42A v4 `[M]` |
| Nominal / full / discharge-cutoff voltage | **3.6 / 4.2 / 2.5 V** | P42A v4 `[M]` |
| Typical / minimum cell energy | **15.5 / 14.7 Wh** | P42A v4 `[M]` |
| Arithmetic nominal energy | `3.6 × 4.2 =` **15.12 Wh** | `[D]` |
| Continuous discharge current | **45 A** | P42A v4 `[M]` |
| DC impedance, 10 A / 1 s | **16 mΩ** | P42A v4 `[M]` |

The manufacturer energy rating is not exactly `V_nom × Q_typ`; both are retained so the
calculation does not silently replace published data. Conservative mission accounting
should eventually use a measured usable-energy curve at the actual cutoff, temperature
and current.

### 3.1 Pack-level installation estimates

| Allowance | Value | Authority |
|---|---:|---|
| Outer wrap | **0.3 mm each side** | I-16 `[E]` |
| Nickel stack on height | **0.3 mm** | I-16 `[E]` |
| Folded main/balance-lead projection | **12 mm on the aft end** | I-16 `[E]` |
| Pack hardware mass | **25 ± 5 g** | I-16 `[E]`; 8S unmeasured |
| Pack-centre travel | **±10 mm** | user requirement interpreted symmetrically `[E]` |
| Cross-axis installation clearance | **2 mm total** | screening minimum `[E]`, before walls |

The 12 mm cable envelope and ±10 mm travel are separate. The former contains the folded
lead; the latter preserves adjustment in both directions because the sign of a real CG
error is unknown.

### 3.2 Correction to the former capacity tables

In a series-only pack,

\[
V_\mathrm{pack}=N_sV_\mathrm{cell},\qquad
E_\mathrm{pack}=N_sE_\mathrm{cell},\qquad
Q_\mathrm{pack}=Q_\mathrm{cell}.
\]

The previous I-16 output incorrectly printed `N_s Q_cell`, giving 25.2 Ah for 6S1P.
That was wrong. Both P42A packs are **4.2 Ah**; voltage and Wh increase with series count.
I-16 and its calculator are corrected under C53.

## 4. Pack-level electrical comparison

| Quantity | 6S1P | 8S1P | 8S / 6S |
|---|---:|---:|---:|
| Installed design mass | **445 ± 5 g** | **585 ± 5 g** | 1.315 |
| Nominal / full voltage | 21.6 / 25.2 V | 28.8 / 33.6 V | 1.333 |
| Typical capacity | **4.2 Ah** | **4.2 Ah** | 1.000 |
| Arithmetic nominal energy | **90.72 Wh** | **120.96 Wh** | 1.333 |
| Data-sheet typical / minimum energy | 93.0 / 88.2 Wh | 124.0 / 117.6 Wh | 1.333 |
| Current at the 109.25 W O1 ceiling | **5.06 A** | **3.79 A** | 0.750 |
| P42A pack DC resistance proxy | 96 mΩ | 128 mΩ | 1.333 |
| `I²R` cell heat at 109.25 W | **2.46 W** | **1.84 W** | 0.750 |
| DC sag proxy at 109.25 W | 0.486 V | 0.486 V | 1.000 |
| Ideal duration at 109.25 W, arithmetic Wh | 49.8 min | 66.4 min | 1.333 |
| Ideal range at the 1.15 Wh/km limit | 78.9 km | 105.2 km | 1.333 |

The lower 8S current reduces the P42A cell-loss proxy by **25 % at equal aircraft power**.
It does not prove a 25 % propulsion-efficiency gain: motor iron/switching losses, partial-
throttle ESC behaviour, propeller loading and aerodynamic drag remain outside that simple
pack-resistance calculation.

## 5. Practical pack shapes

Dimensions below use maximum cells and the complete I-16 pack allowance. `L × W × H`
always follows the aircraft axes. Arrangement `A` places cell axes along pack length;
`B` places them along pack width.

### 5.1 Engineering shortlist

| Pack | Arrangement | Layers | Envelope L × W × H (mm) | What it buys | Primary penalty |
|---|---|---:|---:|---|---|
| 6S | **3×2×1-A** | 1 | **223.2 × 44.0 × 22.6** | Flat, narrow, smallest useful frontal floor | Long |
| 6S | **2×3×1-A** | 1 | **153.0 × 65.7 × 22.6** | Flat, compact length | 49 % more pack frontal area than 3×2 |
| 6S | **6×1×1-B** | 1 | **142.8 × 70.8 × 22.6** | Shorter flat pack | Wider |
| 6S | **1×3×2-A** | 2 | **82.8 × 65.7 × 44.3** | Very short footprint | Twice the height |
| 8S | **4×2×1-A** | 1 | **293.4 × 44.0 × 22.6** | Same narrow/flat section as long 6S | Very long |
| 8S | **8×1×1-B** | 1 | **186.2 × 70.8 × 22.6** | Moderate-length flat pack | 61 % more frontal floor than 4×2 |
| 8S | **2×4×1-A** | 1 | **153.0 × 87.4 × 22.6** | Short flat pack | Wide body floor |
| 8S | **2×2×2-A** | 2 | **153.0 × 44.0 × 44.3** | Narrow and much shorter | Twice the height |
| 8S | **4×1×2-B** | 2 | **99.4 × 70.8 × 44.3** | Compact footprint | Wider and taller |

The user preference for a flat fuselage does **not** uniquely imply a long pack. All
`n_z=1` options are 22.6 mm high. The trade is length against width and the OML needed to
recover from that cross-section.

### 5.2 Common bay alternatives

The CG solver places the pack mass centres at `x_6S = −353.7 mm` and
`x_8S = −291.5 mm`. The rail union below includes the asymmetric aft lead and ±10 mm
centre travel for each configuration. Width and height are pack envelopes before bay wall;
the final column adds only the provisional 2 mm total installation clearance.

| Case | 6S / 8S arrangements | Rail L (mm) | Pack W × H (mm) | Minimum inner W × H (mm) |
|---|---|---:|---:|---:|
| **Flat narrow** | 3×2×1-A / 4×2×1-A | **340.5** | **44.0 × 22.6** | **46.0 × 24.6** |
| **Flat moderate** | 6×1×1-B / 8×1×1-B | **246.7** | **70.8 × 22.6** | **72.8 × 24.6** |
| **Flat short/wide** | 2×3×1-A / 2×4×1-A | **235.2** | **87.4 × 22.6** | **89.4 × 24.6** |
| Hybrid narrow | 3×2×1-A / 2×2×2-A | 270.3 | 44.0 × 44.3 | 46.0 × 46.3 |
| Stacked compact | 1×3×2-A / 2×2×2-A | 200.1 | 65.7 × 44.3 | 67.7 × 46.3 |

For a strictly flat common bay, widening the pack union from 44.0 to 70.8 mm saves
**93.8 mm of rail** without increasing pack height. Whether that helps the aircraft
depends on the complete body: the wider pack floor increases its rectangular frontal-area
proxy from 994 to 1,600 mm², while the shorter rail can reduce wetted area, forward
side-area arm and structural span. I-31 shows why neither scalar alone selects the OML.

### 5.3 Transfer check against the TBS Mojito

The official [TBS Mojito product page](https://www.team-blacksheep.com/products/prod%3Atbs_mojito_kit)
publishes a **230 × 70 × 50 mm** maximum battery envelope and identifies 8S1P 5000 mAh
Li-ion as ideal. Applied only as a packaging comparator:

- the 223.2 × 44.0 × 22.6 mm Salamandra long 6S fits physically but leaves only
  **6.8 mm total length**, less than the requested ±10 mm travel;
- the 293.4 mm long flat 8S does not fit;
- the 153.0 × 44.0 × 44.3 mm stacked 8S does fit its published bounding box.

This supports the earlier inference that Mojito obtains compact 8S packaging by using
height. It does not prove the pack's internal orientation or transfer its CG solution to
Salamandra.

## 6. Mass, stall, balance and agility consequences

The comparison holds the current non-battery airframe fixed. CLEAN mass is the released
1,553.25 g less the 445 g 6S pack; V1 adds the current 48.73 g twin-fin lower model.

| Case | AUW | Wing loading | Stall speed | 45 km/h gate | Pack x |
|---|---:|---:|---:|---:|---:|
| 6S CLEAN | **1,553.25 g** | 55.08 g/dm² | **44.06 km/h** | PASS | −353.7 mm |
| 6S V1 | **1,601.98 g** | 56.81 g/dm² | **44.74 km/h** | PASS | −353.7 mm |
| 8S CLEAN | **1,693.25 g** | 60.04 g/dm² | **46.00 km/h** | **FAIL** | −291.5 mm |
| 8S V1 | **1,741.98 g** | 61.77 g/dm² | **46.66 km/h** | **FAIL** | −291.5 mm |

The current 45 km/h analytical mass ceiling is **1,620.40 g**. At unchanged wing area
and `CLmax=0.589`, an 8S build must therefore remove at least:

- **72.9 g** from CLEAN; or
- **121.6 g** from V1.

Without mass reduction, closing 45 km/h would instead require CLEAN `CLmax=0.6155` or
`S=0.2947 m²`, both **4.50 %** above the current contract. V1 needs 7.50 % more. These are
design changes, not free margins.

The heavier pack does not automatically increase pitch inertia because its balance
station moves aft toward the aircraft CG. The rectangular-envelope pack contribution to
`Iyy` is **0.03192 kg·m²** for the long flat 6S and **0.02708 kg·m²** for the long flat
8S, 15.2 % lower. This is only the pack contribution; the higher AUW still reduces linear
acceleration for a given force and raises stall/landing speed. Whole-aircraft inertia must
be re-derived after the fuselage and equipment stations are real.

## 7. Cruise-energy sensitivity

At 95 km/h the current estimated clean polar gives:

| Case | `CL` | Estimated drag | Estimated total energy |
|---|---:|---:|---:|
| 6S CLEAN | 0.1267 | 1.756 N | 0.999 Wh/km |
| 8S CLEAN | 0.1381 | 1.779 N | 1.009 Wh/km |
| 6S V1 | 0.1307 | 1.764 N | 1.003 Wh/km |
| 8S V1 | 0.1421 | 1.788 N | 1.012 Wh/km |

On this model, the 140 g mass increment raises CLEAN energy per kilometre by only
**0.93 %** at 95 km/h because profile drag dominates at the low cruise `CL`. This is an
`[E]` sensitivity, not a flight claim. The different fuselage length/width/height required
by each pack is absent from the polar and can plausibly dominate the 0.023 N mass-induced
drag increment. E2 must test the selected OML; E3 must measure Wh/km.

## 8. Propulsion and avionics compatibility

The current APC E 8×8 O1 boundary is 8,484 rpm. At a declared 80 % loaded/no-load ratio:

| Pack | Matching point | Existing 500–550 Kv boundary fraction | 550 Kv no-load rpm at full charge |
|---|---:|---:|---:|
| 6S | **491 Kv** | 71–79 % | 13,860 rpm |
| 8S | **368 Kv** | 54–59 % | **18,480 rpm** |

APC's [Thin Electric limit](https://www.apcprop.com/wp-content/uploads/2022/03/APC-Propeller-RPM-Limits-rev5.pdf)
is 18,750 rpm for an 8-inch propeller. A 550 Kv motor on fully charged 8S therefore has
only **1.5 % no-load arithmetic margin** before motor Kv tolerance, overspeed transients
and measurement uncertainty. That combination cannot be released from arithmetic alone.
Scaling the current 500–550 Kv band by `6/8` gives an 8S starting band of approximately
**375–413 Kv**, still requiring a D2 motor/ESC/propeller map.

The electrical-system gate is more immediate:

- the concise guide specifies a **6S, 30 A ESC**;
- the [SpeedyBee F405 WING APP official page](https://www.speedybee.com/speedybee-f405-wing-app-fixed-wing-flight-controller/)
  prints `7–36 V` but explicitly labels the input **2–6S LiPo**. Because those two
  statements conflict, 8S is a FAIL unless the manufacturer supplies written approval or
  the PDB is replaced;
- TBS makes Mojito 8S-capable with a purpose-matched system: its official
  [electronics package](https://www.team-blacksheep.com/products/prod%3Atbs_mojito_electroni)
  uses a 3–12S ESC and a motor advertised for 6–8S. That is evidence for architecture,
  not evidence that Salamandra's current components tolerate 8S.

An 8S Salamandra is therefore a **separate power module**, not a battery-only swap.

## 9. Complete maximum-dimension layout catalog

Every row is physically constructible as a rectangular array, but series-link routing,
insulation, cell polarity, fusing, retention and extraction are not solved. Very wide or
tall rows are retained because the user requested the complete option space.

### 9.1 6S1P — 18 arrangements

| Layout | Layers | Envelope L × W × H (mm) | Frontal floor W×H (mm²) |
|---|---:|---:|---:|
| 1×6×1-B | 1 | 34.3 × 421.8 × 22.6 | 9,533 |
| 2×3×1-B | 1 | 56.0 × 211.2 × 22.6 | 4,773 |
| 3×2×1-B | 1 | 77.7 × 141.0 × 22.6 | 3,187 |
| 1×6×1-A | 1 | 82.8 × 130.8 × 22.6 | 2,956 |
| **6×1×1-B** | **1** | **142.8 × 70.8 × 22.6** | **1,600** |
| **2×3×1-A** | **1** | **153.0 × 65.7 × 22.6** | **1,485** |
| **3×2×1-A** | **1** | **223.2 × 44.0 × 22.6** | **994** |
| 6×1×1-A | 1 | 433.8 × 22.3 × 22.6 | 504 |
| 1×3×2-B | 2 | 34.3 × 211.2 × 44.3 | 9,356 |
| 3×1×2-B | 2 | 77.7 × 70.8 × 44.3 | 3,136 |
| **1×3×2-A** | **2** | **82.8 × 65.7 × 44.3** | **2,911** |
| 3×1×2-A | 2 | 223.2 × 22.3 × 44.3 | 988 |
| 1×2×3-B | 3 | 34.3 × 141.0 × 66.0 | 9,306 |
| 2×1×3-B | 3 | 56.0 × 70.8 × 66.0 | 4,673 |
| 1×2×3-A | 3 | 82.8 × 44.0 × 66.0 | 2,904 |
| 2×1×3-A | 3 | 153.0 × 22.3 × 66.0 | 1,472 |
| 1×1×6-B | 6 | 34.3 × 70.8 × 131.1 | 9,282 |
| 1×1×6-A | 6 | 82.8 × 22.3 × 131.1 | 2,924 |

### 9.2 8S1P — 20 arrangements

| Layout | Layers | Envelope L × W × H (mm) | Frontal floor W×H (mm²) |
|---|---:|---:|---:|
| 1×8×1-B | 1 | 34.3 × 562.2 × 22.6 | 12,706 |
| 2×4×1-B | 1 | 56.0 × 281.4 × 22.6 | 6,360 |
| 1×8×1-A | 1 | 82.8 × 174.2 × 22.6 | 3,937 |
| 4×2×1-B | 1 | 99.4 × 141.0 × 22.6 | 3,187 |
| **2×4×1-A** | **1** | **153.0 × 87.4 × 22.6** | **1,975** |
| **8×1×1-B** | **1** | **186.2 × 70.8 × 22.6** | **1,600** |
| **4×2×1-A** | **1** | **293.4 × 44.0 × 22.6** | **994** |
| 8×1×1-A | 1 | 574.2 × 22.3 × 22.6 | 504 |
| 1×4×2-B | 2 | 34.3 × 281.4 × 44.3 | 12,466 |
| 2×2×2-B | 2 | 56.0 × 141.0 × 44.3 | 6,246 |
| 1×4×2-A | 2 | 82.8 × 87.4 × 44.3 | 3,872 |
| **4×1×2-B** | **2** | **99.4 × 70.8 × 44.3** | **3,136** |
| **2×2×2-A** | **2** | **153.0 × 44.0 × 44.3** | **1,949** |
| 4×1×2-A | 2 | 293.4 × 22.3 × 44.3 | 988 |
| 1×2×4-B | 4 | 34.3 × 141.0 × 87.7 | 12,366 |
| 2×1×4-B | 4 | 56.0 × 70.8 × 87.7 | 6,209 |
| 1×2×4-A | 4 | 82.8 × 44.0 × 87.7 | 3,859 |
| 2×1×4-A | 4 | 153.0 × 22.3 × 87.7 | 1,956 |
| 1×1×8-B | 8 | 34.3 × 70.8 × 174.5 | 12,355 |
| 1×1×8-A | 8 | 82.8 × 22.3 × 174.5 | 3,891 |

## 10. Interpretation and next gates

### 10.1 What the numbers say now

1. **For Article #1, retain 6S.** It closes the current stall requirement and matches the
   released propulsion/avionics voltage architecture.
2. **If both packs must remain geometrically possible while preserving one-cell height,**
   the 70.8 mm-wide flat pair deserves explicit OML study. It saves 93.8 mm of common rail
   relative to the narrow pair, with no height increase.
3. **Do not release 8S as a swap option.** It needs at least 72.9 g CLEAN mass reduction,
   an 8S-qualified PDB/ESC/BEC chain, a lower-Kv starting point and a new D2 map.
4. **Do not infer aircraft drag from the pack rectangle.** The 44, 70.8 and 87.4 mm widths
   are packaging floors; local wing-body integration and the aft recovery determine the
   actual OML drag.

### 10.2 Repair/closure plan

| Gate | Required evidence | Failure condition |
|---|---|---|
| F2-PACK | Build one representative 6S and one 8S pack; measure mass, CG-relative envelope, cable bend, connector and extraction sweep | Any measured envelope exceeds the model or hardware mass falls outside ±5 g |
| F2-BAY | CAD the flat-narrow and flat-moderate body sections with walls, straps, crash retention and access | No continuous load path or no tool-free safe extraction |
| E2-OML | Compare complete-body drag, not isolated rectangular frontal area | Wider/shorter candidate does not recover the rail-length benefit in total drag |
| F2-MASS | Produce an 8S mass ledger | CLEAN >1,620.40 g at the current wing/CLmax |
| D2-8S | Bench an 8S-rated ESC/BEC/PDB, candidate motor and APC E 8×8 over voltage/current/rpm/temperature | Prop limit, component voltage, temperature or O1 power boundary violated |
| E3 | Fly Wh/km and thermal tests at 95 km/h after E2/D2 | O1 >1.15 Wh/km or unsafe temperature/voltage sag |

## 11. Primary sources and transfer limits

1. Molicel — [INR-21700-P42A product page](https://www.molicel.com/product/inr-21700-p42a/)
   and [v4 product data sheet](https://www.molicel.com/wp-content/uploads/INR21700P42A-V4-80092.pdf):
   cell dimensions, mass, voltage, capacity, energy, current and impedance `[M]`.
2. APC Propellers — [Propeller RPM Limits, rev. 5](https://www.apcprop.com/wp-content/uploads/2022/03/APC-Propeller-RPM-Limits-rev5.pdf):
   Thin Electric 150,000/diameter-inch limit `[M]`.
3. SpeedyBee — [F405 WING APP product page](https://www.speedybee.com/speedybee-f405-wing-app-fixed-wing-flight-controller/):
   the manufacturer-controlled but internally conflicting `7–36 V` / `2–6S` input line
   `[M]`; treated as 6S-only until clarified.
4. Team BlackSheep — [Mojito product page](https://www.team-blacksheep.com/products/prod%3Atbs_mojito_kit),
   [manual](https://www.team-blacksheep.com/media/files/tbs-mojito-manual.pdf) and
   [electronics package](https://www.team-blacksheep.com/products/prod%3Atbs_mojito_electroni):
   external reference for a 230 × 70 × 50 mm bay and purpose-built 6–8S/12S power chain.
   No unpublished Mojito pack orientation, CG or aerodynamic coefficient is transferred.

