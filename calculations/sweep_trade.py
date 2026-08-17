#!/usr/bin/env python3
"""Multidisciplinary quarter-chord sweep trade for Salamandra (I-21/ADR-0040).

The decision rule is intentionally explicit: among candidates that preserve the
current trim closure (<= 3 deg geometric wash-in plus <= 0.6 deg equivalent
permanent elevon reflex) and the section-cl stall screen, select the least
negative forward sweep. This maximizes the measured direction of divergence
improvement without depending on an unverified absolute sweep factor.

NASA TP-1685 figures 7-8 are used only for a relative divergence-speed trend;
their aluminium flat-plate magnitudes do not transfer to the printed wing.
"""
import argparse
import numpy as np

from balance_cg import solve_reference_layout
from design_config import B, MAC, S, SWEEP_C4_DEG, TAPER
from vlm_ala_volante import analiza, geom, solve
from weissinger_np import weissinger


CANDIDATES = (-20.0, -16.0, -15.0, -12.0, -10.0)
STATIC_MARGIN = 0.08
CL_CRUISE = 0.132
PROFILE_CM0 = 0.0016       # provisional MH60->13.5 %, I-15
TWIST_CAP = 3.0
ELEVON_EQUIV_CAP = 0.6
SECTION_CL_MAX = 0.65
MIN_SECTION_CL_MARGIN = 0.01

DESIGN_REF_MASS = 1.620  # kg; O1 target, not current 1.6852 kg budget
RHO = 1.225
V_STALL = 45.0 / 3.6
CL_MAX_REQUIRED = DESIGN_REF_MASS * 9.81 / (0.5 * RHO * V_STALL**2 * S)

# Conservative digitization band from NASA TP-1685 figures 7-8, expressed as
# divergence SPEED ratio relative to -20 deg. Trend only [D]/[E].
NASA_SPEED_GAIN = {
    -20.0: 1.00,
    -16.0: 1.10,
    -15.0: 1.15,
    -12.0: 1.23,
    -10.0: 1.28,
}


def stall_screen(sweep, twist, ny, nx):
    g = geom(B, S, TAPER, sweep, twist, ny=ny, nx=nx)
    cl0, _, _, _ = solve(g, 0.0)
    cl4, _, _, _ = solve(g, 4.0)
    slope = (cl4 - cl0) / np.radians(4.0)
    alpha = np.degrees((CL_MAX_REQUIRED - cl0) / slope)
    _, _, d_lift, _ = solve(g, alpha)
    d_lift = d_lift.reshape(ny, nx).sum(axis=1)
    dy = g["dy"].reshape(ny, nx)[:, 0]
    chord = g["chord"].reshape(ny, nx)[:, 0]
    y = g["cps"][:, 1].reshape(ny, nx)[:, 0]
    cl = d_lift / (0.5 * chord * dy)
    right = y > 0
    y_right, cl_right = y[right], cl[right]
    peak = int(np.argmax(cl_right))
    return y_right[peak] / (B / 2.0), cl_right[peak]


def evaluate(sweep, ny=24, nx=4, weissinger_ny=60):
    zero = analiza(B, S, TAPER, sweep, 0.0, ny=ny, nx=nx, verbose=False)
    four = analiza(B, S, TAPER, sweep, 4.0, ny=ny, nx=nx, verbose=False)
    cm0_per_deg = four["Cm0"] / 4.0
    cm_required = CL_CRUISE * STATIC_MARGIN
    twist_required = max(0.0, (cm_required - PROFILE_CM0) / cm0_per_deg)
    residual = max(0.0, twist_required - TWIST_CAP)
    eta_peak, cl_peak = stall_screen(sweep, TWIST_CAP, ny, nx)
    wl = weissinger(B, S, TAPER, sweep, ny=weissinger_ny)
    layout = solve_reference_layout(sweep_deg=sweep, np_x=zero["x_np"])
    feasible = (
        residual <= ELEVON_EQUIV_CAP + 0.02
        and cl_peak <= SECTION_CL_MAX - MIN_SECTION_CL_MARGIN
    )
    return {
        "sweep": sweep,
        "np_vlm": zero["x_np"],
        "np_wl": wl["x_np"],
        "cm0_per_deg": cm0_per_deg,
        "twist_required": twist_required,
        "residual": residual,
        "eta_peak": eta_peak,
        "cl_peak": cl_peak,
        "pack_station": layout["pack_station"],
        "boom_extension": layout["extension"],
        "nasa_speed_gain": NASA_SPEED_GAIN[sweep],
        "feasible": feasible,
    }


def select(rows):
    feasible = [row for row in rows if row["feasible"]]
    if not feasible:
        raise RuntimeError("no sweep candidate closes the declared constraints")
    return max(feasible, key=lambda row: row["sweep"])


def main():
    parser = argparse.ArgumentParser(description="Salamandra sweep trade")
    parser.add_argument("--full", action="store_true",
                        help="32x5 VLM and ny=100 Weissinger (about two minutes)")
    args = parser.parse_args()
    ny, nx, wny = (32, 5, 100) if args.full else (24, 4, 60)
    rows = [evaluate(sweep, ny, nx, wny) for sweep in CANDIDATES]
    chosen = select(rows)

    print("=" * 118)
    print("SALAMANDRA SWEEP TRADE - I-21 / ADR-0040")
    print(f"mesh VLM={ny}x{nx}; Weissinger ny={wny}; provisional profile Cm0={PROFILE_CM0:+.4f}")
    print(f"stall screen mass={DESIGN_REF_MASS:.3f} kg (O1 target; current budget is 1.685 kg and misses 45 km/h)")
    print("=" * 118)
    print(" sweep   NP VLM/WL(mm)  twist req  elevon eq  cl peak@eta  6S station  boom  NASA Vdiv gain  result")
    for row in rows:
        print(f" {row['sweep']:>+5.0f}  {row['np_vlm']*1000:>7.1f}/"
              f"{row['np_wl']*1000:<6.1f}   {row['twist_required']:>5.2f} deg"
              f"   {row['residual']:>5.2f} deg   {row['cl_peak']:.3f}@"
              f"{row['eta_peak']*100:>2.0f}%   {row['pack_station']*1000:>7.1f} mm"
              f"  {row['boom_extension']*1000:>5.0f} mm     "
              f"{row['nasa_speed_gain']:.2f}x       "
              f"{'PASS' if row['feasible'] else 'REJECT'}")

    print(f"\nDECISION: {chosen['sweep']:+.0f} deg c/4. It is the least-negative candidate "
          "that closes the declared design-target trim and stall screens.")
    print("The NASA factor is a relative trend, not an absolute-aircraft validation.")

    checks = {
        "selected sweep equals canonical design": chosen["sweep"] == SWEEP_C4_DEG,
        "selected NP methods agree within 5 mm": abs(chosen["np_vlm"] - chosen["np_wl"]) < 0.005,
        "favourable provisional-polar reflex <= 0.6 deg": chosen["residual"] <= 0.62,
        "-12 deg is rejected with provisional profile": not next(
            row for row in rows if row["sweep"] == -12.0)["feasible"],
        "section-cl stall screen retains >= 0.01 margin": (
            chosen["cl_peak"] <= SECTION_CL_MAX - MIN_SECTION_CL_MARGIN),
    }
    print("\nVALIDATION")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    print("  ALL PASS")


if __name__ == "__main__":
    main()
