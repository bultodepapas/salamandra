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
    board around the I-17 survey average (17.4 g).
  - FPV: I-19 [M] (O4 32 / O4 Pro 37 / O4 Lite 8.2 / legacy O3 39.4 g).
  - Motor / ESC / prop / servos / carbon / hardware: guide §8.1 [E] with
    options where they exist.
  - Elevon balance mass derived [D] from ADR-0025: m_b = 1.2 × m_elevons.
  - Stall speed [D]: V_stall = sqrt(2W/(rho·S·CLmax)), CLmax = 0.589 (I-07);
    reproduces the guide's 46.1 km/h at AUW 1697 g.

Validation: reproduces the guide §8.1 baseline (1697 g) and the I-16 pack
masses; a change that breaks them is not accepted (calculations/README.md).
"""
import argparse
import sys

# --------------------------------------------------------------------------
# 1. MATERIALS (rho [M]/[E], E printed [M]/[E], cost [E])
# --------------------------------------------------------------------------
MATERIALS = {
    "PETG":     dict(rho=1.27, e=1.94e9, price=18.0, note="base material (ADR-0021)"),
    "PLA":      dict(rho=1.24, e=3.00e9, price=15.0, note="stiffest, fails at 65 °C"),
    "PLA_PLUS": dict(rho=1.24, e=2.20e9, price=22.0,
                     note="ADR-0016: REJECTED (softer than PLA, no thermal gain)"),
    "AERO_PLA": dict(rho=0.68, e=1.00e9, price=35.0,
                     note="LW-PLA foamed (PLA-AERO); FLOW RATIO 0.60, never 0.95; "
                          "E ≈ 0.5× PETG -> structural re-check required"),
}

# --------------------------------------------------------------------------
# 2. PRINTED PARTS — base mass in PETG [g], source, default material
#    Fractions of the 600 g shell are [E] until F2/P2 CAD mass properties
#    (OP-28). Validation: core+wings+tips+elevons = 600; boom separate (40 g).
# --------------------------------------------------------------------------
PRINTED = {
    "core":    dict(m=165.0, src="[E] 30 % of shell",        default="PETG"),
    "wings":   dict(m=341.0, src="[E] 62 % of shell, 6 seg", default="PETG"),
    "tips":    dict(m=44.0,  src="[E] 8 % of shell, 2 pcs",  default="PETG"),
    "elevons": dict(m=50.0,  src="[D] ADR-0025: 2 × 25 g",   default="PETG"),
    "boom":    dict(m=41.0,  src="[E] OP-24 prototipo: Al tube Ø8/int6 26g + cradle 15g (boom_flexion.py); carbon pending", default="PETG"),
    "fin":     dict(m=48.0,  src="[E] ADR-0038 V1, mid 36-60", default="PETG",
                    optional=True),
}

# --------------------------------------------------------------------------
# 3. FIXED / OPTION COMPONENTS (masses in g)
# --------------------------------------------------------------------------
BATTERIES = {  # I-16 model [D]: n_cells × cell + 25 g packaging
    "4S1P": dict(n=4), "6S1P": dict(n=6),
    "4S2P": dict(n=8), "6S2P": dict(n=12),
}
CELLS = {"P42A": 70.0, "50E": 68.0}          # [M] I-16
PACKAGING = 25.0                              # [D] I-16 (445-420, 305-280)

FC = {  # [M] I-17 catalog; masses are the board alone
    "F405-WING-V2":    25.0, "F765-WING": 26.0, "F722-WING": 25.0,
    "SpeedyBee-F405":  12.0, "F411-WSE":  8.5,  "Foxeer-F405": 8.4,
}
FC_AVG = 17.4                                 # [D] I-17 survey average (8 boards)

FPV = {  # [M] I-19: unit + antennas
    "O4": 32.0, "O4-Pro": 37.0, "O4-Lite": 8.2, "O3": 39.4,
}
PROPS = {"APC-E-8x8": 40.0, "APC-E-9x6": 45.0, "APC-E-10x7": 55.0}   # [E]
MOTOR_REF = 170.0                             # [E] 28-class
ESC_REF = 35.0                                # [E]
SERVO_REF = 60.0                              # [E] 4 × 15 g (class 12-15, I-18)
CARBON_REF = 70.0                             # [E] tubes + pins
HARDWARE_REF = 20.0                           # [E] screws, TPU, adhesive, dowels
AVIONICS_REF = 110.0                          # [E] guide §8.1 (incl. pitot/GPS/RX)

# Aircraft constants
S = 0.282                                     # m²
RHO_AIR = 1.225
CLMAX = 0.589                                 # [D] I-07 (wing, non-elliptic)
V_STALL_REF, AUW_REF = 46.1, 1697.0           # guide §4/§8.1 datum

# --------------------------------------------------------------------------
# 3b. PRESET POLICIES
# --------------------------------------------------------------------------
POLICIES = {
    "all_petg":    {"core": "PETG", "wings": "PETG", "tips": "PETG",
                    "elevons": "PETG", "boom": "PETG", "fin": "PETG"},
    "aero_wings":  {"core": "PETG", "wings": "AERO_PLA", "tips": "AERO_PLA",
                    "elevons": "PETG", "boom": "PETG", "fin": "PETG"},
    "aero_max":    {"core": "PETG", "wings": "AERO_PLA", "tips": "AERO_PLA",
                    "elevons": "AERO_PLA", "boom": "PETG", "fin": "PETG"},
    "pla_plus":    {"core": "PLA_PLUS", "wings": "PLA_PLUS", "tips": "PLA_PLUS",
                    "elevons": "PLA_PLUS", "boom": "PLA_PLUS", "fin": "PLA_PLUS"},
}


def scale(m_petg, mat):
    return m_petg * MATERIALS[mat]["rho"] / MATERIALS["PETG"]["rho"]


def pack_mass(config, cell):
    n = BATTERIES[config]["n"]
    return n * CELLS[cell] + PACKAGING


def build(policy, battery="6S1P", cell="P42A", fc="FC_AVG", fpv="O4-Pro",
          prop="APC-E-8x8", fin=False, servo_heavy=False, motor=MOTOR_REF):
    """Returns (rows, totals) for one configuration. rows: list of dicts."""
    mat = dict(POLICIES[policy])
    if not fin:
        mat.pop("fin", None)
    rows, printed_m = [], 0.0
    for pid, spec in PRINTED.items():
        if spec.get("optional") and pid not in mat:
            continue
        m = scale(spec["m"], mat[pid])
        printed_m += m
        rows.append(dict(part=pid, kind="printed", m=m, mat=mat[pid],
                         src=spec["src"]))
    # elevon balance mass, derived [D] ADR-0025
    m_elev = next(r["m"] for r in rows if r["part"] == "elevons")
    m_bal = 1.2 * m_elev
    rows.append(dict(part="balance", kind="fixed", m=m_bal, mat="(derived)",
                     src="[D] ADR-0025: 1.2 × elevons"))
    # fixed rows
    m_fc = FC[fc] if fc in FC else FC_AVG
    rows += [
        dict(part="carbon",   kind="fixed", m=CARBON_REF,    mat="carbon",
             src="[E] guide §8.1"),
        dict(part="motor",    kind="fixed", m=motor,         mat="(option)",
             src="[E] 28-class, reference"),
        dict(part="esc",      kind="fixed", m=ESC_REF,       mat="fixed",
             src="[E] 6S 30 A"),
        dict(part="avionics", kind="fixed",
             m=AVIONICS_REF + (m_fc - FC_AVG), mat=f"FC {fc}",
             src="[E] 110 g incl. pitot/GPS/RX; FC adjust [D]"),
        dict(part="servos",   kind="fixed",
             m=SERVO_REF if not servo_heavy else 76.0, mat="servos",
             src="[E] 4 × 15 g (I-18 class); heavy 17-21 g exceeds budget"),
        dict(part="prop",     kind="fixed", m=PROPS[prop],   mat=f"prop {prop}",
             src="[E] incl. hub/spinner"),
        dict(part="fpv",      kind="fixed", m=FPV[fpv],      mat=f"FPV {fpv}",
             src="[M] I-19"),
        dict(part="hardware", kind="fixed", m=HARDWARE_REF,  mat="fixed",
             src="[E] screws, TPU, adhesive, dowels"),
        dict(part="battery",  kind="fixed", m=pack_mass(battery, cell),
             mat=f"{battery} {cell}", src="[D] I-16 model"),
    ]
    auw = sum(r["m"] for r in rows)
    wl = auw / (S * 100.0)
    vs = 3.6 * (2.0 * auw / 1000.0 * 9.81 / (RHO_AIR * S * CLMAX)) ** 0.5
    cost = sum(scale(r["m"], r["mat"]) * MATERIALS[r["mat"]]["price"] / 1000.0
               for r in rows if r["kind"] == "printed")
    return rows, dict(auw=auw, wl=wl, vs=vs, printed=printed_m, cost=cost)


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
    ap = argparse.ArgumentParser(description="Salamandra mass budget (F2-class)")
    ap.add_argument("--config", default="all",
                    choices=list(POLICIES) + ["all", "matrix"],
                    help="material policy or 'all'/'matrix'")
    ap.add_argument("--battery", default="6S1P", choices=BATTERIES)
    ap.add_argument("--cell", default="P42A", choices=CELLS)
    ap.add_argument("--fc", default="FC_AVG",
                    help="FC from I-17 catalog: " + ", ".join(FC))
    ap.add_argument("--fpv", default="O4-Pro", choices=FPV)
    ap.add_argument("--prop", default="APC-E-8x8", choices=PROPS)
    ap.add_argument("--motor", type=float, default=MOTOR_REF)
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
        for pid, spec in PRINTED.items():
            row = f"  {pid:10s}" + "".join(
                f"{scale(spec['m'], m):10.1f} " for m in MATERIALS)
            print(row)
        print(f"  {'TOTAL':10s}" + "".join(
            f"{sum(scale(s['m'], m) for s in PRINTED.values()):10.1f} "
            for m in MATERIALS))
        print("\n  Note: the matrix shows each part fully in each material;")
        print("  the printed total includes only the selected assignment.")
        results = [("MATRIX", None, None)]
    elif a.config == "all":
        for name in POLICIES:
            rows, tot = build(name, a.battery, a.cell, a.fc, a.fpv, a.prop,
                              a.fin, a.servo_heavy, a.motor)
            print_config(name, rows, tot)
            results.append((name, rows, tot))
    else:
        rows, tot = build(a.config, a.battery, a.cell, a.fc, a.fpv, a.prop,
                          a.fin, a.servo_heavy, a.motor)
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

    rows, tot = build("all_petg", "6S1P", "P42A", "FC_AVG", "O4-Pro")
    check(f"Baseline all-PETG 6S1P = 1687 ± 2 g (I-16 pack 445 g; got {tot['auw']:.1f})",
          abs(tot["auw"] - 1687.0) <= 2.0)
    check(f"Baseline V_stall = 45.9 ± 0.15 km/h (got {tot['vs']:.2f})",
          abs(tot["vs"] - 45.9) <= 0.15)
    check("Baseline wing loading = 59.8 ± 0.5 g/dm² "
          f"(got {tot['wl']:.2f})", abs(tot["wl"] - 59.8) <= 0.5)
    for cfg, cell, exp in [("6S1P", "P42A", 445.0), ("6S1P", "50E", 433.0),
                           ("4S1P", "P42A", 305.0), ("4S1P", "50E", 297.0)]:
        got = pack_mass(cfg, cell)
        check(f"Pack {cfg} {cell} = {exp:.0f} g (got {got:.0f})", abs(got - exp) <= 1)
    check("Pure-AERO shell = 600×0.68/1.27 = 321.3 g "
          f"(got {scale(600.0,'AERO_PLA'):.1f})",
          abs(scale(600.0, "AERO_PLA") - 321.26) < 0.5)
    check("Pure-PLA+ shell = 600×1.24/1.27 = 585.8 g "
          f"(got {scale(600.0,'PLA_PLUS'):.1f})",
          abs(scale(600.0, "PLA_PLUS") - 585.83) < 0.5)
    check("Printed parts sum = 600 g (core+wings+tips+elevons)",
          abs(PRINTED["core"]["m"] + PRINTED["wings"]["m"] +
              PRINTED["tips"]["m"] + PRINTED["elevons"]["m"] - 600.0) < 1e-6)
    check("Balance rule: 50 g elevons -> 60 g balance",
          abs(1.2 * PRINTED["elevons"]["m"] - 60.0) < 1e-6)
    _, ta = build("aero_wings", "6S1P", "P42A")
    check(f"AERO_WINGS 6S1P: V_stall <= 45 km/h (got {ta['vs']:.2f})",
          ta["vs"] <= 45.0)
    print(f"\n  VALIDATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")

    # ---- markdown report ----
    if a.out:
        lines = ["# Salamandra mass budget — material variants (2026-08-06)",
                 "",
                 f"Battery {a.battery} {a.cell} · FC {a.fc} · FPV {a.fpv} · "
                 f"prop {a.prop} · fin {'V1' if a.fin else 'CLEAN'} · "
                 f"servos {'heavy' if a.servo_heavy else '12-15 g class'}",
                 "", "| Config | AUW (g) | g/dm² | V_stall (km/h) | printed (g) | "
                 "printed cost (€) |",
                 "|---|---|---|---|---|---|"]
        for name, rows, tot in results:
            if tot is None:
                continue
            lines.append(f"| **{name}** | {tot['auw']:.1f} | {tot['wl']:.1f} | "
                         f"{tot['vs']:.1f} | {tot['printed']:.0f} | "
                         f"{tot['cost']:.2f} |")
        lines += ["", "Rows are [E]/[D] on [M] data — see "
                  "docs/06-material-mass-variants.md.", ""]
        with open(a.out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\nReport written: {a.out}")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
