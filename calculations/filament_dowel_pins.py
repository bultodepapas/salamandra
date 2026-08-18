#!/usr/bin/env python3
"""
Filament dowel pins in the glued SEGMENT joints (2026-08-06, ADR-0039):
Ø1.75 mm 3D-printer filament (PETG/PLA scraps) as alignment/shear dowels in
the glued joints at y = 347 / 498 mm (ADR-0024 segmentation).

Scope: the GLUED segment joints ONLY. The CORE<PANEL joint is removable
(sliding fit, no adhesive — ADR-0031/0032): its alignment is the carbon
tube+pin couple, and it carries NO filament dowel. The carbon Ø6 pin of the
torque couple is NOT replaced (joint_pin_trade.py rejected filament there).

Functions of the dowel:
  1. ALIGNMENT — locates the two faces during glue cure (prevents shear slip
     and the stress concentration of a misaligned joint); standard joinery
     practice, benefit declared [I].
  2. SHEAR REDUNDANCY — additive to the ADR-0023 bond (area >= 3x skin);
     the adhesive remains the primary load path. Redundancy quantified here.

Spec (ADR-0039):
  - 2 dowels per segment joint (4 glued joints per aircraft -> 8 dowels)
  - positions on the joint face: x/c = 0.40 and 0.60, at the section
    mid-plane z = 0 (clear of the carbon tube at x/c 0.25 and of the hinge
    cell starting at 0.72)
  - pin: 3D-printer filament Ø1.75 mm, length ≈ 20-22 mm (embedment
    >= 10 mm per side)
  - hole: Ø1.8-1.9 mm (sliding fit, 0.05-0.15 clearance), printed with a
    SOLID collar Ø8 mm x 4 mm (4+ perimeters) around the bore — bearing
    material, since the surrounding infill is 5 % gyroid
  - bond: dab of the ADR-0023 PETG adhesive on ONE side; the other side
    stays free (alignment during assembly)

Outputs [D] on [E] bands; validation cases at the end.
"""
import sys

import numpy as np
from design_config import (
    ELEVON_HINGE_XC,
    ARTICLE_V1_MASS_KG,
    G0,
    PETG_DENSITY_KG_M3,
    POSITIVE_LIMIT_LOAD_FACTOR,
    chord,
)

# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------
D_PIN = 0.00175           # m, filament Ø1.75
L_PIN = 0.021             # m, length (≈ 10.5 mm embedment per side)
N_PINS_PER_JOINT = 2
N_GLUED_JOINTS = 4        # y = 347 and 498, both halves

# Joint shear demand at +6 g, V_NE (guide §4: n_max 6): half-wing lift at 6 g
# ≈ 50 N; outboard-area fractions [E bands]:
FRAC_OUT = {347: (0.40, 0.70), 498: (0.15, 0.35)}   # of the half-wing lift
W = ARTICLE_V1_MASS_KG * G0
N_MAX = POSITIVE_LIMIT_LOAD_FACTOR

# Material [M]/[E]: PETG printed shear strength band; PLA brittle in shear
TAU_PETG = (26e6, 35e6)
TAU_PLA = (35e6, 50e6)
RHO = PETG_DENSITY_KG_M3

# Solid collar around each bore (bearing material)
COLLAR_D = 0.008           # m
COLLAR_T = 0.004           # m

# --------------------------------------------------------------------------
def pin_capacity(d, tau, double_shear=True):
    """Ultimate shear force of one pin, N."""
    a = np.pi * (d / 2.0) ** 2
    return 2.0 * a * tau if double_shear else a * tau


def joint_demand(y, frac_band):
    """Shear demand at a glued joint, N: half-wing 6-g lift × outboard fraction."""
    half_lift = N_MAX * W / 2.0
    f = half_lift * np.mean(frac_band)
    return f, half_lift * frac_band[0], half_lift * frac_band[1]


def main():
    print("=" * 74)
    print("FILAMENT DOWEL PINS IN THE GLUED SEGMENT JOINTS (ADR-0039)")
    print("2 × Ø1.75 PETG/PLA filament per joint · y = 347 and 498 mm")
    print("=" * 74)

    # ---- 1. Demand vs capacity ----
    print("\n1. SHEAR DEMAND vs DOWEL CAPACITY (+6 g, V_NE)")
    cap_petg = pin_capacity(D_PIN, np.mean(TAU_PETG))
    cap_pla = pin_capacity(D_PIN, np.mean(TAU_PLA))
    print(f"   One dowel, double shear: PETG {cap_petg:.0f} N "
          f"({np.mean(TAU_PETG)/1e6:.0f} MPa [E]), PLA {cap_pla:.0f} N")
    for y in (347, 498):
        d, d_lo, d_hi = joint_demand(y, FRAC_OUT[y])
        cap_j = N_PINS_PER_JOINT * cap_petg
        print(f"   Joint y = {y} mm: demand ≈ {d:.0f} N [E band {d_lo:.0f}–{d_hi:.0f}] "
              f"vs {N_PINS_PER_JOINT}×PETG = {cap_j:.0f} N → FS ≈ {cap_j/d:.1f}")

    # ---- 2. Alignment function ----
    print("\n2. ALIGNMENT (the primary function, [I] declared)")
    print("   The tenon locates the faces; the dowel prevents shear slip during")
    print("   glue cure. A misaligned joint is a stress concentration on the")
    print("   bond — alignment IS strength, and it costs scraps.")

    # ---- 3. Spec check: positions clear of tube and hinge ----
    print("\n3. POSITION CHECK (clear of carbon tube and hinge cell)")
    for y in (347, 498):
        c = chord(y / 1000.0)
        tube_span = (0.25 * c - 0.006, 0.25 * c + 0.006)
        p1, p2 = 0.40 * c, 0.60 * c
        ok = p1 > tube_span[1] + 0.005 and p2 < ELEVON_HINGE_XC * c - 0.005
        print(f"   y = {y} mm (c = {c*1000:.0f} mm): tube {tube_span[0]*1000:.0f}–"
              f"{tube_span[1]*1000:.0f} mm · pin1 {p1*1000:.0f} mm (x/c 0.40) · "
              f"pin2 {p2*1000:.0f} mm (x/c 0.60) · hinge at {ELEVON_HINGE_XC*c*1000:.0f} mm"
              f" → {'CLEAR' if ok else 'CONFLICT'}")

    # ---- 4. Mass and bearing ----
    print("\n4. MASS AND BEARING (solid collar)")
    v_pin = np.pi * (D_PIN / 2.0) ** 2 * L_PIN
    v_col = np.pi * (COLLAR_D / 2.0) ** 2 * COLLAR_T
    m_total = (v_pin + v_col) * RHO * N_PINS_PER_JOINT * N_GLUED_JOINTS
    print(f"   Pin {v_pin*1e9:.0f} mm³ + collar {v_col*1e9:.0f} mm³ → total "
          f"{m_total*1000:.1f} g per aircraft (0.15 % of AUW, inside the "
          f"20 g hardware allowance)")
    d_hi = 0.70 * N_MAX * W / 2.0
    sig_b = d_hi / (D_PIN * COLLAR_T) / 1e6
    print(f"   Worst bearing on the collar: {sig_b:.1f} MPa (PETG yield ≈ 50 MPa, "
          f"FS {50/sig_b:.0f})")

    # ---- 5. Validation cases ----
    print("\n5. VALIDATION CASES")
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"   [{'PASS' if cond else 'FAIL'}] {name}")

    a = np.pi * (D_PIN / 2.0) ** 2
    check(f"Pin area Ø1.75 = 2.405 mm² (got {a*1e6:.3f})",
          abs(a - 2.405e-6) < 1e-9)
    cap1 = pin_capacity(D_PIN, 30e6, double_shear=False)
    check(f"Single shear @30 MPa = 72.2 N (got {cap1:.1f})",
          abs(cap1 - 72.2) < 0.5)
    cap2 = pin_capacity(D_PIN, 30e6, double_shear=True)
    check(f"Double shear @30 MPa = 144.3 N (got {cap2:.1f})",
          abs(cap2 - 144.3) < 0.5)
    d_j = joint_demand(347, FRAC_OUT[347])[0]
    check(f"Joint-347 demand ≈ 28 N (got {d_j:.0f})", 20 < d_j < 36)
    check(f"FS ≥ 4 at the joint (2×PETG double shear vs demand): "
          f"{2*cap2/d_j:.1f}", 2 * cap2 / d_j >= 4.0)
    check(f"Mass < 3 g (got {m_total*1000:.1f} g)", m_total < 0.003)
    print(f"\n   VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
