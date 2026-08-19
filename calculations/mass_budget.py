#!/usr/bin/env python3
"""
Salamandra mass budget — evolvable, data-driven weight calculator with
per-part material selection (2026-08-06).

Purpose (F2-class tool, Phase 2 of the master plan):
  Weight budget of the reference aircraft under three material policies —
  ALL PETG (guide §8.1 baseline), wings+tips in AERO PLA (LW-PLA foamed),
  ALL PLA+ — or a fully arbitrary per-part material assignment.

Data model (all tagged, see docs/06-material-mass-variants.md):
  - PRINTED parts: base masses in PETG [D]/[E]; any material scales mass by
    rho_mat/rho_petg (same geometry). The PETG fractions are [E] placeholders
    that F2/P2 replaces with CAD mass properties (OP-28).
  - Batteries: I-16 model [D]: pack = n_cells × cell + 25 g packaging,
    validated against the measured packs (445/433/305/297 g).
  - FC: I-17 catalog [M] (8.4–26 g); the avionics row (110 g) absorbs any
    board around the I-17 survey average (17.4 g).  SpeedyBee mass includes
    the FC and mandatory PDB/current-sensor board, not the FC PCB alone.
  - FPV: I-19 [M]/[D] (O4 Air Unit 8.95 g installed; its 0.75 g antenna is
    lumped into the VTX assembly; O4 Pro 36.2 g; legacy O3 39.4 g).
  - Motor / ESC / prop adapter / carbon / hardware: guide §8.1 [E].  APC's
    published 8x8E blade mass and catalog servo masses are [M].
  - Elevon balance mass derived [D] from ADR-0025: m_b = 1.2 × m_elevons.
  - Stall speed [D]: V_stall = sqrt(2W/(rho·S·CLmax)), CLmax = 0.589 (I-07);
    reproduces the historical v0.2 45.9 km/h result at 1685 g.

Validation: preserves the released v0.2 baseline as a historical case, closes
the post-v0.2 Article #1 mass allocation, and reproduces the I-16 pack masses.
"""
import argparse
import sys

from battery_pack_layout import (
    CELLS as PACK_CELL_SPECS,
)
from battery_pack_layout import (
    pack_mass_g as layout_pack_mass_g,
)
from design_config import (
    ARTICLE_CLEAN_MASS_KG,
    ARTICLE_V1_ALLOCATION_MASS_KG,
    ARTICLE_V1_MASS_KG,
    PETG_DENSITY_KG_M3,
    STALL_SPEED_LIMIT_KMH,
    V1_FIN_SHELL_MOUNT_LOWER_KG,
    V1_FIN_BOOM_MASS_KG,
    V1_FIN_SPAR_MASS_KG,
    mass_at_stall_speed,
    speed_mps,
    stall_speed,
    wing_loading_g_dm2,
)
from equipment_catalog import DJI_O4_INSTALLED_MASS_G

# --------------------------------------------------------------------------
# 1. MATERIALS (rho [M]/[E], E printed [M]/[E], cost [E])
# --------------------------------------------------------------------------
MATERIALS = {
    "PETG":     {"rho": PETG_DENSITY_KG_M3 / 1000.0, "e": 1.94e9, "price": 18.0,
                     "note": "base material (ADR-0021)"},
    "PLA":      {"rho": 1.24, "e": 3.00e9, "price": 15.0, "note": "stiffest, fails at 65 °C"},
    "PLA_PLUS": {"rho": 1.24, "e": 2.20e9, "price": 22.0,
                     "note": "ADR-0016: REJECTED (softer than PLA, no thermal gain)"},
    "AERO_PLA": {"rho": 0.68, "e": 1.00e9, "price": 35.0,
                     "note": "LW-PLA foamed (PLA-AERO); FLOW RATIO 0.60, never 0.95; "
                          "E ≈ 0.5× PETG -> structural re-check required"},
}

# --------------------------------------------------------------------------
# 2. PRINTED PARTS — base mass in PETG [g], source, default material
#    Fractions of the 600 g shell are [E] until F2/P2 CAD mass properties
#    (OP-28). Validation: core+wings+tips+elevons = 600; the aluminium boom
#    and its printed cradle are a fixed hybrid assembly, not a material-policy part.
# --------------------------------------------------------------------------
PRINTED = {
    "core":    {"m": 165.0, "src": "[E] 30 % of shell",        "default": "PETG"},
    "wings":   {"m": 346.0, "src": "[E] shell incl. fixed y195--227.5 TE bridges", "default": "PETG"},
    "tips":    {"m": 44.0,  "src": "[E] 8 % of shell, 2 pcs",  "default": "PETG"},
    "elevons": {"m": 45.0,  "src": "[D]/[E] ADR-0045: 2 × 22.5 g", "default": "PETG"},
    "fin":     {"m": V1_FIN_SHELL_MOUNT_LOWER_KG * 1000.0,
                    "src": "[E] V1a shell+mount analytical lower model; C32", "default": "PETG",
                    "optional": True},
}

# Exact pre-ADR-0045 distribution retained only for the v0.2 regression.  It
# must not be selected by the Article #1 CLI or downstream design modules.
LEGACY_PRINTED = {
    **PRINTED,
    "wings": {"m": 341.0, "src": "[E] historical 62 % shell share", "default": "PETG"},
    "elevons": {"m": 50.0, "src": "[D] historical 2 × 25 g", "default": "PETG"},
}

# --------------------------------------------------------------------------
# 3. FIXED / OPTION COMPONENTS (masses in g)
# --------------------------------------------------------------------------
BATTERIES = {  # I-16 model [D]: n_cells × cell + 25 g packaging
    "4S1P": {"n": 4}, "6S1P": {"n": 6},
    "4S2P": {"n": 8}, "6S2P": {"n": 12},
}
CELLS = {                                      # [M] I-16, shared with pack layout
    "P42A": PACK_CELL_SPECS["Molicel P42A"][0],
    "50E": PACK_CELL_SPECS["Samsung 50E"][0],
}

FC = {  # [M] I-17 catalog; masses are the board alone
    "F405-WING-V2":    25.0, "F765-WING": 26.0, "F722-WING": 25.0,
    # 8.9 g FC + 11.4 g mandatory PDB/current-sensor board; wireless board omitted.
    "SpeedyBee-F405":  20.3, "F411-WSE":  8.5,  "Foxeer-F405": 8.4,
}
FC_AVG = 17.4                                 # [D] I-17 survey average (8 boards)

FPV = {  # [M]/[D] I-19: camera + transmission module + required antenna(s)
    "O4-Air-Unit": DJI_O4_INSTALLED_MASS_G,
    "O4-Lite": DJI_O4_INSTALLED_MASS_G,  # legacy project/market alias
    "O4": DJI_O4_INSTALLED_MASS_G,       # backwards-compatible CLI alias
    "O4-Pro": 36.2,                      # 32.0 g air unit + 2 x 2.1 g antennas [M]
    "O3": 39.4,
}
PROPS = {
    "APC-E-8x8": 25.0,          # 15 g blade [M] + 10 g adapter/collet [E]
    "APC-E-8x8-v0.2": 40.0,     # historical released estimate only
    "APC-E-9x6": 45.0,
    "APC-E-10x7": 55.0,
}
MOTOR_REF = 170.0                             # [E] 28-class
ESC_REF = 35.0                                # [E]
SERVO_REF = 30.0                              # [E] 2 × 15 g (one per elevon, ADR-0026)
SERVOS = {
    "class-15g": 30.0,                       # 2 x 15 g [E]
    "class-15g-v0.2": 60.0,                  # historical 4-servo regression only
    "Corona-DS939MG": 25.0,                  # 2 x 12.5 g [M], I-18
    "Hitec-HS5055MG": 19.0,                  # 2 x 9.5 g [M], I-18
    "heavy": 38.0,                           # 2 x 19 g class [E]
}
CARBON_REF = 70.0                             # [E] tubes + pins
HARDWARE_REF = 20.0                           # [E] screws, TPU, adhesive, dowels
AVIONICS_REF = 110.0                          # [E] guide §8.1 (incl. pitot/GPS/RX)
BOOM_REF = 37.4                               # [D]/[E] 327 mm Al extension + 15 g cradle
FIN_SPAR_REF = V1_FIN_SPAR_MASS_KG * 1000.0  # [D]/[E] mandatory Ø3 mm Al LE spar
FIN_BOOM_REF = V1_FIN_BOOM_MASS_KG * 1000.0  # [E] two Ø6/4 mm carbon aft booms

V_STALL_REF, AUW_REF = 45.9, 1685.0           # ADR-0040 / balance_cg.py datum

# --------------------------------------------------------------------------
# 3b. PRESET POLICIES
# --------------------------------------------------------------------------
POLICIES = {
    "all_petg":    {"core": "PETG", "wings": "PETG", "tips": "PETG",
                    "elevons": "PETG", "fin": "PETG"},
    "aero_wings":  {"core": "PETG", "wings": "AERO_PLA", "tips": "AERO_PLA",
                    "elevons": "PETG", "fin": "PETG"},
    "aero_max":    {"core": "PETG", "wings": "AERO_PLA", "tips": "AERO_PLA",
                    "elevons": "AERO_PLA", "fin": "PETG"},
    "pla_plus":    {"core": "PLA_PLUS", "wings": "PLA_PLUS", "tips": "PLA_PLUS",
                    "elevons": "PLA_PLUS", "fin": "PLA_PLUS"},
}


def scale(m_petg, mat):
    return m_petg * MATERIALS[mat]["rho"] / MATERIALS["PETG"]["rho"]


def pack_mass(config, cell):
    if config not in BATTERIES or cell not in CELLS:
        raise ValueError(f"unsupported pack selection {config} {cell}")
    return layout_pack_mass_g(config, cell)


def shell_base_mass(part, shell_cap, printed_parts=PRINTED):
    """PETG base mass after applying the shell cap; fin is outside the cap."""
    elevon_mass = printed_parts["elevons"]["m"]
    if not elevon_mass <= shell_cap <= 600.0:
        raise ValueError(
            "shell_cap must be between the selected elevon mass and 600 g"
        )
    mass = printed_parts[part]["m"]
    if part in ("core", "wings", "tips"):
        fixed_base = sum(
            printed_parts[name]["m"] for name in ("core", "wings", "tips")
        )
        mass *= (shell_cap - elevon_mass) / fixed_base
    return mass


def build(policy, battery="6S1P", cell="P42A", fc="SpeedyBee-F405",
          fpv="O4-Air-Unit", prop="APC-E-8x8", fin=False, servo_heavy=False,
          motor=MOTOR_REF, shell_cap=550.0, servo="Corona-DS939MG",
          legacy_elevon_geometry=False):
    """Returns (rows, totals) for one configuration. rows: list of dicts."""
    mat = dict(POLICIES[policy])
    if not fin:
        mat.pop("fin", None)
    rows, printed_m = [], 0.0
    printed_parts = LEGACY_PRINTED if legacy_elevon_geometry else PRINTED
    # Keep the declared total shell cap while assigning the 5 g printed-area
    # transfer from the shortened moving surfaces to the fixed panel bridges.
    for pid, spec in printed_parts.items():
        if spec.get("optional") and pid not in mat:
            continue
        base_m = shell_base_mass(pid, shell_cap, printed_parts)
        m = scale(base_m, mat[pid])
        printed_m += m
        rows.append({"part": pid, "kind": "printed", "m": m, "mat": mat[pid],
                         "src": spec["src"]})
    # Elevon balance mass, derived from the selected moving mass.  The 1.2
    # ratio remains a conservative allocation until CAD measures the moments.
    m_elev = next(r["m"] for r in rows if r["part"] == "elevons")
    m_bal = 1.2 * m_elev
    rows.append({"part": "balance", "kind": "fixed", "m": m_bal, "mat": "(derived)",
                     "src": "[D]/[E] ADR-0025/0045: 1.2 × moving elevons"})
    if fin:
        rows.extend([
            {
                "part": "fin_spars", "kind": "fixed", "m": FIN_SPAR_REF,
                "mat": "aluminium",
                "src": "[D]/[E] V1: two mandatory Ø3 mm LE spars",
            },
            {
                "part": "fin_booms", "kind": "fixed", "m": FIN_BOOM_REF,
                "mat": "carbon",
                "src": "[E] V1: two Ø6/4 mm aft root supports",
            },
        ])
    # fixed rows
    m_fc = FC.get(fc, FC_AVG)
    rows += [
        {"part": "boom",     "kind": "fixed", "m": BOOM_REF,      "mat": "Al + PETG",
             "src": "[D]/[E] ADR-0043: 327 mm Al extension + 15 g cradle; CAD pending"},
        {"part": "carbon",   "kind": "fixed", "m": CARBON_REF,    "mat": "carbon",
             "src": "[E] guide §8.1"},
        {"part": "motor",    "kind": "fixed", "m": motor,         "mat": "(option)",
             "src": "[E] 28-class, reference"},
        {"part": "esc",      "kind": "fixed", "m": ESC_REF,       "mat": "fixed",
             "src": "[E] 6S 30 A"},
        {"part": "avionics", "kind": "fixed",
             "m": AVIONICS_REF + (m_fc - FC_AVG), "mat": f"FC {fc}",
             "src": "[E] 110 g incl. pitot/GPS/RX; FC adjust [D]"},
        {"part": "servos",   "kind": "fixed",
             "m": SERVOS["heavy"] if servo_heavy else SERVOS[servo], "mat": "servos",
             "src": ("[M] I-18 catalog" if not servo_heavy
                  else "[E] 2 x 19 g heavy class")},
        {"part": "prop",     "kind": "fixed", "m": PROPS[prop],   "mat": f"prop {prop}",
             "src": ("[M] 15 g blade + [E] 10 g adapter" if prop == "APC-E-8x8"
                  else "[E] incl. adapter")},
        {"part": "fpv",      "kind": "fixed", "m": FPV[fpv],      "mat": f"FPV {fpv}",
             "src": "[M]/[D] I-19; installed system includes antenna(s)"},
        {"part": "hardware", "kind": "fixed", "m": HARDWARE_REF,  "mat": "fixed",
             "src": "[E] screws, TPU, adhesive, dowels"},
        {"part": "battery",  "kind": "fixed", "m": pack_mass(battery, cell),
             "mat": f"{battery} {cell}", "src": "[D] I-16 model"},
    ]
    auw = sum(r["m"] for r in rows)
    wl = wing_loading_g_dm2(auw / 1000.0)
    vs = stall_speed(auw / 1000.0) * 3.6
    cost = sum(scale(r["m"], r["mat"]) * MATERIALS[r["mat"]]["price"] / 1000.0
               for r in rows if r["kind"] == "printed")
    return rows, {"auw": auw, "wl": wl, "vs": vs, "printed": printed_m, "cost": cost}


def print_config(name, rows, tot):
    print(f"\n  {name}")
    print(f"  {'part':10s} {'mass (g)':>9s}  {'material':14s} source")
    print("  " + "-" * 62)
    for r in rows:
        print(f"  {r['part']:10s} {r['m']:8.1f}  {r['mat']:14s} {r['src']}")
    print("  " + "-" * 62)
    print(f"  {'AUW':10s} {tot['auw']:8.1f}  g · {tot['wl']:5.1f} g/dm² · "
          f"V_stall {tot['vs']:4.1f} km/h (limit 45) · printed {tot['printed']:.0f} g")
    if tot["vs"] > 45:
        print("  !! V_stall > 45 km/h — OP-24 mass lever required (F2)")
    if tot["vs"] <= 45:
        print("  ok: stall compliance at the current budget")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Salamandra mass budget (F2-class)")
    ap.add_argument("--config", default="all",
                    choices=list(POLICIES) + ["all", "matrix"],
                    help="material policy or 'all'/'matrix'")
    ap.add_argument("--battery", default="6S1P", choices=BATTERIES)
    ap.add_argument("--cell", default="P42A", choices=CELLS)
    ap.add_argument("--fc", default="SpeedyBee-F405",
                    help="FC from I-17 catalog: " + ", ".join(FC))
    ap.add_argument("--fpv", default="O4-Air-Unit", choices=FPV)
    ap.add_argument("--prop", default="APC-E-8x8", choices=PROPS)
    ap.add_argument("--motor", type=float, default=MOTOR_REF)
    ap.add_argument("--shell-cap", type=float, default=550.0,
                    help="PETG printed-shell CAD acceptance cap in grams")
    ap.add_argument("--servo", default="Corona-DS939MG", choices=SERVOS,
                    help="four-servo installed-mass option")
    ap.add_argument("--fin", action="store_true", help="V1 fixed fin (ADR-0038)")
    ap.add_argument("--servo-heavy", action="store_true",
                    help="17-21 g servo class (exceeds the 60 g budget)")
    ap.add_argument("--out", help="write a markdown report to this file")
    a = ap.parse_args()

    print("=" * 74)
    print("SALAMANDRA MASS BUDGET — material policies and component options")
    print("Data: [M]/[D]/[E] per row · reproduction: docs/06, calculations/README")
    print("=" * 74)

    results = []
    if a.config == "matrix":
        print("\nPER-PART × MATERIAL MATRIX (mass, g, from the PETG base)")
        hdr = f"  {'part':10s}" + "".join(f"{m:>11s}" for m in MATERIALS)
        print(hdr)
        for pid in PRINTED:
            row = f"  {pid:10s}" + "".join(
                f"{scale(shell_base_mass(pid, a.shell_cap), m):10.1f} "
                for m in MATERIALS)
            print(row)
        totals_by_material = {
            material: sum(scale(shell_base_mass(pid, a.shell_cap), material)
                          for pid in PRINTED)
            for material in MATERIALS
        }
        print(f"  {'TOTAL':10s}" + "".join(
            f"{totals_by_material[m]:10.1f} " for m in MATERIALS))
        print("\n  Note: the matrix shows each part fully in each material;")
        print("  the printed total includes only the selected assignment.")
        results = [("MATRIX", None, None)]
    elif a.config == "all":
        for name in POLICIES:
            rows, tot = build(name, a.battery, a.cell, a.fc, a.fpv, a.prop,
                              a.fin, a.servo_heavy, a.motor, a.shell_cap,
                              a.servo)
            print_config(name, rows, tot)
            results.append((name, rows, tot))
    else:
        rows, tot = build(a.config, a.battery, a.cell, a.fc, a.fpv, a.prop,
                          a.fin, a.servo_heavy, a.motor, a.shell_cap, a.servo)
        print_config(a.config, rows, tot)
        results.append((a.config, rows, tot))

    # ---- warnings ----
    warns = []
    for name, rows, _ in results:
        if not rows:
            continue
        for r in rows:
            if r["kind"] == "printed" and r["mat"] == "AERO_PLA":
                warns.append(f"{name}: AERO_PLA on '{r['part']}' — E ≈ 0.5× PETG; "
                             "re-verify torsion/divergence (G4/G6) and use FLOW 0.60")
            if r["mat"] == "PLA_PLUS":
                warns.append(f"{name}: PLA+ on '{r['part']}' — ADR-0016 rejected "
                             "(softer than PLA, no thermal gain); experimental only")
    if warns:
        print("\nENGINEERING WARNINGS")
        for w in dict.fromkeys(warns):
            print("  ! " + w)

    # ---- validation ----
    print("\nVALIDATION CASES")
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    rows, tot = build("all_petg", "6S1P", "P42A", "FC_AVG", "O4-Pro",
                      "APC-E-8x8-v0.2", False, False, MOTOR_REF, 600.0,
                       "class-15g-v0.2", legacy_elevon_geometry=True)
    check(f"Released v0.2 baseline = 1685 ± 2 g (got {tot['auw']:.1f})",
          abs(tot["auw"] - 1685.0) <= 2.0)
    check(f"Baseline V_stall = 45.9 ± 0.15 km/h (got {tot['vs']:.2f})",
          abs(tot["vs"] - 45.9) <= 0.15)
    check("Baseline wing loading = 59.8 ± 0.5 g/dm² "
          f"(got {tot['wl']:.2f})", abs(tot["wl"] - 59.8) <= 0.5)
    for cfg, cell, exp in [("6S1P", "P42A", 445.0), ("6S1P", "50E", 433.0),
                           ("4S1P", "P42A", 305.0), ("4S1P", "50E", 297.0)]:
        got = pack_mass(cfg, cell)
        check(f"Pack {cfg} {cell} = {exp:.0f} g (got {got:.0f})", abs(got - exp) <= 1)
    check(
        "DJI O4 Air Unit installed mass includes its 0.75 g antenna",
        abs(FPV["O4-Air-Unit"] - 8.95) < 1e-12,
    )
    check("Pure-AERO shell = 600×0.68/1.27 = 321.3 g "
          f"(got {scale(600.0,'AERO_PLA'):.1f})",
          abs(scale(600.0, "AERO_PLA") - 321.26) < 0.5)
    check("Pure-PLA+ shell = 600×1.24/1.27 = 585.8 g "
          f"(got {scale(600.0,'PLA_PLUS'):.1f})",
          abs(scale(600.0, "PLA_PLUS") - 585.83) < 0.5)
    check("Printed parts sum = 600 g (core+wings+tips+elevons)",
          abs(PRINTED["core"]["m"] + PRINTED["wings"]["m"] +
              PRINTED["tips"]["m"] + PRINTED["elevons"]["m"] - 600.0) < 1e-6)
    check("Article #1 balance rule: 45 g elevons -> 54 g balance",
          abs(1.2 * PRINTED["elevons"]["m"] - 54.0) < 1e-6)
    _, reference = build("all_petg", fin=False)
    _, reference_v1 = build("all_petg", fin=True)
    stall_mass_limit_g = 1000.0 * mass_at_stall_speed(
        speed_mps(STALL_SPEED_LIMIT_KMH))
    check(f"Article #1 CLEAN matches shared contract (got {reference['auw']:.2f} g)",
          abs(reference["auw"] - ARTICLE_CLEAN_MASS_KG * 1000.0) < 0.01)
    check(f"Article #1 V1 analytical lower model matches shared contract "
          f"(got {reference_v1['auw']:.2f} g)",
          abs(reference_v1["auw"] - ARTICLE_V1_MASS_KG * 1000.0) < 0.01)
    check(f"Twin-fin two-servo allocation target is "
          f"{ARTICLE_V1_ALLOCATION_MASS_KG*1000:.2f} g",
          abs(ARTICLE_V1_ALLOCATION_MASS_KG * 1000.0 - 1613.25) < 0.01)
    check(f"Twin-fin V1 lower model remains below the exact "
          f"{STALL_SPEED_LIMIT_KMH:.0f} km/h mass limit {stall_mass_limit_g:.1f} g "
          f"(got {reference_v1['auw']:.1f})",
          stall_mass_limit_g - reference_v1["auw"] > 0.0)
    check(f"Two-servo V1 V_stall is below {STALL_SPEED_LIMIT_KMH:.0f} km/h "
          f"(got {reference_v1['vs']:.2f})",
          reference_v1["vs"] < STALL_SPEED_LIMIT_KMH)
    _, ta = build("aero_wings", "6S1P", "P42A")
    check(f"AERO_WINGS 6S1P: V_stall <= {STALL_SPEED_LIMIT_KMH:.0f} km/h "
          f"(got {ta['vs']:.2f})", ta["vs"] <= STALL_SPEED_LIMIT_KMH)
    print(f"\n  VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")

    # ---- markdown report ----
    if a.out:
        lines = ["# Salamandra mass budget — material variants (2026-08-17)",
                 "",
                 (f"Battery {a.battery} {a.cell} · FC {a.fc} · FPV {a.fpv} · "
                  f"prop {a.prop} · fin {'V1' if a.fin else 'CLEAN'} · "
                  f"servos {'heavy' if a.servo_heavy else a.servo} · "
                  f"shell cap {a.shell_cap:.0f} g"),
                 "", ("| Config | AUW (g) | g/dm² | V_stall (km/h) | "
                      "printed (g) | printed cost (€) |"),
                 "|---|---|---|---|---|---|"]
        for name, rows, tot in results:
            if tot is None:
                continue
            lines.append(f"| **{name}** | {tot['auw']:.1f} | {tot['wl']:.1f} | "
                         f"{tot['vs']:.1f} | {tot['printed']:.0f} | "
                         f"{tot['cost']:.2f} |")
        lines += ["", ("Rows are [E]/[D] on [M] data — see "
                       "docs/06-material-mass-variants.md."), ""]
        with open(a.out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\nReport written: {a.out}")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
