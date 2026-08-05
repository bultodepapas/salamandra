#!/usr/bin/env python3
"""
B3 screening: XFOIL polars for the Salamandra airfoil shortlist.

Reproducible method (2026-08-05, results in research/I-15 §6):
  - Coordinates: geometry/airfoils/*.dat (UIUC Selig format, TE->LE->TE).
    Provenance documented in geometry/airfoils/README.md.
  - Variants: affine thickness scaling (y * target_tc / current_tc).
  - XFOIL 6.99 (official MIT Windows console binary, GPL), batch mode.
  - Re = 3e5 and 5e5; Ncrit = 10 and 12 (the I-06 calibrated band).
  - Alpha sweep 0..16 deg step 0.5, ITER 300.
  - Polar files land in calculations/xfoil_out/ and are reused if their
    header already carries the requested Re and Ncrit (incremental runs).

XFOIL batch-mode notes (solved on 2026-08-05, baked in):
  - The Ncrit command lives in the VPAR submenu: OPER -> VPAR -> N <value>.
  - Polar accumulation: PACC (prompts: save file, then dump file = blank),
    then ASEQ; end with PACC (off) + PWRT 1 + filename.
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
import math
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AF_DIR = os.path.join(ROOT, "geometry", "airfoils")
OUT = os.path.join(ROOT, "calculations", "xfoil_out")
os.makedirs(OUT, exist_ok=True)


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
    n = len(pts) // 2
    top = sorted(pts[:n], key=lambda p: p[0])
    bot = sorted(pts[n:], key=lambda p: p[0])
    tmax = 0.0
    for u, l in zip(top, bot):
        tmax = max(tmax, u[1] - l[1])
    return tmax


def scale_tc(pts, target_tc):
    """Affine thickness scaling: y *= target_tc / current_tc (camber line kept)."""
    tc = thickness(pts)
    k = target_tc / tc
    return [(x, y * k) for x, y in pts]


def write_dat(pts, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{os.path.basename(path)}\n")
        for x, y in pts:
            f.write(f"{x: .8f} {y: .8f}\n")


def run_xfoil(dat_path, re_no, ncrit, tag, xfoil):
    pol = os.path.join(OUT, f"{tag}.pol")
    if os.path.exists(pol):
        header = open(pol, encoding="utf-8", errors="ignore").read()
        ok_ncrit = re.search(rf"Ncrit\s*=\s*{ncrit}\.000", header) is not None
        ok_re = re.search(rf"Re\s*=\s*{re_no/1e6:.3f} e 6", header) is not None
        if ok_ncrit and ok_re:
            return parse_polar(pol)          # reuse valid polar (incremental)
        os.remove(pol)
    inp_file = os.path.join(OUT, f"{tag}.inp")
    inp = (
        f"LOAD {dat_path}\r\n"
        "PANE\r\n"
        "OPER\r\n"
        f"ITER 300\r\n"
        f"VISC {re_no}\r\n"
        "VPAR\r\n"
        f"N\r\n{ncrit}\r\n"
        "\r\n"
        "PACC\r\n"
        f"{pol}\r\n"
        "\r\n"
        "ASeq 0.0 16.0 0.5\r\n"
        "PACC\r\n"
        "PWRT 1\r\n"
        f"{pol}\r\n"
        "QUIT\r\n"
        "Y\r\n"
    )
    with open(inp_file, "w", encoding="ascii", newline="") as f:
        f.write(inp)
    with open(inp_file, "r", encoding="ascii") as f:
        for attempt in range(3):
            try:
                proc = subprocess.run(
                    [xfoil], stdin=f, capture_output=True, text=True, timeout=300
                )
                break
            except subprocess.TimeoutExpired:
                f.seek(0)
                if attempt == 2:
                    print(f"  !! xfoil timed out 3x for {tag}")
                    return None
                print(f"  !! timeout for {tag}, retrying ({attempt+1})")
    if not os.path.exists(pol):
        print(f"  !! no polar for {tag} (xfoil tail: {proc.stdout[-300:]})")
        return None
    header = open(pol, encoding="utf-8", errors="ignore").read()
    ok_ncrit = re.search(rf"Ncrit\s*=\s*{ncrit}\.000", header) is not None
    ok_re = re.search(rf"Re\s*=\s*{re_no/1e6:.3f} e 6", header) is not None
    if not ok_ncrit:
        print(f"  !! Ncrit NOT applied for {tag} (header: "
              f"{[l for l in header.splitlines() if 'Ncrit' in l]})")
    if not ok_re:
        print(f"  !! Re NOT applied for {tag} (header: "
              f"{[l for l in header.splitlines() if 'Re =' in l]})")
    return parse_polar(pol)


def parse_polar(pol):
    rows = []
    with open(pol, encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 7:
                try:
                    a, cl, cd, cdp, cm, xtr, btr = [float(p) for p in parts]
                    rows.append((a, cl, cd, cm))
                except ValueError:
                    pass
    return rows


def summarize(rows):
    if not rows:
        return None
    lin = [r for r in rows if r[1] < 0.6]          # linear pre-stall range
    a, cl, cd, cm = zip(*rows)
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
    # cd at cruise CL = 0.132 (interpolate; extrapolate linearly from the first
    # two points if the first computed alpha is already above cruise CL)
    cd_cruise = None
    if len(cl) >= 2:
        if cl[0] > 0.132:
            f = (0.132 - cl[0]) / (cl[1] - cl[0])
            cd_cruise = cd[0] + f * (cd[1] - cd[0])
        else:
            for i in range(len(cl) - 1):
                if cl[i] <= 0.132 <= cl[i + 1]:
                    f = (0.132 - cl[i]) / (cl[i + 1] - cl[i])
                    cd_cruise = cd[i] + f * (cd[i + 1] - cd[i])
                    break
    return dict(cm0=cm0, clmax=clmax, astall=astall, ldmax=ld, cd_cruise=cd_cruise)


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
        ("mh60-12", "mh60.dat", 0.12, "MH60 scaled to 12 %"),
        ("mh60-135", "mh60.dat", 0.135, "MH60 scaled to 13.5 % (root variant)"),
    ]
    cases = []
    for tag, fname, target, label in candidates:
        pts = load_dat(os.path.join(AF_DIR, fname))
        if target is not None:
            pts = scale_tc(pts, target)
            dat = os.path.join(AF_DIR, f"{tag}.dat")
            write_dat(pts, dat)
            dat_src = f"{tag}.dat (scaled)"
        else:
            dat = os.path.join(AF_DIR, fname)
            dat_src = fname
        cases.append((tag, dat, label))

    print("=" * 110)
    print("B3 SCREENING — XFOIL 6.99 batch, Ncrit 10/12, Re 3e5/5e5 (all [D])")
    print("=" * 110)
    hdr = f"{'case':<12}{'Re':>6}{'Nc':>4}{'cm0':>9}{'clmax':>7}{'a_st':>6}{'L/Dmax':>8}{'cd@CL.132':>10}"
    print(hdr)
    print("-" * 110)
    results = {}
    for tag, dat, label in cases:
        tc_now = thickness(load_dat(dat))
        print(f"# {label}  (t/c = {tc_now*100:.2f} %)")
        for re_no in (3e5, 5e5):
            for ncrit in (10, 12):
                rtag = f"{tag}_r{int(re_no/1e5)}e5_n{ncrit}"
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
