#!/usr/bin/env python3
"""Publish the generated SVG drawing set into the repository documentation.

``generate_blueprints.py`` owns the *geometry*: it renders every controlled A3
sheet from the numerical modules.  This module owns the *publication contract*:
which sheets exist, how each one is described, and where that description is
mirrored so that no human has to re-type it.

Single source of truth::

    SHEETS  ->  geometry/drawings/manifest.json  ->  README.md (hero + index)
                                                 ->  geometry/drawings/README.md
                                                 ->  wiki (gen-site.mjs reads the manifest)

The manifest is deterministic (no timestamps): it records the drawing number,
file name, the accessible title/description read back from the rendered SVG, the
editorial purpose/scale/authority, the byte size and the SHA-256 of each sheet.
A changed drawing therefore changes the manifest, and a changed manifest changes
every published surface on the next run.

Run from any directory::

    python3 calculations/drawing_index.py            # write manifest + doc blocks
    python3 calculations/drawing_index.py --check     # read-only staleness gate

``generate_blueprints.py`` calls into this module after rendering, so the normal
workflow stays a single command.  This module imports nothing outside the
standard library, so the documentation gate can run without the numerical stack.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAWINGS_DIR = ROOT / "geometry" / "drawings"
MANIFEST_PATH = DRAWINGS_DIR / "manifest.json"
REPO_README = ROOT / "README.md"
DRAWINGS_README = DRAWINGS_DIR / "README.md"

MANIFEST_SCHEMA = 1
GENERATOR = "calculations/generate_blueprints.py"
INDEXER = "calculations/drawing_index.py"
SHEET_SIZE = "A3 · 420 × 297 mm · 1 SVG user unit = 1 mm"

# Published blocks are named: `drawing-hero` is the single lead sheet that opens
# the repository README, `drawing-index` is the gallery and index table.
HERO_BLOCK = "drawing-hero"
INDEX_BLOCK = "drawing-index"


def block_begin(block: str) -> str:
    return (
        f"<!-- BEGIN GENERATED: {block} · calculations/drawing_index.py · "
        "do not edit by hand -->"
    )


def block_end(block: str) -> str:
    return f"<!-- END GENERATED: {block} -->"


def block_re(block: str) -> re.Pattern[str]:
    return re.compile(
        re.escape(block_begin(block)) + r".*?" + re.escape(block_end(block)), re.DOTALL
    )


@dataclass(frozen=True)
class SheetSpec:
    """Editorial contract for one rendered sheet.

    ``purpose``, ``scale`` and ``authority`` populate the index table; ``note``
    is the reviewer-facing paragraph published under the embedded drawing.  The
    accessible ``title``/``desc`` are not repeated here: they are read back from
    the rendered SVG so the two can never disagree.
    """

    number: str
    filename: str
    heading: str
    purpose: str
    scale: str
    authority: str
    note: str


SHEETS: tuple[SheetSpec, ...] = (
    SheetSpec(
        number="SLM-GA-001",
        filename="SLM-GA-001-general-arrangement.svg",
        heading="General arrangement",
        purpose=(
            "Article #1 top-view arrangement: controlled planform, modular stations, "
            "CG/NP and continuous provisional fuselage/equipment envelopes"
        ),
        scale="A3 · 1:4",
        authority="Planform `[D]`; equipment `[D]`/`[E]`; OML `[I]`",
        note=(
            "Use this sheet to review the whole-aircraft relationship: 1,300 mm controlled "
            "planform, modular stations, quarter-chord sweep, CG/NP, nose-boom battery "
            "station and rear-pusher envelope. A continuous curved fuselage OML connects the "
            "battery fairing, CORE and rear pod so the aircraft reads as one body. Its "
            "required stations are sourced, but its Bézier transitions remain `[I]`, amber "
            "and provisional until OP-21/F2 freezes native CAD."
        ),
    ),
    SheetSpec(
        number="SLM-GA-002",
        filename="SLM-GA-002-side-elevations.svg",
        heading="Side elevations",
        purpose=(
            "Comparative side elevations: CLEAN finless baseline and V1a fixed-fin test "
            "variant, with common root section, packaging, motor/propeller and keel clearance"
        ),
        scale="A3 · 1:4",
        authority="Root/fin `[D]`/`[E]`; side OML/install `[I]`",
        note=(
            "Use this sheet to compare the two published directional configurations without "
            "changing the common wing, boom, battery or propulsion installation. "
            "**SALAMANDRA-CLEAN** is finless; **SALAMANDRA-V1a** adds a passive fixed "
            "centreline fin. Neither configuration has a movable rudder. The released root "
            "airfoil and calculated V1a fin dimensions are traceable, while the side OML, "
            "vertical equipment placement, propeller-clearance keel and fin/pod installation "
            "remain `[I]`. The drawing also flags the open 105 mm fin-root versus "
            "x = +295 mm pod-extension interface for native CAD resolution."
        ),
    ),
    SheetSpec(
        number="SLM-EQP-001",
        filename="SLM-EQP-001-equipment-mass-skeleton.svg",
        heading="Equipment mass skeleton",
        purpose=(
            "Top and side mass skeleton: component envelopes, true mass centres, x/y/z "
            "schedule, CLEAN CG and V1 battery-stop overlay. The top view includes the "
            "controlled exterior wing planform as spatial context but no wing construction, "
            "fuselage or OML."
        ),
        scale="A3 · top 1:6.5 / side 1:4",
        authority=(
            "Planform `[D]`; mass/position ledger `[D]`/`[E]`; open installations `[M]`; "
            "no OML authority"
        ),
        note=(
            "Use this sheet to review mass and packaging rather than shape: component "
            "envelopes, true mass centres, the x/y/z schedule, the CLEAN CG and the V1 "
            "battery-stop overlay. Envelope fill colour identifies system function while "
            "outline style continues to identify maturity. The controlled exterior wing "
            "planform appears only as spatial context: the sheet defines no fuselage outer "
            "mould line, no wing construction and no manufacturing geometry."
        ),
    ),
    SheetSpec(
        number="SLM-WNG-001",
        filename="SLM-WNG-001-half-wing-layout.svg",
        heading="Right half-wing layout",
        purpose=(
            "Right half-wing: printed segments, cells, spar/pin, ADR-0045 elevon/fixed-root "
            "bridge, exact y195 profile and polyhedral inset"
        ),
        scale="A3 · plan 1:2",
        authority="Planform/profile/elevon bounds `[D]`; structure/polyhedral `[E]`/`[I]`",
        note=(
            "Use this sheet to review PANEL segmentation and interfaces. It shows the exact "
            "y195 Salamandra r1 coordinate section, but the spar/channel, servo zones, D-box "
            "web and polyhedral construction retain their provisional status."
        ),
    ),
)


# ---------------------------------------------------------------------------
# manifest


def _extract(source: str, tag: str) -> str:
    match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", source, re.DOTALL)
    if match is None:
        raise SystemExit(f"drawing is missing its <{tag}> element")
    return re.sub(r"\s+", " ", match.group(1)).strip()


def build_manifest() -> dict:
    """Read the rendered sheets and return the deterministic manifest object."""
    sheets = []
    for spec in SHEETS:
        path = DRAWINGS_DIR / spec.filename
        if not path.exists():
            raise SystemExit(
                f"{spec.number}: {path.relative_to(ROOT)} is missing; "
                f"run python3 {GENERATOR} first"
            )
        raw = path.read_bytes()
        source = raw.decode("utf-8")
        sheets.append(
            {
                "number": spec.number,
                "file": spec.filename,
                "heading": spec.heading,
                "title": _extract(source, "title"),
                "description": _extract(source, "desc"),
                "purpose": spec.purpose,
                "scale": spec.scale,
                "authority": spec.authority,
                "note": spec.note,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    return {
        "schema": MANIFEST_SCHEMA,
        "generator": GENERATOR,
        "indexer": INDEXER,
        "sheet_size": SHEET_SIZE,
        "authority": "DRAFT — NOT FOR MANUFACTURE",
        "sheets": sheets,
    }


def manifest_json(manifest: dict) -> str:
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# markdown blocks


def render_table(manifest: dict, href: str) -> str:
    """Index table. ``href`` is the path prefix from the file being written."""
    rows = "\n".join(
        f"| [`{s['number']}`]({href}{s['file']}) | {s['purpose']} | {s['scale']} | "
        f"{s['authority']} |"
        for s in manifest["sheets"]
    )
    return (
        "| Drawing | Purpose | Sheet | Authority |\n"
        "|---|---|---:|---|\n" + rows
    )


def render_gallery(manifest: dict, href: str, level: int = 3) -> str:
    """Embedded sheet gallery: heading, linked SVG, reviewer note."""
    hashes = "#" * level
    blocks = []
    for sheet in manifest["sheets"]:
        target = f"{href}{sheet['file']}"
        blocks.append(
            f"{hashes} {sheet['number']} · {sheet['heading']}\n\n"
            f"[![{sheet['description']}]({target})]({target})\n\n"
            f"{sheet['note']}\n\n"
            f"**Sheet** {sheet['scale']} · **Authority** {sheet['authority']}."
        )
    return "\n\n".join(blocks)


def repo_hero_block(manifest: dict) -> str:
    """Lead sheet, published directly under the README title.

    The reader should see the aircraft before reading anything about it, so the
    first sheet in the registry opens the file. It is generated like every other
    published block: it cannot drift from the drawing it shows.
    """
    sheet = manifest["sheets"][0]
    target = f"geometry/drawings/{sheet['file']}"
    return (
        f"[![{sheet['description']}]({target})]({target})\n\n"
        f"<sub>**{sheet['number']} · {sheet['heading']}** — {sheet['scale']} · "
        f"generated from the calculations, **DRAFT — NOT FOR MANUFACTURE**. "
        f"The complete set is [below](#drawing-set--generated-design-review-sheets).</sub>"
    )


def repo_readme_block(manifest: dict) -> str:
    """Index table, then the gallery.

    The hero block already opened the file with the lead sheet, so the table
    separates that first impression from the same drawing appearing again at the
    head of the gallery.
    """
    href = "geometry/drawings/"
    return (
        f"{render_table(manifest, href)}\n\n"
        f"{render_gallery(manifest, href, level=3)}"
    )


def drawings_readme_block(manifest: dict) -> str:
    return render_table(manifest, "")


# ---------------------------------------------------------------------------
# block replacement


def replace_block(text: str, block: str, body: str, where: Path) -> str:
    pattern = block_re(block)
    if not pattern.search(text):
        raise SystemExit(
            f"{where.relative_to(ROOT)} has no generated {block} block; "
            f"add the {block_begin(block)!r} / {block_end(block)!r} markers"
        )
    replacement = f"{block_begin(block)}\n\n{body.strip()}\n\n{block_end(block)}"
    return pattern.sub(lambda _: replacement, text, count=1)


def targets(manifest: dict) -> tuple[tuple[Path, str], ...]:
    """Every generated artifact as (path, expected content)."""
    return (
        (MANIFEST_PATH, manifest_json(manifest)),
        (
            REPO_README,
            replace_block(
                replace_block(
                    REPO_README.read_text(encoding="utf-8"),
                    HERO_BLOCK,
                    repo_hero_block(manifest),
                    REPO_README,
                ),
                INDEX_BLOCK,
                repo_readme_block(manifest),
                REPO_README,
            ),
        ),
        (
            DRAWINGS_README,
            replace_block(
                DRAWINGS_README.read_text(encoding="utf-8"),
                INDEX_BLOCK,
                drawings_readme_block(manifest),
                DRAWINGS_README,
            ),
        ),
    )


def sync(write: bool) -> dict[str, bool]:
    """Write (or verify) the manifest and every published drawing block."""
    checks: dict[str, bool] = {}

    declared = {spec.filename for spec in SHEETS}
    on_disk = {p.name for p in DRAWINGS_DIR.glob("*.svg")}
    checks["drawing index: every rendered sheet is published"] = declared == on_disk
    if declared != on_disk:
        for orphan in sorted(on_disk - declared):
            checks[f"drawing index: {orphan} is missing a SheetSpec"] = False
        for absent in sorted(declared - on_disk):
            checks[f"drawing index: {absent} declared but not rendered"] = False
        return checks

    manifest = build_manifest()
    for path, expected in targets(manifest):
        if write:
            path.write_text(expected, encoding="utf-8", newline="\n")
        current = path.read_text(encoding="utf-8") if path.exists() else None
        checks[f"drawing index: {path.relative_to(ROOT)} is current"] = current == expected
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish the generated SVG drawing set into README, drawing index and wiki manifest"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the manifest and documentation blocks without writing",
    )
    args = parser.parse_args()

    checks = sync(write=not args.check)
    print("=" * 86)
    print("SALAMANDRA DRAWING INDEX · MANIFEST AND PUBLISHED BLOCKS")
    print("=" * 86)
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        if args.check:
            print(
                "\nSTALE: run `python3 calculations/generate_blueprints.py` "
                "to republish the drawing set."
            )
        raise SystemExit(1)
    print("\nDRAWING INDEX: ALL PASS")


if __name__ == "__main__":
    main()
