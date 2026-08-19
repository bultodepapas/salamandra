#!/usr/bin/env python3
"""
Salamandra directional (yaw) stability — Cn_beta budget, centreline-fin sizing,
rudder-authority check, reduced 2-DOF yaw-mode estimate, and the mass/drag/stall cost
of the fin options. Full analysis thread: research/I-20 (2026-08-05).

Methods (published methodology, cited in I-20 §Sources):
  - Fin contribution  : CnB_v  = eta·(1+dσ/dβ)·(S_v/S)·(l_v/b)·CLα_v        [DATCOM/Roskam]
  - CLα_v             : Helmbold-Diederich low-AR lift curve, DATCOM form
  - Fuselage+boom     : CnB_f ≈ −k_f·(S_fs·l_f)/(S·b), k_f band               [Raymer/DATCOM]
  - Wing (FSW)        : small for AR 6; negative sign for forward sweep; band [E]
  - Rudder authority  : Cnδr  = −η_r·CLα_v·τ·(S_v/S)·(l_v/b)                  [DATCOM]
  - Yaw damping       : Cnr_v = −2·η·CLα_v·(S_v/S)·(l_v/b)² ; Cnr_w ≈ −CL/4   [DATCOM]
  - Yaw modes         : linear 2-DOF (β, r) eigenvalue check                  [E inputs]
  - Fin bending       : cantilever at V_STRUCTURAL, CN = 1.0, slipstream q ratio      [D]
  - Drag penalty      : flat-plate Cf + interference + slipstream             [Hoerner]
  - Stall impact      : V_stall ∝ sqrt(AUW)                                   [D]

Confidence rule: outputs are [D] where the method is published and inputs are
declared; band inputs are [E]. Validation cases run at the end and must PASS
before a modification is trusted (calculations/README.md).
"""
import sys

from dataclasses import dataclass
from functools import cache

import numpy as np

import drag_model
from balance_cg import cg_target, solve_reference_layout
from design_config import (
    ARTICLE_CLEAN_MASS_KG,
    ARTICLE_V1_MASS_KG,
    ASPECT_RATIO,
    CRUISE_SPEED_KMH,
    NU_SL,
    PETG_DENSITY_KG_M3,
    RHO_SL,
    STRUCTURAL_DESIGN_SPEED_KMH,
    SWEEP_C4_DEG,
    V1_FIN_MASS_CAP_KG,
    V1_FIN_SPAR_MASS_KG,
    B,
    S,
    lift_coefficient,
    speed_mps,
    stall_speed,
)

# --------------------------------------------------------------------------
# Inputs — reference geometry (design guide v0.5, §5/§7.6, OP-01) [D]/[M]
# --------------------------------------------------------------------------
ARW = ASPECT_RATIO      # aspect ratio
LAM_C4 = SWEEP_C4_DEG   # c/4 sweep, deg — negative = forward sweep (ADR-0040)

V_CRU = speed_mps(CRUISE_SPEED_KMH)
# NOT V_STRUCTURAL: this is the structural sizing speed (180 km/h), a different
# quantity from the article V_STRUCTURAL (160 km/h) that `divergence.py` uses.  The
# two modules previously both exported a module-level `V_STRUCTURAL` with different
# values, so grepping the symbol gave two answers.
V_STRUCTURAL = speed_mps(STRUCTURAL_DESIGN_SPEED_KMH)
RHO = RHO_SL
NU = NU_SL
AUW_REF = ARTICLE_CLEAN_MASS_KG
V1_FIN_CAP_G = V1_FIN_MASS_CAP_KG * 1000.0
CL_CRU = lift_coefficient(AUW_REF, V_CRU)

# Clean drag decomposition, from the SHARED polar.  These were local literals
# here, which made this the only module in the project honouring ADR-0009 while
# `launch_speed.py` used a single lumped coefficient.
SPAN_EFFICIENCY = drag_model.SPAN_EFFICIENCY
CD_PROFILE_CRUISE = drag_model.CD_PROFILE_CRUISE
PETG_DENSITY = PETG_DENSITY_KG_M3
FIN_SPAR_MASS_G = V1_FIN_SPAR_MASS_KG * 1000.0

# Fuselage + nose boom (guide §7.6, OP-01): length nose tip → rear pod end
REAR_POD_END = 0.265     # m from root c/4, rear pod end (guide 7.6) [E]


@cache
def fuselage_length():
    """Nose-support-to-rear-pod length [m], from the solved balance layout.

    Lazy for the same reason as elsewhere: module-scope solving made a broken
    upstream mass contract surface as an import crash instead of a failed check.
    """
    return REAR_POD_END - solve_reference_layout()["bay_fwd"]
S_FS = 0.040            # fuselage/boom projected side area (m²) [E, band]
S_FS_BAND = (0.032, 0.048)
K_FUS_BAND = (0.40, 0.96)   # DATCOM body factor band: 0.96 Raymer full-body,
                            # lower for slender boom (Munk-type bodies) [E]

# Wing contribution band (FSW, AR 6): small vs the body; negative sign [E]
CNB_W_BAND = (-0.00010, 0.00000)   # per degree

# Fin installation (V1 proposal, I-20): rear-pod extension behind the prop disk.
# One fin contract: the aerodynamic-centre station, the planform and the sweep
# live here and every consumer reads them.  They used to be repeated as bare
# literals inside `fin_area_for_target` and `main`, so a fin revision changed
# some consumers and not others.
FIN_AC_STATION_M = 0.285   # fin AC, m aft of the root c/4 [E]
AR_FIN = 3.0               # fin aspect ratio [E]
FIN_TAPER = 0.6            # fin taper ratio [E]

# The V1a concept has a vertical trailing edge.  For a trapezoid this fixes the
# quarter-chord sweep from AR and taper; keeping a separate 12 degree literal
# made the aerodynamic model disagree with the generated drawing (7.125 deg).
FIN_SWEEP_DEG = float(np.degrees(np.arctan(
    1.5 / AR_FIN * (1.0 - FIN_TAPER) / (1.0 + FIN_TAPER)
)))

FIN_ROOT_THICKNESS_M = 0.0030   # maximum plate thickness at root [E]
FIN_TIP_THICKNESS_M = 0.0015    # maximum plate thickness at tip [E]
FIN_TE_THICKNESS_M = 0.0008     # printable trailing edge [E]
FIN_SPAR_DIAMETER_M = 0.0030    # aluminium rod forming the LE nose [D]/[E]
FIN_SPAR_SEAT_DIAMETER_M = 0.0032  # open rear-facing C-seat, not enclosed [I]
FIN_ROOT_Z_M = 0.014            # carrier/fin vertical interface [I]


@cache
def fin_moment_arm():
    """CG-to-fin-AC lever arm [m], from the re-derived CG target."""
    return FIN_AC_STATION_M - cg_target()
ETA_FIN_POWER_OFF = 1.00   # free-stream reference, propeller not energising fin [E]
ETA_FIN_POWER_ON = 1.25    # whole-fin equivalent q ratio used by released screen [E]
ETA_FIN = ETA_FIN_POWER_ON # compatibility alias; report both power states below
DSIGMA = 0.05           # sidewash factor (1+dσ/dβ) ≈ 1.05, centerline fin [E]
ETA_RUD = 1.15          # rudder q-ratio [E]
CLA_RE_FAC = (0.85, 1.00)  # low-Re lift-curve reduction on Helmbold [E]
TAU_BAND = (0.25, 0.40)    # rudder flap effectiveness, ~30 % chord, low Re [E]

# Yaw inertia.  DERIVED from the released three-dimensional mass model, not
# declared here.  This module used to carry a standalone I_z = 0.28 kg m2 [E]
# with a (0.23, 0.33) band, while `equipment_layout` computed 0.159 kg m2 from
# the same aircraft: a factor 1.76 disagreement, with the computed value
# outside the declared band and nothing cross-checking the two.  The published
# 2-DOF yaw mode is proportional to 1/sqrt(I_z), so the discrepancy was a 33 %
# error in the reported natural frequency.
#
# The remaining uncertainty is the idealisation itself: `equipment_layout`
# represents every part as an oriented cuboid, which captures the spanwise mass
# stations but not the mass distribution inside each shell.  That is carried as
# a declared band and PROPAGATED (see `yaw_mode_band`), instead of being folded
# into a single quoted figure.
IZ_MODEL_UNCERTAINTY = 0.15      # +/- fraction on the cuboid idealisation [E]


@cache
def yaw_inertia():
    """Aircraft yaw inertia I_zz [kg m2] from the solved 3-D mass model [D]."""
    import equipment_layout
    layout, _ = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("clean"))
    return layout.inertia_kg_m2()[2][2]


def yaw_inertia_band():
    """Declared I_zz band [kg m2] from the cuboid-idealisation uncertainty."""
    nominal = yaw_inertia()
    return (nominal * (1.0 - IZ_MODEL_UNCERTAINTY),
            nominal * (1.0 + IZ_MODEL_UNCERTAINTY))

# In-service reference (I-20, [M]): TBS Mojito — FSW 1300 mm, FIXED vertical
# stabilizer on the motor mount, 2 elevon servos only, no rudder servo
# (TBS product page, manual, official INAV CLI — primary sources).

# --------------------------------------------------------------------------
# Methods
# --------------------------------------------------------------------------
DEG = 180.0 / np.pi


def helmbold_cla(AR, sweep_deg, eta=0.95):
    """Low-AR lift-curve slope with sweep (DATCOM/Helmbold-Diederich), 1/rad."""
    b2 = 1.0                       # β² = 1 − M², subsonic
    lam = np.radians(sweep_deg)
    return (2.0 * np.pi * AR / (2.0 + np.sqrt(AR**2 * b2 / eta**2 *
                                              (1.0 + np.tan(lam)**2) + 4.0)))


def cla_fin_band(AR, sweep_deg):
    """Fin CLα band [1/deg] at Re ≈ 1.5–3e5 (Helmbold × low-Re factor)."""
    lo = helmbold_cla(AR, sweep_deg) * CLA_RE_FAC[0]
    hi = helmbold_cla(AR, sweep_deg) * CLA_RE_FAC[1]
    return lo / DEG, hi / DEG


def cnb_fuselage(k_f, S_fs, l_f, S_ref=S, b_ref=B):
    """Raymer/DATCOM body contribution, per degree (negative = destabilizing)."""
    return -k_f * S_fs * l_f / (S_ref * b_ref) / DEG


def cnb_fin(S_v, l_v, cla, eta=ETA_FIN, sw=1.0 + DSIGMA):
    """DATCOM fin contribution, per degree (positive = stabilizing)."""
    return eta * sw * (S_v / S) * (l_v / B) * cla


def cnb_total_band(S_v, eta=ETA_FIN):
    """Independent-corner Cnβ band for one fin area and q-ratio.

    The former implementation paired favourable and unfavourable inputs, which
    did not bound the independent uncertainty space.  Directional stability is
    monotonic in every term here, so the true extrema are explicit.
    """
    cla_lo, cla_hi = cla_fin_band(AR_FIN, FIN_SWEEP_DEG)
    low = (
        cnb_fin(S_v, fin_moment_arm(), cla_lo, eta=eta)
        + cnb_fuselage(K_FUS_BAND[1], S_FS_BAND[1], fuselage_length())
        + CNB_W_BAND[0]
    )
    high = (
        cnb_fin(S_v, fin_moment_arm(), cla_hi, eta=eta)
        + cnb_fuselage(K_FUS_BAND[0], S_FS_BAND[0], fuselage_length())
        + CNB_W_BAND[1]
    )
    return low, high


def fin_area_for_target(target, l_v=None):
    """Fin area that closes a nominal Cn_beta target with current geometry.

    ``l_v=None`` resolves the released lever arm at call time; the fin lift
    slope comes from the fin contract above, not from repeated literals.
    """
    if l_v is None:
        l_v = fin_moment_arm()
    cnb_fus_nom = cnb_fuselage(0.70, S_FS, fuselage_length())
    cla_nom = sum(cla_fin_band(AR_FIN, FIN_SWEEP_DEG)) / 2.0
    wing_mean = sum(CNB_W_BAND) / 2.0
    need = target - cnb_fus_nom - wing_mean
    return need / (ETA_FIN * (1.0 + DSIGMA) * (1.0 / S) *
                   (l_v / B) * cla_nom)


def cnr_fin(S_v, l_v, cla_rad):
    """Fin yaw damping, 1/rad (negative = damping)."""
    return -2.0 * ETA_FIN * cla_rad * (S_v / S) * (l_v / B) ** 2


def cnr_wing():
    """Wing yaw damping, 1/rad: −CL/4 (DATCOM), [E]."""
    return -CL_CRU / 4.0


@dataclass(frozen=True)
class FinGeometry:
    """Single-source trapezoidal V1 fin planform, SI units.

    The vertical trailing edge is an explicit provisional packaging decision.
    All consumers use these vertices, so the aerodynamic sweep, AC station and
    generated SVG cannot silently diverge.
    """

    area_m2: float
    span_m: float
    root_chord_m: float
    tip_chord_m: float
    centroid_height_m: float
    mac_m: float
    ac_x_m: float
    root_le_x_m: float
    root_te_x_m: float
    tip_le_x_m: float
    tip_te_x_m: float
    quarter_chord_sweep_deg: float


def fin_geometry(S_v, b_v=None, ac_x=FIN_AC_STATION_M):
    """Return the complete vertical-TE trapezoidal fin geometry."""
    if b_v is None:
        b_v = np.sqrt(S_v * AR_FIN)
    c_mean = S_v / b_v
    c_r = 2.0 * c_mean / (1.0 + FIN_TAPER)
    c_t = FIN_TAPER * c_r
    h_c = (b_v / 3.0) * (c_r + 2.0 * c_t) / (c_r + c_t)
    mac = c_r + (c_t - c_r) * h_c / b_v
    trailing_edge_x = ac_x + 0.75 * mac
    root_le_x = trailing_edge_x - c_r
    tip_le_x = trailing_edge_x - c_t
    root_qc_x = root_le_x + 0.25 * c_r
    tip_qc_x = tip_le_x + 0.25 * c_t
    sweep = float(np.degrees(np.arctan2(tip_qc_x - root_qc_x, b_v)))
    return FinGeometry(
        area_m2=S_v,
        span_m=b_v,
        root_chord_m=c_r,
        tip_chord_m=c_t,
        centroid_height_m=h_c,
        mac_m=mac,
        ac_x_m=ac_x,
        root_le_x_m=root_le_x,
        root_te_x_m=trailing_edge_x,
        tip_le_x_m=tip_le_x,
        tip_te_x_m=trailing_edge_x,
        quarter_chord_sweep_deg=sweep,
    )


def fin_shell_mount_mass_band(S_v):
    """PETG fin shell plus 15 % mount allowance, excluding the spar [g]."""
    m_lo = S_v * 0.0012 * PETG_DENSITY * 1.15
    m_hi = S_v * 0.0020 * PETG_DENSITY * 1.15
    return 1000.0 * m_lo, 1000.0 * m_hi


def fin_mass_band(S_v):
    """Complete fin assembly band [g], including the mandatory aluminium spar."""
    lo, hi = fin_shell_mount_mass_band(S_v)
    return lo + FIN_SPAR_MASS_G, hi + FIN_SPAR_MASS_G


def fin_drag(S_v):
    """ΔCD0 of the fin at cruise: Cf (printed, Re 1.5–3e5) + interference + wake."""
    c_ref = fin_geometry(S_v).mac_m                # actual trapezoidal MAC
    re = V_CRU * c_ref / NU
    cf = 0.005 + 0.0011 / np.sqrt(re / 1e5)        # turbulent flat plate [E]
    swet = 2.0 * S_v
    dcd0 = ETA_FIN * 1.35 * cf * swet / S          # k_int 1.35 [E]
    return dcd0, cf


def stall_speed_kmh(auw):
    """Stall speed from the shared wing CLmax contract."""
    return stall_speed(auw) * 3.6


def yaw_state_matrix(cnb_per_deg, cnr, cyb=-0.15, cyr=0.25,
                     mass=None, iz=None, speed=None):
    """Dimensional 2-DOF lateral-directional state matrix for (beta, r).

    Cnr and Cyr are derivatives with respect to normalized yaw rate r*b/(2V).
    The 1/(2V) conversion is therefore mandatory in Nr and Yr. Revision 2
    corrects the former omission of this factor.

    ``mass``, ``iz`` and ``speed`` are ``None`` sentinels, not module constants
    bound as defaults: a default argument freezes its value at definition time,
    so reassigning the module constant to run a sensitivity study silently had
    no effect at all.
    """
    if mass is None:
        mass = AUW_REF
    if iz is None:
        iz = yaw_inertia()
    if speed is None:
        speed = V_CRU
    if mass <= 0.0 or iz <= 0.0 or speed <= 0.0:
        raise ValueError("mass, yaw inertia and speed must be positive")
    q = 0.5 * RHO * speed**2
    y_beta = q * S * cyb
    y_r = q * S * B * cyr / (2.0 * speed)
    n_beta = q * S * B * cnb_per_deg * DEG
    n_r = q * S * B**2 * cnr / (2.0 * speed)
    return np.array([
        [y_beta / (mass * speed), -1.0 + y_r / (mass * speed)],
        [n_beta / iz, n_r / iz],
    ])


def yaw_modes(cnb_per_deg, cnr, cyb=-0.15, cyr=0.25,
              mass=None, iz=None, speed=None):
    """Simplified 2-DOF (beta, r) eigenvalues [1/s].

    [E] inputs: Cyβ ≈ −0.15 (finless), Cyr ≈ +0.25; I_z band. The finless
    configuration with Cnβ < 0 shows a divergent real mode (time constant
    reported); the finned configuration shows a damped oscillatory pair. This
    reduced pair is not a full Dutch-roll identification: roll rate and bank
    angle are omitted and remain in the E-series flight-test programme.
    """
    return np.linalg.eigvals(
        yaw_state_matrix(cnb_per_deg, cnr, cyb, cyr, mass, iz, speed))


def yaw_mode_band(cnb_per_deg, cnr, cyb=-0.15, cyr=0.25):
    """Eigenvalues across the declared I_zz band: (low, nominal, high).

    The band used to be declared and never referenced anywhere, and `yaw_modes`
    had no inertia parameter at all, so it could not have been propagated even
    deliberately.
    """
    low, high = yaw_inertia_band()
    return tuple(yaw_modes(cnb_per_deg, cnr, cyb, cyr, iz=iz)
                 for iz in (low, yaw_inertia(), high))


def rudder_delta_req(cnb_total, cndr, v_air, v_cw):
    """Rudder deflection (°) to hold a steady sideslip in a crosswind."""
    beta = np.degrees(np.arctan2(v_cw, v_air))
    return beta * cnb_total / cndr, beta


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 74)
    print("SALAMANDRA — DIRECTIONAL STABILITY (Cn_beta) AND FIN OPTIONS")
    print("Configuration: FSW 1300 mm · nose boom · pusher · elevons only")
    print("Methods: DATCOM/Roskam/Raymer/Helmbold/Hoerner [M]; inputs [E]")
    print("=" * 74)

    # ---- 1. Finless baseline: Cn_beta budget ----
    cnb_f = cnb_fuselage(K_FUS_BAND[1], S_FS, fuselage_length())          # worst (0.96)
    cnb_f_lo = cnb_fuselage(K_FUS_BAND[0], S_FS, fuselage_length())       # best (0.40)
    print("\n1. FINLESS BASELINE — Cn_beta budget (/deg)")
    print(f"   Body (k=0.40 best / 0.96 worst): {cnb_f_lo:+.5f} / {cnb_f:+.5f}"
          f"  (S_fs {S_FS:.3f} m², l_f {fuselage_length():.3f} m)")
    for tag, w in [("wing FSW band", CNB_W_BAND[0]), ("wing best", CNB_W_BAND[1])]:
        print(f"   Wing {tag:12s}: {w:+.5f}")
    WING_MEAN = (CNB_W_BAND[0] + CNB_W_BAND[1]) / 2.0
    cnb_no_lo = cnb_f_lo + CNB_W_BAND[1]
    cnb_no_hi = cnb_f + CNB_W_BAND[0]
    print(f"   TOTAL no fin  : {cnb_no_lo:+.5f} … {cnb_no_hi:+.5f} /deg  "
          f"=> NEGATIVE (statically unstable) [E]")
    lam = yaw_modes(cnb_no_hi, cnr_wing())
    print(f"   2-DOF yaw modes (worst): λ = {lam[0]:+.3f}, {lam[1]:+.3f} 1/s"
          f"  (divergence τ ≈ {1.0/max(lam.real):.2f} s [E])")

    # ---- 2. Fin sizing for stability tiers ----
    print("\n2. FIN SIZING (centreline, rear-pod extension, l_v = %.0f mm)" % (fin_moment_arm()*1000))
    tiers = [
        ("V1a — marginal-stable (nominal ≥ 0.0005/deg)", 0.0005),
        ("V1b — higher powered nominal margin (≥ 0.0010/deg)", 0.0010),
    ]
    # solve S_v at band centre, check band extremes
    tier_areas = []
    for tag, target in tiers:
        # nominal: k_fus = 0.70, S_fs centre, CLα band centre
        cnb_fus_nom = cnb_fuselage(0.70, S_FS, fuselage_length())
        cla_nom = sum(cla_fin_band(AR_FIN, FIN_SWEEP_DEG)) / 2.0
        S_v = fin_area_for_target(target)
        tier_areas.append(S_v)
        # Independent-corner propagation; power-off is reported separately.
        cnb_lo, cnb_hi = cnb_total_band(S_v, eta=ETA_FIN_POWER_ON)
        cnb_off_lo, cnb_off_hi = cnb_total_band(S_v, eta=ETA_FIN_POWER_OFF)
        fin = fin_geometry(S_v)
        b_v = fin.span_m
        c_r = fin.root_chord_m
        c_t = fin.tip_chord_m
        h_c = fin.centroid_height_m
        m_lo, m_hi = fin_mass_band(S_v)
        dcd0, _ = fin_drag(S_v)
        cd_tot = sum(drag_model.clean_cd(CL_CRU))
        dwhkm = 100.0 * dcd0 / cd_tot
        auw_new = AUW_REF + (m_lo + m_hi) / 2.0 / 1000.0
        vs = stall_speed_kmh(auw_new)
        V_v = S_v * fin_moment_arm() / (S * B)
        print(f"\n   {tag}")
        print(f"   S_v = {S_v*100:.2f} dm² · b_v = {b_v*1000:.0f} mm · "
              f"c_r = {c_r*1000:.0f} / c_t = {c_t*1000:.0f} mm · AR_v ≈ {AR_FIN:.1f}")
        print(f"   Planform        : vertical TE · Λc/4 = "
              f"{fin.quarter_chord_sweep_deg:.3f}° · MAC {fin.mac_m*1000:.1f} mm")
        print(f"   Cn_beta power-on  : {cnb_lo:+.5f} … {cnb_hi:+.5f} /deg "
              f"(nominal ≈ {cnb_fin(S_v,fin_moment_arm(),cla_nom)+cnb_fus_nom+WING_MEAN:+.5f})")
        print(f"   Cn_beta power-off : {cnb_off_lo:+.5f} … {cnb_off_hi:+.5f} /deg [E]")
        print(f"   Fin Cn_beta     : {cnb_fin(S_v,fin_moment_arm(),cla_nom):+.5f} /deg")
        print(f"   Volume coeff V_v = {V_v:.3f} (tailless practice ≈ 0.02–0.05 [I])")
        print(f"   Mass complete   : {m_lo:.0f}–{m_hi:.0f} g "
              f"(1.2–2.0 mm PETG + mount + {FIN_SPAR_MASS_G:.1f} g spar)")
        print(f"   ΔCD0            : +{dcd0:.4f}  →  +{dwhkm:.1f} % drag / "
              f"Wh/km ≈ {1.15*(1+dwhkm/100):.2f} [E]")
        print(f"   AUW +{1000*(auw_new-AUW_REF):.0f} g → V_stall ≈ {vs:.1f} km/h "
              f"(limit 45, OP-24 lever applies)")
        if target == 0.0005:
            selected_auw = AUW_REF + V1_FIN_CAP_G / 1000.0
            print(f"   V1 allocation   : {V1_FIN_CAP_G:.2f} g cap → "
                  f"AUW {selected_auw*1000:.1f} g / V_stall "
                  f"{stall_speed_kmh(selected_auw):.1f} km/h")
            print(f"   F2 mass gap     : current analytical lower assembly "
                  f"{m_lo:.2f} g exceeds the cap by {m_lo-V1_FIN_CAP_G:.2f} g")

    # ---- 3. Recommended geometry (V1a) — structural check ----
    S_v = tier_areas[0]
    fin = fin_geometry(S_v)
    b_v = fin.span_m
    c_r = fin.root_chord_m
    c_t = fin.tip_chord_m
    h_c = fin.centroid_height_m
    q_ne = 0.5 * RHO * V_STRUCTURAL**2
    F = q_ne * S_v * 1.0 * ETA_FIN          # CN = 1.0, slipstream
    M = F * h_c
    print("\n3. STRUCTURAL CHECK, recommended V1a fin at V_STRUCTURAL (cantilever)")
    print(f"   F = {F:.1f} N at centroid h = {h_c*1000:.0f} mm → M = {M:.2f} N·m")
    for t in (0.0015, 0.0025, 0.0030):
        I_pl = c_r * t**3 / 12.0
        sig = M * (t / 2.0) / I_pl / 1e6
        print(f"   root t = {t*1000:.1f} mm → σ = {sig:5.1f} MPa "
              f"(PETG yield ≈ 50 MPa, FS {50.0/sig:.2f})")
    print("   => root t ≥ 3.0 mm solid for FS ≥ 1.5 without crediting the Al spar")
    om = 3.516 * np.sqrt(2.0e9 * (c_r*0.0025**3/12.0) /
                         (PETG_DENSITY * c_r*0.0025 * b_v**4))
    print(f"   First bending mode ≈ {om/(2*np.pi):.1f} Hz — flutter/strength "
          f"check in F2 [E]")

    # ---- 4. Rudder authority (movable option) ----
    print("\n4. MOVABLE RUDDER OPTION — authority vs mission need")
    cla_nom = sum(cla_fin_band(AR_FIN, FIN_SWEEP_DEG)) / 2.0
    for tau in (TAU_BAND[0], 0.32, TAU_BAND[1]):
        cndr = ETA_RUD * cla_nom * tau * (S_v / S) * (fin_moment_arm() / B)
        print(f"   τ = {tau:.2f} → |Cnδr| = {cndr:.5f} /deg")
    cndr_nom = ETA_RUD * cla_nom * 0.32 * (S_v / S) * (fin_moment_arm() / B)
    cnb_v1 = cnb_fin(S_v, fin_moment_arm(), cla_nom) + cnb_fuselage(0.70, S_FS, fuselage_length()) + WING_MEAN
    print(f"   Steady-sideslip rudder demand (Cnβ = {cnb_v1:+.5f}/deg, "
          f"|Cnδr| = {cndr_nom:.5f}/deg):")
    for v_air, v_cw, name in [(12.5, 5.56, "stall 45 + 20 km/h x-wind"),
                              (12.5, 4.17, "stall 45 + 15 km/h x-wind"),
                              (26.4, 5.56, "cruise 95 + 20 km/h x-wind")]:
        dr, beta = rudder_delta_req(cnb_v1, cndr_nom, v_air, v_cw)
        print(f"     {name:34s}: β = {beta:4.1f}° → δr = {dr:6.1f}°  "
              f"(avail ±20°: {'NO — cannot hold' if dr > 20 else 'feasible'})")
    d_el = 0.05 * 0.028 * 0.42 / (S * B) / 20.0
    print(f"   Differential elevon (no-fin yaw control) ≈ {d_el:.6f} /deg "
          f"— {cndr_nom/d_el:.0f}× weaker than a rudder [E]")

    # ---- 5. Yaw damping ----
    print("\n5. YAW DAMPING Cnr (1/rad)")
    cnr_w = cnr_wing()
    cnr_f = cnr_fin(S_v, fin_moment_arm(), helmbold_cla(AR_FIN, FIN_SWEEP_DEG))
    print(f"   Wing ≈ {cnr_w:.3f} ; fin V1a ≈ {cnr_f:.3f} → total ≈ "
          f"{cnr_w+cnr_f:.3f} (damping doubled)")
    lam_f = yaw_modes(0.0005, cnr_w + cnr_f)
    print(f"   V1a 2-DOF modes: λ = {lam_f[0]:+.3f}, {lam_f[1]:+.3f} 1/s "
          f"(stable decay τ ≈ {1.0/abs(lam_f.real.max()):.1f} s) [E]")
    iz_lo, iz_hi = yaw_inertia_band()
    print(f"   I_zz = {yaw_inertia():.4f} kg·m² [D] from the 3-D mass model; "
          f"band {iz_lo:.4f}–{iz_hi:.4f} (±{IZ_MODEL_UNCERTAINTY*100:.0f} % "
          f"cuboid idealisation [E])")
    for tag, band_modes in zip(("I_zz low ", "I_zz nom ", "I_zz high"),
                               yaw_mode_band(0.0005, cnr_w + cnr_f)):
        root = band_modes[0]
        omega = abs(root)
        print(f"     {tag}: λ = {root:+.3f} 1/s · ω_n = {omega:.3f} rad/s · "
              f"ζ = {-root.real/omega:.3f}")

    # ---- 6. Validation cases ----
    print("\n6. VALIDATION CASES")
    ok = True
    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"   [{'PASS' if cond else 'FAIL'}] {name}")
    c1 = helmbold_cla(4.0, 0.0)
    check(f"Helmbold AR 4, Λ=0, η=0.95 = 3.7729/rad (got {c1:.4f})",
          abs(c1 - 3.7729) / 3.7729 < 0.005)
    c2 = cnb_fin(0.1 * S, 0.3 * B, 0.06, eta=1.0, sw=1.0)
    check(f"Fin ref (η=sw=1): 0.10·0.30·0.06 = 0.00180/deg (got {c2:.5f})",
          abs(c2 - 0.0018) < 1e-5)
    c3 = cnb_fuselage(0.96, 2.0, 7.5, S_ref=16.2, b_ref=11.0)  # C172-like
    check(f"Raymer C172-like body: −0.0012…−0.0016/deg (got {c3:+.5f})",
          -0.0016 < c3 < -0.0012)
    cnb_v1b = cnb_fin(fin_area_for_target(0.0010), fin_moment_arm(), cla_nom) + \
        cnb_fuselage(0.70, S_FS, fuselage_length()) + WING_MEAN
    check(f"V1b nominal Cnβ = +0.0010/deg (got {cnb_v1b:+.5f})",
          abs(cnb_v1b - 0.0010) < 1e-8)
    check(f"Finless nominal Cnβ < 0 ({cnb_fuselage(0.70,S_FS,fuselage_length()):+.5f})",
          cnb_fuselage(0.70, S_FS, fuselage_length()) < 0.0)
    cndr_ref = ETA_RUD * 0.06 * 0.30 * 0.10 * 0.30
    check(f"Cnδr ref (τ 0.30, η 1.15): {cndr_ref:.6f}/deg",
          abs(cndr_ref - 0.000621) < 1e-5)
    i_root_3 = c_r * 0.003 ** 3 / 12.0
    sig_root_3 = M * 0.0015 / i_root_3
    check(f"V1a 3.0 mm root FS >= 1.5 without spar credit "
          f"(got {50e6/sig_root_3:.2f})", 50e6 / sig_root_3 >= 1.5)
    check("V1a vertical-TE geometry reproduces the aerodynamic sweep",
          abs(fin.quarter_chord_sweep_deg - FIN_SWEEP_DEG) < 1e-12)
    check("V1a geometry reproduces area, AR, taper and AC",
          abs(0.5 * (fin.root_chord_m + fin.tip_chord_m) * fin.span_m
              - fin.area_m2) < 1e-12
          and abs(fin.span_m**2 / fin.area_m2 - AR_FIN) < 1e-12
          and abs(fin.tip_chord_m / fin.root_chord_m - FIN_TAPER) < 1e-12
          and abs(
              fin.root_te_x_m - 0.75 * fin.mac_m - fin.ac_x_m
          ) < 1e-12)
    check("independent-corner Cn_beta band is ordered and contains nominal",
          cnb_total_band(S_v)[0] < cnb_v1 < cnb_total_band(S_v)[1])
    check("power-off is no more stabilizing than the power-on screen",
          cnb_total_band(S_v, ETA_FIN_POWER_OFF)[0]
          <= cnb_total_band(S_v, ETA_FIN_POWER_ON)[0])
    v1a_lo = fin_mass_band(tier_areas[0])[0]
    check(f"C32 complete-fin mass gap is explicit and 5.5--6.2 g "
          f"({V1_FIN_CAP_G:.2f} cap vs {v1a_lo:.2f} g lower assembly)",
          5.5 <= v1a_lo - V1_FIN_CAP_G <= 6.2)
    check("V1 analytical lower assembly matches the shared mass contract within 0.2 g",
          abs(AUW_REF + v1a_lo / 1000.0 - ARTICLE_V1_MASS_KG) < 2e-4)
    finless_modes = yaw_modes(cnb_no_hi, cnr_wing())
    finned_modes = yaw_modes(0.0005, cnr_w + cnr_f)
    check("corrected finless 2-DOF model has one divergent mode",
          max(finless_modes.real) > 0.0)
    check("corrected V1a reduced 2-DOF oscillatory pair is damped",
          np.all(finned_modes.real < 0.0) and np.any(abs(finned_modes.imag) > 0.0))
    check("yaw inertia comes from the 3-D mass model, not a local estimate",
          0.10 < yaw_inertia() < 0.25)
    check("declared I_zz band is propagated and the mode stays damped "
          "across it",
          all(np.all(m.real < 0.0)
              for m in yaw_mode_band(0.0005, cnr_w + cnr_f)))
    band_modes = yaw_mode_band(0.0005, cnr_w + cnr_f)
    check("I_zz band orders the natural frequency monotonically",
          abs(band_modes[0][0]) > abs(band_modes[1][0]) > abs(band_modes[2][0]))
    a_ref = yaw_state_matrix(0.0005, -0.10)
    q_ref = 0.5 * RHO * V_CRU**2
    expected_nr = q_ref * S * B**2 * -0.10 / (2.0 * V_CRU * yaw_inertia())
    check("Cnr dimensionalization includes 1/(2V)",
          abs(a_ref[1, 1] - expected_nr) < 1e-12)
    print(f"\n   VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
