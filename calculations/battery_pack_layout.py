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

Bay check uses the Salamandra reference bay (guide §9, PROVISIONAL):
    bay (x,y,z) = 190 x 70 x 32 mm, single 21 mm layer, never stacked.
"""
import itertools

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

# --- Salamandra reference bay (guide §9, PROVISIONAL) ----------------------
BAY = (190.0, 70.0, 32.0)   # (x, y, z) mm


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


def main():
    print("=" * 74)
    print("PACK LAYOUT — 4S / 6S · 21700 Li-Ion")
    print("=" * 74)
    print(f"Cell inputs: D = {D_NOM:.1f} mm, L = {L_NOM:.1f} mm (datasheet [M]);")
    print(f"  wrapper +{WRAP} mm/side [E] -> wrapped D = {D:.1f}, L = {L:.1f} mm")
    print(f"Assembly: outer wrap +{PVC_OUTER} mm/side, nickel +{NICKEL} mm,")
    print(f"  leads +{LEAD_ADD:.0f} mm on Length, inter-cell gap {GAP} mm")
    print(f"Reference bay (x,y,z) = {tuple(int(v) for v in BAY)} mm  (guide §9, PROVISIONAL)")
    print(f"  note: bay height 32 mm -> only n_z = 1 layer fits (single layer rule).\n")

    for N in (4, 6):
        print("-" * 74)
        print(f"{N}S PACK  ({N} cells)")
        print(f"{'arrangement':>12} {'orientation':>12} {'cell block (LxWxH)':>22} "
              f"{'pack (LxWxH)':>20} {'fits bay':>9}")
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


if __name__ == "__main__":
    main()
