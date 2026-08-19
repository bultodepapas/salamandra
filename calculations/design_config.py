#!/usr/bin/env python3
"""Canonical Salamandra Article #1 numerical design contract.

This module is the single numerical source for quantities shared by two or more
analysis scripts: planform geometry, atmosphere, mission points, load cases and
released Article #1 mass targets.  Model-specific assumptions remain in their
own modules.  Run this file directly after changing any shared input; every
invariant must pass before the Design Guide or CAD is released.

Coordinate convention: x aft, y starboard, origin at the root quarter chord.
Negative quarter-chord sweep is forward sweep.

This module stays stdlib-only on purpose: it is the one import every other
module makes, so it must never be the reason an environment fails to load.
"""
from importlib.metadata import PackageNotFoundError, version
from math import atan, degrees, isclose, radians, tan
from pathlib import Path

# ---------------------------------------------------------------------------
# Repository anchors.  Every data file is resolved through these, never through
# a hand-written relative string: a literal path separator is not portable and
# `geometry\airfoils\...` silently became an unreadable filename on POSIX.
# ---------------------------------------------------------------------------
CALCULATIONS_DIR = Path(__file__).resolve().parent
REPO_ROOT = CALCULATIONS_DIR.parent
AIRFOIL_DIR = REPO_ROOT / "geometry" / "airfoils"
DRAWINGS_DIR = REPO_ROOT / "geometry" / "drawings"

# NOTE ON DEFAULT ARGUMENTS.  Functions below take ``None`` sentinels and
# resolve the module constant inside the body, never ``area=S`` in the
# signature.  A default argument is evaluated ONCE at definition time, so a
# constant bound there cannot be overridden by reassigning the module
# attribute: a sensitivity sweep written the obvious way silently produced the
# unmutated answer, and two seeded defects survived the whole contract suite
# for exactly this reason.
#
# ---------------------------------------------------------------------------
# Numeric-stack contract.  Checked here so an unsupported environment produces
# one named, actionable error instead of an AttributeError raised deep inside
# an integration call.  The check is metadata-only: it does not import numpy,
# which keeps this module stdlib-only for the scripts that need no numerics.
# The floor is a broadly available release, not the newest one: this is a
# community repository and a distribution-packaged numpy must keep working.
# ---------------------------------------------------------------------------
NUMPY_MINIMUM = (1, 24)
NUMPY_MAXIMUM_EXCLUSIVE = (3, 0)


def _parse_version(text):
    """Leading numeric release components of a PEP 440 version string."""
    parts = []
    for chunk in text.split(".")[:3]:
        digits = ""
        for character in chunk:
            if not character.isdigit():
                break
            digits += character
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def check_numeric_stack():
    """Return the installed numpy release, or raise a named contract error.

    Returns ``None`` when numpy is absent: several modules in this repository
    are deliberately stdlib-only and must keep working without it.
    """
    try:
        installed = _parse_version(version("numpy"))
    except PackageNotFoundError:
        return None
    if not installed:
        return None
    if not NUMPY_MINIMUM <= installed < NUMPY_MAXIMUM_EXCLUSIVE:
        floor = ".".join(str(n) for n in NUMPY_MINIMUM)
        ceiling = ".".join(str(n) for n in NUMPY_MAXIMUM_EXCLUSIVE)
        found = ".".join(str(n) for n in installed)
        raise RuntimeError(
            f"unsupported numpy {found}: this repository requires "
            f">={floor},<{ceiling}.  Install the pinned stack with "
            "'python3 -m pip install -r calculations/requirements.txt'."
        )
    return installed


NUMPY_VERSION = check_numeric_stack()

B = 1.300
S = 0.282
TAPER = 0.50
SWEEP_C4_DEG = -15.0          # ADR-0040 / I-21
ROOT_TC = 0.135
TIP_TC = 0.090

# Physical reference conditions.  G0 deliberately retains the project's
# engineering value used by every released calculation; changing it is a
# controlled numerical-contract revision, not a local cleanup.
G0 = 9.81                     # m/s2
# Standard gravity is a *unit definition*, not a local acceleration: the
# kilogram-force is defined as exactly 9.80665 m/s2.  Keeping it separate from
# G0 stops one symbol from serving as two different physical constants.
KGF_STANDARD_GRAVITY = 9.80665   # m/s2, exact by definition [M]
RHO_SL = 1.225                # kg/m3, ISA sea-level density [M]
NU_SL = 1.50e-5               # m2/s, declared low-altitude value [E]

# ---------------------------------------------------------------------------
# The speed ladder.  Each entry has ONE role, and the roles are ordered; the
# ordering is asserted in `validate_geometry`, because nothing previously
# stopped an edit from inverting it.
#
#   STALL_SPEED_LIMIT_KMH        requirement ceiling on V_s (R-series)
#   CRUISE_SPEED_KMH             the O1 energy point
#   INITIAL_SPEED_LIMIT_KMH      operational cap for the first article
#   ARTICLE_V_NE_KMH             article V_NE; the divergence criterion basis
#   STRUCTURAL_DESIGN_SPEED_KMH  structural/hinge-moment sizing case
#
# INITIAL_SPEED_LIMIT_KMH is an OPERATIONAL CAP, not a Part 23 design cruising
# speed V_C.  The distinction matters: the manoeuvring speed V_A at the +6 g
# limit is 107.9 km/h (CLEAN) and 109.4 km/h (V1), i.e. ABOVE this cap, so
# treating it as V_C would place the gust schedule's "V_C" below the manoeuvre
# corner.  `flight_envelope.py` therefore labels it a screening speed and the
# invariant below records the relationship instead of hiding it.
STALL_SPEED_LIMIT_KMH = 45.0
CRUISE_SPEED_KMH = 95.0
INITIAL_SPEED_LIMIT_KMH = 105.0
ARTICLE_V_NE_KMH = 160.0
STRUCTURAL_DESIGN_SPEED_KMH = 180.0
SPEED_LADDER_KMH = (
    ("V_s requirement ceiling", STALL_SPEED_LIMIT_KMH),
    ("cruise (O1 energy point)", CRUISE_SPEED_KMH),
    ("initial operational cap", INITIAL_SPEED_LIMIT_KMH),
    ("article V_NE", ARTICLE_V_NE_KMH),
    ("structural sizing case", STRUCTURAL_DESIGN_SPEED_KMH),
)
O1_ENERGY_LIMIT_WH_PER_KM = 1.15
REFERENCE_BEC_EFFICIENCY = 0.90   # battery-to-avionics rail efficiency [E]
POSITIVE_LIMIT_LOAD_FACTOR = 6.0
NEGATIVE_LIMIT_LOAD_FACTOR = -3.0
ULTIMATE_SAFETY_FACTOR = 1.5
PETG_DENSITY_KG_M3 = 1270.0    # 1.27 g/cm3, project material contract [M]/[E]

# Aerodynamic and mass contract used by coupled performance calculations.
CL_MAX_WING = 0.589           # I-07 wing value [D], pending E2
STATIC_MARGIN = 0.08

# Released printed wash-in (positive = tip at higher incidence).  This is a
# first-order geometric parameter: it sets trim, Cm0, the tip-stall margin and
# the torsion window.  It was previously declared independently in four modules
# plus one bare literal, with nothing cross-checking them.
DESIGN_TWIST_DEG = 3.0        # ADR-0041 / I-07 [D]
TWIST_STRUCTURAL_CAP_DEG = 3.0  # printable/structural cap explored in I-21 [E]

# Canonical analysis meshes.  Every released aerodynamic number is quoted at
# these resolutions; a different mesh is a deliberate convergence study, never
# an incidental call-site choice.  The published neutral point moved by 1.4 mm
# across the meshes previously in use, which is 28 % of the +/-5 mm CG band.
VLM_NY = 40                   # spanwise panels, half-cosine both tips
VLM_NX = 6                    # chordwise panels
WEISSINGER_NY = 100           # Weissinger-L spanwise stations
ARTICLE_CLEAN_MASS_KG = 1.55325

# Propulsion installation geometry shared by equipment, clearance calculations
# and drawings.  These values used to be declared only inside the SVG generator,
# which allowed the physical component ledger and the drawing to diverge.
PROP_PLANE_M = 0.235             # APC 8x8EP plane, aft of root c/4 [D]/[E]
PROP_DIAMETER_M = 0.2032         # APC nominal 8 inch diameter [M]
PROP_AXIAL_ENVELOPE_M = 0.0102   # measured/catalog component envelope [M]/[E]
PROP_AXIAL_DYNAMIC_ALLOWANCE_M = 0.005  # blade/runout/support axial inflation [E]
PROP_AXIAL_RESIDUAL_M = 0.008           # residual after inflated hazard [E]

V1_FIN_MASS_CAP_KG = 0.06000          # forward, prop-safe twin-fin allocation [E]
V1_FIN_SHELL_MOUNT_LOWER_KG = 0.03561492 # geometry-derived LW-PLA-HT lower model [M]/[E]
V1_FIN_SPAR_MASS_KG = 0.01006827         # geometry-derived Ø3 mm Al rods [D]/[E]
V1_FIN_BOOM_MASS_KG = 0.00304446         # geometry-derived Ø6/4 mm root extensions [E]
V1_FIN_MODEL_LOWER_KG = (
    V1_FIN_SHELL_MOUNT_LOWER_KG
    + V1_FIN_SPAR_MASS_KG
    + V1_FIN_BOOM_MASS_KG
)
ARTICLE_V1_ALLOCATION_MASS_KG = ARTICLE_CLEAN_MASS_KG + V1_FIN_MASS_CAP_KG
ARTICLE_V1_MASS_KG = ARTICLE_CLEAN_MASS_KG + V1_FIN_MODEL_LOWER_KG

HALF_SPAN = B / 2.0
ROOT_CHORD = 2.0 * S / (B * (1.0 + TAPER))
TIP_CHORD = TAPER * ROOT_CHORD
MAC = (2.0 / 3.0) * ROOT_CHORD * (1.0 + TAPER + TAPER**2) / (1.0 + TAPER)
Y_MAC = (B / 6.0) * (1.0 + 2.0 * TAPER) / (1.0 + TAPER)
ASPECT_RATIO = B**2 / S

# Article #1 control-surface contract (ADR-0045 / I-27).  The 35 % inboard
# limit creates a fixed 32.5 mm trailing-edge bridge outboard of the removable
# CORE/PANEL joint; the 90 % limit preserves a fixed 65 mm wingtip.
ELEVON_ETA_IN = 0.35
ELEVON_ETA_OUT = 0.90
ELEVON_HINGE_XC = 0.72
ELEVON_CHORD_FRACTION = 1.0 - ELEVON_HINGE_XC
ELEVON_INBOARD_M = ELEVON_ETA_IN * HALF_SPAN
ELEVON_OUTBOARD_M = ELEVON_ETA_OUT * HALF_SPAN
ELEVON_SPAN_M = ELEVON_OUTBOARD_M - ELEVON_INBOARD_M
ELEVON_SERVO_STATION_M = 0.5 * (ELEVON_INBOARD_M + ELEVON_OUTBOARD_M)

STATION_Y = (0.000, 0.130, 0.195, 0.325, 0.347, 0.4875, 0.498, 0.585, 0.650)


def chord(y):
    """Local chord [m] for |y| in [0, b/2]."""
    if abs(y) > HALF_SPAN + 1e-12:
        raise ValueError(f"span station {y!r} m is outside +/-{HALF_SPAN} m")
    eta = abs(y) / HALF_SPAN
    return ROOT_CHORD * (1.0 - (1.0 - TAPER) * eta)


def thickness_ratio(y):
    """Linear relative-thickness schedule."""
    if abs(y) > HALF_SPAN + 1e-12:
        raise ValueError(f"span station {y!r} m is outside +/-{HALF_SPAN} m")
    eta = abs(y) / HALF_SPAN
    return ROOT_TC + (TIP_TC - ROOT_TC) * eta


def x_c4(y, sweep_deg=None):
    if sweep_deg is None:
        sweep_deg = SWEEP_C4_DEG
    if abs(y) > HALF_SPAN + 1e-12:
        raise ValueError(f"span station {y!r} m is outside +/-{HALF_SPAN} m")
    return abs(y) * tan(radians(sweep_deg))


def x_le(y, sweep_deg=None):
    return x_c4(y, sweep_deg) - chord(y) / 4.0


def x_te(y, sweep_deg=None):
    return x_c4(y, sweep_deg) + 3.0 * chord(y) / 4.0


def taper_integrals(y_inner, y_outer, chord_fraction=1.0):
    """Exact ``(integral c dy, integral c**2 dy)`` over a starboard span band.

    The chord law is linear in ``y``, so both integrals are closed-form and no
    quadrature is required: the area is the trapezoid rule (exact for a linear
    integrand) and the second integral is the exact rule for a quadratic,
    ``(y2 - y1) * (c1**2 + c1*c2 + c2**2) / 3``.

    ``chord_fraction`` scales the chord, so passing ``ELEVON_CHORD_FRACTION``
    returns the control-surface area and its hinge-moment second moment.
    ``area * mac`` with ``mac = second / area`` is the exact tapered-surface
    hinge-moment reference.
    """
    if not 0.0 <= y_inner < y_outer <= HALF_SPAN + 1e-12:
        raise ValueError(
            f"require 0 <= y_inner < y_outer <= {HALF_SPAN} m")
    if chord_fraction <= 0.0:
        raise ValueError("chord fraction must be positive")
    c_inner = chord_fraction * chord(y_inner)
    c_outer = chord_fraction * chord(y_outer)
    span = y_outer - y_inner
    area = span * (c_inner + c_outer) / 2.0
    second = span * (c_inner**2 + c_inner * c_outer + c_outer**2) / 3.0
    return area, second


def planform_centroid(sweep_deg=None):
    """Exact area-centroid x station of the trapezoidal planform."""
    if sweep_deg is None:
        sweep_deg = SWEEP_C4_DEG
    return Y_MAC * tan(radians(sweep_deg)) + MAC / 4.0


def line_sweep_deg(x_root, x_tip):
    return degrees(atan((x_tip - x_root) / HALF_SPAN))


def speed_mps(speed_kmh):
    """Convert km/h to m/s with a positive-domain check."""
    if speed_kmh <= 0.0:
        raise ValueError("speed must be positive")
    return speed_kmh / 3.6


def dynamic_pressure(speed, rho=None):
    """Dynamic pressure [Pa] from speed [m/s] and density [kg/m3]."""
    if rho is None:
        rho = RHO_SL
    if speed <= 0.0 or rho <= 0.0:
        raise ValueError("speed and density must be positive")
    return 0.5 * rho * speed**2


def lift_coefficient(mass_kg, speed, area=None, rho=None):
    """Level-flight lift coefficient for SI inputs."""
    if area is None:
        area = S
    if mass_kg <= 0.0 or area <= 0.0:
        raise ValueError("mass and area must be positive")
    return mass_kg * G0 / (dynamic_pressure(speed, rho) * area)


def stall_speed(mass_kg, cl_max=None, area=None, rho=None):
    """Stall speed [m/s] for SI inputs."""
    cl_max = CL_MAX_WING if cl_max is None else cl_max
    area = S if area is None else area
    rho = RHO_SL if rho is None else rho
    if mass_kg <= 0.0 or cl_max <= 0.0 or area <= 0.0 or rho <= 0.0:
        raise ValueError("mass, CLmax, area and density must be positive")
    return (2.0 * mass_kg * G0 / (rho * area * cl_max)) ** 0.5


def mass_at_stall_speed(speed, cl_max=None, area=None, rho=None):
    """Maximum mass [kg] corresponding to a specified stall speed [m/s]."""
    cl_max = CL_MAX_WING if cl_max is None else cl_max
    area = S if area is None else area
    rho = RHO_SL if rho is None else rho
    if speed <= 0.0 or cl_max <= 0.0 or area <= 0.0 or rho <= 0.0:
        raise ValueError("speed, CLmax, area and density must be positive")
    return dynamic_pressure(speed, rho) * area * cl_max / G0


def wing_loading_g_dm2(mass_kg, area=None):
    """Wing loading [g/dm2]."""
    if area is None:
        area = S
    if mass_kg <= 0.0 or area <= 0.0:
        raise ValueError("mass and area must be positive")
    return mass_kg * 1000.0 / (area * 100.0)


def electrical_power_limit_w(speed_kmh=None, energy_wh_per_km=None):
    """Total battery-power limit [W] implied by a Wh/km objective."""
    if speed_kmh is None:
        speed_kmh = CRUISE_SPEED_KMH
    if energy_wh_per_km is None:
        energy_wh_per_km = O1_ENERGY_LIMIT_WH_PER_KM
    if speed_kmh <= 0.0 or energy_wh_per_km <= 0.0:
        raise ValueError("speed and specific energy must be positive")
    return speed_kmh * energy_wh_per_km


def stations(sweep_deg=None):
    """Rows: y, chord, t/c, thickness, x_LE, x_c/4, x_TE [SI units]."""
    return tuple(
        (y, chord(y), thickness_ratio(y), chord(y) * thickness_ratio(y),
         x_le(y, sweep_deg), x_c4(y, sweep_deg), x_te(y, sweep_deg))
        for y in STATION_Y
    )


STATIONS = tuple((y, c, tc) for y, c, tc, *_ in stations())


def validate_geometry():
    """Return named invariant checks. Every result must be true."""
    area = B * (ROOT_CHORD + TIP_CHORD) / 2.0
    tip_from_coordinates = x_te(HALF_SPAN) - x_le(HALF_SPAN)
    c4_sweep = line_sweep_deg(x_c4(0.0), x_c4(HALF_SPAN))
    le_sweep = line_sweep_deg(x_le(0.0), x_le(HALF_SPAN))
    te_sweep = line_sweep_deg(x_te(0.0), x_te(HALF_SPAN))
    return {
        "trapezoid area equals S": isclose(area, S, abs_tol=1e-12),
        "tip chord equals x_TE - x_LE": isclose(
            tip_from_coordinates, TIP_CHORD, abs_tol=1e-12),
        "quarter-chord sweep is canonical": isclose(
            c4_sweep, SWEEP_C4_DEG, abs_tol=1e-12),
        "LE is forward swept": le_sweep < 0.0,
        "TE is forward swept": te_sweep < 0.0,
        "last station is the tip": isclose(STATION_Y[-1], HALF_SPAN),
        "root and tip t/c are preserved": (
            isclose(thickness_ratio(0.0), ROOT_TC)
            and isclose(thickness_ratio(HALF_SPAN), TIP_TC)),
        "canonical aspect ratio is six": isclose(ASPECT_RATIO, 6.0, rel_tol=5e-3),
        "Article #1 elevon spans 35--90 percent half-span": (
            isclose(ELEVON_INBOARD_M, 0.2275, abs_tol=1e-12)
            and isclose(ELEVON_OUTBOARD_M, 0.585, abs_tol=1e-12)
            and isclose(ELEVON_SPAN_M, 0.3575, abs_tol=1e-12)),
        "Article #1 elevon chord closes at the hinge": isclose(
            ELEVON_HINGE_XC + ELEVON_CHORD_FRACTION, 1.0, abs_tol=1e-12),
        "Article #1 servo is at elevon midspan": isclose(
            ELEVON_SERVO_STATION_M, 0.40625, abs_tol=1e-12),
        "mission power identity is 109.25 W": isclose(
            electrical_power_limit_w(), 109.25, abs_tol=1e-12),
        "reference BEC efficiency is physical":
            0.0 < REFERENCE_BEC_EFFICIENCY <= 1.0,
        "limit load factors have the declared signs":
            POSITIVE_LIMIT_LOAD_FACTOR > 1.0
            and NEGATIVE_LIMIT_LOAD_FACTOR < 0.0,
        "ultimate structural safety factor is 1.5": isclose(
            ULTIMATE_SAFETY_FACTOR, 1.5, abs_tol=1e-12),
        "V1 allocation mass is clean plus fin cap": isclose(
            ARTICLE_V1_ALLOCATION_MASS_KG,
            ARTICLE_CLEAN_MASS_KG + V1_FIN_MASS_CAP_KG,
            abs_tol=1e-12),
        "V1 analytical mass includes twin-fin shells, spars and booms": isclose(
            ARTICLE_V1_MASS_KG,
            ARTICLE_CLEAN_MASS_KG + V1_FIN_SHELL_MOUNT_LOWER_KG
            + V1_FIN_SPAR_MASS_KG + V1_FIN_BOOM_MASS_KG,
            abs_tol=1e-12),
        "two-servo V1 allocation stall rounds to 44.9 km/h": isclose(
            stall_speed(ARTICLE_V1_ALLOCATION_MASS_KG) * 3.6,
            44.9, abs_tol=0.05),
        "two-servo analytical V1 remains below the 45 km/h ceiling":
            stall_speed(ARTICLE_V1_MASS_KG) * 3.6 < STALL_SPEED_LIMIT_KMH,
        # The speed ladder must stay ordered.  Nothing enforced this before, so
        # an edit to any single speed could silently invert two roles.
        "the speed ladder is strictly ordered": all(
            low[1] < high[1]
            for low, high in zip(SPEED_LADDER_KMH, SPEED_LADDER_KMH[1:])),
        "every released mass stalls below the requirement ceiling": all(
            stall_speed(mass) * 3.6 < STALL_SPEED_LIMIT_KMH
            for mass in (ARTICLE_CLEAN_MASS_KG, ARTICLE_V1_MASS_KG,
                         ARTICLE_V1_ALLOCATION_MASS_KG)),
        # V_A = V_s * sqrt(n_limit).  It sits ABOVE the initial operational cap
        # for every released mass; the invariant records that relationship so
        # the cap is never silently reinterpreted as a Part 23 V_C.
        "manoeuvring speed exceeds the initial operational cap": all(
            stall_speed(mass) * 3.6 * POSITIVE_LIMIT_LOAD_FACTOR**0.5
            > INITIAL_SPEED_LIMIT_KMH
            for mass in (ARTICLE_CLEAN_MASS_KG, ARTICLE_V1_MASS_KG)),
        "manoeuvring speed stays below the article V_NE": all(
            stall_speed(mass) * 3.6 * POSITIVE_LIMIT_LOAD_FACTOR**0.5
            < ARTICLE_V_NE_KMH
            for mass in (ARTICLE_CLEAN_MASS_KG, ARTICLE_V1_MASS_KG)),
    }


def main():
    print("=" * 86)
    print("SALAMANDRA CANONICAL PLANFORM - ADR-0040")
    print("=" * 86)
    print(f"b={B:.3f} m  S={S:.3f} m2  AR={ASPECT_RATIO:.3f}  "
          f"taper={TAPER:.2f}  sweep_c/4={SWEEP_C4_DEG:+.1f} deg")
    print(f"c_root={ROOT_CHORD*1000:.1f} mm  c_tip={TIP_CHORD*1000:.1f} mm  "
          f"MAC={MAC*1000:.1f} mm")
    print("\n y(mm)   c(mm)   t/c(%)   t(mm)   x_LE(mm)   x_c4(mm)   x_TE(mm)")
    for y, c, tc, t, le, c4, te in stations():
        print(f" {y*1000:5.1f}  {c*1000:7.1f}   {tc*100:6.2f}  {t*1000:6.1f}"
              f"   {le*1000:8.1f}   {c4*1000:9.1f}   {te*1000:8.1f}")

    le_sweep = line_sweep_deg(x_le(0.0), x_le(HALF_SPAN))
    te_sweep = line_sweep_deg(x_te(0.0), x_te(HALF_SPAN))
    print(f"\nLE sweep={le_sweep:+.2f} deg  TE sweep={te_sweep:+.2f} deg  "
          f"planform centroid x={planform_centroid()*1000:+.1f} mm")
    print(f"Mission: cruise={CRUISE_SPEED_KMH:.0f} km/h, "
          f"O1={O1_ENERGY_LIMIT_WH_PER_KM:.2f} Wh/km "
          f"({electrical_power_limit_w():.2f} W total battery power), "
          f"V_NE={ARTICLE_V_NE_KMH:.0f} km/h, "
          f"structural case={STRUCTURAL_DESIGN_SPEED_KMH:.0f} km/h")

    checks = validate_geometry()
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
