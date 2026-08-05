#!/usr/bin/env python3
"""
C2: independent neutral-point check — Weissinger-L (swept lifting line).

Method (textbook Weissinger, 1947; as used in Roskam/Anderson-type lifting-line
formulations for swept wings):
  - One horseshoe per span station; bound vortex on the c/4 line (swept),
    trailing vortices to downstream infinity at the station boundaries.
  - Control points at the 3/4-chord point of each station (mid-station).
  - Boundary condition: zero normal flow at the control points.
  - Solution: circulation distribution -> CL, Cm about root c/4 -> dCm/dCL -> NP.

This is structurally different from the in-house panel VLM
(calculations/vlm_ala_volante.py): 1-D lifting line vs 2-D vortex lattice,
c/4-bound line vs per-panel quarter-chord vortices. Agreement on the NP is
the C2 cross-check ("two methods that disagree = error in one").

Conventions (same as the VLM): x backward, y starboard, z up; lambda_c4
negative = forward sweep; all output [D].
"""
import math

import numpy as np


def vortex_line(p, a, b_):
    """Induced velocity of a unit-circulation vortex segment (Biot-Savart)."""
    r1, r2 = p - a, p - b_
    cr = np.cross(r1, r2)
    cr2 = np.dot(cr, cr)
    n1, n2 = np.linalg.norm(r1), np.linalg.norm(r2)
    if cr2 < 1e-12 or n1 < 1e-9 or n2 < 1e-9:
        return np.zeros(3)
    r0 = b_ - a
    k = (np.dot(r0, r1) / n1 - np.dot(r0, r2) / n2) / (4 * np.pi * cr2)
    return k * cr


def horseshoe(p, a, b_, far=1e5):
    """Horseshoe: bound segment a->b plus two trailing legs to +infinity."""
    a_inf = a + np.array([far, 0.0, 0.0])
    b_inf = b_ + np.array([far, 0.0, 0.0])
    return (vortex_line(p, a_inf, a) + vortex_line(p, a, b_) +
            vortex_line(p, b_, b_inf))


def weissinger(b, S, taper, sweep_c4_deg, ny=80):
    """Solve the Weissinger-L system. Returns dict of results."""
    cr = 2.0 * S / (b * (1.0 + taper))
    tanL = math.tan(math.radians(sweep_c4_deg))
    half = b / 2.0

    # cosine stations across the FULL span (mirrored)
    th = np.linspace(0, math.pi, ny + 1)
    ys = -half * np.cos(th)

    # station boundaries on the c/4 line; control points at 3/4 chord
    bounds = []
    cps = []
    dy = []
    for j in range(ny + 1):
        y = ys[j]
        eta = abs(y) / half
        c = cr * (1.0 - (1.0 - taper) * eta)
        bounds.append(np.array([abs(y) * tanL, y, 0.0]))   # c/4 point (both
                                                           # halves sweep forward)
    for j in range(ny):
        y1, y2 = ys[j], ys[j + 1]
        ym = 0.5 * (y1 + y2)
        eta = abs(ym) / half
        c = cr * (1.0 - (1.0 - taper) * eta)
        cps.append(np.array([abs(ym) * tanL + c / 2.0, ym, 0.0]))  # 3/4 chord
        dy.append(y2 - y1)
    cps = np.array(cps)
    dy = np.array(dy)

    n = ny
    A = np.zeros((n, n))
    for i, p in enumerate(cps):
        for j in range(n):
            A[i, j] = horseshoe(p, bounds[j], bounds[j + 1])[2]

    cbar = (2.0 / 3.0) * cr * (1 + taper + taper ** 2) / (1 + taper)

    def solve(alpha_deg, twist_deg):
        al = math.radians(alpha_deg)
        rhs = np.empty(n)
        for i, ym in enumerate(ys[:-1]):
            eta = abs(0.5 * (ys[i] + ys[i + 1])) / half
            rhs[i] = -(al + math.radians(twist_deg) * eta)
        gamma = np.linalg.solve(A, rhs)
        L = float(np.sum(gamma * dy))                      # rho=U=1
        M = -float(np.sum(gamma * dy * np.array(
            [abs(0.5 * (ys[j] + ys[j + 1])) * tanL for j in range(n)])))
        q = 0.5
        return L / (q * S), M / (q * S * cbar)

    CL1, Cm1 = solve(0.0, 0.0)
    CL2, Cm2 = solve(4.0, 0.0)
    CLa = (CL2 - CL1) / math.radians(4.0)
    dCm_dCL = (Cm2 - Cm1) / (CL2 - CL1)
    x_np = -dCm_dCL * cbar
    y_mac = (b / 6.0) * (1 + 2 * taper) / (1 + taper)
    x_le_mac = y_mac * tanL - cbar / 4.0
    pct = (x_np - x_le_mac) / cbar * 100
    return dict(cr=cr, cbar=cbar, CLa=CLa, x_np=x_np, pct_mac=pct,
                dCm_dCL=dCm_dCL)


if __name__ == "__main__":
    print("=" * 68)
    print("C2 — WEISSINGER-L independent NP check (all [D])")
    print("=" * 68)

    # 1) validation: straight rectangular wing, AR 6, S = 0.282 m2
    b_val = math.sqrt(6.0 * 0.282)
    r = weissinger(b_val, 0.282, 1.0, 0.0, ny=100)
    teo = 2 * math.pi * 6.0 / (2 + math.sqrt(6.0 ** 2 + 4))
    print(f"  VALIDATION: straight AR 6 -> CL_alpha = {r['CLa']:.3f} /rad "
          f"(Helmbold {teo:.3f}, err {100*(r['CLa']-teo)/teo:+.1f} %)")
    print(f"  VALIDATION: NP = {r['pct_mac']:.2f} % MAC (expect ~25 %)")

    # 2) project wing
    B, S, TAPER, SWEEP = 1.30, 0.282, 0.50, -20.0
    r = weissinger(B, S, TAPER, SWEEP, ny=100)
    print(f"\n  PROJECT: b=1300, S=0.282, lambda=0.5, sweep c/4 = -20 deg")
    print(f"  CL_alpha  = {r['CLa']:.3f} /rad")
    print(f"  x_NP      = {r['x_np']*1000:+.1f} mm (ref root c/4)")
    print(f"  NP        = {r['pct_mac']:.2f} % MAC")
    print(f"  VLM reference: x_NP = -101.3 mm, 26.7 % MAC (I-07)")

    # 3) mesh convergence
    for ny in (40, 80, 160, 320):
        rr = weissinger(B, S, TAPER, SWEEP, ny=ny)
        print(f"  ny={ny:>4}: NP = {rr['pct_mac']:.2f} % MAC, "
              f"CLa = {rr['CLa']:.3f}")
