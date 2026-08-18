#!/usr/bin/env python3
"""Generate the controlled Salamandra draft drawing set as metric A3 SVG files.

The drawings are communication artifacts, not manufacturing authority.  Exact
planform geometry is imported from ``design_config.py``; balance stations are
imported from ``balance_cg.py``.  Geometry that is still a CAD assumption is
drawn in amber with a dashed line and is labelled PROVISIONAL.

Run from any directory::

    python calculations/generate_blueprints.py
    python calculations/generate_blueprints.py --check

The SVG viewport is 420 x 297 and the physical size is 420 mm x 297 mm.  Thus
one SVG user unit is one millimetre on the A3 sheet when printed at 100 %.
"""
from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import escape
from itertools import pairwise
from math import sqrt
from pathlib import Path

import equipment_layout
from balance_cg import CG_TARGET, NP_VLM, NP_WL, solve_reference_layout
from design_config import (
    ASPECT_RATIO,
    HALF_SPAN,
    MAC,
    ROOT_CHORD,
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
from yaw_stability import fin_area_for_target, fin_geometry

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
    elevon_inboard_m: float = 0.195
    elevon_outboard_m: float = 0.585
    hinge_fraction: float = 0.72
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
    cradle_inner_length_m: float = 0.155
    cradle_inner_width_m: float = 0.066
    cradle_inner_height_m: float = 0.024
    cradle_wall_m: float = 0.0012
    camera_station_m: float = -0.393
    motor_body_forward_m: float = 0.195
    motor_mount_m: float = 0.230
    prop_plane_m: float = 0.235
    prop_diameter_m: float = 0.2032
    rear_pod_end_m: float = 0.265
    rear_pod_lower_prop_m: float = -0.1116
    rear_pod_v1_end_m: float = 0.295
    motor_diameter_m: float = 0.028
    fin_ac_m: float = 0.285
    fin_aspect_ratio: float = 3.0
    fin_root_thickness_m: float = 0.003


CONTRACT = DrawingContract()

MASS_SKELETON_COMPONENT_IDS = (
    "battery_6s1p",
    "servo_left_195",
    "servo_right_195",
    "servo_left_390",
    "servo_right_390",
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
    "o4_antenna",
    "avionics_installation_reserve",
)


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
        "SOURCE: DESIGN GUIDE v0.21 · ADR-0040/0043 · I-21 · generate_blueprints.py",
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
    cradle_fwd = layout["bay_fwd"]
    cradle_aft = cradle_fwd + CONTRACT.cradle_length_m
    cradle_outer_half = (
        CONTRACT.cradle_inner_width_m + 2.0 * CONTRACT.cradle_wall_m
    ) / 2.0

    def body_point(x_m: float, y_m: float) -> str:
        x_svg, y_svg = plan_point(x_m, y_m, ox, oy, scale)
        return f"{fmt(x_svg)} {fmt(y_svg)}"

    def body_curve(
        control_1: tuple[float, float],
        control_2: tuple[float, float],
        end: tuple[float, float],
    ) -> str:
        return (
            f"C {body_point(*control_1)} {body_point(*control_2)} "
            f"{body_point(*end)}"
        )

    body_path = " ".join([
        f"M {body_point(cradle_fwd, 0.0)}",
        body_curve(
            (cradle_fwd + 0.006, 0.021),
            (cradle_fwd + 0.015, cradle_outer_half),
            (cradle_fwd + 0.026, cradle_outer_half),
        ),
        body_curve(
            (cradle_fwd + 0.075, cradle_outer_half),
            (cradle_aft - 0.030, cradle_outer_half),
            (cradle_aft, 0.030),
        ),
        body_curve(
            (cradle_aft + 0.050, 0.029),
            (CONTRACT.nose_support_m - 0.040, 0.026),
            (CONTRACT.nose_support_m, 0.026),
        ),
        body_curve((-0.050, 0.028), (0.090, 0.042), (0.170, 0.042)),
        body_curve(
            (0.205, 0.042),
            (0.248, 0.032),
            (CONTRACT.rear_pod_end_m, 0.024),
        ),
        body_curve(
            (CONTRACT.rear_pod_end_m + 0.010, 0.016),
            (CONTRACT.rear_pod_end_m + 0.010, -0.016),
            (CONTRACT.rear_pod_end_m, -0.024),
        ),
        body_curve((0.248, -0.032), (0.205, -0.042), (0.170, -0.042)),
        body_curve(
            (0.090, -0.042),
            (-0.050, -0.028),
            (CONTRACT.nose_support_m, -0.026),
        ),
        body_curve(
            (CONTRACT.nose_support_m - 0.040, -0.026),
            (cradle_aft + 0.050, -0.029),
            (cradle_aft, -0.030),
        ),
        body_curve(
            (cradle_aft - 0.030, -cradle_outer_half),
            (cradle_fwd + 0.075, -cradle_outer_half),
            (cradle_fwd + 0.026, -cradle_outer_half),
        ),
        body_curve(
            (cradle_fwd + 0.015, -cradle_outer_half),
            (cradle_fwd + 0.006, -0.021),
            (cradle_fwd, 0.0),
        ),
        "Z",
    ])
    sheet.path(
        body_path,
        "provisional-fill",
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
    pack_station = layout["pack_station"]
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
    prop_left = plan_point(CONTRACT.prop_plane_m, -CONTRACT.prop_diameter_m / 2.0, ox, oy, scale)
    prop_right = plan_point(CONTRACT.prop_plane_m, CONTRACT.prop_diameter_m / 2.0, ox, oy, scale)
    sheet.line(*prop_left, *prop_right, "provisional-line")
    sheet.circle(*plan_point(CONTRACT.prop_plane_m, 0.0, ox, oy, scale), 1.4, "provisional-line")

    # CG and independent NP datums.  The separation is intentionally visible.
    for station, css, label, x_shift in (
        (CG_TARGET, "derived-fill", f"CG {CG_TARGET*1000:+.1f}", -23.0),
        (NP_VLM, "derived", f"NP VLM {NP_VLM*1000:+.1f}", 23.0),
    ):
        sx, sy = plan_point(station, 0.0, ox, oy, scale)
        if css == "derived-fill":
            sheet.path(f"M {fmt(sx)} {fmt(sy-2.3)} l -2.2 4 h 4 z", css)
        else:
            sheet.circle(sx, sy, 1.8, css)
            sheet.line(sx - 2.7, sy, sx + 2.7, sy, css)
            sheet.line(sx, sy - 2.7, sx, sy + 2.7, css)
        sheet.leader(sx, sy, sx + x_shift, sy - 8.5, label)

    camera = plan_point(CONTRACT.camera_station_m, 0.0, ox, oy, scale)
    sheet.circle(*camera, 1.7, "provisional-line")
    sheet.path(
        f"M {fmt(camera[0]-1.2)} {fmt(camera[1]-1.2)} L {fmt(camera[0]+1.2)} {fmt(camera[1]+1.2)} "
        f"M {fmt(camera[0]+1.2)} {fmt(camera[1]-1.2)} L {fmt(camera[0]-1.2)} {fmt(camera[1]+1.2)}",
        "provisional-line",
    )

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
    sheet.leader(*camera, 185, 52, "CAMERA x −393 · PROVISIONAL", True, "end")
    sheet.leader(*plan_point(pack_station, 0.033, ox, oy, scale), 239, 73,
                 f"6S1P PACK x {pack_station*1000:+.1f} [D]/[E]", True)
    sheet.leader(*plan_point(-0.180, -0.028, ox, oy, scale), 164, 86,
                 "FUSELAGE OML · PROVISIONAL [I]", True, "end")
    sheet.leader(*plan_point(CONTRACT.prop_plane_m, 0.1016, ox, oy, scale), 265, 229,
                 "APC 8×8 DISK x +235 · PROVISIONAL", True)
    sheet.leader(*chord_fraction_point(0.44, CONTRACT.hinge_fraction, ox, oy, scale),
                 335, 206, "ELEVON · HINGE 0.72 c", False)
    provenance_legend(sheet, 302, 24)
    sheet.multiline(18, 239, [
        "DATUM: root c/4, x aft, y starboard.",
        f"S {S:.3f} m² · AR {ASPECT_RATIO:.2f} · taper {TAPER:.2f} · MAC {MAC*1000:.1f} mm.",
        f"NP independent check: {NP_WL*1000:+.1f} mm (Weissinger-L).",
    ], "micro", 3.4)
    return sheet


def draw_side_elevations() -> SvgSheet:
    """Draw the shared side OML and the CLEAN/V1a directional variants."""
    scale = 4.0
    origin_x = 175.0
    layout = solve_reference_layout()
    cradle_fwd = layout["bay_fwd"]
    cradle_aft = cradle_fwd + CONTRACT.cradle_length_m
    pack_station = layout["pack_station"]
    pack_fwd = pack_station - CONTRACT.cradle_inner_length_m / 2.0
    pack_aft = pack_station + CONTRACT.cradle_inner_length_m / 2.0
    pack_z_min = 0.004
    pack_z_max = pack_z_min + CONTRACT.cradle_inner_height_m

    root_section = load_airfoil(
        ROOT / "geometry" / "airfoils" / "salamandra-root-r1.dat"
    )
    fin_area = fin_area_for_target(0.0005)
    fin_span = sqrt(fin_area * CONTRACT.fin_aspect_ratio)
    fin_root_chord, fin_tip_chord, fin_centroid_z = fin_geometry(
        fin_area, fin_span
    )
    # Place the provisional trapezoid so its quarter-chord at the area-centroid
    # height is x=+285 mm.  A vertical TE gives a buildable, swept-LE concept and
    # exposes the minimum aft carrier length instead of floating the fin in space.
    centroid_fraction = fin_centroid_z / fin_span
    centroid_chord = (
        fin_root_chord
        + (fin_tip_chord - fin_root_chord) * centroid_fraction
    )
    fin_te = CONTRACT.fin_ac_m + 0.75 * centroid_chord
    fin_root_le = fin_te - fin_root_chord
    fin_tip_le = fin_te - fin_tip_chord
    fin_root_z = 0.014  # Carrier/fin vertical interface remains an OP-21 CAD choice [I].

    sheet = SvgSheet(
        "Salamandra CLEAN and V1a side elevations",
        "Metric A3 side-elevation draft comparing the common root airfoil, battery boom, continuous provisional fuselage OML and local propeller-clearance skid for SALAMANDRA-CLEAN with the V1a fixed centreline-fin variant. The V1a fin is passive and has no movable rudder.",
        "SLM-GA-002",
    )
    title_block(
        sheet,
        "SIDE ELEVATIONS · CLEAN / V1a",
        "SLM-GA-002",
        "1:4",
        "SOURCE: GUIDE §§4.4/6.7/9.2 · ADR-0038 · I-16/I-20",
    )
    def draw_variant(origin_y: float, *, with_fin: bool) -> None:
        def point(x_m: float, z_m: float) -> str:
            x_svg, y_svg = side_point(x_m, z_m, origin_x, origin_y, scale)
            return f"{fmt(x_svg)} {fmt(y_svg)}"

        def curve(
            control_1: tuple[float, float],
            control_2: tuple[float, float],
            end: tuple[float, float],
        ) -> str:
            return (
                f"C {point(*control_1)} {point(*control_2)} "
                f"{point(*end)}"
            )

        body_path = " ".join([
            f"M {point(cradle_fwd, 0.0)}",
            curve(
                (cradle_fwd + 0.005, 0.016),
                (cradle_fwd + 0.014, 0.032),
                (cradle_fwd + 0.030, 0.032),
            ),
            curve(
                (cradle_fwd + 0.075, 0.032),
                (cradle_aft - 0.035, 0.032),
                (cradle_aft, 0.029),
            ),
            curve(
                (cradle_aft + 0.050, 0.025),
                (CONTRACT.nose_support_m - 0.040, 0.012),
                (CONTRACT.nose_support_m, 0.012),
            ),
            curve((-0.105, 0.016), (-0.080, 0.019), (-0.060, 0.020)),
            curve((-0.020, 0.026), (0.085, 0.030), (0.160, 0.026)),
            curve((0.195, 0.024), (0.235, 0.022), (0.255, 0.019)),
            curve((0.265, 0.016), (0.270, 0.006), (0.265, 0.0)),
            curve((0.270, -0.008), (0.265, -0.015), (0.255, -0.017)),
            curve((0.230, -0.022), (0.195, -0.027), (0.160, -0.030)),
            curve((0.085, -0.032), (0.000, -0.030), (-0.060, -0.018)),
            curve(
                (-0.090, -0.012),
                (CONTRACT.nose_support_m - 0.025, -0.010),
                (CONTRACT.nose_support_m, -0.010),
            ),
            curve(
                (CONTRACT.nose_support_m - 0.050, -0.008),
                (cradle_aft + 0.045, -0.006),
                (cradle_aft, -0.006),
            ),
            curve(
                (cradle_aft - 0.040, -0.006),
                (cradle_fwd + 0.040, -0.006),
                (cradle_fwd, 0.0),
            ),
            "Z",
        ])
        sheet.path(
            body_path,
            "provisional-fill",
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
        sheet.path(body_path, "provisional-line", style="stroke-width:.62;fill:none")

        # Internal packaging: Ø8 boom, 155 x 24 mm cradle envelope and Ø28 motor.
        boom_top_left = side_point(cradle_fwd, 0.004, origin_x, origin_y, scale)
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
        pack_top_left = side_point(pack_fwd, pack_z_max, origin_x, origin_y, scale)
        pack_bottom_right = side_point(pack_aft, pack_z_min, origin_x, origin_y, scale)
        sheet.rect(
            pack_top_left[0],
            pack_top_left[1],
            pack_bottom_right[0] - pack_top_left[0],
            pack_bottom_right[1] - pack_top_left[1],
            "provisional-line",
            rx=1.0,
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

        prop_top = side_point(
            CONTRACT.prop_plane_m,
            CONTRACT.prop_diameter_m / 2.0,
            origin_x,
            origin_y,
            scale,
        )
        prop_bottom = side_point(
            CONTRACT.prop_plane_m,
            -CONTRACT.prop_diameter_m / 2.0,
            origin_x,
            origin_y,
            scale,
        )
        sheet.line(*prop_top, *prop_bottom, "provisional-line")
        sheet.circle(
            *side_point(CONTRACT.prop_plane_m, 0.0, origin_x, origin_y, scale),
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
                (CONTRACT.prop_plane_m, CONTRACT.rear_pod_lower_prop_m),
            ),
        ])
        sheet.path(
            skid_path,
            "provisional-line",
            style="fill:none;stroke-width:1.05;stroke-linecap:round",
        )
        sheet.line(
            *side_point(CONTRACT.prop_plane_m - 0.006,
                        CONTRACT.rear_pod_lower_prop_m, origin_x, origin_y, scale),
            *side_point(CONTRACT.prop_plane_m + 0.020,
                        CONTRACT.rear_pod_lower_prop_m, origin_x, origin_y, scale),
            "provisional-line",
            stroke_dasharray="none",
        )

        carrier_end = fin_te if with_fin else CONTRACT.rear_pod_end_m
        sheet.line(
            *side_point(cradle_fwd - 0.015, 0.0, origin_x, origin_y, scale),
            *side_point(carrier_end + 0.015, 0.0, origin_x, origin_y, scale),
            "centre",
        )
        sheet.line(
            *side_point(0.0, 0.045, origin_x, origin_y, scale),
            *side_point(0.0, -0.125, origin_x, origin_y, scale),
            "station",
        )

        if with_fin:
            carrier_start = CONTRACT.prop_plane_m + 0.009
            carrier_path = " ".join([
                f"M {point(carrier_start, fin_root_z)}",
                f"L {point(fin_te, fin_root_z)}",
                curve(
                    (fin_te + 0.006, 0.010),
                    (fin_te + 0.006, -0.010),
                    (fin_te, -fin_root_z),
                ),
                f"L {point(carrier_start, -fin_root_z)}",
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
            sheet.line(fin_points[0][0], fin_points[0][1], fin_points[1][0],
                       fin_points[1][1], "provisional-line", stroke_dasharray="none")
            fin_ac = side_point(
                CONTRACT.fin_ac_m,
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
                f"b_v {fin_span*1000:.0f} [D]",
            )
            sheet.leader(*fin_ac, 300, 140, "FIN AC x +285 [D]/[E]")

        camera = side_point(
            CONTRACT.camera_station_m, 0.018, origin_x, origin_y, scale
        )
        sheet.circle(*camera, 1.2, "provisional-line")
        sheet.line(
            *side_point(CONTRACT.camera_station_m, 0.036, origin_x, origin_y, scale),
            *side_point(CONTRACT.camera_station_m, -0.012, origin_x, origin_y, scale),
            "station",
        )

    draw_variant(73.0, with_fin=False)
    draw_variant(185.0, with_fin=True)

    sheet.text(20, 23, "A · SALAMANDRA-CLEAN", "sheet-subtitle")
    sheet.text(20, 28, "FINLESS · O1 EFFICIENCY BASELINE · YAW RISK [E]", "micro")
    sheet.text(20, 126, "B · SALAMANDRA-V1a", "sheet-subtitle")
    sheet.text(20, 131, "FIXED CENTRELINE FIN · NO MOVABLE RUDDER", "micro")
    sheet.line(51, 38, 32, 38, "medium", marker_end="url(#arrow-end)")
    sheet.text(54, 39, "FORWARD", "label")

    sheet.leader(
        *side_point(pack_station, pack_z_max, origin_x, 73.0, scale),
        108,
        49,
        "6S1P ENVELOPE 155 × 24 [D]/[E]",
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
        *side_point(CONTRACT.prop_plane_m, CONTRACT.prop_diameter_m / 2.0,
                    origin_x, 73.0, scale),
        292,
        55,
        "APC 8×8 · Ø203 · x +235 [D]/[I]",
        True,
    )
    sheet.leader(
        *side_point(CONTRACT.prop_plane_m, CONTRACT.rear_pod_lower_prop_m,
                    origin_x, 185.0, scale),
        298,
        225,
        "LOCAL SKID z −111.6 · PROP CLEARANCE 10 [I]",
        True,
    )
    sheet.leader(
        *side_point(fin_te, 0.0, origin_x, 185.0, scale),
        300,
        198,
        f"V1a CARRIER TO x +{fin_te*1000:.0f} [D]/[I]",
        True,
    )
    sheet.leader(
        *side_point(fin_root_le + 0.62 * fin_root_chord,
                    fin_root_z + 0.55 * fin_span, origin_x, 185.0, scale),
        300,
        153,
        "V1a FIXED FIN · NO HINGE / SERVO",
        True,
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
    sheet.multiline(18, 235, [
        "DATUM: root c/4 x = 0; motor axis z = 0; positive z up.",
        "Shared [D]/[E]: root r1, Ø8 boom/socket, pack envelope, Ø28 motor and V1a fin sizing.",
        "Side OML, equipment vertical placement, local skid and V1a carrier interface remain [I].",
        f"CAD OPEN: fin AC placement requires carrier to x +{fin_te*1000:.0f}; the guide's x +295 concept is insufficient.",
    ], "micro", 3.4)
    return sheet


def draw_equipment_mass_skeleton() -> SvgSheet:
    """Draw the equipment-only mass skeleton from the 3D component ledger."""
    scale = 4.0
    top_origin = (137.0, 137.0)
    side_origin = (330.0, 73.0)
    clean, clean_battery_x = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("clean")
    )
    v1, v1_battery_x = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("v1"), clamp=True
    )
    components = tuple(
        clean.component(identifier) for identifier in MASS_SKELETON_COMPONENT_IDS
    )
    reference_by_id = {
        component.identifier: f"E{index:02d}"
        for index, component in enumerate(components, start=1)
    }

    def top_point(x_mm: float, y_mm: float) -> tuple[float, float]:
        return (
            top_origin[0] + x_mm / scale,
            top_origin[1] + y_mm / scale,
        )

    def side_mass_point(x_mm: float, z_mm: float) -> tuple[float, float]:
        return (
            side_origin[0] + x_mm / scale,
            side_origin[1] - z_mm / scale,
        )

    def top_box(component: equipment_layout.Component3D) -> tuple[float, ...]:
        minimum, maximum = component.aabb()
        x0, y0 = top_point(minimum[0], minimum[1])
        return x0, y0, (maximum[0] - minimum[0]) / scale, (
            maximum[1] - minimum[1]
        ) / scale

    def side_box(component: equipment_layout.Component3D) -> tuple[float, ...]:
        minimum, maximum = component.aabb()
        x0, y0 = side_mass_point(minimum[0], maximum[2])
        return x0, y0, (maximum[0] - minimum[0]) / scale, (
            maximum[2] - minimum[2]
        ) / scale

    top_reference_offsets = {
        "motor": (-4.0, -7.0),
        "prop_adapter": (3.5, 7.0),
        "propeller": (5.0, -5.0),
        "fc": (-8.0, -8.0),
        "pdb": (7.0, 7.0),
        "receiver": (-4.0, -7.0),
        "receiver_antenna": (0.0, -8.0),
        "pitot_sensor": (-5.0, 7.0),
        "buzzer": (6.0, -7.0),
        "avionics_installation_reserve": (20.0, 11.0),
    }
    side_reference_offsets = {
        "battery_6s1p": (0.0, 8.0),
        "servo_left_195": (4.0, -24.0),
        "servo_left_390": (-11.0, -15.0),
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
        "o4_antenna": (5.0, -11.0),
        "avionics_installation_reserve": (4.0, -24.5),
    }
    side_reference_overrides = {
        "servo_left_195": "E02/03",
        "servo_left_390": "E04/05",
    }
    side_projection_duplicates = {"servo_right_195", "servo_right_390"}

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
        "Metric A3 equipment-only orthographic drawing generated from the three-dimensional component ledger. It shows CLEAN component envelopes and mass centres, the battery travel and V1 battery-stop overlay, without an airframe, outer mould line or manufacturing geometry.",
        "SLM-EQP-001",
    )
    title_block(
        sheet,
        "EQUIPMENT MASS SKELETON",
        "SLM-EQP-001",
        "TOP / SIDE 1:4",
        "SOURCE: equipment_layout.py · mass_budget.py · P42A MAX CAD ENVELOPE",
        title_font_size=3.55,
    )
    sheet.text(
        210,
        249,
        "DRAFT · EQUIPMENT ONLY · NO AIRFRAME / OML",
        "watermark",
        "middle",
    )

    # Orthographic datums.  Forward is negative x and starboard is positive y.
    sheet.text(18, 20, "A · TOP VIEW · CLEAN", "sheet-subtitle")
    sheet.text(18, 25, "x/y ENVELOPES + COMPONENT MASS CENTRES", "micro")
    sheet.line(*top_point(-485.0, 0.0), *top_point(255.0, 0.0), "centre")
    sheet.line(*top_point(0.0, -420.0), *top_point(0.0, 420.0), "centre")
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

    # Component envelopes are status-coded.  Any estimated input remains
    # amber/dashed; measured envelopes are solid blue.  E## is the mass centre.
    for component in components:
        provisional = (
            "[E]" in component.authority
            or "[I]" in component.authority
            or component.reserve
            or not component.budgeted
        )
        css = "provisional-fill" if provisional else "derived"
        style = None if provisional else (
            "fill:#dcecf4;fill-opacity:.58;stroke:#146e9b;stroke-width:.45"
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

    # V1 uses the same equipment but drives the battery to the forward stop.
    v1_battery = v1.component(equipment_layout.PRIMARY_CG_ADJUSTER)
    for prefix, box in (("top", top_box(v1_battery)), ("side", side_box(v1_battery))):
        sheet.rect(
            *box,
            "provisional-line",
            rx=1.0,
            id=f"v1-battery-stop-{prefix}",
            style=(
                "fill:none;stroke:#7c4b00;stroke-width:.7;"
                "stroke-dasharray:6 1.5 1.2 1.5"
            ),
        )

    # CLEAN CG markers are derived from every installed component, including
    # the small unbudgeted O4 antenna mass.
    clean_cg = clean.cg_mm()
    top_cg = top_point(clean_cg[0], clean_cg[1])
    side_cg = side_mass_point(clean_cg[0], clean_cg[2])
    for prefix, point in (("top", top_cg), ("side", side_cg)):
        sheet.path(
            f"M {fmt(point[0])} {fmt(point[1]-3.2)} l -3 5.4 h 6 z",
            "derived-fill",
            id=f"clean-cg-{prefix}",
        )
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
        "V1 BATTERY AT FORWARD STOP",
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
        sheet.text(215, row_y, reference, "mono")
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
        f"SHOWN EQUIPMENT: {shown_mass:.2f} g · CLEAN INSTALLED: {clean.mass_g():.2f} g",
        f"NOT SHOWN: structure, elevons/balances and hardware = {excluded_mass:.2f} g",
        f"BATTERY: CLEAN x {clean_battery_x:+.2f}; V1 required {v1_battery_x:+.2f}, placed {v1_battery.position_mm[0]:+.2f} mm.",
        "R = unresolved reserve · U = outside released budget · dimensions are envelopes.",
        "NO FUSELAGE, WING SKIN, FAIRING OR MANUFACTURING SURFACE IS DEFINED HERE.",
    ], "micro", 4.1)
    provenance_legend(sheet, 214, 103)
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
        "SOURCE: DESIGN GUIDE v0.21 §§4–6 · ADR-0002/0015/0032/0039",
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

    # Servo positions are zones, deliberately not dimensioned as CAD pockets.
    for station in (0.235, 0.390):
        point = chord_fraction_point(station, 0.53, ox, oy, scale)
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
                 314, 152, "HINGE · 0.72 c", False)
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
    fin_span = sqrt(fin_area * CONTRACT.fin_aspect_ratio)
    fin_root_chord, fin_tip_chord, _ = fin_geometry(fin_area, fin_span)
    equipment_clean, _ = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("clean")
    )
    equipment_v1, equipment_v1_required_x = equipment_layout.solve_battery_x(
        equipment_layout.reference_layout("v1"), clamp=True
    )
    equipment_components = tuple(
        equipment_clean.component(identifier)
        for identifier in MASS_SKELETON_COMPONENT_IDS
    )
    equipment_ids = set(MASS_SKELETON_COMPONENT_IDS)
    equipment_battery = equipment_clean.component(
        equipment_layout.PRIMARY_CG_ADJUSTER
    )
    return {
        "canonical geometry validation passes": all(validate_geometry().values()),
        "drawing half-span matches design contract": abs(CONTRACT.segment_joints_m[-1] - HALF_SPAN) < 1e-12,
        "CORE join is at 30 percent half-span": abs(CONTRACT.core_half_span_m / HALF_SPAN - 0.30) < 1e-12,
        "panel segment spans are 152/151/152 mm": all(
            abs(actual - expected) < 1e-9
            for actual, expected in zip(segment_spans[1:], (152.0, 151.0, 152.0))
        ),
        "elevon is a 390 mm PANEL component": abs(
            (CONTRACT.elevon_outboard_m - CONTRACT.elevon_inboard_m) * 1000.0 - 390.0
        ) < 1e-9,
        "target CG preserves 8 percent MAC margin": abs(
            (NP_VLM - CG_TARGET) / MAC - 0.08
        ) < 1e-12,
        "independent NP methods agree within 5 mm": abs(NP_VLM - NP_WL) < 0.005,
        "provisional polyhedral tip rise is about 12 mm": 0.0115 < polyhedral_z(HALF_SPAN) < 0.0128,
        "released y195 airfoil coordinates are available": len(load_airfoil(
            ROOT / "geometry" / "airfoils" / "salamandra-r1-y195.dat"
        )) >= 20,
        "released root airfoil coordinates are available": len(load_airfoil(
            ROOT / "geometry" / "airfoils" / "salamandra-root-r1.dat"
        )) >= 20,
        "V1a fin geometry reproduces I-20": (
            abs(fin_area * 100.0 - 2.13) < 0.01
            and abs(fin_span * 1000.0 - 253.0) < 1.0
            and abs(fin_root_chord * 1000.0 - 105.0) < 1.0
            and abs(fin_tip_chord * 1000.0 - 63.0) < 1.0
        ),
        "propeller skid datum preserves 10 mm ground clearance": abs(
            -CONTRACT.rear_pod_lower_prop_m
            - CONTRACT.prop_diameter_m / 2.0
            - 0.010
        ) < 1e-12,
        "side cradle envelope contains the declared 24 mm height": (
            CONTRACT.cradle_inner_height_m >= 0.024
        ),
        "equipment-layout numerical validation passes": all(
            equipment_layout.validation_checks().values()
        ),
        "equipment skeleton component references are unique": (
            len(MASS_SKELETON_COMPONENT_IDS) == len(equipment_ids)
        ),
        "equipment skeleton contains the primary installed systems": {
            "battery_6s1p",
            "motor",
            "fc",
            "pdb",
            "esc",
            "o4_camera",
            "o4_vtx",
            "servo_left_195",
            "servo_right_390",
        } <= equipment_ids,
        "equipment skeleton excludes airframe and control-surface masses": all(
            component.category not in {"structure", "stability", "control"}
            for component in equipment_components
        ),
        "equipment skeleton shown mass reproduces the current ledger": abs(
            sum(component.mass_g for component in equipment_components) - 846.85
        ) < 1e-9,
        "CLEAN and V1 pack stations remain inside physical battery travel": (
            equipment_battery.bounds.contains(
                equipment_clean.component(
                    equipment_layout.PRIMARY_CG_ADJUSTER
                ).position_mm
            )
            and equipment_battery.bounds.contains(
                equipment_v1.component(
                    equipment_layout.PRIMARY_CG_ADJUSTER
                ).position_mm
            )
        ),
        "equipment skeleton exposes unreachable exact V1 battery station": (
            equipment_v1_required_x < equipment_battery.bounds.minimum_mm[0]
        ),
    }


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
    return {
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


def build_drawings() -> tuple[DrawingOutput, ...]:
    """Render every drawing in memory without mutating the workspace."""
    drawings = (
        ("SLM-GA-001-general-arrangement.svg", "SLM-GA-001", draw_general_arrangement()),
        ("SLM-GA-002-side-elevations.svg", "SLM-GA-002", draw_side_elevations()),
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
