#!/usr/bin/env python3
"""Vortex-lattice model for the forward-swept Salamandra flying wing.

The model calculates lift slope, neutral point, wash-in pitch moment and local
section loading. Geometry dictionaries cache their aerodynamic influence
matrix, so repeated angle-of-attack solves do not rebuild the O(N^2) Biot-
Savart system.

Conventions: x aft, y starboard, z up; negative quarter-chord sweep means
forward sweep; positive epsilon means wash-in.
"""
import numpy as np
from design_config import SWEEP_C4_DEG, TAPER, B, S


def geom(b, S, taper, sweep_c4_deg, tip_twist_deg, ny=40, nx=6):
    """Generate the panel mesh and return its geometry dictionary."""
    if b <= 0.0 or S <= 0.0 or not 0.0 < taper <= 1.0:
        raise ValueError("span and area must be positive; taper must be in (0, 1]")
    if ny < 4 or nx < 1:
        raise ValueError("ny must be at least 4 and nx at least 1")
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
    return {"panels": panels, "cps": np.array(cps), "eps": np.array(norms),
                "dy": np.array(dys), "xv": np.array(xs_c4), "chord": np.array(chords),
                "cr": cr, "ny": ny, "nx": nx, "b": b, "S": S, "cbar": cbar, "x_le_mac": x_le_mac}


def geom_cached(b, S, taper, sweep_c4_deg, tip_twist_deg, ny=40, nx=6):
    """`geom` with the aerodynamic influence matrix shared across calls.

    The matrix depends only on the mesh, not on twist or angle of attack, and
    building it is the O(N^2) Biot-Savart cost.  Callers that sweep twist or
    control deflection over one mesh (elevon_sizing, ventana_torsion) rebuilt
    it every time.  A shallow copy with its own `eps` keeps mutation safe.
    """
    key = (b, S, taper, sweep_c4_deg, ny, nx)
    template = _GEOM_CACHE.get(key)
    if template is None:
        template = geom(b, S, taper, sweep_c4_deg, 0.0, ny, nx)
        solve(template, 0.0)              # populates '_influence_matrix'
        _GEOM_CACHE[key] = template
    fresh = dict(template)
    half = b / 2.0
    fresh['eps'] = np.radians(tip_twist_deg) * np.abs(
        fresh['cps'][:, 1]) / half
    return fresh


_GEOM_CACHE = {}


def vortex_line(p, a, b_):
    """Velocity induced by a unit-circulation finite vortex segment."""
    r1, r2 = p - a, p - b_
    cr = np.cross(r1, r2)
    cr2 = np.dot(cr, cr)
    n1, n2 = np.linalg.norm(r1), np.linalg.norm(r2)
    if cr2 < 1e-12 or n1 < 1e-9 or n2 < 1e-9:
        return np.zeros(3)
    r0 = b_ - a
    k = (np.dot(r0, r1) / n1 - np.dot(r0, r2) / n2) / (4 * np.pi * cr2)
    return k * cr


def vortex_line_many(points, a, b_):
    """Vectorized unit-vortex velocity for an array of field points."""
    points = np.asarray(points, dtype=float)
    r1, r2 = points - a, points - b_
    cross = np.cross(r1, r2)
    cross2 = np.einsum('ij,ij->i', cross, cross)
    n1 = np.linalg.norm(r1, axis=1)
    n2 = np.linalg.norm(r2, axis=1)
    valid = (cross2 >= 1e-12) & (n1 >= 1e-9) & (n2 >= 1e-9)
    scale = np.zeros(len(points))
    r0 = b_ - a
    scale[valid] = (
        (r1[valid] @ r0) / n1[valid]
        - (r2[valid] @ r0) / n2[valid]
    ) / (4.0 * np.pi * cross2[valid])
    return scale[:, None] * cross


def horseshoe(p, a, b_, far=1e4):
    """Horseshoe vortex with trailing legs extending downstream (+x)."""
    a_inf = a + np.array([far, 0.0, 0.0])
    b_inf = b_ + np.array([far, 0.0, 0.0])
    return (vortex_line(p, a_inf, a)
            + vortex_line(p, a, b_)
            + vortex_line(p, b_, b_inf))


def horseshoe_many(points, a, b_, far=1e4):
    """Vectorized horseshoe velocity for all control points."""
    a_inf = a + np.array([far, 0.0, 0.0])
    b_inf = b_ + np.array([far, 0.0, 0.0])
    return (vortex_line_many(points, a_inf, a)
            + vortex_line_many(points, a, b_)
            + vortex_line_many(points, b_, b_inf))


def solve(g, alpha_deg, U=1.0):
    if U <= 0.0:
        raise ValueError("freestream speed must be positive")
    n = len(g['panels'])
    A = g.get('_influence_matrix')
    if A is None:
        A = np.zeros((n, n))
        for j, (a, b_) in enumerate(g['panels']):
            A[:, j] = horseshoe_many(g['cps'], a, b_)[:, 2]
        g['_influence_matrix'] = A
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
    g = geom_cached(b, S, taper, sweep, twist, ny, nx)
    cbar = g['cbar']            # already computed by `geom`; `mac` duplicated it

    CL1, Cm1, _, _ = solve(g, 0.0)
    CL2, Cm2, _, _ = solve(g, 4.0)

    CLa = (CL2 - CL1) / np.radians(4.0)
    dCm_dCL = (Cm2 - Cm1) / (CL2 - CL1)
    x_np = -dCm_dCL * cbar                       # respecto a c/4 de raiz

    if verbose:
        print(f"  cr={g['cr']*1000:.0f} mm  ct={g['cr']*taper*1000:.0f} mm  "
              f"MAC={cbar*1000:.1f} mm")
        print(f"  CL_alpha = {CLa:.3f} /rad")
        pct = (x_np - g['x_le_mac']) / cbar * 100
        print(f"  x_NP = {x_np*1000:+.1f} mm (from root c/4) -> {pct:.1f} % MAC")
        print(f"  Cm0 (a CL=0) = {Cm1 - CL1*dCm_dCL:+.4f}")
    return {"g": g, "cbar": cbar, "CLa": CLa, "x_np": x_np, "Cm0": Cm1 - CL1 * dCm_dCL,
                "dCm_dCL": dCm_dCL}


def cl_local(g, dL, q=0.5):
    """Chord-averaged local section lift coefficient."""
    if q <= 0.0:
        raise ValueError("dynamic pressure must be positive")
    ny, nx = g['ny'], g['nx']
    dL = dL.reshape(ny, nx).sum(axis=1)
    dy = g['dy'].reshape(ny, nx)[:, 0]
    c = g['chord'].reshape(ny, nx)[:, 0]
    y = g['cps'][:, 1].reshape(ny, nx)[:, 0]
    return y, dL / (q * c * dy), c


def validation_checks():
    """Independent checks the solver must pass exactly or within a stated band.

    The former suite accepted the lift slope "within 8 percent of Helmbold" and
    the straight-wing neutral point "within 1.5 percent MAC".  Neither could
    discriminate: Helmbold is itself an approximation, and 8 percent is wider
    than any error the discretisation actually makes.  Correction C17 (a missing
    MAC normalisation) is exactly the class of defect they would have missed, so
    the checks below are the ones that catch it: exact linear-model identities,
    exact symmetry, and a bounded mesh-convergence statement.
    """
    result = analiza(B, S, 1.0, 0.0, 0.0, verbose=False)
    ar = B * B / S
    helmbold = 2 * np.pi * ar / (2 + np.sqrt(ar**2 + 4))

    # Vectorised Biot-Savart against the scalar reference.
    p = np.array([[0.7, 0.1, 0.2], [0.8, -0.3, 0.4]])
    a = np.array([0.1, -0.2, 0.0])
    b_ = np.array([0.2, 0.4, 0.0])
    vectorized = vortex_line_many(p, a, b_)
    scalar = np.array([vortex_line(row, a, b_) for row in p])

    # Exact linearity: the model is linear, so CL and Cm must be affine in
    # alpha to machine precision.  A non-linear residual means the boundary
    # condition or the influence matrix is being rebuilt inconsistently.
    g = geom_cached(B, S, TAPER, SWEEP_C4_DEG, 0.0)
    cl = np.array([solve(g, alpha)[0] for alpha in (0.0, 2.0, 4.0)])
    cm = np.array([solve(g, alpha)[1] for alpha in (0.0, 2.0, 4.0)])
    linear_cl = abs((cl[2] - cl[1]) - (cl[1] - cl[0]))
    linear_cm = abs((cm[2] - cm[1]) - (cm[1] - cm[0]))

    # Superposition in twist: alpha and wash-in enter the same linear boundary
    # condition, so their effects must add exactly.
    g_twist = geom_cached(B, S, TAPER, SWEEP_C4_DEG, 3.0)
    cl_both = solve(g_twist, 4.0)[0]
    cl_alpha_only = solve(g, 4.0)[0]
    cl_twist_only = solve(g_twist, 0.0)[0]
    cl_zero = solve(g, 0.0)[0]
    superposition = abs(cl_both - (cl_alpha_only + cl_twist_only - cl_zero))

    # Spanwise symmetry of an untwisted symmetric wing.
    _, _, strip_lift, _ = solve(g, 4.0)
    y_strip, cl_strip, _ = cl_local(g, strip_lift)
    asymmetry = float(np.max(np.abs(cl_strip - cl_strip[::-1])))

    # THE C17 GUARD.  Re-take the pitching moment about the computed neutral
    # point: by definition dCm/dCL there must be zero.  A missing or wrong MAC
    # normalisation breaks this identity immediately, whereas comparing a lift
    # slope against an approximate formula does not.
    released = analiza(B, S, TAPER, SWEEP_C4_DEG, 0.0, verbose=False)
    x_np = released["x_np"]
    g_ref = geom_cached(B, S, TAPER, SWEEP_C4_DEG, 0.0)
    residuals = []
    for alpha in (0.0, 4.0):
        cl_a, _, strip, _ = solve(g_ref, alpha)
        moment_about_np = -((strip * (g_ref["xv"] - x_np)).sum()) / (
            0.5 * g_ref["S"] * g_ref["cbar"])
        residuals.append((cl_a, moment_about_np))
    (cl0, cm0), (cl1, cm1) = residuals
    dcm_dcl_at_np = abs((cm1 - cm0) / (cl1 - cl0))

    # Mesh convergence, stated as a bound instead of left unmeasured.
    coarse = analiza(B, S, TAPER, SWEEP_C4_DEG, 0.0, ny=40, nx=6,
                     verbose=False)["x_np"]
    fine = analiza(B, S, TAPER, SWEEP_C4_DEG, 0.0, ny=80, nx=12,
                   verbose=False)["x_np"]

    return {
        "CL is exactly linear in alpha": linear_cl < 1e-12,
        "Cm is exactly linear in alpha": linear_cm < 1e-12,
        "alpha and twist superpose exactly": superposition < 1e-12,
        "an untwisted symmetric wing carries a symmetric load":
            asymmetry < 1e-12,
        "C17 guard: dCm/dCL vanishes about the computed neutral point":
            dcm_dcl_at_np < 1e-9,
        "canonical mesh is converged to better than 0.4 mm in x_NP":
            abs(coarse - fine) < 0.4e-3,
        "straight untwisted wing puts the NP just aft of the quarter chord":
            0.005 < abs(result['x_np']) / result['cbar'] < 0.015,
        "influence matrix is cached after a solve":
            '_influence_matrix' in result['g'],
        "vectorized Biot-Savart matches scalar reference":
            np.allclose(vectorized, scalar, rtol=1e-12, atol=1e-12),
        # Helmbold is an APPROXIMATION, not a reference solution: the residual
        # difference is the classical lifting-line/lifting-surface gap, so this
        # stays a wide sanity band and is never the discriminating check.
        "lift slope is within the lifting-surface/Helmbold gap":
            abs(result['CLa'] - helmbold) / helmbold < 0.08,
    }


def main():
    SWEEP = SWEEP_C4_DEG

    print("=" * 68)
    print("VALIDATION: STRAIGHT AR-6 WING, ZERO SWEEP AND TWIST")
    print("=" * 68)
    r = analiza(B, S, 1.0, 0.0, 0.0)
    AR = B * B / S
    teo = 2 * np.pi * AR / (2 + np.sqrt(AR ** 2 + 4))
    print(f"  theoretical CL_alpha (Helmbold) = {teo:.3f} /rad  "
          f"-> error {100*(r['CLa']-teo)/teo:+.1f} %")
    print(f"  expected NP from root c/4 = 0.0 mm "
          f"(obtained {r['x_np']*1000:+.1f} mm)")

    print()
    print("=" * 68)
    print(f"PROJECT: b={B*1000:.0f} mm  S={S} m2  AR={AR:.2f}  "
          f"lambda={TAPER}  flecha c/4={SWEEP} deg")
    print("=" * 68)
    for tw in [0.0, 1.0, 2.0, 3.0, 4.0]:
        print(f"\n-- tip wash-in = {tw:+.1f} deg --")
        analiza(B, S, TAPER, SWEEP, tw)

    checks = validation_checks()
    print("\nVALIDATION CHECKS")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
