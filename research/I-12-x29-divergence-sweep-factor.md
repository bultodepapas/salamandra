# I-12 — Forward-sweep divergence: X-29 flight data and sweep-factor bounds

**Status:** ⬜ **Open — proposed thread; primary sources located**
**Feeds:** G6 (sweep factor — **declared weakest link**), G4 (torsional stiffness bounds), S4 of the master plan, ADR-0001 review conditions
**Closes:** G6 with E7 (flight data); this thread bounds the `[E]` factor before that

---

# 1. Question

What did the X-29 program actually measure about forward-swept divergence — and can its
flight data, combined with published divergence theory and printed-shell torsion data,
tighten the 0.50–0.70 sweep factor currently used in the project's divergence scaling
law?

# 2. Why it matters

The divergence calculation (I-05) uses a reduction factor of **0.50–0.70** for −20° of
sweep, taken from generic literature and **not computed on this section's EI/GJ ratio**
(G6 in `gaps/`). It is the term that dominates the `[E]` ±35 % uncertainty. The X-29 is
the only flight program in history with forward-swept divergence/flutter monitoring —
its flight envelope expansion data are exactly the missing reference.

# 3. Primary sources located (verified accessible)

| Source | Content | Status |
|---|---|---|
| **NASA-TM-86025** — Putnam, T. W., "X-29 flight-research program" (NASA Ames, 1984; also AIAA 2nd Flight Test Conf.) | Methods for monitoring **wing divergence, flutter and aeroservoelastic coupling** during envelope expansion; flight data examples | NTRS, fulltext PDF available `[M]` |
| **AIAA PAPER 83-2687** — Putnam, "X-29 flight research program" (1983) | Same subject, conference version | NTRS, metadata only `[M]` |

# 4. What to search next

| Source | Expected contribution |
|---|---|
| NASA NTRS: X-29A divergence/flutter follow-on reports (Grumman aeroelastic tailoring reports; NASA TM series 1985–1990) | Measured/estimated divergence margin vs. untailored prediction; the famous result that the X-29 flew well above the untailored divergence speed thanks to aeroelastic tailoring |
| Forward-swept divergence theory (Diederich, Krone; AGARD reports on forward-swept wings) | Proper sweep-factor formulation as a function of the real EI/GJ ratio and sweep angle — replacing the generic 0.50–0.70 |
| CNC Kitchen and additive-manufacturing literature: torsional stiffness of printed thin-wall shells (gyroid-reinforced) | Bounds for the printed PETG GJ term (G4) — the second `[E]` in the divergence chain |
| X-29 flight-envelope reports (NASA Dryden, TF-1044 series) | Flight-validated divergence behavior of a *tailored* FSW — transferable method, not magnitude (different scale, material, tailoring) |

# 5. Method

1. Pull NASA-TM-86025 + follow-ons; extract the divergence monitoring method and any
   quantitative divergence-margin data.
2. Re-derive the sweep factor for the project's geometry (sweep −20°, real section
   EI/GJ from S3) using the theory sources; compare with the 0.50–0.70 band.
3. Bound the printed-shell GJ with the additive literature + the Peregrine anchor
   (docs/02) — reduces the second `[E]` term.
4. Deliver the updated divergence speed band for S4; E7 (Southwell plot in flight)
   remains the closing measurement.

# 6. Deliverable

- Sweep-factor bounds `[D]` computed on the real section (or a declared reason why the
  generic band must stay), GJ band for the printed shell, and a documented X-29
  reference for the E7 method. Input to S4 and the V_div criterion (≥ 1.5 × V_NE).

# 7. Transfer limits

- The X-29 was a tailored carbon/metal fighter at transonic speeds: its **divergence
  margins do not transfer numerically** to a 1300 mm printed PETG model. It transfers
  the **method** (how divergence is monitored and extrapolated) and the **physics**
  (the feedback mechanism, the wash-in coupling documented in I-02/I-05).
- NASA-TM-86025 is a program-overview paper; the definitive X-29 divergence numbers may
  be spread across several reports — the thread must assemble them, not cite one.
- Printed-shell torsion literature spans many materials/infill patterns; only
  low-density (3–5 %) gyroid data with declared wall counts are comparable to
  ADR-0028.
