#!/usr/bin/env python3
"""Derived aerodynamic contract for Salamandra Article #1.

`design_config.py` holds the quantities a human *chooses*: span, area, taper,
sweep, twist, mass. This module holds the quantities that must then be
*computed* from them and that more than one downstream module needs — above all
the neutral point that sets the CG target.

WHY THIS MODULE EXISTS. The neutral point used to be a hand-copied literal in
`balance_cg.py`:

    NP_VLM = -75.8e-3       # m, VLM 40x6, I-21 [D]

with `CG_TARGET = NP_VLM - STATIC_MARGIN * MAC` built on top of it. Changing
`SWEEP_C4_DEG`, `TAPER`, `B` or `S` moved the real neutral point and left that
literal untouched, and no check compared the two. That is the project's most
repeated correction (failure mode #3, "failing to re-derive downstream") written
into the source of the single most consequential number in the aircraft.

Here the neutral point is **derived and cached**, and the published values are
kept only as regression anchors with an explicit tolerance. If the planform
changes, the derivation moves, the anchor check fails, and the change has to be
made deliberately through an ADR and a CHANGELOG correction instead of silently.

Confidence: every value returned is `[D]` from the `[M]`/`[E]` planform inputs.
Both solvers are inviscid, linear, flat-plate lifting-surface models; the
section moment comes from XFOIL separately (see `elevon_authority.py`).
"""
from functools import cache

from design_config import (
    B,
    DESIGN_TWIST_DEG,
    MAC,
    S,
    STATIC_MARGIN,
    SWEEP_C4_DEG,
    TAPER,
    VLM_NX,
    VLM_NY,
    WEISSINGER_NY,
)

# ---------------------------------------------------------------------------
# Published anchors (I-21, ADR-0040).  These are REGRESSION GUARDS, not the
# source: the derivation below is the source.  A re-derivation outside the
# tolerance is a real design change and must be published as such.
# ---------------------------------------------------------------------------
NP_VLM_PUBLISHED = -75.8e-3      # m from root c/4, VLM at the canonical mesh
NP_WL_PUBLISHED = -72.9e-3       # m from root c/4, Weissinger-L, ny = 100
NP_ANCHOR_TOLERANCE = 0.5e-3     # m; drift beyond this is a published change

# Spread between two structurally different formulations.  This is a real
# modelling uncertainty on the neutral point, not a rounding: at 2.9 mm it is
# 16 % of the 18.0 mm static margin and 58 % of the +/-5 mm CG band, so it is
# carried explicitly rather than absorbed into a single quoted figure.
NP_METHOD_TOLERANCE = 5.0e-3     # m; agreement required between the methods

# Discretisation error retained at the canonical mesh, established by the
# convergence assertion in `validation_checks`.
NP_MESH_TOLERANCE = 0.4e-3       # m between the canonical mesh and 2x refinement


@cache
def _vlm(ny=VLM_NY, nx=VLM_NX, twist_deg=DESIGN_TWIST_DEG):
    """Cached VLM solution for the released planform."""
    from vlm_ala_volante import analiza      # deferred: keeps import cost local
    return analiza(B, S, TAPER, SWEEP_C4_DEG, twist_deg,
                   ny=ny, nx=nx, verbose=False)


@cache
def neutral_point_vlm(ny=VLM_NY, nx=VLM_NX):
    """Panel-VLM neutral point [m aft of the root quarter chord].

    Negative is forward of the root c/4.  Twist does not enter: the model is
    linear, so the lift-slope and moment-slope superpose and the neutral point
    is a property of the planform alone.
    """
    return _vlm(ny, nx)["x_np"]


@cache
def neutral_point_weissinger(ny=WEISSINGER_NY):
    """Weissinger-L neutral point [m], an independent formulation (C2)."""
    from weissinger_np import weissinger
    return weissinger(B, S, TAPER, SWEEP_C4_DEG, ny=ny)["x_np"]


@cache
def lift_curve_slope(ny=VLM_NY, nx=VLM_NX):
    """Released-wing lift-curve slope [1/rad] at the canonical mesh."""
    return _vlm(ny, nx)["CLa"]


@cache
def cg_target():
    """Longitudinal CG target [m aft of the root c/4] at the released margin.

    Derived from the re-computed neutral point, not from a copied constant.
    """
    return neutral_point_vlm() - STATIC_MARGIN * MAC


def neutral_point_percent_mac(x_np=None):
    """Neutral point as a percentage of MAC, measured from the MAC leading edge."""
    if x_np is None:
        x_np = neutral_point_vlm()
    return (x_np - _vlm()["g"]["x_le_mac"]) / MAC * 100.0


def validation_checks():
    """Named checks: the derivation reproduces the published contract."""
    vlm = neutral_point_vlm()
    weissinger = neutral_point_weissinger()
    refined = neutral_point_vlm(ny=2 * VLM_NY, nx=2 * VLM_NX)
    return {
        "VLM neutral point reproduces its published anchor":
            abs(vlm - NP_VLM_PUBLISHED) <= NP_ANCHOR_TOLERANCE,
        "Weissinger-L neutral point reproduces its published anchor":
            abs(weissinger - NP_WL_PUBLISHED) <= NP_ANCHOR_TOLERANCE,
        "independent formulations agree within the declared method spread":
            abs(vlm - weissinger) <= NP_METHOD_TOLERANCE,
        "canonical mesh is converged within the declared mesh tolerance":
            abs(vlm - refined) <= NP_MESH_TOLERANCE,
        "the neutral point is forward of the root quarter chord": vlm < 0.0,
        "CG target trails the derived neutral point by the static margin":
            abs((neutral_point_vlm() - cg_target()) / MAC - STATIC_MARGIN)
            < 1e-12,
        "released lift slope is in the finite-wing range":
            3.5 < lift_curve_slope() < 5.5,
    }


def main():
    vlm = neutral_point_vlm()
    weissinger = neutral_point_weissinger()
    refined = neutral_point_vlm(ny=2 * VLM_NY, nx=2 * VLM_NX)
    print("=" * 78)
    print("SALAMANDRA DERIVED AERODYNAMIC CONTRACT - re-derived, not copied")
    print("=" * 78)
    print(f"  canonical mesh: VLM {VLM_NY}x{VLM_NX}, "
          f"Weissinger-L ny={WEISSINGER_NY}")
    print(f"  x_NP  (VLM)          = {vlm*1000:+.2f} mm "
          f"({neutral_point_percent_mac():.2f} % MAC)")
    print(f"  x_NP  (Weissinger-L) = {weissinger*1000:+.2f} mm")
    print(f"  method spread        = {abs(vlm-weissinger)*1000:.2f} mm "
          f"(limit {NP_METHOD_TOLERANCE*1000:.1f} mm)")
    print(f"  mesh sensitivity     = {abs(vlm-refined)*1000:.2f} mm at 2x "
          f"refinement (limit {NP_MESH_TOLERANCE*1000:.1f} mm)")
    print(f"  CL_alpha             = {lift_curve_slope():.4f} /rad")
    print(f"  CG target at SM {STATIC_MARGIN*100:.0f} %  = "
          f"{cg_target()*1000:+.2f} mm from root c/4")
    print("\n  Published anchors: "
          f"VLM {NP_VLM_PUBLISHED*1000:+.1f} mm, "
          f"Weissinger-L {NP_WL_PUBLISHED*1000:+.1f} mm "
          f"(tolerance +/-{NP_ANCHOR_TOLERANCE*1000:.1f} mm)")

    checks = validation_checks()
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
