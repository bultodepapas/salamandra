# 12 — Calculation system: audit and remediation plan

**Status:** proposed · **Scope:** the 29 Python modules in `calculations/` and the CI that
guards them · **Audit date:** 2026-08-18 · **Auditor role:** senior engineering review
(numerics, physics, software contract) · **Confidence of findings:** every claim below is
`[M]` — measured by executing the code in this repository — unless tagged otherwise.

---

## 0. How this audit was performed

Environment used for every measurement in this document:

| Item | Value |
|---|---|
| Python | 3.12.3 (Linux x86-64) |
| numpy | 1.26.4 |
| Repository state | `2e749ec`, working tree clean |
| Commands | every `*.py` executed as a CLI; `verify_calculations.py`; targeted harnesses driving the public functions directly |

The audit answers four questions, in this order:

1. **Does it run?** Reproducibility on a clean machine.
2. **Is it one system?** Does every module read shared quantities from one place.
3. **Can the verification fail?** Does a broken contract actually turn a check red.
4. **Is the physics and the numerics right, and is it efficient?**

The architecture passes a test that many repositories fail: the import graph is a
**clean, acyclic, 8-level DAG** with `design_config.py` at the root and
`verify_calculations.py` at the leaf. That foundation is correct and this plan does not
propose replacing it. What follows is what sits on top of it and does not yet honour it.

---

## 1. Verdict

> **The calculation system is well-conceived and materially unsynchronised.**
> A published, safety-critical quantity — the neutral point that sets the CG target — is a
> frozen literal that no test compares against the solver that produced it. Two modules
> carry a different value for the same yaw inertia (factor 1.76). The design wash-in is
> declared independently in five places. Several validation checks are algebraic
> tautologies that cannot fail. And on a clean POSIX machine the verification harness dies
> before printing its first check.

Severity ledger:

| ID | Class | Count | Meaning |
|---|---|---:|---|
| **S1** | Reproducibility broken | 4 | The published commands do not run as documented |
| **S2** | Contract desynchronisation | 12 | Two sources for one physical quantity |
| **S3** | Non-discriminating verification | 9 | A check that cannot turn red |
| **S4** | Numerics / efficiency / hygiene | 10 | Correct answer, wrong cost or fragile construction |
| **S5** | Physics model gaps | 4 | Declared model omits a term or a validity envelope |

The three failure modes this repository already documented in `CLAUDE.md` are all present
in the code itself: **#3 failing to re-derive downstream** (S2-1, S2-3), **#8 tests that
do not discriminate** (all of S3), and **#2 false precision** (S2-2).

---

## PART A — S1: The system does not reproduce

### S1-1 · `np.trapezoid` requires numpy ≥ 2.0; the documentation declares numpy 1.2x

**Evidence.** On numpy 1.26.4, `python3 verify_calculations.py` aborts with

```
AttributeError: module 'numpy' has no attribute 'trapezoid'
  servo_torque.py:67  in control_geometry
```

before a single check is printed. `np.trapezoid` was added in numpy 2.0; the alias in
numpy 1.x is `np.trapz`. Call sites: [servo_torque.py:67](../calculations/servo_torque.py#L67),
[servo_torque.py:69](../calculations/servo_torque.py#L69),
[elevon_sizing.py:93](../calculations/elevon_sizing.py#L93),
[elevon_sizing.py:94](../calculations/elevon_sizing.py#L94).

`calculations/README.md` line 20 declares **numpy 1.2x**. There is no `requirements.txt`,
no `pyproject.toml`, no version floor asserted anywhere in the repository. CI runs
`pip install --upgrade pip numpy`, unpinned, so it silently receives numpy 2.x and never
observes the failure a contributor following the README will hit on the first command.

**Why it matters.** The repository's entire proposition is that a stranger can rerun the
numbers. The published first command does not run on the published dependency set.

**Fix.**

1. Add `calculations/requirements.txt` with an explicit floor and ceiling:
   `numpy>=2.0,<3.0`.
2. Correct `calculations/README.md` to state Python ≥ 3.10 and numpy ≥ 2.0.
3. Add a runtime guard in `design_config.py` — the module everything imports — that raises
   a named, actionable error on an unsupported numpy, rather than an `AttributeError`
   three modules deep.
4. Pin CI: `pip install -r calculations/requirements.txt`.

**Acceptance.** A CI job on a matrix of `{3.10, 3.12}` × `{numpy floor, numpy latest}`
runs `verify_calculations.py --all-scripts` green.

---

### S1-2 · Windows path separators make `divergence.py` unrunnable on POSIX

**Evidence.** [divergence.py:71](../calculations/divergence.py#L71):

```python
PROFILE_FILE = r"geometry\airfoils\salamandra-root-r1.dat"
```

consumed by `os.path.join(os.path.dirname(__file__), "..", PROFILE_FILE)`. On Linux this
resolves to a literal filename containing backslashes:

```
FileNotFoundError: /home/.../calculations/../geometry\airfoils\salamandra-root-r1.dat
```

`divergence.py` exits 1, and the harness check
`airfoil: divergence uses the released Salamandra r1 root` reports **FAIL**. Confirmed:
replacing the separators with `/` makes `divergence.py` run to completion and the harness
turn green.

**Fix.** Use `pathlib` throughout. Establish one module-level anchor in `design_config.py`:

```python
REPO_ROOT = Path(__file__).resolve().parent.parent
AIRFOIL_DIR = REPO_ROOT / "geometry" / "airfoils"
```

and have every consumer (`divergence`, `airfoil_reflex_trade`, `b3_screening`,
`equipment_layout`, `generate_blueprints`, `verify_calculations`) resolve data files
through it. Ban raw string paths with separators in a lint rule.

**Acceptance.** `grep -rn '\\\\' calculations/*.py` returns no path literal, and the audit
runs green on Linux, macOS and Windows.

---

### S1-3 · A contract breach crashes the harness instead of reporting a failed check

**Evidence.** `contract_checks()` builds ~80 checks in one 284-line function with no
per-check isolation. Perturbing `design_config.ARTICLE_CLEAN_MASS_KG` by 5 % — exactly the
kind of change this harness exists to police — produces:

```
RuntimeError: mass-budget default no longer matches design_config
  equipment_layout.py:612 in _mass_rows
```

Zero checks are printed. The contributor sees a traceback, not a diagnosis. The same
happens for S1-1 and S1-2 style faults.

**Why it matters.** A verification harness whose failure mode is an opaque traceback
teaches contributors to distrust it and skip it.

**Fix.**

1. Restructure `contract_checks()` into a registry of small check functions
   (`@contract("mass: CLEAN budget equals shared contract")`), each executed inside a
   `try/except Exception` that converts an exception into a **failed check carrying the
   exception text**, never an abort.
2. Split the registry into topic modules (`checks/geometry.py`, `checks/mass.py`,
   `checks/aero.py`, `checks/structure.py`, `checks/power.py`) so a 284-line function does
   not grow to 500.
3. Guarantee that the harness always prints a complete PASS/FAIL table and always exits
   with the correct code.

**Acceptance.** With any single shared constant deliberately corrupted, the harness prints
the full table, marks the affected checks FAIL, marks the rest PASS, and exits 1.

---

### S1-4 · CI does not run the physics contract at all

**Evidence.** `.github/workflows/docs.yml` runs exactly one
Python step:

```yaml
- run: python calculations/generate_blueprints.py --check
```

It never runs `verify_calculations.py`. It never runs `--all-scripts`. It never runs any
module's own validation case. The workflow is named *Deploy wiki* and is gated on `paths:`
filters — so a pull request touching only `calculations/**` triggers it, but the only
thing it proves is that the drawings are not stale.

**Consequence.** Every S1, S2 and S3 defect in this document is invisible to CI today.
`divergence.py` has been unrunnable on Linux and CI has stayed green.

**Fix.** Add a separate, required workflow `calculations.yml`:

```yaml
jobs:
  contracts:
    strategy:
      matrix: {python: ['3.10','3.12'], numpy: ['floor','latest']}
    steps:
      - run: python calculations/verify_calculations.py --all-scripts
      - run: python calculations/generate_blueprints.py --check
      - run: python calculations/drawing_index.py --check
```

Mark it a required status check on `main`. Keep the drawing check in both places; it is
cheap and it guards a different artefact.

**Acceptance.** A PR that changes `SWEEP_C4_DEG` without re-deriving downstream is blocked
by CI, not by a reviewer's memory.

---

## PART B — S2: One quantity, two sources

This is the heart of what the review was asked for: *does everything connect, does every
variable synchronise with every other*. Today, twelve quantities do not.

### S2-1 · **[CRITICAL]** The neutral point is a frozen literal, and nothing re-derives it

**Evidence.** [balance_cg.py:26-28](../calculations/balance_cg.py#L26-L28):

```python
NP_VLM = -75.8e-3       # m, VLM 40x6, I-21 [D]
NP_WL  = -72.9e-3       # m, Weissinger-L ny=100, I-21 [D]
CG_TARGET = NP_VLM - STATIC_MARGIN * MAC
```

`CG_TARGET` is the single most consequential number in the aircraft. It propagates to
`equipment_layout.TARGET_CG_MM`, `yaw_stability.CG`, the battery solve, the drawing set
and the published Design Guide. **It is a hand-copied constant.** If anyone changes `B`,
`S`, `TAPER` or `SWEEP_C4_DEG` in `design_config.py`, the VLM neutral point moves and
`NP_VLM` does not. Nothing in `verify_calculations.py` compares `balance_cg.NP_VLM` with a
live `vlm_ala_volante.analiza(...)` result.

The only NP check that exists — `stability: independent NP methods agree within 5 mm` —
compares **two live solvers to each other** at yet another mesh, and never touches the
literal that actually drives the CG.

This is `CLAUDE.md` failure mode **#3 (failing to re-derive downstream, the most repeated
correction in the project)** written directly into the source.

**Fix.**

1. Delete the literals. Replace with a **cached derivation** in a new module
   `aero_contract.py` (layer 2, below `balance_cg`):

   ```python
   @cache
   def neutral_point_vlm() -> float:      # m, from root c/4
       return analiza(B, S, TAPER, SWEEP_C4_DEG, DESIGN_TWIST_DEG,
                      ny=VLM_NY, nx=VLM_NX, verbose=False)["x_np"]
   ```

2. Keep a **published reference value with an explicit tolerance** as the regression
   guard, not as the source:

   ```python
   NP_VLM_PUBLISHED = -75.8e-3   # I-21, ADR-0040 — regression anchor only
   NP_VLM_TOLERANCE =  0.5e-3    # re-derivation must land inside this
   ```

3. Add the contract check that is missing today:
   `abs(neutral_point_vlm() - NP_VLM_PUBLISHED) <= NP_VLM_TOLERANCE`.

**Acceptance.** Changing `SWEEP_C4_DEG` by 1° turns the NP check red and states the new
value, forcing an explicit ADR + CHANGELOG `C` entry rather than a silent drift.

---

### S2-2 · No canonical VLM mesh; the published NP is quoted from an unconverged grid

**Evidence — measured convergence** (`x_NP` in mm from root c/4, current geometry):

| VLM `ny × nx` | `x_NP` (mm) | | Weissinger `ny` | `x_NP` (mm) |
|---:|---:|---|---:|---:|
| 12 × 3 | −76.895 | | 20 | −73.966 |
| 24 × 4 | −76.069 | | 40 | −73.303 |
| **40 × 6** | **−75.787** | | 60 | −73.079 |
| 60 × 8 | −75.637 | | **100** | **−72.899** |
| 80 × 10 | −75.561 | | 140 | −72.821 |
| 120 × 14 | −75.482 | | 300 | −72.718 |
| *Richardson limit* | *≈ −75.43* | | *Richardson limit* | *≈ −72.65* |

Meshes actually in use across the codebase:

| Module | Mesh |
|---|---|
| `vlm_ala_volante.analiza` default, `flight_envelope`, `ventana_torsion` | 40 × 6 |
| `verify_calculations` NP cross-check, `sweep_trade.evaluate` | 24 × 4 |
| `elevon_sizing` | 80 × 6 |
| `weissinger_np` default / verify / published | 80 / 60 / 100 |

The published pair (−75.8 / −72.9 mm) is the 40×6 and ny=100 result. It carries ≈ 0.36 mm
and ≈ 0.25 mm of **undeclared discretisation error**, and the drift has already leaked into
the documents: `docs/09-release-v0.2.md` states **−75.9** on line 66 and **−75.8** on lines
44 and 110.

**Why it matters.** The static margin is 8 % MAC = **18.0 mm**, and the CG tolerance is
`R_CG = ±5 mm`. The VLM↔Weissinger method spread of 2.9 mm is **58 % of the CG tolerance
band** and is currently published as a bare agreement statement with no uncertainty carried
into `CG_TARGET`. That is `CLAUDE.md` failure mode **#2 (false precision)**: a value quoted
to 0.1 mm on top of a 2.9 mm method spread.

**Fix.**

1. Promote `VLM_NY = 40`, `VLM_NX = 6`, `WEISSINGER_NY = 100` into `design_config.py` as
   the **canonical analysis mesh**, and make every caller use them. No literal mesh
   arguments outside a deliberate convergence study.
2. Add a **grid-convergence contract** to `vlm_ala_volante.validation_checks()`: solve at
   the canonical mesh and at 2× refinement, and assert the change is below a declared
   `NP_MESH_TOLERANCE = 0.3e-3` m. This makes the discretisation error a *tested,
   published* number instead of an unstated one.
3. Publish the NP as a value **with a band**, e.g. `x_NP = −75.8 mm [D], method spread
   ±1.5 mm, mesh ±0.4 mm`, and propagate that band into the CG statement.
4. Reconcile `docs/09` line 66 with the released value and record the correction as **C39**.

---

### S2-3 · The design wash-in (3.0°) is declared five times and lives nowhere canonical

**Evidence.**

| Location | Symbol |
|---|---|
| `airfoil_reflex_trade.py:59` | `TWIST_DEG = 3.0` |
| `elevon_sizing.py:27` | `DESIGN_TWIST_DEG = 3.0` |
| `sweep_trade.py:36` | `TWIST_CAP = 3.0` |
| `ventana_torsion.py:35` | `DESIGN_TWIST_DEG = 3.0` |
| `flight_envelope.py:66` | bare literal `3.0` in the `analiza(...)` call |
| `design_config.py` | **absent** |

Wash-in is a first-order geometric parameter: it sets trim, `Cm0`, the tip-stall margin and
the torsion window. Five independent declarations, zero cross-checks.

**Fix.** Add to `design_config.py`:

```python
DESIGN_TWIST_DEG = 3.0        # tip wash-in, ADR-0041 / I-07 [D]
```

with the invariant `0.0 <= DESIGN_TWIST_DEG <= TWIST_STRUCTURAL_CAP_DEG`, delete the four
duplicates, and replace the `flight_envelope` literal.

---

### S2-4 · Elevon hinge station `x/c = 0.72` is declared four times

| Location | Symbol |
|---|---|
| `design_config.py:67` | `ELEVON_HINGE_XC = 0.72` ← canonical |
| `divergence.py:66` | `X_BOX = 0.72` (torsion-box aft closure) |
| `airfoil_reflex_trade.py:57` | `HINGE_X = 0.72` |
| `filament_dowel_pins.py:112,115` | bare literal `0.72` |

The `divergence.py` case is the dangerous one: the torsion box ends **at the hinge by
definition**. Move the hinge and the torsion box silently does not follow, changing `J`,
`GJ` and therefore the divergence speed — the project's declared weakest link (G6).

**Fix.** All four read `design_config.ELEVON_HINGE_XC`. Add a contract check asserting the
torsion-box aft closure equals the hinge station.

---

### S2-5 · **[CRITICAL]** Two irreconcilable yaw inertias

**Evidence.**

| Source | `I_zz` | Provenance |
|---|---:|---|
| `yaw_stability.py:86` | **0.28 kg·m²** | `[E]`, band `(0.23, 0.33)` |
| `equipment_layout.inertia_kg_m2()` on the released solved layout | **0.1587 kg·m²** | `[D]` from the 3D oriented-box mass model |

Ratio **1.76**. The value computed from the repository's own released mass model lies
**entirely outside** the band declared next to the hardcoded one. Nothing cross-checks them,
and `verify_calculations.py` accepts both in the same run — it checks
`equipment layout: assembly inertia diagonal is positive` and, separately,
`yaw: corrected V1 2-DOF modes are damped`, without noticing they disagree about the same
physical quantity.

**Measured consequence** on the published 2-DOF yaw mode:

| `I_zz` | eigenvalue | ω_n | ζ |
|---:|---|---:|---:|
| 0.28 (published) | −0.794 ± 3.948j | 4.027 rad/s | 0.197 |
| 0.23 (band low) | −0.919 ± 4.347j | 4.443 rad/s | 0.207 |
| 0.33 (band high) | −0.707 ± 3.641j | 3.709 rad/s | 0.191 |
| **0.1587 (repo's own 3D model)** | **−1.233 ± 5.204j** | **5.349 rad/s** | **0.231** |

The qualitative conclusion (damped) survives. The **published frequency is 33 % low**, and
the declared band does not contain the model's own answer.

**Caveat, stated honestly.** `equipment_layout` idealises every part as an oriented cuboid.
The wing shells are placed at correct spanwise stations, so 0.1587 kg·m² is a defensible
rigid-body estimate, but it does not capture the spanwise mass distribution inside each
shell. Either number could be the better one. **What is not defensible is that both exist,
unreconciled, driving published results.**

**Fix.**

1. Make `equipment_layout` the single source of inertia; `yaw_stability` imports it.
2. If the box idealisation is judged insufficient, refine it — integrate the shell mass
   along the span using `design_config.chord(y)` — and record the refinement, not a second
   constant.
3. Add the contract check:
   `abs(yaw_stability.iz() - equipment_layout Izz) / Izz < 0.10`.
4. Open a new gap entry for **yaw inertia** (next free gap number) if the reconciliation cannot be closed
   analytically, and re-derive the published mode with a band, per **C40**.

---

### S2-6 · `V_NE` means two different speeds in two modules

```python
divergence.py:61      V_NE = speed_mps(ARTICLE_V_NE_KMH)            # 160 km/h
yaw_stability.py:53   V_NE = speed_mps(STRUCTURAL_DESIGN_SPEED_KMH) # 180 km/h
```

Worse, `verify_calculations.py:305` **codifies the confusion** by asserting
`yaw_stability.V_NE * 3.6 == 180.0` under a check named *"servo and fin strength use
180 km/h structural case"*. A reader who greps for `V_NE` gets two answers.

**Fix.** Ban module-level re-aliasing of speeds. Use the canonical names everywhere
(`ARTICLE_V_NE_MPS`, `V_STRUCTURAL_MPS`, exported from `design_config` already converted),
and add a lint rule forbidding assignment to a name that shadows a `design_config` export
with a different value.

---

### S2-7 · The speed ladder has no ordering invariant, and `V_A > V_C`

**Evidence — the current speed contract:**

| Symbol | Value | Role |
|---|---:|---|
| `STALL_SPEED_LIMIT_KMH` | 45 | requirement ceiling |
| `CRUISE_SPEED_KMH` | 95 | O1 energy point |
| `INITIAL_SPEED_LIMIT_KMH` | 105 | operational cap · **used as `V_C` in the gust schedule** |
| `ARTICLE_V_NE_KMH` | 160 | divergence criterion basis · **used as `V_D`** |
| `STRUCTURAL_DESIGN_SPEED_KMH` | 180 | servo and fin sizing |

`design_config.validate_geometry()` asserts **none** of the ordering relations. Any edit can
invert the ladder silently.

**And the ladder is already inconsistent.** Measured manoeuvring speed at the +6 g limit:

| Case | mass | `V_s` | `V_A(+6)` | vs `V_C` = 105 |
|---|---:|---:|---:|---|
| CLEAN | 1553.2 g | 44.06 km/h | **107.92** | `V_A > V_C` |
| V1 model | 1596.3 g | 44.66 km/h | **109.40** | `V_A > V_C` |
| V1 allocation | 1590.0 g | 44.58 km/h | **109.19** | `V_A > V_C` |

`flight_envelope.py` evaluates the legacy Part 23 gust schedule with `V_C = 105 km/h` and
`V_D = 160 km/h`, but the manoeuvre corner sits **above** the speed being called `V_C` for
all three released masses. In a V-n construction `V_C ≥ V_A` is a structural premise, not a
convention.

Separately, `divergence.py` publishes a first-flight clearance of **`V_limit` = 110 km/h**
at the conservative band (and prints **CRITERION FAILS**, `V_div` 129.6 vs 240 km/h
required) while `V_NE = 160` and a 180 km/h structural sizing case remain in the same
contract with no invariant relating them.

**Fix.**

1. Introduce an explicit, role-tagged **speed ladder** in `design_config.py` with an
   ordering invariant:
   `V_S < V_LIMIT_AEROELASTIC <= V_C_DESIGN` and `V_A <= V_C_DESIGN < V_NE <= V_STRUCTURAL`.
2. Either raise `V_C_DESIGN` above the computed `V_A`, or state in the module and in
   `docs/00` that 105 km/h is an **operational cap**, not a Part 23 `V_C`, and rename the
   gust-schedule argument accordingly. Both are acceptable; the present silence is not.
3. Feed `divergence.v_limit()` back into the contract as a *derived* ceiling and assert
   `V_LIMIT_AEROELASTIC <= INITIAL_SPEED_LIMIT_KMH` — a check the divergence module already
   performs internally and which belongs in the shared harness.
4. Record the resolution as **C41**.

---

### S2-8 · No shared drag model; three modules treat drag three incompatible ways

| Module | Treatment | ADR-0009 compliant? |
|---|---|---|
| `yaw_stability.py:272` | `CD_PROFILE_CRUISE = 0.0136` + `CL²/(π·AR·e)` separately | **Yes** |
| `launch_speed.py:72` | single lumped `CD_LAUNCH = 0.08` `[E]` | **No** |
| `propulsion_match.py` | inverts an *allowable* drag from the power budget, pending E2 | n/a |

`CLAUDE.md` states, unambiguously: *"**Never use** a single Oswald factor for drag. Always
separate the viscous term from the induced one."* `launch_speed` does exactly that, and the
project's only drag polar exists as two bare literals inside a directional-stability module.

**Fix.** Create `drag_model.py` (layer 1) exposing
`cd(cl, reynolds) -> (cd_viscous, cd_induced)` with the viscous term traceable to the
airfoil polars and the induced term using the span-efficiency contract. Have
`yaw_stability`, `launch_speed`, `propulsion_match` and `flight_envelope` all consume it.
Add the contract check that the launch-configuration `CD` produced by the shared model
brackets the current 0.08 estimate, or replace the estimate.

---

### S2-9 to S2-12 · Remaining duplications

| ID | Duplicate | Canonical home |
|---|---|---|
| S2-9 | `joint_pin_trade.RHO_PETG = 1270.0` (module imports nothing from `design_config`) | `design_config.PETG_DENSITY_KG_M3` |
| S2-10 | `divergence.j_section` hardcodes `tc / 0.135` | `design_config.ROOT_TC` |
| S2-11 | `servo_torque` re-derives the chord law from `ROOT_CHORD`/`TAPER` at lines 51 and 64 | `design_config.chord(y)` |
| S2-12 | `yaw_stability.fin_area_for_target` hardcodes fin `AR = 3.0`, sweep `12.0°`, and `L_V` uses a bare `0.285` m fin-AC station, none linked to `fin_geometry()` | a `fin_contract` dataclass |

Additionally: `yaw_stability.LAM_C4 = SWEEP_C4_DEG` is **assigned and never used**, and the
wing contribution to `Cn_β` is a fixed hardcoded band `CNB_W_BAND = (-0.00010, 0.0)` that
does **not depend on the −15° forward sweep**. On a forward-swept wing the sweep-induced
`Cn_β` term is not negligible and its sign matters. Either derive it or open a gap; do not
carry a sweep-independent band on a swept-wing project.

---

## PART C — S3: Verification that cannot turn red

`CLAUDE.md` failure mode **#8**: *"Before proposing a test, ask what result would make it
fail. If there is none, it measures nothing."* Nine checks in the current suite have no
such result.

### S3-1 · Tautology: two literals compared to each other

[balance_cg.py:183](../calculations/balance_cg.py#L183) and
[generate_blueprints.py:1861](../calculations/generate_blueprints.py#L1861):

```python
"VLM/Weissinger NP agreement < 5 mm": abs(NP_VLM - NP_WL) < 0.005
```

`NP_VLM` and `NP_WL` are both hardcoded. This check compares `-0.0758` with `-0.0729`. It
can only fail if a human edits one of the two literals. It verifies **nothing about the
solvers** and gives false assurance that the independent-method cross-check is live.

**Fix.** Replace with the live re-derivation from S2-1: solve both methods at the canonical
mesh and compare. Keep the 5 mm threshold, and additionally assert each against its
published anchor.

### S3-2 · Tautology: an algebraic identity, with a bonus false-failure mode

[balance_cg.py:184](../calculations/balance_cg.py#L184) and
[generate_blueprints.py:1859](../calculations/generate_blueprints.py#L1859):

```python
"SM is 8 percent MAC": abs((NP_VLM - CG_TARGET) / MAC - 0.08) < 1e-12
```

Since `CG_TARGET := NP_VLM - STATIC_MARGIN * MAC`, the expression reduces identically to
`abs(STATIC_MARGIN - 0.08)`. It is an identity — **and** it hardcodes `0.08` instead of
reading `STATIC_MARGIN`, so if the static-margin contract is ever revised to 0.10 the check
turns red while the system is perfectly consistent. It fails in the one scenario where it
should stay green, and passes in every scenario where it should look.

**Fix.** Delete it. Replace with the real invariant: the **solved layout CG** lands within
`R_CG` of `CG_TARGET`, and `CG_TARGET` sits `STATIC_MARGIN` ahead of the **re-derived** NP.

### S3-3 · Tautology: multiplying by 1.0 and dividing by 1

[servo_torque.py](../calculations/servo_torque.py):

```python
"single actuator carries the complete elevon hinge moment":
    abs(servo_torque_nm(ch, v) - hinge_moment(ch, v)) < 1e-12
```

with `HORN_RADIUS_RATIO = 1.0` and `N_SERVOS_PER_ELEVON = 1`. Always true by construction.

**Fix.** Make it a *parameterised* check: assert that for `N_SERVOS_PER_ELEVON = 2` the
per-servo torque halves, and that a horn ratio of 0.5 halves it again. That tests the
lever-arm algebra, which is the thing that can actually be wrong.

### S3-4 · The NP cross-check never touches the published value

Already covered in S2-1. Restated here because it is the most consequential *verification*
gap, not only a *synchronisation* gap.

### S3-5 · An inverted test that fails when the design improves

[flight_envelope.py](../calculations/flight_envelope.py):

```python
"reference VC gust intentionally exposes the unresolved +6/-3 mismatch":
    1.0 + dn_si > POSITIVE_LIMIT_LOAD_FACTOR
    and 1.0 - dn_si < NEGATIVE_LIMIT_LOAD_FACTOR
```

This asserts **that a problem exists**. If wing loading rose or the gust model were refined
so the reference gust no longer breached the limits, the suite would report a *failure* for
a *good* outcome, and a contributor would be pushed to "fix" it by reverting the
improvement.

**Fix.** A validation suite asserts *correctness*, never *the current state of an open
question*. Demote this to a printed diagnostic and track the open question in `G11`.

### S3-6 · The VLM validation tolerance is too loose to discriminate

```python
"straight-wing lift slope is within 8 percent of Helmbold":
    abs(CLa - theory) / theory < 0.08
```

Eight percent will not catch a systematic error in the influence matrix, the boundary
condition, or the MAC normalisation — which is precisely the class of bug that produced
correction **C17**. There is no mesh-convergence check at all.

**Fix.** Tighten to a *measured* tolerance derived from the converged solution, and add:
(a) the Richardson/grid-convergence assertion of S2-2; (b) an elliptic-loading check on an
untwisted elliptical planform if one can be constructed; (c) an assertion that the straight
untwisted wing NP sits at 25.00 % MAC to within the declared mesh tolerance, rather than
1.5 %.

### S3-7 · A declared uncertainty band the code physically cannot propagate

`yaw_stability.IZ_BAND = (0.23, 0.33)` appears **exactly once in the repository — its own
definition**. It is never read. And `yaw_modes(cnb, cnr, cyb, cyr)` has **no `iz`
parameter**, so it cannot forward an inertia at all: the band is unpropagatable by
construction. Verified by execution.

Compounding it: `yaw_state_matrix(..., mass=AUW_REF, iz=IZ, speed=V_CRU)` binds those module
constants as **default arguments at definition time**. Reassigning `yaw_stability.IZ` to run
a sensitivity study silently has **no effect** — verified: all four inertias returned
identical eigenvalues until `iz` was passed explicitly. Any contributor attempting a
sensitivity sweep the obvious way will get a confidently wrong answer.

**Fix.** Ban module constants as default-argument values across the codebase; pass them
explicitly or read them inside the function. Give `yaw_modes` the full parameter set. Make
every declared band exercised by a band-propagation check, or delete the band.

### S3-8 · A stale default that contradicts its own module

`divergence.q_divergence(..., e_frac=0.11)` and `q_divergence_shooting(..., e_frac=0.11)`.
The module's own `E_BAND = tuple(x - X_AC for x in X_EA_BAND)` = **(0.10, 0.05, 0.20)** —
the nominal is **0.10**, not 0.11. Every current call site passes `e_frac` explicitly, so
the wrong default is dormant. Dormant is not safe: the next caller who trusts the default
gets a quietly wrong divergence speed.

**Fix.** Remove the default entirely — make `e_frac` a required argument. A quantity with a
declared uncertainty band must never have a silent default.

### S3-9 · Coverage holes in the harness

- `drawing_index.py` and `equipment_catalog.py` are absent from `LOCAL_SCRIPTS`, so their
  own validation cases never run under the harness.
- **Plain `verify_calculations.py` — the command the README tells contributors to run
  first — executes no module's validation case.** Only `--all-scripts` does, and CI runs
  neither. The per-script validation cases that `CLAUDE.md` calls non-negotiable are, in
  practice, run by nobody automatically.

**Fix.** Make `--all-scripts` the **default** and add `--fast` for the interface-only path.
Add both missing modules. Wire the default into CI (S1-4).

---

## PART D — S4: Numerics, efficiency and hygiene

### S4-1 · A `@cache` that never hits, on the hot path

[divergence.py:107](../calculations/divergence.py#L107): `@cache def section_geometry(tc_scale)`
is keyed on a **continuously varying float**. `grid(n=401)` calls it with 401 distinct
`tc/0.135` values. Measured:

```
CacheInfo(hits=0, misses=401, maxsize=None, currsize=401)
```

**Zero hits.** The decorator provides no speedup and leaks 401 entries into an unbounded
cache. Measured `grid(401)` cost: 0.29 s of pure section re-integration.

**Fix.** Quantise the key (`round(tc_scale, 6)`) or, better, restructure: the section
geometry scales linearly in `t/c`, so compute it **once** at the reference thickness and
scale the areas and perimeters analytically. That removes 400 polygon integrations per
grid call.

### S4-2 · A 40 000-step linear scan where a root-find belongs

`q_divergence_shooting` sweeps `q = qmax * iq / nq` for `nq = 40000`, each evaluation
marching 400 transfer-matrix segments in a pure-Python loop, and on the first sign change
**returns `q_prev` — the lower bracket, not the root**. So the result carries a resolution
of `qmax/nq = 5 Pa` *and* a systematic low bias.

Measured: **3.86 s per call**; `divergence.py` end-to-end **33 s**.

**Fix.** Bracket coarsely (a few hundred points), then `scipy.optimize.brentq` — or a
hand-rolled bisection if the no-scipy constraint stands — on `T(L; q)`. Converges to
machine precision in ~30 evaluations. Expected: **~1000× fewer marches**, exact root,
`divergence.py` under 2 s. Vectorising the segment march over `q` gives another large
factor if wanted.

Also add the degenerate-`k` guard: `th_new = th·cos(k·dy) + T·sin(k·dy)/(GJ·k)` divides by
`GJ·k` with `k = sqrt(q·m/GJ)`, which has no series limit as `k → 0`.

### S4-3 · Variable shadowing inside the divergence eigenproblem

[divergence.py:242-250](../calculations/divergence.py#L242-L250):

```python
e = e_frac * c          # eccentricity array, physics
m = c * e * a
...
for e in range(1, n):   # <-- shadows the eccentricity with an integer index
```

Harmless **today** only because `m` is formed before the loop. It is one edit away from a
silent, plausible-looking physics error inside the project's declared weakest-link
calculation. Rename the loop index to `elem`.

### S4-4 · One second of VLM burned at import time, on every importer

[airfoil_reflex_trade.py:73-74](../calculations/airfoil_reflex_trade.py#L73-L74) executes two
80×6 VLM solves **in the module body**:

```python
DCM_TWIST  = cm0_wing(1.0, 0.0) - cm0_wing(0.0, 0.0)
DCM_ELEVON = cm0_wing(0.0, 1.0) - cm0_wing(0.0, 0.0)
```

Measured import cost: **978 ms**, out of 1.115 s total for `import verify_calculations`.
Everyone who imports the module — including the harness, including a contributor who only
wants one constant — pays it.

**Fix.** Wrap in `@cache`d functions. Nothing expensive at module scope, anywhere.

### S4-5 · Duplicated formulas within a single module

- `vlm_ala_volante.mac()` (line 144) reproduces character-for-character the `cbar`
  expression already computed in `geom()` (line 61); `analiza()` then calls `mac()` instead
  of reading `g["cbar"]`.
- `servo_torque.elevon_chord_avg()` is **dead code** — an arithmetic-mean chord superseded
  by the correct `∫c²dy/∫c dy` in `control_geometry()`, never called. Delete it; a
  contributor who finds it and uses it gets the wrong hinge-moment reference.

### S4-6 · Other unused declarations

`battery_pack_layout.P42A_DATASHEET_URL`, `divergence.JOINT_HALF`,
`equipment_catalog.DJI_O4_COAX_LENGTH_MM`, `equipment_layout.PACK_OUTER_WRAP_MM` /
`PACK_NICKEL_HEIGHT_MM` / `PACK_LEAD_LENGTH_MM`, `generate_blueprints.SHEET_WIDTH` /
`SHEET_HEIGHT`, `joint_pin_trade.SOCKET_D`, `mass_budget.SERVO_REF`,
`yaw_stability.LAM_C4` / `IZ_BAND`. Each is either a live input that was disconnected or a
dead one that should go. Triage individually — a disconnected input is a bug, not clutter.

### S4-7 · Monolithic functions

| Function | Lines |
|---|---:|
| `generate_blueprints.draw_equipment_mass_skeleton` | 455 |
| `generate_blueprints.draw_side_elevations` | 396 |
| `equipment_layout.reference_components` | 350 |
| `verify_calculations.contract_checks` | 284 |
| `generate_blueprints.draw_variant` | 272 |
| `divergence.main` | 238 |

`generate_blueprints.py` is 2124 lines and `equipment_layout.py` is 1469. These are the two
modules a community contributor is most likely to need to extend. Decompose into a package
(`blueprints/` with `sheets/`, `primitives/`, `annotations/`) with a stable public surface.

### S4-8 · Mixed natural language in the source

Spanish identifiers and comments in an otherwise English codebase: `vlm_ala_volante`
(`analiza`, `geom`, `cl_local`, *"condicion de contorno linealizada"*, *"morro arriba
positivo"*, *"estaciones de envergadura"*), `ventana_torsion`, `weissinger_np`, and
`calibra_xfoil_e387` whose entire CLI and error messages are Spanish
(`error: indica --xfoil o define XFOIL_EXE`).

For a repository whose stated purpose is community contribution, pick one language for
code and CLI. English matches the documentation, `CLAUDE.md` and all recent modules. Keep
the Spanish module filenames if renaming would break published references, but alias them
and deprecate on a stated schedule.

### S4-9 · `kgf` defined from the project's gravity rather than standard gravity

`servo_torque.nm_to_kgf_cm` divides by the project gravity constant, 9.81 m/s². The
kilogram-force is defined by `g_n = 9.80665` exactly. The error is 0.036 % — immaterial
numerically, but the same symbol is being used as **two different physical constants**: the
local gravitational acceleration for weight, and a unit-definition constant. Separate them; the check
`10.19 < nm_to_kgf_cm(1.0) < 10.20` passes either way and therefore does not discriminate.

### S4-10 · No test framework

Every module is `main()` + `print` + `raise SystemExit(1)`. There is no `pytest`, no
per-assertion reporting, no way to run a single check, no fixtures, no parameterisation, no
coverage measurement. The printed-table convention is genuinely good for the auditability
this project values and should be **kept as the human-facing output** — but it should sit
on top of a real test layer, not instead of one.

---

## PART E — S5: Physics model gaps

### S5-1 · The hand-launch model has no gravity term and no declared flight-path angle

[launch_speed.py:84](../calculations/launch_speed.py#L84):

```python
def acceleration(speed, thrust, mass, cd=CD_LAUNCH):
    drag = 0.5 * RHO_SL * speed**2 * S * cd
    return (thrust - drag) / mass
```

The axial equation omits `−g·sin γ`. Below `V_stall` — which is the entire regime this
script exists to analyse — lift **cannot** balance weight by definition, so the trajectory
is not level and `γ ≠ 0`. The model implicitly assumes a horizontal path, and `γ` is never
declared, bounded or varied. A descending throw makes the current result conservative; a
climbing one makes it optimistic. Neither is stated.

**Fix.** Write the two-degree-of-freedom launch equation with an explicit declared `γ`
band, or state the horizontal-path assumption with its sign of conservatism and bound the
error. Release gate `V_release ≥ V_stall` is the headline result of this module; it deserves
a stated validity envelope.

### S5-2 · The hinge-moment coefficient has no `α` or `δ` dependence

`servo_torque.CH_RANGE = (0.01, 0.05)` `[E]`, with `MAX_HINGE_COEFFICIENT = max(CH_RANGE)`
evaluated at 180 km/h. Physically `C_h = C_hα·α + C_hδ·δ`. The module never states which
`(α, δ)` its band corresponds to, so it cannot be checked against the elevon deflections
`elevon_authority` and `elevon_sizing` actually produce, nor against the `V_A` corner where
full deflection is credible.

**Fix.** Tie `C_h` to the `(α, δ)` schedule the control modules produce, and add a contract
check that the deflection assumed by `servo_torque` bounds the deflection `elevon_authority`
requires for trim plus the manoeuvre increment.

### S5-3 · The VLM's validity envelope is undocumented

Flat-plate lattice, no camber, uniform chordwise panel spacing, trailing legs truncated at
`far = 1e4`. Section `Cm0` is supplied separately from XFOIL — a **correct** and
well-reasoned split. But the module never states the envelope in which this is valid
(linear, attached, small-`α`, incompressible, rigid), and cosine chordwise clustering would
improve leading-edge resolution at no cost.

**Fix.** Add a short "validity envelope and known omissions" section to the docstring, and
add the same to `weissinger_np`. This is cheap traceability of exactly the kind this
repository is built on.

### S5-4 · A twist argument that cannot affect the answer

`flight_envelope.project_lift_curve_slope()` passes `twist = 3.0` into a **linear** VLM,
where `CL_α` is twist-independent by superposition. Harmless numerically, misleading to a
reader, and it conceals the absence of a canonical twist constant (S2-3).

---

## PART F — Target architecture

The current DAG is right. What it needs is one more layer and a stricter rule.

```
L0  design_config.py          — geometry, atmosphere, speed ladder, masses, load factors
    equipment_catalog.py      — bought-in hardware [M]
    battery_pack_layout.py    — pack envelope model
    drawing_index.py          — publication registry

L1  drag_model.py       (NEW) — viscous + induced, separated per ADR-0009
    vlm_ala_volante.py         weissinger_np.py        servo_torque.py
    mass_budget.py             inav_fc_match.py        joint_pin_trade.py
    filament_dowel_pins.py     b3_screening.py

L2  aero_contract.py    (NEW) — CACHED re-derivation of NP, CL_alpha, Cm0 yields
    balance_cg.py              flight_envelope.py      ventana_torsion.py
    fpv_power_budget.py

L3+ equipment_layout · boom_flexion · propulsion_match · sweep_trade · yaw_stability
    divergence · elevon_sizing · elevon_authority · airfoil_reflex_trade
    generate_blueprints

L∞  verify_calculations.py   — contract registry, exception-isolated, exit-coded
```

**The rule, stated so it can be enforced by lint:**

> A module may **compute** a physical quantity, or **import** it. It may never **declare**
> one that another module also declares. Any number appearing in two modules is either
> promoted to `design_config`/`aero_contract`, or one of the two is deleted.

Concretely, four things move:

| Quantity | From | To |
|---|---|---|
| `NP_VLM`, `NP_WL` | `balance_cg` literals | `aero_contract` cached derivation + published anchor |
| `DESIGN_TWIST_DEG` | 4 modules + 1 literal | `design_config` |
| `VLM_NY`, `VLM_NX`, `WEISSINGER_NY` | 4 different meshes | `design_config` |
| `I_zz` | `yaw_stability` literal | `equipment_layout` derivation |

---

## PART G — Remediation programme

Ordered so that each package is verifiable before the next begins. **Do not reorder** — WP1
must land first because nothing downstream can be trusted until the harness reports
honestly.

### WP1 — Make it run and make it tell the truth *(S1-1…S1-4, S3-9)*

| # | Task | Acceptance |
|---|---|---|
| 1.1 | `calculations/requirements.txt`; numpy floor guard in `design_config`; README corrected | Fresh venv at the floor runs the harness green |
| 1.2 | `pathlib` everywhere; `REPO_ROOT`/`AIRFOIL_DIR` anchors; ban separator literals | `divergence.py` runs on Linux/macOS/Windows |
| 1.3 | Exception-isolated check registry; full table always printed; correct exit code | Corrupt any shared constant → full table, targeted FAIL, exit 1 |
| 1.4 | `--all-scripts` becomes the default; add `drawing_index`, `equipment_catalog` | Every module's validation case runs by default |
| 1.5 | `calculations.yml` CI, matrixed, required on `main` | A desynchronising PR is blocked by CI |

**Gate:** the harness is trustworthy. Nothing in WP2+ counts until this is green.

### WP2 — Collapse the duplicate contracts *(S2-1…S2-4, S2-6, S2-9…S2-12)*

| # | Task | Acceptance |
|---|---|---|
| 2.1 | `aero_contract.py`; NP derived and cached; literals become anchors with tolerance | Changing `SWEEP_C4_DEG` by 1° turns the NP check red |
| 2.2 | Canonical mesh constants; all call sites updated | `grep -n "ny=[0-9]"` finds only convergence studies |
| 2.3 | `DESIGN_TWIST_DEG` promoted; 4 duplicates + 1 literal deleted | One declaration repo-wide |
| 2.4 | `ELEVON_HINGE_XC` consumed by `divergence`, `airfoil_reflex_trade`, `filament_dowel_pins` | Torsion-box aft closure == hinge, asserted |
| 2.5 | `V_NE` aliasing removed; `RHO_PETG`, `0.135`, chord law, fin geometry consolidated | No module-level shadowing of a `design_config` export |

**Gate:** no physical quantity is declared twice. Add a lint check that enforces it.

### WP3 — Reconcile the contradictions *(S2-5, S2-7, S2-8)*

| # | Task | Acceptance |
|---|---|---|
| 3.1 | Yaw inertia: single source, ≤10 % cross-check, republished mode with band | `C40` in CHANGELOG; a new gap entry if it cannot close |
| 3.2 | Speed ladder: ordering invariants; `V_A` vs `V_C` resolved; `V_limit` fed back | Ladder inversion impossible; `C41` recorded |
| 3.3 | `drag_model.py`; `CD_LAUNCH` derived, not lumped | ADR-0009 honoured in every module |

**Gate:** every published number has exactly one derivation and one declared band.

### WP4 — Make the verification discriminate *(S3-1…S3-8)*

| # | Task | Acceptance |
|---|---|---|
| 4.1 | Delete the three tautologies; replace with live re-derivations | Each replacement demonstrably fails under a seeded fault |
| 4.2 | Mutation test: seed a fault (sign flip, dropped MAC normalisation, ×2 on a constant) and confirm a check catches it | ≥1 check red per seeded fault, documented |
| 4.3 | Tighten VLM tolerances; add grid-convergence assertions | Discretisation error is a published, tested number |
| 4.4 | Remove the inverted gust assertion; make it a diagnostic under `G11` | Suite asserts correctness only |
| 4.5 | Ban module constants as default arguments; give `yaw_modes` its full parameter set; every declared band is propagated or deleted | A sensitivity sweep written the obvious way is correct |
| 4.6 | `e_frac` becomes required, no default | No banded quantity has a silent default |

**Gate:** for every seeded fault in a documented list, at least one check turns red. This is
the only real proof a test suite works.

### WP5 — Numerics and cost *(S4-1…S4-4)*

| # | Task | Target |
|---|---|---|
| 5.1 | Fix or remove the ineffective `@cache`; scale section properties analytically | `grid(401)` ≪ 0.29 s |
| 5.2 | Replace the 40 000-point scan with a bracketed Brent root-find; add the `k → 0` guard | `divergence.py` 33 s → **< 2 s**, exact root |
| 5.3 | Rename the shadowed `e` loop index | — |
| 5.4 | No expensive work at module scope; `@cache`d accessors | `import verify_calculations` 1.115 s → **< 0.3 s** |

**Gate:** `verify_calculations.py --all-scripts` completes in under 60 s, so contributors
actually run it.

### WP6 — Structure and physics envelopes *(S4-5…S4-10, S5-1…S5-4)*

| # | Task |
|---|---|
| 6.1 | Delete dead code (`elevon_chord_avg`, `mac()` duplication); triage every unused constant as *disconnected input* vs *dead* |
| 6.2 | Decompose `generate_blueprints.py` and `equipment_layout.py` into packages |
| 6.3 | Introduce `pytest` beneath the printed tables; keep the human-facing output verbatim |
| 6.4 | One source language; deprecate Spanish CLI surfaces on a stated schedule |
| 6.5 | Launch model: declare `γ` or write the 2-DOF equation with its band |
| 6.6 | `C_h` tied to the `(α, δ)` the control modules produce |
| 6.7 | Validity-envelope docstrings for both aero solvers; cosine chordwise spacing |

---

## PART H — Invariants to add to `design_config.validate_geometry()`

Concrete, each one catching a defect found above:

```
speed ladder is strictly ordered            V_S < V_CRUISE < V_C < V_NE <= V_STRUCT
manoeuvring speed does not exceed V_C       V_A(m) <= V_C for every released mass
aeroelastic clearance bounds the cap        V_LIMIT_AEROELASTIC <= INITIAL_SPEED_LIMIT
design twist is within the structural cap   0 <= DESIGN_TWIST_DEG <= TWIST_CAP
NP re-derivation matches the anchor         |NP_vlm() - NP_PUBLISHED| <= NP_TOLERANCE
independent NP methods agree, live          |NP_vlm() - NP_weissinger()| <= 5 mm
mesh convergence is bounded                 |NP(mesh) - NP(2x mesh)| <= NP_MESH_TOL
CG target trails the derived NP by SM       (NP_vlm() - CG_TARGET)/MAC == STATIC_MARGIN
solved layout CG lands on target            |CG_solved - CG_TARGET| <= R_CG
torsion box closes at the hinge             divergence.X_BOX == ELEVON_HINGE_XC
one yaw inertia                             |Iz_yaw - Iz_layout| / Iz_layout < 0.10
one PETG density, one root t/c, one chord law
drag is separated everywhere                every CD consumer returns (viscous, induced)
```

---

## PART I — Traceability obligations

`CLAUDE.md` is explicit: *"When finding an error — do not silence it by editing the text.
Fix it **and** add an entry to the CHANGELOG with a `C` number."* The current record runs
through **C38**. This plan therefore obliges:

| New | Subject |
|---|---|
| **C39** | Published NP mesh provenance and the `docs/09` −75.9 / −75.8 discrepancy; NP restated with a declared band |
| **C40** | Yaw inertia reconciled; the 2-DOF yaw mode republished (ω_n 4.03 → value from the single source) |
| **C41** | Speed-ladder roles clarified; `V_A > V_C` resolved; `V_limit` feedback made a contract |
| **C42** | Drag treatment unified under ADR-0009; lumped `CD_LAUNCH` withdrawn |
| **C43** | Verification tautologies withdrawn; the three checks that could not fail are named |

Likely new artefacts: a new ADR — *"design_config is the sole declaration site for shared
physical quantities"* (the enforceable version of the rule in Part F) — and a new gap entry
for **yaw inertia** if 3.1 cannot close analytically. Both take the next free numbers at
the time they are opened.

---

## PART J — What this plan deliberately does not do

- **It does not change a single physical result.** Every fix is a synchronisation, a
  verification, or a cost fix. Where a number must move (NP band, yaw mode frequency), it
  moves through an ADR and a `C` entry, never silently.
- **It does not rewrite the printed-table convention.** That output is one of the best
  things in this repository: auditable, greppable, human-readable. `pytest` goes underneath
  it, not instead of it.
- **It does not restructure the module DAG.** The layering is correct. Two modules are
  added; none are merged.
- **It does not resolve the open engineering questions** — `G6` divergence margin, `G11`,
  the missing `CL_min`, the E2/E9 measurement gates. Those need data, not code. This plan
  makes sure that when the data arrives, exactly one number changes and everything
  downstream follows.

---

## Appendix — Reproducing this audit

```bash
cd calculations
python3 verify_calculations.py --all-scripts     # S1-1 aborts here on numpy 1.x
python3 divergence.py                            # S1-2 FileNotFoundError on POSIX
python3 -X importtime -c "import verify_calculations" | sort -k2 -t'|' -rn | head
```

```python
# S2-2 mesh convergence
import design_config as dc, vlm_ala_volante as v, weissinger_np as w
for ny, nx in [(12,3),(24,4),(40,6),(60,8),(80,10),(120,14)]:
    print(ny, nx, v.analiza(dc.B, dc.S, dc.TAPER, dc.SWEEP_C4_DEG, 0.0,
                            ny=ny, nx=nx, verbose=False)["x_np"] * 1000)

# S2-5 the two yaw inertias
import equipment_layout as el, yaw_stability as ys
lay, _ = el.solve_battery_x(el.reference_layout())
print(lay.inertia_kg_m2()[2][2], ys.IZ)

# S3-7 the frozen default argument
import numpy as np
for iz in (0.28, 0.1587):
    print(iz, np.linalg.eigvals(ys.yaw_state_matrix(0.0005, -0.0835, iz=iz)))

# S4-1 the cache that never hits
import divergence as d
d.grid(); print(d.section_geometry.cache_info())
```
