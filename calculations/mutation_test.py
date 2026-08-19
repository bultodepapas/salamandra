#!/usr/bin/env python3
"""Mutation test: prove the verification suite can actually fail.

`CLAUDE.md`, failure mode #8: *"Before proposing a test, ask what result would
make it fail. If there is none, it measures nothing."* This file applies that
rule to the verification suite itself.

Several checks in this repository could not fail. `balance_cg` compared two
hardcoded neutral-point literals to each other; `"SM is 8 percent MAC"` reduced
algebraically to `abs(STATIC_MARGIN - 0.08)`; `servo_torque` asserted that a
value multiplied by 1.0 and divided by 1 equalled itself. All three reported
PASS on every run and verified nothing.

The defence against that is not review, it is measurement. Each entry below
seeds ONE deliberate defect — a sign flip, a dropped normalisation, a doubled
constant, a desynchronised copy — and the suite must turn at least one check
red. A mutation that survives is a hole in the verification, and it is reported
as a FAILURE of this file.

Every mutation is applied to an in-memory module attribute and reverted
afterwards; nothing on disk is modified.

    python3 mutation_test.py            # run every mutation
    python3 mutation_test.py --list     # show what is seeded, run nothing
"""
import argparse
import importlib
import sys
from dataclasses import dataclass, field
from typing import Callable

import design_config


@dataclass(frozen=True)
class Mutation:
    """One seeded defect and the modules whose caches it invalidates."""

    name: str
    rationale: str
    apply: Callable[[], Callable[[], None]]
    invalidates: tuple = field(default=())


def _set_attr(module_name, attribute, value):
    """Return an apply() that sets an attribute and yields its undo."""

    def apply():
        module = importlib.import_module(module_name)
        original = getattr(module, attribute)
        setattr(module, attribute, value)

        def undo():
            setattr(module, attribute, original)

        return undo

    return apply


def _scale_attr(module_name, attribute, factor):
    def apply():
        module = importlib.import_module(module_name)
        original = getattr(module, attribute)
        setattr(module, attribute, original * factor)

        def undo():
            setattr(module, attribute, original)

        return undo

    return apply


def _patch_function(module_name, attribute, replacement_factory):
    def apply():
        module = importlib.import_module(module_name)
        original = getattr(module, attribute)
        setattr(module, attribute, replacement_factory(original))

        def undo():
            setattr(module, attribute, original)

        return undo

    return apply


MUTATIONS = (
    Mutation(
        "planform: quarter-chord sweep loses its forward sign",
        "The forward sweep is the whole point of the aircraft; a sign flip "
        "must never survive.",
        _patch_function("design_config", "SWEEP_C4_DEG", lambda old: -old),
    ),
    Mutation(
        "planform: span desynchronised from the released value",
        "C6 was a chord carried over from an old table after the aspect "
        "ratio changed. The geometry invariants must catch the same class.",
        _scale_attr("design_config", "B", 1.05),
    ),
    Mutation(
        "mass: CLEAN contract drifts from the mass budget",
        "The mass contract and the mass budget are two representations of "
        "one number; they must not be allowed to disagree.",
        _scale_attr("design_config", "ARTICLE_CLEAN_MASS_KG", 1.02),
    ),
    Mutation(
        "aero: static margin silently changed",
        "The old check hardcoded 0.08 instead of reading STATIC_MARGIN, so "
        "it would have failed for the WRONG reason. It must now track it.",
        _set_attr("design_config", "STATIC_MARGIN", 0.12),
    ),
    Mutation(
        "aero: neutral point desynchronised from its published anchor",
        "This is the defect the whole aero_contract module exists to catch: "
        "a hand-copied NP that no longer matches the solver.",
        _scale_attr("aero_contract", "NP_VLM_PUBLISHED", 1.10),
    ),
    Mutation(
        "aero: VLM drops the MAC normalisation (correction C17)",
        "C17 exactly. The lift-slope-versus-Helmbold check could not see it; "
        "the moment-about-NP identity must.",
        _patch_function(
            "vlm_ala_volante", "solve",
            lambda old: lambda g, alpha_deg, U=1.0: (
                lambda r: (r[0], r[1] * g["cbar"], r[2], r[3])
            )(old(g, alpha_deg, U)),
        ),
    ),
    Mutation(
        "speeds: the ladder is inverted",
        "Nothing enforced the ordering of the speed roles before; an edit "
        "could silently place V_NE below the operational cap.",
        _set_attr("design_config", "ARTICLE_V_NE_KMH", 90.0),
    ),
    Mutation(
        "speeds: structural sizing case falls below V_NE",
        "The servo and fin are sized at the structural case; it must stay "
        "above the article V_NE.",
        _set_attr("design_config", "STRUCTURAL_DESIGN_SPEED_KMH", 150.0),
    ),
    Mutation(
        "loads: the ultimate safety factor is dropped",
        "Limit and ultimate loads must never be conflated (I-24/C33).",
        _set_attr("design_config", "ULTIMATE_SAFETY_FACTOR", 1.0),
    ),
    Mutation(
        "loads: the negative limit load factor loses its sign",
        "A sign error on the negative limit would invert the whole lower "
        "branch of the V-n envelope.",
        _patch_function("design_config", "NEGATIVE_LIMIT_LOAD_FACTOR",
                        lambda old: -old),
    ),
    Mutation(
        "controls: elevon hinge station moves without the torsion box",
        "The torsion box ends AT the hinge; divergence silently kept 0.72 "
        "when this was duplicated.",
        _set_attr("design_config", "ELEVON_HINGE_XC", 0.65),
    ),
    Mutation(
        "controls: elevon span fractions desynchronised across modules",
        "The elevon geometry is consumed by servo_torque, elevon_sizing and "
        "equipment_layout; they must not be allowed to disagree.",
        _set_attr("servo_torque", "ETA_IN", 0.30),
    ),
    Mutation(
        "controls: the servo torque safety factor is dropped",
        "A missing factor makes the margin look better, which is exactly the "
        "direction a check must still catch.",
        _set_attr("servo_torque", "TORQUE_SAFETY_FACTOR", 1.0),
    ),
    Mutation(
        "drag: the induced term is folded into a single Oswald factor",
        "ADR-0009 forbids exactly this; it already caused correction C1.",
        _patch_function(
            "drag_model", "induced_cd",
            lambda old: lambda cl, aspect_ratio=None, span_efficiency=None: 0.0,
        ),
    ),
    Mutation(
        "yaw: inertia reverts to the retired standalone estimate",
        "Two values for one physical quantity, differing by a factor 1.76, "
        "is the defect this cross-check exists to prevent.",
        _patch_function("yaw_stability", "yaw_inertia",
                        lambda old: lambda: 0.28),
    ),
    Mutation(
        "power: the BEC efficiency stops being physical",
        "An efficiency above unity would silently create power.",
        _set_attr("design_config", "REFERENCE_BEC_EFFICIENCY", 1.20),
    ),
    Mutation(
        "power: the O1 energy limit drifts from the power identity",
        "The motor and hotel allocations must close exactly to O1.",
        _scale_attr("design_config", "O1_ENERGY_LIMIT_WH_PER_KM", 1.10),
    ),
    Mutation(
        "aero: CLmax raised beyond the released I-07 value",
        "C16: the stall requirement was not re-derived when mass rose. The "
        "stall chain must react to CLmax too.",
        _scale_attr("design_config", "CL_MAX_WING", 1.30),
    ),
    Mutation(
        "geometry: taper ratio desynchronised",
        "Taper sets the chord law, the MAC and the neutral point at once.",
        _set_attr("design_config", "TAPER", 0.65),
    ),
    Mutation(
        "fuselage: containment query always reports clearance",
        "A smooth render must not survive when the OML audit is made blind to "
        "a seeded equipment penetration.",
        _patch_function(
            "fuselage_geometry",
            "point_margin_mm",
            lambda old: lambda model, point_mm: 1.0,
        ),
    ),
    Mutation(
        "fuselage: distribution audit is forced to approve every body",
        "A cylindrical plateau must fail even when its mesh is smooth and watertight.",
        _patch_function(
            "fuselage_geometry",
            "distribution_diagnostics",
            lambda old: lambda model, stations=801: {
                **old(model, stations),
                "maximum_area_in_root_band": True,
                "no_payload_to_root_neck": True,
                "no_long_parallel_sides": True,
            },
        ),
    ),
)


def _clear_caches():
    """Drop every cached derivation so a mutation is actually observed."""
    for module_name in (
        "aero_contract", "balance_cg", "equipment_layout", "yaw_stability",
        "divergence", "vlm_ala_volante", "fpv_power_budget",
        "propulsion_match", "boom_flexion", "airfoil_reflex_trade",
        "fuselage_geometry", "verify_calculations",
    ):
        module = sys.modules.get(module_name)
        if module is None:
            continue
        for name in dir(module):
            attribute = getattr(module, name, None)
            if hasattr(attribute, "cache_clear"):
                try:
                    attribute.cache_clear()
                except TypeError:      # pragma: no cover - defensive
                    pass
    vlm = sys.modules.get("vlm_ala_volante")
    if vlm is not None and hasattr(vlm, "_GEOM_CACHE"):
        vlm._GEOM_CACHE.clear()


def run_mutation(mutation, verify):
    """Apply one mutation, run the contracts, and report what turned red."""
    undo = mutation.apply()
    _clear_caches()
    try:
        checks = verify.contract_checks()
        failures = [check for check in checks if not check.passed]
    except Exception as error:            # noqa: BLE001
        # An uncaught exception still means the mutation was DETECTED, but the
        # harness should have reported it as a check; say so explicitly.
        failures = [f"uncaught {type(error).__name__}: {error}"]
    finally:
        undo()
        _clear_caches()
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true",
                        help="print the seeded defects and exit")
    args = parser.parse_args()

    print("=" * 78)
    print("SALAMANDRA MUTATION TEST - can the verification suite fail?")
    print("=" * 78)

    if args.list:
        for mutation in MUTATIONS:
            print(f"\n  {mutation.name}")
            print(f"      {mutation.rationale}")
        print(f"\n{len(MUTATIONS)} seeded defects.")
        return

    import verify_calculations

    baseline = verify_calculations.contract_checks()
    baseline_failures = [c for c in baseline if not c.passed]
    print(f"\nBaseline: {len(baseline)} contract checks, "
          f"{len(baseline_failures)} failing.")
    if baseline_failures:
        print("  The unmutated suite is not clean; fix that before trusting "
              "any result below:")
        for check in baseline_failures:
            print(f"    [FAIL] {check.name}")

    survivors = []
    print("\nSeeded defects and the checks that caught them")
    print("-" * 78)
    for mutation in MUTATIONS:
        failures = run_mutation(mutation, verify_calculations)
        caught = len(failures) > len(baseline_failures)
        status = "CAUGHT " if caught else "SURVIVED"
        print(f"[{status}] {mutation.name}")
        if caught:
            named = [f.name if hasattr(f, "name") else str(f)
                     for f in failures
                     if not hasattr(f, "name")
                     or f.name not in {c.name for c in baseline_failures}]
            for label in named[:3]:
                print(f"           -> {label}")
            if len(named) > 3:
                print(f"           -> ... and {len(named) - 3} more")
        else:
            survivors.append(mutation)

    print("-" * 78)
    print(f"{len(MUTATIONS) - len(survivors)}/{len(MUTATIONS)} seeded defects "
          "were caught by the contract suite.")
    if survivors:
        print("\nSURVIVING MUTATIONS - these are holes in the verification:")
        for mutation in survivors:
            print(f"  - {mutation.name}")
            print(f"      {mutation.rationale}")
        raise SystemExit(1)
    print("\nMUTATION TEST: ALL SEEDED DEFECTS CAUGHT")


if __name__ == "__main__":
    main()
