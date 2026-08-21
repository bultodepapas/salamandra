# E2A results — printed section lift, drag and moment

**Status:** OPEN — no physical measurements have been supplied.

The empty raw-data template is intentional. XFOIL rows are stored under
`calculations/trim_redesign_out/` and must never be copied here with
`source=measured`.

The current computational disposition is:

- r1 at 8% nominal static margin fails at least one 45 km/h/CG-band corner;
- r2a at 5% nominal static margin screens all 30 speed/Ncrit/CG cases inside
  11.04 deg of symmetric elevon;
- only 8/30 r2a cases have a trim root bracketed by converged deflected
  polars; 22/30 use a boundary control-slope extrapolation;
- therefore neither airfoil family has measured trim, stall or drag closure.

Populate `raw/section_polars.csv`, reduce repeat sweeps with the procedure in
the test README, then run the measured-data evaluation. This file must be
replaced with uncertainty-bearing tables and the signed acceptance disposition
before ADR-0047 can become active. A passing trim subgate alone does not close
E2A.
