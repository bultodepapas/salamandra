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
from pathlib import Path

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
    cradle_inner_width_m: float = 0.066
    cradle_wall_m: float = 0.0012
    camera_station_m: float = -0.393
    motor_body_forward_m: float = 0.195
    motor_mount_m: float = 0.230
    prop_plane_m: float = 0.235
    prop_diameter_m: float = 0.2032
    rear_pod_end_m: float = 0.265


CONTRACT = DrawingContract()


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
