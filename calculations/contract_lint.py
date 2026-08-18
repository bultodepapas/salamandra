#!/usr/bin/env python3
"""Static enforcement of the single-declaration rule.

THE RULE. A module may **compute** a physical quantity, or **import** it. It may
never **declare** one that another module also declares. Any number appearing in
two modules is either promoted to `design_config` / `aero_contract` /
`drag_model`, or one of the two is deleted.

That rule is what stops the project's most repeated correction (failure mode #3,
"failing to re-derive downstream") from recurring. It was previously enforced by
review alone, and review missed: the design wash-in was declared in four modules
plus a bare literal, the elevon hinge station in four places, PETG density in
two, the root thickness ratio in two, and the neutral point was a hand-copied
literal that no live check compared against its solver.

This file is the mechanical version of that rule. It parses every module and
reports:

  1. a contract constant re-declared with a LITERAL outside its owning module;
  2. a bare numeric literal equal to a contract value, outside its owner;
  3. two modules exporting the same module-level name with different values;
  4. a contract constant bound as a DEFAULT ARGUMENT of a function whose value
     carries a declared uncertainty band — a default is evaluated once at
     definition time, so reassigning the constant for a sensitivity study has
     no effect at all.

It is a lint, not a proof: `mutation_test.py` is what proves the contract suite
can fail. The two are complementary — this one catches desynchronisation before
it can produce a wrong number, that one catches it after.

    python3 contract_lint.py            # report and exit non-zero on findings
    python3 contract_lint.py --list     # show the watched contract values
"""
import argparse
import ast
from pathlib import Path

import design_config

HERE = Path(__file__).resolve().parent

# Quantities owned by a single module.  A literal equal to one of these,
# appearing anywhere else, is a desynchronisation waiting to happen.
WATCHED = {
    "B": ("design_config", design_config.B),
    "S": ("design_config", design_config.S),
    "TAPER": ("design_config", design_config.TAPER),
    "SWEEP_C4_DEG": ("design_config", design_config.SWEEP_C4_DEG),
    "ROOT_TC": ("design_config", design_config.ROOT_TC),
    "TIP_TC": ("design_config", design_config.TIP_TC),
    "G0": ("design_config", design_config.G0),
    "RHO_SL": ("design_config", design_config.RHO_SL),
    "NU_SL": ("design_config", design_config.NU_SL),
    "PETG_DENSITY_KG_M3": ("design_config", design_config.PETG_DENSITY_KG_M3),
    "CL_MAX_WING": ("design_config", design_config.CL_MAX_WING),
    "STATIC_MARGIN": ("design_config", design_config.STATIC_MARGIN),
    "DESIGN_TWIST_DEG": ("design_config", design_config.DESIGN_TWIST_DEG),
    "ELEVON_HINGE_XC": ("design_config", design_config.ELEVON_HINGE_XC),
    "ELEVON_ETA_IN": ("design_config", design_config.ELEVON_ETA_IN),
    "ELEVON_ETA_OUT": ("design_config", design_config.ELEVON_ETA_OUT),
    "ARTICLE_V_NE_KMH": ("design_config", design_config.ARTICLE_V_NE_KMH),
    "STRUCTURAL_DESIGN_SPEED_KMH":
        ("design_config", design_config.STRUCTURAL_DESIGN_SPEED_KMH),
    "CRUISE_SPEED_KMH": ("design_config", design_config.CRUISE_SPEED_KMH),
    "STALL_SPEED_LIMIT_KMH":
        ("design_config", design_config.STALL_SPEED_LIMIT_KMH),
    "POSITIVE_LIMIT_LOAD_FACTOR":
        ("design_config", design_config.POSITIVE_LIMIT_LOAD_FACTOR),
    "ULTIMATE_SAFETY_FACTOR":
        ("design_config", design_config.ULTIMATE_SAFETY_FACTOR),
    "ARTICLE_CLEAN_MASS_KG":
        ("design_config", design_config.ARTICLE_CLEAN_MASS_KG),
}

# The numeric-literal scan is deliberately restricted to DISTINCTIVE values.
# Matching on magnitude alone is not discriminating: 15 is a sweep angle AND a
# percentage AND a gram count, 45 is a stall speed AND a degree, 0.09 is a tip
# thickness AND a drawing coordinate, 180 is a speed AND half a turn.  A lint
# that cries wolf gets switched off, so only values specific enough to identify
# the quantity on sight are policed here; everything else relies on the
# named-redeclaration and conflicting-export scans, which cannot false-positive.
DISTINCTIVE = {
    "PETG_DENSITY_KG_M3", "CL_MAX_WING", "ARTICLE_CLEAN_MASS_KG",
    "ROOT_TC", "ELEVON_HINGE_XC", "B", "S",
}

# Files that are allowed to carry contract literals: the owners themselves, and
# the ones whose entire purpose is to compare against a published value.
EXEMPT_FILES = {
    "design_config.py",
    # The drawing generator is a page of layout coordinates in millimetres;
    # matching them against physical values by magnitude is pure noise.
    "generate_blueprints.py",
    "contract_lint.py",
    "mutation_test.py",
    "verify_calculations.py",
}

# Constants that carry a declared uncertainty band and must therefore never be
# frozen into a default argument: they exist to be swept.
BANDED = {
    "IZ", "IZ_BAND", "E_BAND", "G_BAND", "K_SWEEP", "A_SLOPE", "AREA_BAND",
    "CH_RANGE", "CD_LAUNCH", "X_EA_BAND", "S_FS_BAND", "K_FUS_BAND",
    "CNB_W_BAND", "CLA_RE_FAC", "TAU_BAND", "V_HAND", "T_W", "IDLE_FRAC",
    "T_GESTURE", "LAUNCH_SEPARATION_ALLOWANCE", "GAMMA_LAUNCH_BAND_DEG",
}


def _modules():
    for path in sorted(HERE.glob("*.py")):
        yield path, ast.parse(path.read_text(encoding="utf-8"))


def _module_constants(tree):
    """Module-level UPPER_CASE assignments bound to a plain numeric literal."""
    found = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        value = node.value
        literal = None
        if isinstance(value, ast.Constant) and isinstance(
                value.value, (int, float)) and not isinstance(
                value.value, bool):
            literal = float(value.value)
        elif (isinstance(value, ast.UnaryOp)
              and isinstance(value.op, ast.USub)
              and isinstance(value.operand, ast.Constant)
              and isinstance(value.operand.value, (int, float))):
            literal = -float(value.operand.value)
        if literal is None:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                found[target.id] = (literal, node.lineno)
    return found


def _imported_names(tree):
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def find_redeclarations():
    """A watched contract name re-bound to a literal outside its owner."""
    findings = []
    for path, tree in _modules():
        if path.name in EXEMPT_FILES:
            continue
        for name, (literal, line) in _module_constants(tree).items():
            owner = WATCHED.get(name)
            if owner and owner[0] != path.stem:
                findings.append(
                    f"{path.name}:{line} re-declares the contract constant "
                    f"{name} as a literal ({literal:g}); import it from "
                    f"{owner[0]} instead")
    return findings


def find_contract_literals():
    """A bare numeric literal equal to a watched contract value."""
    findings = []
    by_value = {}
    for name, (owner, value) in WATCHED.items():
        if name not in DISTINCTIVE or value == 0.0:
            continue
        by_value.setdefault(round(abs(float(value)), 10), (name, owner))
    for path, tree in _modules():
        if path.name in EXEMPT_FILES:
            continue
        imported = _imported_names(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            if isinstance(node.value, bool) or not isinstance(
                    node.value, (int, float)):
                continue
            match = by_value.get(round(abs(float(node.value)), 10))
            if match is None:
                continue
            name, owner = match
            if name in imported or path.stem == owner:
                continue
            findings.append(
                f"{path.name}:{node.lineno} uses the bare literal "
                f"{node.value:g}, which is {owner}.{name}; import the name")
    return findings


def find_conflicting_exports():
    """Two modules exporting the same UPPER_CASE name with different values."""
    seen = {}
    findings = []
    for path, tree in _modules():
        if path.name in EXEMPT_FILES:
            continue
        for name, (literal, line) in _module_constants(tree).items():
            if name in seen:
                other_module, other_value, other_line = seen[name]
                if abs(other_value - literal) > 1e-12:
                    findings.append(
                        f"{path.name}:{line} and {other_module}:{other_line} "
                        f"both export {name}, with different values "
                        f"({literal:g} vs {other_value:g})")
            else:
                seen[name] = (path.name, literal, line)
    return findings


def find_frozen_banded_defaults():
    """A banded constant bound as a default argument, which freezes it."""
    findings = []
    for path, tree in _modules():
        if path.name in EXEMPT_FILES:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            defaults = list(node.args.defaults) + [
                d for d in node.args.kw_defaults if d is not None]
            for default in defaults:
                if isinstance(default, ast.Name) and default.id in BANDED:
                    findings.append(
                        f"{path.name}:{node.lineno} {node.name}() binds the "
                        f"banded constant {default.id} as a default argument; "
                        "a default is evaluated once at definition time, so "
                        "reassigning it cannot sweep the band. Use a None "
                        "sentinel resolved in the body")
    return findings


CHECKS = (
    ("contract constants re-declared outside their owner", find_redeclarations),
    ("bare literals duplicating a contract value", find_contract_literals),
    ("conflicting exports of the same name", find_conflicting_exports),
    ("banded constants frozen as default arguments",
     find_frozen_banded_defaults),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true",
                        help="print the watched contract values and exit")
    args = parser.parse_args()

    print("=" * 78)
    print("SALAMANDRA CONTRACT LINT - one declaration per physical quantity")
    print("=" * 78)

    if args.list:
        for name, (owner, value) in sorted(WATCHED.items()):
            print(f"  {owner}.{name} = {value:g}")
        print(f"\n{len(WATCHED)} watched contract values.")
        return

    total = 0
    for title, check in CHECKS:
        findings = check()
        total += len(findings)
        status = "PASS" if not findings else "FAIL"
        print(f"\n[{status}] {title}")
        for finding in findings:
            print(f"    - {finding}")

    print("\n" + "-" * 78)
    if total:
        print(f"CONTRACT LINT: {total} finding(s)")
        raise SystemExit(1)
    print("CONTRACT LINT: ALL PASS - no physical quantity is declared twice")


if __name__ == "__main__":
    main()
