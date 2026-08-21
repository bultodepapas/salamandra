#!/usr/bin/env python3
"""Validate the MP-02 Article #1 redesign disposition of every ADR.

An ADR's historical status and its authority over the redesigned aircraft are
different facts.  This module owns the second fact.  It guarantees that every
ADR file has exactly one redesign classification, names the gate that can
change it, carries a matching field in its own preamble, and appears in the
human-readable generated ledger.
"""
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADR_DIR = ROOT / "decisions"
LEDGER_PATH = ADR_DIR / "REDESIGN-DISPOSITION.md"
INDEX_PATH = ADR_DIR / "README.md"

BEGIN_MARKER = (
    "<!-- BEGIN GENERATED: ADR redesign disposition · "
    "calculations/decision_ledger.py · do not edit by hand -->"
)
END_MARKER = "<!-- END GENERATED: ADR redesign disposition -->"
COUNTS_BEGIN_MARKER = (
    "<!-- BEGIN GENERATED: ADR redesign counts · "
    "calculations/decision_ledger.py · do not edit by hand -->"
)
COUNTS_END_MARKER = "<!-- END GENERATED: ADR redesign counts -->"

ALLOWED_CLASSIFICATIONS = {
    "RETAINED",
    "RETAINED-METHOD",
    "CANDIDATE-ONLY",
    "REOPENED",
    "SUPERSEDED",
    "CANCELLED",
}


@dataclass(frozen=True)
class Disposition:
    adr: str
    classification: str
    gate: str
    authority: str


DISPOSITIONS = (
    Disposition("0001", "CANDIDATE-ONLY", "M3", "Forward sweep remains architecture candidate A; no v2 planform authority."),
    Disposition("0002", "REOPENED", "M6", "A closed printed load path is credible, but cell count and topology follow correlated loads and stiffness."),
    Disposition("0003", "CANDIDATE-ONLY", "M4", "Wash-in applies to the forward-swept r2a test candidate; twist is reselected with section and trim evidence."),
    Disposition("0004", "CANDIDATE-ONLY", "M3", "Aspect ratio 6 is a v0.6 comparison value, not a redesign constraint."),
    Disposition("0006", "REOPENED", "M3/M4", "One motor is retained; the pusher is the working baseline pending architecture and propulsion closure."),
    Disposition("0007", "RETAINED-METHOD", "M4", "Match propellers from measured maps by advance ratio; the 0.8–1.0 P/D band and hardware are not frozen."),
    Disposition("0008", "RETAINED-METHOD", "M4", "Do not credit an unmeasured 7x12 efficiency claim; measured data may readmit the propeller."),
    Disposition("0009", "RETAINED-METHOD", "All", "Keep viscous and induced drag separate in every candidate and mission state."),
    Disposition("0010", "SUPERSEDED", "M0", "ADR-0048 replaces the single fast-cruise branch with the E0–E3 total-energy mission."),
    Disposition("0012", "REOPENED", "M6", "Light colour remains the PETG default, but mandatory scope follows measured thermal/process evidence."),
    Disposition("0015", "RETAINED-METHOD", "M6", "Credit carbon only through an explicit load path and measured stiffness; its exact v0.6 role is not fixed."),
    Disposition("0016", "CANDIDATE-ONLY", "M6", "The reviewed PLA+ data remain material evidence; Article #1 is governed by the PETG-primary requirement."),
    Disposition("0018", "CANDIDATE-ONLY", "M6", "The reviewed ABS UV evidence remains material evidence; Article #1 is governed by the PETG-primary requirement."),
    Disposition("0021", "RETAINED", "M0/M6", "PETG remains the primary printed-airframe material; any local exception needs its own evidence and decision."),
    Disposition("0022", "CANCELLED", "—", "Wet carbon-veil lamination remains outside Article #1 scope."),
    Disposition("0023", "REOPENED", "M6", "Adhesive, tenon and bond-area rules require production-process coupons and complete joint loads."),
    Disposition("0024", "CANDIDATE-ONLY", "M6/M8", "The exact three-segment cuts and print orientation belong only to the v0.6 geometry; 256 mm fit remains binding."),
    Disposition("0025", "RETAINED-METHOD", "M5/M6/M8", "Control-surface inertia, balance and freeplay are mandatory aeroelastic gates; the final balance target is model/test derived."),
    Disposition("0026", "CANDIDATE-ONLY", "M1/M5", "Two DS-939MG servos and their stations are v0.6 packaging data; actuator count and selection are reopened."),
    Disposition("0027", "CANDIDATE-ONLY", "M3/M4/M6", "The 13.5/9 percent thickness schedule remains candidate A evidence and must compete with other architectures."),
    Disposition("0028", "CANDIDATE-ONLY", "M6", "Five-percent gyroid is a v0.6 process candidate pending shell buckling and stiffness tests."),
    Disposition("0030", "REOPENED", "M6", "The torsion architecture is selected only after process allowables and representative-section correlation."),
    Disposition("0031", "CANDIDATE-ONLY", "M6", "The exact carbon tube/pin couple is a v0.6 modular-joint candidate, not a v2 interface release."),
    Disposition("0032", "REOPENED", "M2/M3/M6", "Configuration-controlled modularity is retained; exact CORE/PANEL geometry and the range/sport catalogue are not."),
    Disposition("0033", "SUPERSEDED", "M0", "ADR-0048 requires a bound reference electrical and propulsion configuration for Article #1."),
    Disposition("0034", "RETAINED-METHOD", "M4/M5", "Keep thrust-line angle parametric and close power-on pitching moment; 0.8 degrees is precedent only."),
    Disposition("0035", "REOPENED", "M6", "TPU versus film hinge technology requires measured stiffness, hysteresis, fatigue and aeroelastic evidence."),
    Disposition("0036", "RETAINED", "All", "The open community platform and human-CAD collaboration model remain programme policy."),
    Disposition("0037", "RETAINED", "All", "The repository licence decision remains programme policy."),
    Disposition("0038", "SUPERSEDED", "M0/M5", "ADR-0048 replaces the no-rudder first-flight concept; V1a survives only as comparison evidence."),
    Disposition("0039", "CANDIDATE-ONLY", "M6", "Filament dowels are a v0.6 glued-joint detail pending the selected structure and joint tests."),
    Disposition("0040", "CANDIDATE-ONLY", "M3", "Minus-15-degree quarter-chord sweep is candidate A, not the redesigned planform."),
    Disposition("0041", "CANDIDATE-ONLY", "M4", "r1 is immutable reference/coupon geometry and has no flight-wing CAD authority."),
    Disposition("0042", "RETAINED-METHOD", "M4", "Close propulsion by total battery power and measured drag; APC 8x8, 95 km/h and Kv values are v0.6 data."),
    Disposition("0043", "CANDIDATE-ONLY", "M2/M3", "The v0.6 mass allocation and 45 km/h closure are comparison evidence; v2 rebuilds the ledger."),
    Disposition("0044", "RETAINED-METHOD", "M6", "Keep limit, ultimate and gust meanings separate; +6/-3 and 1.5 remain provisional screens."),
    Disposition("0045", "CANDIDATE-ONLY", "M4/M5", "The 35–90 percent, 28-percent-chord elevon is the E2A starting geometry only."),
    Disposition("0046", "RETAINED", "All", "Single declaration, contract lint and mutation proof remain mandatory calculation architecture."),
    Disposition("0047", "CANDIDATE-ONLY", "M4", "r2a-sm5 is the sole next coupon candidate, not a selected redesign airfoil or CG."),
    Disposition("0048", "RETAINED", "M0–M9", "This is the governing Article #1 mission, configuration and product contract."),
)


def _adr_files() -> dict[str, Path]:
    found = {}
    for path in sorted(ADR_DIR.glob("ADR-[0-9][0-9][0-9][0-9]-*.md")):
        identifier = path.name[4:8]
        if identifier in found:
            raise ValueError(f"duplicate ADR identifier {identifier}")
        found[identifier] = path
    return found


def _title(path: Path) -> str:
    first = path.read_text(encoding="utf-8").splitlines()[0]
    prefix = f"# ADR-{path.name[4:8]} — "
    if not first.startswith(prefix):
        raise ValueError(f"unexpected title format in {path.relative_to(ROOT)}")
    return first.removeprefix(prefix)


def redesign_field(item: Disposition) -> str:
    return (
        f"**Article #1 redesign:** `{item.classification}` · "
        f"**Gate:** `{item.gate}` · "
        "[MP-02 ledger](REDESIGN-DISPOSITION.md)"
    )


def render_table() -> str:
    files = _adr_files()
    lines = [
        "| ADR | Historical decision | Article #1 disposition | Owning gate | v2 authority |",
        "|---|---|---|---|---|",
    ]
    for item in DISPOSITIONS:
        path = files[item.adr]
        lines.append(
            f"| [{item.adr}]({path.name}) | {_title(path)} | "
            f"**{item.classification}** | `{item.gate}` | {item.authority} |"
        )
    return "\n".join(lines)


def generated_block() -> str:
    return f"{BEGIN_MARKER}\n\n{render_table()}\n\n{END_MARKER}"


def render_counts_table() -> str:
    counts = classification_counts()
    return "\n".join((
        "| Retained | Retained method | Candidate only | Reopened | Superseded | Cancelled |",
        "|---:|---:|---:|---:|---:|---:|",
        (
            f"| {counts['RETAINED']} | {counts['RETAINED-METHOD']} | "
            f"{counts['CANDIDATE-ONLY']} | {counts['REOPENED']} | "
            f"{counts['SUPERSEDED']} | {counts['CANCELLED']} |"
        ),
    ))


def generated_counts_block() -> str:
    return (
        f"{COUNTS_BEGIN_MARKER}\n\n{render_counts_table()}\n\n"
        f"{COUNTS_END_MARKER}"
    )


def validation_checks() -> dict[str, bool]:
    files = _adr_files()
    identifiers = tuple(item.adr for item in DISPOSITIONS)
    classifications = tuple(item.classification for item in DISPOSITIONS)
    ledger_text = LEDGER_PATH.read_text(encoding="utf-8")
    index_text = INDEX_PATH.read_text(encoding="utf-8")
    field_matches = []
    for item in DISPOSITIONS:
        preamble = files[item.adr].read_text(encoding="utf-8").split("\n## ", 1)[0]
        field_matches.append(preamble.count(redesign_field(item)) == 1)
    superseded_headers = all(
        "Superseded" in files[item.adr].read_text(encoding="utf-8").split("\n## ", 1)[0]
        for item in DISPOSITIONS
        if item.classification == "SUPERSEDED"
    )
    cancelled_headers = all(
        "CANCELLED" in files[item.adr].read_text(encoding="utf-8").split("\n## ", 1)[0]
        for item in DISPOSITIONS
        if item.classification == "CANCELLED"
    )
    return {
        "every ADR file has exactly one ledger entry": (
            set(identifiers) == set(files)
            and len(identifiers) == len(set(identifiers))
        ),
        "every classification is controlled": (
            set(classifications) <= ALLOWED_CLASSIFICATIONS
        ),
        "every ADR preamble carries its exact redesign field": all(field_matches),
        "superseded ADR headers are explicit": superseded_headers,
        "cancelled ADR headers are explicit": cancelled_headers,
        "human-readable ledger table is current": generated_block() in ledger_text,
        "decision index counts are current": generated_counts_block() in index_text,
    }


def classification_counts() -> dict[str, int]:
    return {
        classification: sum(
            item.classification == classification for item in DISPOSITIONS
        )
        for classification in sorted(ALLOWED_CLASSIFICATIONS)
    }


def main() -> None:
    print("SALAMANDRA MP-02 — ARTICLE #1 ADR DISPOSITION")
    print(f"\nADR files classified: {len(DISPOSITIONS)}")
    for classification, count in classification_counts().items():
        print(f"  {classification:16s} {count:2d}")
    print("\nValidation")
    checks = validation_checks()
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print(f"\nMP-02 LEDGER: {'PASS' if all(checks.values()) else 'FAIL'}")
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
