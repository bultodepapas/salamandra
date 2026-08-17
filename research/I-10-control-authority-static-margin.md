# I-10 — Tailless pitch control authority and minimum static margin

**Status:** 🔄 **Partial — potential-flow authority executed; measured validation and
full envelope remain open**
**Feeds:** C6/S5 of the master plan, OP-01 (CG reachability), OP-06 (elevon span/travel),
G8 (NP/SM verification)
**Gaps:** G8 · **Does not close:** G2

---

# 1. Question

What pitch control power (Cm_δ) can a tailless wing with ~28 % chord elevons achieve at
Re 3–5×10⁵, what is the resulting **minimum static margin** at which the elevons can trim
the whole envelope (including gust and extreme CG), and what margins do in-service
tailless FPV aircraft actually fly with?

# 2. Why it matters

The repo now computes potential-flow elevon authority in `elevon_authority.py`, but it
has not validated flap effectiveness against low-Re measurements or closed the
gust/extreme-CG envelope. Two dependencies keep the thread open:

1. **OP-01:** ADR-0040 now gives NP −75.8 mm and target CG −93.8 mm; the 6S1P pack closes
   that point. The remaining question is the defensible SM floor and usable CG envelope,
   not basic reachability.
2. **OP-06:** the ±20° travel and 390 mm span are assumptions; authority verification
   decides them.

# 3. What is already known in the repo `[D]`

- VLM NP = 25.72 % MAC / −75.8 mm, SM target 8 % (I-21/ADR-0040).
- Elevon 0.28 c, span 30–90 % half-span, ±20°, dual actuation (guide §6.6).
- Current VLM: wash-in yield +0.00249 Cm/°, elevon yield +0.00256 Cm/°. Five degrees
  of elevon gives 2.6× the limiting provisional trim deficit; low-Re validation is open.
- Printed twist cap is 3.0°. The favourable provisional polar needs ≈ 0.6° permanent
  reflex, while the adverse Ncrit-12 polar needs ≈ 1.9° and fails that cap.
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

1. **Partial:** the in-house VLM models the elevon as a local incidence step over the
   30–90 % half-span. Replace/validate that approximation with a hinged-flap model and
   at least one measured low-Re datum (search item 1).
2. Build the trim envelope: Cm_δ × δ_avail (minus authority reserve) vs. the torsion
   window of I-07 → feasible SM range.
3. Cross it with the in-service SM survey (items 2–3) → recommended SM floor and CG
   band for the OP-01 resolution.
4. Deliver the C6/S5 gate with a declared reserve policy (e.g. 50 % of travel kept).

# 6. Deliverable

- Cm_δ/deg `[D]`, validated; feasible SM band; recommended CG envelope for F2 (P3) and
  S5; recommended elevon travel and chord for the guide §6.6.

# 7. Transfer limits

- Flap effectiveness at Re 3–5×10⁵ suffers from separation and hysteresis that
  potential-flow methods miss; the XFOIL calibration band of I-06 applies, and in-flight
  E2 data remain the final arbiter.
- In-service SM figures from forums are `[M]`-grade practice but rarely measured with
  the precision the repo requires; treat as priors, not data.
- This thread bounds the *pitch* problem; lateral-directional (dihedral effect, roll
  authority) remains Phase 1's own task.
