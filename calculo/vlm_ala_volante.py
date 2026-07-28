#!/usr/bin/env python3
"""
VLM (vortex lattice) para ala volante de flecha invertida.
Calcula: punto neutro, margen estatico, torsion requerida para trim,
y distribucion de cl local para verificar margen de perdida en punta.

Convenciones:
  x  positivo hacia atras
  y  positivo hacia estribor
  z  positivo hacia arriba
  Lambda_c4 negativo = flecha invertida
  epsilon positivo = wash-in (punta a mayor incidencia)
"""
import numpy as np


def geom(b, S, taper, sweep_c4_deg, tip_twist_deg, ny=40, nx=6):
    """Genera malla de paneles. Devuelve esquinas y datos por panel."""
    cr = 2.0 * S / (b * (1.0 + taper))
    tanL = np.tan(np.radians(sweep_c4_deg))
    half = b / 2.0

    # estaciones de envergadura (coseno: mas denso en punta y raiz)
    th = np.linspace(0, np.pi, ny + 1)
    ys = -half * np.cos(th)          # de -half a +half

    panels, cps, norms, dys, xs_c4, chords, twists = [], [], [], [], [], [], []

    for j in range(ny):
        y1, y2 = ys[j], ys[j + 1]
        ym = 0.5 * (y1 + y2)
        eta = abs(ym) / half
        c = cr * (1.0 - (1.0 - taper) * eta)
        x_c4 = abs(ym) * tanL
        x_le = x_c4 - c / 4.0
        eps = np.radians(tip_twist_deg) * eta      # lineal desde la raiz

        for i in range(nx):
            xa = x_le + c * i / nx
            xb = x_le + c * (i + 1) / nx
            dc = (xb - xa)
            # vortice ligado a 1/4 del panel, punto de control a 3/4
            xv = xa + 0.25 * dc
            xc = xa + 0.75 * dc
            # extremos del vortice ligado, siguiendo la flecha local
            c1 = cr * (1.0 - (1.0 - taper) * abs(y1) / half)
            c2 = cr * (1.0 - (1.0 - taper) * abs(y2) / half)
            xv1 = abs(y1) * tanL - c1 / 4.0 + c1 * (i + 0.25) / nx
            xv2 = abs(y2) * tanL - c2 / 4.0 + c2 * (i + 0.25) / nx
            panels.append((np.array([xv1, y1, 0.0]), np.array([xv2, y2, 0.0])))
            cps.append(np.array([xc, ym, 0.0]))
            norms.append(eps)
            dys.append(y2 - y1)
            xs_c4.append(xv)
            chords.append(c)
            twists.append(eps)

    cbar = (2.0 / 3.0) * cr * (1 + taper + taper ** 2) / (1 + taper)
    y_mac = (b / 6.0) * (1 + 2 * taper) / (1 + taper)
    x_le_mac = y_mac * tanL - cbar / 4.0
    return dict(panels=panels, cps=np.array(cps), eps=np.array(norms),
                dy=np.array(dys), xv=np.array(xs_c4), chord=np.array(chords),
                cr=cr, ny=ny, nx=nx, b=b, S=S, cbar=cbar, x_le_mac=x_le_mac)


def vortex_line(p, a, b_):
    """Velocidad inducida por segmento de vortice de circulacion unidad."""
    r1, r2 = p - a, p - b_
    cr = np.cross(r1, r2)
    cr2 = np.dot(cr, cr)
    n1, n2 = np.linalg.norm(r1), np.linalg.norm(r2)
    if cr2 < 1e-12 or n1 < 1e-9 or n2 < 1e-9:
        return np.zeros(3)
    r0 = b_ - a
    k = (np.dot(r0, r1) / n1 - np.dot(r0, r2) / n2) / (4 * np.pi * cr2)
    return k * cr


def horseshoe(p, a, b_, far=1e4):
    """Herradura: estelas hacia +x desde a y b_, mas el segmento ligado."""
    a_inf = a + np.array([far, 0.0, 0.0])
    b_inf = b_ + np.array([far, 0.0, 0.0])
    return (vortex_line(p, a_inf, a)
            + vortex_line(p, a, b_)
            + vortex_line(p, b_, b_inf))


def solve(g, alpha_deg, U=1.0):
    n = len(g['panels'])
    A = np.zeros((n, n))
    for i, p in enumerate(g['cps']):
        for j, (a, b_) in enumerate(g['panels']):
            A[i, j] = horseshoe(p, a, b_)[2]     # componente z
    alpha = np.radians(alpha_deg)
    rhs = -U * (alpha + g['eps'])                # condicion de contorno linealizada
    gamma = np.linalg.solve(A, rhs)

    rho = 1.0
    dL = rho * U * gamma * g['dy']               # Kutta-Joukowski por panel
    L = dL.sum()
    M = -(dL * g['xv']).sum()                    # morro arriba positivo
    q = 0.5 * rho * U ** 2
    CL = L / (q * g['S'])
    Cm = M / (q * g['S'] * g['cbar'])      # adimensionalizado con la CMA
    return CL, Cm, dL, gamma


def mac(b, S, taper):
    cr = 2.0 * S / (b * (1.0 + taper))
    return (2.0 / 3.0) * cr * (1 + taper + taper ** 2) / (1 + taper)


def analiza(b, S, taper, sweep, twist, ny=40, nx=6, verbose=True):
    g = geom(b, S, taper, sweep, twist, ny, nx)
    cbar = mac(b, S, taper)

    CL1, Cm1, _, _ = solve(g, 0.0)
    CL2, Cm2, dL2, _ = solve(g, 4.0)

    CLa = (CL2 - CL1) / np.radians(4.0)
    dCm_dCL = (Cm2 - Cm1) / (CL2 - CL1)
    x_np = -dCm_dCL * cbar                       # respecto a c/4 de raiz

    if verbose:
        print(f"  cr={g['cr']*1000:.0f} mm  ct={g['cr']*taper*1000:.0f} mm  "
              f"CMA={cbar*1000:.1f} mm")
        print(f"  CL_alpha = {CLa:.3f} /rad")
        pct = (x_np - g['x_le_mac']) / cbar * 100
        print(f"  x_NP = {x_np*1000:+.1f} mm (ref c/4 raiz)  ->  {pct:.1f} % CMA")
        print(f"  Cm0 (a CL=0) = {Cm1 - CL1*dCm_dCL:+.4f}")
    return dict(g=g, cbar=cbar, CLa=CLa, x_np=x_np, Cm0=Cm1 - CL1 * dCm_dCL,
                dCm_dCL=dCm_dCL)


def cl_local(g, dL, q=0.5):
    """cl de seccion, promediado en cuerda."""
    ny, nx = g['ny'], g['nx']
    dL = dL.reshape(ny, nx).sum(axis=1)
    dy = g['dy'].reshape(ny, nx)[:, 0]
    c = g['chord'].reshape(ny, nx)[:, 0]
    y = g['cps'][:, 1].reshape(ny, nx)[:, 0]
    return y, dL / (q * c * dy), c


if __name__ == "__main__":
    B, S, TAPER, SWEEP = 1.30, 0.282, 0.50, -20.0

    print("=" * 68)
    print("VALIDACION: ala recta AR 6 sin flecha ni torsion")
    print("=" * 68)
    r = analiza(B, S, 1.0, 0.0, 0.0)
    AR = B * B / S
    teo = 2 * np.pi * AR / (2 + np.sqrt(AR ** 2 + 4))
    print(f"  CL_alpha teorico (Helmbold) = {teo:.3f} /rad  "
          f"-> error {100*(r['CLa']-teo)/teo:+.1f} %")
    print(f"  NP esperado en c/4 = {0.25*r['cbar']*1000:.1f} mm")

    print()
    print("=" * 68)
    print(f"PROYECTO: b={B*1000:.0f} mm  S={S} m2  AR={AR:.2f}  "
          f"lambda={TAPER}  flecha c/4={SWEEP} deg")
    print("=" * 68)
    for tw in [0.0, 1.0, 2.0, 3.0, 4.0]:
        print(f"\n-- wash-in en punta = {tw:+.1f} deg --")
        analiza(B, S, TAPER, SWEEP, tw)
