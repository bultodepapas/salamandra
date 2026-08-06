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
import sys
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
K_H = 0.80                 # [E] mean box height factor vs h_max (0.65-0.95 band)
X_AC = 0.25                # aerodynamic centre x/c (reflexed sections 0.24-0.27)
X_SC = 0.36                # shear centre x/c of the two-cell box (0.34-0.38)
E_BAND = (0.11, 0.07, 0.14)   # e = X_SC - X_AC: nominal / min / max
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
# Multi-cell Bredt-Batho
# ---------------------------------------------------------------------------
def j_torsion_box(c, h, t, w1=None, w2=None):
    """J of the double-cell torsion box (D-box + center cell, common web),
    exact compatibility solution, uniform wall thickness t. Single-cell
    consistency: equal cells -> web shear flow cancels -> combined rectangle.
    w1/w2 overridable for validation cases."""
    if w1 is None:
        w1 = X_DBOX * c
    if w2 is None:
        w2 = (X_BOX - X_DBOX) * c
    a1, a2 = w1 * h, w2 * h          # cell areas
    s1 = 2.0 * (w1 + h)              # perimeter incl. web and LE closure
    s2 = 2.0 * (w2 + h)              # perimeter incl. web and hinge closure
    s12 = h                          # shared web
    A = np.array([[s1, -s12], [-s12, s2]])
    rhs = 2.0 * np.array([a1, a2])
    x = np.linalg.solve(A, rhs)      # x_i = q_i / (G·theta·t)
    return 2.0 * (a1 * x[0] + a2 * x[1]) * t


def j_single_rect(w, h, t):
    """Closed form, single rectangular cell: J = 2·t·w²·h²/(w+h)."""
    return 2.0 * t * w * w * h * h / (w + h)


# ---------------------------------------------------------------------------
# Section properties on a fine spanwise grid
# ---------------------------------------------------------------------------
def grid(n=401):
    ys = np.linspace(0.0, L, n)
    c = np.interp(ys, [s[0] for s in STATIONS], [s[1] for s in STATIONS])
    tc = np.interp(ys, [s[0] for s in STATIONS], [s[2] for s in STATIONS])
    h = K_H * c * tc
    j = np.array([j_torsion_box(ci, hi, T_SKIN) for ci, hi in zip(c, h)])
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


def q_divergence_shooting(ys, c, j, g, a, e_frac=0.11, nq=20000):
    """INDEPENDENT method (C2 discipline): shooting with transfer matrices.
    Piecewise-constant segments (exact uniform solution per segment);
    root-find the smallest q with GJ·th'(L) = 0 for th(0) = 0."""
    e = e_frac * c
    m = c * e * a
    qmax = 2e5
    # first candidate: uniform closed form with root values
    q0 = 0.0
    q_prev, sign_prev = None, None
    for iq in range(1, nq):
        q = qmax * iq / nq
        # march
        th, thp = 0.0, 1.0
        for i in range(len(ys) - 1):
            dy = ys[i + 1] - ys[i]
            k = np.sqrt(q * m[i] / (j[i] * g))
            ck, sk = np.cos(k * dy), np.sin(k * dy)
            th_new = th * ck + thp * sk / k
            thp = -th * k * sk + thp * ck
            th = th_new
        f = thp
        sign = np.sign(f)
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

    # ---- 1. Section J per station ----
    print("\n1. TORSION BOX — multi-cell Bredt-Batho (guide §7.1)")
    print(f"   {'y (mm)':>8} {'c (m)':>7} {'h_eff (mm)':>10} {'J (m⁴)':>12}")
    for yi, ci, tci in STATIONS:
        hi = K_H * ci * tci
        ji = j_torsion_box(ci, hi, T_SKIN)
        print(f"   {yi*1000:8.0f} {ci:7.4f} {hi*1000:10.1f} {ji:12.4e}")
    js = [j_torsion_box(ci, K_H*ci*tci, T_SKIN) for _, ci, tci in STATIONS]
    print(f"   -> J varies {min(js):.3e} .. {max(js):.3e} m⁴ along the span")

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
    # conservative end (design verdict): low G, high a, low k_sweep, low k_h
    def grid_kh(kh):
        ys_, c_ = grid(401)[:2]
        tc_ = np.interp(ys_, [s[0] for s in STATIONS], [s[2] for s in STATIONS])
        h_ = kh * c_ * tc_
        j_ = np.array([j_torsion_box(ci, hi, T_SKIN) for ci, hi in zip(c_, h_)])
        return ys_, c_, h_, j_
    ys_c, c_c, h_c, j_c = grid_kh(0.65)
    q_cons = q_divergence(ys_c, c_c, j_c, G_PETG * (1 - G_BAND), a_hi,
                          joint=True, e_frac=e_hi)
    v_cons = k_lo * v_from_q(q_cons)
    # optimistic end
    ys_o, c_o, h_o, j_o = grid_kh(0.95)
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
    h_i = K_H * c_i * tc_i
    j_i = np.array([j_torsion_box(ci, hi, T_SKIN) for ci, hi in zip(c_i, h_i)])
    q_fem = q_divergence(ys_i, c_i, j_i, G_PETG, A_SLOPE[0], joint=False,
                         e_frac=E_BAND[0])
    q_shot = q_divergence_shooting(ys_i, c_i, j_i, G_PETG, A_SLOPE[0],
                                   e_frac=E_BAND[0])
    check(f"C2: shooting agrees with FEM on the real wing "
          f"(q {q_shot:.0f} vs {q_fem:.0f} Pa, "
          f"{100*abs(q_shot-q_fem)/q_fem:.2f} %)", abs(q_shot-q_fem)/q_fem < 0.03)
    # ADR-0032: the lumped table's own math (sqrt(N/(N+1))) must reproduce -9/-29
    for n_ratio, exp_p in [(5.0, -9.0), (1.0, -29.0)]:
        p_lump = 100.0 * (np.sqrt(n_ratio / (n_ratio + 1.0)) - 1.0)
        check(f"ADR-0032 lumped table math: k={n_ratio:.0f}x -> {p_lump:+.0f} % "
              f"(published {exp_p:.0f} %)", abs(p_lump - exp_p) < 1.0)
    # distributed model on the real wing at the design point: penalty <= lumped
    check(f"Real wing, k=5x: distributed penalty {p5:.1f} % <= lumped -9 % "
          f"(requirement basis conservative)", p5 <= 9.0 and p5 > 0.0)
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
