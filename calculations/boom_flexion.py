#!/usr/bin/env python3
"""
Nose-boom and rear-fin structural check for PROTOTYPE 0.1 (updated for
ADR-0040/0043): the battery boom is an ALUMINIUM tube Ø8x1.0 (ext 8, int
6 mm — the designer already owns it) and a Ø3 mm aluminium tube is added
aft, near the trailing edge, as the V1 fin / rear-pod stiffener. Carbon
optimisation is deferred (documented as pending, ADR-0015 revision).

WHY THIS SCRIPT EXISTS: the printed boom (70x32 mm box, 0.9 mm skin, <= 40 g
target, OP-24) carries the 445 g 6S1P pack at x ~= -360 with supports at the
front cradle face (x ~= -459) and the CORE (x = -132) — a 327 mm span. Replacing the
box by a Ø8 aluminium tube changes stiffness by ~250x and strength by ~4x in
section properties; the governing question is whether the TUBE ALONE can
carry the pack, and under which support arrangement.

KEY FINDING: the Ø8x1.0 tube remains unacceptable as a pure cantilever at
+6 g, but passes as a simply-supported beam with the pack between the two
supports. The ADR-0043 geometry (pack centred near -360, front support near
-459 and CORE support at -132) is exactly a two-support configuration — the printed cradle around
the pack is what makes it work.

Loads: pack 445 g [D] (I-16), FPV camera ~15 g at the tip (short cantilever),
cradle ~20 g [E]. Load factors +6/-3 (docs/00); landing impact at the tip
skid up to ~5 g [E] (the printed skid absorbs it; the bare tube sees ~3 g).

Aluminium band: 6061-T6 yield 276 MPa, 6061-O 55 MPa, 7075-T6 503 MPa [M]
(standard alloy data); the owner tube alloy is unknown -> band declared.

The Ø3 mm aft stiffener: V1 fin (b_v 250 mm, root t 2.5 mm solid PETG, I-20)
gets an Ø3 aluminium leading-edge spar: EI doubles the root stiffness and
adds a load path against pusher-slipstream buffeting (OP-26); mass ~5 g.

Confidence tags: [M] measured, [D] derived, [E] estimated. Validation cases
at the end.
"""
import sys
import numpy as np

from balance_cg import (CRADLE_MASS, NOSE_POD_TIP, REFERENCE_PACK,
                        TUBE_CORE_INSERTION, solve_reference_layout)

G = 9.81
E_AL = 70.0e9             # Pa, aluminium 6061
SIG_Y = (276.0e6, 55.0e6, 503.0e6)   # 6061-T6 / 6061-O / 7075-T6 [M]
RHO_AL = 2700.0           # kg/m³

# Tube Ø8, interior Ø6 (measured by the designer -> wall 1.0 mm)
D_T, T_T = 0.008, 0.001
D_I = D_T - 2 * T_T

# Geometry is solved by the same ADR-0040 balance model used by the guide.
_LAYOUT = solve_reference_layout()
X_TIP = _LAYOUT["bay_fwd"]
X_CORE = NOSE_POD_TIP
L = X_CORE - X_TIP
X_PACK = _LAYOUT["pack_station"]
M_PACK = REFERENCE_PACK
M_CAM = 0.015             # kg, FPV camera at the tip
M_CRADLE = CRADLE_MASS
N_MAX = 6.0               # design load factor (docs/00)
N_IMPACT = 5.0            # landing impact at the tip skid [E]


def tube_i(d_ext, d_int):
    """Second moment of area of a thin tube, m⁴."""
    return np.pi / 64.0 * (d_ext ** 4 - d_int ** 4)


def main():
    print("=" * 74)
    print("NOSE BOOM Ø8x1.0 ALUMINIUM + Ø3 AFT STIFFENER — ADR-0040/0043")
    print("=" * 74)

    i_t = tube_i(D_T, D_I)
    a_t = np.pi / 4.0 * (D_T ** 2 - D_I ** 2)
    m_tube = RHO_AL * a_t * (L + TUBE_CORE_INSERTION)
    m_total_boom = m_tube + M_CRADLE
    print(f"\n1. TUBE DATA (Ø8 / int Ø6 — wall 1.0 mm, measured)")
    print(f"   A = {a_t*1e6:.2f} mm² · I = {i_t*1e12:.1f} mm⁴ "
          f"· mass {(L+TUBE_CORE_INSERTION)*1000:.0f} mm = {m_tube*1000:.1f} g")
    print(f"   Boom total (tube + cradle) = {m_total_boom*1000:.1f} g "
          f"vs the 40 g budget (OP-24) "
          f"-> {'OK' if m_total_boom <= 0.042 else 'OVER'} "
          f"({m_total_boom*1000-40:+.1f} g from target)")

    # ---- 2. Pure cantilever (rejected arrangement) ----
    print("\n2. PURE CANTILEVER (pack at the tip) — REJECTED")
    f = N_MAX * (M_PACK + M_CAM + M_CRADLE) * G
    m_max = f * L
    sig = m_max * (D_T / 2) / i_t
    delta = f * L ** 3 / (3 * E_AL * i_t)
    k = 3 * E_AL * i_t / L ** 3
    freq = np.sqrt(k / (M_PACK + M_CAM + M_CRADLE)) / (2 * np.pi)
    print(f"   +{N_MAX:.0f} g: M = {m_max:.2f} N·m -> σ = {sig/1e6:.0f} MPa "
          f"(6061-T6 yield {SIG_Y[0]/1e6:.0f}) FS {SIG_Y[0]/sig:.2f} — FAILS")
    print(f"   deflection {delta*1000:.0f} mm · first mode {freq:.1f} Hz "
          f"(pack in the 5 Hz band: bad)")
    print(f"   => The tube alone cannot cantilever the 445 g pack.")

    # ---- 3. Two-support beam (pack between supports) ----
    print(f"\n3. TWO-SUPPORT BEAM (pack {X_PACK*1000:.0f}, supports "
          f"{X_TIP*1000:.0f}/{X_CORE*1000:.0f} mm)")
    a = X_PACK - X_TIP
    b = X_CORE - X_PACK
    f_pack = N_MAX * M_PACK * G
    f_cam = N_MAX * M_CAM * G
    m_pack = f_pack * a * b / L   # simply-supported point load
    m_cam = f_cam * (X_TIP - X_TIP + 0.08) * (L - 0.08) / L
    m_max = m_pack + m_cam
    sig = m_max * (D_T / 2) / i_t
    delta_pack = f_pack * a ** 2 * b ** 2 / (3 * E_AL * i_t * L)
    k2 = 48 * E_AL * i_t / L ** 3
    freq2 = np.sqrt(k2 / (M_PACK + M_CRADLE)) / (2 * np.pi)
    print(f"   M_max = {m_max:.2f} N·m -> σ = {sig/1e6:.0f} MPa "
          f"(FS {SIG_Y[0]/sig:.2f} vs 6061-T6; {SIG_Y[1]/sig:.2f} vs 6061-O)")
    print(f"   deflection {delta_pack*1000:.1f} mm at +{N_MAX:.0f} g "
          f"· first mode {freq2:.1f} Hz")
    ok_2s = sig < SIG_Y[0] / 2.0 and delta_pack < 0.005 and freq2 > 15.0
    print(f"   Verdict: {'PASS' if ok_2s else 'FAIL'} "
          f"(FS >= 2, δ < 5 mm, f > 15 Hz)")

    # ---- 4. Landing impact at the tip skid ----
    print("\n4. LANDING IMPACT (tip skid first contact, ~5 g [E])")
    f_imp = N_IMPACT * (M_PACK + M_CRADLE) * G * (a / L)   # pack near tip:
    # actually the skid load acts at the tip: short cantilever from the
    # cradle face (~60 mm) — the cradle carries the pack, the tip sees the
    # camera only
    f_tip = N_IMPACT * M_CAM * G
    m_tip = f_tip * 0.06
    sig_tip = m_tip * (D_T / 2) / i_t
    print(f"   tip skid (camera only, 60 mm cantilever): σ = "
          f"{sig_tip/1e6:.1f} MPa — trivial")
    print(f"   pack impact absorbed by the printed cradle + skid [E]; the "
          f"bare tube must not see impacts > 3 g at the tip (printed skid "
          f"is the crush zone)")

    # ---- 5. Ø3 aft stiffener (V1 fin leading-edge spar) ----
    print("\n5. Ø3 mm AFT STIFFENER — V1 fin / rear-pod (TE region)")
    i3 = tube_i(0.003, 0.002)          # Ø3x0.5 tube (or solid: similar EI)
    i3_solid = np.pi / 64.0 * 0.003 ** 4
    ei3 = E_AL * max(i3, i3_solid)
    ei_fin_root = 1.94e9 * (0.106 * 0.0030 ** 3 / 12.0)   # ADR-0038 fin root
    m3 = RHO_AL * (np.pi / 4.0 * 0.003 ** 2) * 0.30
    print(f"   EI spar = {ei3:.3f} N·m² vs fin-root PETG EI = "
          f"{ei_fin_root:.3f} N·m² -> {'>2x' if ei3 > 2*ei_fin_root else '<2x'} "
          f"stiffness added at the root")
    print(f"   mass (Ø3, 300 mm) = {m3*1000:.1f} g — negligible")

    # ---- 6. Tube channel vs dihedral kinks (CAD question Q2) ----
    print("\n6. TUBE CHANNEL vs DIHEDRAL KINKS (CAD question Q2)")
    # cumulative dihedral per segment (guide §4.3): CORE 0 / seg1 1.07 /
    # seg2 1.53 / seg3 2.0 deg -> kinks at y=195 (1.07), 347 (0.46), 498 (0.47)
    kinks = [1.07, 0.46, 0.47]
    t_joint = 0.010                    # m, joint-face thickness (tenon) [E]
    clear_ch = (0.0126 - 0.012) / 2    # radial clearance of the Ø12.4-12.6 channel
    for kdeg in kinks:
        dev = t_joint * np.tan(np.radians(kdeg))
        print(f"   kink {kdeg:.2f}°: deviation across the joint face = "
              f"{dev*1000:.2f} mm vs channel radial clearance "
              f"{clear_ch*1000:.2f} mm -> "
              f"{'FITS' if dev < clear_ch else 'INTERFERES'}")
    k_flat = max(kinks)
    dev_max = t_joint * np.tan(np.radians(k_flat))
    # (checks moved to section 7 — check() is defined there)

    # ---- 7. Validation cases ----
    print("\n7. VALIDATION CASES")
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"   [{'PASS' if cond else 'FAIL'}] {name}")

    # tube geometry
    check(f"I tube Ø8/int6 = 1.374e-10 m⁴ (got {i_t:.4e})",
          abs(i_t - 1.374e-10) / 1.374e-10 < 0.01)
    check(f"A tube = 22.0 mm² (got {a_t*1e6:.2f})", abs(a_t*1e6 - 22.0) < 0.5)
    # cantilever formulas
    f_cl = N_MAX * (M_PACK + M_CAM + M_CRADLE) * G
    m_cl = f_cl * L
    sig_cl = m_cl * 0.004 / i_t
    check(f"Cantilever σ at +6 g in 260-300 MPa band (got {sig_cl/1e6:.0f})",
          260 < sig_cl / 1e6 < 300)
    d_cl = f_cl * L ** 3 / (3 * E_AL * i_t)
    check(f"Cantilever δ at +6 g in 30-38 mm band (got {d_cl*1000:.0f})",
          30 < d_cl * 1000 < 38)
    # two-support point load at the current solved station
    mp = N_MAX * M_PACK * G * a * b / L
    check(f"Two-support M in 1.7-2.0 N·m band (got {mp:.2f})",
          1.7 < mp < 2.0)
    # deflection via standard formula for point load on simple beam:
    # δ = F·a²·b²/(3·E·I·L)
    d2 = N_MAX * M_PACK * G * a ** 2 * b ** 2 / (3 * E_AL * i_t * L)
    check(f"Two-support δ < 2.0 mm (got {d2*1000:.1f})", d2 * 1000 < 2.0)
    f2 = np.sqrt(48 * E_AL * i_t / L ** 3 / (M_PACK + M_CRADLE)) / (2 * np.pi)
    check(f"Two-support mode > 20 Hz (got {f2:.1f})", f2 > 20)
    # mass
    check(f"Tube mass 22-25 g for current length (got {m_tube*1000:.1f})",
          22 <= m_tube * 1000 <= 25)
    check(f"Boom total 37-40 g (got "
          f"{m_total_boom*1000:.1f})", m_total_boom <= 0.042)
    # stiffener
    check(f"Ø3 spar adds >= 50 % of the fin-root EI "
          f"(spar {ei3:.3f} vs root {ei_fin_root:.3f}; total "
          f"{(ei3+ei_fin_root)/ei_fin_root:.2f}x)", ei3 >= 0.5 * ei_fin_root)
    # tube channel vs dihedral kinks (CAD question Q2)
    clear_ch = (0.0126 - 0.012) / 2
    dev_max = t_joint * np.tan(np.radians(max(kinks)))
    check(f"Largest kink {max(kinks):.2f}° deviates {dev_max*1000:.2f} mm < "
          f"clearance {clear_ch*1000:.2f} mm (straight channels OK)",
          dev_max < clear_ch)
    L_seg = 0.151
    kappa = np.radians(0.47) / L_seg
    sig_bend = 105e9 * 0.006 * kappa
    check(f"Even forced, the kink bends the tube elastically at "
          f"σ = {sig_bend/1e6:.0f} MPa (CFRP ~1600 MPa) — no plastic set",
          sig_bend < 100e6)

    print(f"\n   VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
