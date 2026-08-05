# I-14 — Hand-launch and stall-margin practice for printed FPV wings

**Status:** ⬜ **Open — proposed thread (not yet executed)**
**Feeds:** O1 stall-speed requirement (≤ 45 km/h — the **tightest margin in the design**,
0.4 km/h), C16 review conditions, launch method (hand launch + autolaunch, docs/00),
D1/D2 (measurement chain validation platform)

---

# 1. Question

What is a realistic hand-launch velocity, how much stall margin do in-service FPV
aircraft actually operate with, and what does the INAV/ArduPlane autolaunch practice
require of the stall speed and thrust — for a 1620 g, 57 g/dm² tailless wing?

# 2. Why it matters

The stall requirement was relaxed to ≤ 45 km/h (C16) and the design sits at **44.6 km/h
at CL_max 0.60 — a 0.4 km/h margin**, the tightest in the whole design (I-07 §4.2). The
launch is a mandatory hand throw (docs/00) with autolaunch via acceleration detection.
If the achievable launch speed is below stall, the aircraft cannot leave the hand — the
requirement chain (CL_max ≥ 0.65, R-AIRFOIL, wing loading) is only as strong as the
launch number. No project datum quantifies any of this.

# 3. What is already known in the repo

- Stall ≈ 44.6 km/h at CL_max 0.60; wing C_Lmax 0.589 required (I-07 §4.2).
- C_Lmax measured band for low-Re sections: 0.55–0.70 `[M]` (I-01, Ananda et al.).
- In-service practice: Peregrine 840 mm hand-launched, wing loading 50–60 g/dm²
  `[M]` (docs/02); Flightory Stallion: "grab under the wings, throw at a slight AoA,
  confident motion" `[M]` (I-09); Mojito hand-launched pusher `[M]` (docs/02).
- Autolaunch: INAV acceleration detection required (docs/00 §3.5).

# 4. What to search

| Source | Expected contribution |
|---|---|
| Human throwing performance for RC aircraft (biomechanics/RC practice studies and forum measurements) | Achievable hand-launch speed band for a 1.6 kg wing (typical 8–12 m/s); relationship with weight and grip |
| INAV and ArduPlane autolaunch documentation (official wikis) | Launch conditions: throttle settings, detection thresholds, minimum airspeed logic; how stall speed and CG position interact with autolaunch success |
| In-service FPV wing documentation (Peregrine, Mojito, Nemesis, Stormbird, Flightory family) | Published stall speeds, launch techniques, and the actual margins flown (many fly with stall margins far below 1.5×) |
| FPV community data (blackbox logs shared publicly; forum threads on launch failures) | Real-world launch failure modes: stall on throw, torque roll, CG-induced pitch-up |

# 5. Method

1. Establish the launch-speed band from the throwing data + in-service launch footage
   measurements where possible.
2. Establish the in-service stall-margin practice (cruise/stall ratio) for the
   reference set.
3. Extract the autolaunch requirements from the INAV/ArduPlane documentation.
4. Deliver: launch-speed requirement for the Salamandra, a recommended stall-margin
   policy for the O1 chain (keep ≤ 45 km/h / relax further / require CL_max ≥ 0.65),
   and autolaunch configuration guidance for D1/D2 validation.

# 6. Deliverable

- Declared launch envelope (speed, technique, CG position) for the guide §4/§12 and
  docs/00; recommendation on the stall-speed requirement with the data behind it;
  autolaunch settings for the D2 validation platform.

# 7. Transfer limits

- Throw-speed data are mostly amateur measurements (`[I]`-grade unless published
  studies are found); the band must be declared with its spread.
- In-service stall margins are rarely measured (published cruise speeds vs. estimated
  stalls) — treat as practice priors, not data (the same discipline as I-08/I-09).
- Autolaunch behavior is specific to firmware versions; the thread must pin the version
  (INAV 9.1+, per docs/00).
