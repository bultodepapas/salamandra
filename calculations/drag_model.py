#!/usr/bin/env python3
"""Shared clean-configuration drag model for Salamandra Article #1.

ADR-0009 and `CLAUDE.md` are explicit: **never use a single Oswald factor for
drag; always separate the viscous term from the induced one.** That rule exists
because conflating them already produced correction C1.

Before this module the project honoured the rule in exactly one place. The
profile coefficient and the span efficiency lived as bare literals inside
`yaw_stability.py`, while `launch_speed.py` used a single lumped
``CD_LAUNCH = 0.08`` [E] with no decomposition at all, and `propulsion_match.py`
inverted an *allowable* drag from the power budget without a polar. Three
incompatible treatments of one physical quantity, none cross-checked.

This module is the one drag polar. Every consumer gets the two terms back
separately and is free to report their sum, but the separation is never lost on
the way.

    CD(CL) = CD_viscous(Re) + CL^2 / (pi * AR * e_span)

CONFIDENCE AND VALIDITY. `CD_PROFILE_CRUISE` is `[E]`, pending measured E2
polars; `SPAN_EFFICIENCY` is `[E]`. The model is a clean-configuration cruise
polar: it has no flap, no gear, no separated-flow rise and no compressibility.
It is applied outside cruise only where the caller declares the transfer, which
is what `launch_configuration_cd` does explicitly.
"""
from math import pi

from design_config import (
    ASPECT_RATIO,
    CL_MAX_WING,
    RHO_SL,
    S,
)

# Clean profile (viscous) drag coefficient at the cruise Reynolds number.
# Retains the value previously carried inside `yaw_stability.py`.
CD_PROFILE_CRUISE = 0.0136        # [E], pending measured E2 polars

# Induced span efficiency.  This is NOT an Oswald factor: it multiplies the
# induced term alone and never absorbs viscous drag (ADR-0009).
SPAN_EFFICIENCY = 0.85            # [E]

# Launch configuration: high incidence, near CLmax, gear-free hand launch.
# The viscous term is raised over the cruise value to cover the higher local
# incidence and the boom/pod at an off-design attitude.  Declared as a transfer,
# with its limit stated, rather than hidden inside a single lumped number.
CD_PROFILE_LAUNCH_FACTOR = 1.25   # [E] viscous rise at launch incidence
LAUNCH_CL_FRACTION = 0.90         # fraction of CLmax held during the throw [E]

# Separated-flow / attitude / windmilling allowance on top of the clean polar.
# The attached-flow decomposition alone gives CD ~ 0.035 at launch incidence,
# whereas the retired lumped estimate was CD_LAUNCH = 0.08 [E].  Adopting the
# lower number outright would make the launch analysis 2.3x more optimistic on
# drag with no evidence, which is precisely the unwarranted-transfer failure
# mode (C7/C12).  The allowance therefore spans both: the NOMINAL is the
# decomposed polar, the CONSERVATIVE end reproduces the retired estimate, and
# the hand-launch release gate is judged on the conservative end because higher
# drag is what makes reaching V_release harder.
LAUNCH_SEPARATION_ALLOWANCE = (1.0, 2.31)   # nominal, conservative [E]


def induced_cd(cl, aspect_ratio=ASPECT_RATIO, span_efficiency=SPAN_EFFICIENCY):
    """Induced drag coefficient for a lift coefficient [-]."""
    if aspect_ratio <= 0.0 or not 0.0 < span_efficiency <= 1.0:
        raise ValueError("aspect ratio must be positive and e_span in (0, 1]")
    return cl**2 / (pi * aspect_ratio * span_efficiency)


def clean_cd(cl, cd_profile=CD_PROFILE_CRUISE):
    """Return ``(viscous, induced)`` for the clean cruise configuration.

    Deliberately returns the pair, not the sum: a caller that wants the total
    adds them, and a caller that conflates them has to do so visibly.
    """
    if cd_profile < 0.0:
        raise ValueError("profile drag coefficient must be non-negative")
    return cd_profile, induced_cd(cl)


def launch_configuration_cd(cl=None, allowance=1.0):
    """Return ``(viscous, induced)`` for the hand-launch configuration.

    TRANSFER LIMIT: the cruise polar is carried to launch incidence through a
    declared viscous factor.  It models no separated flow and is not valid
    above CLmax; ``allowance`` is the declared cover for what it cannot model.
    """
    if cl is None:
        cl = LAUNCH_CL_FRACTION * CL_MAX_WING
    if cl <= 0.0 or allowance <= 0.0:
        raise ValueError("lift coefficient and allowance must be positive")
    return (CD_PROFILE_CRUISE * CD_PROFILE_LAUNCH_FACTOR * allowance,
            induced_cd(cl) * allowance)


def launch_cd_total(cl=None, allowance=1.0):
    """Total launch-configuration CD [-] (the two terms, summed here)."""
    viscous, induced = launch_configuration_cd(cl, allowance)
    return viscous + induced


def launch_cd_band(cl=None):
    """``(nominal, conservative)`` total launch CD across the allowance band."""
    return tuple(launch_cd_total(cl, allowance)
                 for allowance in LAUNCH_SEPARATION_ALLOWANCE)


def drag_newton(cd_total, speed, area=S, rho=RHO_SL):
    """Dimensional drag [N] from a total coefficient and a speed [m/s]."""
    if speed < 0.0 or area <= 0.0 or rho <= 0.0 or cd_total < 0.0:
        raise ValueError("speed/CD non-negative; area and density positive")
    return 0.5 * rho * speed**2 * area * cd_total


def lift_to_drag(cl, cd_profile=CD_PROFILE_CRUISE):
    """Clean-configuration lift-to-drag ratio at a lift coefficient."""
    viscous, induced = clean_cd(cl, cd_profile)
    return cl / (viscous + induced)


def best_glide_cl(cd_profile=CD_PROFILE_CRUISE,
                  aspect_ratio=ASPECT_RATIO,
                  span_efficiency=SPAN_EFFICIENCY):
    """CL at maximum L/D: the analytic optimum where induced == viscous."""
    return (cd_profile * pi * aspect_ratio * span_efficiency) ** 0.5


def validation_checks():
    """Named checks against closed-form results the model must reproduce."""
    cl_star = best_glide_cl()
    viscous, induced = clean_cd(cl_star)
    doubled = induced_cd(2.0)
    single = induced_cd(1.0)
    launch_viscous, launch_induced = launch_configuration_cd()
    return {
        "induced drag is quadratic in CL":
            abs(doubled - 4.0 * single) < 1e-12,
        "at best glide the induced term equals the viscous term":
            abs(viscous - induced) < 1e-12,
        "maximum L/D matches its closed form":
            abs(lift_to_drag(cl_star)
                - 0.5 * (pi * ASPECT_RATIO * SPAN_EFFICIENCY
                         / CD_PROFILE_CRUISE) ** 0.5) < 1e-9,
        "the viscous and induced terms are returned separately":
            launch_viscous > 0.0 and launch_induced > 0.0,
        "launch drag exceeds cruise-CL drag at the same speed":
            launch_cd_total() > sum(clean_cd(0.13)),
        "the launch band is ordered and brackets the retired 0.08 estimate":
            launch_cd_band()[0] < launch_cd_band()[1]
            and abs(launch_cd_band()[1] - 0.08) < 0.005,
        "span efficiency multiplies only the induced term":
            abs(clean_cd(1.0)[0] - CD_PROFILE_CRUISE) < 1e-12,
        "dimensional drag follows the dynamic-pressure law":
            abs(drag_newton(0.05, 20.0) - 4.0 * drag_newton(0.05, 10.0))
            < 1e-12,
    }


def main():
    print("=" * 78)
    print("SALAMANDRA SHARED DRAG MODEL - viscous and induced, never merged")
    print("=" * 78)
    print(f"  CD_profile(cruise) = {CD_PROFILE_CRUISE:.4f} [E]   "
          f"e_span = {SPAN_EFFICIENCY:.2f} [E]   AR = {ASPECT_RATIO:.3f}")
    print("\n    CL      CD_visc    CD_ind     CD_tot      L/D")
    for cl in (0.10, 0.13, 0.20, 0.30, best_glide_cl(), 0.50, CL_MAX_WING):
        viscous, induced = clean_cd(cl)
        print(f"  {cl:5.3f}    {viscous:.5f}   {induced:.5f}   "
              f"{viscous+induced:.5f}   {cl/(viscous+induced):6.2f}")
    print(f"\n  best glide at CL={best_glide_cl():.4f}, "
          f"L/D={lift_to_drag(best_glide_cl()):.2f} [D on E inputs]")
    launch_viscous, launch_induced = launch_configuration_cd()
    nominal, conservative = launch_cd_band()
    print(f"  launch configuration (CL={LAUNCH_CL_FRACTION*CL_MAX_WING:.3f}): "
          f"CD_visc={launch_viscous:.4f} + CD_ind={launch_induced:.4f} "
          f"= {nominal:.4f} nominal")
    print(f"  launch band: {nominal:.4f} (attached decomposition) .. "
          f"{conservative:.4f} (separated-flow allowance, reproduces the "
          "retired lumped 0.08 [E])")
    print("  The hand-launch gate is judged on the CONSERVATIVE end: higher "
          "drag is what makes reaching V_release harder.")
    print("  TRANSFER LIMIT: the cruise polar is carried to launch incidence "
          "through a declared viscous factor; it is not valid above CLmax and "
          "models no separated flow.")

    checks = validation_checks()
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
