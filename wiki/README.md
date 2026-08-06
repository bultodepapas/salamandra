# Salamandra wiki — maintenance guide

The served documentation site, built with **Astro Starlight**. It is deployed to
GitHub Pages by [`.github/workflows/docs.yml`](../.github/workflows/docs.yml) on
every push to `main`.

## How it works

```
canonical folders (decisions/ research/ gaps/ tests/ calculations/ docs/ design/ ...)
        │  read, never edited
        ▼
wiki/scripts/gen-site.mjs          ← the generator (Node, no dependencies)
        │  emits + auto-generated index tables + rewrites internal links
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
```

`predev`/`prebuild` hooks run the generator automatically, so `npm run dev` and
`npm run build` always work on fresh content.

## When to touch what

| You change ... | Then ... |
|---|---|
| A canonical `.md` (an ADR, a research thread, gaps, tests, a `docs/` file) | Nothing — build regenerates. `npm run dev` to preview |
| Onboarding content (the wiki's own pages) | Edit `wiki/content/` (home, 404, guide pages) — this is committed source |
| Site structure / nav / theme | `wiki/astro.config.mjs`, `wiki/src/styles/custom.css` |
| Deployment identity (repo name) | `wiki/base.mjs` (single source of truth) |

## Authoring guide pages

Pages under `wiki/content/guide/` are committed Markdown (MDX for the architecture
page, which uses the `Mermaid` component). They must carry a `title` frontmatter.
Links between pages should be **relative** to the served location (e.g. from
`/guide/...` use `../decisions/`).

## Checks that protect the record

- The generator reports **unresolved internal links** on stderr. A new broken link
  appears in the build log; keep the count at zero except for known forward
  references (e.g. `prompts/` in the design guide).
- Starlight's schema validation fails the build if a generated page is missing a
  required field.
- The CI job (`npm ci` → `npm run build`) is the same pipeline used locally, so
  what builds in CI builds here.
