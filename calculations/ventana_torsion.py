#!/usr/bin/env python3
"""
Ventana de torsion: cuanto wash-in hace falta para equilibrar, y cuanto
cabe antes de que la punta entre en perdida primero.

Es la decision central de la Fase 1.
"""
import numpy as np
from vlm_ala_volante import geom, solve, analiza, mac
from design_config import B, S, SWEEP_C4_DEG, TAPER

# --- configuracion Cruise, articulo #1 ---
SWEEP = SWEEP_C4_DEG
DESIGN_REF_MASS = 1.620        # kg; O1 target, not current 1.6852 kg budget
RHO = 1.225
V_CRUCERO = 95 / 3.6           # m/s
V_STALL = 45 / 3.6             # m/s
CL_SEC_MAX = 0.65              # cl_max de seccion [M] Ananda et al. 0.55-0.70
PROFILE_CM0 = 0.0016           # provisional MH60->13.5 %, I-15 / ADR-0040

WS = DESIGN_REF_MASS * 9.81 / S
CL_CRU = WS / (0.5 * RHO * V_CRUCERO ** 2)
CL_MAX_REQ = WS / (0.5 * RHO * V_STALL ** 2)

print("=" * 70)
print("VENTANA DE TORSION — configuracion Cruise")
print("=" * 70)
print(f"  Masa de referencia {DESIGN_REF_MASS:.3f} kg  (objetivo O1; presupuesto actual 1.685 kg)")
print(f"  Carga alar         {WS:.1f} N/m2  ({DESIGN_REF_MASS*1000/(S*100):.0f} g/dm2)")
print(f"  CL de crucero      {CL_CRU:.3f}   a {V_CRUCERO*3.6:.0f} km/h")
print(f"  CL_max requerido   {CL_MAX_REQ:.3f}   para perder a {V_STALL*3.6:.0f} km/h")
print(f"  cl_max de seccion  {CL_SEC_MAX:.2f}   [M]")

# --- punto neutro ---
r = analiza(B, S, TAPER, SWEEP, 0.0, verbose=False)
g0 = geom(B, S, TAPER, SWEEP, 0.0)
cbar = r['cbar']
np_pct = (r['x_np'] - g0['x_le_mac']) / cbar * 100
print(f"\n  PUNTO NEUTRO       {np_pct:.1f} % CMA   "
      f"(x = {r['x_np']*1000:+.0f} mm respecto a c/4 de raiz)")
print(f"  CL_alpha           {r['CLa']:.3f} /rad")
print(f"  CMA                {cbar*1000:.1f} mm")

# --- rendimiento del wash-in ---
r4 = analiza(B, S, TAPER, SWEEP, 4.0, verbose=False)
cm0_por_grado = r4['Cm0'] / 4.0
print(f"\n  Cm0 por grado de wash-in : {cm0_por_grado:+.5f} /deg")

# --- torsion requerida para equilibrar ---
print("\n" + "-" * 70)
print("LIMITE INFERIOR — wash-in necesario para trim en crucero")
print("-" * 70)
print(f"  MargenEst   Cm0 requerido   solo torsion   con perfil Cm0={PROFILE_CM0:+.4f}")
for sm in [0.06, 0.08, 0.10, 0.12, 0.15]:
    cm0_req = CL_CRU * sm
    tw_solo = cm0_req / cm0_por_grado
    tw_mixto = max(0.0, (cm0_req - PROFILE_CM0) / cm0_por_grado)
    print(f"    {sm*100:4.0f} %     {cm0_req:+.4f}        {tw_solo:5.2f} deg      "
          f"{tw_mixto:5.2f} deg")

# --- limite superior: perdida en punta ---
print("\n" + "-" * 70)
print("LIMITE SUPERIOR — reparto de cl en condicion de perdida")
print("-" * 70)
print("  Se busca alpha tal que el ala alcance CL_max requerido,")
print("  y se mira donde toca primero el cl_max de seccion.\n")
print("  wash-in   y(cl_max)   cl_raiz   cl_punta   cl_max local   margen")

for tw in [0.0, 2.0, 3.0, 4.0, 5.0, 6.0]:
    g = geom(B, S, TAPER, SWEEP, tw)
    # alpha que da CL_MAX_REQ
    CLa_, Cma_, _, _ = solve(g, 0.0)
    CLb_, _, _, _ = solve(g, 4.0)
    slope = (CLb_ - CLa_) / np.radians(4.0)
    alpha = np.degrees((CL_MAX_REQ - CLa_) / slope)
    CL, Cm, dL, _ = solve(g, alpha)

    ny, nx = g['ny'], g['nx']
    dLs = dL.reshape(ny, nx).sum(axis=1)
    dy = g['dy'].reshape(ny, nx)[:, 0]
    c = g['chord'].reshape(ny, nx)[:, 0]
    y = g['cps'][:, 1].reshape(ny, nx)[:, 0]
    cl = dLs / (0.5 * c * dy)

    half = y > 0
    yv, clv = y[half], cl[half]
    k = np.argmax(clv)
    eta_max = yv[k] / (B / 2)
    print(f"   {tw:4.1f} deg    {eta_max*100:4.0f} % b/2   "
          f"{clv[0]:+.3f}    {clv[-1]:+.3f}      {clv[k]:+.3f}        "
          f"{CL_SEC_MAX - clv[k]:+.3f}")

print("\n  eta = 0 % es la raiz, 100 % la punta.")
print("  Si el maximo se desplaza hacia la punta, se pierde la ventaja")
print("  principal de la flecha invertida (perdida por raiz primero).")
