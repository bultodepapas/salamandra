# Provisional fuselage geometry

This directory contains generated review geometry for the Salamandra Article #1
center body. It is **DRAFT — NOT FOR MANUFACTURE**.

The authority is the NumPy pipeline:

- `calculations/fuselage_contract.py` owns provisional family parameters and
  envelope ownership;
- `calculations/fuselage_geometry.py` generates and audits the analytical OML;
- `calculations/fuselage_trade.py` writes the deterministic artifacts under
  `provisional/`.

Reproduce from the repository root:

```bash
python calculations/fuselage_trade.py
python calculations/fuselage_trade.py --check
```

`provisional/oml-manifest.json` is ASCII-safe machine output. It records the
design vector, inflated-envelope margins, mesh metrics, convergence, battery
reachability and every open project blocker. `provisional/lifting-saddle-body.obj`
is a millimetre-unit review mesh generated from the same manifest.

The OBJ is an analytical body operand, not a wing-body Boolean union, printable
solid or structural shell. Its gross 0.9 mm skin estimate must not be added to
the aircraft mass ledger: overlap with the controlled center wing, cavities,
ribs, supports, hatches and local reinforcement remain unresolved. OP-21/F2,
native CAD, tolerances, print compensation and physical tests retain authority.
