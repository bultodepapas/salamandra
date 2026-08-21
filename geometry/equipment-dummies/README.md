# MP-04 equipment envelope dummies

`mp04-envelope-dummies.scad` is generated from the MP-03 manifest and I-33 propulsion
shortlist. Set its `PART` string, render in OpenSCAD and export the selected STL.

The shells reproduce only the stated external envelope and leave an open ballast cavity.
They do not include connector sweeps, cooling air, mounting tolerances or service access.
They are **not airworthy and must never be installed as flight hardware**.

Regenerate or verify with:

```bash
python3 calculations/generate_hardware_dummies.py --write
python3 calculations/generate_hardware_dummies.py --check
```

Ballast mass and its location are physical measurements. Record them under the relevant
H01–H22 specimen ID; do not assume a uniform-density shell has the real component's centre
of mass.
