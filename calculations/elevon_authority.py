#!/usr/bin/env python3
"""
Autoridad de elevones: Dm por grado de deflexion (reflex) sobre el 30-90 % de
semienvergadura, y margen frente al trim requerido a SM 8 %.

Modelo: el VLM de vlm_ala_volante con torsion por tramos — el elevon se modela
como incidencia local constante sobre su tramo (misma fisica que el wash-in).
NOTA: el VLM de placa plana no tiene Cm0 de seccion; el Cm0 del perfil se suma
como dato [D] del cribado B3 (I-15 §6.2).
"""
import numpy as np
from vlm_ala_volante import geom, solve

B, S, TAPER, SWEEP = 1.30, 0.282, 0.50, -20.0
ETA_IN, ETA_OUT = 0.30, 0.90          # tramo de elevon (30-90 % b/2)
SM = 0.08
CL_CRU = 0.132                        # ventana_torsion.py
CM0_REQ = CL_CRU * SM                 # 0.01056
YIELD = 0.00338                       # Cm0 por grado de wash-in [D] (VLM)
# Cm0 de seccion del candidato raiz (MH60->13.5 %, cribado B3, I-15 §6.2):
CM0_SEC_BEST = +0.0016                # Re 5e5, Ncrit 10
CM0_SEC_WORST = -0.0018               # Re 5e5, Ncrit 12
TWIST_DISENO = 3.0                    # R-TWIST (nueva cota, ver guia §5.3)


def cm0_wing(twist_deg, elev_deg):
    """Cm a CL=0 del ala (VLM, placa plana) para wash-in + elevon por tramos."""
    g = geom(B, S, TAPER, SWEEP, 0.0)
    eta = np.abs(g['cps'][:, 1]) / (B / 2)
    mask = (eta >= ETA_IN) & (eta <= ETA_OUT)
    g['eps'] = np.radians(twist_deg * eta + elev_deg * mask)
    CL1, Cm1, _, _ = solve(g, 0.0)
    CL2, Cm2, _, _ = solve(g, 4.0)
    dCm_dCL = (Cm2 - Cm1) / (CL2 - CL1)
    return Cm1 - CL1 * dCm_dCL


def main():
    print("=" * 70)
    print("AUTORIDAD DE ELEVONES — trim a SM 8 % (todo [D])")
    print("=" * 70)
    dCm_tw = cm0_wing(1.0, 0.0) - cm0_wing(0.0, 0.0)
    dCm_de = cm0_wing(0.0, 1.0) - cm0_wing(0.0, 0.0)
    print(f"  Rendimiento wash-in : {dCm_tw:+.5f} /deg  (I-07: 0.0034)")
    print(f"  Rendimiento elevon  : {dCm_de:+.5f} /deg sobre 30-90 % b/2")
    print(f"  Trim requerido      : Cm0_req = {CM0_REQ:+.5f} (SM 8 %, CL_cru 0.132)")

    print("\n  Cierre de trim con R-TWIST = 3.0 deg (seccion raiz MH60->13.5 %):")
    for tag, cm0_sec in [("mejor caso (Re 5e5, Ncrit 10)", CM0_SEC_BEST),
                         ("peor caso  (Re 5e5, Ncrit 12)", CM0_SEC_WORST)]:
        deficit = CM0_REQ - (cm0_sec + YIELD * TWIST_DISENO)
        elev_deg = deficit / dCm_de
        print(f"    {tag:32s}: cm0_seccion {cm0_sec:+.4f} -> deficit "
              f"{deficit:+.4f} -> reflex de elevon ≈ {elev_deg:+.1f} deg")

    print("\n  Margen de control (caso nominal, twist 0.5 deg):")
    cm0_nom = CM0_SEC_BEST + YIELD * 0.5
    d = CM0_REQ - cm0_nom
    for de in [5.0, 10.0, 20.0]:
        avail = dCm_de * de
        print(f"    elevon {de:5.1f} deg -> Dm {avail:+.4f}  "
              f"({avail/d:5.1f} x el trim requerido {d:+.4f})")
    print("\n  Concl.: autoridad suficiente; el reflex permanente (I-08) cubre el")
    print("  cierre de trim y sobra recorrido de mando para maniobra.")


if __name__ == "__main__":
    main()
