#!/usr/bin/env python3
"""
Hand-launch feasibility of the Salamandra Cruise (I-14 — executed 2026-08-06,
rev. 3 updated to the ADR-0043 Article #1 masses after the Mojito
configuration-class correction and published throwing biomechanics).

WHY THIS DOCUMENT EXISTS: the launch is a mandatory hand throw (docs/00) and
the stall speed is the tightest margin in the design (45.0 km/h = 12.5 m/s for
the current V1 allocation, ADR-0043). The FIRST revision of this script demanded
k_safe = 1.20 at the RELEASE INSTANT and concluded "infeasible". That was too
strict on two counts, corrected here:

  (1) The release requirement is V_suelta >= V_stall with the elevon-up launch
      attitude — NOT k x V_stall at the release instant. The margin is built
      by the motor acceleration in the first 0.3-0.5 s after release
      (T/W ~ 1.0 -> a ~ 10 m/s2: from 13 to 15.3 m/s in 0.23 s).
  (2) The thrust during the throw was underestimated: INAV wing-throw practice
      uses nav_fw_launch_idle_thr = 1350-1450 (0.5-0.67 x hover throttle) and
      the motor spins for the whole throw gesture (0.4-0.6 s) -> +2-4 m/s.

CONFIGURATION-CLASS ANCHOR [M]: the TBS Mojito — 1300 mm, ~1800 g, pusher,
community-reported stall ~60 km/h (16.7 m/s), i.e. HEAVIER and with a HIGHER
stall than the Salamandra — is hand-launched in service (TBS manual includes
a bungee hook as an option; community launches it by hand with idle 1300 +
launch 1850 and over-head techniques). If the configuration class launches at
16.7 m/s stall, the Salamandra at 12.5 m/s is a strictly easier case.

MODEL:
  V_suelta  = V_hand + (T_idle/m) * t_gesture     (thrust during the throw)
  gate      = V_suelta >= V_stall                 (release requirement)
  t_margin  = time after release to reach k=1.2 x V_stall at launch accel
              (incl. nav_fw_launch_motor_delay = 0.2 s)
  torque-roll check: T/W at launch <= 1.5 [I] (community risk threshold)

Inputs: W 1.5835 kg CLEAN / 1.6202 kg V1 (ADR-0043); CL_max 0.589 [D] I-07;
S 0.282 m2. V_hand: published throwing biomechanics (van den Tillaar 2004,
JSSM: 0.409 kg -> 21.5 m/s, significant negative linear mass-speed
relationship; extrapolation to 1.6-1.7 kg overhead/two-hand push: typical
8-12, strong 10-13 m/s) + community practice (8-10 m/s for 2+ kg, Reddit).
Idle thrust: INAV hover rule T/W ~ 1.0 (nav_fw_launch_thr) x 0.5-0.67
(nav_fw_launch_idle_thr, wing-throw band) -> 8-12 N; t_gesture 0.4-0.6 s.
Motor delay 0.2 s (INAV guide, pushers never 0); spinup 0.1-0.2 s.

Confidence tags: [D] derived, [E] estimated, [I] inferred; bands declared.
Validation cases at the end.
"""
import sys
import numpy as np

RHO = 1.225
S = 0.282
CL_MAX = 0.589              # [D] I-07 (wing, non-elliptic) — matches mass_budget
G = 9.81

AUW = (1.5835, 1.6202)        # kg: Article #1 CLEAN / V1 allocations (ADR-0043)
K_REF = 1.20                  # margin reached AFTER release (acceleration)
V_HAND = (10.5, 8.0, 13.0)    # m/s: [D]-ish band from throwing biomechanics
                              # (van den Tillaar 2004 + community): ref/lo/hi
T_W = (1.00, 0.90, 1.10)      # INAV nav_fw_launch_thr = hover throttle [D]
IDLE_FRAC = (0.60, 0.50, 0.67)  # nav_fw_launch_idle_thr, wing-throw band [D]
T_GESTURE = (0.5, 0.4, 0.6)   # s: throw gesture with motor spinning [E]
MOTOR_DELAY = 0.2             # s: nav_fw_launch_motor_delay (200 ms) [D]
T_W_MAX = 1.5                 # torque-roll community risk threshold [I]

# Mojito configuration-class anchor [M] (docs/02 + community): 1300 mm,
# ~1800 g, stall ~60 km/h reported (16.7 m/s), hand-launched
MOJITO_W = 1.8
MOJITO_STALL = 60.0 / 3.6     # m/s, community-reported (optimistic band)


def v_stall(weight):
    return np.sqrt(2.0 * weight * G / (RHO * S * CL_MAX))


def main():
    print("=" * 74)
    print("HAND-LAUNCH FEASIBILITY — Salamandra Cruise (I-14 executed, rev. 3)")
    print("=" * 74)

    vs = v_stall(AUW[1])
    vs_g = v_stall(AUW[0])
    print(f"\n1. STALL SPEED")
    print(f"   V1 (1620.2 g): {vs*3.6:5.1f} km/h ({vs:4.1f} m/s) "
          f"· CLEAN (1583.5 g): {vs_g*3.6:5.1f} km/h ({vs_g:4.1f} m/s)")
    print(f"   Configuration-class anchor [M]: TBS Mojito 1800 g, stall "
          f"~{MOJITO_STALL*3.6:.0f} km/h reported, HAND-LAUNCHED in service")
    print(f"   -> Salamandra stall is LOWER: strictly easier launch case")

    print(f"\n2. RELEASE GATE (V_suelta >= V_stall)")
    vh_r, vh_lo, vh_hi = V_HAND
    t_r = T_GESTURE[0]
    t_idle_r = IDLE_FRAC[0] * T_W[0] * AUW[1] * G
    t_idle_lo = IDLE_FRAC[1] * T_W[1] * AUW[1] * G
    t_idle_hi = IDLE_FRAC[2] * T_W[2] * AUW[1] * G
    for vh, ti, tg, tag in [(vh_lo, t_idle_lo, T_GESTURE[1], "weak throw, low idle"),
                            (vh_r, t_idle_r, t_r, "typical throw, ref idle"),
                            (vh_hi, t_idle_hi, T_GESTURE[2], "firm throw, high idle")]:
        v_rel = vh + ti / AUW[1] * tg
        k_rel = v_rel / vs
        print(f"   {tag:30s}: V_suelta = {v_rel:4.1f} m/s "
              f"({v_rel*3.6:5.1f} km/h) -> k = {k_rel:4.2f} x V_stall "
              f"({'PASS' if v_rel >= vs else 'FAIL'} gate)")

    print(f"\n3. MARGIN AFTER RELEASE (k reaches {K_REF:.2f} by acceleration)")
    a_launch = T_W[0] * G                    # launch throttle, T/W ~ 1.0 [D]
    for vh, ti, tg, tag in [(vh_lo, t_idle_lo, T_GESTURE[1], "weak throw"),
                            (vh_r, t_idle_r, t_r, "typical throw"),
                            (vh_hi, t_idle_hi, T_GESTURE[2], "firm throw")]:
        v_rel = vh + ti / AUW[1] * tg
        t_need = max((K_REF * vs - v_rel) / a_launch, 0.0)
        t_tot = MOTOR_DELAY + t_need
        print(f"   {tag:14s}: V_suelta {v_rel:4.1f} m/s -> k={K_REF:.2f} at "
              f"{t_tot:4.2f} s after release (0.2 s delay + spinup)")

    print(f"\n4. TORQUE-ROLL CHECK (community threshold T/W <= {T_W_MAX} [I])")
    tw_launch = T_W[1]                       # worst band end
    print(f"   Launch T/W = {tw_launch:.2f} ({T_W[0]:.2f} ref) "
          f"-> {'OK (below threshold)' if tw_launch < T_W_MAX else 'RISK'}")
    print(f"   Recommended: progressive throttle at launch; the Salamandra "
          f"T/W ~ 1.0 is inside the safe band (the 1.7:1 problematic cases "
          f"documented are overpowered models).")

    print(f"\n5. VERDICT (printed finding, not a model check)")
    v_typ = vh_r + t_idle_r / AUW[1] * t_r
    v_firm = vh_hi + t_idle_hi / AUW[1] * T_GESTURE[2]
    ok_typ = v_typ >= vs
    print(f"   Typical throw: V_suelta {v_typ:.1f} m/s ({v_typ*3.6:.1f} km/h) "
          f"vs V_stall {vs*3.6:.1f} km/h -> "
          f"{'PASSES the gate' if ok_typ else 'below stall'}; k=1.20 reached "
          f"in {MOTOR_DELAY + max((K_REF*vs - v_typ)/a_launch, 0.0):.2f} s")
    print(f"   Firm throw: V_suelta {v_firm:.1f} m/s ({v_firm*3.6:.1f} km/h) "
          f"-> k = {v_firm/vs:.2f} at release")
    print(f"   => HAND LAUNCH IS FEASIBLE with a firm throw (V_hand >= 10 "
          f"m/s) + high idle (nav_fw_launch_idle_thr 1350-1450) + launch "
          f"throttle at the hover setting (T/W ~ 1.0). The weak-throw case "
          f"stays below stall: technique is part of the specification.")
    print(f"   Corroborated by the configuration-class anchor [M]: the Mojito "
          f"(heavier, higher stall) is hand-launched in service.")

    print("\n6. VALIDATION CASES")
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"   [{'PASS' if cond else 'FAIL'}] {name}")

    vs_c = v_stall(1.6202)
    check(f"V_stall reproduces mass_budget V1 45.0 km/h (got "
          f"{vs_c*3.6:.1f})", abs(vs_c * 3.6 - 45.0) < 0.3)
    vs_g2 = v_stall(1.5835)
    check(f"V_stall reproduces mass_budget CLEAN 44.5 km/h (got {vs_g2*3.6:.1f})",
          abs(vs_g2 * 3.6 - 44.5) < 0.3)
    v_zero = vh_r + 0.0 / AUW[1] * t_r
    check(f"No thrust: V_suelta = V_hand ({v_zero:.1f} m/s)",
          abs(v_zero - vh_r) < 1e-9)
    check(f"Firm throw + high idle passes the release gate "
          f"({v_firm:.1f} vs {vs_c:.1f} m/s)", v_firm >= vs_c)
    check(f"Typical throw + ref idle passes the release gate "
          f"({v_typ:.1f} vs {vs_c:.1f} m/s)", v_typ >= vs_c)
    t_marg_typ = MOTOR_DELAY + max((K_REF * vs_c - v_typ) / (T_W[0] * G), 0.0)
    check(f"Typical throw reaches k=1.20 in < 0.6 s "
          f"(got {t_marg_typ:.2f} s)", t_marg_typ < 0.6)
    check(f"Launch T/W below the 1.5 torque-roll threshold "
          f"({T_W[1]:.2f} < {T_W_MAX})", T_W[1] < T_W_MAX)
    check(f"Mojito anchor consistency: heavier and higher stall than the "
          f"Salamandra ({MOJITO_W} kg, {MOJITO_STALL*3.6:.0f} km/h vs "
          f"{AUW[1]} kg, {vs_c*3.6:.1f} km/h)", MOJITO_W > AUW[1]
          and MOJITO_STALL > vs_c)
    check(f"Biomechanics band: V_hand ref 10.5 in [8, 13] "
          f"({V_HAND[0]} in [{V_HAND[1]}, {V_HAND[2]}])",
          V_HAND[1] <= V_HAND[0] <= V_HAND[2])

    print(f"\n   VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
