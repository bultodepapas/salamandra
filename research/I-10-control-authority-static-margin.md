# I-10 — Tailless pitch control authority and minimum static margin

**Status:** ⬜ **Open — proposed thread (not yet executed)**
**Feeds:** C6/S5 of the master plan (elevon authority — **never done before**, failure
mode #1), OP-01 (CG reachability), OP-06 (elevon span/travel), G8 (NP/SM verification)
**Gaps:** G8 · **Does not close:** G2

---

# 1. Question

What pitch control power (Cm_δ) can a tailless wing with ~28 % chord elevons achieve at
Re 3–5×10⁵, what is the resulting **minimum static margin** at which the elevons can trim
the whole envelope (including gust and extreme CG), and what margins do in-service
tailless FPV aircraft actually fly with?

# 2. Why it matters

The repo has **never computed elevon authority** (C6: "never done before"). It is the
task that corrects failure mode #1 (CLAUDE.md §1): control surfaces were sized and their
flutter/mass balance computed without the authority check. Two dependencies make it
urgent:

1. **OP-01 (critical):** with NP at −101 mm and the reachable CG band ≈ −24…+9 mm
   (v0.2 balance), **every reachable CG is aft of the NP** — i.e. statically unstable.
   The resolution paths (re-verified NP, mass redistribution, planform revision) all
   need a defensible SM floor: how much positive margin is actually *needed* once the CG
   is reachable? That number is C6's output.
2. **OP-06:** the ±20° travel and 390 mm span are assumptions; authority verification
   decides them.

# 3. What is already known in the repo `[D]`

- VLM NP = 26.7 % MAC, SM target 8 % (I-07).
- Elevon 0.28 c, span 30–90 % half-span, ±20°, dual actuation (guide §7.5).
- Twist yield 0.00338/° (I-07); the torsion window R-TWIST ≤ 2.5° bounds how much the
  elevon must contribute at the extreme CG.
- In-service trim data points: Peregrine INAV "level flight pitch 0→3°" `[M]` (I-02);
  Nemesis/Stormbird 1–2 mm of reflex `[M]` (I-08).

# 4. What to search

| Source | Expected contribution | Tag |
|---|---|---|
| XFOIL/VLM validation data on elevon effectiveness at low Re (panel codes, journal data on trailing-edge flap effectiveness Re 1–5×10⁵) | Magnitude of Cm_δ per degree at Re 3–5×10⁵, losses vs. potential-flow prediction | `[M]`/`[D]` |
| aerodesign.de — "Faszination Nurflügel" (Unverferth) summaries and plank articles (Siegmann's database pages) | Practice-based CG/SM ranges for tailless; warnings on cm0<0 sections and pitch-frequency problems (SB-13 "pilot shaker", EH series) | `[M]` |
| INAV / ArduPlane documentation and FPV forums (RCM, RCgroups threads on flying-wing CG) | In-service CG positions and SM of tailless FPV (Mojito, Peregrine, Nemesis); stabilized-flight minimum SM with pitch damping | `[M]`/`[I]` |
| Published tailless control-power data (NACA TN/NASA, e.g. swept-wing flap effectiveness; Horten-derived literature) | Analytical bounds for Cm_δ of a swept tailless with elevons | `[M]` |

# 5. Method

1. Extend the in-house VLM (`calculations/vlm_ala_volante.py`) with a control-surface
   model (deflected flap panels) and validate the flap-effectiveness prediction against
   at least one measured datum (search item 1).
2. Build the trim envelope: Cm_δ × δ_avail (minus authority reserve) vs. the torsion
   window of I-07 → feasible SM range.
3. Cross it with the in-service SM survey (items 2–3) → recommended SM floor and CG
   band for the OP-01 resolution.
4. Deliver the C6/S5 gate with a declared reserve policy (e.g. 50 % of travel kept).

# 6. Deliverable

- Cm_δ/deg `[D]`, validated; feasible SM band; recommended CG envelope for F2 (P3) and
  S5; recommended elevon travel and chord for the guide §7.5.

# 7. Transfer limits

- Flap effectiveness at Re 3–5×10⁵ suffers from separation and hysteresis that
  potential-flow methods miss; the XFOIL calibration band of I-06 applies, and in-flight
  E2 data remain the final arbiter.
- In-service SM figures from forums are `[M]`-grade practice but rarely measured with
  the precision the repo requires; treat as priors, not data.
- This thread bounds the *pitch* problem; lateral-directional (dihedral effect, roll
  authority) remains Phase 1's own task.
