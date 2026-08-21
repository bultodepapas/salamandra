# MP-04 hardware characterisation

This directory owns physical evidence for Master Plan H01–H22. The repository currently
contains only `measurement-template.json`; every gate is intentionally `pending`.

Create a separate completed record, preserve specimen IDs, instrument calibration and raw
evidence paths, then validate it with:

```bash
python3 calculations/hardware_measurements.py --record tests/MP04-hardware-characterisation/<record>.json
python3 calculations/hardware_measurements.py --record tests/MP04-hardware-characterisation/<record>.json --require-closure
```

The second command shall fail until all 22 gates are accepted. Never replace a missing
physical value with a catalog value merely to make the record pass.

Recommended subdirectories for a real campaign are `instruments/`, `photos/`, `raw/` and
`reduced/`. Raw files are immutable evidence; reductions must name their generating script.
