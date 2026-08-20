#!/usr/bin/env python3
"""Reproducible evidence for NF Design Guide audit, Part 3.

This script does not release a fin or a flight envelope.  It interrogates the
current Salamandra contracts from the viewpoint of the NF Design Guide 2024
chapters on directional stability, low-Reynolds-number vertical surfaces,
finite sideslip, adverse yaw, stall progression and maiden-flight practice.

Evidence classes used in the accompanying report:

* [D] deterministic result from current repository inputs;
* [E] current engineering estimate inherited from ``yaw_stability.py``;
* [I] audit diagnostic used to expose sensitivity, not a validated model.

Run from the repository root with::

    python3 calculations/nf_design_guide_part3_directional_stability.py
"""

from __future__ import annotations

from math import atan2, degrees, radians, tan

import numpy as np

import equipment_layout
import yaw_stability as yaw
from design_config import (
    ARTICLE_V1_MASS_KG,
    B,
    CL_MAX_WING,
    NU_SL,
    RHO_SL,
    S,
    STALL_SPEED_LIMIT_KMH,
    SWEEP_C4_DEG,
    TAPER,
    TWIST_STRUCTURAL_CAP_DEG,
    lift_coefficient,
    speed_mps,
)
from vlm_ala_volante import geom, solve


SPEEDS_KMH = (45.0, 60.0, 75.0, 95.0)
SIDESLIP_DEG = (5.0, 10.0, 15.0, 24.0)
LOCAL_SECTION_CL_SCREEN = 0.65  # current sweep_trade.py generic [E]


def solved_layout(variant: str):
    """Return the repository's CG-closed layout for CLEAN or V1."""
    if variant.lower() == "clean":
        return equipment_layout.solve_battery_x(
            equipment_layout.reference_layout("clean")
        )[0]
    if variant.lower() == "v1":
        return equipment_layout.solve_v1_packaging().layout
    raise ValueError("variant must be CLEAN or V1")


def fin_reynolds(speed_kmh: float, fin) -> tuple[float, float, float]:
    """Root, MAC and tip Reynolds numbers for the V1 fin [D]."""
    speed = speed_mps(speed_kmh)
    return tuple(
        speed * chord / NU_SL
        for chord in (fin.root_chord_m, fin.mac_m, fin.tip_chord_m)
    )


def mode_metrics(values: np.ndarray) -> tuple[str, float, float, float]:
    """Classify an eigenvalue pair and return max real, wn and zeta."""
    dominant = values[int(np.argmax(values.real))]
    stable = "DAMPED" if dominant.real < 0.0 else "DIVERGENT"
    wn = abs(dominant)
    zeta = -dominant.real / wn if wn else float("nan")
    return stable, float(dominant.real), float(wn), float(zeta)


def wing_cnr(speed_kmh: float) -> float:
    """Current DATCOM wing Cnr estimate evaluated at the local V1 CL [E]."""
    cl = lift_coefficient(ARTICLE_V1_MASS_KG, speed_mps(speed_kmh))
    return -cl / 4.0


def yaw_modes_at(
    cnb_per_deg: float,
    speed_kmh: float,
    *,
    cyb: float = -0.15,
    cyr: float = 0.25,
) -> np.ndarray:
    """Evaluate the current reduced model with V1 mass and V1 inertia [I]."""
    layout = solved_layout("v1")
    s_v = yaw.fin_area_for_target(0.0005)
    cnr = wing_cnr(speed_kmh) + yaw.cnr_fin(
        s_v,
        yaw.fin_moment_arm(),
        yaw.helmbold_cla(yaw.AR_FIN, yaw.FIN_SWEEP_DEG),
    )
    return yaw.yaw_modes(
        cnb_per_deg,
        cnr,
        cyb=cyb,
        cyr=cyr,
        mass=layout.mass_g() / 1000.0,
        iz=layout.inertia_kg_m2()[2][2],
        speed=speed_mps(speed_kmh),
    )


def fin_sideforce_derivatives(s_v: float) -> tuple[float, float]:
    """Geometry-derived fin Cy_beta and Cy_r diagnostic, per radian [I].

    The signs follow the convention already used by ``yaw_state_matrix``.  This
    diagnostic is deliberately not called a correction: body/wing/fin
    interference and the final section polar are unavailable.
    """
    cla_lo_deg, cla_hi_deg = yaw.cla_fin_band(yaw.AR_FIN, yaw.FIN_SWEEP_DEG)
    cla_rad = 0.5 * (cla_lo_deg + cla_hi_deg) * yaw.DEG
    cyb_fin = -(
        yaw.ETA_FIN
        * (1.0 + yaw.DSIGMA)
        * (s_v / S)
        * cla_rad
    )
    cyr_fin = -2.0 * (yaw.fin_moment_arm() / B) * cyb_fin
    return float(cyb_fin), float(cyr_fin)


def stall_distribution(ny: int = 80, nx: int = 8):
    """Current symmetric VLM section-Cl screen at the 45 km/h requirement [D/E]."""
    target_cl = lift_coefficient(
        ARTICLE_V1_MASS_KG,
        speed_mps(STALL_SPEED_LIMIT_KMH),
    )
    grid = geom(
        B,
        S,
        TAPER,
        SWEEP_C4_DEG,
        TWIST_STRUCTURAL_CAP_DEG,
        ny=ny,
        nx=nx,
    )
    cl0, _, _, _ = solve(grid, 0.0)
    cl4, _, _, _ = solve(grid, 4.0)
    slope = (cl4 - cl0) / np.radians(4.0)
    alpha_deg = degrees((target_cl - cl0) / slope)
    _, _, strip_lift, _ = solve(grid, alpha_deg)
    strip_lift = strip_lift.reshape(ny, nx).sum(axis=1)
    dy = grid["dy"].reshape(ny, nx)[:, 0]
    chord = grid["chord"].reshape(ny, nx)[:, 0]
    y = grid["cps"][:, 1].reshape(ny, nx)[:, 0]
    local_cl = strip_lift / (0.5 * chord * dy)
    right = y > 0.0
    return (
        float(alpha_deg),
        y[right] / (B / 2.0),
        local_cl[right],
    )


def nearest_at(eta: np.ndarray, values: np.ndarray, target: float) -> tuple[float, float]:
    index = int(np.argmin(abs(eta - target)))
    return float(eta[index]), float(values[index])


def restoring_moment_nm(cnb_per_deg: float, beta_deg: float, speed_kmh: float) -> float:
    """Dimensional yaw moment from the current linear Cn_beta convention."""
    q = 0.5 * RHO_SL * speed_mps(speed_kmh) ** 2
    return q * S * B * cnb_per_deg * beta_deg


def main() -> None:
    if hasattr(__import__("sys").stdout, "reconfigure"):
        __import__("sys").stdout.reconfigure(encoding="utf-8", errors="replace")

    s_v = yaw.fin_area_for_target(0.0005)
    fin = yaw.fin_geometry(s_v)
    cnb_lo, cnb_hi = yaw.cnb_total_band(s_v)
    cnb_nom = 0.0005
    clean_published_best = yaw.cnb_fuselage(
        yaw.K_FUS_BAND[0], yaw.S_FS, yaw.fuselage_length()
    ) + yaw.CNB_W_BAND[1]
    clean_published_worst = yaw.cnb_fuselage(
        yaw.K_FUS_BAND[1], yaw.S_FS, yaw.fuselage_length()
    ) + yaw.CNB_W_BAND[0]
    clean_independent_best = yaw.cnb_fuselage(
        yaw.K_FUS_BAND[0], yaw.S_FS_BAND[0], yaw.fuselage_length()
    ) + yaw.CNB_W_BAND[1]
    clean_independent_worst = yaw.cnb_fuselage(
        yaw.K_FUS_BAND[1], yaw.S_FS_BAND[1], yaw.fuselage_length()
    ) + yaw.CNB_W_BAND[0]
    cla_lo, cla_hi = yaw.cla_fin_band(yaw.AR_FIN, yaw.FIN_SWEEP_DEG)

    print("=" * 86)
    print("NF DESIGN GUIDE 2024 AUDIT — PART 3 DIRECTIONAL/STABILITY EVIDENCE")
    print("All output is a screen, not manufacturing or flight release.")
    print("=" * 86)

    print("\n1. V1 FIN GEOMETRY AND LOW-REYNOLDS-NUMBER REGIME [D]/[E]")
    print(
        f"  total area={s_v*100:.4f} dm2; each span={fin.span_m*1000:.2f} mm; "
        f"root/MAC/tip chord={fin.root_chord_m*1000:.2f}/"
        f"{fin.mac_m*1000:.2f}/{fin.tip_chord_m*1000:.2f} mm"
    )
    print(
        f"  plate t/c root={100*yaw.FIN_ROOT_THICKNESS_M/fin.root_chord_m:.3f}%; "
        f"tip={100*yaw.FIN_TIP_THICKNESS_M/fin.tip_chord_m:.3f}% "
        "(external LE rod is not an aerodynamic coordinate definition)"
    )
    print(f"  assumed CLalpha={cla_lo:.5f}...{cla_hi:.5f}/deg")
    print("  speed    Re_root    Re_MAC    Re_tip")
    for speed_kmh in SPEEDS_KMH:
        root_re, mac_re, tip_re = fin_reynolds(speed_kmh, fin)
        print(
            f"  {speed_kmh:5.0f}   {root_re/1000:7.1f}k  {mac_re/1000:7.1f}k  "
            f"{tip_re/1000:7.1f}k"
        )

    print("\n  Linear fin-CL implication [I; not a finite-beta polar]")
    print("  beta       CL low       CL high")
    for beta in SIDESLIP_DEG:
        print(f"  {beta:4.0f} deg    {cla_lo*beta:8.3f}      {cla_hi*beta:8.3f}")

    print("\n2. STATIC Cn_beta BAND AND 45 km/h RESTORING MOMENT [D]/[E]")
    print(
        f"  CLEAN published={clean_published_worst:+.6f}..."
        f"{clean_published_best:+.6f}/deg; "
        f"V1a={cnb_lo:+.6f}...{cnb_hi:+.6f}/deg; nominal={cnb_nom:+.6f}/deg"
    )
    print(
        f"  CLEAN with independent S_fs and k_f corners="
        f"{clean_independent_worst:+.6f}...{clean_independent_best:+.6f}/deg [I]"
    )
    print("  beta       V1 low       V1 nominal       V1 high")
    for beta in (5.0, 10.0, 15.0):
        moments = (
            restoring_moment_nm(value, beta, 45.0)
            for value in (cnb_lo, cnb_nom, cnb_hi)
        )
        lo_m, nom_m, hi_m = moments
        print(f"  {beta:4.0f} deg   {lo_m:+10.4f}    {nom_m:+10.4f}    {hi_m:+10.4f} N m")

    print("\n3. PROPAGATING THE PUBLISHED Cn_beta BAND INTO THE REDUCED MODES [I]")
    print("  speed  Cn_beta case   classification    max Re(lambda)    wn       zeta")
    for speed_kmh in (45.0, 60.0, 95.0):
        for label, cnb in (("low", cnb_lo), ("nominal", cnb_nom), ("high", cnb_hi)):
            state, real_part, wn, zeta = mode_metrics(yaw_modes_at(cnb, speed_kmh))
            print(
                f"  {speed_kmh:5.0f}  {label:11s}  {state:10s}  "
                f"{real_part:+12.4f}/s  {wn:7.3f}  {zeta:+7.3f}"
            )

    clean_layout = solved_layout("clean")
    v1_layout = solved_layout("v1")
    clean_izz = clean_layout.inertia_kg_m2()[2][2]
    v1_izz = v1_layout.inertia_kg_m2()[2][2]
    print("\n4. CONFIGURATION-CONSISTENT MASS AND INERTIA [D]")
    print(
        f"  CLEAN mass/Izz={clean_layout.mass_g():.2f} g / {clean_izz:.6f} kg m2"
    )
    print(f"  V1    mass/Izz={v1_layout.mass_g():.2f} g / {v1_izz:.6f} kg m2")
    print(
        f"  V1 increase={100*(v1_layout.mass_g()/clean_layout.mass_g()-1):.2f}% mass, "
        f"{100*(v1_izz/clean_izz-1):.2f}% Izz"
    )

    cyb_fin, cyr_fin = fin_sideforce_derivatives(s_v)
    baseline_modes = yaw_modes_at(cnb_nom, 95.0)
    diagnostic_modes = yaw_modes_at(
        cnb_nom,
        95.0,
        cyb=-0.15 + cyb_fin,
        cyr=0.25 + cyr_fin,
    )
    print("\n5. OMITTED FIN SIDE-FORCE DERIVATIVE SENSITIVITY [I]")
    print(
        f"  geometry-only diagnostic increments: Cy_beta_fin={cyb_fin:+.4f}/rad; "
        f"Cy_r_fin={cyr_fin:+.4f}/rad"
    )
    print(f"  current-default V1 modes : {baseline_modes[0]:+.4f}, {baseline_modes[1]:+.4f}/s")
    print(f"  with diagnostic increments: {diagnostic_modes[0]:+.4f}, {diagnostic_modes[1]:+.4f}/s")
    print("  This spread is sensitivity only; it cannot replace coupled derivative data.")

    arm = yaw.fin_moment_arm()
    cla_nom_rad = yaw.helmbold_cla(yaw.AR_FIN, yaw.FIN_SWEEP_DEG)
    base_static = yaw.cnb_fin(s_v, arm, 0.5 * (cla_lo + cla_hi))
    base_damping = yaw.cnr_fin(s_v, arm, cla_nom_rad)
    arm_long = 1.2 * arm
    same_area_static = yaw.cnb_fin(s_v, arm_long, 0.5 * (cla_lo + cla_hi))
    same_area_damping = yaw.cnr_fin(s_v, arm_long, cla_nom_rad)
    resized_area = s_v / 1.2
    resized_static = yaw.cnb_fin(resized_area, arm_long, 0.5 * (cla_lo + cla_hi))
    resized_damping = yaw.cnr_fin(resized_area, arm_long, cla_nom_rad)
    print("\n6. STATIC-STABILITY VERSUS DAMPING LEVER-ARM LESSON [I]")
    print(
        f"  current arm={arm*1000:.2f} mm: fin Cn_beta={base_static:+.6f}/deg, "
        f"Cnr={base_damping:+.5f}/rad"
    )
    print(
        f"  +20% arm, same area: static x{same_area_static/base_static:.3f}; "
        f"damping x{same_area_damping/base_damping:.3f}"
    )
    print(
        f"  +20% arm, area /1.20: static x{resized_static/base_static:.3f}; "
        f"damping x{resized_damping/base_damping:.3f}"
    )

    alpha_deg, eta, local_cl = stall_distribution()
    peak_index = int(np.argmax(local_cl))
    peak_y = eta[peak_index] * B / 2.0
    peak_quarter_chord_x = peak_y * tan(radians(SWEEP_C4_DEG))
    peak_x_from_cg = peak_quarter_chord_x - yaw.cg_target()
    print("\n7. CURRENT SYMMETRIC STALL-DISTRIBUTION SCREEN [D on an E limit]")
    print(
        f"  required wing CL={lift_coefficient(ARTICLE_V1_MASS_KG, speed_mps(45.0)):.5f}; "
        f"VLM alpha={alpha_deg:.3f} deg; local peak={local_cl[peak_index]:.4f} "
        f"at eta={eta[peak_index]:.3f}"
    )
    print(
        f"  peak quarter-chord x={peak_quarter_chord_x*1000:+.2f} mm, "
        f"{peak_x_from_cg*1000:+.2f} mm relative to CG "
        "(negative is forward in the repository datum)"
    )
    print("  eta       local Cl     reserve to generic 0.65")
    for target in (0.50, 0.66, 0.80, 0.90, 0.95):
        station, section_cl = nearest_at(eta, local_cl, target)
        print(
            f"  {station:5.3f}      {section_cl:7.4f}       "
            f"{LOCAL_SECTION_CL_SCREEN-section_cl:+7.4f}"
        )
    print("  No beta, differential elevon, fin interference or local measured CLmax is included.")

    print("\n8. CROSSWIND/RUDDER SCREEN ENTERS AN UNVALIDATED FIN-BETA REGION [I]")
    cla_nom_deg = 0.5 * (cla_lo + cla_hi)
    cndr_nom = (
        yaw.ETA_RUD
        * cla_nom_deg
        * 0.32
        * (s_v / S)
        * (arm / B)
    )
    print("  crosswind at 45 km/h    beta     linear fin CL    rudder demand")
    for wind_kmh in (5.0, 10.0, 15.0, 20.0):
        beta = degrees(atan2(speed_mps(wind_kmh), speed_mps(45.0)))
        rudder, _ = yaw.rudder_delta_req(
            cnb_nom, cndr_nom, speed_mps(45.0), speed_mps(wind_kmh)
        )
        print(
            f"          {wind_kmh:5.1f} km/h      {beta:5.1f} deg      "
            f"{cla_nom_deg*beta:7.3f}          {rudder:7.2f} deg"
        )

    print("\n9. AUDIT REGRESSION CHECKS")
    checks = {
        "released V1 geometry is reproduced": (
            abs(s_v - 0.0614367) < 2e-6
            and abs(fin.span_m - 0.24786) < 2e-5
        ),
        "V1 lower Cn_beta corner remains negative": cnb_lo < 0.0,
        "CLEAN remains negative under independent declared corners": (
            clean_independent_best < 0.0
        ),
        "V1 nominal reduced mode is damped": mode_metrics(
            yaw_modes_at(cnb_nom, 95.0)
        )[0] == "DAMPED",
        "V1 lower-corner reduced mode is divergent": mode_metrics(
            yaw_modes_at(cnb_lo, 95.0)
        )[0] == "DIVERGENT",
        "V1 Izz exceeds the CLEAN value": v1_izz > clean_izz,
        "fin tip Reynolds number is below 100k at 45 km/h": (
            fin_reynolds(45.0, fin)[2] < 100_000
        ),
        "outer-wing generic reserve exceeds 10 percent at eta about 0.95": (
            (LOCAL_SECTION_CL_SCREEN - nearest_at(eta, local_cl, 0.95)[1])
            / LOCAL_SECTION_CL_SCREEN
            > 0.10
        ),
        "the published 20 km/h crosswind case exceeds beta 20 degrees": (
            degrees(atan2(speed_mps(20.0), speed_mps(45.0))) > 20.0
        ),
    }
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("  ALL PASS")


if __name__ == "__main__":
    main()
