#!/usr/bin/env python3
"""
Balance de masas y CG (OP-01) — deriva la solucion de la nariz-boom y las
estaciones de pack necesarias para alcanzar el CG objetivo.

Convenciones: x positivo hacia atras, origen en c/4 de raiz.
Salidas [D] salvo las etiquetadas PROVISIONAL/[E].
"""
import numpy as np

B, S, TAPER, SWEEP = 1.30, 0.282, 0.50, -20.0
NP_VLM = -101.3e-3     # m, I-07 / I-15 §6.3 [D]
NP_WL = -98.3e-3       # m, Weissinger-L, I-15 §6.3 [D]
MAC = (2.0 / 3.0) * (2 * S / (B * (1 + TAPER))) * \
      (1 + TAPER + TAPER ** 2) / (1 + TAPER)
CG_TARGET = -119e-3    # m, 18.7 % MAC, SM 8 %
R_CG = 5e-3            # m, docs/00 §3.3
AUW_REF, V_STALL_REF = 1.620, 45.0   # km/h de referencia a 1620 g
NOSE_POD_TIP = -132e-3               # guia §7.6 (v0.2)

# --- tablas de masas (Justification §3.1; boom PROVISIONAL [E], F2) ---
COMPONENTS = [
    ("Shell (centroide del planform)", 0.600, -49e-3),
    ("Carbon (tubo en linea c/4)",     0.070, -142e-3),
    ("Motor + helice",                 0.210, +217e-3),
    ("ESC",                            0.035, +40e-3),
    ("Avionica (FC, pitot, GPS, RX, cableria)", 0.110, -10e-3),
    ("Servos + masa de balance",       0.120, -5e-3),
    ("Hardware",                       0.020, +50e-3),
]
BOOM_MASS, BOOM_STATION = 0.040, -320e-3   # PROVISIONAL [E]
PACKS = [("4S1P", 0.300), ("6S1P", 0.455), ("4S2P", 0.605), ("6S2P", 0.910)]
# Envolventes reales de pack terminado (I-16, battery_pack_layout.py [D]):
# 4S1P 2x2 y 6S1P 2x3, orientacion A (eje de celula paralelo a x):
PACK_LEN = {"4S1P": 0.1532, "6S1P": 0.1532}
# 4S2P (8 celdas) y 6S2P (12 celdas) NO CABEN en el bay de una capa
# (I-16: ninguna disposicion n_z=1 entra en 200x70x32) -> fuera por geometria.
# v0.2 bay (sin boom): extremo delantero -131.5, trasero +48.5 (guia §9)


def planform_centroid():
    """Centroide de area del planform (validacion de la estacion de la shell)."""
    y = np.linspace(0, B / 2, 20001)
    cr = 2 * S / (B * (1 + TAPER))
    c = cr * (1 - (1 - TAPER) * y / (B / 2))
    x_c4 = y * np.tan(np.radians(SWEEP))
    x_mid = x_c4 - c / 4.0 + c / 2.0
    return np.trapezoid(x_mid * c, y) / np.trapezoid(c, y)


def pack_station(m_no_batt, mom_no_batt, m_pack, cg):
    """Estacion de pack para un CG dado."""
    return (cg * (m_no_batt + m_pack) - mom_no_batt) / m_pack


def main():
    print("=" * 70)
    print("BALANCE DE MASAS Y CG — OP-01 (boom de bateria)")
    print("=" * 70)
    xc = planform_centroid()
    print(f"\n  Validacion: centroide del planform = {xc*1000:+.1f} mm "
          f"(tabla de masas: -49 mm)  ->  {'OK' if abs(xc*1000+49) < 2 else 'DESVIACION'}")
    print(f"  MAC = {MAC*1000:.1f} mm  (I-07: 224.9)   NP = {NP_VLM*1000:+.1f} / "
          f"{NP_WL*1000:+.1f} mm (VLM / Weissinger-L)")

    comps = COMPONENTS + [("Boom de bateria (estructura)", BOOM_MASS, BOOM_STATION)]
    m0 = sum(m for _, m, _ in comps)
    mm0 = sum(m * x for _, m, x in comps)
    print("\n  Tabla de masas (sin pack):")
    for name, m, x in comps:
        print(f"    {name:42s} {m*1000:6.0f} g  x = {x*1000:+7.1f} mm")
    print(f"    {'Subtotal':42s} {m0*1000:6.0f} g  CG = {mm0/m0*1000:+7.1f} mm")

    print("\n" + "-" * 70)
    print("ESTACIONES DE PACK PARA CG = -119 mm (SM 8 %)  y banda R-CG +/-5 mm")
    print("-" * 70)
    for name, mp in PACKS:
        x_t = pack_station(m0, mm0, mp, CG_TARGET)
        x_f = pack_station(m0, mm0, mp, CG_TARGET - R_CG)
        x_a = pack_station(m0, mm0, mp, CG_TARGET + R_CG)
        print(f"  {name:5s} {mp*1000:5.0f} g  ->  pack en x = {x_t*1000:+7.1f} mm  "
              f"(banda {x_f*1000:+7.1f} ... {x_a*1000:+7.1f} mm)")

    print("\n" + "-" * 70)
    print("BAY DE BATERIA (configuracion de referencia 6S1P, pack 153.2 mm I-16)")
    print("-" * 70)
    x6 = pack_station(m0, mm0, 0.455, CG_TARGET)
    pl = PACK_LEN["6S1P"]
    CLEAR = 0.005                       # holgura de extremo
    bay_fwd = pack_station(m0, mm0, 0.455, CG_TARGET - R_CG) - pl / 2 - CLEAR
    bay_aft = pack_station(m0, mm0, 0.455, CG_TARGET + R_CG) + pl / 2 + CLEAR
    boom_len = bay_fwd - NOSE_POD_TIP
    print(f"  Pack 6S1P: {pl*1000:.1f} mm de largo, centro en x = {x6*1000:+.1f} mm "
          f"(banda {pack_station(m0, mm0, 0.455, CG_TARGET-R_CG)*1000:+.1f} ... "
          f"{pack_station(m0, mm0, 0.455, CG_TARGET+R_CG)*1000:+.1f} mm)")
    print(f"  Bay: {bay_fwd*1000:+.1f} ... {bay_aft*1000:+.1f} mm "
          f"({(bay_aft-bay_fwd)*1000:.0f} mm de largo)")
    print(f"  Boom: desde la punta del nose pod ({NOSE_POD_TIP*1000:+.0f} mm) hasta "
          f"{bay_fwd*1000:+.0f} mm -> extension de boom = {boom_len*1000:.0f} mm")

    print("\n  Cobertura del bay por configuracion (pack real de I-16):")
    for name, mp in PACKS:
        x_t = pack_station(m0, mm0, mp, CG_TARGET)
        if name not in PACK_LEN:
            print(f"    {name:5s} x = {x_t*1000:+7.1f} mm  ->  "
                  f"NO CABE en el bay (I-16: ninguna disposicion n_z=1 en 200x70x32)")
            continue
        ok = bay_fwd + PACK_LEN[name] / 2 <= x_t <= bay_aft - PACK_LEN[name] / 2
        print(f"    {name:5s} x = {x_t*1000:+7.1f} mm  ->  "
              f"{'DENTRO' if ok else 'FUERA'}  "
              f"{'(requerimiento R-CG a revisar en F2)' if not ok else ''}")

    print("\n" + "-" * 70)
    print("COMPROBACIONES DE ENVOLVENTE")
    print("-" * 70)
    for name, mp in PACKS:
        auw = m0 + mp
        v_stall = V_STALL_REF * np.sqrt(auw / AUW_REF)
        print(f"  {name:5s}: AUW = {auw*1000:.0f} g  ({auw/(S*100)*1000:.0f} g/dm2)  "
              f"V_stall ~ {v_stall:.1f} km/h")
    sm_t = (NP_VLM - CG_TARGET) / MAC * 100
    print(f"\n  SM en CG objetivo: {sm_t:.1f} % MAC")
    print(f"  Nota: el efecto de cuerpo central (I-07 §6) mueve el NP hacia delante "
          f"(direccion conocida, ~-10 mm); absorbe margen, no revierte la solucion.")


if __name__ == "__main__":
    main()
