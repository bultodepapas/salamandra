# Airfoil coordinates — provenance

Candidate and reference profiles for the Salamandra B3 screening
(consumed by `calculations/b3_screening.py`; results in `research/I-15` §6).

| File | Profile | t/c (as published) | Source | Retrieved |
|---|---|---|---|---|
| `e205.dat` | Eppler E205 | 10.6 % | UIUC Airfoil Data Site (`coord_seligFmt/e205.dat`) | 2026-08-05 |
| `s5010.dat` | Selig S5010 | 9.8 % | UIUC Airfoil Data Site (`coord_seligFmt/s5010.dat`) | 2026-08-05 |
| `mh60.dat` | Martin Hepperle MH60 | 10.1 % | aerodesign.de tailless-airfoil database (`/profile/mh60.txt`) | 2026-08-05 |
| `mh60-12.dat` | MH60 → 12 % t/c | 12.0 % | **Generated** by `b3_screening.py` (affine thickness scaling) | 2026-08-05 |
| `mh60-135.dat` | MH60 → 13.5 % t/c | 13.5 % | **Generated** by `b3_screening.py` (affine thickness scaling) | 2026-08-05 |
| `e205-9.dat` | E205 → 9 % t/c | 9.0 % | **Generated** by `b3_screening.py` (affine thickness scaling) | 2026-08-05 |

Notes:

- The generated variants implement the design guide's provisional scaling rule
  (§6.3): affine y-coordinate scaling (camber line unchanged). The screening
  quantifies why the tip must NOT be thinned this way without camber compensation
  (E205→9 % loses ≈ 0.1 clmax and 3–4° of stall angle — I-15 §6.2, `[D]`).
- UIUC coordinates are published for research use; aerodesign.de coordinates are
  published by the author (Hepperle) for use in design work. The database review
  lives in `research/I-11`.
- The measured E387 polar used for the XFOIL calibration (I-06) is downloaded at
  runtime by `calculations/calibra_xfoil_e387.py` and is **not** copied here.
- PW51 (Nemesis airfoil, I-08) is **not in the UIUC database** (404 confirmed
  2026-08-05); sourcing it remains open (I-15/A3).
