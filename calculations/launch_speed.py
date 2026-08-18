#!/usr/bin/env python3
"""
Hand-launch feasibility of the Salamandra Cruise (I-14 — executed 2026-08-06,
revision 6: ADR-0045 Article #1 masses, drag-inclusive RK4 propagation,
Mojito configuration-class correction and published throwing biomechanics).

WHY THIS DOCUMENT EXISTS: the launch is a mandatory hand throw (docs/00) and
the stall speed is the tightest margin in the design (44.7 km/h = 12.4 m/s for
the connected V1 lower model; physical mass and CLmax closure remain open at F2/E2).
The FIRST revision of this script demanded
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
16.7 m/s stall, the Salamandra at 12.4 m/s is a strictly easier case.

MODEL:
  m dV/dt   = T - 0.5 rho V^2 S CD_launch - m g sin(gamma), RK4; T is
               piecewise constant within the idle/delay/launch phases
  V_suelta  = propagated speed after the powered throw gesture
  gate      = V_suelta >= V_stall                 (release requirement)
  t_margin  = time after release to reach k=1.2 x V_stall, retaining idle
               during nav_fw_launch_motor_delay = 0.2 s
  torque-roll check: T/W at launch <= 1.5 [I] (community risk threshold)

Inputs: shared CLEAN allocation and V1 analytical lower mass (C32);
CL_max 0.589 [D] I-07;
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

import drag_model
from design_config import (
    ARTICLE_CLEAN_MASS_KG,
    ARTICLE_V1_MASS_KG,
    G0,
    RHO_SL,
    S,
    stall_speed,
)

AUW = (ARTICLE_CLEAN_MASS_KG, ARTICLE_V1_MASS_KG)
K_REF = 1.20                  # margin reached AFTER release (acceleration)
V_HAND = (10.5, 8.0, 13.0)    # m/s: [D]-ish band from throwing biomechanics
                              # (van den Tillaar 2004 + community): ref/lo/hi
T_W = (1.00, 0.90, 1.10)      # INAV nav_fw_launch_thr = hover throttle [D]
IDLE_FRAC = (0.60, 0.50, 0.67)  # nav_fw_launch_idle_thr, wing-throw band [D]
T_GESTURE = (0.5, 0.4, 0.6)   # s: throw gesture with motor spinning [E]
MOTOR_DELAY = 0.2             # s: nav_fw_launch_motor_delay (200 ms) [D]
T_W_MAX = 1.5                 # torque-roll community risk threshold [I]
# Launch drag now comes from the SHARED polar with its viscous and induced
# terms separated (ADR-0009), not from a single lumped coefficient.  The gate
# is judged on the conservative end of the declared allowance band, which
# reproduces the retired 0.08 [E]: higher drag is what makes the release gate
# harder, so adopting the lower attached-flow value would be an unwarranted
# relaxation of a published conclusion.
CD_LAUNCH = drag_model.launch_cd_band()[1]        # conservative end [E]
CD_LAUNCH_NOMINAL = drag_model.launch_cd_band()[0]  # attached decomposition

# Mojito configuration-class anchor [M] (docs/02 + community): 1300 mm,
# ~1800 g, stall ~60 km/h reported (16.7 m/s), hand-launched
MOJITO_W = 1.8
MOJITO_STALL = 60.0 / 3.6     # m/s, community-reported (optimistic band)


def v_stall(weight):
    return stall_speed(weight)


# Flight-path angle during the throw and the seconds after release.  Below
# V_stall the wing cannot carry the weight by definition, so the trajectory is
# NOT level and the along-path gravity component is not zero.  The model
# previously omitted the term entirely and never declared a path angle, which
# left the sign of its conservatism unstated.  Positive gamma is a climb.
#
# The released gate uses GAMMA_LAUNCH_DEG = 0: a level throw.  That is the
# conservative choice for the release gate, because a descending throw would
# ADD  g*sin|gamma|  to the acceleration and make the gate easier to pass.
GAMMA_LAUNCH_DEG = 0.0            # declared launch path angle [E]
GAMMA_LAUNCH_BAND_DEG = (-10.0, 0.0, +10.0)   # descend / level / climb [E]


def acceleration(speed, thrust, mass, cd=CD_LAUNCH, gamma_deg=None):
    """Along-path acceleration [m/s2]: thrust, quadratic drag and gravity.

        m dV/dt = T - 0.5 rho V^2 S CD - m g sin(gamma)

    ``gamma_deg=None`` uses the declared launch path angle.
    """
    if gamma_deg is None:
        gamma_deg = GAMMA_LAUNCH_DEG
    if speed < 0.0 or thrust < 0.0 or mass <= 0.0 or cd < 0.0:
        raise ValueError("speed, thrust and CD must be non-negative; mass positive")
    drag = 0.5 * RHO_SL * speed**2 * S * cd
    return (thrust - drag) / mass - G0 * np.sin(np.radians(gamma_deg))


def propagate_speed(speed, thrust, mass, duration, cd=CD_LAUNCH, dt=0.001,
                    gamma_deg=None):
    """Integrate the along-path equation with fourth-order Runge-Kutta."""
    if duration < 0.0 or dt <= 0.0:
        raise ValueError("duration must be non-negative and dt positive")
    steps = max(1, int(np.ceil(duration / dt)))
    h = duration / steps
    value = speed
    for _ in range(steps):
        k1 = acceleration(value, thrust, mass, cd, gamma_deg)
        k2 = acceleration(value + 0.5 * h * k1, thrust, mass, cd, gamma_deg)
        k3 = acceleration(value + 0.5 * h * k2, thrust, mass, cd, gamma_deg)
        k4 = acceleration(value + h * k3, thrust, mass, cd, gamma_deg)
        value += h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
    return value


def time_to_speed(speed, target, idle_thrust, launch_thrust, mass,
                  motor_delay=MOTOR_DELAY, dt=0.001, timeout=2.0):
    """Time after release to reach target, retaining idle during motor delay."""
    if target <= speed:
        return 0.0
    elapsed = 0.0
    value = speed
    while elapsed < timeout and value < target:
        thrust = idle_thrust if elapsed < motor_delay else launch_thrust
        value = propagate_speed(value, thrust, mass, dt, dt=dt)
        elapsed += dt
    return elapsed if value >= target else float("inf")


def main():
    print("=" * 74)
    print("HAND-LAUNCH FEASIBILITY — Salamandra Cruise (I-14 executed, rev. 6)")
    print("=" * 74)

    vs = v_stall(AUW[1])
    vs_g = v_stall(AUW[0])
    print("\n1. STALL SPEED")
    print(f"   V1 analytical lower ({AUW[1]*1000:.1f} g): "
          f"{vs*3.6:5.1f} km/h ({vs:4.1f} m/s) · CLEAN "
          f"({AUW[0]*1000:.1f} g): {vs_g*3.6:5.1f} km/h ({vs_g:4.1f} m/s)")
    print(f"   Configuration-class anchor [M]: TBS Mojito 1800 g, stall "
          f"~{MOJITO_STALL*3.6:.0f} km/h reported, HAND-LAUNCHED in service")
    print("   -> Salamandra stall is LOWER: strictly easier launch case")

    print("\n2. RELEASE GATE (V_suelta >= V_stall)")
    vh_r, vh_lo, vh_hi = V_HAND
    t_r = T_GESTURE[0]
    t_idle_r = IDLE_FRAC[0] * T_W[0] * AUW[1] * G0
    t_idle_lo = IDLE_FRAC[1] * T_W[1] * AUW[1] * G0
    t_idle_hi = IDLE_FRAC[2] * T_W[2] * AUW[1] * G0
    for vh, ti, tg, tag in [(vh_lo, t_idle_lo, T_GESTURE[1], "weak throw, low idle"),
                            (vh_r, t_idle_r, t_r, "typical throw, ref idle"),
                            (vh_hi, t_idle_hi, T_GESTURE[2], "firm throw, high idle")]:
        v_rel = propagate_speed(vh, ti, AUW[1], tg)
        k_rel = v_rel / vs
        print(f"   {tag:30s}: V_suelta = {v_rel:4.1f} m/s "
              f"({v_rel*3.6:5.1f} km/h) -> k = {k_rel:4.2f} x V_stall "
              f"({'PASS' if v_rel >= vs else 'FAIL'} gate)")

    print(f"\n3. MARGIN AFTER RELEASE (k reaches {K_REF:.2f} by acceleration)")
    t_launch = T_W[0] * AUW[1] * G0          # launch throttle, T/W ~ 1.0 [D]
    for vh, ti, tg, tag in [(vh_lo, t_idle_lo, T_GESTURE[1], "weak throw"),
                            (vh_r, t_idle_r, t_r, "typical throw"),
                            (vh_hi, t_idle_hi, T_GESTURE[2], "firm throw")]:
        v_rel = propagate_speed(vh, ti, AUW[1], tg)
        t_tot = time_to_speed(v_rel, K_REF * vs, ti, t_launch, AUW[1])
        print(f"   {tag:14s}: V_suelta {v_rel:4.1f} m/s -> k={K_REF:.2f} at "
              f"{t_tot:4.2f} s after release (0.2 s delay + spinup)")

    print(f"\n4. TORQUE-ROLL CHECK (community threshold T/W <= {T_W_MAX} [I])")
    tw_launch = T_W[2]                       # worst (highest-thrust) band end
    print(f"   Launch T/W = {tw_launch:.2f} ({T_W[0]:.2f} ref) "
          f"-> {'OK (below threshold)' if tw_launch < T_W_MAX else 'RISK'}")
    print("   Recommended: progressive throttle at launch; the Salamandra "
          "T/W ~ 1.0 is inside the safe band (the 1.7:1 problematic cases "
          "documented are overpowered models).")

    print("\n5. VERDICT (printed finding, not a model check)")
    v_typ = propagate_speed(vh_r, t_idle_r, AUW[1], t_r)
    v_firm = propagate_speed(vh_hi, t_idle_hi, AUW[1], T_GESTURE[2])
    ok_typ = v_typ >= vs
    print(f"   Typical throw: V_suelta {v_typ:.1f} m/s ({v_typ*3.6:.1f} km/h) "
          f"vs V_stall {vs*3.6:.1f} km/h -> "
          f"{'PASSES the gate' if ok_typ else 'below stall'}; k=1.20 reached "
          f"in {time_to_speed(v_typ, K_REF*vs, t_idle_r, t_launch, AUW[1]):.2f} s")
    print(f"   Firm throw: V_suelta {v_firm:.1f} m/s ({v_firm*3.6:.1f} km/h) "
          f"-> k = {v_firm/vs:.2f} at release")
    print("   => HAND LAUNCH IS FEASIBLE with a firm throw (V_hand >= 10 "
          "m/s) + high idle (nav_fw_launch_idle_thr 1350-1450) + launch "
          "throttle at the hover setting (T/W ~ 1.0). The weak-throw case "
          "stays below stall: technique is part of the specification.")
    print("   Corroborated by the configuration-class anchor [M]: the Mojito "
          "(heavier, higher stall) is hand-launched in service.")

    print("\n6. VALIDATION CASES")
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"   [{'PASS' if cond else 'FAIL'}] {name}")

    vs_c = v_stall(ARTICLE_V1_MASS_KG)
    check(f"V_stall reproduces mass_budget V1 44.7 km/h (got "
          f"{vs_c*3.6:.1f})", abs(vs_c * 3.6 - 44.7) < 0.1)
    vs_g2 = v_stall(ARTICLE_CLEAN_MASS_KG)
    check(f"V_stall reproduces mass_budget CLEAN 44.1 km/h (got {vs_g2*3.6:.1f})",
          abs(vs_g2 * 3.6 - 44.1) < 0.1)
    v_zero = propagate_speed(vh_r, 0.0, AUW[1], t_r, cd=0.0)
    check(f"No thrust and no drag: release speed equals hand speed "
          f"({v_zero:.1f} m/s)",
          abs(v_zero - vh_r) < 1e-9)
    check(f"Firm throw + high idle passes the release gate "
          f"({v_firm:.1f} vs {vs_c:.1f} m/s)", v_firm >= vs_c)
    check(f"Typical throw + ref idle passes the release gate "
          f"({v_typ:.1f} vs {vs_c:.1f} m/s)", v_typ >= vs_c)
    t_marg_typ = time_to_speed(
        v_typ, K_REF * vs_c, t_idle_r, t_launch, AUW[1])
    check(f"Typical throw reaches k=1.20 in < 0.6 s "
          f"(got {t_marg_typ:.2f} s)", t_marg_typ < 0.6)
    check(f"Launch T/W below the 1.5 torque-roll threshold "
          f"({T_W[2]:.2f} < {T_W_MAX})", T_W[2] < T_W_MAX)
    check(f"Mojito anchor consistency: heavier and higher stall than the "
          f"Salamandra ({MOJITO_W} kg, {MOJITO_STALL*3.6:.0f} km/h vs "
          f"{AUW[1]} kg, {vs_c*3.6:.1f} km/h)", MOJITO_W > AUW[1]
          and MOJITO_STALL > vs_c)
    v_band = [propagate_speed(vh_r, t_idle_r, AUW[1], t_r, gamma_deg=angle)
              for angle in GAMMA_LAUNCH_BAND_DEG]
    check(f"Declared path-angle band is propagated and ordered "
          f"(descend {v_band[0]:.2f} > level {v_band[1]:.2f} > "
          f"climb {v_band[2]:.2f} m/s)",
          v_band[0] > v_band[1] > v_band[2])
    check(f"The released level throw is the conservative end against a "
          f"descent ({v_band[1]:.2f} <= {v_band[0]:.2f} m/s)",
          v_band[1] <= v_band[0])
    check(f"Biomechanics band: V_hand ref 10.5 in [8, 13] "
          f"({V_HAND[0]} in [{V_HAND[1]}, {V_HAND[2]}])",
          V_HAND[1] <= V_HAND[0] <= V_HAND[2])
    check("RK4 constant-acceleration reference is exact within 1e-9",
          abs(propagate_speed(10.0, 5.0, 2.0, 0.4, cd=0.0) - 11.0) < 1e-9)

    print(f"\n   VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
