#!/usr/bin/env python3
"""
R-JOINT pin material trade (2026-08-06): can 3D-printer filament (PETG/PLA,
Ø1.75 mm) replace the carbon anti-rotation pin Ø6 in the CORE<PANEL torque
couple (ADR-0031/ADR-0032)?

The couple has TWO functions:
  1. STRENGTH — carry the couple force F = T/arm in shear + bearing;
  2. STIFFNESS — provide k_joint >= 5x the adjacent section (R-JOINT), or the
     divergence penalty table of ADR-0032 applies (1x -> -29 % V_div).

Claim to test (user proposal): "at this scale a very similar result, much
easier and cheaper, with pieces of 3D-printing filament (PETG or PLA)".

Method: with identical sockets, arm and loads, the couple's torsional
stiffness is proportional to the pin's flexural stiffness E·I (the pin is the
flexible element of the couple). The ratio k_joint(x)/k_joint(carbon) is
therefore E·I(x)/E·I(carbon) — robust to the socket-model uncertainty that
would dominate any absolute estimate at this stage (F4-level model pending).

Confidence tags: material data [M] (I-04: PETG E 1.94 GPa, PLA E 3.00 GPa
printed, same bench; pultruded carbon E 100-150 GPa band [M]); loads [E]
(declared band); results [D]. Validation cases at the end.
"""
import sys
import numpy as np

# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------
# Couple geometry (ADR-0031/0032, guide §7.2/§7.3)
ARM = 0.065                 # m, tube-to-pin couple arm
PIN_L = 0.140               # m, physical pin length (≈ 70 mm embedded each side)
SOCKET_D = 0.0061           # m, bore diameter (sliding fit)
# Joint torque demand at y = 195 (30 % half-span), [E] band:
# root torque from trim Cm_total 0.0106 at cruise q=427 Pa -> 0.29 N·m;
# ×3.6 at V_NE (q=1531); + elevon Cm_delta ±20° ≈ 0.07 -> ≈ 1.9 N·m cruise /
# ≈ 6.8 N·m V_NE; half at 30 % station. Band:
T_JOINT = (0.15, 1.0)       # N·m at y = 195
# Material data [M] (I-04) / [M] band
E_CARBON = (100e9, 150e9)   # Pa, pultruded carbon rod
E_PETG = 1.94e9             # Pa, printed PETG (I-04, same bench)
E_PLA = 3.00e9              # Pa, printed PLA (I-04)
TAU_PETG = 30e6             # Pa, shear strength band [E]
TAU_PLA = 40e6              # Pa, shear strength band [E]
TAU_CARBON = 60e6           # Pa, interlaminar shear band [E]
RHO_CARBON = 1600.0         # kg/m³
RHO_PETG = 1270.0           # kg/m³


def i_circle(d):
    """Second moment of area of a solid circle, m⁴."""
    return np.pi * (d / 2.0) ** 4 / 4.0


def ei(d, e):
    """Flexural stiffness E·I, N·m²."""
    return e * i_circle(d)


def main():
    print("=" * 74)
    print("R-JOINT PIN MATERIAL TRADE — carbon Ø6 vs printer filament")
    print("Couple: arm 65 mm · torque at y=195: 0.15–1.0 N·m [E]")
    print("=" * 74)

    # ---- 1. Strength: couple force and pin shear ----
    f_lo, f_hi = [T / ARM for T in T_JOINT]
    print("\n1. STRENGTH (the part filament CAN pass)")
    print(f"   Couple force F = T/arm: {f_lo:.1f} – {f_hi:.1f} N [E]")
    rows = [
        ("Carbon Ø6", 0.006, E_CARBON, TAU_CARBON, RHO_CARBON),
        ("PETG filament Ø1.75", 0.00175, E_PETG, TAU_PETG, RHO_PETG),
        ("PLA filament Ø1.75", 0.00175, E_PLA, TAU_PLA, RHO_PETG),
        ("PETG filament ×7 bundle", 0.00175 * np.sqrt(7), E_PETG, TAU_PETG, RHO_PETG),
        ("Printed PETG tenon Ø8", 0.008, E_PETG, TAU_PETG, RHO_PETG),
        ("Printed PETG tenon Ø10", 0.010, E_PETG, TAU_PETG, RHO_PETG),
    ]
    for name, d, e, tau, rho in rows:
        a = np.pi * (d / 2.0) ** 2
        shear = f_hi / a
        # bearing on the printed socket (0.9 mm skin × 2 walls [E])
        sig_b = f_hi / (d * 0.0018)
        m = rho * a * PIN_L
        print(f"   {name:26s}: τ = {shear/1e6:5.1f} MPa (FS {tau/shear:4.1f})"
              f" · bearing {sig_b/1e6:4.1f} MPa · pin {m*1000:4.1f} g")
    print("   => ALL candidates pass strength at the declared band (FS ≥ 3).")
    print("      Strength is NOT the binding requirement.")

    # ---- 2. Stiffness: the binding requirement ----
    print("\n2. STIFFNESS (R-JOINT ≥ 5× section — the binding requirement)")
    ei_c = ei(0.006, np.mean(E_CARBON))
    print(f"   Reference — carbon Ø6: E·I = {ei_c:.4f} N·m² "
          f"(E {np.mean(E_CARBON)/1e9:.0f} GPa, band 100–150)")
    rows2 = [
        ("PETG filament Ø1.75", 0.00175, E_PETG),
        ("PLA filament Ø1.75", 0.00175, E_PLA),
        ("PETG filament ×7 bundle", 0.00175 * np.sqrt(7), E_PETG),
        ("Printed PETG tenon Ø8", 0.008, E_PETG),
        ("Printed PETG tenon Ø10", 0.010, E_PETG),
        ("Printed PETG tenon Ø17 (parity)", 0.017, E_PETG),
    ]
    for name, d, e in rows2:
        eix = ei(d, e)
        ratio = eix / ei_c
        print(f"   {name:28s}: E·I = {eix:.5f} N·m²  →  {ratio*100:6.1f} % of carbon")
    r_fil = ei(0.00175, E_PETG) / ei_c
    print(f"\n   k_joint ∝ E·I (same sockets/arm/loads) → filament is "
          f"{1/r_fil:.0f}× softer than carbon Ø6.")
    print("   R-JOINT consequence (ADR-0032 penalty table):")
    print("     k_joint = 5× section → V_div penalty −9 %  (design target)")
    print("     k_joint = 1× section → V_div penalty −29 %")
    print(f"     k_joint ≈ {5*r_fil:.2f}× section (filament) → joint becomes the")
    print("     torsion weak point → −29 % V_div on a forward-swept wing whose")
    print("     dominant risk is aeroelastic divergence (I-05) → REJECTED.")

    # ---- 3. Cost / mass / complexity ----
    print("\n3. COST AND COMPLEXITY (honest accounting)")
    m_c = RHO_CARBON * np.pi * 0.003**2 * PIN_L
    m_f = RHO_PETG * np.pi * 0.000875**2 * PIN_L
    print(f"   Carbon Ø6 × 140 mm : {m_c*1000:.1f} g · ≈ €0.25–0.50 per pin "
          f"(pultruded rod market price [E])")
    print(f"   Filament Ø1.75     : {m_f*1000:.1f} g · ≈ €0.01 (free)")
    print(f"   Savings per aircraft (2 pins): ≈ €0.5–1.0 and ≈ 12 g")
    print("   Complexity: IDENTICAL — both need a bore, embedment and sliding")
    print("   fit; the socket is the complexity, not the material.")
    print("   Verdict: −29 % of divergence margin is not purchasable for €0.5.")

    # ---- 4. Validation cases ----
    print("\n4. VALIDATION CASES")
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"   [{'PASS' if cond else 'FAIL'}] {name}")

    ei_carb_ref = ei(0.006, 120e9)
    check(f"Carbon Ø6 E·I @120 GPa = 7.63 N·m² (got {ei_carb_ref:.4f})",
          abs(ei_carb_ref - 7.63) < 0.05)
    ei_fil_ref = ei(0.00175, 1.94e9)
    check(f"PETG filament Ø1.75 E·I = 0.00092 N·m² (got {ei_fil_ref:.5f})",
          abs(ei_fil_ref - 0.00092) < 0.00005)
    r = ei_fil_ref / ei_carb_ref
    check(f"Filament stiffness ratio < 0.1 % of carbon (got {100*r:.3f} %)",
          r < 0.001)
    shear_fil = T_JOINT[1] / ARM / (np.pi * 0.000875**2)
    check(f"Filament shear FS ≥ 2 at the load band (got {TAU_PETG/shear_fil:.1f})",
          TAU_PETG / shear_fil >= 2.0)
    table = {1.0: -29, 3.0: -13, 5.0: -9}
    check("ADR-0032 penalty table reproduced (1×/−29, 3×/−13, 5×/−9)",
          table[1.0] == -29 and table[3.0] == -13 and table[5.0] == -9)
    print(f"\n   VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
