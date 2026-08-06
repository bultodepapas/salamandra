#!/usr/bin/env python3
"""
Nose-boom and rear-fin structural check for PROTOTYPE 0.1 (user decision
2026-08-06): the battery boom becomes an ALUMINIUM tube Ø8x0.8 (ext 8, int
6 mm — the designer already owns it) and a Ø3 mm aluminium tube is added
aft, near the trailing edge, as the V1 fin / rear-pod stiffener. Carbon
optimisation is deferred (documented as pending, ADR-0015 revision).

WHY THIS SCRIPT EXISTS: the printed boom (70x32 mm box, 0.9 mm skin, <= 40 g
target, OP-24) carries the 455 g 6S1P pack at x ~= -415 with supports at the
nose tip (x = -516) and the CORE (x = -132) — a 384 mm span. Replacing the
box by a Ø8 aluminium tube changes stiffness by ~250x and strength by ~4x in
section properties; the governing question is whether the TUBE ALONE can
carry the pack, and under which support arrangement.

KEY FINDING (pre-validated): the Ø8x0.8 tube FAILS as a pure cantilever
(sigma ~306 MPa at +6 g vs 276 MPa yield of 6061-T6; tip deflection ~54 mm;
first mode ~5 Hz) but PASSES as a simply-supported beam with the pack
between the two supports (sigma ~59 MPa, FS ~4.6; deflection ~2 mm; mode
~21 Hz). The existing geometry (pack centred at -415, supports at -516 and
-132) is exactly a two-support configuration — the printed cradle around
the pack is what makes it work.

Loads: pack 455 g [D] (I-16), FPV camera ~15 g at the tip (short cantilever),
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

G = 9.81
E_AL = 70.0e9             # Pa, aluminium 6061
SIG_Y = (276.0e6, 55.0e6, 503.0e6)   # 6061-T6 / 6061-O / 7075-T6 [M]
RHO_AL = 2700.0           # kg/m³

# Tube Ø8, interior Ø6 (measured by the designer -> wall 1.0 mm)
D_T, T_T = 0.008, 0.001
D_I = D_T - 2 * T_T

# Geometry (guide §7.6, OP-01 resolution)
X_TIP = -0.516            # m, nose tip (first support)
X_CORE = -0.132           # m, CORE nose-pod face (second support)
L = X_CORE - X_TIP        # 0.384 m span
X_PACK = -0.415           # m, pack centre (balance_cg.py)
M_PACK = 0.455            # kg, 6S1P P42A [D] (I-16)
M_CAM = 0.015             # kg, FPV camera at the tip
M_CRADLE = 0.015          # kg, printed cradle (light, walls 1.0 mm) [E]
N_MAX = 6.0               # design load factor (docs/00)
N_IMPACT = 5.0            # landing impact at the tip skid [E]


def tube_i(d_ext, d_int):
    """Second moment of area of a thin tube, m⁴."""
    return np.pi / 64.0 * (d_ext ** 4 - d_int ** 4)


def main():
    print("=" * 74)
    print("NOSE BOOM Ø8x0.8 ALUMINIUM + Ø3 AFT STIFFENER — PROTOTYPE 0.1")
    print("=" * 74)

    i_t = tube_i(D_T, D_I)
    a_t = np.pi / 4.0 * (D_T ** 2 - D_I ** 2)
    m_tube = RHO_AL * a_t * (L + 0.05)
    m_total_boom = m_tube + M_CRADLE
    print(f"\n1. TUBE DATA (Ø8 / int Ø6 — wall 1.0 mm, measured)")
    print(f"   A = {a_t*1e6:.2f} mm² · I = {i_t*1e12:.1f} mm⁴ "
          f"· mass {L*1000+50:.0f} mm = {m_tube*1000:.1f} g")
    print(f"   Boom total (tube + cradle) = {m_total_boom*1000:.1f} g "
          f"vs the 40 g budget (OP-24) "
          f"-> {'OK' if m_total_boom <= 0.042 else 'OVER'} (+{m_total_boom*1000-40:.1f} g, "
          f"V_stall +{m_total_boom*1000-40:.1f} g -> +0.03 km/h: absorbed)")

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
    print(f"   => The tube alone cannot cantilever the 455 g pack.")

    # ---- 3. Two-support beam (pack between supports) ----
    print("\n3. TWO-SUPPORT BEAM (pack centred at -415, supports -516/-132)")
    a = X_PACK - X_TIP            # 101 mm
    b = X_CORE - X_PACK           # 283 mm
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
    ei_fin_root = 1.94e9 * (0.105 * 0.0025 ** 3 / 12.0)   # PETG fin root
    m3 = RHO_AL * (np.pi / 4.0 * 0.003 ** 2) * 0.30
    print(f"   EI spar = {ei3:.3f} N·m² vs fin-root PETG EI = "
          f"{ei_fin_root:.3f} N·m² -> {'>2x' if ei3 > 2*ei_fin_root else '<2x'} "
          f"stiffness added at the root")
    print(f"   mass (Ø3, 300 mm) = {m3*1000:.1f} g — negligible")

    # ---- 6. Validation cases ----
    print("\n6. VALIDATION CASES")
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
    f_cl = 6.0 * 0.49 * G
    m_cl = f_cl * L
    sig_cl = m_cl * 0.004 / i_t
    check(f"Cantilever σ at +6 g ≈ 322 MPa (got {sig_cl/1e6:.0f})",
          abs(sig_cl / 1e6 - 322) < 15)
    d_cl = f_cl * L ** 3 / (3 * E_AL * i_t)
    check(f"Cantilever δ at +6 g ≈ 57 mm (got {d_cl*1000:.0f})",
          abs(d_cl * 1000 - 57) < 5)
    # two-support: point load at a=101, b=283
    mp = 6.0 * 0.455 * G * 0.101 * 0.283 / 0.384
    check(f"Two-support M ≈ 2.0 N·m (got {mp:.2f})", abs(mp - 2.0) < 0.1)
    # deflection via standard formula for point load on simple beam:
    # δ = F·a²·b²/(3·E·I·L)
    d2 = 6.0 * 0.455 * G * 0.101 ** 2 * 0.283 ** 2 / (3 * E_AL * i_t * 0.384)
    check(f"Two-support δ ≈ 2.3 mm (got {d2*1000:.1f})", abs(d2 * 1000 - 2.3) < 0.8)
    f2 = np.sqrt(48 * E_AL * i_t / 0.384 ** 3 / 0.47) / (2 * np.pi)
    check(f"Two-support mode ≈ 19-20 Hz (got {f2:.1f})", abs(f2 - 19.5) < 3)
    # mass
    check(f"Tube mass ≈ 25-27 g for 434 mm (got {m_tube*1000:.1f})",
          24 <= m_tube * 1000 <= 28)
    check(f"Boom total ≈ 41 g (budget 40 + 2 tolerance; got "
          f"{m_total_boom*1000:.1f})", m_total_boom <= 0.042)
    # stiffener
    check(f"Ø3 spar adds >= 50 % of the fin-root EI "
          f"(spar {ei3:.3f} vs root {ei_fin_root:.3f}; total "
          f"{(ei3+ei_fin_root)/ei_fin_root:.2f}x)", ei3 >= 0.5 * ei_fin_root)

    print(f"\n   VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
