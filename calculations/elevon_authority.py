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
from design_config import B, S, SWEEP_C4_DEG, TAPER

SWEEP = SWEEP_C4_DEG
ETA_IN, ETA_OUT = 0.30, 0.90          # tramo de elevon (30-90 % b/2)
SM = 0.08
CL_CRU = 0.132                        # ventana_torsion.py
CM0_REQ = CL_CRU * SM                 # 0.01056
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
    print(f"  Rendimiento wash-in : {dCm_tw:+.5f} /deg  (I-07 historico -20 deg: 0.0034)")
    print(f"  Rendimiento elevon  : {dCm_de:+.5f} /deg sobre 30-90 % b/2")
    print(f"  Trim requerido      : Cm0_req = {CM0_REQ:+.5f} (SM 8 %, CL_cru 0.132)")

    print("\n  Cierre de trim con R-TWIST = 3.0 deg (seccion raiz MH60->13.5 %):")
    elev_needed = {}
    for tag, cm0_sec in [("mejor caso (Re 5e5, Ncrit 10)", CM0_SEC_BEST),
                         ("peor caso  (Re 5e5, Ncrit 12)", CM0_SEC_WORST)]:
        deficit = CM0_REQ - (cm0_sec + dCm_tw * TWIST_DISENO)
        elev_deg = deficit / dCm_de
        elev_needed[tag] = elev_deg
        print(f"    {tag:32s}: cm0_seccion {cm0_sec:+.4f} -> deficit "
              f"{deficit:+.4f} -> reflex de elevon ≈ {elev_deg:+.1f} deg")

    print(f"\n  Margen de control (caso limitante, twist {TWIST_DISENO:.1f} deg):")
    cm0_lim = CM0_SEC_WORST + dCm_tw * TWIST_DISENO
    d = CM0_REQ - cm0_lim
    for de in [5.0, 10.0, 20.0]:
        avail = dCm_de * de
        print(f"    elevon {de:5.1f} deg -> Dm {avail:+.4f}  "
              f"({avail/d:5.1f} x el trim requerido {d:+.4f})")
    best = elev_needed["mejor caso (Re 5e5, Ncrit 10)"]
    worst = elev_needed["peor caso  (Re 5e5, Ncrit 12)"]
    checks = {
        "rendimiento de wash-in calculado positivo": dCm_tw > 0.0,
        "perfil provisional favorable cierra dentro de 0.6 deg": best <= 0.62,
        "polar desfavorable se identifica fuera del cap de 0.6 deg": worst > 0.6,
        "5 deg de mando cubren el deficit limitante": dCm_de * 5.0 > d,
    }
    print("\n  VALIDACION")
    for name, passed in checks.items():
        print(f"    [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)

    print("\n  Concl.: la autoridad de mando es suficiente, pero el cap de reflex")
    print("  permanente solo cierra con la polar provisional favorable. La polar")
    print("  final B3 es un gate de CAD; el extremo desfavorable requiere ≈ 1.9 deg.")


if __name__ == "__main__":
    main()
