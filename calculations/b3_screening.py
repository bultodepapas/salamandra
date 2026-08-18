#!/usr/bin/env python3
"""
B3 screening: XFOIL polars for the Salamandra airfoil shortlist.

Reproducible method (revision 2, 2026-08-17):
  - Coordinates: geometry/airfoils/*.dat (UIUC Selig format, TE->LE->TE).
    Provenance documented in geometry/airfoils/README.md.
  - Variants: vertical thickness scaling about the interpolated mean camber
    line.  This preserves camber/reflex instead of multiplying every y value.
  - XFOIL 6.99 (official MIT Windows console binary, GPL), batch mode.
  - Re = 1.2e5, 2.5e5 and 5e5; Ncrit = 10 and 12.  These Reynolds numbers
    bracket the tip at 45 km/h, tip at cruise/root at stall, and root at cruise.
  - Alpha sweep 0..16 deg step 0.5, ITER 300.
  - Polar files land in calculations/xfoil_out/ and are reused only when a
    sidecar records the requested Re, Ncrit and SHA-256 of the input geometry.

XFOIL batch-mode notes (solved on 2026-08-05, baked in):
  - The Ncrit command lives in the VPAR submenu: OPER -> VPAR -> N <value>.
  - Polar accumulation: PACC (prompts: save file, then dump file = blank),
    then ASEQ; end with PACC (off).  PACC already writes every converged row;
    issuing PWRT to the same file creates an overwrite prompt and can hang batch mode.
  - The input file must use CRLF line endings; the Fortran runtime emits a
    harmless "End of file" message after QUIT (tolerated).

Getting the XFOIL executable:
  - Official Windows build 6.99: https://web.mit.edu/drela/Public/web/xfoil/
    (file XFOIL6.99.zip). Set the path via --xfoil or the XFOIL_EXE env var.

Dependencies: Python >= 3.8, numpy (parsing/summary). XFOIL itself is an
external GPL binary, not bundled with this repository.

Outputs (all [D]): XFOIL predictions, NOT measured polars. The I-06
calibration applies: Ncrit 10-12 band, E387 anchor (NASA-CR-186263).
"""
import argparse
import bisect
import hashlib
import json
import os
import re
import subprocess
import time

from design_config import (
    ROOT_TC,
    ARTICLE_V1_MASS_KG,
    CRUISE_SPEED_KMH,
    lift_coefficient,
    speed_mps,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AF_DIR = os.path.join(ROOT, "geometry", "airfoils")
OUT = os.path.join(ROOT, "calculations", "xfoil_out")
os.makedirs(OUT, exist_ok=True)
CRUISE_CL = lift_coefficient(
    ARTICLE_V1_MASS_KG, speed_mps(CRUISE_SPEED_KMH))


def find_xfoil(arg=None):
    """XFOIL executable: --xfoil CLI arg > XFOIL_EXE env var > PATH."""
    candidates = [arg, os.environ.get("XFOIL_EXE")]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    if arg and os.path.isfile(arg):
        return arg
    from shutil import which
    found = which("xfoil") or which("xfoil.exe")
    if found:
        return found
    raise SystemExit(
        "XFOIL executable not found. Download the official Windows build "
        "6.99 from https://web.mit.edu/drela/Public/web/xfoil/ "
        "(XFOIL6.99.zip) and pass it with --xfoil <path> or set XFOIL_EXE."
    )


def load_dat(path):
    pts = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    pts.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    pass
    return pts


def thickness(pts):
    """Maximum vertical thickness on a common x grid."""
    upper, lower = split_surfaces(pts)
    x0 = max(upper[0][0], lower[0][0])
    x1 = min(upper[-1][0], lower[-1][0])
    return max(
        interp_surface(upper, x) - interp_surface(lower, x)
        for x in (x0 + (x1 - x0) * i / 2000.0 for i in range(2001))
    )


def split_surfaces(pts):
    """Return upper/lower surfaces ordered from LE to TE."""
    if len(pts) < 5:
        raise ValueError("airfoil needs at least five coordinate points")
    ile = min(range(len(pts)), key=lambda i: pts[i][0])
    if ile == 0 or ile == len(pts) - 1:
        raise ValueError("expected Selig TE-upper -> LE -> TE-lower ordering")
    upper = sorted(pts[:ile + 1], key=lambda p: p[0])
    lower = sorted(pts[ile:], key=lambda p: p[0])
    return upper, lower


def interp_surface(surface, x):
    """Linear interpolation on an LE-to-TE surface."""
    xs = [p[0] for p in surface]
    i = bisect.bisect_left(xs, x)
    if i <= 0:
        return surface[0][1]
    if i >= len(surface):
        return surface[-1][1]
    x0, y0 = surface[i - 1]
    x1, y1 = surface[i]
    if abs(x1 - x0) < 1e-12:
        return 0.5 * (y0 + y1)
    f = (x - x0) / (x1 - x0)
    return y0 + f * (y1 - y0)


def scale_tc(pts, target_tc):
    """Scale vertical thickness while preserving the interpolated camber line."""
    upper, lower = split_surfaces(pts)
    k = target_tc / thickness(pts)
    ile = min(range(len(pts)), key=lambda i: pts[i][0])
    scaled = []
    for i, (x, y) in enumerate(pts):
        if i <= ile:
            opposite = interp_surface(lower, x)
        else:
            opposite = interp_surface(upper, x)
        camber = 0.5 * (y + opposite)
        scaled.append((x, camber + k * (y - camber)))

    # Interpolation between unequal upper/lower point grids introduces a small
    # second-order error.  One correction makes the written t/c exact to <1e-5.
    correction = target_tc / thickness(scaled)
    if abs(correction - 1.0) > 1e-7:
        return scale_thickness_by_factor(scaled, correction)
    return scaled


def scale_thickness_by_factor(pts, factor):
    """Apply a known thickness factor about the current mean camber line."""
    upper, lower = split_surfaces(pts)
    ile = min(range(len(pts)), key=lambda i: pts[i][0])
    out = []
    for i, (x, y) in enumerate(pts):
        opposite = interp_surface(lower if i <= ile else upper, x)
        camber = 0.5 * (y + opposite)
        out.append((x, camber + factor * (y - camber)))
    return out


def write_dat(pts, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{os.path.basename(path)}\n")
        f.writelines(f"{x: .8f} {y: .8f}\n" for x, y in pts)


def run_xfoil(dat_path, re_no, ncrit, tag, xfoil, *, alpha_end=16.0,
              alpha_step=0.5, iter_limit=300, stable_seconds=15.0):
    pol = os.path.join(OUT, f"{tag}.pol")
    pol_name = os.path.basename(pol)  # XFOIL has a short Fortran filename buffer
    meta_path = os.path.join(OUT, f"{tag}.meta.json")
    with open(dat_path, "rb") as f:
        dat_sha256 = hashlib.sha256(f.read()).hexdigest()
    expected_meta = {
        "analysis": (
            f"xfoil-6.99-aseq-0-{alpha_end:g}-{alpha_step:g}-"
            f"iter-{iter_limit}"),
        "dat_sha256": dat_sha256,
        "ncrit": int(ncrit),
        "reynolds": int(re_no),
    }
    if os.path.exists(pol) and os.path.exists(meta_path):
        with open(pol, encoding="utf-8", errors="ignore") as f:
            header = f.read()
        ok_ncrit = re.search(rf"Ncrit\s*=\s*{ncrit}\.000", header) is not None
        ok_re = re.search(rf"Re\s*=\s*{re_no/1e6:.3f} e 6", header) is not None
        try:
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
        except (OSError, ValueError):
            meta = None
        meta_matches = meta is not None and all(
            meta.get(key) == value for key, value in expected_meta.items())
        if ok_ncrit and ok_re and meta_matches:
            return parse_polar(pol)          # reuse valid polar (incremental)
    for stale in (pol, meta_path):
        if os.path.exists(stale):
            os.remove(stale)
    inp_file = os.path.join(OUT, f"{tag}.inp")
    inp = (
        f"LOAD {dat_path}\r\n"
        "PANE\r\n"
        "OPER\r\n"
        f"ITER {iter_limit}\r\n"
        f"VISC {re_no}\r\n"
        "VPAR\r\n"
        f"N\r\n{ncrit}\r\n"
        "\r\n"
        "PACC\r\n"
        f"{pol_name}\r\n"
        "\r\n"
        f"ASeq 0.0 {alpha_end:g} {alpha_step:g}\r\n"
        "PACC\r\n"
        "\r\n"
        "QUIT\r\n"
    )
    with open(inp_file, "w", encoding="ascii", newline="") as f:
        f.write(inp)
    # XFOIL can spend minutes iterating the first non-converged post-stall
    # point.  PACC flushes each converged row, so stop once the polar has made
    # no progress for 15 s.  This retains the converged pre-/near-stall data
    # and avoids misclassifying a solver hang as a completed 0..16 deg sweep.
    stopped_on_stable_polar = False
    with open(inp_file, "r", encoding="ascii") as f:
        proc = subprocess.Popen(
            [xfoil], stdin=f, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, text=True, cwd=OUT)
        deadline = time.monotonic() + 120.0
        last_signature = None
        last_progress = time.monotonic()
        while proc.poll() is None and time.monotonic() < deadline:
            if os.path.exists(pol):
                signature = (os.path.getsize(pol), os.path.getmtime(pol))
                if signature != last_signature:
                    last_signature = signature
                    last_progress = time.monotonic()
                elif time.monotonic() - last_progress >= stable_seconds:
                    stopped_on_stable_polar = True
                    proc.terminate()
                    break
            time.sleep(0.25)
        if proc.poll() is None:
            proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    if not os.path.exists(pol):
        print(f"  !! no polar for {tag}")
        return None
    with open(pol, encoding="utf-8", errors="ignore") as f:
        header = f.read()
    ok_ncrit = re.search(rf"Ncrit\s*=\s*{ncrit}\.000", header) is not None
    ok_re = re.search(rf"Re\s*=\s*{re_no/1e6:.3f} e 6", header) is not None
    if not ok_ncrit:
        print(f"  !! Ncrit NOT applied for {tag} (header: "
              f"{[l for l in header.splitlines() if 'Ncrit' in l]})")
    if not ok_re:
        print(f"  !! Re NOT applied for {tag} (header: "
              f"{[l for l in header.splitlines() if 'Re =' in l]})")
    rows = parse_polar(pol)
    if ok_ncrit and ok_re and rows:
        meta_out = dict(expected_meta)
        meta_out.update({
            "alpha_max_converged": max(row[0] for row in rows),
            "rows": len(rows),
            "stopped_on_stable_polar": stopped_on_stable_polar,
        })
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_out, f, indent=2, sort_keys=True)
            f.write("\n")
    return rows


def parse_polar(pol):
    rows = []
    with open(pol, encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 7:
                try:
                    a, cl, cd, _, cm, _, _ = [float(p) for p in parts]
                    rows.append((a, cl, cd, cm))
                except ValueError:
                    pass
    return rows


def summarize(rows, cruise_cl=CRUISE_CL):
    """Summarize a polar at the connected Article #1 cruise lift coefficient."""
    if not rows:
        return None
    if cruise_cl <= 0.0:
        raise ValueError("cruise CL must be positive")
    # Only the first monotonic pre-stall branch belongs in the CM(CL) fit.
    # A global ``CL < 0.6`` filter also admitted post-stall points after CL had
    # fallen again and could shift cm0 by more than 0.01 on reflexed sections.
    lin = []
    for row in rows:
        if row[1] >= 0.6:
            break
        lin.append(row)
    a, cl, cd, _ = zip(*rows)
    cm0 = None
    if len(lin) >= 3:
        n = len(lin)
        sx = sum(x[1] for x in lin); sy = sum(x[3] for x in lin)
        sxx = sum(x[1] ** 2 for x in lin); sxy = sum(x[1] * x[3] for x in lin)
        b = (n * sxy - sx * sy) / (n * sxx - sx * sx) if n * sxx != sx * sx else 0
        cm0 = (sy - b * sx) / n                      # CM at CL=0 (linear fit)
    clmax = max(cl)
    astall = a[cl.index(clmax)]
    ld = max(c / d for c, d in zip(cl, cd) if d > 0)
    # Cd at the shared cruise CL (interpolate; extrapolate linearly from the first
    # two points if the first computed alpha is already above cruise CL)
    cd_cruise = None
    if len(cl) >= 2:
        if cl[0] > cruise_cl:
            f = (cruise_cl - cl[0]) / (cl[1] - cl[0])
            cd_cruise = cd[0] + f * (cd[1] - cd[0])
        else:
            for i in range(len(cl) - 1):
                if cl[i] <= cruise_cl <= cl[i + 1]:
                    f = (cruise_cl - cl[i]) / (cl[i + 1] - cl[i])
                    cd_cruise = cd[i] + f * (cd[i + 1] - cd[i])
                    break
    return {"cm0": cm0, "clmax": clmax, "astall": astall, "ldmax": ld, "cd_cruise": cd_cruise}


def main():
    parser = argparse.ArgumentParser(
        description="B3 airfoil screening (XFOIL 6.99 batch).")
    parser.add_argument("--xfoil", help="path to the xfoil executable "
                        "(default: XFOIL_EXE env var, then PATH)")
    args = parser.parse_args()
    xfoil = find_xfoil(args.xfoil)
    print(f"XFOIL: {xfoil}")

    candidates = [
        ("e205", "e205.dat", None, "E205 (10.6 %, as-is)"),
        ("e205-9", "e205.dat", 0.09, "E205 scaled to 9 % (tip variant)"),
        ("s5010", "s5010.dat", None, "S5010 (9.83 %)"),
        ("mh60", "mh60.dat", None, "MH60 (10.08 %)"),
        ("mh60-9", "mh60.dat", 0.09,
         "MH60 scaled to 9 % with camber preserved (tip diagnostic)"),
        ("mh60-12", "mh60.dat", 0.12, "MH60 scaled to 12 %"),
        ("mh60-135", "mh60.dat", ROOT_TC,
         "MH60 scaled to the released root t/c (root variant)"),
    ]
    cases = []
    for tag, fname, target, label in candidates:
        pts = load_dat(os.path.join(AF_DIR, fname))
        if target is not None:
            pts = scale_tc(pts, target)
            dat = os.path.join(AF_DIR, f"{tag}.dat")
            write_dat(pts, dat)
        else:
            dat = os.path.join(AF_DIR, fname)
        cases.append((tag, dat, label))

    print("=" * 110)
    print("B3 SCREENING — XFOIL 6.99, Ncrit 10/12, Re 1.2e5/2.5e5/5e5 (all [D])")
    print("=" * 110)
    hdr = f"{'case':<12}{'Re':>6}{'Nc':>4}{'cm0':>9}{'clmax':>7}{'a_st':>6}{'L/Dmax':>8}{'cd@CL.132':>10}"
    print(hdr)
    print("-" * 110)
    results = {}
    for tag, dat, label in cases:
        tc_now = thickness(load_dat(dat))
        print(f"# {label}  (t/c = {tc_now*100:.2f} %)")
        for re_no in (1.2e5, 2.5e5, 5e5):
            for ncrit in (10, 12):
                rtag = f"{tag}_r{int(re_no/1e3)}k_n{ncrit}_v2"
                rows = run_xfoil(dat, int(re_no), ncrit, rtag, xfoil)
                s = summarize(rows)
                results[rtag] = s
                if s:
                    print(
                        f"{tag:<12}{int(re_no):>6}{ncrit:>4}"
                        f"{s['cm0'] if s['cm0'] is not None else float('nan'):>9.4f}"
                        f"{s['clmax']:>7.3f}{s['astall']:>6.1f}"
                        f"{s['ldmax']:>8.1f}{s['cd_cruise'] if s['cd_cruise'] else float('nan'):>10.4f}"
                    )
    print("=" * 110)
    print("cm0 = CM at CL=0 about c/4 (linear fit). clmax/a_st from the sweep.")
    print("I-06 calibration: Ncrit 10-12 is the declared band; polars are [D].")


if __name__ == "__main__":
    main()
