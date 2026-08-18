#!/usr/bin/env python3
"""
Layout analysis of 4S and 6S packs of 21700 Li-Ion cells.

Enumerates every rectangular arrangement (n_x, n_y, n_z) of the pack of N cells
and computes the physical envelope (Length x Width x Height) for the two
horizontal cell orientations that are admissible in an aircraft bay:

    orientation A : cell axis parallel to the pack Length (in-line, "longitudinal")
    orientation B : cell axis parallel to the pack Width  (transverse, "flat")

Height is always n_z * D because the cells are cylinders lying on their side.

Outputs are [D] (derived from the declared cell inputs). The cell inputs are
taken from manufacturer datasheets [M] plus a declared wrapper allowance [E].
Full source / confidence discussion in research/I-16-battery-pack-layout.md.

Bay check uses the Salamandra reference bay (guide §8, PROVISIONAL; superseded by the cradle):
    bay (x,y,z) = 190 x 70 x 32 mm, single 21 mm layer, never stacked.
"""

# --- cell inputs ----------------------------------------------------------
D_NOM = 21.0     # mm, 21700 nominal diameter, manufacturer datasheet [M]
L_NOM = 70.0     # mm, 21700 nominal length,  manufacturer datasheet [M]
WRAP = 0.15      # mm/side, PVC heat-shrink wrapper thickness [E]
D = D_NOM + 2 * WRAP     # 21.3 mm wrapped diameter
L = L_NOM + 2 * WRAP     # 70.3 mm wrapped length

# --- pack-level assembly allowances [E] -----------------------------------
PVC_OUTER = 0.3      # mm/side outer shrink wrap -> +0.6 mm per dimension
NICKEL    = 0.3      # mm, nickel-strip stack added to the smallest face
LEAD_ADD  = 12.0     # mm, XT60 main + balance lead protrusion on one Length end
GAP       = 0.0      # mm inter-cell clearance, 0.0 = tight, 0.5 = with slack

# --- Salamandra reference bay (guide §8, PROVISIONAL; superseded by the cradle) ----------------------
BAY = (190.0, 70.0, 32.0)   # (x, y, z) mm

# --- reference cells (datasheet [M], masses/pack via [D]) -------------------
# name : (mass_g, cap_Ah, Vnom, I_cont_A, I_chg_A, energy_Wh)
CELLS = {
    "Molicel P42A": (70.0, 4.2, 3.6, 45.0, 8.4, 15.12),
    "Samsung 50E":  (68.0, 5.0, 3.6, 9.8, 4.9, 18.00),
}
# arithmetic mean of the two reference cells (declared average point)
AVG = tuple(sum(v) / 2 for v in zip(*CELLS.values()))  # (69.0, 4.6, 3.6, 27.4, 6.65, 16.56)
HARDWARE = 25.0    # g, pack hardware (nickel, wires, XT60, wrap) [E]
CELL_ALIASES = {"P42A": "Molicel P42A", "50E": "Samsung 50E"}
P42A_DATASHEET_URL = (
    "https://www.molicel.com/wp-content/uploads/INR21700P42A-V4-80092.pdf"
)
# Maximum sleeved cell envelope for CAD packaging.  This is deliberately
# separate from the nominal generic-21700 model above: fit decisions must use
# manufacturer maxima, while concept enumeration may retain nominal geometry.
CELL_MAX_DIMENSIONS_MM = {
    # Molicel P42A v4 product data sheet: height and diameter maxima [M].
    "Molicel P42A": (70.2, 21.7),  # (length, diameter)
}
REFERENCE_LAYOUTS = {
    "4S1P": (2, 2, 1, "A"),
    "6S1P": (2, 3, 1, "A"),
}


def factor_triples(N):
    """All (n_x, n_y, n_z) positive-integer triples with product == N.

    The axes have distinct physical roles, so each ordered triple is a
    distinct arrangement. Divisors of N span every valid combination.
    """
    divs = [d for d in range(1, N + 1) if N % d == 0]
    out = []
    for nx in divs:
        for ny in divs:
            nz = N // (nx * ny)
            if nx * ny * nz == N:
                out.append((nx, ny, nz))
    return out


def envelope(nx, ny, nz, orient):
    """Return (Length, Width, Height) mm of a raw cell block, before assembly.

    orient 'A': cell axis parallel to Length (L along x, D along y,z)
    orient 'B': cell axis parallel to Width  (L along y, D along x,z)
    """
    if orient == "A":
        Lx = nx * L + max(0, nx - 1) * GAP
        Wy = ny * D + max(0, ny - 1) * GAP
    else:  # 'B'
        Lx = nx * D + max(0, nx - 1) * GAP
        Wy = ny * L + max(0, ny - 1) * GAP
    Hz = nz * D + max(0, nz - 1) * GAP
    return (Lx, Wy, Hz)


def assemble(block):
    """Add pack-level assembly allowances to a raw block.

    Returns (Length, Width, Height) of the finished, wrapped pack.
    +0.6 mm/side-pair PVC outer wrap on all three axes; +nickel on height;
    +balance/connector lead on Length.
    """
    Lx, Wy, Hz = block
    Lx += 2 * PVC_OUTER + LEAD_ADD
    Wy += 2 * PVC_OUTER
    Hz += 2 * PVC_OUTER + NICKEL
    return (Lx, Wy, Hz)


def fits(px, bay):
    """Does the finished pack fit the Salamandra bay?

    The bay is a horizontal channel (x x y x z) = 190 x 70 x 32 mm, single
    layer, never stacked. The pack Height (n_z*D + allowances) is the vertical
    (z) envelope and must be <= bay_z. The horizontal footprint (Length, Width)
    must sit in the 190 x 70 plane, allowing Length/Width swap (rotation in the
    horizontal plane only).
    """
    L, W, H = px
    bay_x, bay_y, bay_z = bay
    if H > bay_z:
        return False
    return (L <= bay_x and W <= bay_y) or (L <= bay_y and W <= bay_x)


def cell_count(configuration):
    """Number of cells in an NsMp pack configuration string."""
    try:
        series_text, parallel_text = configuration.upper().split("S", 1)
        parallel_text = parallel_text.removesuffix("P")
        count = int(series_text) * int(parallel_text)
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid pack configuration {configuration!r}") from exc
    if count <= 0:
        raise ValueError("pack cell count must be positive")
    return count


def pack_mass_g(configuration, cell="P42A"):
    """Installed pack mass [g] from shared cell data and hardware allowance."""
    canonical = CELL_ALIASES.get(cell, cell)
    if canonical not in CELLS:
        raise ValueError(f"unknown cell {cell!r}")
    return cell_count(configuration) * CELLS[canonical][0] + HARDWARE


def reference_pack_envelope(configuration):
    """Finished reference one-layer pack envelope [mm]."""
    if configuration not in REFERENCE_LAYOUTS:
        raise ValueError(f"no released one-layer layout for {configuration!r}")
    nx, ny, nz, orientation = REFERENCE_LAYOUTS[configuration]
    return assemble(envelope(nx, ny, nz, orientation))


def reference_pack_cad_envelope(configuration, cell="P42A"):
    """Finished reference envelope from manufacturer maximum cell dimensions.

    The datasheet maximum already includes the individual cell sleeve, so the
    nominal-model ``WRAP`` allowance is not added a second time.  Pack-level
    wrap, nickel and lead allowances remain explicit estimates.
    """
    if configuration not in REFERENCE_LAYOUTS:
        raise ValueError(f"no released one-layer layout for {configuration!r}")
    canonical = CELL_ALIASES.get(cell, cell)
    if canonical not in CELL_MAX_DIMENSIONS_MM:
        raise ValueError(f"no maximum CAD dimensions for cell {cell!r}")
    cell_length, cell_diameter = CELL_MAX_DIMENSIONS_MM[canonical]
    nx, ny, nz, orientation = REFERENCE_LAYOUTS[configuration]
    if orientation == "A":
        block = (
            nx * cell_length + max(0, nx - 1) * GAP,
            ny * cell_diameter + max(0, ny - 1) * GAP,
            nz * cell_diameter + max(0, nz - 1) * GAP,
        )
    else:
        block = (
            nx * cell_diameter + max(0, nx - 1) * GAP,
            ny * cell_length + max(0, ny - 1) * GAP,
            nz * cell_diameter + max(0, nz - 1) * GAP,
        )
    return assemble(block)


def _invalid_pack_is_rejected():
    try:
        cell_count("not-a-pack")
    except ValueError:
        return True
    return False


def main():
    print("=" * 74)
    print("PACK LAYOUT — 4S / 6S · 21700 Li-Ion")
    print("=" * 74)
    print(f"Cell inputs: D = {D_NOM:.1f} mm, L = {L_NOM:.1f} mm (datasheet [M]);")
    print(f"  wrapper +{WRAP} mm/side [E] -> wrapped D = {D:.1f}, L = {L:.1f} mm")
    print(f"Assembly: outer wrap +{PVC_OUTER} mm/side, nickel +{NICKEL} mm,")
    print(f"  leads +{LEAD_ADD:.0f} mm on Length, inter-cell gap {GAP} mm")
    print(f"Reference bay (x,y,z) = {tuple(int(v) for v in BAY)} mm  (guide §8, PROVISIONAL; superseded by the cradle)")
    print("  note: bay height 32 mm accommodates a single 21 mm layer (n_z = 1).")
    print("  A pack taller than the bay is possible only if the bay is resized "
          "by the designer; this is a reference, not a verdict.\n")
    cad_envelope = reference_pack_cad_envelope("6S1P", "P42A")
    print(
        "P42A maximum-dimension CAD envelope [M]/[E]: "
        + " x ".join(f"{value:.1f}" for value in cad_envelope)
        + " mm\n"
    )

    for N in (4, 6):
        print("-" * 74)
        print(f"{N}S PACK  ({N} cells)")
        print(f"{'arrangement':>12} {'orientation':>12} {'cell block (LxWxH)':>22} "
              f"{'pack (LxWxH)':>20} {'bay ok':>7}")
        print("-" * 74)
        for nx, ny, nz in sorted(factor_triples(N), key=lambda t: (t[2], max(t), t)):
            for orient in ("A", "B"):
                block = envelope(nx, ny, nz, orient)
                pck = assemble(block)
                ok = fits(pck, BAY)
                tag = "YES" if ok else "no"
                print(f"{f'{nx}x{ny}x{nz}':>12} {orient:>12} "
                      f"({block[0]:5.1f} x{block[1]:5.1f} x{block[2]:5.1f}) "
                      f"({pck[0]:5.1f} x{pck[1]:5.1f} x{pck[2]:5.1f}) {tag:>7}")
        print()

    # --- summary: best / smallest-envelope single-layer options -------------
    print("-" * 74)
    print("SINGLE-LAYER (n_z=1) PACKS SORTED BY VOLUME")
    print(f"{'pack':>6} {'arr':>8} {'orient':>4} {'pack LxWxH (mm)':>22} {'vol (L)':>9} "
          f"{'mass* (g)':>9} {'Wh (4.2V)':>10}")
    print("-" * 74)
    for N, name in ((4, "4S"), (6, "6S")):
        rows = []
        for nx, ny, nz in factor_triples(N):
            if nz != 1:
                continue
            for orient in ("A", "B"):
                pck = assemble(envelope(nx, ny, nz, orient))
                vol = pck[0] * pck[1] * pck[2] / 1e3  # cm^3 = mL
                rows.append((vol, nx, ny, nz, orient, pck))
        rows.sort()
        for vol, nx, ny, nz, orient, pck in rows:
            mass = N * 68.0                       # ~68 g/cell [M]
            wh = N * 3.6 * 5.0                    # ~18 Wh/cell nominal [M]
            print(f"{name:>6} {f'{nx}x{ny}x{nz}':>8} {orient:>4} "
                  f"{pck[0]:6.1f} x{pck[1]:5.1f} x{pck[2]:5.1f} "
                  f"{vol:8.2f} {mass:8.0f} {wh:9.1f}")
        print()

    # --- mass / energy / discharge by reference cell ------------------------
    print("-" * 74)
    print("MASS / ENERGY / DISCHARGE BY REFERENCE CELL  (4S1P and 6S1P series)")
    print("-" * 74)
    rows_cell = list(CELLS.items()) + [("Average (P42A+50E)", AVG)]
    print(f"{'cell':>20} {'mass':>6} {'cap':>6} {'Vnom':>5} {'I cont':>7} "
          f"{'I chg':>6} {'Wh':>6} {'Wh/kg':>6}")
    print("-" * 74)
    for name, (m, q, v, ic, ich, wh) in rows_cell:
        print(f"{name:>20} {m:>5.1f} {q:>5.2f} {v:>5.2f} {ic:>6.1f} "
              f"{ich:>6.1f} {wh:>5.1f} {wh/m*1000:>6.0f}")
    print()
    for N, name in ((4, "4S1P"), (6, "6S1P")):
        print(f"  {name}  (physical layout: {('2x2' if N==4 else '2x3')} single layer, orient. A):")
        print(f"    {'cell':>20} {'mass g':>8} {'+hw':>8} {'Wh':>8} {'Ah':>6} "
              f"{'Vnom':>6} {'Vmax':>6} {'Wh/kg':>7} {'I pack':>7}")
        for cname, (m, q, v, ic, ich, wh) in rows_cell:
            pm = N * m
            pwh = N * wh
            pakw = pm + HARDWARE
            print(f"    {cname:>20} {pm:>7.0f} {pakw:>7.0f} {pwh:>7.1f} "
                  f"{N*q:>6.2f} {N*v:>6.1f} {N*4.2:>6.1f} {pwh/pakw*1000:>7.0f} {ic:>7.1f}")
        print()

    checks = {
        "4S1P P42A installed mass is 305 g":
            abs(pack_mass_g("4S1P", "P42A") - 305.0) < 1e-12,
        "6S1P P42A installed mass is 445 g":
            abs(pack_mass_g("6S1P", "P42A") - 445.0) < 1e-12,
        "6S1P reference envelope is 153.2 x 64.5 x 22.2 mm": all(
            abs(got - expected) < 0.05
            for got, expected in zip(
                reference_pack_envelope("6S1P"), (153.2, 64.5, 22.2))),
        "6S1P P42A maximum CAD envelope is 153.0 x 65.7 x 22.6 mm": all(
            abs(got - expected) < 0.05
            for got, expected in zip(
                reference_pack_cad_envelope("6S1P", "P42A"),
                (153.0, 65.7, 22.6),
            )
        ),
        "released 4S1P and 6S1P layouts fit the bay": all(
            fits(reference_pack_envelope(name), BAY)
            for name in REFERENCE_LAYOUTS),
        "invalid pack configuration is rejected": _invalid_pack_is_rejected(),
    }
    print("VALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
