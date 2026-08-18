# I-26 — Codex, VS Code and agent toolchain for controlled SVG drawings

**Status:** Executed — repository workflow hardened; optional renderer and schema gates
remain open  
**Date:** 2026-08-18  
**Feeds:** `.agents/skills/salamandra-svg-drafting/`, `.vscode/tasks.json`,
`calculations/generate_blueprints.py`, `geometry/drawings/`, wiki drawing guide

## 1. Question

Which Codex, VS Code, SVG, Python, browser, MCP and agent practices produce good
technical SVG drawings, and which combination is appropriate for Salamandra?

“Good” means geometrically traceable, deterministic, readable, safe to open, visually
reviewed, accessible, diffable and explicit about its engineering authority. It does not
mean merely polished.

## 2. Method

Firecrawl MCP is required by the repository instructions but was unavailable in this
session. The investigation therefore used current first-party documentation and upstream
project repositories. Local binaries, Python packages, VS Code extensions and configured
MCP servers were also inspected. Tool popularity was treated only as adoption evidence,
never as engineering validation.

Sources were evaluated against six failure modes:

1. geometry drifting away from calculations;
2. non-deterministic output or environment-dependent rendering;
3. structurally valid XML that is visually unusable;
4. optimisation that silently changes meaning or removes accessibility;
5. external or active content in an SVG master; and
6. an illustration being mistaken for manufacturing authority.

## 3. Findings

### 3.1 Codex and agent architecture

The [Codex IDE extension](https://developers.openai.com/codex/ide) can use open files and
selections as context and review changes beside the source. This is useful for inspecting
the generator, source calculation and rendered artifact together. Codex instructions are
layered through [`AGENTS.md`](https://developers.openai.com/codex/guides/agents-md), with
files nearer the working directory taking precedence.

[Codex skills](https://developers.openai.com/codex/skills) package focused instructions,
references and scripts with progressive disclosure. A repository skill under
`.agents/skills/` is therefore the correct place for Salamandra's drawing-authority and
review rules; a global generic SVG prompt would not know the aircraft's evidence model.

[Codex MCP support](https://developers.openai.com/codex/mcp) exposes the same configured
servers to the CLI and IDE. The useful division of labour is:

| Role | Suitable tool | Authority |
|---|---|---|
| Derive geometry | Python calculation modules and coordinate files | Numerical source |
| Author SVG | Deterministic repository generator | Drawing source |
| Inspect DOM and render | Chrome DevTools or Playwright MCP | Verification only |
| Exchange visual concepts | Figma MCP | Concept/review only |
| Export or manually inspect | Inkscape or a static renderer | Derived artifact only |

The [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) and
[Playwright MCP](https://github.com/microsoft/playwright-mcp) both provide browser
snapshots and screenshots. They close a real gap: XML validation cannot detect clipped
labels, weak line hierarchy or a misleading composition. Playwright's
[`toHaveScreenshot`](https://playwright.dev/docs/test-snapshots) can add regression
baselines, but the project must generate and compare them on a controlled OS, browser and
font stack because screenshots vary by environment.

Figma's [official MCP server](https://developers.figma.com/docs/figma-mcp-server/) is
useful for collaborative layout and native Figma content. It is not suitable as the
authority for calculated wing coordinates unless a deterministic import/export and
comparison gate is added.

### 3.2 SVG authoring and validation

[SVG 2](https://www.w3.org/TR/SVG/) is a text-based, structured graphics format with
viewport, coordinate, linking and accessibility semantics. Salamandra should keep a
small static subset: primitives, paths, text, CSS, markers, patterns and same-document
fragment references.

W3C documents that SVG links and references may fetch external resources in normal
processing, while secure static processing excludes them
([SVG linking](https://www.w3.org/TR/SVG/linking.html)). A controlled drawing master
therefore needs an explicit ban on scripts, event attributes, embedded media and
external URLs; “the XML parses” is insufficient.

The [Nu Html Checker](https://validator.github.io/validator/docs/vnu.1.html) supports an
SVG-only command-line mode and is the strongest optional schema/conformance gate found.
It is not installed locally, so it is not made mandatory in this change.

### 3.3 Generation libraries

| Option | Evidence | Assessment for Salamandra |
|---|---|---|
| Python standard library | Current generator uses escaped strings, dataclasses and ElementTree checks | **Keep now:** zero runtime dependency, transparent diffs and sufficient primitives |
| [`svg.py`](https://github.com/orsinium-labs/svg.py) | Typed, pure-Python SVG builder with no runtime dependencies | Best optional authoring library if element complexity outgrows the local writer |
| [`drawsvg`](https://github.com/cduck/drawsvg) | Python drawing API with arrows, animation and notebook support | Useful for exploratory figures; extra abstraction is not currently justified |
| [`svgwrite`](https://svgwrite.readthedocs.io/en/latest/) | SVG 1.1/1.2 library; documentation states maintenance mode since 2022 | Do not adopt for a new long-lived drawing pipeline |

The decision is deliberately conservative: a library is valuable only if it removes a
demonstrated defect such as malformed attributes or unmanageable composition. It does not
make coordinates more correct.

### 3.4 Rendering, export and optimisation

[`resvg`](https://github.com/linebender/resvg) is the strongest optional deterministic
rendering gate found: it targets static SVG, maintains a large regression corpus and aims
for reproducible cross-platform pixels. Adding a pinned resvg binary and PNG reference
images is the preferred next automation step.

[Inkscape's command line](https://wiki.inkscape.org/wiki/Using_the_Command_Line) can query
objects and export PNG/PDF without interactive editing. Its manual also recommends
retaining the SVG source because PDF cannot preserve every SVG capability
([PDF export](https://inkscape-manuals.readthedocs.io/en/latest/export-pdf.html)). Use it
for inspection and review exports, not as the primary geometry editor.

[`CairoSVG`](https://cairosvg.org/documentation/index.html) provides convenient Python
and CLI conversion to PNG/PDF, but its native Cairo dependency is currently missing in
the Windows environment. It is not a reliable repository gate here until that dependency
is provisioned and pinned.

[`SVGO`](https://svgo.dev/docs/plugins/) has powerful opt-in transformations. Several can
remove metadata, identifiers, classes, descriptions or viewBox information. Optimising a
web delivery copy can be reasonable; running default or editor-triggered optimisation on
the controlled master is not.

### 3.5 VS Code

[VS Code tasks](https://code.visualstudio.com/docs/debugtest/tasks) are workspace-owned,
reviewable commands and can be grouped as build or test tasks. They are a better
integration point than an undocumented button in an extension. This repository now
exposes regeneration, read-only drawing verification and the complete calculation check
through `.vscode/tasks.json`.

The locally installed `jock.svg` extension provides preview and SVG symbol navigation.
Its own [Marketplace page](https://marketplace.visualstudio.com/items?itemName=jock.svg)
warns that minimisation may break some SVGs and states that it does not support SVG 2.
Use its preview only; do not minimise the controlled files. Other preview extensions or
automatic “better SVG” optimisers do not add authority and should not run on save.

## 4. Skills audit

Searches of the public skills catalog found no mature aircraft technical-drawing skill.
Two candidates were inspected but not installed:

- [`svg-precision-skill`](https://skills.sh/dkyazzentwatwa/chatgpt-skills/svg-precision-skill)
  showed approximately 228 installs on 2026-08-18. It has a sound spec → build → validate
  → render loop, but is generic and depends optionally on CairoSVG/Pillow. Install command:
  `npx skills add https://github.com/dkyazzentwatwa/chatgpt-skills --skill svg-precision-skill`.
- [`svg-figure`](https://skills.sh/neuromechanist/research-skills/svg-figure) showed
  approximately 24 installs. It offers useful scientific-figure conventions but not
  aircraft drawing authority. Install command:
  `npx skills add https://github.com/neuromechanist/research-skills --skill svg-figure`.

Low adoption does not make either unsafe, but neither encodes Salamandra's `[D]/[E]/[I]`
status, calculation sources, print contract or manufacturing gate. The implemented
repository skill keeps the useful review sequence while adding those project controls.

## 5. Local environment snapshot

On 2026-08-18 the workstation had Codex, Python, Node/npm, Pillow, the `jock.svg` VS Code
extension, Playwright, Chrome DevTools MCP and Playwright MCP. Inkscape, resvg, vnu,
`svg.py`, drawsvg and svgwrite were not installed. CairoSVG was importable only far enough
to report a missing native Cairo library. Figma MCP was configured but not authenticated.

One MCP credential was visible in a command-line argument during the audit. Its value is
not recorded here. Secrets should be supplied through environment variables or a secret
store and the exposed credential should be rotated; changing user-level MCP credentials
is outside this repository change.

## 6. Implemented workflow

The recommended sequence is intentionally short:

1. Read the drawing contract and the authoritative calculation/evidence sources.
2. Edit the Python generator, not the generated SVG.
3. Regenerate with `python calculations/generate_blueprints.py`.
4. Run the read-only stale/structure/security check with
   `python calculations/generate_blueprints.py --check`.
5. Open each standalone SVG in a real browser; inspect the whole sheet and dense regions.
6. Run all calculations when geometry or status changed and report remaining provisional
   items.

The browser review in this implementation found two defects that XML and numerical checks
could not: the half-span label crossed the inner frame by 0.55 mm and the half-wing title
crossed its title-block cell by 0.80 mm. Both were corrected in the generator before
acceptance, confirming that DOM bounds plus human visual inspection are necessary.

Conceptually these are three roles—geometry author, structural validator and visual
reviewer. One Codex agent can execute them sequentially for routine work. Separate agents
are useful only for an independent high-risk review; more agents do not create more
authority.

A strong task instruction is:

> Read the relevant design calculation and drawing contract. Edit the SVG generator only.
> Preserve `[D]/[E]/[I]` status, regenerate, run the read-only check, inspect the standalone
> SVG at full-sheet and detail zoom, and report both visual defects and unresolved gates.

## 7. Decision and next gate

Adopt now:

- Python-generated static SVG masters tied to canonical calculations;
- the repository-specific Codex skill and VS Code tasks;
- strict structural/security/accessibility checks; and
- browser-based visual inspection for every changed sheet.

Evaluate next, without blocking current work:

- pinned resvg rendering and Playwright screenshot baselines in one controlled CI image;
- vnu SVG validation; and
- Inkscape PDF export for controlled review packages.

Do not adopt automatic optimisation, manual geometry authority, raster-first drafting or
a new Python SVG library until a measured failure justifies the added dependency.
