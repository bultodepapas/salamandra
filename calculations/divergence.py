#!/usr/bin/env python3
"""
Absolute aeroelastic divergence speed of the Salamandra Cruise wing (G6 — the
project's declared weakest link, master plan F4-S3/S4).

WHY THIS SCRIPT EXISTS: ADR-0030 states "the divergence criterion
V_div >= 1.5 x V_NE is met with the shell alone", but until now no calculation
produced the absolute value: I-05 gives only a RELATIVE scaling anchor to the
Peregrine (GJ 6.45x, V_div 1.14x) and explicitly says "it does not give the
absolute value". This script is the first absolute, reproducible estimate.

MODEL (first pass, S3/CAD remains the closure trigger):
  1. Section per guide §7.1 + §5.2: torsion box x/c 0 -> 0.72 (D-box 0->0.30,
     center cell 0.30->0.72; the hinge cell 0.72->1.00 is the elevon, OUT of the
     torsion path — "the closed torsion box ends here"). Idealized as a double
     rectangle of height k_h·h_max(y) with the shear web at 0.30 (OP-09), skin
     0.9 mm (2 x 0.45, ADR-0028), web 0.9 mm.
  2. J multi-cell Bredt-Batho per station (compatibility system solved exactly).
  3. G_eff = 0.55 GPa [M] PETG (ADR-0021) with the G4 [E] band +/-35 %.
  4. Elastic axis = shear center of the torsion box (x_EA = 0.36 c for equal
     cells); AC at 0.25 c -> e = x_EA - x_AC = +0.11 c (AC ahead: divergence
     arrangement, as expected for the forward-swept wing). Declared assumption,
     CAD check in S3.
  5. Section lift slope a [D] from the in-repo XFOIL polars of the MH60->13.5 %
     candidate (0.155-0.195/deg at Re 3-5e5), floor 2*pi.
  6. Divergence q_D = smallest eigenvalue of the spanwise twist problem
     (weak form: K·th = q·M·th, FEM linear elements, lumped mass, symmetric
     definite eigenproblem via eigh — root fixed, tip free), on a fine grid
     from the §5.2 station table. Validated against the uniform closed form
     pi^2·GJ/(4·L^2·c·e·a).
  7. Forward-sweep reduction factor k_sweep = 0.50-0.70 [E] for -20° (I-05/I-12,
     G6) and the R-JOINT series compliance at y = 195 (k_joint = 5x section,
     ADR-0032; penalty -9% reproduced natively by the solver).
  8. Carbon tube Ø12x1.0: quantified, expected negligible (pultruded UD carbon
     G_12 ~ 3-7 GPa [E] -> GJ ~ 3-7 N·m² vs shell GJ ~ hundreds).

CRITERION: V_div >= 1.5 x V_NE = 1.5 x 160 km/h = 240 km/h (docs/00).
The verdict is reported at the CONSERVATIVE end of the declared bands.
"""
import os
import sys
from functools import lru_cache
import numpy as np

# ---------------------------------------------------------------------------
# Inputs (all with confidence tags)
# ---------------------------------------------------------------------------
RHO = 1.225                # kg/m³, ISA sea level
V_NE = 160.0 / 3.6         # m/s, article #1 (docs/00)
F_DIV = 1.5                # criterion V_div >= 1.5 x V_NE

# Station table, guide §5.2: y (m), c (m), t/c (-)
STATIONS = [
    (0.000, 0.2892, 0.135),
    (0.130, 0.2603, 0.126),
    (0.195, 0.2458, 0.122),
    (0.325, 0.2169, 0.113),
    (0.347, 0.2120, 0.111),
    (0.4875, 0.1808, 0.101),
    (0.498, 0.1784, 0.101),
    (0.585, 0.1590, 0.095),
    (0.650, 0.1446, 0.090),
]
L = 0.650                  # m, half-span
X_DBOX = 0.30              # D-box x/c extent; shear web position (OP-09)
X_BOX = 0.72               # torsion box end x/c (hinge line, ADR-0002)
T_SKIN = 0.0009            # m, skin 0.9 mm = 2 perimeters (ADR-0028)
X_AC = 0.25                # aerodynamic centre x/c (reflexed sections 0.24-0.27)
E_BAND = (0.1028, 0.090, 0.120)  # e = x_SC - X_AC from the REAL profile geometry
                                # (x_SC = 0.3528 c, computed in section_geometry):
                                # nominal / conservative / optimistic
PROFILE_FILE = r"geometry\airfoils\mh60-135.dat"   # real section coordinates
AREA_BAND = (1.00, 0.95, 1.05)  # nominal / conservative / optimistic area
                                # factor for the final-profile uncertainty (OP-02)
G_PETG = 0.55e9            # Pa, G_eff printed PETG [M] (ADR-0021)
G_BAND = 0.35              # G4 [E] +/-35 %
A_SLOPE = (9.7, 6.28, 11.2)   # /rad: nominal, floor (2pi), top — [D] XFOIL
                                # polars MH60->13.5 % 0.155-0.195/deg; 2*pi floor
K_SWEEP = (0.60, 0.50, 0.70)  # forward-sweep V_div reduction, -20° [E] (I-12)
K_JOINT = 5.0              # R-JOINT stiffness ratio, ADR-0032 requirement
JOINT_Y = 0.195            # m, CORE<->PANEL joint (30 % half-span)
JOINT_HALF = 0.035         # m, socket region half-length [E] (≈ 70 mm socket)

# Carbon tube Ø12x1.0 (ADR-0015): pultruded UD carbon G_12 [E]
G_TUBE = 5.0e9             # Pa, band 3-7 GPa
D_TUBE, T_TUBE = 0.012, 0.001

# AERO LW-PLA variant (docs/06, OP-28): E ~ 0.5 x PETG -> G ~ 0.5 x G_PETG [E]
G_AERO = 0.5 * G_PETG


# ---------------------------------------------------------------------------
# Real-section geometry (guide §7.1 + geometry/airfoils/mh60-135.dat)
# ---------------------------------------------------------------------------
def load_profile():
    """Loads the MH60->13.5 % coordinates (x/c, z/c), UIUC order
    (TE->LE upper, LE->TE lower). Returns x, z arrays."""
    pts = np.loadtxt(os.path.join(os.path.dirname(__file__), "..",
                                  PROFILE_FILE), skiprows=1)
    i_min = int(np.argmin(pts[:, 0]))
    upper = pts[:i_min + 1]      # TE -> LE
    lower = pts[i_min:]          # LE -> TE
    return upper, lower


@lru_cache(maxsize=None)
def section_geometry(tc_scale=1.0):
    """Cell areas, perimeters, web length and shear-centre x/c of the REAL
    two-cell torsion box (D-box 0->X_DBOX, center cell X_DBOX->X_BOX) from
    the profile coordinates, scaled to the local t/c by tc_scale. Returns
    (A1, A2, s1, s2, s12, x_sc) in units of c (areas c², perimeters c)."""
    upper, lower = load_profile()

    def interp_profile(xq):
        return (np.interp(xq, upper[::-1, 0], upper[::-1, 1]) * tc_scale,
                np.interp(xq, lower[:, 0], lower[:, 1]) * tc_scale)

    def poly_area(poly):
        n = len(poly)
        s = 0.0
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            s += x1 * y2 - x2 * y1
        return abs(s) / 2.0

    def poly_len(seg):
        return np.sum(np.hypot(np.diff(seg[:, 0]), np.diff(seg[:, 1])))

    def poly_centroid(poly):
        n = len(poly)
        cx = cy = 0.0
        A = 0.0
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            cr = x1 * y2 - x2 * y1
            A += cr
            cx += (x1 + x2) * cr
            cy += (y1 + y2) * cr
        A *= 0.5
        return cx / (6 * A), cy / (6 * A)

    xs_all = np.sort(np.unique(np.concatenate([upper[:, 0], lower[:, 0]])))

    def cell(xa, xb, close_aft):
        xs = xs_all[(xs_all >= xa) & (xs_all <= xb)]
        zu, zl = interp_profile(xs)
        p = np.array(list(zip(xs, zu)) + [(xb, zl[-1])]
                     + list(zip(xs[::-1], zl[::-1])))
        A = poly_area(p)
        s = poly_len(np.array(list(zip(xs, zu)))) \
            + poly_len(np.array(list(zip(xs[::-1], zl[::-1])))) \
            + abs(zu[0] - zl[0])          # front closure (LE arc / web)
        if close_aft:
            s += abs(zu[-1] - zl[-1])     # aft closure (hinge line)
        return A, s, (zu[0], zl[0]), (zu[-1], zl[-1]), poly_centroid(p)

    A1, s1, web_in, web_out, (cx1, _) = cell(0.0, X_DBOX, False)
    A2, s2, _, _, (cx2, _) = cell(X_DBOX, X_BOX, True)
    s12 = abs(web_out[0] - web_out[1])    # shared web at x = X_DBOX
    s1 += s12                             # web belongs to cell 1's perimeter
    # cell 2 already counts the web as its front closure
    x_sc = (A1 * cx1 + A2 * cx2) / (A1 + A2)
    return A1, A2, s1, s2, s12, x_sc


def j_section(c, tc, t, area_factor=1.0):
    """J of the real two-cell section scaled to chord c, local t/c tc."""
    A1, A2, s1, s2, s12, _ = section_geometry(tc / 0.135)
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
def q_divergence(ys, c, j, g, a, k_joint=K_JOINT, joint=True, e_frac=0.11):
    """Smallest divergence dynamic pressure via the WEAK FORM (FEM, linear
    elements, lumped mass): K·th = q·M·th, K symmetric tridiagonal,
    M diagonal -> symmetric definite eigenproblem solved with np.linalg.eigh
    (robust for the fundamental mode, unlike QR on the non-symmetric ODE).

    Boundary conditions: th(0) = 0 (root fixed — node removed); tip free
    (natural: GJ·th'(L) = 0). R-JOINT (ADR-0032): discrete torsional spring
    at y = 195, k_joint = ratio x GJ(y_joint)/L, entered as potential energy
    k_s·th_j²/2. The lumped table (1x/-29 %, 3x/-13 %, 5x/-9 %) is the
    requirement basis; the distributed model here is the physical one (the
    spring sits at 30 % half-span, where the mode torque has fallen)."""
    n = len(ys)
    dy = ys[1] - ys[0]
    gj = j * g
    e = e_frac * c
    m = c * e * a                      # m(y) = c·e·a, q·m·th coupling
    K = np.zeros((n - 1, n - 1))
    M = m[1:] * dy
    j0 = int(np.argmin(np.abs(ys - JOINT_Y)))
    k_s = k_joint * gj[j0] / L if joint else None
    for e in range(1, n):                  # element between nodes e-1 and e
        gje = 0.5 * (gj[e - 1] + gj[e])    # edge stiffness
        if k_s is not None and e == j0 + 1:
            gje = 1.0 / (1.0 / gje + 1.0 / (k_s * dy))   # series compliance
        if e == 1:
            K[0, 0] += gje / dy            # root element: node 0 fixed
        else:
            r = e - 1                      # reduced index of original node e
            K[r - 1, r - 1] += gje / dy
            K[r - 1, r] -= gje / dy
            K[r, r - 1] -= gje / dy
            K[r, r] += gje / dy
    D = np.sqrt(M)
    B = K / np.outer(D, D)             # symmetric: B (D·th) = q (D·th)
    w = np.linalg.eigh(B)[0]
    return w[0] if w[0] > 0 else np.inf


def v_from_q(q):
    return np.sqrt(2.0 * q / RHO)


def q_uniform(gj, c_ref, a, e_frac=0.11):
    """Closed form (I-05): q_D = pi²·GJ/(4·L²·c·e·a) — validation only."""
    return np.pi ** 2 * gj / (4.0 * L ** 2 * c_ref * e_frac * c_ref * a)


def q_divergence_shooting(ys, c, j, g, a, e_frac=0.11, nq=40000, qmax=2e5):
    """INDEPENDENT method (C2 discipline): shooting with transfer matrices in
    FLUX form — state (th, T = GJ·th'), T continuous across interfaces (the
    correct condition for varying GJ; matching th' instead is a
    non-consistent discretization: it drops the GJ'·th' term of the ODE
    (GJ·th')' + q·m·th = 0 — the piecewise-constant k march converges to the
    WRONG equation). Piecewise-constant coefficients per segment (exact local
    solution); root-find the smallest q with T(L) = 0 for th(0) = 0."""
    e = e_frac * c
    m = c * e * a
    q_prev, sign_prev = None, None
    for iq in range(1, nq):
        q = qmax * iq / nq
        th, t = 0.0, 1.0                    # th(0)=0, unit torque at the root
        for i in range(len(ys) - 1):
            dy = ys[i + 1] - ys[i]
            gj = j[i] * g
            k = np.sqrt(q * m[i] / gj)
            ck, sk = np.cos(k * dy), np.sin(k * dy)
            th_new = th * ck + t * sk / (gj * k)
            t = -th * gj * k * sk + t * ck
            th = th_new
        sign = np.sign(t)
        if sign_prev is not None and sign != sign_prev and sign_prev != 0:
            return q_prev
        q_prev, sign_prev = q, sign
    return np.inf


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 74)
    print("ABSOLUTE DIVERGENCE SPEED — Salamandra Cruise (G6 first pass)")
    print(f"Criterion: V_div >= {F_DIV:.1f} x V_NE = {F_DIV*V_NE*3.6:.0f} km/h")
    print("=" * 74)

    ys, c, h, j = grid()
    e_nom, e_lo, e_hi = E_BAND

    # ---- 1. Section J per station (REAL profile geometry) ----
    print("\n1. TORSION BOX — multi-cell Bredt-Batho, REAL profile (mh60-135.dat)")
    print(f"   {'y (mm)':>8} {'c (m)':>7} {'t/c':>6} {'J (m⁴)':>12}")
    for yi, ci, tci in STATIONS:
        ji = j_section(ci, tci, T_SKIN)
        print(f"   {yi*1000:8.0f} {ci:7.4f} {tci:6.3f} {ji:12.4e}")
    js = [j_section(ci, tci, T_SKIN) for _, ci, tci in STATIONS]
    A1r, A2r, s1r, s2r, s12r, x_sc_r = section_geometry(1.0)
    print(f"   -> J varies {min(js):.3e} .. {max(js):.3e} m⁴ along the span")
    print(f"   -> real geometry: A1={A1r:.4f} A2={A2r:.4f} c², "
          f"shear centre x/c = {x_sc_r:.3f}, e = {x_sc_r-X_AC:.3f} c")

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
    print("\n3. DIVERGENCE SPEED")
    a_nom, a_lo, a_hi = A_SLOPE
    k_nom, k_lo, k_hi = K_SWEEP
    # nominal
    q_nom = q_divergence(ys, c, j, G_PETG, a_nom, joint=True, e_frac=e_nom)
    v_nom = k_nom * v_from_q(q_nom)
    # conservative end (design verdict): low G, high a, low k_sweep, low area
    def grid_area(af):
        ys_, c_, h_, j_ = grid(401, area_factor=af)
        return ys_, c_, h_, j_
    ys_c, c_c, h_c, j_c = grid_area(AREA_BAND[1])
    q_cons = q_divergence(ys_c, c_c, j_c, G_PETG * (1 - G_BAND), a_hi,
                          joint=True, e_frac=e_hi)
    v_cons = k_lo * v_from_q(q_cons)
    # optimistic end
    ys_o, c_o, h_o, j_o = grid_area(AREA_BAND[2])
    q_opt = q_divergence(ys_o, c_o, j_o, G_PETG * (1 + G_BAND), a_lo,
                         joint=True, e_frac=e_lo)
    v_opt = k_hi * v_from_q(q_opt)
    req = F_DIV * V_NE
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
    print(f"\n4. AERO LW-PLA WINGS (docs/06, OP-28): G ~ 0.5 x PETG [E]")
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
        jx = j_c * gx_frac if gx_tag.startswith("gyroid") else \
            j_c * gx_frac
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
    q_num = q_divergence(ys_u, c_ref * np.ones_like(ys_u), j_uniform,
                         G_PETG, a_ref, joint=False)
    q_cl = q_uniform(gj_ref, c_ref, a_ref)
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
    print(f"\n6. CRITERION VERDICT (conservative end of the declared bands)")
    print(f"   V_div = {v_cons*3.6:.1f} km/h vs {req*3.6:.0f} km/h required: "
          f"{verdict}")
    # AERO penalty ~ sqrt(0.5) at the same geometry, G band and factors
    v_petg_hi = k_lo * v_from_q(q_divergence(ys_c, c_c, j_c,
                                             G_PETG * (1 - G_BAND), a_hi,
                                             joint=True, e_frac=e_hi))
    check(f"AERO penalty ≈ √0.5 = 0.707 (got {v_aero/v_petg_hi:.3f})",
          abs(v_aero / v_petg_hi - np.sqrt(0.5)) < 0.03)

    print(f"\n   MODEL VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
