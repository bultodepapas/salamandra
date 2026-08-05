#!/usr/bin/env python3
"""
Calibra Ncrit de XFOIL contra la polar medida del E387 (C) de UIUC.

La salida de XFOIL sigue siendo [D]. Este script no convierte una polar calculada
en dato medido: cuantifica el desacuerdo frente a datos [M].

Fuentes primarias:
  - Coordenadas E387: UIUC Airfoil Data Site.
  - Polar E387 (C): UIUC LSATs, Summary of Low-Speed Airfoil Data, Vol. 3.
  - Ejecutable XFOIL: distribución oficial de Mark Drela (MIT).
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.request import urlopen


COORD_URL = "https://m-selig.ae.illinois.edu/ads/coord_seligFmt/e387.dat"
DRAG_URL = "https://m-selig.ae.illinois.edu/pd/pub/lsat/vol3/E387C.DRG"


def parse_uiuc_drag(text: str) -> dict[int, list[tuple[float, float, float]]]:
    """Devuelve {Re: [(alpha, Cl, Cd), ...]} desde E387C.DRG."""
    lines = text.splitlines()
    blocks: dict[int, list[tuple[float, float, float]]] = {}
    i = 0
    while i < len(lines):
        if lines[i].strip() != "Average Reynolds #:":
            i += 1
            continue

        reynolds = int(lines[i + 1].strip())
        i += 2
        while i < len(lines) and lines[i].strip() != "Number of angles of attack:":
            i += 1
        if i + 2 >= len(lines):
            raise ValueError("Bloque UIUC incompleto")

        count = int(lines[i + 1].strip())
        i += 3  # salta cantidad y cabecera de columnas
        rows: list[tuple[float, float, float]] = []
        for _ in range(count):
            values = lines[i].split()
            if len(values) < 3:
                raise ValueError(f"Fila UIUC inválida: {lines[i]!r}")
            rows.append(tuple(map(float, values[:3])))
            i += 1
        blocks[reynolds] = rows

    if not blocks:
        raise ValueError("No se encontraron bloques de Reynolds en E387C.DRG")
    return blocks


def parse_xfoil_polar(text: str) -> list[tuple[float, float, float]]:
    """Devuelve [(alpha, Cl, Cd), ...] desde un archivo PACC de XFOIL."""
    rows: list[tuple[float, float, float]] = []
    for line in text.splitlines():
        values = line.split()
        if len(values) < 7:
            continue
        try:
            alpha, cl, cd = map(float, values[:3])
        except ValueError:
            continue
        rows.append((alpha, cl, cd))
    return rows


def interpolate_cd(polar: list[tuple[float, float, float]], cl: float) -> float | None:
    """Interpolación lineal de Cd(Cl), sin extrapolar."""
    points = sorted((row[1], row[2]) for row in polar)
    for (cl0, cd0), (cl1, cd1) in zip(points, points[1:]):
        if cl0 <= cl <= cl1 and cl1 > cl0:
            weight = (cl - cl0) / (cl1 - cl0)
            return cd0 + weight * (cd1 - cd0)
    return None


def mismatch_factor(
    measured: list[tuple[float, float, float]],
    predicted: list[tuple[float, float, float]],
    cl_min: float,
    cl_max: float,
) -> tuple[float, int]:
    """
    Devuelve exp(RMSE(log(Cd_xfoil/Cd_medido))).

    Un valor 1 es coincidencia exacta; 1,20 representa un desacuerdo
    multiplicativo RMS del orden del 20 %.
    """
    errors: list[float] = []
    for _, cl, cd in measured:
        if not cl_min <= cl <= cl_max:
            continue
        predicted_cd = interpolate_cd(predicted, cl)
        if predicted_cd is not None and predicted_cd > 0.0 and cd > 0.0:
            errors.append(math.log(predicted_cd / cd))
    if not errors:
        raise ValueError("No hay puntos comunes de Cl para comparar")
    rmse = math.sqrt(sum(error * error for error in errors) / len(errors))
    return math.exp(rmse), len(errors)


def run_xfoil(
    executable: Path,
    workdir: Path,
    reynolds: int,
    ncrit: float,
    timeout: float,
) -> list[tuple[float, float, float]]:
    """Ejecuta una rama pre-pérdida desde alpha=0° hasta 9°."""
    suffix = str(ncrit).replace(".", "p")
    polar_path = workdir / f"polar_re{reynolds}_n{suffix}.txt"
    commands = f"""PLOP
G F

LOAD e387.dat
PANE
OPER
VISC {reynolds}
VPAR
N {ncrit}

ITER 250
PACC
{polar_path.name}

ASEQ 0 9 0.5
PACC
"""
    subprocess.run(
        [str(executable)],
        input=commands,
        text=True,
        cwd=workdir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
        check=False,
    )
    if not polar_path.exists():
        raise RuntimeError(f"XFOIL no produjo {polar_path.name}")
    polar = parse_xfoil_polar(polar_path.read_text(errors="replace"))
    if len(polar) < 5:
        raise RuntimeError(
            f"Polar insuficiente en Re={reynolds}, Ncrit={ncrit}: {len(polar)} puntos"
        )
    return polar


def fetch(url: str, destination: Path) -> None:
    with urlopen(url, timeout=30) as response:
        destination.write_bytes(response.read())


def self_check() -> None:
    """Caso analítico: interpolación lineal y error multiplicativo conocidos."""
    polar = [(0.0, 0.0, 0.010), (1.0, 1.0, 0.020)]
    assert math.isclose(interpolate_cd(polar, 0.5) or 0.0, 0.015, rel_tol=1e-12)

    measured = [(0.0, 0.25, 0.0125), (1.0, 0.75, 0.0175)]
    predicted = [(0.0, 0.0, 0.011), (1.0, 1.0, 0.022)]
    factor, count = mismatch_factor(measured, predicted, 0.0, 1.0)
    assert count == 2
    assert math.isclose(factor, 1.1, rel_tol=1e-12)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--xfoil",
        type=Path,
        default=os.environ.get("XFOIL_EXE"),
        help="Ruta al ejecutable oficial de XFOIL (o variable XFOIL_EXE)",
    )
    parser.add_argument(
        "--ncrit",
        nargs="+",
        type=float,
        default=[8, 9, 10, 11, 12],
        help="Valores Ncrit a contrastar",
    )
    parser.add_argument("--cl-min", type=float, default=0.25)
    parser.add_argument("--cl-max", type=float, default=0.85)
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()

    self_check()
    print("VALIDACIÓN INTERNA: interpolación y métrica exactas  [OK]")

    if args.xfoil is None:
        parser.error("indica --xfoil o define XFOIL_EXE")
    executable = args.xfoil.expanduser().resolve()
    if not executable.is_file():
        parser.error(f"no existe el ejecutable: {executable}")

    with tempfile.TemporaryDirectory(prefix="salmandra_xfoil_") as tmp:
        workdir = Path(tmp)
        fetch(COORD_URL, workdir / "e387.dat")
        fetch(DRAG_URL, workdir / "E387C.DRG")
        measured = parse_uiuc_drag((workdir / "E387C.DRG").read_text())
        reynolds_values = sorted(measured)

        predictions: dict[float, dict[int, list[tuple[float, float, float]]]] = {}
        for ncrit in args.ncrit:
            predictions[ncrit] = {}
            for reynolds in reynolds_values:
                predictions[ncrit][reynolds] = run_xfoil(
                    executable, workdir, reynolds, ncrit, args.timeout
                )

        # Todos los Ncrit se puntúan contra exactamente los mismos puntos medidos.
        # Así, una corrida con peor convergencia no obtiene ventaja por omitir casos.
        common_measured: dict[int, list[tuple[float, float, float]]] = {}
        for reynolds in reynolds_values:
            common_measured[reynolds] = [
                row
                for row in measured[reynolds]
                if args.cl_min <= row[1] <= args.cl_max
                and all(
                    interpolate_cd(predictions[ncrit][reynolds], row[1]) is not None
                    for ncrit in args.ncrit
                )
            ]
            if not common_measured[reynolds]:
                raise RuntimeError(
                    f"No hay puntos comunes a todos los Ncrit en Re={reynolds}"
                )

        results: dict[float, tuple[float, int, dict[int, tuple[float, int]]]] = {}
        print(
            f"\nCriterio [I]: {args.cl_min:.2f} ≤ Cl ≤ {args.cl_max:.2f}; "
            "métrica = exp(RMSE(log(Cd_XFOIL/Cd_UIUC)))"
        )
        print("Ncrit   global   puntos   " + "   ".join(f"Re={r}" for r in reynolds_values))

        for ncrit in args.ncrit:
            all_log_errors: list[float] = []
            per_re: dict[int, tuple[float, int]] = {}
            for reynolds in reynolds_values:
                predicted = predictions[ncrit][reynolds]
                factor, count = mismatch_factor(
                    common_measured[reynolds],
                    predicted,
                    args.cl_min,
                    args.cl_max,
                )
                per_re[reynolds] = (factor, count)

                # Reconstruye los errores para ponderar cada punto, no cada bloque.
                for _, cl, cd in common_measured[reynolds]:
                    predicted_cd = interpolate_cd(predicted, cl)
                    if predicted_cd is not None and predicted_cd > 0.0:
                        all_log_errors.append(math.log(predicted_cd / cd))

            global_factor = math.exp(
                math.sqrt(
                    sum(error * error for error in all_log_errors)
                    / len(all_log_errors)
                )
            )
            results[ncrit] = (global_factor, len(all_log_errors), per_re)
            cells = "   ".join(f"{per_re[r][0]:.3f}" for r in reynolds_values)
            print(f"{ncrit:5.1f}   {global_factor:6.3f}   "
                  f"{len(all_log_errors):6d}   {cells}")

        best_ncrit = min(results, key=lambda value: results[value][0])
        print(
            f"\nMejor ajuste global [D]: Ncrit={best_ncrit:g}, "
            f"factor RMS={results[best_ncrit][0]:.3f}"
        )
        print("Óptimo por Reynolds dentro de la rejilla [D]:")
        for reynolds in reynolds_values:
            local = min(
                results,
                key=lambda value: results[value][2][reynolds][0],
            )
            factor = results[local][2][reynolds][0]
            print(f"  Re={reynolds}: Ncrit={local:g}, factor={factor:.3f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
