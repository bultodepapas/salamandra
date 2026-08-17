# I-14 — Hand-launch and stall-margin practice for printed FPV wings

**Status:** ✅ **Executed 2026-08-06 (rev. 2 — verdict corrected)** · **Feeds:** O1
stall-speed requirement (≤ 45 km/h), C16 review, launch method (docs/00), D1/D2
autolaunch configuration
**Tool:** `calculations/launch_speed.py` (9 validation cases, ALL PASS)

> **Correction record (2026-08-06):** rev. 1 concluded "infeasible" by demanding
> k_safe = 1.20 at the release instant and using a low idle-thrust estimate. Rev. 2
> corrects both: (a) the release gate is V_suelta ≥ V_stall — the margin is built by
> motor acceleration in the first 0.2–0.4 s (T/W ≈ 1.0 → 10 m/s²); (b) the throw
> gesture (0.4–0.6 s) runs with the motor at wing-throw idle (0.5–0.67 × hover),
> adding 2–4 m/s. The configuration-class anchor (TBS Mojito, `[M]`) confirms:
> heavier and higher-stall than the Salamandra, hand-launched in service.

---

# 1. Question

What is a realistic hand-launch velocity, how much stall margin do in-service FPV
aircraft actually operate with, and what does the INAV/ArduPlane autolaunch practice
require of the stall speed and thrust — for a 1685 g, 59.8 g/dm² tailless wing?

# 2. Why it matters

The stall requirement was relaxed to ≤ 45 km/h (C16) and the design sits at **45.9 km/h
(1685 g, `mass_budget.py`) — above the requirement** (OP-24 lever to F2). The launch is a
mandatory hand throw (docs/00) with autolaunch via acceleration detection. If the
achievable launch speed is below stall, the aircraft cannot leave the hand. This thread
was opened with **zero project data**; it now closes with the quantitative envelope.

# 3. Findings

## 3.1 Human throw velocity — published biomechanics + community

- **Published (van den Tillaar, JSSM 2004):** 0.409 kg ball → 21.5 m/s; 0.206–0.818 kg
  balls show a **significant negative linear mass–velocity relationship**.
  Extrapolation to a 1.6–1.7 kg overhead/two-hand push throw: **typical 8–12,
  strong 10–13 m/s** (community estimate for 2+ kg aircraft: 8–10 m/s, r/RCPlanes).
  DLG 20–25 m/s figures are NOT transferable (200 g, discus spin technique).
- **Configuration-class anchor `[M]` (decisive):** the **TBS Mojito — 1300 mm,
  ≈ 1800 g, pusher, community-reported stall ≈ 60 km/h (16.7 m/s)** — is
  **hand-launched in service** (TBS manual, community launches with INAV idle 1300 +
  launch 1850, over-head techniques; bungee hook documented as an option). Heavier
  and higher-stall than the Salamandra, it launches by hand: the Salamandra at
  12.8 m/s stall is a strictly easier case.
- In-service failure reports exist on record (Mojito "a few throwing failures" on the
  first day, Chupito autolaunch roll, ZOHD Dart XL "difficult and dangerous to
  launch") — launch is the documented weak moment of this aircraft class, but the
  class as a whole launches by hand routinely.
- **Torque-roll threshold `[I]`:** community-documented risk at T/W ≳ 1.5 with low
  launch speed (700 g at 1.7:1 documented as problematic; 2.1 kg at 0.75:1 works).
  The Salamandra launch T/W ≈ 0.9–1.1 is inside the safe band.

## 3.2 INAV autolaunch — official guide (Hoffmann, iNavFlight/inav docs `[D]`)

| Setting | Default | Salamandra recommendation | Basis |
|---|---|---|---|
| `nav_fw_launch_thr` | 1700 | **Hover throttle: T/W ≈ 1.0 → ≈ 16.5 N** (bench: nose-up, throttle until "about to fly out of your hand") | guide: hover rule; the 8×8 static band 15–20 N at 6S `[D]` |
| `nav_fw_launch_idle_thr` | 1000 | **0.5–0.67 × launch (≈ 8.3–11.1 N)** — extra push during the throw | guide Scenario 3 (wing throws): 1350–1450 for launch 1700 |
| `nav_fw_launch_motor_delay` | 500 ms | **200 ms** — pusher: never 0 (prop past the hand) | guide: smaller planes lose speed fast; 200 ms recommended |
| `nav_fw_launch_accel` | 1863 (1.8 G) | keep (heavy-wing throw still exceeds it) | guide: default OK |
| `nav_fw_launch_detect_time` | 40 ms | keep | guide |
| `nav_fw_launch_climb_angle` | 18° | 18–25° | guide: 25–30° recommended, but keep ≤ hover thrust |
| `nav_fw_launch_spinup_time` | 100 ms | **200 ms** (8-inch prop) | guide: 8–10 in props → 200 ms+ |

Guide warnings relevant to Salamandra: **"you will need to do a perfect throw in the
right angle and with good speed"**; wing throws "not recommended because Autolaunch
could flip it and crash into ground with full throttle"; **launch thrust should never
exceed hover** (backward G-forces confuse the FC climb detection).

## 3.3 ArduPlane hand launch — official docs `[D]`

- `TKOFF_THR_MINACC` ≈ **15 m/s²** (1.5 G) — matches INAV's 1.8 G.
- `TKOFF_THR_DELAY` ≥ **0.2 s** (motor past the hand).
- `TKOFF_THR_MINSPD` = 4 m/s ground speed (GPS) as an extra gate.
- **"The vehicle leaves your hand at zero to 5° pitch. Higher pitches could lead to a
  stall."** — the launch attitude is a declared envelope limit, not a preference.
- Motor start blocked if pitch > 40° or roll > 30° (safety gates).

# 4. Quantified envelope (`launch_speed.py`)

| Quantity | Value |
|---|---:|
| V_stall (1685 g, ALL PETG) | **45.9 km/h** (12.8 m/s) |
| **Release gate (rev. 2):** V_suelta ≥ V_stall | **PASS for typical and firm throws** |
| V_suelta, typical throw 10.5 m/s + ref idle | **13.4 m/s (48.4 km/h) — k = 1.05 at release; k = 1.20 reached in 0.39 s** |
| V_suelta, firm throw 13 m/s + high idle | **17.3 m/s (62.4 km/h) — k = 1.36 at release** |
| V_suelta, weak throw 8 m/s + low idle | 9.8 m/s (35.2 km/h) — **below stall: technique is part of the specification** |
| Time to k = 1.20 after release (typical, incl. 0.2 s motor delay) | 0.39 s |
| Launch T/W (hover rule) | 0.9–1.1 — inside the 1.5 torque-roll threshold |

**Verdict (rev. 2): HAND LAUNCH IS FEASIBLE** with a firm throw (V_hand ≥ 10 m/s) +
high idle throttle (`nav_fw_launch_idle_thr` 1350–1450) + launch throttle at the hover
setting (T/W ≈ 1.0). The margin is not at the release instant — it is built by the
motor acceleration in the first 0.4 s. Corroborated by the configuration-class anchor
`[M]` (Mojito 1800 g / ~60 km/h reported stall, hand-launched). The V1 fin (ADR-0038)
remains recommended for the test programme (directional stability in the first
seconds, finless yaw divergence τ ≈ 0.7 s).

**Levers (unchanged, now for comfort not feasibility):** (a) mass reduction to the
OP-24 low end; (b) CL_max raise via the designed airfoil (R-AIRFOIL, OP-02) — lowers
V_stall and raises the release margin; (c) bungee/launch dolly as an option for the
instrumented test programme; (d) accept the declared technique rule (firm throw).

# 5. Deliverables

1. **Declared launch envelope** (guide §4/§12, this document):
   - **Release gate: V_suelta ≥ V_stall** (45.9 km/h at 1685 g) with the elevon-up
     launch attitude; margin k = 1.20 reached by acceleration in < 0.5 s.
   - **Technique rule: firm throw (V_hand ≥ 10 m/s), release at 0–5° pitch
     (ArduPilot guidance; higher → stall), launch throttle at the hover setting.**
   - Autolaunch configuration table (§3.2) for D1/D2 validation.
2. **Stall-margin policy (C16 chain):** the ≤ 45 km/h requirement stands and is
   **not reachable at the current budget** (45.9 km/h); F2 must arbitrate mass vs stall
   (OP-24). The launch analysis (rev. 2) no longer blocks the first flight — it
   prescribes the technique. The CL_max chain (R-AIRFOIL, designed section, OP-02)
   remains double-critical for COMFORT: it lowers V_stall AND raises the release
   margin.
3. **Autolaunch settings for D2** (the validation platform must first fly with the §3.2
   table; the launch failures of in-service wings — Mojito, AR Wing Mini — are the
   documented baseline of what a wrong setup looks like).

# 6. Method note

The release model is deliberately simple: V_suelta = V_hand + (T_idle/m)·t_gesture,
with the bands declared. It is a gate check, not a trajectory model. Rev. 1's error is
documented in the correction record above: requiring k_safe at the release instant is
too strict because the motor (T/W ≈ 1.0 at launch throttle) builds the margin in
0.2–0.4 s; the correct gate is V_suelta ≥ V_stall. The trajectory (pitch dynamics on
release, sink rate) is a first-flight measurement, not a calculation input: the
envelope says when the launch is *allowed*, blackbox data (E-series) will say how it
*behaves*.

# 7. Transfer limits

- The 8–13 m/s throw band is extrapolated from published biomechanics (van den
  Tillaar 2004) with community practice — declared `[D]`-ish with spread; the DLG
  20–25 m/s numbers are not transferable (200 g, discus technique).
- The Mojito anchor transfers the CONFIGURATION CLASS (1300 mm pusher FSW,
  hand-launched at ≥ Salamandra stall), not its exact numbers (stall reported by the
  community, likely optimistic — the same caution as the Peregrine 35 km/h).
- In-service stall margins are community estimates, not measured polars.
- Autolaunch behavior is firmware-specific: the table pins INAV 9.x per docs/00; D2
  must validate on the bench + first flights.
- The 0.4 s margin time is `[D]` on the declared bands; it is the quantity to measure
  first (blackbox launch log).
