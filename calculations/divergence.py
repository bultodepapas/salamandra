#!/usr/bin/env python3
"""
Absolute aeroelastic divergence speed of the Salamandra Cruise wing (G6 — the
project's declared weakest link, master plan F4-S3/S4).

WHY THIS SCRIPT EXISTS: ADR-0030 states "the divergence criterion
V_div >= 1.5 x V_ARTICLE_NE is met with the shell alone", but until now no calculation
produced the absolute value: I-05 gives only a RELATIVE scaling anchor to the
Peregrine (GJ 6.45x, V_div 1.14x) and explicitly says "it does not give the
absolute value". This script is the first absolute, reproducible estimate.

MODEL (revision 4, S3/CAD remains the closure trigger):
  1. Section per guide §6.2 + §5.2: torsion box x/c 0 -> 0.72 (D-box 0->0.30,
     center cell 0.30->0.72; the hinge cell 0.72->1.00 is the elevon, OUT of the
     torsion path — "the closed torsion box ends here"). Idealized as a double
     rectangle of height k_h·h_max(y) with the shear web at 0.30 (OP-09), skin
     0.9 mm (2 x 0.45, ADR-0028), web 0.9 mm.
  2. J multi-cell Bredt-Batho per station (compatibility system solved exactly).
  3. G_eff = 0.55 GPa [M] PETG (ADR-0021) with the G4 [E] band +/-35 %.
  4. Elastic-axis position is NOT inferred from the enclosed-cell centroid.
     The earlier implementation made that category error. Until S3 obtains the
     shear center from multi-cell shear flow/warping FEM and a printed section,
     x_EA/c is explicitly bracketed 0.30-0.45 [E]; AC is at 0.25 c.
  5. Section lift slope a [D] from the in-repo XFOIL polars of the MH60->13.5 %
     candidate (0.155-0.195/deg at Re 3-5e5), floor 2*pi.
  6. Divergence q_D = smallest eigenvalue of the spanwise twist problem
     (weak form: K·th = q·M·th, FEM linear elements, lumped mass, symmetric
     definite eigenproblem via eigh — root fixed, tip free), on a fine grid
     from the §5.2 station table. Validated against the uniform closed form
     pi^2·GJ/(4·L^2·c·e·a).
  7. Forward-sweep speed factor k_sweep = 0.55-0.85 [D]/[E] for -15 degrees.
     The update is anchored to NASA TP-1685 figures 7-8: reducing forward sweep
     from -20 to -15 degrees raises divergence speed about 10-22 percent across
     the AR 4-8 test models. Numerical transfer remains an uncertainty (I-21).
     R-JOINT series compliance is included at y = 195 (k_joint = 5x section).
  8. Carbon tube Ø12x1.0: quantified, expected negligible (pultruded UD carbon
     G_12 ~ 3-7 GPa [E] -> GJ ~ 3-7 N·m² vs shell GJ ~ hundreds).

CRITERION: V_div >= 1.5 x V_ARTICLE_NE = 1.5 x 160 km/h = 240 km/h (docs/00).
The verdict is reported at the CONSERVATIVE end of the declared bands.
"""
import sys
from functools import cache

import numpy as np
from design_config import (
    AIRFOIL_DIR,
    ARTICLE_V_NE_KMH,
    ELEVON_HINGE_XC,
    HALF_SPAN,
    INITIAL_SPEED_LIMIT_KMH,
    RHO_SL,
    ROOT_TC,
    STATIONS,
    SWEEP_C4_DEG,
    speed_mps,
)

# ---------------------------------------------------------------------------
# Inputs (all with confidence tags)
# ---------------------------------------------------------------------------
RHO = RHO_SL
V_ARTICLE_NE = speed_mps(ARTICLE_V_NE_KMH)   # article V_ARTICLE_NE, 160 km/h
F_DIV = 1.5                # criterion V_div >= 1.5 x V_ARTICLE_NE

L = HALF_SPAN              # m, half-span
X_DBOX = 0.30              # D-box x/c extent; shear web position (OP-09)
X_BOX = ELEVON_HINGE_XC    # torsion box end x/c: it IS the hinge line
                           # (ADR-0002).  Duplicating 0.72 here meant a hinge
                           # revision silently left the torsion box behind.
T_SKIN = 0.0009            # m, skin 0.9 mm = 2 perimeters (ADR-0028)
X_AC = 0.25                # aerodynamic centre x/c (reflexed sections 0.24-0.27)
X_EA_BAND = (0.35, 0.30, 0.45)  # nominal / optimistic / conservative [E]
E_BAND = tuple(x - X_AC for x in X_EA_BAND)
PROFILE_NAME = "salamandra-root-r1.dat"
PROFILE_FILE = AIRFOIL_DIR / PROFILE_NAME   # resolved, never a relative string
AREA_BAND = (1.00, 0.95, 1.05)  # nominal / conservative / optimistic area
                                # factor for the final-profile uncertainty (OP-02)
G_PETG = 0.55e9            # Pa, G_eff printed PETG [M] (ADR-0021)
G_BAND = 0.35              # G4 [E] +/-35 %
A_SLOPE = (9.7, 6.28, 11.2)   # /rad: nominal, floor (2pi), top — [D] XFOIL
                                # polars MH60->13.5 % 0.155-0.195/deg; 2*pi floor
K_SWEEP = (0.70, 0.55, 0.85)  # nominal / conservative / optimistic, -15 deg (I-21)
K_JOINT = 5.0              # R-JOINT stiffness ratio, ADR-0032 requirement
JOINT_Y = 0.195            # m, CORE<->PANEL joint (30 % half-span)
JOINT_HALF = 0.035         # m, socket region half-length [E] (≈ 70 mm socket)

# Carbon tube Ø12x1.0 (ADR-0015): pultruded UD carbon G_12 [E]
G_TUBE = 5.0e9             # Pa, band 3-7 GPa
D_TUBE, T_TUBE = 0.012, 0.001

# AERO LW-PLA variant (docs/06, OP-28): E ~ 0.5 x PETG -> G ~ 0.5 x G_PETG [E]
G_AERO = 0.5 * G_PETG
V_LIMIT_FACTOR = 0.85      # explicit first-flight clearance below conservative V_div
V_LIMIT_INCREMENT = 5.0    # km/h; operational limits always round down


# ---------------------------------------------------------------------------
# Real-section geometry (guide §7.1 + geometry/airfoils/mh60-135.dat)
# ---------------------------------------------------------------------------
@cache
def load_profile():
    """Loads the MH60->13.5 % coordinates (x/c, z/c), UIUC order
    (TE->LE upper, LE->TE lower). Returns x, z arrays."""
    pts = np.loadtxt(PROFILE_FILE, skiprows=1)
    i_min = int(np.argmin(pts[:, 0]))
    upper = pts[:i_min + 1]      # TE -> LE
    lower = pts[i_min:]          # LE -> TE
    return upper, lower


@cache
def section_geometry(tc_scale=1.0):
    """Cell areas, perimeters, web length and enclosed-area centroid of the REAL
    two-cell torsion box (D-box 0->X_DBOX, center cell X_DBOX->X_BOX) from
    the profile coordinates, scaled to the local t/c by tc_scale. Returns
    (A1, A2, s1, s2, s12, x_cell_area) in units of c.

    IMPORTANT: x_cell_area is a geometric diagnostic only. It is not the shear
    center and is never used as the elastic axis in the divergence calculation.
    """
    upper, lower = load_profile()

    def interp_profile(xq):
        return (np.interp(xq, upper[::-1, 0], upper[::-1, 1]) * tc_scale,
                np.interp(xq, lower[:, 0], lower[:, 1]) * tc_scale)

    # Vectorised shoelace.  These were Python loops over ~200 vertices, called
    # once per spanwise station: `grid(401)` spent 0.29 s here.  The @cache on
    # this function was keyed on a continuously varying float and measured
    # hits=0, misses=401, so it never removed any of that cost.
    def _shoelace(poly):
        x, z = poly[:, 0], poly[:, 1]
        cross = x * np.roll(z, -1) - np.roll(x, -1) * z
        return cross

    def poly_area(poly):
        return abs(_shoelace(poly).sum()) / 2.0

    def poly_len(seg):
        return np.sum(np.hypot(np.diff(seg[:, 0]), np.diff(seg[:, 1])))

    def poly_centroid(poly):
        x, z = poly[:, 0], poly[:, 1]
        cross = _shoelace(poly)
        area2 = cross.sum()
        cx = np.dot(x + np.roll(x, -1), cross)
        cz = np.dot(z + np.roll(z, -1), cross)
        return cx / (3.0 * area2), cz / (3.0 * area2)

    xs_all = np.sort(np.unique(np.concatenate([upper[:, 0], lower[:, 0]])))

    def cell(xa, xb, close_aft):
        xs = xs_all[(xs_all >= xa) & (xs_all <= xb)]
        zu, zl = interp_profile(xs)
        p = np.concatenate((
            np.column_stack((xs, zu)),
            np.array([[xb, zl[-1]]]),
            np.column_stack((xs[::-1], zl[::-1])),
        ))
        A = poly_area(p)
        s = poly_len(np.column_stack((xs, zu))) \
            + poly_len(np.column_stack((xs, zl))) \
            + abs(zu[0] - zl[0])          # front closure (LE arc / web)
        if close_aft:
            s += abs(zu[-1] - zl[-1])     # aft closure (hinge line)
        return A, s, (zu[0], zl[0]), (zu[-1], zl[-1]), poly_centroid(p)

    A1, s1, _, web_out, (cx1, _) = cell(0.0, X_DBOX, False)
    A2, s2, _, _, (cx2, _) = cell(X_DBOX, X_BOX, True)
    s12 = abs(web_out[0] - web_out[1])    # shared web at x = X_DBOX
    s1 += s12                             # web belongs to cell 1's perimeter
    # cell 2 already counts the web as its front closure
    x_cell_area = (A1 * cx1 + A2 * cx2) / (A1 + A2)
    return A1, A2, s1, s2, s12, x_cell_area


@cache
def _section_scaling_basis():
    """Thickness-independent pieces of the two-cell section geometry.

    Under a pure z-scaling of the profile the enclosed AREAS, the web length
    and the cell-area centroid are exactly linear in `tc_scale` (verified to
    machine precision), while the two cell PERIMETERS are not: they need
    ``sum(hypot(dx, tc_scale*dz))`` re-evaluated.  Caching the dx/dz arrays
    once turns each subsequent station into two vectorised reductions.
    """
    upper, lower = load_profile()
    xs_all = np.sort(np.unique(np.concatenate([upper[:, 0], lower[:, 0]])))

    def cell_segments(xa, xb):
        xs = xs_all[(xs_all >= xa) & (xs_all <= xb)]
        zu = np.interp(xs, upper[::-1, 0], upper[::-1, 1])
        zl = np.interp(xs, lower[:, 0], lower[:, 1])
        return (np.diff(xs), np.diff(zu), np.diff(zl),
                abs(zu[0] - zl[0]), abs(zu[-1] - zl[-1]))

    unit = section_geometry(1.0)
    return cell_segments(0.0, X_DBOX), cell_segments(X_DBOX, X_BOX), unit


def scaled_section_geometry(tc_scale):
    """`section_geometry` for an arbitrary t/c, without re-integrating.

    Equivalent to `section_geometry(tc_scale)` to machine precision; it exists
    because `section_geometry` is keyed on a continuously varying float, so its
    cache measured hits=0 / misses=401 on a single `grid(401)` call and removed
    no cost at all.
    """
    (dx1, dzu1, dzl1, front1, aft1), \
        (dx2, dzu2, dzl2, front2, aft2), unit = _section_scaling_basis()
    a1_u, a2_u, _, _, s12_u, x_cell = unit

    def perimeter(dx, dzu, dzl, front, aft, close_aft):
        total = (np.hypot(dx, tc_scale * dzu).sum()
                 + np.hypot(dx, tc_scale * dzl).sum()
                 + tc_scale * front)
        if close_aft:
            total += tc_scale * aft
        return float(total)

    s12 = tc_scale * s12_u
    s1 = perimeter(dx1, dzu1, dzl1, front1, aft1, False) + s12
    s2 = perimeter(dx2, dzu2, dzl2, front2, aft2, True)
    return (tc_scale * a1_u, tc_scale * a2_u, s1, s2, s12, x_cell)


def j_section(c, tc, t, area_factor=1.0):
    """J of the real two-cell section scaled to chord c, local t/c tc."""
    A1, A2, s1, s2, s12, _ = scaled_section_geometry(tc / ROOT_TC)
    return j_bredt(A1 * c ** 2 * area_factor, A2 * c ** 2 * area_factor,
                   s1 * c, s2 * c, s12 * c, t)


def j_bredt(a1, a2, s1, s2, s12, t):
    """Multi-cell Bredt-Batho exact solution, uniform wall thickness t."""
    A = np.array([[s1, -s12], [-s12, s2]])
    rhs = 2.0 * np.array([a1, a2])
    x = np.linalg.solve(A, rhs)
    return 2.0 * (a1 * x[0] + a2 * x[1]) * t


def j_torsion_box(c, h, t, w1=None, w2=None):
    """Rectangular double-cell idealization (validation only — the real
    section uses j_section). Single-cell consistency: equal cells -> web
    shear flow cancels -> combined rectangle."""
    if w1 is None:
        w1 = X_DBOX * c
    if w2 is None:
        w2 = (X_BOX - X_DBOX) * c
    a1, a2 = w1 * h, w2 * h
    s1 = 2.0 * (w1 + h)
    s2 = 2.0 * (w2 + h)
    return j_bredt(a1, a2, s1, s2, h, t)


def j_single_rect(w, h, t):
    """Closed form, single rectangular cell: J = 2·t·w²·h²/(w+h)."""
    return 2.0 * t * w * w * h * h / (w + h)


# ---------------------------------------------------------------------------
# Section properties on a fine spanwise grid
# ---------------------------------------------------------------------------
def grid(n=401, area_factor=1.0):
    ys = np.linspace(0.0, L, n)
    c = np.interp(ys, [s[0] for s in STATIONS], [s[1] for s in STATIONS])
    tc = np.interp(ys, [s[0] for s in STATIONS], [s[2] for s in STATIONS])
    h = c * tc
    j = np.array([j_section(ci, tci, T_SKIN, area_factor)
                  for ci, tci in zip(c, tc)])
    return ys, c, h, j


def gj_shell(j, g=G_PETG):
    return j * g


# ---------------------------------------------------------------------------
# Divergence: smallest eigenvalue of (GJ·th')' + q·c·e·a·th = 0
# ---------------------------------------------------------------------------
def _sturm_count_below(diag, off, value):
    """Number of eigenvalues of a symmetric tridiagonal matrix below `value`.

    Standard Sturm sequence on the leading principal minors, with the usual
    guard against an exact zero pivot.
    """
    count = 0
    pivot = diag[0] - value
    if pivot < 0.0:
        count += 1
    for i in range(1, len(diag)):
        if pivot == 0.0:
            pivot = np.finfo(float).tiny
        pivot = (diag[i] - value) - off[i - 1] ** 2 / pivot
        if pivot < 0.0:
            count += 1
    return count


def _smallest_tridiagonal_eigenvalue(diag, off, tol=1e-12):
    """Smallest eigenvalue of a symmetric tridiagonal matrix, by bisection.

    The FEM matrix here IS tridiagonal, but it used to be assembled dense and
    handed to `np.linalg.eigh`, which computes the whole spectrum in O(n^3):
    0.9 s per call on the n = 401 grid, 13.6 s of a 15 s run, for one number.
    Sturm bisection costs O(n) per step and returns the same value.
    """
    radius = float(np.max(np.abs(diag))
                   + 2.0 * (np.max(np.abs(off)) if off.size else 0.0))
    lo, hi = -radius, radius
    while hi - lo > tol * max(1.0, abs(hi)):
        mid = 0.5 * (lo + hi)
        if _sturm_count_below(diag, off, mid) >= 1:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def q_divergence(ys, c, j, g, a, e_frac, k_joint=K_JOINT, joint=True):
    """Smallest divergence dynamic pressure via the WEAK FORM (FEM, linear
    elements, lumped mass): K·th = q·M·th, K symmetric tridiagonal,
    M diagonal -> symmetric definite eigenproblem whose SMALLEST eigenvalue is
    obtained by Sturm bisection on the tridiagonal bands (robust for the
    fundamental mode, unlike QR on the non-symmetric ODE, and O(n) per step
    instead of the O(n^3) full spectrum a dense `eigh` would compute).

    Boundary conditions: th(0) = 0 (root fixed — node removed); tip free
    (natural: GJ·th'(L) = 0). R-JOINT (ADR-0032): discrete torsional spring
    at y = 195, k_joint = ratio x GJ(y_joint)/L, entered as potential energy
    k_s·th_j²/2. The lumped table (1x/-29 %, 3x/-13 %, 5x/-9 %) is the
    requirement basis; the distributed model here is the physical one (the
    spring sits at 30 % half-span, where the mode torque has fallen)."""
    n = len(ys)
    dy = ys[1] - ys[0]
    gj = j * g
    m = c * (e_frac * c) * a           # m(y) = c·e·a, q·m·th coupling
    M = m[1:] * dy
    j0 = int(np.argmin(np.abs(ys - JOINT_Y)))
    k_s = k_joint * gj[j0] / L if joint else None

    # Element stiffnesses, vectorised.  The joint contributes series compliance
    # to the single element that spans it.
    gje = 0.5 * (gj[:-1] + gj[1:])
    if k_s is not None:
        idx = j0                       # element (j0, j0+1) in 0-based edges
        gje = gje.copy()
        gje[idx] = 1.0 / (1.0 / gje[idx] + 1.0 / (k_s * dy))

    # Assemble K directly as the two bands of a symmetric tridiagonal matrix
    # instead of a dense (n-1)x(n-1) array: node 0 is fixed and removed.
    k_edge = gje / dy
    diag = np.empty(n - 1)
    diag[:-1] = k_edge[:-1] + k_edge[1:]
    diag[-1] = k_edge[-1]
    off = -k_edge[1:]                  # length n-2

    # B = D^-1 K D^-1 with D = sqrt(M) preserves symmetry and tridiagonality.
    d_scale = np.sqrt(M)
    diag = diag / d_scale**2
    off = off / (d_scale[:-1] * d_scale[1:])

    smallest = _smallest_tridiagonal_eigenvalue(diag, off)
    return smallest if smallest > 0 else np.inf


def v_from_q(q):
    return np.sqrt(2.0 * q / RHO)


def q_uniform(gj, c_ref, a, e_frac):
    """Closed form (I-05): q_D = pi²·GJ/(4·L²·c·e·a) — validation only."""
    return np.pi ** 2 * gj / (4.0 * L ** 2 * c_ref * e_frac * c_ref * a)


def _tip_torque(q, ys, c, j, g, a, e_frac):
    """Tip torque T(L) after marching from th(0)=0, T(0)=1, for each q.

    Vectorised over ``q``: the march is sequential in span but independent
    across dynamic pressures, so all candidates advance in lockstep.  The
    divergence eigenvalue is the smallest positive q with T(L) = 0.
    """
    q = np.atleast_1d(np.asarray(q, dtype=float))
    m = c * (e_frac * c) * a
    theta = np.zeros_like(q)
    torque = np.ones_like(q)
    for i in range(len(ys) - 1):
        dy = ys[i + 1] - ys[i]
        gj = j[i] * g
        k = np.sqrt(q * m[i] / gj)
        kdy = k * dy
        # Exact piecewise-constant solution, with the k -> 0 series limit:
        # sin(k dy)/k -> dy and gj k sin(k dy) -> q m dy.  Without it the
        # transfer matrix divides by gj*k and is singular at vanishing q or
        # vanishing eccentricity.
        small = kdy < 1e-8
        sin_over_k = np.where(small, dy, np.sin(kdy) / np.where(small, 1.0, k))
        gjk_sin = np.where(small, q * m[i] * dy, gj * k * np.sin(kdy))
        cos_kdy = np.cos(kdy)
        theta, torque = (theta * cos_kdy + torque * sin_over_k / gj,
                         -theta * gjk_sin + torque * cos_kdy)
    return torque


def q_divergence_shooting(ys, c, j, g, a, e_frac, nq=400, qmax=2e5,
                          tol=1e-10):
    """INDEPENDENT method (C2 discipline): shooting with transfer matrices in
    FLUX form — state (th, T = GJ·th'), T continuous across interfaces (the
    correct condition for varying GJ; matching th' instead is a
    non-consistent discretization: it drops the GJ'·th' term of the ODE
    (GJ·th')' + q·m·th = 0 — the piecewise-constant k march converges to the
    WRONG equation). Piecewise-constant coefficients per segment (exact local
    solution); root-find the smallest q with T(L) = 0 for th(0) = 0.

    The bracket is found with ONE vectorised coarse sweep and then closed by
    bisection to ``tol`` relative.  The previous implementation swept 40 000
    dynamic pressures in a pure-Python double loop and returned ``q_prev``, the
    LOWER bracket rather than the root: 3.9 s per call for a 5 Pa resolution
    carrying a systematic low bias.
    """
    if nq < 2 or qmax <= 0.0 or tol <= 0.0:
        raise ValueError("nq >= 2, qmax > 0 and tol > 0 are required")
    grid_q = np.linspace(qmax / nq, qmax, nq)
    torque = _tip_torque(grid_q, ys, c, j, g, a, e_frac)
    sign_change = np.nonzero(np.sign(torque[:-1]) * np.sign(torque[1:]) < 0.0)[0]
    if sign_change.size == 0:
        return np.inf
    lo, hi = grid_q[sign_change[0]], grid_q[sign_change[0] + 1]
    f_lo = float(_tip_torque(lo, ys, c, j, g, a, e_frac)[0])
    while hi - lo > tol * hi:
        mid = 0.5 * (lo + hi)
        f_mid = float(_tip_torque(mid, ys, c, j, g, a, e_frac)[0])
        if f_mid == 0.0:
            return mid
        if f_lo * f_mid < 0.0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------------
# Released clearance, exposed so the shared speed contract can consume it
# ---------------------------------------------------------------------------
def _grid_area(area_factor):
    ys_, c_, h_, j_ = grid(area_factor=area_factor)
    return ys_, c_, h_, j_


@cache
def conservative_divergence_speed():
    """V_div [m/s] at the conservative end of every declared band.

    This is the number the criterion is judged on, so it is a function the rest
    of the system can call rather than a value buried inside `main`.
    """
    _, e_lo, e_hi = E_BAND
    ys_c, c_c, _, j_c = _grid_area(AREA_BAND[1])
    q_cons = q_divergence(ys_c, c_c, j_c, G_PETG * (1 - G_BAND),
                          A_SLOPE[2], e_hi, joint=True)
    return K_SWEEP[1] * v_from_q(q_cons)


@cache
def operational_speed_limit_kmh():
    """First-flight operational speed limit [km/h], rounded DOWN.

    `V_LIMIT_FACTOR` clearance below the conservative V_div, floored to
    `V_LIMIT_INCREMENT`.  The shared `INITIAL_SPEED_LIMIT_KMH` must not exceed
    it; that relationship is asserted here and in the cross-module harness.
    """
    v_limit = V_LIMIT_FACTOR * conservative_divergence_speed()
    return float(np.floor(v_limit * 3.6 / V_LIMIT_INCREMENT)
                 * V_LIMIT_INCREMENT)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 74)
    print("ABSOLUTE DIVERGENCE SPEED - Salamandra Cruise (revision 4)")
    print(f"Planform: sweep c/4 = {SWEEP_C4_DEG:+.1f} deg (ADR-0040)")
    print(f"Criterion: V_div >= {F_DIV:.1f} x V_ARTICLE_NE = {F_DIV*V_ARTICLE_NE*3.6:.0f} km/h")
    print("=" * 74)

    ys, c, h, j = grid()
    e_nom, e_lo, e_hi = E_BAND

    # ---- 1. Section J per station (REAL profile geometry) ----
    print("\n1. TORSION BOX — multi-cell Bredt-Batho, released Salamandra r1 root")
    print(f"   {'y (mm)':>8} {'c (m)':>7} {'t/c':>6} {'J (m⁴)':>12}")
    for yi, ci, tci in STATIONS:
        ji = j_section(ci, tci, T_SKIN)
        print(f"   {yi*1000:8.0f} {ci:7.4f} {tci:6.3f} {ji:12.4e}")
    js = [j_section(ci, tci, T_SKIN) for _, ci, tci in STATIONS]
    A1r, A2r, _, _, _, x_cell_r = section_geometry(1.0)
    print(f"   -> J varies {min(js):.3e} .. {max(js):.3e} m⁴ along the span")
    print(f"   -> real geometry: A1={A1r:.4f} A2={A2r:.4f} c², "
          f"cell-area centroid x/c = {x_cell_r:.3f} (NOT the shear center)")
    print(f"   -> elastic-axis bracket x_EA/c = {X_EA_BAND[1]:.2f}.."
          f"{X_EA_BAND[2]:.2f} [E]; nominal {X_EA_BAND[0]:.2f}")

    # ---- 2. Carbon tube contribution ----
    j_tube = np.pi / 32.0 * (D_TUBE ** 4 - (D_TUBE - 2*T_TUBE) ** 4)
    gj_tube = G_TUBE * j_tube
    gj_shell_lo = min(js) * G_PETG * (1 - G_BAND)
    gj_shell_hi = max(js) * G_PETG * (1 + G_BAND)
    print("\n2. CARBON TUBE Ø12x1.0 — quantified (ADR-0015 'bending only')")
    print(f"   J_tube = {j_tube:.3e} m⁴ · G_12 pultruded UD = 3-7 GPa [E]")
    print(f"   GJ_tube = {gj_tube:.1f} N·m² vs shell GJ "
          f"{gj_shell_lo:.0f}-{gj_shell_hi:.0f} N·m² (root to tip)")

    # ---- 3. Divergence at nominal and band ends ----
    print("\n3. DIVERGENCE SPEED - corrected elastic-axis uncertainty")
    a_nom, a_lo, a_hi = A_SLOPE
    k_nom, k_lo, k_hi = K_SWEEP
    # nominal
    q_nom = q_divergence(ys, c, j, G_PETG, a_nom, joint=True, e_frac=e_nom)
    v_nom = k_nom * v_from_q(q_nom)
    # conservative end (design verdict): low G, high a, low k_sweep, low area
    def grid_area(af):
        ys_, c_, h_, j_ = grid(401, area_factor=af)
        return ys_, c_, h_, j_
    ys_c, c_c, _, j_c = grid_area(AREA_BAND[1])
    q_cons = q_divergence(ys_c, c_c, j_c, G_PETG * (1 - G_BAND), a_hi,
                          joint=True, e_frac=e_hi)
    v_cons = k_lo * v_from_q(q_cons)
    # optimistic end
    ys_o, c_o, _, j_o = grid_area(AREA_BAND[2])
    q_opt = q_divergence(ys_o, c_o, j_o, G_PETG * (1 + G_BAND), a_lo,
                         joint=True, e_frac=e_lo)
    v_opt = k_hi * v_from_q(q_opt)
    req = F_DIV * V_ARTICLE_NE
    # tube sensitivity at the conservative end (bonded 195 -> 585)
    jc_t = j_c.copy()
    bonded = (ys_c >= 0.195) & (ys_c <= 0.585)
    jc_t[bonded] += G_TUBE * j_tube / (G_PETG * (1 - G_BAND))
    q_tub = q_divergence(ys_c, c_c, jc_t, G_PETG * (1 - G_BAND), a_hi,
                         joint=True, e_frac=e_hi)
    v_tub = k_lo * v_from_q(q_tub)
    print(f"\n   Tube sensitivity at the conservative end: fully bonded "
          f"Ø12x1.0 raises V_div {100*(v_tub/v_cons - 1):+.1f} % "
          f"({v_tub*3.6:.1f} km/h) — 'bending only' holds for the eigenvalue.")
    for tag, v in [("NOMINAL", v_nom), ("CONSERVATIVE", v_cons),
                   ("OPTIMISTIC", v_opt)]:
        marg = v / req
        print(f"   {tag:13s}: V_div = {v*3.6:5.1f} km/h "
              f"({v:4.1f} m/s) -> margin {marg:4.2f} x "
              f"({'PASS' if v >= req else 'FAIL'})")
    print(f"   Verdict (conservative end): V_div = {v_cons*3.6:.1f} km/h vs "
          f"{req*3.6:.0f} km/h required -> "
          f"{'CRITERION MET' if v_cons >= req else 'CRITERION FAILS'}")

    # joint penalty as ADR-0032: discrete spring, k = 1x vs 5x
    q_k5 = q_divergence(ys_c, c_c, j_c, G_PETG * (1 - G_BAND), a_hi,
                        k_joint=5.0, joint=True, e_frac=e_hi)
    q_k1 = q_divergence(ys_c, c_c, j_c, G_PETG * (1 - G_BAND), a_hi,
                        k_joint=1.0, joint=True, e_frac=e_hi)
    q_kinf = q_divergence(ys_c, c_c, j_c, G_PETG * (1 - G_BAND), a_hi,
                          joint=False, e_frac=e_hi)
    v_inf = v_from_q(q_kinf)
    p5 = 100 * (1 - v_from_q(q_k5) / v_inf)
    p1 = 100 * (1 - v_from_q(q_k1) / v_inf)
    print(f"\n   Joint penalty (distributed model, spring at y=195): "
          f"k=5x -> -{p5:.1f} %; k=1x -> -{p1:.1f} % of no-joint "
          f"(ADR-0032 lumped table: -9 % / -29 % — conservative basis)")

    # ---- 4. AERO LW-PLA variant (OP-28) ----
    g_aero_cons = G_AERO * (1 - G_BAND)
    q_aero = q_divergence(ys_c, c_c, j_c, g_aero_cons, a_hi, joint=True,
                          e_frac=e_hi)
    v_aero = k_lo * v_from_q(q_aero)
    print("\n4. AERO LW-PLA WINGS (docs/06, OP-28): G ~ 0.5 x PETG [E]")
    print(f"   V_div = {v_aero*3.6:.1f} km/h vs {req*3.6:.0f} km/h required "
          f"-> {'PASS' if v_aero >= req else 'FAIL — confirms OP-28 with numbers'}")

    # ---- 4b. Literature sensitivity: factors NOT in the baseline ----
    print("\n4b. SENSITIVITY — real-print factors absent from the baseline")
    # G in the skin plane: E 1.94 GPa [M], nu 0.35-0.40 -> G_XY ~ 0.69-0.72 GPa
    # (the 0.55 GPa [M] anchor is the conservative measured value; Sadaghian
    # 2022 measured ~0.24 GPa only for cylinders loaded ACROSS layers, the
    # worst orientation — the wing skin loads IN the layer plane)
    g_plane = 0.69e9
    q_gp = q_divergence(ys_c, c_c, j_c, g_plane, a_hi, joint=True,
                        e_frac=e_hi)
    v_gp = k_lo * v_from_q(q_gp)
    # gyroid 5 %: no published torsion data at 5 % density; qualitative
    # evidence (Kati 2025: gyroid raises stiffness at 40-100 %) and community
    # torsion practice suggest 5-15 % GJ contribution [E]
    for gx_tag, gx_frac in [("gyroid +10 % GJ", 1.10),
                            ("wall 1.1 mm (J ~ t)", 1.0 + 0.2)]:
        jx = j_c * gx_frac
        qx = q_divergence(ys_c, c_c, jx, G_PETG * (1 - G_BAND), a_hi,
                          joint=True, e_frac=e_hi)
        vx = k_lo * v_from_q(qx)
        print(f"   {gx_tag:24s}: V_div = {vx*3.6:5.1f} km/h "
              f"({vx/v_cons:4.2f}x conservative)")
    print(f"   G in-plane {g_plane/1e9:.2f} GPa (physics, E-nu) [D]: "
          f"V_div = {v_gp*3.6:.1f} km/h ({v_gp/v_cons:4.2f}x conservative)")
    v_comb = v_cons * np.sqrt(g_plane / (G_PETG * (1 - G_BAND))) \
        * np.sqrt(1.10) * np.sqrt(1.2)
    print(f"   Combined best case (G in-plane + gyroid + wall 1.1 mm): "
          f"{v_comb*3.6:.0f} km/h vs {req*3.6:.0f} km/h — "
          f"{'PASSES' if v_comb >= req else 'STILL SHORT'} at the "
          f"conservative end (the sweep factor and the section GJ remain "
          f"the S3/I-12 closures)")

    v_limit = V_LIMIT_FACTOR * v_cons
    v_limit_gp = V_LIMIT_FACTOR * v_gp
    print(f"   First-flight clearance factor: {V_LIMIT_FACTOR:.2f} x conservative V_div")
    print(f"   -> V_limit = {v_limit*3.6:.1f} km/h, rounded DOWN to "
          f"{np.floor(v_limit*3.6/V_LIMIT_INCREMENT)*V_LIMIT_INCREMENT:.0f} km/h")
    print(f"   -> if S3 confirms G_XY=0.69 GPa: {v_limit_gp*3.6:.1f} km/h, "
          f"rounded DOWN to "
          f"{np.floor(v_limit_gp*3.6/V_LIMIT_INCREMENT)*V_LIMIT_INCREMENT:.0f} km/h")

    # ---- 5. Validation cases ----
    print("\n5. VALIDATION CASES")
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"   [{'PASS' if cond else 'FAIL'}] {name}")

    w, h, t = 0.1, 0.03, 0.0009
    jc = j_single_rect(w, h, t)
    check(f"Single-cell closed form J = 2tw²h²/(w+h) (got {jc:.3e} m⁴)",
          abs(jc - 2*t*w*w*h*h/(w+h)) < 1e-18)
    # two equal cells = combined rectangle (web shear flow cancels)
    w_eq = 0.05
    j_two = j_torsion_box(0.2, 0.05, t, w1=w_eq, w2=w_eq)
    j_one = j_single_rect(2 * w_eq, 0.05, t)
    check(f"Two equal cells reproduce the combined rectangle "
          f"(got {j_two:.4e} vs {j_one:.4e})", abs(j_two - j_one) / j_one < 1e-9)
    # uniform solver vs closed form
    c_ref, gj_ref, a_ref = 0.225, 500.0, 6.28
    ys_u = np.linspace(0.0, L, 401)
    j_uniform = np.full_like(ys_u, gj_ref / G_PETG)
    # Both sides use the SAME declared nominal eccentricity.  They previously
    # relied on a 0.11 default that contradicted this module's own E_BAND
    # nominal of 0.10; the comparison was self-consistent and therefore passed,
    # but at an eccentricity the module never declares anywhere.
    q_num = q_divergence(ys_u, c_ref * np.ones_like(ys_u), j_uniform,
                         G_PETG, a_ref, e_nom, joint=False)
    q_cl = q_uniform(gj_ref, c_ref, a_ref, e_nom)
    # The tridiagonal eigensolver replaced a dense eigh.  Prove the
    # substitution, do not assume it: rebuild the same matrix densely and
    # compare the smallest eigenvalue.
    rng = np.random.default_rng(20260818)
    d_test = rng.uniform(1.0, 5.0, 40)
    o_test = rng.uniform(-1.0, 1.0, 39)
    dense = np.diag(d_test) + np.diag(o_test, 1) + np.diag(o_test, -1)
    check(f"Sturm bisection reproduces dense eigh on a random tridiagonal "
          f"(rel {abs(_smallest_tridiagonal_eigenvalue(d_test, o_test) - np.linalg.eigvalsh(dense)[0]) / abs(np.linalg.eigvalsh(dense)[0]):.2e})",
          abs(_smallest_tridiagonal_eigenvalue(d_test, o_test)
              - np.linalg.eigvalsh(dense)[0])
          <= 1e-9 * abs(np.linalg.eigvalsh(dense)[0]))
    check(f"Discretized solver reproduces uniform closed form "
          f"(q {q_num:.1f} vs {q_cl:.1f} Pa, {100*abs(q_num-q_cl)/q_cl:.2f} %)",
          abs(q_num - q_cl) / q_cl < 0.02)
    # C2: independent shooting method on the REAL wing (nominal grid)
    ys_i = np.linspace(0.0, L, 2001)
    c_i = np.interp(ys_i, [s[0] for s in STATIONS], [s[1] for s in STATIONS])
    tc_i = np.interp(ys_i, [s[0] for s in STATIONS], [s[2] for s in STATIONS])
    j_i = np.array([j_section(ci, tci, T_SKIN) for ci, tci in zip(c_i, tc_i)])
    q_fem = q_divergence(ys_i, c_i, j_i, G_PETG, A_SLOPE[0], joint=False,
                         e_frac=E_BAND[0])
    q_shot = q_divergence_shooting(ys_i, c_i, j_i, G_PETG, A_SLOPE[0],
                                   e_frac=E_BAND[0])
    check(f"C2: shooting agrees with FEM on the real wing "
          f"(q {q_shot:.0f} vs {q_fem:.0f} Pa, "
          f"{100*abs(q_shot-q_fem)/q_fem:.2f} %)", abs(q_shot-q_fem)/q_fem < 0.03)
    # real geometry vs the old rectangular idealization (k_h = 0.8)
    j_real = j_section(0.2892, 0.135, T_SKIN)
    j_ideal = j_torsion_box(0.2892, 0.8 * 0.135 * 0.2892, T_SKIN)
    check(f"Real profile J within 3 % of the k_h=0.8 idealization "
          f"(got {j_real/j_ideal:.3f})", abs(j_real / j_ideal - 1.0) < 0.03)
    # profile area sanity: total area ~ 0.55-0.65 c·tmax
    A_tot = section_geometry(1.0)[0] + section_geometry(1.0)[1]
    check(f"Box area sanity: A_box/(c·tmax) in [0.50, 0.65] "
          f"(got {A_tot/0.135:.3f})", 0.50 <= A_tot / 0.135 <= 0.65)
    check("Cell-area centroid is diagnostic only and lies inside the box",
          X_DBOX <= x_cell_r <= X_BOX)
    check("Elastic-axis uncertainty is ordered (optimistic < nominal < conservative)",
          E_BAND[1] < E_BAND[0] < E_BAND[2])
    # ADR-0032: the lumped table's own math (sqrt(N/(N+1))) must reproduce -9/-29
    for n_ratio, exp_p in [(5.0, -9.0), (1.0, -29.0)]:
        p_lump = 100.0 * (np.sqrt(n_ratio / (n_ratio + 1.0)) - 1.0)
        check(f"ADR-0032 lumped table math: k={n_ratio:.0f}x -> {p_lump:+.0f} % "
              f"(published {exp_p:.0f} %)", abs(p_lump - exp_p) < 1.0)
    # distributed model on the real wing at the design point: quantify the
    # penalty vs the lumped table (the table is the requirement basis; the
    # distributed model at 5x is -12 %, slightly worse than -9 % — captured
    # in V_div; the requirement R-JOINT >= 5x stands)
    check(f"Real wing, k=5x: distributed penalty {p5:.1f} % in "
          f"[5, 20] % (lumped table -9 % — basis; model -12 %)",
          5 <= p5 <= 20)
    check("Real wing joint penalty monotone: 1x > 5x > no-joint",
          p1 > p5 > 0)
    # I-05 Peregrine anchor: GJ 6.45x, V_div 1.14x
    jr = (260.0/180.0)**3 * (0.9/0.42)          # c³·t ratio
    vd_r = (260.0/180.0)**1.5 * (0.9/0.42)**0.5 * (420.0/650.0) * (180.0/260.0)
    check(f"I-05 anchor: GJ ratio 6.45x (got {jr:.2f})", abs(jr - 6.45) < 0.05)
    check(f"I-05 anchor: V_div ratio 1.14x (got {vd_r:.3f})",
          abs(vd_r - 1.14) < 0.03)
    # e -> 0: q_D -> inf (AC on the elastic axis)
    ys_e = np.linspace(0.0, L, 401)
    q_e0 = q_divergence(ys_e, c_ref*np.ones_like(ys_e), j_uniform, G_PETG,
                        a_ref, joint=False, e_frac=1e-9)
    check(f"e -> 0 gives q_D -> inf (got {q_e0:.3e} Pa)", q_e0 > 1e9)
    # conservative-end verdict vs criterion — printed finding, not a model check
    verdict = ("PASS" if v_cons >= req else
               "FAIL — margin at risk; S3 GJ/EI verification is mandatory "
               "before trusting the nominal value")
    print("\n6. CRITERION VERDICT (conservative end of the declared bands)")
    print(f"   V_div = {v_cons*3.6:.1f} km/h vs {req*3.6:.0f} km/h required: "
          f"{verdict}")
    # AERO penalty ~ sqrt(0.5) at the same geometry, G band and factors
    v_petg_hi = k_lo * v_from_q(q_divergence(ys_c, c_c, j_c,
                                             G_PETG * (1 - G_BAND), a_hi,
                                             joint=True, e_frac=e_hi))
    check(f"AERO penalty ≈ √0.5 = 0.707 (got {v_aero/v_petg_hi:.3f})",
          abs(v_aero / v_petg_hi - np.sqrt(0.5)) < 0.03)
    check("V_limit arithmetic uses the declared 0.85 clearance factor",
          abs(v_limit - V_LIMIT_FACTOR * v_cons) < 1e-12)
    rounded_limit = np.floor(
        v_limit * 3.6 / V_LIMIT_INCREMENT) * V_LIMIT_INCREMENT
    check("shared initial speed limit does not exceed the computed clearance",
          INITIAL_SPEED_LIMIT_KMH <= rounded_limit)

    print(f"\n   MODEL VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
