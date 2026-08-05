# I-11 — Reflexed-airfoil database for the B3 shortlist

**Status:** 🔄 **Open — partial: aerodesign.de tailless database reviewed (2026-08-05); UIUC availability checked for the shortlist**
**Feeds:** B3/G2 (airfoil screening), OP-02 (provisional profile), R-AIRFOIL re-derivation, guide §6.2
**Closes:** G2 (with I-06, E2)
**Correction generated:** C28 (MH 45 t/c error in the design guide)

---

# 1. Question

What do the published reflexed-airfoil databases say about the B3 shortlist *before*
XFOIL runs — thickness, published Cm0, flight-verified wing-loading bands, and known
behavioral warnings — and what measured polars exist for these sections at Re 2–5×10⁵?

# 2. Primary sources reviewed

- **aerodesign.de — "Airfoil Database for Tailless and Flying Wings"** (Hartmut
  Siegmann; MH data from Hepperle) — accessed 2026-08-05 `[M]`:
  https://www.aerodesign.de/english/profile/profile_s.htm
- **UIUC Airfoil Data Site** — checked for the shortlist candidates `[D]` (E205
  present; PW51 absent — 404 confirmed).

# 3. Database values `[M]` (published by the database, not yet XFOIL-verified here)

| Section | Camber f | Thickness d | Published cm0 | Notes from the database |
|---|---|---|---:|---|
| **MH 45** | 1.65 % | **9.85 %** | **+0.0070** | clmax "somewhat small"; **best at 15–40 g/dm²**; conclusion: lightweight swept wings, low AR |
| MH 45-8 % | 1.65 % | 8.00 % | +0.0070 | **"Bad idea!"** — lack of camber *and* thickness causes trouble on reflexed sections; clmax loss, harsh stall |
| **MH 60** | 1.76 % | 10.08 % | +0.0030 | "somewhat better than MH45"; lower pitch moment → more washout needed |
| **MH 60-12 %** | 1.76 % | 12.00 % | +0.0030 | MH at highest thickness — still below 13.5 % |
| S 5010 | 2.20 % | 9.83 % | **+0.0080** | Meets R-AIRFOIL cm0; thickness in the tip range |
| S 5020 | 2.62 % | 8.40 % | +0.0080 | "too high cambered for F5B"; fine at higher wing loading |
| TL 56 | 1.40 % | 8.96 % | +0.0072 | Aerobatics/EDF |
| **HS 130** (plank) | 1.68 % | 9.65 % | **+0.0157** | Very popular fast planks; elevons 25 % c; min chord 150 mm; AR 8–13 |
| EH 1.5/9, EH 2.0/10 | 1.5–2.0 % | 9–10 % | 0.0000 | **Warned against**: pitch-frequency problems ("pilot shaker", SB-13-like); "this use is not recommended" |
| HS 3.4/12.0 | 3.5 % | 12.0 % | −0.0010 | "Damn uncritical", smooth stall, for span ≥ 4 m |

# 4. Findings `[D]` (derived from the table)

1. **No off-the-shelf reflexed section reaches 13.5 % t/c.** The thickest are
   MH 60-12 % (12.0 %) and HS 3.4/12.0 (12.0 %). The guide's provisional root (MH 45,
   "t/c ≈ 13 %") was wrong — MH 45 is **9.85 %** (C28).
2. **The published cm0 band of reflexed sections is +0.003…+0.008.** R-AIRFOIL
   (≥ +0.008, target +0.010…+0.015) is met by S 5010/S 5020 only, and only at 8–10 %
   thickness. At 12–13.5 % thickness there is no published candidate at or above +0.008.
   **R-AIRFOIL must either be re-derived against the twist window (I-07) or the airfoil
   must be a scaled/modified section — B3's core decision.**
3. **The 9 % tip plan runs into the database's explicit warning:** thinning reflexed
   sections (MH 45-8 % precedent) costs clmax and produces harsh stall ("lack of camber
   and thickness causes trouble on this specific kind of reflexed airfoils"). The tip
   profile must be selected with camber compensation, not pure thickness scaling.
4. **Wing-loading compatibility:** MH 45 is documented for 15–40 g/dm²; Salamandra
   cruises at 57 g/dm². S 5010 (35–100 g/dm²) and S 5020 (25–90 g/dm²) are documented
   for the project's loading — with the caveat that those figures come from fast
   competition tailless (F5B, 100–150 km/h), not FPV cruise.
5. **E205** (I-09): 10.6 % t/c, flight-proven at Re 1.5–3×10⁵ on two in-service FPV
   aircraft, camber 2.9 %; cm0 unknown (tailed planes trim it) — screening candidate
   only.
6. **PW51** (Nemesis airfoil, I-08): **not in the UIUC database** (404). Coordinates and
   polars must be sourced elsewhere (designer's files, other databases) or dropped from
   the measured-data path.

# 5. What still needs to be found

- Measured polars at Re 2–5×10⁵ for the shortlist: UIUC (E205, E208, SD7003 have
  data); MH 45/S 5010 measured data are scarce — likely XFOIL-only with the calibrated
  Ncrit 10–12 band (I-06).
- PW51 coordinates/polars availability.
- The "Faszination Nurflügel" (Unverferth) book data for flight-verified cm0 of these
  sections — for cross-checking the database.

# 6. Consequence for the design guide (applied)

- §6.2 provisional candidates updated (C28): root MH 45 → **replaced by a
  thickness-scaled reflexed section candidate (MH 60-12 % as the closest published
  family member; final in B3)**; tip: thickness scaling alone warned against — camber
  compensation required.
- R-AIRFOIL feasibility at 13.5 % is now an explicit B3 question, not an assumption.

# 7. Transfer limits

- The database values are **published design values** (mostly XFOIL-derived origin),
  not tunnel measurements — `[M]` in the sense of "published by the designer", not
  "measured". The measured-data path remains UIUC/E2 (G2 closing plan).
- Wing-loading bands come from competition practice at higher speeds than the
  Salamandra cruise; they are priors, not requirements.
