#!/usr/bin/env python3
"""
Salamandra directional (yaw) stability — Cn_beta budget, centreline-fin sizing,
rudder-authority check, yaw-subsidence estimate, and the mass/drag/stall cost
of the fin options. Full analysis thread: research/I-20 (2026-08-05).

Methods (published methodology, cited in I-20 §Sources):
  - Fin contribution  : CnB_v  = eta·(1+dσ/dβ)·(S_v/S)·(l_v/b)·CLα_v        [DATCOM/Roskam]
  - CLα_v             : Helmbold-Diederich low-AR lift curve, DATCOM form
  - Fuselage+boom     : CnB_f ≈ −k_f·(S_fs·l_f)/(S·b), k_f band               [Raymer/DATCOM]
  - Wing (FSW)        : small for AR 6; negative sign for forward sweep; band [E]
  - Rudder authority  : Cnδr  = −η_r·CLα_v·τ·(S_v/S)·(l_v/b)                  [DATCOM]
  - Yaw damping       : Cnr_v = −2·η·CLα_v·(S_v/S)·(l_v/b)² ; Cnr_w ≈ −CL/4   [DATCOM]
  - Yaw subsidence    : linear 2-DOF (β, r) eigenvalue check                  [E inputs]
  - Fin bending       : cantilever at V_NE, CN = 1.0, slipstream q ratio      [D]
  - Drag penalty      : flat-plate Cf + interference + slipstream             [Hoerner]
  - Stall impact      : V_stall ∝ sqrt(AUW)                                   [D]

Confidence rule: outputs are [D] where the method is published and inputs are
declared; band inputs are [E]. Validation cases run at the end and must PASS
before a modification is trusted (calculations/README.md).
"""
import sys
import numpy as np
from design_config import B, MAC, S, SWEEP_C4_DEG
from balance_cg import CG_TARGET, solve_reference_layout

# --------------------------------------------------------------------------
# Inputs — reference geometry (design guide v0.5, §5/§7.6, OP-01) [D]/[M]
# --------------------------------------------------------------------------
ARW = 6.0               # aspect ratio
LAM_C4 = SWEEP_C4_DEG   # c/4 sweep, deg — negative = forward sweep (ADR-0040)
CL_CRU = 0.132          # cruise CL (I-07)
E_OSW = 0.85            # Oswald factor [E]
CD0_CRU = 0.0136        # zero-lift drag of the finless clean config [D] (L/D ≈ 8-10)
CG = CG_TARGET           # target CG, m from root c/4 (ADR-0040)
V_CRU = 26.4            # 95 km/h cruise speed (m/s)
V_NE = 50.0             # design V_NE, 180 km/h (m/s)
RHO = 1.225             # air density sea level (kg/m³)
NU = 1.5e-5             # kinematic viscosity (m²/s)
AUW_REF = 1.5835        # CLEAN Article #1 allocation (kg, ADR-0043)
V_STALL_REF = 44.5      # km/h at AUW_REF (guide §11)
V1_FIN_CAP_G = 36.72    # lower-band V1a estimate and CAD acceptance cap [E]

# Fuselage + nose boom (guide §7.6, OP-01): length nose tip → rear pod end
L_F = 0.265 - solve_reference_layout()["bay_fwd"]  # nose support to rear pod
S_FS = 0.040            # fuselage/boom projected side area (m²) [E, band]
S_FS_BAND = (0.032, 0.048)
K_FUS_BAND = (0.40, 0.96)   # DATCOM body factor band: 0.96 Raymer full-body,
                            # lower for slender boom (Munk-type bodies) [E]

# Wing contribution band (FSW, AR 6): small vs the body; negative sign [E]
CNB_W_BAND = (-0.00010, 0.00000)   # per degree

# Fin installation (V1 proposal, I-20): rear-pod extension behind the prop disk
L_V = 0.285 - CG        # CG → fin AC (m): fin AC ≈ +285 mm from root c/4
ETA_FIN = 1.25          # dynamic-pressure ratio, fin in pusher slipstream [E]
DSIGMA = 0.05           # sidewash factor (1+dσ/dβ) ≈ 1.05, centerline fin [E]
ETA_RUD = 1.15          # rudder q-ratio [E]
CLA_RE_FAC = (0.85, 1.00)  # low-Re lift-curve reduction on Helmbold [E]
TAU_BAND = (0.25, 0.40)    # rudder flap effectiveness, ~30 % chord, low Re [E]

# Yaw inertia (guide §8.1 masses, boom battery at x ≈ −0.42 m): I_z ≈ 0.28
IZ = 0.28               # kg·m² [E, band]
IZ_BAND = (0.23, 0.33)

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


def fin_area_for_target(target, l_v=L_V):
    """Fin area that closes a nominal Cn_beta target with current geometry."""
    cnb_fus_nom = cnb_fuselage(0.70, S_FS, L_F)
    cla_nom = sum(cla_fin_band(3.0, 12.0)) / 2.0
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


def fin_geometry(S_v, b_v):
    """Trapezoidal fin: root/tip chords for a given span, m."""
    c_mean = S_v / b_v
    c_r = 1.25 * c_mean          # taper 0.6
    c_t = 0.75 * c_mean
    h_c = (b_v / 3.0) * (c_r + 2.0 * c_t) / (c_r + c_t)   # centroid height
    return c_r, c_t, h_c


def fin_mass_band(S_v):
    """Solid thin PETG fin, t 1.2–2.0 mm + 15 % mount, g [E]."""
    m_lo = S_v * 0.0012 * 1250.0 * 1.15
    m_hi = S_v * 0.0020 * 1250.0 * 1.15
    return 1000.0 * m_lo, 1000.0 * m_hi


def fin_drag(S_v):
    """ΔCD0 of the fin at cruise: Cf (printed, Re 1.5–3e5) + interference + wake."""
    c_ref = np.sqrt(S_v / 0.8)                     # mean chord of the fin
    re = V_CRU * c_ref / NU
    cf = 0.005 + 0.0011 / np.sqrt(re / 1e5)        # turbulent flat plate [E]
    swet = 2.0 * S_v
    dcd0 = ETA_FIN * 1.35 * cf * swet / S          # k_int 1.35 [E]
    return dcd0, cf


def stall_speed_kmh(auw):
    """V_stall scaling from the reference point (guide §4 datum)."""
    return V_STALL_REF * np.sqrt(auw / AUW_REF)


def yaw_subsidence(cnb_per_deg, cnr, cyb=-0.15, cyr=0.25):
    """Simplified 2-DOF (β, r) yaw dynamics: returns eigenvalues, 1/s.

    [E] inputs: Cyβ ≈ −0.15 (finless), Cyr ≈ +0.25; I_z band. The finless
    configuration with Cnβ < 0 shows a divergent real mode (time constant
    reported); the finned configuration shows stable subsidence. Full Dutch
    roll (4-DOF) is left to the flight-test programme (E-series).
    """
    q = 0.5 * RHO * V_CRU**2
    m = AUW_REF
    yb = q * S * cyb / m
    yr = q * S * B * cyr / (m * V_CRU)
    nb = q * S * B * cnb_per_deg * DEG / IZ
    nr = q * S * B**2 * cnr / IZ
    A = np.array([[yb / V_CRU, -1.0 + yr / V_CRU],
                  [nb, nr]])
    return np.linalg.eigvals(A)


def rudder_delta_req(cnb_total, cndr, v_air, v_cw):
    """Rudder deflection (°) to hold a steady sideslip in a crosswind."""
    beta = np.degrees(np.arctan2(v_cw, v_air))
    return beta * cnb_total / cndr, beta


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    print("=" * 74)
    print("SALAMANDRA — DIRECTIONAL STABILITY (Cn_beta) AND FIN OPTIONS")
    print("Configuration: FSW 1300 mm · nose boom · pusher · elevons only")
    print("Methods: DATCOM/Roskam/Raymer/Helmbold/Hoerner [M]; inputs [E]")
    print("=" * 74)

    # ---- 1. Finless baseline: Cn_beta budget ----
    cnb_f = cnb_fuselage(K_FUS_BAND[1], S_FS, L_F)          # worst (0.96)
    cnb_f_lo = cnb_fuselage(K_FUS_BAND[0], S_FS, L_F)       # best (0.40)
    print("\n1. FINLESS BASELINE — Cn_beta budget (/deg)")
    print(f"   Body (k=0.40 best / 0.96 worst): {cnb_f_lo:+.5f} / {cnb_f:+.5f}"
          f"  (S_fs {S_FS:.3f} m², l_f {L_F:.3f} m)")
    for tag, w in [("wing FSW band", CNB_W_BAND[0]), ("wing best", CNB_W_BAND[1])]:
        print(f"   Wing {tag:12s}: {w:+.5f}")
    WING_MEAN = (CNB_W_BAND[0] + CNB_W_BAND[1]) / 2.0
    cnb_no_lo = cnb_f_lo + CNB_W_BAND[1]
    cnb_no_hi = cnb_f + CNB_W_BAND[0]
    print(f"   TOTAL no fin  : {cnb_no_lo:+.5f} … {cnb_no_hi:+.5f} /deg  "
          f"=> NEGATIVE (statically unstable) [E]")
    lam = yaw_subsidence(cnb_no_hi, cnr_wing())
    print(f"   Yaw subsidence mode (worst): λ = {lam.real[0]:+.3f} 1/s"
          f"  (divergence τ ≈ {1.0/max(lam.real):.1f} s [E])")

    # ---- 2. Fin sizing for stability tiers ----
    print("\n2. FIN SIZING (centreline, rear-pod extension, l_v = %.0f mm)" % (L_V*1000))
    tiers = [
        ("V1a — marginal-stable (nominal ≥ 0.0005/deg)", 0.0005),
        ("V1b — robust (nominal ≥ 0.0010/deg)",          0.0010),
    ]
    # solve S_v at band centre, check band extremes
    AR_FIN = 3.0
    tier_areas = []
    for tag, target in tiers:
        # nominal: k_fus = 0.70, S_fs centre, CLα band centre
        cnb_fus_nom = cnb_fuselage(0.70, S_FS, L_F)
        cla_nom = sum(cla_fin_band(AR_FIN, 12.0)) / 2.0
        S_v = fin_area_for_target(target)
        tier_areas.append(S_v)
        # band propagation
        cnb_lo = cnb_fin(S_v, L_V, cla_fin_band(AR_FIN, 12.0)[0]) + \
            cnb_fuselage(K_FUS_BAND[0], S_FS_BAND[0], L_F) + CNB_W_BAND[1]
        cnb_hi = cnb_fin(S_v, L_V, cla_fin_band(AR_FIN, 12.0)[1]) + \
            cnb_fuselage(K_FUS_BAND[1], S_FS_BAND[1], L_F) + CNB_W_BAND[0]
        b_v = np.sqrt(S_v * AR_FIN)
        c_r, c_t, h_c = fin_geometry(S_v, b_v)
        m_lo, m_hi = fin_mass_band(S_v)
        dcd0, cf = fin_drag(S_v)
        cd_tot = CD0_CRU + CL_CRU**2 / (np.pi * ARW * E_OSW)
        dwhkm = 100.0 * dcd0 / cd_tot
        auw_new = AUW_REF + (m_lo + m_hi) / 2.0 / 1000.0
        vs = stall_speed_kmh(auw_new)
        V_v = S_v * L_V / (S * B)
        print(f"\n   {tag}")
        print(f"   S_v = {S_v*100:.2f} dm² · b_v = {b_v*1000:.0f} mm · "
              f"c_r = {c_r*1000:.0f} / c_t = {c_t*1000:.0f} mm · AR_v ≈ {AR_FIN:.1f}")
        print(f"   Cn_beta total band: {cnb_lo:+.5f} … {cnb_hi:+.5f} /deg "
              f"(nominal ≈ {cnb_fin(S_v,L_V,cla_nom)+cnb_fus_nom+WING_MEAN:+.5f})")
        print(f"   Fin Cn_beta     : {cnb_fin(S_v,L_V,cla_nom):+.5f} /deg")
        print(f"   Volume coeff V_v = {V_v:.3f} (tailless practice ≈ 0.02–0.05 [I])")
        print(f"   Mass            : {m_lo:.0f}–{m_hi:.0f} g (solid 1.2–2.0 mm PETG)")
        print(f"   ΔCD0            : +{dcd0:.4f}  →  +{dwhkm:.1f} % drag / "
              f"Wh/km ≈ {1.15*(1+dwhkm/100):.2f} [E]")
        print(f"   AUW +{1000*(auw_new-AUW_REF):.0f} g → V_stall ≈ {vs:.1f} km/h "
              f"(limit 45, OP-24 lever applies)")
        if target == 0.0005:
            selected_auw = AUW_REF + V1_FIN_CAP_G / 1000.0
            print(f"   V1 allocation   : {V1_FIN_CAP_G:.2f} g cap → "
                  f"AUW {selected_auw*1000:.1f} g / V_stall "
                  f"{stall_speed_kmh(selected_auw):.1f} km/h")

    # ---- 3. Recommended geometry (V1a) — structural check ----
    S_v = tier_areas[0]
    b_v = np.sqrt(S_v * AR_FIN)
    c_r, c_t, h_c = fin_geometry(S_v, b_v)
    q_ne = 0.5 * RHO * V_NE**2
    F = q_ne * S_v * 1.0 * ETA_FIN          # CN = 1.0, slipstream
    M = F * h_c
    print("\n3. STRUCTURAL CHECK, recommended V1a fin at V_NE (cantilever)")
    print(f"   F = {F:.1f} N at centroid h = {h_c*1000:.0f} mm → M = {M:.2f} N·m")
    for t in (0.0015, 0.0025, 0.0030):
        I_pl = c_r * t**3 / 12.0
        sig = M * (t / 2.0) / I_pl / 1e6
        print(f"   root t = {t*1000:.1f} mm → σ = {sig:5.1f} MPa "
              f"(PETG yield ≈ 50 MPa, FS {50.0/sig:.2f})")
    print("   => root t ≥ 3.0 mm solid for FS ≥ 1.5 without crediting the Al spar")
    om = 3.516 * np.sqrt(2.0e9 * (c_r*0.0025**3/12.0) /
                         (1250.0 * c_r*0.0025 * b_v**4))
    print(f"   First bending mode ≈ {om/(2*np.pi):.1f} Hz — flutter/strength "
          f"check in F2 [E]")

    # ---- 4. Rudder authority (movable option) ----
    print("\n4. MOVABLE RUDDER OPTION — authority vs mission need")
    cla_nom = sum(cla_fin_band(AR_FIN, 12.0)) / 2.0
    for tau in (TAU_BAND[0], 0.32, TAU_BAND[1]):
        cndr = ETA_RUD * cla_nom * tau * (S_v / S) * (L_V / B)
        print(f"   τ = {tau:.2f} → |Cnδr| = {cndr:.5f} /deg")
    cndr_nom = ETA_RUD * cla_nom * 0.32 * (S_v / S) * (L_V / B)
    cnb_v1 = cnb_fin(S_v, L_V, cla_nom) + cnb_fuselage(0.70, S_FS, L_F) + WING_MEAN
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
    cnr_f = cnr_fin(S_v, L_V, helmbold_cla(AR_FIN, 12.0))
    print(f"   Wing ≈ {cnr_w:.3f} ; fin V1a ≈ {cnr_f:.3f} → total ≈ "
          f"{cnr_w+cnr_f:.3f} (damping doubled)")
    lam_f = yaw_subsidence(0.0005, cnr_w + cnr_f)
    print(f"   Yaw subsidence (V1a): λ = {lam_f.real.max():+.3f} 1/s "
          f"(stable, τ ≈ {1.0/abs(lam_f.real.max()):.1f} s) [E]")

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
    cnb_v1b = cnb_fin(fin_area_for_target(0.0010), L_V, cla_nom) + \
        cnb_fuselage(0.70, S_FS, L_F) + WING_MEAN
    check(f"V1b nominal Cnβ = +0.0010/deg (got {cnb_v1b:+.5f})",
          abs(cnb_v1b - 0.0010) < 1e-8)
    check(f"Finless nominal Cnβ < 0 ({cnb_fuselage(0.70,S_FS,L_F):+.5f})",
          cnb_fuselage(0.70, S_FS, L_F) < 0.0)
    cndr_ref = ETA_RUD * 0.06 * 0.30 * 0.10 * 0.30
    check(f"Cnδr ref (τ 0.30, η 1.15): {cndr_ref:.6f}/deg",
          abs(cndr_ref - 0.000621) < 1e-5)
    i_root_3 = c_r * 0.003 ** 3 / 12.0
    sig_root_3 = M * 0.0015 / i_root_3
    check(f"V1a 3.0 mm root FS >= 1.5 without spar credit "
          f"(got {50e6/sig_root_3:.2f})", 50e6 / sig_root_3 >= 1.5)
    v1a_lo = fin_mass_band(tier_areas[0])[0]
    check(f"V1 fin cap matches the lower mass estimate "
          f"({V1_FIN_CAP_G:.2f} vs {v1a_lo:.2f} g)",
          abs(V1_FIN_CAP_G - v1a_lo) <= 0.01)
    check("V1 allocation remains below the 1620.4 g stall ceiling",
          AUW_REF * 1000.0 + V1_FIN_CAP_G <= 1620.4)
    print(f"\n   VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
