#!/usr/bin/env python3
"""Deterministic feasibility-first trade runner for the provisional OML.

The default command writes an ASCII-safe manifest and an OBJ review mesh. It
does not select manufacturing geometry: the integrated-spindle family is the
Revision 3 starting candidate, and every artifact remains [I].
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import fuselage_contract
import fuselage_geometry


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "geometry" / "fuselage" / "provisional"
MANIFEST_NAME = "oml-manifest.json"
MESH_NAME = "integrated-spindle-body.obj"


@dataclass(frozen=True)
class Candidate:
    identifier: str
    design: fuselage_contract.OmlDesignVector
    report: dict[str, object]

    @property
    def objectives(self) -> tuple[float, float, float]:
        return (
            float(self.report["mesh"]["area_m2"]),
            float(self.report["projected"]["maximum_width_mm"]),
            float(self.report["fairness"]["total_curvature_energy"]),
        )


def latin_hypercube(samples: int, dimensions: int, seed: int) -> np.ndarray:
    """Seeded Latin hypercube with one point in every stratum per dimension."""
    if samples < 0 or dimensions < 1:
        raise ValueError("samples must be non-negative and dimensions positive")
    if samples == 0:
        return np.empty((0, dimensions), dtype=float)
    rng = np.random.default_rng(seed)
    result = np.empty((samples, dimensions), dtype=float)
    for dimension in range(dimensions):
        result[:, dimension] = (
            rng.permutation(samples) + rng.random(samples)
        ) / samples
    return result


def design_of_experiments(
    family: str,
    samples: int,
    seed: int,
) -> tuple[fuselage_contract.OmlDesignVector, ...]:
    base = fuselage_contract.OmlDesignVector(family=family)
    points = latin_hypercube(samples, 5, seed)
    designs = [base]
    for row in points:
        designs.append(
            base.perturbed(
                width_scale=0.94 + 0.14 * row[0],
                dorsal_scale=0.95 + 0.15 * row[1],
                ventral_scale=0.95 + 0.15 * row[2],
                waist_shift_mm=-3.0 + 6.0 * row[3],
                tail_scale=0.92 + 0.16 * row[4],
            )
        )
    return tuple(designs)


def nondominated_indices(objectives: np.ndarray) -> tuple[int, ...]:
    """Return indices not Pareto-dominated for minimization objectives."""
    if objectives.ndim != 2:
        raise ValueError("objectives must be a two-dimensional matrix")
    keep = []
    for index, candidate in enumerate(objectives):
        dominated = any(
            np.all(other <= candidate) and np.any(other < candidate)
            for other_index, other in enumerate(objectives)
            if other_index != index
        )
        if not dominated:
            keep.append(index)
    return tuple(keep)


def evaluate_candidate(
    identifier: str,
    design: fuselage_contract.OmlDesignVector,
    longitudinal: int,
    circumferential: int,
) -> Candidate:
    model = fuselage_geometry.build_model(design)
    return Candidate(
        identifier,
        design,
        fuselage_geometry.report_as_dict(model, longitudinal, circumferential),
    )


def candidate_summary(candidate: Candidate, pareto: bool) -> dict[str, object]:
    report = candidate.report
    return {
        "id": candidate.identifier,
        "family": candidate.design.family,
        "design_vector": {
            "width_scale": candidate.design.width_scale,
            "dorsal_scale": candidate.design.dorsal_scale,
            "ventral_scale": candidate.design.ventral_scale,
            "waist_shift_mm": candidate.design.waist_shift_mm,
            "tail_scale": candidate.design.tail_scale,
        },
        "geometry_feasible": report["geometry_feasible"],
        "aircraft_feasible": report["aircraft_feasible"],
        "pareto_geometry_screen": pareto,
        "objectives": {
            "gross_body_area_m2": candidate.objectives[0],
            "maximum_width_mm": candidate.objectives[1],
            "curvature_energy": candidate.objectives[2],
        },
        "minimum_envelope_margin_mm": min(
            audit["minimum_margin_mm"] for audit in report["envelope_audits"]
        ),
        "distribution": report["distribution"],
        "open_project_blockers": [
            name for name, passed in report["project_blockers"].items() if not passed
        ],
    }


def build_trade(
    family: str = "all",
    samples: int = 0,
    seed: int = 2801,
    longitudinal: int = 81,
    circumferential: int = 72,
    variant: str = "all",
) -> tuple[dict[str, object], str]:
    family_ids = (
        tuple(family.identifier for family in fuselage_contract.FAMILIES)
        if family == "all"
        else (family,)
    )
    candidates: list[Candidate] = []
    for family_index, family_id in enumerate(family_ids):
        for sample_index, design in enumerate(
            design_of_experiments(family_id, samples, seed + family_index)
        ):
            identifier = f"{family_id}-{sample_index:03d}"
            candidates.append(
                evaluate_candidate(
                    identifier,
                    design,
                    longitudinal,
                    circumferential,
                )
            )
    geometry_feasible = [candidate for candidate in candidates if candidate.report["geometry_feasible"]]
    pareto_ids: set[str] = set()
    if geometry_feasible:
        matrix = np.asarray([candidate.objectives for candidate in geometry_feasible])
        pareto_ids = {
            geometry_feasible[index].identifier
            for index in nondominated_indices(matrix)
        }
    selected = next(
        (
            candidate
            for candidate in candidates
            if candidate.design.family == fuselage_contract.DEFAULT_FAMILY
            and candidate.identifier.endswith("-000")
        ),
        candidates[0],
    )
    selected_model = fuselage_geometry.build_model(selected.design)
    selected_mesh = fuselage_geometry.build_mesh(
        selected_model,
        longitudinal,
        circumferential,
    )
    obj = fuselage_geometry.mesh_obj(selected_mesh, selected.report)
    manifest: dict[str, object] = {
        "schema": fuselage_contract.SCHEMA_VERSION,
        "generator": "calculations/fuselage_trade.py",
        "authority": fuselage_contract.AUTHORITY,
        "warning": fuselage_contract.WARNING,
        "variant_scope": variant.upper(),
        "seed": seed,
        "samples_per_family_excluding_baseline": samples,
        "resolution": {
            "longitudinal": longitudinal,
            "circumferential": circumferential,
        },
        "selection": {
            "candidate": selected.identifier,
            "basis": (
                "I-28 starting family for review only; not an optimization winner "
                "and not manufacturing authority"
            ),
            "mesh_file": MESH_NAME,
            "mesh_sha256": hashlib.sha256(obj.encode("ascii")).hexdigest(),
        },
        "candidates": [
            candidate_summary(candidate, candidate.identifier in pareto_ids)
            for candidate in candidates
        ],
        "selected_report": selected.report,
    }
    return manifest, obj


def manifest_text(manifest: dict[str, object]) -> str:
    return json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def _write_or_check(path: Path, expected: str, check: bool) -> None:
    if check:
        if not path.exists():
            raise SystemExit(f"missing generated artifact: {path.relative_to(ROOT)}")
        if path.read_text(encoding="ascii") != expected:
            raise SystemExit(
                f"stale generated artifact: {path.relative_to(ROOT)}; "
                "run python calculations/fuselage_trade.py"
            )
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="ascii", newline="\n")


def validation_checks() -> dict[str, bool]:
    lhs_a = latin_hypercube(12, 5, 2801)
    lhs_b = latin_hypercube(12, 5, 2801)
    known = np.asarray(((1.0, 2.0), (2.0, 1.0), (2.0, 2.0), (0.5, 3.0)))
    manifest, obj = build_trade(longitudinal=41, circumferential=48)
    encoded = manifest_text(manifest)
    baseline_families = {candidate["family"] for candidate in manifest["candidates"]}
    return {
        "Latin hypercube is seeded and deterministic": np.array_equal(lhs_a, lhs_b),
        "Latin hypercube occupies [0, 1]": (
            float(lhs_a.min()) >= 0.0 and float(lhs_a.max()) <= 1.0
        ),
        "Pareto filter rejects a known dominated point": nondominated_indices(known) == (0, 1, 3),
        "baseline trade evaluates all three families": baseline_families == {
            family.identifier for family in fuselage_contract.FAMILIES
        },
        "trade retains the integrated spindle as provisional review selection": (
            manifest["selection"]["candidate"] == "integrated_spindle-000"
        ),
        "selected review operand passes geometric gates": bool(
            manifest["selected_report"]["geometry_feasible"]
        ),
        "manifest and OBJ are ASCII safe": encoded.isascii() and obj.isascii(),
        "selected OBJ hash closes to its manifest": hashlib.sha256(
            obj.encode("ascii")
        ).hexdigest() == manifest["selection"]["mesh_sha256"],
        "open aircraft gates remain visible": not manifest["selected_report"]["aircraft_feasible"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--family",
        default="all",
        choices=("all", *(family.identifier for family in fuselage_contract.FAMILIES)),
    )
    parser.add_argument("--variant", default="all", choices=("all", "clean", "v1"))
    parser.add_argument("--seed", type=int, default=2801)
    parser.add_argument("--samples", type=int, default=0)
    parser.add_argument("--resolution", type=int, default=81)
    parser.add_argument("--circumferential", type=int, default=72)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true", help="print the complete manifest")
    args = parser.parse_args()
    if args.samples < 0 or args.samples > 200:
        parser.error("--samples must be in [0, 200]")

    manifest, obj = build_trade(
        family=args.family,
        samples=args.samples,
        seed=args.seed,
        longitudinal=args.resolution,
        circumferential=args.circumferential,
        variant=args.variant,
    )
    text = manifest_text(manifest)
    _write_or_check(args.output / MANIFEST_NAME, text, args.check)
    _write_or_check(args.output / MESH_NAME, obj, args.check)

    if args.json:
        print(text, end="")
    else:
        action = "VERIFIED" if args.check else "WROTE"
        print("=" * 78)
        print("SALAMANDRA PROVISIONAL FUSELAGE TRADE")
        print("=" * 78)
        print(f"  {action}: {(args.output / MANIFEST_NAME).relative_to(ROOT)}")
        print(f"  {action}: {(args.output / MESH_NAME).relative_to(ROOT)}")
        print(f"  candidates: {len(manifest['candidates'])}")
        print(f"  selected for review: {manifest['selection']['candidate']} [I]")
        print(f"  aircraft feasible: {manifest['selected_report']['aircraft_feasible']}")
        print(f"  {fuselage_contract.WARNING}")

    checks = validation_checks()
    for name, passed in checks.items():
        if not args.json:
            print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    if not args.json:
        print("\nVALIDATION: ALL PASS; OPEN DESIGN GATES REMAIN")


if __name__ == "__main__":
    main()
