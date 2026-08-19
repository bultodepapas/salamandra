#!/usr/bin/env python3
"""Generate the controlled Salamandra draft drawing set as metric A3 SVG files.

The drawings are communication artifacts, not manufacturing authority.  Exact
planform geometry is imported from ``design_config.py``; balance stations are
imported from ``balance_cg.py``.  Geometry that is still a CAD assumption is
drawn in amber with a dashed line and is labelled PROVISIONAL.

Run from any directory::

    python calculations/generate_blueprints.py
    python calculations/generate_blueprints.py --check

Writing also republishes ``geometry/drawings/manifest.json`` and the generated
drawing blocks in ``README.md`` and ``geometry/drawings/README.md`` through
``drawing_index.py``; ``--check`` fails when any of them is stale.  The wiki
reads the same manifest at build time.

The SVG viewport is 420 x 297 and the physical size is 420 mm x 297 mm.  Thus
one SVG user unit is one millimetre on the A3 sheet when printed at 100 %.
"""
from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import escape
from itertools import pairwise
from math import sqrt
from pathlib import Path

import aero_contract
import aircraft_scene
import drawing_index
import equipment_layout
import fuselage_contract
import fuselage_geometry
from balance_cg import cg_target, np_vlm, np_weissinger, solve_reference_layout
from design_config import (
    ASPECT_RATIO,
    ELEVON_HINGE_XC,
    ELEVON_INBOARD_M,
    ELEVON_OUTBOARD_M,
    HALF_SPAN,
    MAC,
    PROP_DIAMETER_M,
    PROP_PLANE_M,
    ROOT_CHORD,
    STATIC_MARGIN,
    SWEEP_C4_DEG,
    TAPER,
    TIP_CHORD,
    S,
    chord,
    validate_geometry,
    x_c4,
    x_le,
    x_te,
)
from yaw_stability import (
    AR_FIN,
    FIN_BOOM_WIDTH_M,
    FIN_COUNT,
    FIN_AC_STATION_M,
    FIN_ROOT_THICKNESS_M,
    FIN_ROOT_Z_M,
    FIN_LE_SWEEP_DEG,
    FIN_SPAR_DIAMETER_M,
    FIN_SPAR_SEAT_DIAMETER_M,
    FIN_SWEEP_DEG,
    FIN_TAPER,
    FIN_TE_THICKNESS_M,
    FIN_TIP_THICKNESS_M,
    ETA_FIN_POWER_OFF,
    ETA_FIN_POWER_ON,
    cnb_total_band,
    fin_area_for_target,
    fin_drag,
    fin_geometry,
    fin_mass_band,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "geometry" / "drawings"
SHEET_WIDTH = 420.0
SHEET_HEIGHT = 297.0
TITLE_BLOCK_TOP = 257.0


@dataclass(frozen=True)
class DrawingContract:
    """Draft-only dimensions that are not part of the shared planform module."""

    core_half_span_m: float = 0.195
    segment_joints_m: tuple[float, ...] = (0.195, 0.347, 0.498, 0.650)
    elevon_inboard_m: float = ELEVON_INBOARD_M
    elevon_outboard_m: float = ELEVON_OUTBOARD_M
    hinge_fraction: float = ELEVON_HINGE_XC
    d_box_fraction: float = 0.30
    spar_fraction: float = 0.25
    spar_outboard_m: float = 0.585
    socket_depth_m: float = 0.070
    anti_rotation_offset_m: float = 0.065
    anti_rotation_bonded_m: float = 0.070
    nose_support_m: float = -0.132
    forward_support_m: float = -0.459
    tube_core_insertion_m: float = 0.050
    cradle_length_m: float = 0.201
    pack_length_m: float = 0.1530
    pack_width_m: float = 0.0657
    pack_height_m: float = 0.0226
    cradle_inner_width_m: float = 0.068
    cradle_inner_height_m: float = 0.025
    cradle_wall_m: float = 0.0012
    motor_body_forward_m: float = 0.195
    motor_mount_m: float = 0.230
    rear_pod_end_m: float = 0.265
    rear_pod_lower_prop_m: float = -0.1116
    motor_diameter_m: float = 0.028
    equipment_top_scale: float = 6.5
    equipment_side_scale: float = 4.0


CONTRACT = DrawingContract()

MASS_SKELETON_COMPONENT_IDS = (
    "battery_6s1p",
    "servo_left_406",
    "servo_right_406",
    "motor",
    "prop_adapter",
    "propeller",
    "esc",
    "fc",
    "pdb",
    "gps_mag",
    "receiver",
    "receiver_antenna",
    "pitot_sensor",
    "pitot_probe_tube",
    "buzzer",
    "o4_camera",
    "o4_vtx",
    "avionics_installation_reserve",
)

# E-numbers are controlled item references, not row numbers. Retiring a number
# instead of reusing it prevents a removed item from silently renumbering the
# motor, avionics and O4 references downstream.
RETIRED_MASS_SKELETON_REFERENCES = (
    "E02",  # inboard left servo, removed by the two-servo decision (ADR-0026)
    "E03",  # inboard right servo, removed by the two-servo decision (ADR-0026)
)

MASS_SKELETON_REFERENCE_BY_ID = {
    "battery_6s1p": "E01",
    "servo_left_406": "E04",
    "servo_right_406": "E05",
    "motor": "E06",
    "prop_adapter": "E07",
    "propeller": "E08",
    "esc": "E09",
    "fc": "E10",
    "pdb": "E11",
    "gps_mag": "E12",
    "receiver": "E13",
    "receiver_antenna": "E14",
    "pitot_sensor": "E15",
    "pitot_probe_tube": "E16",
    "buzzer": "E17",
    "o4_camera": "E18",
    "o4_vtx": "E19",
    "avionics_installation_reserve": "E21",
}


@dataclass(frozen=True)
class DrawingOutput:
    """One deterministic drawing artifact before it is written to disk."""

    path: Path
    drawing_number: str
    source: str


def fmt(value: float) -> str:
    """Compact, deterministic SVG number formatting."""
    if abs(value) < 5e-10:
        value = 0.0
    return f"{value:.3f}".rstrip("0").rstrip(".")


def attrs(**values: object) -> str:
    pairs = []
    for key, value in values.items():
        if value is None:
            continue
        key = key.rstrip("_").replace("_", "-")
        pairs.append(f'{key}="{escape(str(value), quote=True)}"')
    return " ".join(pairs)


class SvgSheet:
    """Small SVG writer with millimetre-native drafting primitives."""

    def __init__(self, title: str, description: str, drawing_number: str):
        self.title = title
        self.description = description
        self.drawing_number = drawing_number
        self._body: list[str] = []

    def raw(self, value: str) -> None:
        self._body.append(value)

    def line(self, x1: float, y1: float, x2: float, y2: float,
             css: str = "thin", **extra: object) -> None:
        self.raw(
            f"<line {attrs(x1=fmt(x1), y1=fmt(y1), x2=fmt(x2), y2=fmt(y2), class_=css, **extra)}/>"
        )

    def rect(self, x: float, y: float, width: float, height: float,
             css: str = "thin", rx: float | None = None, **extra: object) -> None:
        self.raw(
            f"<rect {attrs(x=fmt(x), y=fmt(y), width=fmt(width), height=fmt(height), rx=None if rx is None else fmt(rx), class_=css, **extra)}/>"
        )

    def circle(self, cx: float, cy: float, radius: float,
               css: str = "thin", **extra: object) -> None:
        self.raw(
            f"<circle {attrs(cx=fmt(cx), cy=fmt(cy), r=fmt(radius), class_=css, **extra)}/>"
        )

    def cg_symbol(self, cx: float, cy: float, radius: float,
                  identifier: str) -> None:
        """Draw the conventional quartered centre-of-gravity target."""
        top = cy - radius
        bottom = cy + radius
        left = cx - radius
        right = cx + radius
        self.raw(
            f'<g {attrs(id=identifier, role="img", aria_label="Calculated centre of gravity")}> '
            "<title>Calculated centre of gravity</title>"
        )
        self.circle(
            cx,
            cy,
            radius,
            "medium",
            style="fill:#fffdf8;stroke:none",
        )
        self.path(
            f"M {fmt(cx)} {fmt(cy)} L {fmt(cx)} {fmt(top)} "
            f"A {fmt(radius)} {fmt(radius)} 0 0 0 {fmt(left)} {fmt(cy)} Z",
            "thin",
            style="fill:#111820;stroke:none",
        )
        self.path(
            f"M {fmt(cx)} {fmt(cy)} L {fmt(cx)} {fmt(bottom)} "
            f"A {fmt(radius)} {fmt(radius)} 0 0 0 {fmt(right)} {fmt(cy)} Z",
            "thin",
            style="fill:#111820;stroke:none",
        )
        self.line(
            left,
            cy,
            right,
            cy,
            "thin",
            style="fill:none;stroke:#111820;stroke-width:.28",
        )
        self.line(
            cx,
            top,
            cx,
            bottom,
            "thin",
            style="fill:none;stroke:#111820;stroke-width:.28",
        )
        self.circle(
            cx,
            cy,
            radius,
            "medium",
            style="fill:none;stroke:#111820;stroke-width:.52",
        )
        self.raw("</g>")

    def polyline(self, points: list[tuple[float, float]], css: str = "thin",
                 close: bool = False, **extra: object) -> None:
        value = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)
        tag = "polygon" if close else "polyline"
        self.raw(f"<{tag} {attrs(points=value, class_=css, **extra)}/>")

    def path(self, data: str, css: str = "thin", **extra: object) -> None:
        self.raw(f"<path {attrs(d=data, class_=css, **extra)}/>")

    def text(self, x: float, y: float, value: str, css: str = "label",
             anchor: str = "start", rotate: float | None = None,
             **extra: object) -> None:
        transform = None if rotate is None else f"rotate({fmt(rotate)} {fmt(x)} {fmt(y)})"
        self.raw(
            f"<text {attrs(x=fmt(x), y=fmt(y), class_=css, text_anchor=anchor, transform=transform, **extra)}>{escape(value)}</text>"
        )

    def multiline(self, x: float, y: float, lines: list[str],
                  css: str = "note", leading: float = 4.0,
                  anchor: str = "start") -> None:
        self.raw(f"<text {attrs(x=fmt(x), y=fmt(y), class_=css, text_anchor=anchor)}>")
        for index, line in enumerate(lines):
            self.raw(
                f'<tspan x="{fmt(x)}" dy="{fmt(0 if index == 0 else leading)}">{escape(line)}</tspan>'
            )
        self.raw("</text>")

    def horizontal_dimension(self, x1: float, x2: float, y: float,
                             object_y1: float, object_y2: float, label: str,
                             label_above: bool = True) -> None:
        self.line(x1, object_y1, x1, y, "extension")
        self.line(x2, object_y2, x2, y, "extension")
        self.line(x1, y, x2, y, "dimension",
                  marker_start="url(#arrow-start)", marker_end="url(#arrow-end)")
        self.text((x1 + x2) / 2.0, y - 1.7 if label_above else y + 3.8,
                  label, "dimension-text", "middle")

    def vertical_dimension(self, x: float, y1: float, y2: float,
                           object_x1: float, object_x2: float, label: str,
                           label_left: bool = False) -> None:
        self.line(object_x1, y1, x, y1, "extension")
        self.line(object_x2, y2, x, y2, "extension")
        self.line(x, y1, x, y2, "dimension",
                  marker_start="url(#arrow-start)", marker_end="url(#arrow-end)")
        offset = -2.0 if label_left else 2.0
        self.text(x + offset, (y1 + y2) / 2.0, label, "dimension-text",
                  "middle", rotate=-90)

    def leader(self, x1: float, y1: float, x2: float, y2: float,
               label: str, provisional: bool = False, anchor: str = "start") -> None:
        css = "leader provisional-line" if provisional else "leader"
        self.line(x1, y1, x2, y2, css)
        self.circle(x1, y1, 0.65, "provisional-dot" if provisional else "datum-dot")
        self.text(x2 + (-1.5 if anchor == "end" else 1.5), y2 - 0.8, label,
                  "provisional-text" if provisional else "note", anchor)

    def render(self) -> str:
        style = """
          :root { color-scheme: light; }
          * { vector-effect: non-scaling-stroke; }
          .sheet { fill: #fffdf8; }
          .grid { fill: url(#grid); }
          .frame, .title-line { fill: none; stroke: #17202a; stroke-width: .5; }
          .outline { fill: none; stroke: #111820; stroke-width: .7; stroke-linejoin: round; }
          .medium { fill: none; stroke: #263746; stroke-width: .42; }
          .thin { fill: none; stroke: #455563; stroke-width: .25; }
          .hidden { fill: none; stroke: #667784; stroke-width: .25; stroke-dasharray: 2.4 1.4; }
          .centre { fill: none; stroke: #5a6c79; stroke-width: .2; stroke-dasharray: 7 1.4 1.2 1.4; }
          .station { fill: none; stroke: #6c7c87; stroke-width: .22; stroke-dasharray: 4 1.5; }
          .controlled-fill { fill: #eaf0f3; stroke: none; }
          .core-fill { fill: #d9e2e7; stroke: none; }
          .segment-fill-a { fill: #eef3f5; stroke: none; }
          .segment-fill-b { fill: #f7f9fa; stroke: none; }
          .elevon-fill { fill: #dcecf4; stroke: #24698f; stroke-width: .35; }
          .derived { fill: none; stroke: #146e9b; stroke-width: .45; }
          .derived-fill { fill: #146e9b; stroke: none; }
          .provisional-line { fill: none; stroke: #a86000; stroke-width: .48; stroke-dasharray: 3 1.5; }
          .provisional-fill { fill: #f4c46a; fill-opacity: .18; stroke: #a86000; stroke-width: .48; stroke-dasharray: 3 1.5; }
          .provisional-dot { fill: #b76e00; stroke: none; }
          .datum-dot { fill: #17202a; stroke: none; }
          .dimension, .extension, .leader { fill: none; stroke: #314451; stroke-width: .22; }
          .extension { stroke: #71808a; }
          .leader { stroke-width: .25; }
          text { font-family: Arial, Helvetica, sans-serif; fill: #17202a; }
          .sheet-title { font-size: 5.2px; font-weight: 700; letter-spacing: .35px; }
          .block-title { font-size: 3.8px; font-weight: 700; letter-spacing: .16px; }
          .sheet-subtitle { font-size: 3.2px; font-weight: 600; letter-spacing: .18px; }
          .label { font-size: 3.1px; font-weight: 600; }
          .note { font-size: 2.75px; }
          .micro { font-size: 2.35px; letter-spacing: .05px; }
          .dimension-text { font: 600 2.8px 'Courier New', Consolas, monospace; }
          .mono { font: 2.7px 'Courier New', Consolas, monospace; }
          .provisional-text { font-size: 2.65px; font-weight: 600; fill: #985b00; }
          .status { font-size: 3.1px; font-weight: 700; fill: #985b00; letter-spacing: .25px; }
          .watermark { font-size: 8px; font-weight: 700; fill: #b76e00; fill-opacity: .08; letter-spacing: .8px; }
        """
        defs = f"""
        <defs>
          <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
            <path d="M10 0H0V10" fill="none" stroke="#2e4757" stroke-opacity=".07" stroke-width=".16"/>
          </pattern>
          <marker id="arrow-end" markerWidth="3" markerHeight="3" refX="2.6" refY="1.5" orient="auto" markerUnits="userSpaceOnUse">
            <path d="M0 0L3 1.5L0 3Z" fill="#314451"/>
          </marker>
          <marker id="arrow-start" markerWidth="3" markerHeight="3" refX=".4" refY="1.5" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
            <path d="M0 0L3 1.5L0 3Z" fill="#314451"/>
          </marker>
          <style>{style}</style>
        </defs>
        """
        body = "\n".join(self._body)
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm"
     viewBox="0 0 420 297" role="img" aria-labelledby="svg-title svg-desc">
  <title id="svg-title">{escape(self.title)}</title>
  <desc id="svg-desc">{escape(self.description)}</desc>
  <metadata>Generated by calculations/generate_blueprints.py; drawing {escape(self.drawing_number)}; units mm.</metadata>
  {defs}
  <rect width="420" height="297" class="sheet"/>
  <rect x="10" y="10" width="400" height="277" class="grid"/>
  {body}
</svg>
"""


def plan_point(x_m: float, y_m: float, origin_x: float, origin_y: float,
               scale: float) -> tuple[float, float]:
    """Map aircraft x/y to sheet x/y; aircraft forward is up on the sheet."""
    return origin_x + y_m * 1000.0 / scale, origin_y + x_m * 1000.0 / scale


def side_point(x_m: float, z_m: float, origin_x: float, origin_y: float,
               scale: float) -> tuple[float, float]:
    """Map aircraft x/z to sheet x/y; aft is right and positive z is up."""
    return origin_x + x_m * 1000.0 / scale, origin_y - z_m * 1000.0 / scale


def half_band(y0: float, y1: float, origin_x: float, origin_y: float,
              scale: float) -> list[tuple[float, float]]:
    return [
        plan_point(x_le(y0), y0, origin_x, origin_y, scale),
        plan_point(x_le(y1), y1, origin_x, origin_y, scale),
        plan_point(x_te(y1), y1, origin_x, origin_y, scale),
        plan_point(x_te(y0), y0, origin_x, origin_y, scale),
    ]


def full_outline(origin_x: float, origin_y: float,
                 scale: float) -> list[tuple[float, float]]:
    h = HALF_SPAN
    return [
        plan_point(x_le(0.0), 0.0, origin_x, origin_y, scale),
        plan_point(x_le(h), -h, origin_x, origin_y, scale),
        plan_point(x_te(h), -h, origin_x, origin_y, scale),
        plan_point(x_te(0.0), 0.0, origin_x, origin_y, scale),
        plan_point(x_te(h), h, origin_x, origin_y, scale),
        plan_point(x_le(h), h, origin_x, origin_y, scale),
    ]


def chord_fraction_point(y_m: float, fraction: float, origin_x: float,
                         origin_y: float, scale: float) -> tuple[float, float]:
    x_m = x_le(y_m) + fraction * chord(y_m)
    return plan_point(x_m, y_m, origin_x, origin_y, scale)


def load_airfoil(path: Path) -> list[tuple[float, float]]:
    """Load a two-column UIUC-format airfoil file, ignoring its name line."""
    points: list[tuple[float, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) != 2:
            continue
        try:
            points.append((float(fields[0]), float(fields[1])))
        except ValueError:
            continue
    if len(points) < 20:
        raise ValueError(f"airfoil file has too few coordinate rows: {path}")
    return points


def airfoil_limits(points: list[tuple[float, float]], x_fraction: float) -> tuple[float, float]:
    """Interpolate lower/upper normalized ordinates at one chord fraction."""
    leading_edge = min(range(len(points)), key=lambda index: points[index][0])

    def interpolate(branch: list[tuple[float, float]]) -> float:
        ordered = sorted(branch)
        for (x0, y0), (x1, y1) in pairwise(ordered):
            if x0 <= x_fraction <= x1 and x1 > x0:
                weight = (x_fraction - x0) / (x1 - x0)
                return y0 + weight * (y1 - y0)
        return min(ordered, key=lambda point: abs(point[0] - x_fraction))[1]

    first = interpolate(points[:leading_edge + 1])
    second = interpolate(points[leading_edge:])
    return min(first, second), max(first, second)


def title_block(sheet: SvgSheet, title: str, number: str, scale: str,
                sources: str, title_font_size: float = 3.8) -> None:
    sheet.rect(10, 10, 400, 277, "frame")
    sheet.line(10, TITLE_BLOCK_TOP, 410, TITLE_BLOCK_TOP, "title-line")
    sheet.line(258, TITLE_BLOCK_TOP, 258, 287, "title-line")
    sheet.line(348, TITLE_BLOCK_TOP, 348, 287, "title-line")
    sheet.line(258, 274, 410, 274, "title-line")
    sheet.line(379, 274, 379, 287, "title-line")
    sheet.text(16, 266, "SALAMANDRA · OPEN 3D-PRINTED AIRCRAFT", "sheet-subtitle")
    sheet.text(16, 272, "METRIC TECHNICAL SKETCH · PRINT AT 100 %", "note")
    sheet.text(16, 280, sources, "micro")
    sheet.text(263, 264, title, "block-title", style=f"font-size:{fmt(title_font_size)}px")
    sheet.text(263, 270, "DRAFT · NOT FOR MANUFACTURE", "status")
    sheet.text(352, 263, "DRAWING", "micro")
    sheet.text(352, 270, number, "mono")
    sheet.text(263, 280, "SCALE", "micro")
    sheet.text(263, 285, scale, "mono")
    sheet.text(352, 280, "SHEET", "micro")
    sheet.text(352, 285, "A3 · 420 × 297", "mono")
    sheet.text(383, 280, "REV", "micro")
    sheet.text(383, 285, "P0", "mono")


def provenance_legend(sheet: SvgSheet, x: float, y: float) -> None:
    sheet.line(x, y, x + 10, y, "outline")
    sheet.text(x + 13, y + 1, "CONTROLLED / DERIVED", "micro")
    sheet.line(x, y + 5, x + 10, y + 5, "provisional-line")
    sheet.text(x + 13, y + 6, "PROVISIONAL · CAD GATE F2", "micro")


def draw_general_arrangement() -> SvgSheet:
    scale = 4.0
    ox, oy = 210.0, 160.0
    sheet = SvgSheet(
        "Salamandra Article #1 general arrangement",
        "Metric A3 top-view draft showing controlled forward-swept planform geometry, modular stations, calculated balance datums, and a provisional continuous fuselage outer-mould concept around the battery boom and propulsion pod.",
        "SLM-GA-001",
    )
    title_block(
        sheet,
        "GENERAL ARRANGEMENT · TOP VIEW",
        "SLM-GA-001",
        "1:4",
        "SOURCE: DESIGN GUIDE v0.22 · ADR-0040/0043/0045 · I-21/I-27 · generate_blueprints.py",
    )
    sheet.text(210, 151, "DRAFT · CONTROLLED GEOMETRY + PROVISIONAL EQUIPMENT", "watermark", "middle")

    # Filled component bands make the modular breakdown readable without
    # changing the controlling outline.
    intervals = (0.0, 0.195, 0.347, 0.498, HALF_SPAN)
    fills = ("core-fill", "segment-fill-a", "segment-fill-b", "segment-fill-a")
    for sign in (-1.0, 1.0):
        for index, (a, b) in enumerate(pairwise(intervals)):
            points = half_band(sign * a, sign * b, ox, oy, scale)
            sheet.polyline(points, fills[index], close=True)

    # Elevons are controlled in chord fraction but remain provisional as final
    # CAD parts; blue indicates a derived geometric region.
    for sign in (-1.0, 1.0):
        y0 = sign * CONTRACT.elevon_inboard_m
        y1 = sign * CONTRACT.elevon_outboard_m
        points = [
            chord_fraction_point(y0, CONTRACT.hinge_fraction, ox, oy, scale),
            chord_fraction_point(y1, CONTRACT.hinge_fraction, ox, oy, scale),
            plan_point(x_te(y1), y1, ox, oy, scale),
            plan_point(x_te(y0), y0, ox, oy, scale),
        ]
        sheet.polyline(points, "elevon-fill", close=True)

    sheet.polyline(full_outline(ox, oy, scale), "outline", close=True)
    center_top = plan_point(-0.505, 0.0, ox, oy, scale)
    center_bottom = plan_point(0.285, 0.0, ox, oy, scale)
    sheet.line(*center_top, *center_bottom, "centre")

    # Quarter-chord datum and modular stations.
    for sign in (-1.0, 1.0):
        sheet.line(*plan_point(x_c4(0.0), 0.0, ox, oy, scale),
                   *plan_point(x_c4(sign * HALF_SPAN), sign * HALF_SPAN, ox, oy, scale),
                   "derived")
        for station in CONTRACT.segment_joints_m[:-1]:
            y = sign * station
            sheet.line(*plan_point(x_le(y), y, ox, oy, scale),
                       *plan_point(x_te(y), y, ox, oy, scale), "station")

    # Provisional continuous body OML.  Its longitudinal stations and required
    # battery width come from the current Design Guide, but the Bezier control
    # points are an [I] styling/packaging concept until OP-21 and F2 freeze CAD.
    layout = solve_reference_layout()
    component_layout, pack_station_mm = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("clean"), clamp=True
    )
    cradle_fwd = layout["bay_fwd"]
    cradle_aft = cradle_fwd + CONTRACT.cradle_length_m
    cradle_outer_half = (
        CONTRACT.cradle_inner_width_m + 2.0 * CONTRACT.cradle_wall_m
    ) / 2.0

    oml_model = fuselage_geometry.reference_model()
    body_points = [
        plan_point(x_mm / 1000.0, y_mm / 1000.0, ox, oy, scale)
        for x_mm, y_mm in fuselage_geometry.plan_outline_mm(oml_model)
    ]
    sheet.polyline(
        body_points,
        "provisional-fill",
        close=True,
        style=(
            "fill:#f4c46a;fill-opacity:.22;stroke:#985b00;stroke-width:.62;"
            "stroke-dasharray:3.4 1.6;stroke-linejoin:round"
        ),
    )

    # Internal packaging remains visible through the OML: Ø8 boom, cradle
    # envelope, pack station and the two structural support stations.
    boom_forward = layout["bay_fwd"]
    boom_aft = CONTRACT.nose_support_m + CONTRACT.tube_core_insertion_m
    boom_left = plan_point(boom_forward, -0.004, ox, oy, scale)
    boom_right = plan_point(boom_aft, 0.004, ox, oy, scale)
    sheet.rect(boom_left[0], boom_left[1], boom_right[0] - boom_left[0],
               boom_right[1] - boom_left[1], "provisional-line", rx=0.8)

    c1 = plan_point(cradle_fwd, -cradle_outer_half, ox, oy, scale)
    c2 = plan_point(cradle_aft, cradle_outer_half, ox, oy, scale)
    sheet.rect(c1[0], c1[1], c2[0] - c1[0], c2[1] - c1[1],
               "provisional-line", rx=4.0)
    pack_station = pack_station_mm / 1000.0
    camera_component = component_layout.component("o4_camera")
    vtx_component = component_layout.component("o4_vtx")
    camera_station = camera_component.position_mm[0] / 1000.0
    o4_coax_distance_mm = next(
        distance
        for link, distance, _ in component_layout.link_results()
        if link.name.startswith("DJI O4")
    )
    px1, py1 = plan_point(pack_station, -0.040, ox, oy, scale)
    px2, _ = plan_point(pack_station, 0.040, ox, oy, scale)
    sheet.line(px1, py1, px2, py1, "provisional-line")
    for station, half_width in (
        (cradle_aft, 0.030),
        (CONTRACT.nose_support_m, 0.026),
        (CONTRACT.motor_mount_m, 0.034),
    ):
        sheet.line(*plan_point(station, -half_width, ox, oy, scale),
                   *plan_point(station, half_width, ox, oy, scale), "station")

    motor_fwd = plan_point(CONTRACT.motor_body_forward_m, -0.0175, ox, oy, scale)
    motor_aft = plan_point(CONTRACT.motor_mount_m, 0.0175, ox, oy, scale)
    sheet.rect(motor_fwd[0], motor_fwd[1], motor_aft[0] - motor_fwd[0],
               motor_aft[1] - motor_fwd[1], "provisional-fill", rx=1.2)
    prop_left = plan_point(PROP_PLANE_M, -PROP_DIAMETER_M / 2.0, ox, oy, scale)
    prop_right = plan_point(PROP_PLANE_M, PROP_DIAMETER_M / 2.0, ox, oy, scale)
    sheet.line(*prop_left, *prop_right, "provisional-line")
    sheet.circle(*plan_point(PROP_PLANE_M, 0.0, ox, oy, scale), 1.4, "provisional-line")

    # CG and independent NP datums.  The separation is intentionally visible.
    for station, css, label, x_shift in (
        (cg_target(), "derived-fill", f"CG {cg_target()*1000:+.1f}", -23.0),
        (np_vlm(), "derived", f"NP VLM {np_vlm()*1000:+.1f}", 23.0),
    ):
        sx, sy = plan_point(station, 0.0, ox, oy, scale)
        if css == "derived-fill":
            sheet.leader(sx, sy, sx + x_shift, sy - 8.5, label)
            sheet.cg_symbol(sx, sy, 2.3, "cg-target-general-arrangement")
        else:
            sheet.circle(sx, sy, 1.8, css)
            sheet.line(sx - 2.7, sy, sx + 2.7, sy, css)
            sheet.line(sx, sy - 2.7, sx, sy + 2.7, css)
            sheet.leader(sx, sy, sx + x_shift, sy - 8.5, label)

    # FPV installation from the same 3-D ledger used for mass and cable gates.
    # The lens face is the camera envelope's minimum-x plane; the view ray is
    # forward (-x).  The straight centre-to-centre line is only a conservative
    # routing lower bound, not a released cable path.
    camera_min, camera_max = camera_component.aabb()
    vtx_min, vtx_max = vtx_component.aabb()
    for component_min, component_max, identifier in (
        (camera_min, camera_max, "camera"),
        (vtx_min, vtx_max, "vtx"),
    ):
        top_left = plan_point(
            component_min[0] / 1000.0,
            component_min[1] / 1000.0,
            ox,
            oy,
            scale,
        )
        bottom_right = plan_point(
            component_max[0] / 1000.0,
            component_max[1] / 1000.0,
            ox,
            oy,
            scale,
        )
        sheet.rect(
            top_left[0],
            top_left[1],
            bottom_right[0] - top_left[0],
            bottom_right[1] - top_left[1],
            "provisional-line",
            rx=0.7,
            id=f"general-arrangement-o4-{identifier}",
        )
    camera = plan_point(camera_station, 0.0, ox, oy, scale)
    vtx = plan_point(
        vtx_component.position_mm[0] / 1000.0,
        vtx_component.position_mm[1] / 1000.0,
        ox,
        oy,
        scale,
    )
    lens_face = plan_point(camera_min[0] / 1000.0, 0.0, ox, oy, scale)
    sheet.line(
        *camera,
        *vtx,
        "provisional-line",
        id="general-arrangement-o4-coax-lower-bound",
        style="stroke:#9a4f87;stroke-width:.55;stroke-dasharray:2 1",
    )
    sheet.line(
        *lens_face,
        lens_face[0] - 5.0,
        lens_face[1],
        "medium",
        marker_end="url(#arrow-end)",
        id="general-arrangement-camera-view-direction",
    )
    sheet.circle(*lens_face, 1.2, "provisional-line")

    # Principal dimensions.
    left_tip_le = plan_point(x_le(-HALF_SPAN), -HALF_SPAN, ox, oy, scale)
    right_tip_le = plan_point(x_le(HALF_SPAN), HALF_SPAN, ox, oy, scale)
    sheet.horizontal_dimension(left_tip_le[0], right_tip_le[0], 101.5,
                               left_tip_le[1], right_tip_le[1], "1300 mm [D]")
    root_le = plan_point(x_le(0.0), 0.0, ox, oy, scale)
    root_te = plan_point(x_te(0.0), 0.0, ox, oy, scale)
    sheet.vertical_dimension(272.0, root_le[1], root_te[1], root_le[0], root_te[0],
                             f"ROOT {ROOT_CHORD*1000:.1f}")
    tip_le = right_tip_le
    tip_te = plan_point(x_te(HALF_SPAN), HALF_SPAN, ox, oy, scale)
    sheet.vertical_dimension(383.5, tip_le[1], tip_te[1], tip_le[0], tip_te[0],
                             f"TIP {TIP_CHORD*1000:.1f}", label_left=True)

    # Labels and callouts are kept outside the densest geometry wherever possible.
    sheet.text(24, 24, "FORWARD", "label", "middle")
    sheet.line(24, 40, 24, 27, "medium", marker_end="url(#arrow-end)")
    sheet.text(225, 116, f"c/4 · {SWEEP_C4_DEG:+.1f}°", "label")
    sheet.text(210, 179, "CORE", "label", "middle")
    sheet.text(116, 166, "LEFT PANEL", "note", "middle")
    sheet.text(304, 166, "RIGHT PANEL", "note", "middle")
    for station, label in ((0.195, "J0 · 195"), (0.347, "J1 · 347"), (0.498, "J2 · 498")):
        sx, sy = plan_point(x_le(station), station, ox, oy, scale)
        sheet.text(sx + 1.5, sy + 5.0, label, "micro", rotate=-90)
    sheet.leader(
        *camera,
        185,
        52,
        f"O4 CAMERA x {camera_station*1000:+.1f} · FRONT / CENTRELINE [D]",
        True,
        "end",
    )
    sheet.leader(*plan_point(pack_station, 0.033, ox, oy, scale), 239, 73,
                 f"6S1P PACK x {pack_station*1000:+.1f} [D]/[E]", True)
    sheet.leader(
        *vtx,
        199,
        62,
        f"O4 VTX · COAX LOWER BOUND {o4_coax_distance_mm:.1f}/50.0 [D]/[M]",
        True,
    )
    sheet.leader(*plan_point(-0.180, -0.028, ox, oy, scale), 164, 86,
                 "FUSELAGE OML · PROVISIONAL [I]", True, "end")
    sheet.leader(*plan_point(PROP_PLANE_M, PROP_DIAMETER_M / 2.0, ox, oy, scale), 265, 229,
                 "APC 8×8 DISK x +235 · PROVISIONAL", True)
    sheet.leader(*chord_fraction_point(0.44, CONTRACT.hinge_fraction, ox, oy, scale),
                 335, 206, f"ELEVON · HINGE {ELEVON_HINGE_XC:.2f} c", False)
    provenance_legend(sheet, 302, 24)
    sheet.multiline(18, 239, [
        "DATUM: root c/4, x aft, y starboard.",
        f"S {S:.3f} m² · AR {ASPECT_RATIO:.2f} · taper {TAPER:.2f} · MAC {MAC*1000:.1f} mm.",
        f"NP independent check: {np_weissinger()*1000:+.1f} mm (Weissinger-L).",
    ], "micro", 3.4)
    return sheet


def draw_side_elevations() -> SvgSheet:
    """Draw the shared side OML and CLEAN/V1a twin-fin variants."""
    scale = 4.0
    origin_x = 175.0
    layout = solve_reference_layout()
    clean_scene = aircraft_scene.reference_scene("clean")
    v1_scene = aircraft_scene.reference_scene("v1")
    component_layout = clean_scene.layout
    pack_station_mm = component_layout.component("battery_6s1p").position_mm[0]
    cradle_fwd = layout["bay_fwd"]
    cradle_aft = cradle_fwd + CONTRACT.cradle_length_m
    pack_station = pack_station_mm / 1000.0
    camera_component = component_layout.component("o4_camera")
    vtx_component = component_layout.component("o4_vtx")
    camera_station = camera_component.position_mm[0] / 1000.0
    o4_coax_distance_mm = next(
        distance
        for link, distance, _ in component_layout.link_results()
        if link.name.startswith("DJI O4")
    )
    pack_fwd = pack_station - CONTRACT.pack_length_m / 2.0
    pack_aft = pack_station + CONTRACT.pack_length_m / 2.0
    pack_z_min = 0.004
    pack_z_max = pack_z_min + CONTRACT.pack_height_m
    v1_packaging = v1_scene.packaging
    v1_clearance = v1_scene.clearance
    assert v1_packaging is not None and v1_clearance is not None
    v1_o4_coax_distance_mm = next(
        distance
        for link, distance, _ in v1_scene.layout.link_results()
        if link.name.startswith("DJI O4")
    )
    clean_oml_model = fuselage_geometry.build_model(layout=clean_scene.layout)
    v1_oml_model = fuselage_geometry.build_model(layout=v1_scene.layout)

    root_section = load_airfoil(
        ROOT / "geometry" / "airfoils" / "salamandra-root-r1.dat"
    )
    fin_area = fin_area_for_target(0.0005)
    fin = fin_geometry(fin_area)
    fin_span = fin.span_m
    fin_root_chord = fin.root_chord_m
    fin_tip_chord = fin.tip_chord_m
    fin_centroid_z = fin.centroid_height_m
    fin_te = fin.root_te_x_m
    fin_root_le = fin.root_le_x_m
    fin_tip_le = fin.tip_le_x_m
    fin_root_z = FIN_ROOT_Z_M
    cnb_on = cnb_total_band(fin_area, ETA_FIN_POWER_ON)
    cnb_off = cnb_total_band(fin_area, ETA_FIN_POWER_OFF)

    sheet = SvgSheet(
        "Salamandra CLEAN and V1a side elevations",
        "Metric A3 side-elevation draft comparing SALAMANDRA-CLEAN with the V1a passive twin-fin variant. The two CORE-rooted fins and their aft root supports remain forward of the fixed propeller hazard; their side projections coincide. No movable rudder is defined.",
        "SLM-GA-002",
    )
    title_block(
        sheet,
        "SIDE ELEVATIONS · CLEAN / V1a",
        "SLM-GA-002",
        "1:4",
        "SOURCE: GUIDE §§4.4/6.7/9.2 · ADR-0038 · I-16/I-29",
    )
    def draw_variant(origin_y: float, *, with_fin: bool) -> None:
        active_scene = v1_scene if with_fin else clean_scene
        active_layout = active_scene.layout
        active_battery = active_layout.component("battery_6s1p")
        active_camera = active_layout.component("o4_camera")
        active_vtx = active_layout.component("o4_vtx")
        active_cradle_fwd = cradle_fwd - (
            v1_packaging.nose_extension_mm / 1000.0 if with_fin else 0.0
        )
        active_pack_min, active_pack_max = active_battery.aabb()
        active_camera_min, active_camera_max = active_camera.aabb()
        active_vtx_min, active_vtx_max = active_vtx.aabb()
        def point(x_m: float, z_m: float) -> str:
            x_svg, y_svg = side_point(x_m, z_m, origin_x, origin_y, scale)
            return f"{fmt(x_svg)} {fmt(y_svg)}"

        def curve(
            control_1: tuple[float, float],
            control_2: tuple[float, float],
            end: tuple[float, float],
        ) -> str:
            """Return a cubic segment for non-OML local installation details."""
            return f"C {point(*control_1)} {point(*control_2)} {point(*end)}"

        # The side OML is rebuilt from the active component layout.  V1 therefore
        # inherits the solver's forward camera/cradle shift instead of reusing
        # the shorter CLEAN body silhouette.
        oml_model = v1_oml_model if with_fin else clean_oml_model
        body_points = [
            side_point(x_mm / 1000.0, z_mm / 1000.0, origin_x, origin_y, scale)
            for x_mm, z_mm in fuselage_geometry.side_outline_mm(oml_model)
        ]
        sheet.polyline(
            body_points,
            "provisional-fill",
            close=True,
            style=(
                "fill:#f4c46a;fill-opacity:.22;stroke:#985b00;stroke-width:.62;"
                "stroke-dasharray:3.4 1.6;stroke-linejoin:round"
            ),
        )

        # The released root airfoil remains distinct from the provisional OML.
        section_points = [
            side_point(
                x_le(0.0) + x_fraction * ROOT_CHORD,
                z_fraction * ROOT_CHORD,
                origin_x,
                origin_y,
                scale,
            )
            for x_fraction, z_fraction in root_section
        ]
        sheet.polyline(section_points, "controlled-fill", close=True)
        sheet.polyline(section_points, "outline", close=True)
        sheet.polyline(
            body_points,
            "provisional-line",
            close=True,
            style="stroke-width:.62;fill:none",
        )

        # Complete electronic/propulsion skeleton from the canonical 3-D
        # component ledger.  The five large items drawn explicitly below are
        # excluded here to avoid double linework; every other equipment item is
        # projected from its oriented envelope and carries its stable E-number.
        skeleton_colours = {
            "energy": "#8c62a8",
            "propulsion": "#b94a48",
            "power": "#c07a16",
            "avionics": "#2d74a8",
            "sensor": "#258f8a",
            "actuator": "#4d8a45",
            "fpv": "#a64886",
            "rf": "#a64886",
            "reserve": "#737b82",
        }
        explicit_ids = {"battery_6s1p", "motor", "propeller", "o4_camera", "o4_vtx"}
        for component in (
            active_layout.component(identifier)
            for identifier in MASS_SKELETON_COMPONENT_IDS
            if identifier not in explicit_ids
        ):
            projected_min, projected_max = aircraft_scene.projected_bounds(
                component, "side"
            )
            top_left = side_point(
                projected_min[0] / 1000.0,
                projected_max[1] / 1000.0,
                origin_x,
                origin_y,
                scale,
            )
            bottom_right = side_point(
                projected_max[0] / 1000.0,
                projected_min[1] / 1000.0,
                origin_x,
                origin_y,
                scale,
            )
            colour = skeleton_colours.get(component.category, "#737b82")
            dash = "3 1.5" if component.authority in {"[E]", "[I]"} else "none"
            variant_id = "v1a" if with_fin else "clean"
            sheet.rect(
                top_left[0],
                top_left[1],
                bottom_right[0] - top_left[0],
                bottom_right[1] - top_left[1],
                "provisional-line",
                rx=0.45,
                id=f"side-skeleton-{variant_id}-{component.identifier}",
                style=(
                    f"fill:{colour};fill-opacity:.12;stroke:{colour};"
                    f"stroke-width:.38;stroke-dasharray:{dash}"
                ),
            )
            centre = side_point(
                component.position_mm[0] / 1000.0,
                component.position_mm[2] / 1000.0,
                origin_x,
                origin_y,
                scale,
            )
            sheet.circle(
                *centre,
                0.55,
                "derived",
                id=f"side-skeleton-mass-{variant_id}-{component.identifier}",
                style=f"fill:{colour};stroke:{colour};stroke-width:.2",
            )
            reference = MASS_SKELETON_REFERENCE_BY_ID[component.identifier]
            sheet.text(
                top_left[0] + 0.6,
                top_left[1] - 0.7,
                reference,
                "micro",
                id=f"side-skeleton-label-{variant_id}-{component.identifier}",
                style=f"fill:{colour};font-size:2.15px",
            )

        # Internal packaging: Ø8 boom, 155 x 24 mm cradle envelope and Ø28 motor.
        boom_top_left = side_point(active_cradle_fwd, 0.004, origin_x, origin_y, scale)
        boom_bottom_right = side_point(
            CONTRACT.nose_support_m + CONTRACT.tube_core_insertion_m,
            -0.004,
            origin_x,
            origin_y,
            scale,
        )
        sheet.rect(
            boom_top_left[0],
            boom_top_left[1],
            boom_bottom_right[0] - boom_top_left[0],
            boom_bottom_right[1] - boom_top_left[1],
            "provisional-line",
            rx=0.8,
        )
        pack_top_left = side_point(
            active_pack_min[0] / 1000.0,
            active_pack_max[2] / 1000.0,
            origin_x,
            origin_y,
            scale,
        )
        pack_bottom_right = side_point(
            active_pack_max[0] / 1000.0,
            active_pack_min[2] / 1000.0,
            origin_x,
            origin_y,
            scale,
        )
        sheet.rect(
            pack_top_left[0],
            pack_top_left[1],
            pack_bottom_right[0] - pack_top_left[0],
            pack_bottom_right[1] - pack_top_left[1],
            "provisional-line",
            rx=1.0,
        )
        for component_min, component_max, identifier in (
            (active_camera_min, active_camera_max, "camera"),
            (active_vtx_min, active_vtx_max, "vtx"),
        ):
            top_left = side_point(
                component_min[0] / 1000.0,
                component_max[2] / 1000.0,
                origin_x,
                origin_y,
                scale,
            )
            bottom_right = side_point(
                component_max[0] / 1000.0,
                component_min[2] / 1000.0,
                origin_x,
                origin_y,
                scale,
            )
            sheet.rect(
                top_left[0],
                top_left[1],
                bottom_right[0] - top_left[0],
                bottom_right[1] - top_left[1],
                "provisional-line",
                rx=0.7,
                id=(
                    f"side-o4-{identifier}-"
                    f"{'v1a' if with_fin else 'clean'}"
                ),
            )
        camera_centre = side_point(
            active_camera.position_mm[0] / 1000.0,
            active_camera.position_mm[2] / 1000.0,
            origin_x,
            origin_y,
            scale,
        )
        vtx_centre = side_point(
            active_vtx.position_mm[0] / 1000.0,
            active_vtx.position_mm[2] / 1000.0,
            origin_x,
            origin_y,
            scale,
        )
        lens_face = side_point(
            active_camera_min[0] / 1000.0,
            active_camera.position_mm[2] / 1000.0,
            origin_x,
            origin_y,
            scale,
        )
        sheet.line(
            *camera_centre,
            *vtx_centre,
            "provisional-line",
            id=(
                "side-o4-coax-lower-bound-"
                f"{'v1a' if with_fin else 'clean'}"
            ),
            style="stroke:#9a4f87;stroke-width:.55;stroke-dasharray:2 1",
        )
        sheet.circle(*lens_face, 1.1, "provisional-line")
        sheet.line(
            *lens_face,
            lens_face[0] - 5.0,
            lens_face[1],
            "medium",
            marker_end="url(#arrow-end)",
        )
        motor_top_left = side_point(
            CONTRACT.motor_body_forward_m,
            CONTRACT.motor_diameter_m / 2.0,
            origin_x,
            origin_y,
            scale,
        )
        motor_bottom_right = side_point(
            CONTRACT.motor_mount_m,
            -CONTRACT.motor_diameter_m / 2.0,
            origin_x,
            origin_y,
            scale,
        )
        sheet.rect(
            motor_top_left[0],
            motor_top_left[1],
            motor_bottom_right[0] - motor_top_left[0],
            motor_bottom_right[1] - motor_top_left[1],
            "provisional-line",
            rx=1.0,
        )

        hazard = active_scene.propeller
        hazard_top_left = side_point(
            (hazard.centre_mm[0] - hazard.inflated_axial_half_mm) / 1000.0,
            hazard.inflated_radius_mm / 1000.0,
            origin_x,
            origin_y,
            scale,
        )
        hazard_bottom_right = side_point(
            (hazard.centre_mm[0] + hazard.inflated_axial_half_mm) / 1000.0,
            -hazard.inflated_radius_mm / 1000.0,
            origin_x,
            origin_y,
            scale,
        )
        sheet.rect(
            hazard_top_left[0],
            hazard_top_left[1],
            hazard_bottom_right[0] - hazard_top_left[0],
            hazard_bottom_right[1] - hazard_top_left[1],
            "provisional-line",
            id=f"side-prop-hazard-{'v1a' if with_fin else 'clean'}",
            style=(
                "fill:#c43d32;fill-opacity:.055;stroke:#b83b32;"
                "stroke-width:.35;stroke-dasharray:1.5 1"
            ),
        )
        prop_top = side_point(
            PROP_PLANE_M,
            PROP_DIAMETER_M / 2.0,
            origin_x,
            origin_y,
            scale,
        )
        prop_bottom = side_point(
            PROP_PLANE_M,
            -PROP_DIAMETER_M / 2.0,
            origin_x,
            origin_y,
            scale,
        )
        sheet.line(*prop_top, *prop_bottom, "provisional-line")
        sheet.circle(
            *side_point(PROP_PLANE_M, 0.0, origin_x, origin_y, scale),
            1.3,
            "provisional-line",
        )

        # C26 is a local landing-skid/propeller-guard datum, not a 112 mm-deep
        # fuselage.  Keep the strut forward of the prop plane and meet the
        # ground datum only below the 101.6 mm prop radius.
        skid_path = " ".join([
            f"M {point(0.205, -0.025)}",
            curve(
                (0.214, -0.050),
                (0.226, -0.092),
                (PROP_PLANE_M, CONTRACT.rear_pod_lower_prop_m),
            ),
        ])
        sheet.path(
            skid_path,
            "provisional-line",
            style="fill:none;stroke-width:1.05;stroke-linecap:round",
        )
        sheet.line(
            *side_point(PROP_PLANE_M - 0.006,
                        CONTRACT.rear_pod_lower_prop_m, origin_x, origin_y, scale),
            *side_point(PROP_PLANE_M + 0.020,
                        CONTRACT.rear_pod_lower_prop_m, origin_x, origin_y, scale),
            "provisional-line",
            stroke_dasharray="none",
        )

        carrier_end = fin.boom_x_end_m if with_fin else CONTRACT.rear_pod_end_m
        sheet.line(
            *side_point(active_cradle_fwd - 0.015, 0.0, origin_x, origin_y, scale),
            *side_point(carrier_end + 0.015, 0.0, origin_x, origin_y, scale),
            "centre",
        )
        sheet.line(
            *side_point(0.0, 0.045, origin_x, origin_y, scale),
            *side_point(0.0, -0.125, origin_x, origin_y, scale),
            "station",
        )

        if with_fin:
            carrier_start = fin.boom_x_start_m
            carrier_path = " ".join([
                f"M {point(carrier_start, FIN_ROOT_Z_M)}",
                f"L {point(fin.boom_x_end_m, FIN_ROOT_Z_M)}",
                curve(
                    (fin.boom_x_end_m + 0.004, 0.004),
                    (fin.boom_x_end_m + 0.004, -0.004),
                    (fin.boom_x_end_m, -FIN_ROOT_Z_M),
                ),
                f"L {point(carrier_start, -FIN_ROOT_Z_M)}",
                "Z",
            ])
            sheet.path(
                carrier_path,
                "provisional-fill",
                style=(
                    "fill:#f4c46a;fill-opacity:.22;stroke:#985b00;"
                    "stroke-width:.55;stroke-dasharray:3.4 1.6;stroke-linejoin:round"
                ),
            )
            # Both booms and fins are identical; side elevation is coincident.
            sheet.line(
                *side_point(fin.boom_x_start_m, 0.0, origin_x, origin_y, scale),
                *side_point(fin.boom_x_end_m, 0.0, origin_x, origin_y, scale),
                "derived",
                style="stroke:#146e9b;stroke-width:.35;stroke-dasharray:1.3 1.0",
            )
            fin_points = [
                side_point(fin_root_le, fin_root_z, origin_x, origin_y, scale),
                side_point(fin_tip_le, fin_root_z + fin_span, origin_x, origin_y, scale),
                side_point(
                    fin_tip_le + fin_tip_chord,
                    fin_root_z + fin_span,
                    origin_x,
                    origin_y,
                    scale,
                ),
                side_point(
                    fin_root_le + fin_root_chord,
                    fin_root_z,
                    origin_x,
                    origin_y,
                    scale,
                ),
            ]
            sheet.polyline(fin_points, "provisional-fill", close=True)
            # A small dorsal fairing makes the fin/boom junction physically
            # legible and removes the sharp printed stress riser.  Its area is
            # deliberately excluded from S_v and Cn_beta, so it cannot inflate
            # the directional-stability result before F2 geometry closure.
            root_fillet_path = " ".join([
                f"M {point(fin_root_le, fin_root_z)}",
                curve(
                    (fin_root_le + 0.010, fin_root_z),
                    (fin_root_le + 0.018, fin_root_z + 0.010),
                    (fin_root_le + 0.024, fin_root_z + 0.028),
                ),
                f"L {point(fin_root_le + 0.024, fin_root_z)}",
                "Z",
            ])
            sheet.path(
                root_fillet_path,
                "provisional-fill",
                style=(
                    "fill:#f4c46a;fill-opacity:.30;stroke:#985b00;"
                    "stroke-width:.55;stroke-dasharray:3.4 1.6;stroke-linejoin:round"
                ),
            )
            fin_ac = side_point(
                fin.ac_x_m,
                fin_root_z + fin_centroid_z,
                origin_x,
                origin_y,
                scale,
            )
            sheet.circle(*fin_ac, 1.4, "derived")
            sheet.line(fin_ac[0] - 2.2, fin_ac[1], fin_ac[0] + 2.2, fin_ac[1], "derived")
            sheet.line(fin_ac[0], fin_ac[1] - 2.2, fin_ac[0], fin_ac[1] + 2.2, "derived")
            fin_top_y = side_point(
                fin_tip_le,
                fin_root_z + fin_span,
                origin_x,
                origin_y,
                scale,
            )[1]
            fin_root_y = side_point(
                fin_root_le,
                fin_root_z,
                origin_x,
                origin_y,
                scale,
            )[1]
            sheet.vertical_dimension(
                286,
                fin_top_y,
                fin_root_y,
                fin_points[1][0],
                fin_points[0][0],
                f"b_v EACH {fin_span*1000:.0f} [D]",
            )
            sheet.leader(
                *fin_ac,
                300,
                140,
                f"FIN AC x +{fin.ac_x_m*1000:.0f} [D]/[E]",
            )

    draw_variant(73.0, with_fin=False)
    draw_variant(185.0, with_fin=True)

    sheet.text(20, 23, "A · SALAMANDRA-CLEAN", "sheet-subtitle")
    sheet.text(20, 28, "FINLESS · O1 EFFICIENCY BASELINE · YAW RISK [E]", "micro")
    sheet.text(20, 126, "B · SALAMANDRA-V1a", "sheet-subtitle")
    sheet.text(
        20,
        131,
        "2× FIXED FINS ON AFT CORE BOOMS · NO MOVABLE RUDDER · MARGINAL [E]",
        "micro",
    )
    sheet.line(51, 38, 32, 38, "medium", marker_end="url(#arrow-end)")
    sheet.text(54, 39, "FORWARD", "label")

    # Rear-view proof of the hidden y separation.  This inset is essential:
    # the side projection reports axial overlap but cannot establish collision.
    rear_cx, rear_cy, rear_scale = 350.0, 103.0, 4.0
    nominal_radius = v1_scene.propeller.nominal_radius_mm / rear_scale
    hazard_radius = v1_scene.propeller.inflated_radius_mm / rear_scale
    sheet.text(314, 43, "C · V1 REAR CLEARANCE", "sheet-subtitle")
    sheet.text(
        314,
        48,
        "y/z PROOF · x OVERLAP EVALUATED IN 3-D",
        "micro",
    )
    sheet.circle(
        rear_cx,
        rear_cy,
        hazard_radius,
        "provisional-line",
        id="side-rear-prop-hazard",
        style=(
            "fill:#c43d32;fill-opacity:.045;stroke:#b83b32;"
            "stroke-width:.4;stroke-dasharray:1.5 1"
        ),
    )
    sheet.circle(
        rear_cx,
        rear_cy,
        nominal_radius,
        "provisional-line",
        id="side-rear-prop-disk",
        style="fill:none;stroke:#b83b32;stroke-width:.55",
    )
    for side, sign in (("left", -1.0), ("right", 1.0)):
        boom_cx = rear_cx + sign * fin.lateral_station_m * 1000.0 / rear_scale
        boom_w = FIN_BOOM_WIDTH_M * 1000.0 / rear_scale
        boom_h = 14.0 / rear_scale
        sheet.rect(
            boom_cx - boom_w / 2.0,
            rear_cy - boom_h / 2.0,
            boom_w,
            boom_h,
            "provisional-line",
            id=f"side-rear-boom-{side}",
            style=(
                "fill:#f4c46a;fill-opacity:.24;stroke:#985b00;"
                "stroke-width:.45;stroke-dasharray:2 1"
            ),
        )
        fin_root_y = rear_cy - FIN_ROOT_Z_M * 1000.0 / rear_scale
        fin_top_y = rear_cy - (
            FIN_ROOT_Z_M + fin.span_m
        ) * 1000.0 / rear_scale
        fin_w = max(1.0, FIN_ROOT_THICKNESS_M * 1000.0 / rear_scale)
        sheet.rect(
            boom_cx - fin_w / 2.0,
            fin_top_y,
            fin_w,
            fin_root_y - fin_top_y,
            "provisional-line",
            id=f"side-rear-fin-{side}",
            style=(
                "fill:#f4c46a;fill-opacity:.18;stroke:#985b00;"
                "stroke-width:.55;stroke-dasharray:2 1"
            ),
        )
    right_disk = rear_cx + nominal_radius
    right_boom_inner = (
        rear_cx
        + (fin.lateral_station_m * 1000.0 - FIN_BOOM_WIDTH_M * 500.0)
        / rear_scale
    )
    sheet.line(right_disk, rear_cy + 4.5, right_boom_inner, rear_cy + 4.5, "dimension")
    sheet.line(right_disk, rear_cy + 2.0, right_disk, rear_cy + 7.0, "extension")
    sheet.line(
        right_boom_inner,
        rear_cy + 2.0,
        right_boom_inner,
        rear_cy + 7.0,
        "extension",
    )
    sheet.text(
        314,
        136,
        f"BOOM: {v1_clearance.boom_nominal_mm:.1f} nominal / "
        f"{v1_clearance.boom_residual_mm:.1f} residual [E]/[I]",
        "micro",
        id="side-rear-clearance-label",
    )
    sheet.text(
        314,
        141,
        f"{v1_clearance.physical_status} · axial projection overlap "
        f"{v1_clearance.axial_overlap_mm:.1f} mm",
        "micro",
        id="side-rear-clearance-status",
    )

    sheet.leader(
        *side_point(pack_station, pack_z_max, origin_x, 73.0, scale),
        108,
        49,
        "E01 MAX 153.0 × 22.6 [M]/[E]",
        True,
        "end",
    )
    sheet.leader(
        *side_point(-0.165, 0.012, origin_x, 73.0, scale),
        138,
        43,
        "SIDE OML [I]",
        True,
        "end",
    )
    sheet.leader(
        *side_point(PROP_PLANE_M, PROP_DIAMETER_M / 2.0,
                    origin_x, 73.0, scale),
        292,
        55,
        "APC 8×8 · Ø203 · x +235 [D]/[I]",
        True,
    )
    sheet.leader(
        *side_point(PROP_PLANE_M, CONTRACT.rear_pod_lower_prop_m,
                    origin_x, 185.0, scale),
        298,
        225,
        "LOCAL SKID z −111.6 · PROP CLEARANCE 10 [I]",
        True,
    )
    sheet.leader(
        *side_point(fin.boom_x_end_m, 0.0, origin_x, 185.0, scale),
        300,
        198,
        f"2× AFT BOOMS TO x +{fin.boom_x_end_m*1000:.0f} [D]/[I]",
        True,
    )
    sheet.leader(
        *side_point(fin_root_le + 0.62 * fin_root_chord,
                    fin_root_z + 0.55 * fin_span, origin_x, 185.0, scale),
        300,
        153,
        f"V1a 2× FIXED FINS · S_v,total {fin_area*100:.2f} dm² · NO HINGE / SERVO",
        True,
    )
    sheet.leader(
        *side_point(v1_oml_model.x_min_mm / 1000.0, 0.0, origin_x, 185.0, scale),
        84,
        168,
        f"V1 OML NOSE x {v1_oml_model.x_min_mm:+.1f} · +{v1_packaging.nose_extension_mm:.1f} [D]/[I]",
        True,
        "end",
    )
    sheet.horizontal_dimension(
        side_point(x_le(0.0), 0.0, origin_x, 73.0, scale)[0],
        side_point(x_te(0.0), 0.0, origin_x, 73.0, scale)[0],
        108.0,
        73.0,
        73.0,
        f"ROOT {ROOT_CHORD*1000:.1f} [D]",
    )
    provenance_legend(sheet, 303, 24)
    sheet.multiline(18, 228, [
        "DATUM: root c/4 x = 0; motor axis z = 0; positive z up.",
        "Shared [D]/[E]: root r1, Ø8 boom/socket, pack envelope, Ø28 motor and V1a fin sizing.",
        "Side OML, equipment vertical placement, local skid and twin-boom interfaces remain [I].",
        f"O4: CAMERA FRONT/CENTRELINE [D]; COAX STRAIGHT-LINE LOWER BOUND {o4_coax_distance_mm:.1f}/50.0 mm [D]/[M].",
        f"FIN PLANFORM EACH [D]/[E]: LE {FIN_LE_SWEEP_DEG:.1f}° · Λc/4 {fin.quarter_chord_sweep_deg:.3f}° · taper {FIN_TAPER:.2f}.",
        "ROOT FAIRING [I]: contained inside the credited planform; no forward decorative extension.",
        f"Cnβ independent corners: power-on {cnb_on[0]:+.5f}…{cnb_on[1]:+.5f}; power-off {cnb_off[0]:+.5f}…{cnb_off[1]:+.5f} /deg [E].",
        f"V1 COUPLED PACKAGING [E]/[I]: nose +{v1_packaging.nose_extension_mm:.1f} mm; mass {v1_scene.layout.mass_g():.1f} g; O4 coax {v1_o4_coax_distance_mm:.1f}/50.0 mm.",
        f"BODY OML [I]: CLEAN {clean_oml_model.length_mm:.1f} mm; V1 {v1_oml_model.length_mm:.1f} mm; V1 nose-to-boom extent {fin.boom_x_end_m*1000-v1_oml_model.x_min_mm:.1f} mm.",
        f"INSTALL [I]: roots y ±{fin.lateral_station_m*1000:.0f}; axial residual {v1_clearance.axial_residual_mm:.2f} mm to inflated prop slab; radial residual {v1_clearance.boom_residual_mm:.1f} mm; F2 open.",
    ], "micro", 3.4)
    return sheet


def draw_fin_detail() -> SvgSheet:
    """Draw one V1a fin and the complete twin-fin installation."""
    fin_area = fin_area_for_target(0.0005)
    fin = fin_geometry(fin_area)
    mass_lo, mass_hi = fin_mass_band(fin_area)
    dcd0, cf = fin_drag(fin_area)
    cnb_on = cnb_total_band(fin_area, ETA_FIN_POWER_ON)
    cnb_off = cnb_total_band(fin_area, ETA_FIN_POWER_OFF)
    boom_length = fin.boom_x_end_m - fin.boom_x_start_m
    scene = aircraft_scene.reference_scene("v1")
    clearance = scene.clearance
    packaging = scene.packaging
    assert clearance is not None and packaging is not None

    sheet = SvgSheet(
        "Salamandra V1a twin-fin geometry review",
        "Metric A3 engineering-review sheet for the passive V1a twin fins. It shows one calculated CORE-rooted fin, both aft root supports, the fixed propeller hazard, the aerodynamic datum and provisional structural interfaces. No movable rudder is defined.",
        "SLM-FIN-001",
    )
    title_block(
        sheet,
        "TWIN-FIN GEOMETRY REVIEW · V1a FIXED",
        "SLM-FIN-001",
        "1:1.5 / DETAILS NTS",
        "SOURCE: GUIDE §4.4/6.7 · ADR-0038 · I-29 · yaw_stability.py",
    )
    provenance_legend(sheet, 158, 218)
    sheet.text(20, 23, "A · ONE OF TWO IDENTICAL FINS", "sheet-subtitle")
    sheet.text(
        20,
        28,
        "PASSIVE TWIN FINS · SWEPT TRAPEZOID · NO HINGE / SERVO",
        "micro",
    )

    scale = 1.5
    origin_x = 43.0
    origin_y = 220.0

    def fin_point(x_m: float, z_m: float) -> tuple[float, float]:
        return (
            origin_x + (x_m - fin.root_le_x_m) * 1000.0 / scale,
            origin_y - z_m * 1000.0 / scale,
        )

    root_le = fin_point(fin.root_le_x_m, 0.0)
    tip_le = fin_point(fin.tip_le_x_m, fin.span_m)
    tip_te = fin_point(fin.tip_te_x_m, fin.span_m)
    root_te = fin_point(fin.root_te_x_m, 0.0)
    fin_points = [root_le, tip_le, tip_te, root_te]
    sheet.polyline(
        fin_points,
        "provisional-fill",
        close=True,
        id="fin-v1a-planform",
        style=(
            "fill:#f4c46a;fill-opacity:.20;stroke:#985b00;stroke-width:.62;"
            "stroke-dasharray:3.4 1.6;stroke-linejoin:round"
        ),
    )
    fillet_start = fin_point(fin.root_le_x_m, 0.0)
    fillet_c1 = fin_point(fin.root_le_x_m + 0.010, 0.0)
    fillet_c2 = fin_point(fin.root_le_x_m + 0.018, 0.010)
    fillet_end = fin_point(fin.root_le_x_m + 0.024, 0.028)
    fillet_close = fin_point(fin.root_le_x_m + 0.024, 0.0)
    sheet.path(
        " ".join([
            f"M {fmt(fillet_start[0])} {fmt(fillet_start[1])}",
            f"C {fmt(fillet_c1[0])} {fmt(fillet_c1[1])} "
            f"{fmt(fillet_c2[0])} {fmt(fillet_c2[1])} "
            f"{fmt(fillet_end[0])} {fmt(fillet_end[1])}",
            f"L {fmt(fillet_close[0])} {fmt(fillet_close[1])}",
            "Z",
        ]),
        "provisional-fill",
        id="fin-root-fillet-envelope",
        style=(
            "fill:#f4c46a;fill-opacity:.30;stroke:#985b00;stroke-width:.62;"
            "stroke-dasharray:3.4 1.6;stroke-linejoin:round"
        ),
    )

    root_qc = fin_point(fin.root_le_x_m + 0.25 * fin.root_chord_m, 0.0)
    tip_qc = fin_point(fin.tip_le_x_m + 0.25 * fin.tip_chord_m, fin.span_m)
    sheet.line(
        *root_qc,
        *tip_qc,
        "centre",
        id="fin-quarter-chord-line",
    )
    sheet.line(
        *root_le,
        *tip_le,
        "derived",
        id="fin-leading-edge-spar",
        style="stroke:#146e9b;stroke-width:.70;stroke-dasharray:5 1.2",
    )
    ac = fin_point(fin.ac_x_m, fin.centroid_height_m)
    sheet.circle(*ac, 1.7, "derived", id="fin-aerodynamic-centre")
    sheet.line(ac[0] - 2.8, ac[1], ac[0] + 2.8, ac[1], "derived")
    sheet.line(ac[0], ac[1] - 2.8, ac[0], ac[1] + 2.8, "derived")

    sheet.vertical_dimension(
        131.0,
        tip_le[1],
        root_le[1],
        tip_te[0],
        root_te[0],
        f"b_v EACH {fin.span_m*1000:.1f} [D]",
    )
    sheet.horizontal_dimension(
        root_le[0],
        root_te[0],
        231.5,
        root_le[1],
        root_te[1],
        f"c_r {fin.root_chord_m*1000:.1f} [D]",
        label_above=False,
    )
    sheet.horizontal_dimension(
        tip_le[0],
        tip_te[0],
        44.0,
        tip_le[1],
        tip_te[1],
        f"c_t {fin.tip_chord_m*1000:.1f} [D]",
    )
    sheet.leader(
        *ac,
        118,
        117,
        f"AC x +{fin.ac_x_m*1000:.0f} · z {fin.centroid_height_m*1000:.1f} [D]/[E]",
    )
    sheet.leader(
        *(fin_point(
            fin.root_le_x_m + 0.25 * fin.root_chord_m
            + 0.5 * (fin.tip_le_x_m + 0.25 * fin.tip_chord_m
                     - fin.root_le_x_m - 0.25 * fin.root_chord_m),
            0.5 * fin.span_m,
        )),
        118,
        80,
        f"Λc/4 {fin.quarter_chord_sweep_deg:.3f}° [D]",
    )
    sheet.leader(
        *(fin_point(
            0.5 * (fin.root_le_x_m + fin.tip_le_x_m),
            0.5 * fin.span_m,
        )),
        108,
        58,
        "LE SPAR Ø3 AL [D]/[E]",
    )

    # Cross-sections are deliberately schematic: chord is shortened and
    # thickness is exaggerated so the external LE rod/seat relationship is
    # reviewable on an A3 sheet.
    sheet.text(158, 23, "B · SECTION CONCEPTS", "sheet-subtitle")
    sheet.text(158, 28, "CHORD REDUCED · THICKNESS EXAGGERATED ×4 · NTS", "micro")

    def section_path(x0: float, cy: float, chord: float, plate_t: float) -> str:
        rod_r = 4.0
        te_half = 1.05
        half_t = plate_t / 2.0
        x1 = x0 + rod_r
        x2 = x0 + chord
        return " ".join([
            f"M {fmt(x1)} {fmt(cy-half_t)}",
            f"C {fmt(x0+0.40*chord)} {fmt(cy-half_t)} "
            f"{fmt(x0+0.78*chord)} {fmt(cy-te_half)} {fmt(x2)} {fmt(cy-te_half)}",
            f"L {fmt(x2)} {fmt(cy+te_half)}",
            f"C {fmt(x0+0.78*chord)} {fmt(cy+te_half)} "
            f"{fmt(x0+0.40*chord)} {fmt(cy+half_t)} {fmt(x1)} {fmt(cy+half_t)}",
            "Z",
        ])

    for tag, cy, chord, thickness in (
        ("ROOT", 73.0, 76.0, 8.0),
        ("TIP", 119.0, 48.0, 4.0),
    ):
        x0 = 166.0
        sheet.circle(
            x0 + 4.0,
            cy,
            4.0,
            "derived",
            style="fill:#eaf0f3;stroke:#146e9b;stroke-width:.55",
        )
        sheet.path(
            section_path(x0, cy, chord, thickness),
            "provisional-fill",
            style=(
                "fill:#f4c46a;fill-opacity:.20;stroke:#985b00;"
                "stroke-width:.48;stroke-dasharray:3 1.5"
            ),
        )
        sheet.line(x0 + 4.0, cy - 6.0, x0 + 4.0, cy + 6.0, "centre")
        sheet.text(
            158,
            cy - 15.0,
            f"{tag} · t_max {FIN_ROOT_THICKNESS_M*1000:.1f} mm"
            if tag == "ROOT"
            else f"{tag} · t_max {FIN_TIP_THICKNESS_M*1000:.1f} mm",
            "label",
        )
    sheet.multiline(158, 139, [
        f"LE: Ø{FIN_SPAR_DIAMETER_M*1000:.1f} Al rod; external nose element [D]/[E].",
        f"SEAT: Ø{FIN_SPAR_SEAT_DIAMETER_M*1000:.1f} open rear-facing C-seat [I].",
        f"TE: {FIN_TE_THICKNESS_M*1000:.1f} mm [E]. No enclosed Ø3.2 bore is claimed.",
    ], "micro", 3.4)

    sheet.text(158, 160, "C · ROOT / BOOM INTERFACE", "sheet-subtitle")
    mount_x = 165.0
    mount_y = 177.0
    mount_w = fin.root_chord_m * 1000.0 / scale
    sheet.rect(
        mount_x,
        mount_y,
        mount_w,
        8.0,
        "provisional-fill",
        rx=1.0,
        id="fin-root-interface-envelope",
    )
    sheet.line(mount_x, mount_y + 4.0, mount_x + mount_w, mount_y + 4.0, "centre")
    sheet.multiline(158, 194, [
        f"INTERFACE ENVELOPE: {fin.root_chord_m*1000:.1f} × "
        f"{FIN_ROOT_THICKNESS_M*1000:.1f} mm [D]/[I].",
        "HARDWARE PER FIN: 1× Ø1.75 dowel + 1× M2 screw [E].",
        "ROOT FILLET ENVELOPE SHOWN; final saddle, load spread and print compensation OPEN [I].",
    ], "micro", 3.4)

    sheet.text(273, 23, "D · CALCULATED SCHEDULE", "sheet-subtitle")
    schedule = [
        ("STATUS", "V1a MARGINAL · F2/E8 OPEN [E]"),
        ("COUNT / AREA", f"{FIN_COUNT} / {fin.area_m2*100:.4f} dm² total [D]"),
        ("AREA EACH", f"{fin.area_each_m2*100:.4f} dm² [D]"),
        ("SPAN EACH", f"{fin.span_m*1000:.1f} mm [D]"),
        ("ROOT / TIP", f"{fin.root_chord_m*1000:.1f} / {fin.tip_chord_m*1000:.1f} mm [D]"),
        ("MAC", f"{fin.mac_m*1000:.1f} mm [D]"),
        ("AR / TAPER", f"{AR_FIN:.2f} / {FIN_TAPER:.2f} [E]"),
        ("SWEEP LE / c/4", f"{FIN_LE_SWEEP_DEG:.1f}° / {FIN_SWEEP_DEG:.3f}° [D]/[E]"),
        ("AC STATION", f"x +{FIN_AC_STATION_M*1000:.0f} mm [E]"),
        ("ROOT / TIP t", f"{FIN_ROOT_THICKNESS_M*1000:.1f} / {FIN_TIP_THICKNESS_M*1000:.1f} mm [E]"),
        ("MASS", f"{mass_lo:.2f}–{mass_hi:.2f} g incl. booms [E]"),
        ("Cnβ ON", f"{cnb_on[0]:+.5f}…{cnb_on[1]:+.5f}/deg [E]"),
        ("Cnβ OFF", f"{cnb_off[0]:+.5f}…{cnb_off[1]:+.5f}/deg [E]"),
        ("ΔCD0", f"+{dcd0:.4f}; Cf {cf:.4f} [E]"),
        ("BOOMS", f"2× {boom_length*1000:.1f} mm at y ±{fin.lateral_station_m*1000:.0f} [E]/[I]"),
        ("PROP CLEAR", f"{clearance.boom_nominal_mm:.1f} nom / {clearance.boom_residual_mm:.1f} residual mm [E]/[I]"),
    ]
    y = 36.0
    for index, (name, value) in enumerate(schedule):
        sheet.text(273, y, name, "micro", id=f"fin-schedule-name-{index}")
        sheet.text(307, y, value, "mono", id=f"fin-schedule-value-{index}")
        sheet.line(272, y + 1.7, 399, y + 1.7, "thin", style="stroke-opacity:.18")
        y += 7.4

    sheet.text(273, 153, "E · TOP + REAR INSTALLATION", "sheet-subtitle")
    plan_x0 = 278.0
    plan_y0 = 190.0
    x_scale = 3.5
    y_scale = 5.5

    def px(x_m: float) -> float:
        return plan_x0 + (x_m - 0.145) * 1000.0 / x_scale

    def py(y_m: float) -> float:
        return plan_y0 - y_m * 1000.0 / y_scale

    # Top view: the inflated hazard slab and both outboard boom/fin roots.
    hazard = scene.propeller
    hazard_left = px((hazard.centre_mm[0] - hazard.inflated_axial_half_mm) / 1000.0)
    hazard_right = px((hazard.centre_mm[0] + hazard.inflated_axial_half_mm) / 1000.0)
    hazard_top = py(hazard.inflated_radius_mm / 1000.0)
    hazard_bottom = py(-hazard.inflated_radius_mm / 1000.0)
    sheet.rect(
        hazard_left,
        min(hazard_top, hazard_bottom),
        hazard_right - hazard_left,
        abs(hazard_bottom - hazard_top),
        "provisional-line",
        id="fin-install-prop-hazard-top",
        style=(
            "fill:#c43d32;fill-opacity:.05;stroke:#b83b32;"
            "stroke-width:.35;stroke-dasharray:1.5 1"
        ),
    )
    sheet.line(
        px(PROP_PLANE_M), py(-PROP_DIAMETER_M / 2.0),
        px(PROP_PLANE_M), py(PROP_DIAMETER_M / 2.0),
        "station", id="fin-install-prop-disk",
    )
    sheet.circle(px(PROP_PLANE_M), py(0.0), 1.2, "provisional-line")
    for sign, tag in ((-1.0, "L"), (1.0, "R")):
        y_m = sign * fin.lateral_station_m
        top = py(y_m + 0.009)
        bottom = py(y_m - 0.009)
        sheet.rect(
            px(fin.boom_x_start_m), min(top, bottom),
            px(fin.boom_x_end_m) - px(fin.boom_x_start_m), abs(bottom - top),
            "provisional-fill", rx=0.8, id=f"fin-install-boom-{tag.lower()}",
        )
        sheet.line(
            px(fin.root_le_x_m), py(y_m), px(fin.root_te_x_m), py(y_m),
            "derived", id=f"fin-install-root-{tag.lower()}",
            style="stroke:#146e9b;stroke-width:1.0",
        )
        sheet.text(px(fin.boom_x_end_m) + 2.0, py(y_m) + 1.0, tag, "micro")

    # Rear view: the hidden coordinate that the side elevation cannot prove.
    rear_cx, rear_cy, rear_scale = 371.0, 191.0, 5.5
    sheet.circle(
        rear_cx,
        rear_cy,
        hazard.inflated_radius_mm / rear_scale,
        "provisional-line",
        id="fin-install-prop-hazard-rear",
        style=(
            "fill:#c43d32;fill-opacity:.04;stroke:#b83b32;"
            "stroke-width:.35;stroke-dasharray:1.5 1"
        ),
    )
    sheet.circle(
        rear_cx,
        rear_cy,
        hazard.nominal_radius_mm / rear_scale,
        "provisional-line",
        id="fin-install-prop-disk-rear",
        style="fill:none;stroke:#b83b32;stroke-width:.5",
    )
    for side, sign in (("left", -1.0), ("right", 1.0)):
        fin_x = rear_cx + sign * fin.lateral_station_m * 1000.0 / rear_scale
        boom_w = FIN_BOOM_WIDTH_M * 1000.0 / rear_scale
        sheet.rect(
            fin_x - boom_w / 2.0,
            rear_cy - 7.0 / rear_scale,
            boom_w,
            14.0 / rear_scale,
            "provisional-fill",
            id=f"fin-install-boom-rear-{side}",
        )
        sheet.rect(
            fin_x - 0.5,
            rear_cy - (FIN_ROOT_Z_M + fin.span_m) * 1000.0 / rear_scale,
            1.0,
            fin.span_m * 1000.0 / rear_scale,
            "provisional-fill",
            id=f"fin-install-fin-rear-{side}",
        )
    sheet.multiline(273, 228, [
        f"PROP Ø{PROP_DIAMETER_M*1000:.1f} at x +{PROP_PLANE_M*1000:.0f}; hazard inflation {hazard.allowance.radial_total_mm:.1f} mm [E]/[I].",
        f"BOOM CLEARANCE {clearance.boom_nominal_mm:.1f} nominal / {clearance.boom_residual_mm:.1f} residual mm; {clearance.physical_status}.",
        f"Nose extension {packaging.nose_extension_mm:.1f} mm; root fairing contained inside planform; wake/F2 remain open [I].",
    ], "micro", 3.4)

    sheet.multiline(18, 239, [
        "AUTHORITY: planform coordinates are [D] from yaw_stability.py on [E] aerodynamic inputs.",
        "The fixed fins are not rudders. No hinge line, horn, linkage or servo is released.",
        "The independent-corner Cnβ screen includes power-on/off q-ratio cases; it is not flight-test closure.",
        "Structural sections, external LE spar seats, boom saddles and hardware remain provisional [I].",
    ], "micro", 3.4)
    return sheet


def draw_fuselage_oml_review() -> SvgSheet:
    """Draw the analytical body OML, skeleton envelopes and audit evidence."""
    model = fuselage_geometry.reference_model()
    report = fuselage_geometry.report_as_dict(model)
    audits = fuselage_geometry.audit_envelopes(model)
    layout = equipment_layout.reference_layout("clean")
    scale = 4.0
    origin_x = 128.0
    plan_y = 74.0
    side_y = 165.0

    sheet = SvgSheet(
        "Salamandra provisional fuselage OML review",
        "Metric A3 review sheet generated from the NumPy asymmetric superelliptic loft. "
        "It overlays body-owned inflated equipment envelopes in plan and side views, "
        "shows five transverse sections, and reports numerical containment and mesh "
        "diagnostics. All fuselage OML geometry is inferred and is not manufacturing authority.",
        "SLM-FUS-001",
    )
    title_block(
        sheet,
        "PARAMETRIC FUSELAGE OML REVIEW",
        "SLM-FUS-001",
        "VIEWS 1:4 · SECTIONS 1:1.5",
        "SOURCE: I-28 REV 3 · FUSELAGE_CONTRACT/GEOMETRY · EQP LAYOUT",
        title_font_size=3.35,
    )

    def x_view(x_mm: float) -> float:
        return origin_x + x_mm / scale

    def yz_view(value_mm: float, origin_y: float) -> float:
        return origin_y - value_mm / scale

    plan_points = [
        (x_view(x_mm), yz_view(y_mm, plan_y))
        for x_mm, y_mm in fuselage_geometry.plan_outline_mm(model)
    ]
    side_points = [
        (x_view(x_mm), yz_view(z_mm, side_y))
        for x_mm, z_mm in fuselage_geometry.side_outline_mm(model)
    ]
    sheet.polyline(
        plan_points,
        "provisional-fill",
        close=True,
        id="fuselage-oml-plan",
        style=(
            "fill:#f4c46a;fill-opacity:.20;stroke:#985b00;stroke-width:.62;"
            "stroke-dasharray:3.4 1.6;stroke-linejoin:round"
        ),
    )
    sheet.polyline(
        side_points,
        "provisional-fill",
        close=True,
        id="fuselage-oml-side",
        style=(
            "fill:#f4c46a;fill-opacity:.20;stroke:#985b00;stroke-width:.62;"
            "stroke-dasharray:3.4 1.6;stroke-linejoin:round"
        ),
    )
    sheet.line(x_view(model.x_min_mm - 18.0), plan_y,
               x_view(model.x_max_mm + 18.0), plan_y, "centre")
    sheet.line(x_view(model.x_min_mm - 18.0), side_y,
               x_view(model.x_max_mm + 18.0), side_y, "centre")

    envelope_by_id = {envelope.identifier: envelope for envelope in model.envelopes}
    for identifier in fuselage_contract.BODY_ENVELOPE_COMPONENT_IDS:
        envelope = envelope_by_id[identifier]
        minimum = envelope.minimum_mm
        maximum = envelope.maximum_mm
        sheet.rect(
            x_view(minimum[0]),
            yz_view(maximum[1], plan_y),
            (maximum[0] - minimum[0]) / scale,
            (maximum[1] - minimum[1]) / scale,
            "hidden",
            id=f"fuselage-envelope-plan-{identifier}",
        )
        sheet.rect(
            x_view(minimum[0]),
            yz_view(maximum[2], side_y),
            (maximum[0] - minimum[0]) / scale,
            (maximum[2] - minimum[2]) / scale,
            "hidden",
            id=f"fuselage-envelope-side-{identifier}",
        )

    sheet.text(16, 27, "A · PLAN · BODY-OWNED INFLATED ENVELOPES", "sheet-subtitle")
    sheet.text(16, 32, "WALL 1.2 + INSTALLATION CLEARANCE 1.0 mm [I]", "micro")
    sheet.text(16, 119, "B · SIDE · ASYMMETRIC DORSAL / VENTRAL LAW", "sheet-subtitle")
    sheet.text(16, 124, "ROOT WING SURFACE IS NOT A BOOLEAN UNION IN THIS OPERAND", "micro")
    sheet.line(36, 39, 23, 39, "medium", marker_end="url(#arrow-end)")
    sheet.text(40, 40, "FORWARD", "label")
    sheet.leader(x_view(-345.0), plan_y - 10.0, 161, 47,
                 "DASHED BOXES = EQUIPMENT + 2.45 mm [D]/[E]/[I]", True)
    sheet.leader(x_view(0.0), side_y - 8.0, 164, 143,
                 "LOFT FROM COMMON NUMPY SECTION LAW [I]", True)
    sheet.horizontal_dimension(
        x_view(model.x_min_mm),
        x_view(model.x_max_mm),
        205.0,
        side_y,
        side_y,
        f"BODY OPERAND L = {model.length_mm:.1f} mm [I]",
    )

    section_ids = ("o4_camera", "battery_6s1p", "nose_boom_tube", "fc", "motor")
    section_labels = ("CAM", "BAT", "BOOM", "CORE", "MOTOR")
    section_centres = [
        layout.component(identifier).position_mm[0] for identifier in section_ids
    ]
    section_origins = ((240.0, 53.0), (305.0, 53.0), (370.0, 53.0),
                       (270.0, 112.0), (354.0, 112.0))
    section_scale = 1.5
    for identifier, label, x_mm, (cx, cy) in zip(
        section_ids, section_labels, section_centres, section_origins
    ):
        points = fuselage_geometry.section_points(model, float(x_mm), 72)
        section = [
            (cx + float(y_mm) / section_scale, cy - float(z_mm) / section_scale)
            for _, y_mm, z_mm in points
        ]
        sheet.polyline(
            section,
            "provisional-fill",
            close=True,
            id=f"fuselage-section-{identifier}",
        )
        sheet.line(cx - 29, cy, cx + 29, cy, "centre")
        sheet.line(cx, cy - 25, cx, cy + 25, "centre")
        sheet.text(cx, cy + 31, f"{label} · x {float(x_mm):+.1f}", "micro", "middle")

    mesh = report["mesh"]
    projected = report["projected"]
    distribution = report["distribution"]
    sheet.text(223, 21, "C · TRANSVERSE SECTIONS · ONE 3-D SOURCE", "sheet-subtitle")
    sheet.text(221, 151, "D · NUMERICAL REVIEW", "sheet-subtitle")
    sheet.multiline(
        221,
        158,
        [
            f"FAMILY       {report['family']} [I]",
            f"RANGE x      {model.x_min_mm:+.2f} .. {model.x_max_mm:+.2f} mm",
            f"MAX WIDTH    {projected['maximum_width_mm']:.2f} mm",
            f"MAX HEIGHT   {projected['maximum_height_mm']:.2f} mm",
            f"AREA MAX x   {distribution['maximum_area_x_mm']:+.2f} mm · ROOT BAND PASS",
            f"NO-NECK      ratio={distribution['payload_to_root_minimum_area_ratio']:.3f}",
            f"PARALLEL     longest={100.0 * distribution['longest_parallel_side_fraction']:.2f}%",
            f"WETTED AREA  {mesh['area_m2']:.5f} m2 (gross operand)",
            f"VOLUME       {mesh['volume_m3'] * 1e3:.3f} L",
            f"0.9 mm SKIN  {mesh['gross_0p9_mm_skin_mass_g']:.1f} g SCREEN ONLY",
            f"TOPOLOGY     watertight={str(mesh['watertight']).upper()}",
            f"AIRCRAFT     feasible={str(report['aircraft_feasible']).upper()}",
        ],
        "mono",
        4.15,
    )
    sheet.text(322, 151, "ENVELOPE MINIMUM MARGINS", "sheet-subtitle")
    audit_lines = [
        f"{audit.identifier[:17]:17s} {audit.minimum_margin_mm:+6.3f} mm "
        f"{'PASS' if audit.passed else 'FAIL'}"
        for audit in audits
    ]
    sheet.multiline(322, 158, audit_lines, "mono", 4.15)
    sheet.multiline(
        221,
        218,
        [
            "OPEN PROJECT GATES:",
            "V1 BATTERY REACH · 92.88 g RESERVES · NET UNION MASS",
            "CAMERA APERTURE BOOLEAN · BODY-INCLUSIVE NP/TRIM · WING AUDIT",
            "GROSS OML OPERAND: NO RIBS, CUTOUTS, JOINTS OR PRINT WALL RELEASE",
        ],
        "provisional-text",
        4.2,
    )
    provenance_legend(sheet, 16, 226)
    sheet.text(16, 244, "[I] DRAFT OML · NOT A PRINTABLE SHELL · NOT FOR MANUFACTURE", "status")
    sheet.text(214, 246, "COORDINATES: mm · x AFT · y STARBOARD · z UP", "micro")
    return sheet


def draw_equipment_mass_skeleton() -> SvgSheet:
    """Draw the mass skeleton over a controlled top-view planform context."""
    top_scale = CONTRACT.equipment_top_scale
    side_scale = CONTRACT.equipment_side_scale
    top_origin = (137.0, 137.0)
    side_origin = (330.0, 73.0)
    clean, clean_battery_x = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("clean")
    )
    v1_packaging = equipment_layout.solve_v1_packaging()
    v1 = v1_packaging.layout
    v1_battery_x = v1_packaging.required_battery_x_mm
    components = tuple(
        clean.component(identifier) for identifier in MASS_SKELETON_COMPONENT_IDS
    )
    reference_by_id = MASS_SKELETON_REFERENCE_BY_ID
    equipment_group_by_category = {
        "energy": "energy",
        "propulsion": "propulsion",
        "power": "power",
        "avionics": "flight_control",
        "sensor": "sensors",
        "actuator": "actuators",
        "fpv": "fpv_rf",
        "rf": "fpv_rf",
        "reserve": "reserve",
    }
    equipment_palette = {
        # label, strong outline/text colour, light envelope fill
        "energy": ("ENERGY", "#6f4aa8", "#e9e0f5"),
        "propulsion": ("PROPULSION", "#c44b34", "#f6d8d1"),
        "power": ("POWER", "#c47a11", "#f7e3bd"),
        "flight_control": ("FLIGHT CTRL", "#246aa0", "#d9eaf5"),
        "sensors": ("SENSORS", "#177c73", "#d6eeea"),
        "actuators": ("ACTUATORS", "#4f7f32", "#dfeccf"),
        "fpv_rf": ("FPV / RF", "#9a4f87", "#f0ddec"),
        "reserve": ("RESERVE", "#626b73", "#e4e7e9"),
    }

    def component_palette(
        component: equipment_layout.Component3D,
    ) -> tuple[str, str, str]:
        group = equipment_group_by_category[component.category]
        return equipment_palette[group]

    def top_point(x_mm: float, y_mm: float) -> tuple[float, float]:
        return (
            top_origin[0] + x_mm / top_scale,
            top_origin[1] + y_mm / top_scale,
        )

    def side_mass_point(x_mm: float, z_mm: float) -> tuple[float, float]:
        return (
            side_origin[0] + x_mm / side_scale,
            side_origin[1] - z_mm / side_scale,
        )

    def top_box(component: equipment_layout.Component3D) -> tuple[float, ...]:
        minimum, maximum = component.aabb()
        x0, y0 = top_point(minimum[0], minimum[1])
        return x0, y0, (maximum[0] - minimum[0]) / top_scale, (
            maximum[1] - minimum[1]
        ) / top_scale

    def side_box(component: equipment_layout.Component3D) -> tuple[float, ...]:
        minimum, maximum = component.aabb()
        x0, y0 = side_mass_point(minimum[0], maximum[2])
        return x0, y0, (maximum[0] - minimum[0]) / side_scale, (
            maximum[2] - minimum[2]
        ) / side_scale

    top_reference_offsets = {
        "battery_6s1p": (6.0, -7.5),
        "motor": (-4.0, -7.0),
        "prop_adapter": (3.5, 7.0),
        "propeller": (5.0, -5.0),
        "fc": (-8.0, -8.0),
        "pdb": (7.0, 7.0),
        "receiver": (-4.0, -7.0),
        "receiver_antenna": (0.0, -8.0),
        "pitot_sensor": (-5.0, 7.0),
        "buzzer": (6.0, -7.0),
        "o4_camera": (0.0, 7.5),
        "o4_vtx": (-6.0, -7.5),
        "avionics_installation_reserve": (20.0, 11.0),
    }
    side_reference_offsets = {
        "battery_6s1p": (0.0, 8.0),
        "servo_left_406": (-11.0, -15.0),
        "motor": (-8.0, 7.0),
        "prop_adapter": (0.0, -8.0),
        "propeller": (8.0, 0.0),
        "esc": (-17.5, 13.5),
        "fc": (-12.0, -24.0),
        "pdb": (-15.0, 6.5),
        "gps_mag": (-13.0, 10.0),
        "receiver": (-8.0, -15.0),
        "receiver_antenna": (-9.5, -23.0),
        "pitot_sensor": (-14.0, 10.0),
        "pitot_probe_tube": (-17.0, -15.5),
        "buzzer": (5.0, 8.5),
        "o4_camera": (-2.0, 8.0),
        "o4_vtx": (0.0, -8.0),
        "avionics_installation_reserve": (4.0, -24.5),
    }
    side_reference_overrides = {
        "servo_left_406": "E04/05",
    }
    side_projection_duplicates = {"servo_right_406"}

    def draw_mass_reference(
        point: tuple[float, float],
        reference: str,
        prefix: str,
        identifier: str,
        offset: tuple[float, float],
    ) -> None:
        """Draw the true mass centre and a legible offset schedule reference."""
        label_point = (point[0] + offset[0], point[1] + offset[1])
        sheet.circle(
            *point,
            0.55,
            "datum-dot",
            id=f"mass-centre-{prefix}-{identifier}",
        )
        if offset != (0.0, 0.0):
            sheet.line(*point, *label_point, "leader")
        label_width = max(7.0, len(reference) * 1.65)
        sheet.rect(
            label_point[0] - label_width / 2.0,
            label_point[1] - 2.45,
            label_width,
            4.9,
            "medium",
            rx=2.0,
            id=f"mass-reference-{prefix}-{identifier}",
            style="fill:#fffdf8;stroke:#17202a;stroke-width:.3",
        )
        sheet.text(
            label_point[0],
            label_point[1] + 0.82,
            reference,
            "micro",
            "middle",
        )

    sheet = SvgSheet(
        "Salamandra equipment mass skeleton",
        "Metric A3 orthographic mass-skeleton drawing generated from the three-dimensional component ledger. The top view places CLEAN component envelopes and mass centres over the controlled wing planform for spatial context; both views overlay the coupled V1 battery, camera and VTX solution. No fuselage outer mould line, wing construction or manufacturing geometry is defined.",
        "SLM-EQP-001",
    )
    title_block(
        sheet,
        "EQUIPMENT MASS SKELETON",
        "SLM-EQP-001",
        "TOP 1:6.5 · SIDE 1:4",
        "SOURCE: equipment_layout.py · equipment_catalog.py · P42A MAX CAD ENVELOPE",
        title_font_size=3.55,
    )
    sheet.text(
        210,
        249,
        "DRAFT · MASS SKELETON + PLANFORM CONTEXT · NO OML",
        "watermark",
        "middle",
    )

    # Controlled planform context.  It shares the top-view datum and scale with
    # every component, but does not represent wing skin, structure or an OML.
    wing_outline = [
        top_point(x_le(HALF_SPAN) * 1000.0, -HALF_SPAN * 1000.0),
        top_point(x_le(0.0) * 1000.0, 0.0),
        top_point(x_le(HALF_SPAN) * 1000.0, HALF_SPAN * 1000.0),
        top_point(x_te(HALF_SPAN) * 1000.0, HALF_SPAN * 1000.0),
        top_point(x_te(0.0) * 1000.0, 0.0),
        top_point(x_te(HALF_SPAN) * 1000.0, -HALF_SPAN * 1000.0),
    ]
    sheet.polyline(
        wing_outline,
        "outline",
        close=True,
        id="equipment-wing-planform-context",
        style=(
            "fill:#dbe7ee;fill-opacity:.30;stroke:#334a5a;"
            "stroke-width:.48"
        ),
    )
    sheet.polyline(
        [
            top_point(x_c4(HALF_SPAN) * 1000.0, -HALF_SPAN * 1000.0),
            top_point(x_c4(0.0) * 1000.0, 0.0),
            top_point(x_c4(HALF_SPAN) * 1000.0, HALF_SPAN * 1000.0),
        ],
        "derived",
        id="equipment-wing-quarter-chord-context",
        style="fill:none;stroke:#6d8796;stroke-width:.3;stroke-dasharray:5 1.5",
    )
    sheet.leader(
        *top_point(x_le(0.55) * 1000.0, -550.0),
        61,
        57,
        "CONTROLLED WING PLANFORM [D]",
    )

    # Orthographic datums.  Forward is negative x and starboard is positive y.
    sheet.text(18, 20, "A · TOP VIEW · CLEAN", "sheet-subtitle")
    sheet.text(
        18,
        25,
        "x/y ENVELOPES + MASS CENTRES · WING CONTEXT [D]",
        "micro",
    )
    sheet.text(
        18,
        29,
        "BROWN CHAIN = COUPLED V1 BATTERY / CAMERA / VTX SOLUTION",
        "micro",
        style="fill:#7c4b00;font-weight:700",
    )
    sheet.line(*top_point(-485.0, 0.0), *top_point(255.0, 0.0), "centre")
    sheet.line(
        *top_point(0.0, -HALF_SPAN * 1000.0),
        *top_point(0.0, HALF_SPAN * 1000.0),
        "centre",
    )
    sheet.line(52, 31, 29, 31, "medium", marker_end="url(#arrow-end)")
    sheet.text(55, 32, "FORWARD · −x", "label")
    sheet.line(18, 38, 18, 53, "medium", marker_end="url(#arrow-end)")
    sheet.text(21, 49, "STARBOARD · +y", "micro")

    sheet.text(214, 20, "B · SIDE VIEW · CLEAN", "sheet-subtitle")
    sheet.text(214, 25, "x/z ENVELOPES · POSITIVE z UP", "micro")
    sheet.line(*side_mass_point(-485.0, 0.0), *side_mass_point(255.0, 0.0), "centre")
    sheet.line(*side_mass_point(0.0, -115.0), *side_mass_point(0.0, 115.0), "centre")
    sheet.line(244, 31, 221, 31, "medium", marker_end="url(#arrow-end)")
    sheet.text(247, 32, "FORWARD · −x", "label")

    # The complete possible pack region is shown before the actual CLEAN pack.
    battery = clean.component(equipment_layout.PRIMARY_CG_ADJUSTER)
    battery_half = tuple(value / 2.0 for value in battery.size_mm)
    travel_min_x = battery.bounds.minimum_mm[0] - battery_half[0]
    travel_max_x = battery.bounds.maximum_mm[0] + battery_half[0]
    travel_top_start = top_point(travel_min_x, -battery_half[1])
    travel_top_end = top_point(travel_max_x, battery_half[1])
    sheet.rect(
        travel_top_start[0],
        travel_top_start[1],
        travel_top_end[0] - travel_top_start[0],
        travel_top_end[1] - travel_top_start[1],
        "hidden",
        rx=1.0,
        id="battery-travel-top",
        style="fill:none;stroke:#146e9b;stroke-width:.32;stroke-dasharray:5 1 1 1",
    )
    travel_side_start = side_mass_point(
        travel_min_x, battery.position_mm[2] + battery_half[2]
    )
    travel_side_end = side_mass_point(
        travel_max_x, battery.position_mm[2] - battery_half[2]
    )
    sheet.rect(
        travel_side_start[0],
        travel_side_start[1],
        travel_side_end[0] - travel_side_start[0],
        travel_side_end[1] - travel_side_start[1],
        "hidden",
        rx=1.0,
        id="battery-travel-side",
        style="fill:none;stroke:#146e9b;stroke-width:.32;stroke-dasharray:5 1 1 1",
    )

    # Fill colour identifies system function.  Maturity remains independent:
    # estimated/open envelopes keep an amber dashed outline, while measured or
    # controlled envelopes use a solid outline in the system colour.  E## is
    # the component mass centre, so the convention survives monochrome output.
    camera_component = clean.component("o4_camera")
    vtx_component = clean.component("o4_vtx")
    o4_link, o4_distance_mm, o4_link_passed = next(
        result
        for result in clean.link_results()
        if result[0].name.startswith("DJI O4")
    )
    sheet.line(
        *top_point(
            camera_component.position_mm[0], camera_component.position_mm[1]
        ),
        *top_point(vtx_component.position_mm[0], vtx_component.position_mm[1]),
        "provisional-line",
        id="equipment-top-o4-coax-lower-bound",
        style="stroke:#9a4f87;stroke-width:.55;stroke-dasharray:2 1",
    )
    sheet.line(
        *side_mass_point(
            camera_component.position_mm[0], camera_component.position_mm[2]
        ),
        *side_mass_point(vtx_component.position_mm[0], vtx_component.position_mm[2]),
        "provisional-line",
        id="equipment-side-o4-coax-lower-bound",
        style="stroke:#9a4f87;stroke-width:.55;stroke-dasharray:2 1",
    )
    for component in components:
        provisional = (
            "[E]" in component.authority
            or "[I]" in component.authority
            or component.reserve
            or not component.budgeted
        )
        css = "provisional-fill" if provisional else "derived"
        _, system_colour, system_fill = component_palette(component)
        outline_colour = "#a86000" if provisional else system_colour
        style = (
            f"fill:{system_fill};fill-opacity:.72;stroke:{outline_colour};"
            "stroke-width:.48"
        )
        top_rect = top_box(component)
        side_rect = side_box(component)
        sheet.rect(
            *top_rect,
            css,
            rx=0.7,
            id=f"equipment-top-{component.identifier}",
            style=style,
        )
        reference = reference_by_id[component.identifier]
        top_mass_point = top_point(
            component.position_mm[0], component.position_mm[1]
        )
        draw_mass_reference(
            top_mass_point,
            reference,
            "top",
            component.identifier,
            top_reference_offsets.get(component.identifier, (0.0, 0.0)),
        )
        if component.identifier not in side_projection_duplicates:
            sheet.rect(
                *side_rect,
                css,
                rx=0.7,
                id=f"equipment-side-{component.identifier}",
                style=style,
            )
            side_reference = side_reference_overrides.get(
                component.identifier, reference
            )
            side_point_value = side_mass_point(
                component.position_mm[0], component.position_mm[2]
            )
            draw_mass_reference(
                side_point_value,
                side_reference,
                "side",
                component.identifier,
                side_reference_offsets.get(component.identifier, (0.0, 0.0)),
            )

    # V1 is a genuinely coupled result: fin/boom mass drives the battery target;
    # insufficient battery travel extends the forward cradle, which moves the
    # camera and then the VTX just enough to preserve the measured 50 mm coax.
    v1_battery = v1.component(equipment_layout.PRIMARY_CG_ADJUSTER)
    for identifier in ("battery_6s1p", "o4_camera", "o4_vtx"):
        v1_component = v1.component(identifier)
        for prefix, box in (
            ("top", top_box(v1_component)),
            ("side", side_box(v1_component)),
        ):
            sheet.rect(
                *box,
                "provisional-line",
                rx=1.0,
                id=f"v1-coupled-{identifier}-{prefix}",
                style=(
                    "fill:none;stroke:#7c4b00;stroke-width:.7;"
                    "stroke-dasharray:6 1.5 1.2 1.5"
                ),
            )
    v1_camera = v1.component("o4_camera")
    v1_vtx = v1.component("o4_vtx")
    sheet.line(
        *top_point(v1_camera.position_mm[0], v1_camera.position_mm[1]),
        *top_point(v1_vtx.position_mm[0], v1_vtx.position_mm[1]),
        "provisional-line",
        id="v1-coupled-o4-coax-top",
        style="stroke:#7c4b00;stroke-width:.55;stroke-dasharray:2 1",
    )
    sheet.line(
        *side_mass_point(v1_camera.position_mm[0], v1_camera.position_mm[2]),
        *side_mass_point(v1_vtx.position_mm[0], v1_vtx.position_mm[2]),
        "provisional-line",
        id="v1-coupled-o4-coax-side",
        style="stroke:#7c4b00;stroke-width:.55;stroke-dasharray:2 1",
    )

    # CLEAN CG markers are derived from every installed and budgeted component;
    # the lightweight O4 antenna mass is lumped into the E19 VTX assembly.
    clean_cg = clean.cg_mm()
    top_cg = top_point(clean_cg[0], clean_cg[1])
    side_cg = side_mass_point(clean_cg[0], clean_cg[2])
    sheet.leader(
        *top_cg,
        97,
        112,
        f"CLEAN CG ({clean_cg[0]:+.1f}, {clean_cg[1]:+.1f}) [D]",
    )
    sheet.leader(
        *side_cg,
        291,
        43,
        f"CG z {clean_cg[2]:+.1f} [D]",
        anchor="end",
    )
    for prefix, point in (("top", top_cg), ("side", side_cg)):
        sheet.cg_symbol(*point, 2.7, f"clean-cg-{prefix}")

    battery_min_x = top_point(battery.bounds.minimum_mm[0], 0.0)[0]
    battery_max_x = top_point(battery.bounds.maximum_mm[0], 0.0)[0]
    sheet.horizontal_dimension(
        battery_min_x,
        battery_max_x,
        242.0,
        top_origin[1],
        top_origin[1],
        f"BATTERY CG TRAVEL {battery.bounds.axis_span(0):.1f} mm [D]/[E]",
    )
    sheet.leader(
        *top_point(v1_battery.position_mm[0], -battery_half[1]),
        24,
        161,
        f"V1 COUPLED BATTERY x {v1_battery.position_mm[0]:+.1f} [D]/[E]",
        True,
    )

    # Component schedule.  It deliberately includes the unresolved avionics
    # reserve so the visible skeleton closes to the current mass allocation.
    table_left = 214.0
    table_top = 118.0
    sheet.text(table_left, table_top, "COMPONENT MASS / POSITION SCHEDULE", "label")
    sheet.text(215, 124, "REF", "micro")
    sheet.text(228, 124, "COMPONENT", "micro")
    sheet.text(314, 124, "g", "micro", "end")
    sheet.text(334, 124, "x", "micro", "end")
    sheet.text(354, 124, "y", "micro", "end")
    sheet.text(374, 124, "z", "micro", "end")
    sheet.text(405, 124, "STATUS", "micro", "end")
    sheet.line(214, 126, 406, 126, "thin")
    row_y = 130.0
    for component in components:
        reference = reference_by_id[component.identifier]
        status = component.authority
        if component.reserve:
            status += " R"
        if not component.budgeted:
            status += " U"
        _, system_colour, _ = component_palette(component)
        sheet.text(
            215,
            row_y,
            reference,
            "mono",
            style=f"fill:{system_colour};font-weight:700",
        )
        sheet.text(228, row_y, component.identifier, "micro")
        sheet.text(314, row_y, f"{component.mass_g:.2f}", "mono", "end")
        sheet.text(334, row_y, f"{component.position_mm[0]:+.1f}", "mono", "end")
        sheet.text(354, row_y, f"{component.position_mm[1]:+.1f}", "mono", "end")
        sheet.text(374, row_y, f"{component.position_mm[2]:+.1f}", "mono", "end")
        sheet.text(405, row_y, status, "micro", "end")
        row_y += 4.05
    sheet.line(214, row_y - 2.1, 406, row_y - 2.1, "thin")

    shown_mass = sum(component.mass_g for component in components)
    excluded_mass = clean.mass_g() - shown_mass
    sheet.multiline(214, 219, [
        "AUDIT: E01 153.0x65.7x22.6 [M]/[E] · E18 13.44x12.36x16.50 [M].",
        (
            f"E18→E19 COAX: LOWER BOUND {o4_distance_mm:.1f}/"
            f"{o4_link.maximum_mm:.1f} mm [D]/[M] · "
            f"{'PASS' if o4_link_passed else 'FAIL'}; ROUTE/CONNECTOR BENDS OPEN [I]."
        ),
        "E19: VTX 30x30x6 [M] + ANTENNA MASS = 5.85 g [D] · 80 mm ROUTE NOTE · E20 RETIRED.",
        f"SHOWN EQUIPMENT: {shown_mass:.2f} g · CLEAN INSTALLED: {clean.mass_g():.2f} g",
        f"NOT SHOWN: structure, elevons/balances and hardware = {excluded_mass:.2f} g",
        f"BATTERY: CLEAN x {clean_battery_x:+.2f}; V1 required/placed {v1_battery_x:+.2f} mm; CG {v1.cg_mm()[0]:+.2f} mm.",
        f"V1 COUPLING: nose +{v1_packaging.nose_extension_mm:.2f} mm; camera {v1_camera.position_mm[0]:+.2f}; VTX {v1_vtx.position_mm[0]:+.2f}; mass {v1.mass_g():.2f} g.",
        "SERVOS: E04/E05 = 1 PER ELEVON AT y=406.25 mm · E02/E03 RETIRED WITH 4-SERVO CONCEPT.",
        "COLOUR = SYSTEM FUNCTION · SOLID = MEASURED/CONTROLLED · AMBER DASH = OPEN.",
        "R = unresolved reserve · U = outside released budget · dimensions are envelopes.",
        "WING OUTLINE = CONTROLLED PLANFORM CONTEXT [D]; NO SKIN, STRUCTURE, FUSELAGE OR OML.",
    ], "micro", 4.1)
    provenance_legend(sheet, 214, 103)
    sheet.text(282, 99.5, "SYSTEM COLOUR (FILL)", "micro")
    palette_order = (
        "energy",
        "propulsion",
        "power",
        "flight_control",
        "sensors",
        "actuators",
        "fpv_rf",
        "reserve",
    )
    for index, group in enumerate(palette_order):
        row, column = divmod(index, 4)
        x = 282.0 + column * 31.0
        y = 103.0 + row * 5.0
        label, system_colour, system_fill = equipment_palette[group]
        sheet.rect(
            x,
            y - 2.5,
            3.3,
            3.3,
            "medium",
            rx=0.35,
            style=f"fill:{system_fill};stroke:{system_colour};stroke-width:.4",
        )
        sheet.text(x + 4.5, y, label, "micro")
    return sheet


def polyhedral_z(y_m: float) -> float:
    """Piecewise-flat provisional dihedral schedule from Design Guide section 3."""
    if not 0.0 <= y_m <= HALF_SPAN:
        raise ValueError("polyhedral station must be in the right half-span")
    points = (0.0, 0.195, 0.347, 0.498, HALF_SPAN)
    slopes_deg = (0.0, 1.07, 1.53, 2.0)
    z = 0.0
    for index, (a, b) in enumerate(pairwise(points)):
        if y_m <= a:
            break
        run = min(y_m, b) - a
        if run > 0.0:
            from math import radians, tan
            z += run * tan(radians(slopes_deg[index]))
        if y_m <= b:
            break
    return z


def draw_half_wing_layout() -> SvgSheet:
    scale = 2.0
    ox, oy = 47.0, 126.0
    sheet = SvgSheet(
        "Salamandra right half-wing structural layout",
        "Metric A3 plan-view draft of the right half-wing showing the common center module, three printed segments, structural cell boundaries, removable joiner, spar, anti-rotation pin, elevon and a vertically exaggerated polyhedral inset.",
        "SLM-WNG-001",
    )
    title_block(
        sheet,
        "RIGHT HALF-WING · STRUCTURAL LAYOUT",
        "SLM-WNG-001",
        "PLAN 1:2",
        "SOURCE: DESIGN GUIDE v0.22 §§4–6 · ADR-0002/0015/0032/0039/0045",
        title_font_size=3.65,
    )
    sheet.text(210, 146, "DRAFT · NOT A CUTTING OR MANUFACTURING TEMPLATE", "watermark", "middle")

    # Exact local airfoil inset fills the otherwise empty forward-swept corner.
    # It is drawn in local section coordinates; the +0.9 deg station twist is
    # intentionally omitted and called out to avoid mixing coordinate systems.
    section_station = CONTRACT.core_half_span_m
    section_file = ROOT / "geometry" / "airfoils" / "salamandra-r1-y195.dat"
    section = load_airfoil(section_file)
    section_scale = 2.0
    section_chord = chord(section_station) * 1000.0 / section_scale
    section_x0, section_y0 = 24.0, 59.0
    section_points = [
        (section_x0 + x * section_chord, section_y0 - z * section_chord)
        for x, z in section
    ]
    sheet.polyline(section_points, "controlled-fill", close=True)
    sheet.polyline(section_points, "outline", close=True)
    sheet.line(section_x0, section_y0, section_x0 + section_chord, section_y0, "centre")
    for fraction, css in ((CONTRACT.d_box_fraction, "provisional-line"),
                          (CONTRACT.hinge_fraction, "derived")):
        lower, upper = airfoil_limits(section, fraction)
        sx = section_x0 + fraction * section_chord
        sheet.line(sx, section_y0 - lower * section_chord,
                   sx, section_y0 - upper * section_chord, css)
    spar_x = section_x0 + CONTRACT.spar_fraction * section_chord
    sheet.circle(spar_x, section_y0, 0.006 * 1000.0 / section_scale,
                 "provisional-line")
    sheet.text(section_x0, 31.0, "SECTION A–A · y = 195 mm · LOCAL 1:2", "sheet-subtitle")
    sheet.text(section_x0, 35.5,
               "SALAMANDRA r1 y195 [D] · TWIST +0.9° NOT SHOWN", "micro")
    sheet.text(section_x0 + 0.15 * section_chord, 76.0, "D-BOX", "micro", "middle")
    sheet.text(section_x0 + 0.50 * section_chord, 76.0, "CENTER CELL", "micro", "middle")
    sheet.text(section_x0 + 0.86 * section_chord, 76.0, "ELEVON", "micro", "middle")

    intervals = (0.0, 0.195, 0.347, 0.498, HALF_SPAN)
    fills = ("core-fill", "segment-fill-a", "segment-fill-b", "segment-fill-a")
    for index, (a, b) in enumerate(pairwise(intervals)):
        sheet.polyline(half_band(a, b, ox, oy, scale), fills[index], close=True)

    elevon = [
        chord_fraction_point(CONTRACT.elevon_inboard_m, CONTRACT.hinge_fraction, ox, oy, scale),
        chord_fraction_point(CONTRACT.elevon_outboard_m, CONTRACT.hinge_fraction, ox, oy, scale),
        plan_point(x_te(CONTRACT.elevon_outboard_m), CONTRACT.elevon_outboard_m, ox, oy, scale),
        plan_point(x_te(CONTRACT.elevon_inboard_m), CONTRACT.elevon_inboard_m, ox, oy, scale),
    ]
    sheet.polyline(elevon, "elevon-fill", close=True)
    sheet.polyline(half_band(0.0, HALF_SPAN, ox, oy, scale), "outline", close=True)

    # Cell boundaries and station cuts.
    for fraction, css in ((CONTRACT.d_box_fraction, "hidden"),
                          (CONTRACT.hinge_fraction, "derived")):
        y0 = CONTRACT.elevon_inboard_m if fraction == CONTRACT.hinge_fraction else 0.0
        y1 = CONTRACT.elevon_outboard_m if fraction == CONTRACT.hinge_fraction else HALF_SPAN
        sheet.line(*chord_fraction_point(y0, fraction, ox, oy, scale),
                   *chord_fraction_point(y1, fraction, ox, oy, scale), css)
    for station in CONTRACT.segment_joints_m[:-1]:
        sheet.line(*plan_point(x_le(station), station, ox, oy, scale),
                   *plan_point(x_te(station), station, ox, oy, scale), "station")
    # The elevon begins 32.5 mm outboard of the removable joint.  Show this
    # control boundary independently from the structural station chain.
    sheet.line(
        *plan_point(x_le(CONTRACT.elevon_inboard_m), CONTRACT.elevon_inboard_m, ox, oy, scale),
        *plan_point(x_te(CONTRACT.elevon_inboard_m), CONTRACT.elevon_inboard_m, ox, oy, scale),
        "derived",
    )

    # Main carbon tube: inserted socket portion is dashed; bonded panel portion
    # is solid amber because its dimensions remain provisional pending CAD/F2.
    socket_start = CONTRACT.core_half_span_m - CONTRACT.socket_depth_m
    sheet.line(*chord_fraction_point(socket_start, CONTRACT.spar_fraction, ox, oy, scale),
               *chord_fraction_point(CONTRACT.core_half_span_m, CONTRACT.spar_fraction, ox, oy, scale),
               "provisional-line")
    sheet.line(*chord_fraction_point(CONTRACT.core_half_span_m, CONTRACT.spar_fraction, ox, oy, scale),
               *chord_fraction_point(CONTRACT.spar_outboard_m, CONTRACT.spar_fraction, ox, oy, scale),
               "provisional-line", stroke_dasharray="none")

    pin_start = CONTRACT.core_half_span_m - CONTRACT.socket_depth_m
    pin_end = CONTRACT.core_half_span_m + CONTRACT.anti_rotation_bonded_m
    p1_c4 = x_c4(pin_start) + CONTRACT.anti_rotation_offset_m
    p2_c4 = x_c4(pin_end) + CONTRACT.anti_rotation_offset_m
    sheet.line(*plan_point(p1_c4, pin_start, ox, oy, scale),
               *plan_point(p2_c4, pin_end, ox, oy, scale), "provisional-line")

    # Filament dowels at x/c 0.40 and 0.60 on glued joints.
    for station in (0.347, 0.498):
        for fraction in (0.40, 0.60):
            sheet.circle(*chord_fraction_point(station, fraction, ox, oy, scale),
                         1.0, "provisional-line")

    # One fixed elevon servo per half-wing.  The station is imported from the
    # equipment model so this sheet cannot silently retain the retired
    # four-servo concept.  The zone is not a released CAD pocket.
    servo_station = equipment_layout.SERVO_STATION_MM / 1000.0
    point = chord_fraction_point(servo_station, 0.53, ox, oy, scale)
    sheet.rect(point[0] - 4.0, point[1] - 8.5, 8.0, 17.0,
               "provisional-fill", rx=1.0)
    sheet.text(point[0], point[1] + 1.0, "S", "provisional-text", "middle")

    # Principal dimensions and station chain.
    root_le = plan_point(x_le(0.0), 0.0, ox, oy, scale)
    tip_le = plan_point(x_le(HALF_SPAN), HALF_SPAN, ox, oy, scale)
    sheet.horizontal_dimension(root_le[0], tip_le[0], 14.5,
                               root_le[1], tip_le[1], "HALF-SPAN 650 mm [D]")
    root_te = plan_point(x_te(0.0), 0.0, ox, oy, scale)
    sheet.vertical_dimension(29.0, root_le[1], root_te[1], root_le[0], root_te[0],
                             f"{ROOT_CHORD*1000:.1f}", label_left=True)
    tip_te = plan_point(x_te(HALF_SPAN), HALF_SPAN, ox, oy, scale)
    sheet.vertical_dimension(388.0, tip_le[1], tip_te[1], tip_le[0], tip_te[0],
                             f"{TIP_CHORD*1000:.1f}", label_left=False)
    elevon_inboard_hinge = chord_fraction_point(
        CONTRACT.elevon_inboard_m, CONTRACT.hinge_fraction, ox, oy, scale
    )
    elevon_outboard_hinge = chord_fraction_point(
        CONTRACT.elevon_outboard_m, CONTRACT.hinge_fraction, ox, oy, scale
    )
    sheet.horizontal_dimension(
        elevon_inboard_hinge[0],
        elevon_outboard_hinge[0],
        91.5,
        elevon_inboard_hinge[1],
        elevon_outboard_hinge[1],
        "ELEVON 357.5 mm [D]",
        label_above=True,
    )

    chain_y = 247.0
    chain_points = [plan_point(0.235, value, ox, oy, scale)[0] for value in intervals]
    labels = ("195", "152", "151", "152")
    for index, (x1, x2) in enumerate(pairwise(chain_points)):
        sheet.horizontal_dimension(x1, x2, chain_y,
                                   plan_point(x_te(intervals[index]), intervals[index], ox, oy, scale)[1],
                                   plan_point(x_te(intervals[index + 1]), intervals[index + 1], ox, oy, scale)[1],
                                   labels[index], label_above=True)

    # Compact annotations in the clear area aft of the swept trailing edge.
    sheet.leader(*chord_fraction_point(0.46, CONTRACT.d_box_fraction, ox, oy, scale),
                 279, 177, "D-BOX WEB · 0.30 c · PROVISIONAL", True)
    sheet.leader(*chord_fraction_point(0.50, CONTRACT.hinge_fraction, ox, oy, scale),
                 314, 152, f"HINGE · {ELEVON_HINGE_XC:.2f} c", False)
    sheet.leader(
        *plan_point(x_te(0.21125), 0.21125, ox, oy, scale),
        166,
        207,
        "FIXED TE BRIDGE · y195–227.5 · 32.5 mm",
        True,
    )
    sheet.leader(*chord_fraction_point(0.52, CONTRACT.spar_fraction, ox, oy, scale),
                 293, 119, "CFRP Ø12×1 · c/4 · PROVISIONAL", True)
    sheet.leader(*plan_point(x_c4(0.20) + CONTRACT.anti_rotation_offset_m, 0.20, ox, oy, scale),
                 131, 211, "PIN Ø6 · 65 mm AFT · PROVISIONAL", True)
    sheet.text(72, 219, "CORE", "label", "middle")
    sheet.text(181, 196, "SEGMENT 1", "note", "middle")
    sheet.text(257, 163, "SEGMENT 2", "note", "middle")
    sheet.text(333, 128, "SEGMENT 3", "note", "middle")
    sheet.text(212, 112, "REMOVABLE", "micro", "middle", rotate=-90)
    sheet.text(286, 114, "GLUED", "micro", "middle", rotate=-90)
    sheet.text(362, 103, "GLUED", "micro", "middle", rotate=-90)

    # Front-elevation inset.  Vertical geometry is exaggerated eightfold so the
    # 12 mm tip rise remains inspectable on an A3 print.
    inset_x0, inset_y0 = 206.0, 242.0
    h_scale, z_exaggeration = 4.0, 8.0
    stations = (0.0, 0.195, 0.347, 0.498, HALF_SPAN)
    front_points = [
        (inset_x0 + y * 1000.0 / h_scale,
         inset_y0 - polyhedral_z(y) * 1000.0 / h_scale * z_exaggeration)
        for y in stations
    ]
    sheet.line(inset_x0, inset_y0, inset_x0 + 168, inset_y0, "centre")
    sheet.polyline(front_points, "provisional-line")
    for x, y in front_points:
        sheet.circle(x, y, 0.8, "provisional-dot")
    sheet.text(inset_x0, 214.5, "FRONT ELEVATION INSET · H 1:4 · Z ×8", "sheet-subtitle")
    sheet.text(inset_x0, 219.0,
               f"POLYHEDRAL 0 / 1.07 / 1.53 / 2.00° · TIP RISE {polyhedral_z(HALF_SPAN)*1000:.1f} mm [E]",
               "micro")

    provenance_legend(sheet, 303, 24)
    sheet.text(14, 243, "SPAN CHAIN [mm] · CORE / P1 / P2 / P3", "micro")
    return sheet


def validate_contract() -> dict[str, bool]:
    segment_spans = [
        (b - a) * 1000.0
        for a, b in zip((0.0,) + CONTRACT.segment_joints_m[:-1], CONTRACT.segment_joints_m)
    ]
    fin_area = fin_area_for_target(0.0005)
    fin = fin_geometry(fin_area)
    equipment_clean, _ = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("clean")
    )
    equipment_v1_packaging = equipment_layout.solve_v1_packaging()
    equipment_v1 = equipment_v1_packaging.layout
    equipment_v1_required_x = equipment_v1_packaging.required_battery_x_mm
    equipment_components = tuple(
        equipment_clean.component(identifier)
        for identifier in MASS_SKELETON_COMPONENT_IDS
    )
    equipment_ids = set(MASS_SKELETON_COMPONENT_IDS)
    equipment_battery = equipment_clean.component(
        equipment_layout.PRIMARY_CG_ADJUSTER
    )
    fuselage_model = fuselage_geometry.reference_model()
    fuselage_audits = fuselage_geometry.audit_envelopes(fuselage_model)
    checks = {
        "canonical geometry validation passes": all(validate_geometry().values()),
        "retired equipment references are not reused": not (
            set(RETIRED_MASS_SKELETON_REFERENCES)
            & set(MASS_SKELETON_REFERENCE_BY_ID.values())
        ),
        "drawing half-span matches design contract": abs(CONTRACT.segment_joints_m[-1] - HALF_SPAN) < 1e-12,
        "equipment top scale fits the complete 1300 mm span in 200 mm": abs(
            2.0 * HALF_SPAN * 1000.0 / CONTRACT.equipment_top_scale - 200.0
        ) < 1e-12,
        "CORE join is at 30 percent half-span": abs(CONTRACT.core_half_span_m / HALF_SPAN - 0.30) < 1e-12,
        "panel segment spans are 152/151/152 mm": all(
            abs(actual - expected) < 1e-9
            for actual, expected in zip(segment_spans[1:], (152.0, 151.0, 152.0))
        ),
        "elevon is a 357.5 mm PANEL component": abs(
            (CONTRACT.elevon_outboard_m - CONTRACT.elevon_inboard_m) * 1000.0 - 357.5
        ) < 1e-9,
        # Both of these were tautologies over hardcoded literals: the first
        # reduced algebraically to abs(STATIC_MARGIN - 0.08), the second
        # compared two constants.  The live derivation is checked here instead.
        "target CG preserves the released static margin": abs(
            (np_vlm() - cg_target()) / MAC - STATIC_MARGIN
        ) < 1e-12,
        "derived neutral point reproduces its published anchor": abs(
            np_vlm() - aero_contract.NP_VLM_PUBLISHED
        ) <= aero_contract.NP_ANCHOR_TOLERANCE,
        "independent NP methods agree within the declared spread": abs(
            np_vlm() - np_weissinger()
        ) <= aero_contract.NP_METHOD_TOLERANCE,
        "provisional polyhedral tip rise is about 12 mm": 0.0115 < polyhedral_z(HALF_SPAN) < 0.0128,
        "released y195 airfoil coordinates are available": len(load_airfoil(
            ROOT / "geometry" / "airfoils" / "salamandra-r1-y195.dat"
        )) >= 20,
        "released root airfoil coordinates are available": len(load_airfoil(
            ROOT / "geometry" / "airfoils" / "salamandra-root-r1.dat"
        )) >= 20,
        "generated twin fins reproduce total area, per-fin AR, taper, sweep and AC": (
            abs(fin.span_m**2 / fin.area_each_m2 - AR_FIN) < 1e-12
            and abs(
                0.5 * (fin.root_chord_m + fin.tip_chord_m) * fin.span_m
                - fin.area_each_m2
            ) < 1e-12
            and abs(fin.fin_count * fin.area_each_m2 - fin.area_m2) < 1e-12
            and fin.fin_count == FIN_COUNT
            and abs(fin.tip_chord_m / fin.root_chord_m - FIN_TAPER) < 1e-12
            and abs(fin.quarter_chord_sweep_deg - FIN_SWEEP_DEG) < 1e-12
            and abs(fin.ac_x_m - FIN_AC_STATION_M) < 1e-12
            and fin.tip_te_x_m > fin.root_te_x_m
        ),
        "twin booms remain radially outside the propeller disk": (
            fin.boom_inner_prop_clearance_m >= 0.025
        ),
        "aft root supports begin at the CORE trailing edge and end behind the root": (
            abs(fin.boom_x_start_m - x_te(fin.lateral_station_m)) < 1e-3
            and fin.root_le_x_m < fin.boom_x_start_m < fin.root_te_x_m
            and fin.boom_x_end_m >= fin.root_te_x_m + 0.009
        ),
        "fin section declares the spar as an external LE nose": (
            FIN_SPAR_SEAT_DIAMETER_M > FIN_ROOT_THICKNESS_M
            and FIN_SPAR_DIAMETER_M <= FIN_ROOT_THICKNESS_M
            and FIN_TIP_THICKNESS_M < FIN_SPAR_DIAMETER_M
        ),
        "fin independent-corner power-off screen is no more favourable than power-on": (
            cnb_total_band(fin_area, ETA_FIN_POWER_OFF)[0]
            <= cnb_total_band(fin_area, ETA_FIN_POWER_ON)[0]
        ),
        "propeller skid datum preserves 10 mm ground clearance": abs(
            -CONTRACT.rear_pod_lower_prop_m
            - PROP_DIAMETER_M / 2.0
            - 0.010
        ) < 1e-12,
        "side cradle envelope clears the maximum-dimension P42A pack": (
            CONTRACT.cradle_inner_width_m - CONTRACT.pack_width_m >= 0.002
            and CONTRACT.cradle_inner_height_m - CONTRACT.pack_height_m >= 0.002
        ),
        "equipment-layout numerical validation passes": all(
            equipment_layout.validation_checks().values()
        ),
        "connected aircraft-scene and propeller-clearance validation passes": all(
            aircraft_scene.validation_checks().values()
        ),
        "equipment skeleton component references are unique": (
            len(MASS_SKELETON_COMPONENT_IDS) == len(equipment_ids)
            and set(MASS_SKELETON_REFERENCE_BY_ID) == set(equipment_ids)
            and len(set(MASS_SKELETON_REFERENCE_BY_ID.values()))
            == len(MASS_SKELETON_REFERENCE_BY_ID)
        ),
        "equipment skeleton contains the primary installed systems": {
            "battery_6s1p",
            "motor",
            "fc",
            "pdb",
            "esc",
            "o4_camera",
            "o4_vtx",
            "servo_right_406",
        } <= equipment_ids,
        "drawing and equipment model use one fixed servo per half-wing": (
            sum(component.category == "actuator" for component in equipment_components) == 2
            and {
                abs(component.position_mm[1])
                for component in equipment_components
                if component.category == "actuator"
            } == {equipment_layout.SERVO_STATION_MM}
        ),
        "equipment skeleton excludes airframe and control-surface masses": all(
            component.category not in {"structure", "stability", "control"}
            for component in equipment_components
        ),
        "equipment skeleton shown mass reproduces the current ledger": abs(
            sum(component.mass_g for component in equipment_components) - 821.85
        ) < 1e-9,
        "CLEAN and coupled V1 pack stations remain inside their physical travel": (
            equipment_battery.bounds.contains(
                equipment_clean.component(
                    equipment_layout.PRIMARY_CG_ADJUSTER
                ).position_mm
            )
            and equipment_v1.component(
                equipment_layout.PRIMARY_CG_ADJUSTER
            ).bounds.contains(
                equipment_v1.component(
                    equipment_layout.PRIMARY_CG_ADJUSTER
                ).position_mm
            )
        ),
        "equipment skeleton consumes the converged V1 packaging solution": (
            abs(
                equipment_v1_required_x
                - equipment_v1.component(
                    equipment_layout.PRIMARY_CG_ADJUSTER
                ).position_mm[0]
            ) < 1e-6
            and equipment_v1_packaging.nose_extension_mm >= 0.0
        ),
        "fuselage generator analytical validation passes": all(
            fuselage_geometry.validation_checks().values()
        ),
        "fuselage review covers every body-owned envelope": (
            {audit.identifier for audit in fuselage_audits}
            == set(fuselage_contract.BODY_ENVELOPE_COMPONENT_IDS)
        ),
        "fuselage review envelope audits pass": all(
            audit.passed for audit in fuselage_audits
        ),
    }
    return checks


def validate_svg(source: str, filename: str, drawing_number: str) -> dict[str, bool]:
    """Validate the portable, static subset used by the drawing masters."""
    root = ET.fromstring(source)
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    labels = " ".join(element.text or "" for element in root.findall(".//svg:text", namespace))
    elements = list(root.iter())
    ids = [element.attrib["id"] for element in elements if "id" in element.attrib]
    id_set = set(ids)
    aria_ids = root.attrib.get("aria-labelledby", "").split()
    url_references = re.findall(r"url\(\s*['\"]?([^'\")\s]+)", source)
    fragment_references = {value[1:] for value in url_references if value.startswith("#")}
    hrefs = [
        value
        for element in elements
        for key, value in element.attrib.items()
        if key.rsplit("}", 1)[-1] == "href"
    ]
    active_tags = {"script", "foreignObject", "iframe", "object", "embed", "audio", "video", "image"}
    event_attributes = [
        key
        for element in elements
        for key in element.attrib
        if key.rsplit("}", 1)[-1].lower().startswith("on")
    ]
    title_element = root.find("svg:title", namespace)
    description_element = root.find("svg:desc", namespace)
    metadata = root.find("svg:metadata", namespace)
    checks = {
        f"{filename}: XML parses": root.tag.endswith("svg"),
        f"{filename}: physical A3 size": root.attrib.get("width") == "420mm" and root.attrib.get("height") == "297mm",
        f"{filename}: metric viewBox": root.attrib.get("viewBox") == "0 0 420 297",
        f"{filename}: accessible title and description": (
            title_element is not None
            and title_element.attrib.get("id") == "svg-title"
            and bool((title_element.text or "").strip())
            and description_element is not None
            and description_element.attrib.get("id") == "svg-desc"
            and bool((description_element.text or "").strip())
            and aria_ids == ["svg-title", "svg-desc"]
            and all(reference in id_set for reference in aria_ids)
            and root.attrib.get("role") == "img"
        ),
        f"{filename}: IDs are unique": len(ids) == len(id_set),
        f"{filename}: fragment references resolve": fragment_references <= id_set,
        f"{filename}: no external references": (
            all(value.startswith("#") for value in hrefs)
            and all(value.startswith("#") for value in url_references)
        ),
        f"{filename}: no active or embedded content": (
            not event_attributes
            and not any(element.tag.rsplit("}", 1)[-1] in active_tags for element in elements)
            and "@import" not in source.lower()
            and "<!doctype" not in source.lower()
            and "<!entity" not in source.lower()
        ),
        f"{filename}: generator provenance present": (
            metadata is not None
            and "calculations/generate_blueprints.py" in (metadata.text or "")
            and drawing_number in (metadata.text or "")
        ),
        f"{filename}: drawing number present": drawing_number in source,
        f"{filename}: manufacture warning present": "NOT FOR MANUFACTURE" in labels or "NOT A CUTTING" in labels,
        f"{filename}: provisional style present": "PROVISIONAL" in labels,
    }
    if drawing_number == "SLM-GA-001":
        cg_group = next(
            (element for element in elements if element.attrib.get("id") == "cg-target-general-arrangement"),
            None,
        )
        checks[f"{filename}: conventional quartered CG symbol present"] = (
            cg_group is not None
            and sum(child.tag.endswith("path") for child in cg_group) == 2
        )
    if drawing_number == "SLM-EQP-001":
        element_by_id = {
            element.attrib.get("id"): element
            for element in elements
            if element.attrib.get("id")
        }
        cg_groups = {
            element.attrib.get("id"): element
            for element in elements
            if element.attrib.get("id") in {"clean-cg-top", "clean-cg-side"}
        }
        checks[f"{filename}: top and side use quartered CG symbols"] = (
            len(cg_groups) == 2
            and all(
                sum(child.tag.endswith("path") for child in group) == 2
                for group in cg_groups.values()
            )
        )
        checks[f"{filename}: controlled wing planform context is present"] = (
            element_by_id.get("equipment-wing-planform-context") is not None
            and element_by_id["equipment-wing-planform-context"].tag.endswith(
                "polygon"
            )
            and element_by_id.get("equipment-wing-quarter-chord-context")
            is not None
        )
        checks[f"{filename}: mixed orthographic scales are declared"] = (
            "TOP 1:6.5 · SIDE 1:4" in labels
        )
        checks[f"{filename}: functional colour legend is complete"] = all(
            label in labels
            for label in (
                "ENERGY",
                "PROPULSION",
                "POWER",
                "FLIGHT CTRL",
                "SENSORS",
                "ACTUATORS",
                "FPV / RF",
                "RESERVE",
            )
        )
    if drawing_number == "SLM-FUS-001":
        element_by_id = {
            element.attrib.get("id"): element
            for element in elements
            if element.attrib.get("id")
        }
        body_ids = set(fuselage_contract.BODY_ENVELOPE_COMPONENT_IDS)
        checks[f"{filename}: common-source plan and side OML are present"] = {
            "fuselage-oml-plan",
            "fuselage-oml-side",
        } <= element_by_id.keys()
        checks[f"{filename}: every body envelope is shown in both projections"] = all(
            f"fuselage-envelope-plan-{identifier}" in element_by_id
            and f"fuselage-envelope-side-{identifier}" in element_by_id
            for identifier in body_ids
        )
        checks[f"{filename}: five analytical transverse sections are shown"] = sum(
            identifier.startswith("fuselage-section-")
            for identifier in element_by_id
        ) == 5
        checks[f"{filename}: open aircraft gates remain explicit"] = (
            "feasible=FALSE" in source
            and "OPEN PROJECT GATES" in source
            and "NOT A PRINTABLE SHELL" in source
        )
    if drawing_number == "SLM-FIN-001":
        element_by_id = {
            element.attrib.get("id"): element
            for element in elements
            if element.attrib.get("id")
        }
        checks[f"{filename}: single-source fin planform and AC are present"] = {
            "fin-v1a-planform",
            "fin-quarter-chord-line",
            "fin-aerodynamic-centre",
        } <= element_by_id.keys()
        checks[f"{filename}: external LE spar and root interface are explicit"] = {
            "fin-leading-edge-spar",
            "fin-root-interface-envelope",
        } <= element_by_id.keys()
        checks[f"{filename}: fixed-fin and no-rudder authority is explicit"] = (
            "NO HINGE / SERVO" in labels
            and "The fixed fins are not rudders" in source
            and "No enclosed Ø3.2 bore is claimed" in source
        )
        checks[f"{filename}: powered and motor-off Cnβ bands are both scheduled"] = (
            "Cnβ ON" in labels and "Cnβ OFF" in labels
        )
    return checks


def build_drawings() -> tuple[DrawingOutput, ...]:
    """Render every drawing in memory without mutating the workspace."""
    drawings = (
        ("SLM-GA-001-general-arrangement.svg", "SLM-GA-001", draw_general_arrangement()),
        ("SLM-GA-002-side-elevations.svg", "SLM-GA-002", draw_side_elevations()),
        ("SLM-FIN-001-fixed-fin-review.svg", "SLM-FIN-001", draw_fin_detail()),
        (
            "SLM-FUS-001-fuselage-oml-review.svg",
            "SLM-FUS-001",
            draw_fuselage_oml_review(),
        ),
        (
            "SLM-EQP-001-equipment-mass-skeleton.svg",
            "SLM-EQP-001",
            draw_equipment_mass_skeleton(),
        ),
        ("SLM-WNG-001-half-wing-layout.svg", "SLM-WNG-001", draw_half_wing_layout()),
    )
    return tuple(
        DrawingOutput(OUTPUT_DIR / filename, drawing_number, drawing.render())
        for filename, drawing_number, drawing in drawings
    )


def write_drawings(outputs: tuple[DrawingOutput, ...]) -> None:
    """Write a previously rendered set using stable UTF-8/LF serialization."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for output in outputs:
        output.path.write_text(output.source, encoding="utf-8", newline="\n")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Generate metric A3 Salamandra SVG drawing drafts")
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate XML/contract and fail on a stale drawing without modifying files",
    )
    args = parser.parse_args()

    outputs = build_drawings()
    if not args.check:
        write_drawings(outputs)

    checks = validate_contract()
    # The sheets are only half of the artifact: README, drawing index and wiki
    # manifest are republished from the same run so no published surface can
    # silently describe an older drawing set.
    checks["drawing set: published sheets match the drawing index"] = {
        output.path.name for output in outputs
    } == {spec.filename for spec in drawing_index.SHEETS}
    checks.update(drawing_index.sync(write=not args.check))
    for output in outputs:
        checks[f"{output.path.name}: generated file is current"] = (
            output.path.exists()
            and output.path.read_text(encoding="utf-8") == output.source
        )
        checks.update(validate_svg(output.source, output.path.name, output.drawing_number))

    print("=" * 86)
    print("SALAMANDRA SVG DRAWING SET · A3 METRIC · REV P0")
    print("=" * 86)
    action = "CHECKED" if args.check else "WROTE"
    for output in outputs:
        print(f"  {action} {output.path.relative_to(ROOT)}")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if args.check and not all(checks.values()):
        raise SystemExit(1)
    if not all(checks.values()):
        raise SystemExit("drawing validation failed")
    print("\nVALIDATION: ALL PASS")


if __name__ == "__main__":
    main()
