# Salamandra wiki — maintenance guide

The served documentation site, built with **Astro Starlight**. It is deployed to
GitHub Pages by [`.github/workflows/docs.yml`](../.github/workflows/docs.yml) on
every push to `main`.

## How it works

```
canonical folders (decisions/ research/ gaps/ tests/ calculations/ docs/ design/ ...)
        │  read, never edited
        ▼
wiki/scripts/gen-site.mjs          ← the generator (Node, no runtime dependencies)
        │  emits + derives release metadata + builds indexes + rewrites links
        ▼
wiki/src/content/docs/             ← GENERATED, gitignored
        │
        ▼
astro build  →  wiki/dist/  →  GitHub Pages
```

**Canonical files are never duplicated.** The generator reads the source-of-truth
folders, adds a frontmatter block, and rewrites relative links to served URLs.
Index pages (ADR table, research threads, scripts list) are **generated at build
time from the folders they index** — they cannot drift from the sources.

## Commands (run inside `wiki/`)

```bash
npm install          # first time; keep package-lock.json committed
npm run dev          # local server (regenerates content first)
npm run build        # production build (regenerates content first)
npm run gen          # regenerate site content only
npm run check        # astro check (type + schema validation)
npm run check:refs   # strict integrity: broken links + unknown ADR/I/G/E ids
npm run check:site   # verify links and anchors in the compiled site
npm run lint         # lint committed wiki Markdown and MDX
```

`predev`/`prebuild` hooks run the generator automatically, so `npm run dev` and
`npm run build` always work on fresh content.

## When to touch what

| You change ... | Then ... |
|---|---|
| A canonical `.md` (an ADR, a research thread, gaps, tests, a `docs/` file) | Nothing — build regenerates. `npm run dev` to preview |
| Onboarding content (the wiki's own pages) | Edit `wiki/content/` (home, 404, guide pages) — this is committed source |
| Site structure / nav / theme | `wiki/astro.config.mjs`, `wiki/src/styles/custom.css` |
| Hero or diagram assets | `wiki/src/assets/` for imported assets; canonical technical drawings live in `geometry/drawings/` and are copied to the generated `wiki/public/drawings/`; other stable public files remain in `wiki/public/` |
| A generated SVG drawing | Nothing here — rerun `python3 calculations/generate_blueprints.py`. The build copies the sheets, verifies each SHA-256 against `geometry/drawings/manifest.json` and expands `{{DRAWINGS}}` in the drawing guide page from it |
| Deployment identity (repo name) | `wiki/base.mjs` (single source of truth) |

## Authoring guide pages

Pages under `wiki/content/guide/` are committed Markdown (MDX for the architecture
page, which uses the `Mermaid` component). They must carry a `title` frontmatter; do
not repeat it as a level-one Markdown heading because Starlight renders the page H1.
Links between pages should be **relative** to the served location (e.g. from
`/guide/...` use `../decisions/`).

Onboarding pages may use generator tokens such as `{{RELEASE_TAG}}`,
`{{GUIDE_VERSION}}`, `{{CURRENT_RELEASE_URL}}` and `{{LATEST_CORRECTION}}`. Their values
are derived from the tagged release document, the controlling Design Guide and the
changelog, preventing wiki-only version drift.

## Checks that protect the record

- **Referential integrity** (`check:refs`, strict in CI): every inline Markdown/MDX link
  in the repository must resolve, and every mention of `ADR-XXXX` / `I-XX` / `GX` /
  `EX` must match a real or intentionally fileless record (superseded ADRs and withdrawn
  tests included).
- **Strict generation** (`gen-site.mjs --strict`, run in CI): the generator fails
  on unresolved internal links that are not declared forward references
  (currently only `prompts/` in the design guide).
- The generator reports **unresolved internal links** on stderr; keep the count at
  zero except for declared forward references.
- Starlight's schema validation fails the build if a generated page is missing a
  required field.
- **Built navigation** (`check:site`, after `build`) validates actual output routes and
  anchors. This catches framework slug transformations that source-level checks cannot
  see.
- The CI job (`npm ci` → references → lint → strict generation → build → built links)
  uses the same checked-in commands as local verification, so a local pass represents
  the deployment pipeline.
