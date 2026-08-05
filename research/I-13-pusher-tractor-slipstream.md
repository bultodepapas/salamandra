# I-13 — Propeller slipstream: pusher vs tractor at Re 3–5×10⁵

**Status:** ⬜ **Open — proposed thread (not yet executed)**
**Feeds:** G5 (propeller wash on a thin airfoil at Re 4×10⁵), **disputed ADR-0006**
(single pusher vs twin tractor), OP-14, propulsion chain (I-03 review)
**Closes:** G5 with the comparative in-flight test; this thread bounds the dispute before it

---

# 1. Question

What does the literature say about the drag/lift effect of a propeller slipstream on a
thin wing at Re 3–5×10⁵ — and specifically, how does a **pusher** installation compare
with a **tractor** one for a tailless FPV configuration like the Salamandra?

# 2. Why it matters

ADR-0006 (single pusher) is **under dispute, low confidence `[I]`**, and G5 is open: no
datum quantifies how the slipstream interacts with a thin reflexed airfoil at the
project's Reynolds number. The decision affects the OML (pusher = clean wing, rear
motor pod; tractor = twin nacelles, prop wash over the center section) — and the v0.2
guide's whole propulsion section rests on it.

# 3. What is already known in the repo

- ADR-0006 rationale: blade Re, clean wing, single-motor simplicity — `[I]`, disputed.
- I-08 quasi-controlled comparison: Nemesis (twin tractor) vs. Stormbird (single
  pusher) — **confounded** by airfoil (PW51↔PW75) and size; cannot isolate the
  slipstream effect (I-08 §4).
- I-03 (propulsion chain) and ADR-0007 (propeller matching) define the J/η framework.
- Flightory reference set (I-09): both aircraft are **tractor** — evidence of the
  family's practice, not of pusher behavior.
- Mojito (docs/02) is a pusher FSW — the only in-service pusher-FSW datum `[M]`.

# 4. What to search

| Source | Expected contribution |
|---|---|
| Tractor-vs-pusher wind-tunnel studies at low Re (UAV propulsive configurations; e.g. NASA/AGARD pusher-configuration reports, and low-Re prop-wing interaction papers) | Magnitude of the slipstream-induced drag/lift changes at Re 1–5×10⁵; pusher installation penalties (pylon, nacelle, wake impingement) |
| Propeller-wing interaction at low Re (e.g. UIUC propeller tests combined with wing polars; papers on "slipstream effect on wing at low Reynolds") | How much the washed region's C_Lmax and C_D0 change — the input to the G5 question (thin airfoil, Re 4×10⁵) |
| In-service FPV data: Mojito (pusher FSW, docs/02), TBS Caipirinha/Caipirinha v2 (pusher wings), Z-84/X-UAV (pusher), Flightory tractors (I-09) | Practice-based comparisons of pusher vs tractor efficiency and handling in the same size class |
| INAV/ArduPilot forum data on pusher trim, thrust-line coupling, and autolaunch behavior of pusher wings | Operational consequences (pitch coupling under power — relevant to the z = 0 thrust line, guide §10.2) |

# 5. Method

1. Systematic literature sweep (tractor/pusher at low Re), extract comparable
   efficiencies and installation penalties.
2. Reduce to the Salamandra case: single pusher at the CORE rear, prop disk at
   x ≈ +235 behind the root TE (guide §10.2) — the slipstream does **not** wash the
   wing (unlike a tractor or a mid-wing pusher); quantify what is actually affected
   (CORE rear pod, elevon inner section at high deflection, wake behind).
3. Compare with the twin-tractor alternative using the same propeller data.
4. Deliver the bounded statement for ADR-0006 (or the explicit trigger to reopen it)
   and the G5 pre-test bounds; the comparative flight test remains the closer.

# 6. Deliverable

- Bounds on the slipstream effect for the pusher layout `[D]`/`[M]`, a documented
  comparison table pusher vs twin tractor, and a recommendation for the ADR-0006 status
  (keep / reopen / plan the comparative test) — feeding OP-14 and the guide §10.

# 7. Transfer limits

- Most low-Re propeller studies use tractor or isolated-propeller setups; direct pusher
  data at Re 4×10⁵ are scarce — expect `[I]`-grade transfers with declared ranges.
- The in-service comparisons are not controlled experiments (I-08 discipline applies).
- The slipstream wake behind the Salamandra's prop affects the **elevons only at large
  deflections** (inner end at y = 195, 0.28 c); high-frequency effects (flutter
  coupling, G7) are outside this thread.
