// gen-site.mjs — builds the served wiki content from the canonical repository.
//
// Principles (do not violate):
//  1. Canonical files are NEVER copied or edited. They are read, given a
//     frontmatter block, and emitted into src/content/docs/ (gitignored).
//  2. Index pages (ADR / research / reference / scripts ...) are generated at
//     build time from the folders they index, so they cannot drift.
//  3. Internal relative links are rewritten to served URLs; unresolved internal
//     links are reported on stderr so CI can catch broken references.
//
// Run with:  node scripts/gen-site.mjs   (also wired to predev/prebuild)

import {
  readFileSync,
  writeFileSync,
  mkdirSync,
  rmSync,
  readdirSync,
  existsSync,
  statSync,
} from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { BASE, REPO } from '../base.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const WIKI = path.resolve(HERE, '..');
const ROOT = path.resolve(WIKI, '..');
const OUT = path.join(WIKI, 'src', 'content', 'docs');
const CONTENT = path.join(WIKI, 'content');

const EDIT = `https://github.com/${REPO}/edit/main/`;
const warnings = [];
const warn = (msg) => warnings.push(msg);

// Strict mode (--strict): any unresolved internal link that is not a declared
// forward reference fails the run. CI uses it as a traceability gate.
const STRICT = process.argv.includes('--strict');
const isKnownForwardRef = (w) => w.includes('prompts/');

// ---------------------------------------------------------------------------
// small helpers

const readAbs = (rel) =>
  readFileSync(path.join(ROOT, ...rel.split('/')), 'utf8').replace(/^\uFEFF/, '');

const writeOut = (dest, content) => {
  const abs = path.join(OUT, ...dest.split('/'));
  mkdirSync(path.dirname(abs), { recursive: true });
  writeFileSync(abs, content, 'utf8');
};

const clean = (s) =>
  s.replace(/\*\*/g, '').replace(/\[|\]/g, '').replace(/\s+/g, ' ').trim();

const extractTitle = (md) => {
  const m = md.match(/^#\s+(.+?)\s*$/m);
  return m ? m[1].trim() : null;
};

const extractDescription = (md) => {
  const st = md.match(/\*\*Status:\*\*\s*([^\n]+)/);
  if (st) return clean(st[1]);
  const p = md.match(/\n\n\s*([^\n#|][^\n]{20,320})/);
  return p ? clean(p[1]) : '';
};

const frontmatter = (title, description, editUrl) =>
  `---\ntitle: ${JSON.stringify(title)}\ndescription: ${JSON.stringify(
    description || '',
  )}\neditUrl: ${JSON.stringify(editUrl)}\n---\n\n`;

// ---------------------------------------------------------------------------
// mount table: canonical source (repo-relative posix path) -> destination

const mounted = new Map(); // srcRel -> { dest }

const add = (srcRel, dest) => mounted.set(srcRel, { dest });

add('design/Salamandra-Design-Guide-v0.1.md', 'salamandra/design-guide.md');
add('design/Design-Guide-Justification-v0.1.md', 'salamandra/design-guide-justification.md');
add('design/Design-Guide-Open-Points-v0.1.md', 'salamandra/design-guide-open-points.md');

for (const f of readdirSync(path.join(ROOT, 'decisions'))
  .filter((f) => /^ADR-\d{4}.*\.md$/.test(f))
  .sort()) {
  add(`decisions/${f}`, `decisions/${f.toLowerCase()}`);
}
add('decisions/README.md', 'decisions/overview.md');

for (const f of readdirSync(path.join(ROOT, 'research'))
  .filter((f) => /^I-\d{2}.*\.md$/.test(f))
  .sort()) {
  add(`research/${f}`, `research/${f.toLowerCase()}`);
}
add('research/README.md', 'research/overview.md');
add('first_investigation.md', 'research/first-investigation.md');

add('gaps/README.md', 'gaps/index.md');
add('tests/README.md', 'tests/index.md');
add('calculations/README.md', 'calculations/reproduction-guide.md');
add('decisions/TEMPLATE.md', 'decisions/template.md');

for (const f of readdirSync(path.join(ROOT, 'docs'))
  .filter((f) => f.endsWith('.md'))
  .sort()) {
  add(`docs/${f}`, `reference/${f.toLowerCase()}`);
}

add('README.md', 'platform/readme.md');
add('CONTRIBUTING.md', 'platform/contributing.md');
add('CHANGELOG.md', 'platform/changelog.md');
add('CLAUDE.md', 'platform/ai-context.md');
add('LICENSE-docs.md', 'platform/license-docs.md');

// ---------------------------------------------------------------------------
// URL resolution

const destToUrl = (dest) => {
  const dir = path.posix.dirname(dest);
  const baseName = path.posix.basename(dest).replace(/\.(md|mdx)$/, '');
  const slug = baseName === 'index' ? '' : baseName + '/';
  return BASE + (dir === '.' ? '' : dir + '/') + slug;
};

const urlMap = new Map(); // canonical srcRel -> served URL
for (const [srcRel, spec] of mounted) urlMap.set(srcRel, destToUrl(spec.dest));

// Every served page, keyed by its site path without leading/trailing slashes
// (e.g. "decisions/adr-0001-inverted-sweep", "" for the home page).
const pagePaths = new Map();
const addPagePath = (dest) => {
  const url = destToUrl(dest);
  pagePaths.set(url.slice(BASE.length).replace(/\/+$/, ''), url);
};

// folderMap: canonical folder -> served landing (for folder-only links like `(tests/)`)
const folderMap = new Map([
  ['decisions', `${BASE}decisions/`],
  ['research', `${BASE}research/`],
  ['gaps', `${BASE}gaps/`],
  ['tests', `${BASE}tests/`],
  ['calculations', `${BASE}calculations/`],
  ['design', `${BASE}salamandra/`],
  ['docs', `${BASE}reference/`],
  ['wiki', BASE],
]);

for (const [, spec] of mounted) addPagePath(spec.dest);
// generated index pages (not part of `mounted`) still need their URLs registered
for (const d of [
  'salamandra/index.md',
  'reference/index.md',
  'platform/index.md',
  'decisions/index.md',
  'research/index.md',
  'calculations/index.md',
]) {
  addPagePath(d);
}

// siteDir: site-relative directory of the page being processed
// (e.g. "decisions" for canonical files, "guide" for wiki content pages).
function rewriteLinks(md, siteDir) {
  return md.replace(/\]\(([^()\s]+)\)/g, (m, href) => {
    if (/^(https?:|mailto:|#|\/|data:)/.test(href)) return m;
    const idx = href.indexOf('#');
    const anchor = idx >= 0 ? href.slice(idx) : '';
    const base = idx >= 0 ? href.slice(0, idx) : href;
    // template placeholders like `(../research/...)` must stay untouched
    if (base.includes('...')) return m;
    let norm = path.posix.normalize(path.posix.join(siteDir, base)).replace(/\/+$/, '');
    if (norm === '.') norm = '';
    if (norm.startsWith('./')) norm = norm.slice(2);

    const lookup = (key) => pagePaths.get(key) || urlMap.get(key) || folderMap.get(key);

    if (base.endsWith('.py')) {
      if (norm.startsWith('calculations/')) {
        return '](' + BASE + 'calculations/reproduction-guide/' + anchor + ')';
      }
      warn(`Unresolved script link "${href}" on page "${siteDir}"`);
      return m;
    }

    if (/\.(md|mdx)$/.test(base)) {
      let u = urlMap.get(norm);
      if (!u) u = pagePaths.get(norm.replace(/\.(md|mdx)$/, ''));
      // fallback: some canonical links omit the folder hop (pre-existing repo
      // links like `(research/I-15....md)` inside gaps/README.md)
      if (!u && siteDir !== '.') {
        const short = norm.replace(siteDir + '/', '');
        u = urlMap.get(short) || pagePaths.get(short.replace(/\.(md|mdx)$/, ''));
      }
      if (u) return '](' + u + anchor + ')';
      warn(`Unresolved link "${href}" -> "${norm}" on page "${siteDir}"`);
      return m;
    }

    const hit = lookup(norm);
    if (hit) return '](' + hit + anchor + ')';
    // repo files that are not served by the wiki
    if (norm === 'LICENSE') {
      return '](' + `https://github.com/${REPO}/blob/main/LICENSE` + anchor + ')';
    }
    warn(`Unresolved link "${href}" -> "${norm}" on page "${siteDir}"`);
    return m;
  });
}

// ---------------------------------------------------------------------------
// canonical page mounting

function buildMounted() {
  for (const [srcRel, spec] of mounted) {
    if (!existsSync(path.join(ROOT, ...srcRel.split('/')))) {
      warn(`Missing source: ${srcRel}`);
      continue;
    }
    const md = rewriteLinks(readAbs(srcRel), path.posix.dirname(srcRel));
    const title = extractTitle(md) || path.posix.basename(spec.dest).replace(/\.md$/, '');
    const desc = extractDescription(md);
    writeOut(spec.dest, frontmatter(title, desc, EDIT + srcRel) + md);
  }
}

// ---------------------------------------------------------------------------
// committed wiki-only pages (home + guide)

function buildContent() {
  const files = [];
  const walk = (rel) => {
    const dir = rel ? path.join(CONTENT, ...rel.split('/')) : CONTENT;
    for (const f of readdirSync(dir)) {
      const relFull = rel ? `${rel}/${f}` : f;
      const abs = path.join(CONTENT, ...relFull.split('/'));
      if (statSync(abs).isDirectory()) walk(relFull);
      else files.push(relFull);
    }
  };
  walk('');
  // register destinations so guide pages can link to each other
  for (const relFull of files) {
    addPagePath(relFull === 'home.md' ? 'index.md' : relFull);
  }
  for (const relFull of files) {
    const siteDir = path.posix.dirname(relFull); // 'guide' or '.'
    const md = rewriteLinks(readFileSync(path.join(CONTENT, ...relFull.split('/')), 'utf8').replace(/^\uFEFF/, ''), siteDir);
    const dest = relFull === 'home.md' ? 'index.md' : relFull;
    writeOut(dest, md);
  }
}

// ---------------------------------------------------------------------------
// header parser shared by the generated index tables

function parseHeader(srcRel) {
  const md = readAbs(srcRel);
  const title = extractTitle(md) || '';
  const statusLine = md.match(/\*\*Status:\*\*\s*([^\n]+)/)?.[1] || '';
  const status =
    statusLine.match(
      /(✅ Active|🔄 Provisional|⬜ Superseded|❌ Cancelled|⚠️ Under dispute)/,
    )?.[1] || '';
  const confidence = statusLine.match(/Confidence:\*\*\s*([^·\n]+)/)?.[1]?.trim() || '';
  const reversible = statusLine.match(/Reversible:\*\*\s*([^·\n]+)/)?.[1]?.trim() || '';
  return { title, status, confidence, reversible };
}

const indexPage = (title, desc, body) =>
  frontmatter(title, desc, EDIT + 'wiki/scripts/gen-site.mjs') + body;

// ---------------------------------------------------------------------------
// generated index pages

function genDecisionsIndex() {
  const rows = readdirSync(path.join(ROOT, 'decisions'))
    .filter((f) => /^ADR-\d{4}.*\.md$/.test(f))
    .sort()
    .map((f) => {
      const src = `decisions/${f}`;
      const { title, status, confidence, reversible } = parseHeader(src);
      const num = f.match(/^ADR-(\d{4})/)?.[1] || '';
      return { num, title, status, confidence, reversible, url: destToUrl(`decisions/${f.toLowerCase()}`) };
    });
  const table = rows
    .map(
      (r) =>
        `| [ADR-${r.num}](${r.url}) | ${r.title.replace(/^ADR-\d{4}\s*—\s*/, '')} | ${r.status} | ${r.confidence} | ${r.reversible} |`,
    )
    .join('\n');
  writeOut(
    'decisions/index.md',
    indexPage(
      'Decision record (ADR)',
      `Auto-generated index of all ${rows.length} ADRs. Cannot drift from the source files.`,
      `# Decision record (ADR)

One decision, one file. Each ADR declares **context, alternatives considered, decision, consequences and confidence**.

> This table is **generated at build time** from the files in \`decisions/\` — it cannot drift.
> The maintained manual table, including superseded and cancelled ADRs, lives in the [overview](./overview/).

| # | Decision | Status | Confidence | Reversible |
|---|---|---|---|---|
${table}
`,
    ),
  );
}

function genResearchIndex() {
  const rows = readdirSync(path.join(ROOT, 'research'))
    .filter((f) => /^I-\d{2}.*\.md$/.test(f))
    .sort()
    .map((f) => {
      const src = `research/${f}`;
      const md = readAbs(src);
      const title = extractTitle(md) || f;
      const status = md.match(/\*\*Status:\*\*\s*([^\n]+)/)?.[1] || '';
      const closes =
        md.match(/\*\*(?:Partially )?closes?:\*\*\s*([^\n]+)/i)?.[1] || '';
      const feeds = md.match(/\*\*Feeds:\*\*\s*([^\n]+)/)?.[1] || '';
      const num = f.match(/^I-(\d{2})/)?.[1] || '';
      return {
        num,
        title: title.replace(/^I-\d{2}\s*—\s*/, ''),
        status: clean(status),
        closes: clean(closes),
        feeds: clean(feeds),
        url: destToUrl(`research/${f.toLowerCase()}`),
      };
    });
  const table = rows
    .map(
      (r) =>
        `| [I-${r.num}](${r.url}) | ${r.title} | ${r.status} | ${r.closes || '—'} | ${r.feeds || '—'} |`,
    )
    .join('\n');
  writeOut(
    'research/index.md',
    indexPage(
      'Research threads',
      `Auto-generated index of ${rows.length} research threads (I-XX).`,
      `# Research threads

What was searched, what was found, with what sources — **not** what was decided (that is the [ADR index](../decisions/)). Generated at build time.

| Thread | Topic | Status | Closes | Feeds |
|---|---|---|---|---|
${table}

See also: [first investigation](./first-investigation/).
`,
    ),
  );
}

function genSalamandraIndex() {
  const items = [
    ['design-guide', 'design-guide', 'Salamandra Design Guide v0.1 — the CAD-ready specification handed to the designer.'],
    ['design-guide-justification', 'design-guide-justification', 'Why every number in the guide is what it is — the justification and its sources.'],
    ['design-guide-open-points', 'design-guide-open-points', 'The open points that still constrain the design.'],
  ];
  const table = items
    .map(([slug, _src, desc]) => `| [${slug}](${slug}/) | ${desc} |`)
    .join('\n');
  writeOut(
    'salamandra/index.md',
    indexPage(
      'Salamandra — reference design',
      'The forward-swept flying wing, first platform design.',
      `# Salamandra

The first reference design on the platform: a **PETG forward-swept flying wing**, modular and configurable (CORE center module + interchangeable PANEL wings). Target: **≤ 1.15 Wh/km** at 95 km/h, falsifiable with tests E2/E3.

| Document | Content |
|---|---|
${table}

> The **reasoning is the product**: every decision traces back to an ADR, every number to a calculation or a source.
`,
    ),
  );
}

function genReferenceIndex() {
  const rows = readdirSync(path.join(ROOT, 'docs'))
    .filter((f) => f.endsWith('.md'))
    .sort()
    .map((f) => {
      const src = `docs/${f}`;
      const md = readAbs(src);
      const title = extractTitle(md) || f;
      const url = destToUrl(`reference/${f.toLowerCase()}`);
      const first =
        md.match(/\n\n\s*([^\n#|][^\n]{20,200})/)?.[1]?.trim() || '';
      return { name: f.replace(/\.md$/, ''), title, url, desc: clean(first) };
    });
  const table = rows
    .map((r) => `| [${r.name}](${r.url}) | ${r.desc} |`)
    .join('\n');
  writeOut(
    'reference/index.md',
    indexPage(
      'Reference documents',
      'Specification, phase plan, conventions and master plan.',
      `# Reference documents

Specification and project planning documents. Generated at build time.

| Document | Content |
|---|---|
${table}
`,
    ),
  );
}

function genCalculationsIndex() {
  const scripts = readdirSync(path.join(ROOT, 'calculations'))
    .filter((f) => f.endsWith('.py'))
    .sort()
    .map((f) => {
      const abs = path.join(ROOT, 'calculations', f);
      const src = readFileSync(abs, 'utf8');
      const doc = src.match(/^\s*"""(.*?)"""/s)?.[1] || '';
      const summary =
        doc
          .split('\n')
          .map((l) => l.trim())
          .filter(Boolean)[0] || '';
      return { f, summary: clean(summary).slice(0, 180) };
    });
  const table = scripts
    .map((s) => `| \`${s.f}\` | ${s.summary} |`)
    .join('\n');
  writeOut(
    'calculations/index.md',
    indexPage(
      'Calculations',
      `Auto-generated index of ${scripts.length} validated, rerunnable analysis scripts.`,
      `# Calculations

Every quantitative claim in this repository comes from a script that anyone can rerun. Each script carries a **validation case against a known analytical solution** and must pass it before use.

> Generated at build time from \`calculations/\`. The full reproduction guide — versions, commands, batch quirks, validation discipline — is in the [reproduction guide](./reproduction-guide/).

## Reproducing the Phase-1 results

\`\`\`bash
python3 calculations/vlm_ala_volante.py       # NP (I-07)
python3 calculations/weissinger_np.py         # C2 independent NP check (I-15 §6.3)
python3 calculations/b3_screening.py --xfoil /path/to/xfoil.exe   # B3 screening (I-15 §6)
python3 calculations/balance_cg.py            # OP-01 balance / nose-boom sizing (guide §8.2)
python3 calculations/elevon_authority.py      # elevon control power (guide §5.3)
\`\`\`

## Scripts

| Script | What it does |
|---|---|
${table}
`,
    ),
  );
}

function genPlatformIndex() {
  const items = [
    ['readme', 'Project readme'],
    ['changelog', 'Change log (corrections C1–C21)'],
    ['contributing', 'How to contribute'],
    ['ai-context', 'AI working rules'],
    ['license-docs', 'Documentation licence (CC BY-SA 4.0)'],
  ];
  const table = items.map(([slug, label]) => `| [${label}](${slug}/) |`).join('\n');
  writeOut(
    'platform/index.md',
    indexPage(
      'Platform',
      'Project-level documents: readme, changelog, contributing, licence.',
      `# Platform

Project-level documents.

| Document | |
|---|---|
${table}
`,
    ),
  );
}

// ---------------------------------------------------------------------------
// llms.txt — the site map for AI agents, derived from the served pages

function genLlmsTxt() {
  const pages = [
    ['', 'Salamandra — open 3D-printed FPV aircraft platform'],
    ['guide/01-getting-started', 'Getting started'],
    ['guide/02-how-to-read', 'How to read this repository'],
    ['guide/03-architecture', 'Architecture'],
    ['guide/04-glossary', 'Glossary'],
    ['guide/05-contributing', 'Contributing'],
    ['salamandra', 'Salamandra reference design'],
    ['salamandra/design-guide', 'Design guide v0.1'],
    ['salamandra/design-guide-justification', 'Design guide justification'],
    ['salamandra/design-guide-open-points', 'Design guide open points'],
    ['decisions', 'Decision record (ADR)'],
    ['research', 'Research threads'],
    ['gaps', 'Gap register'],
    ['tests', 'Experimental program'],
    ['calculations', 'Calculations'],
    ['calculations/reproduction-guide', 'Reproduction guide'],
    ['reference', 'Reference documents'],
    ['reference/00-objectives-and-requirements', 'Objectives and requirements'],
    ['reference/03-phase-1-plan', 'Phase-1 plan'],
    ['platform/readme', 'Project readme'],
    ['platform/changelog', 'Changelog'],
    ['platform/contributing', 'Contributing'],
  ];
  const lines = [
    '# Salamandra',
    '',
    'Open, community-driven 3D-printed FPV aircraft platform. The reasoning is the product:',
    'every decision carries its rationale, its source and its confidence level ([M]/[D]/[E]/[I]).',
    '',
    '## Key pages',
    '',
  ];
  for (const [p, label] of pages) {
    const url = pagePaths.get(p);
    if (url) lines.push(`- ${label}: ${url}`);
  }
  lines.push('');
  const out = path.join(WIKI, 'public', 'llms.txt');
  mkdirSync(path.dirname(out), { recursive: true });
  writeFileSync(out, lines.join('\n'), 'utf8');
  console.log(`[gen-site] wrote ${lines.length - 1} llms.txt entries.`);
}

// ---------------------------------------------------------------------------

rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });

buildMounted();
buildContent();
genDecisionsIndex();
genResearchIndex();
genSalamandraIndex();
genReferenceIndex();
genCalculationsIndex();
genPlatformIndex();
genLlmsTxt();

const count = (p) =>
  readdirSync(path.join(OUT, ...p.split('/')), { withFileTypes: true }).filter((e) => e.isFile()).length;
console.log(
  `[gen-site] wrote ${count('.')} root pages, ${count('guide')} guide, ` +
    `${count('decisions')} decisions, ${count('research')} research, ` +
    `${count('reference')} reference, ${count('platform')} platform, ` +
    `${count('calculations')} calculations, ${count('salamandra')} salamandra.`,
);
if (warnings.length) {
  console.warn(`[gen-site] ${warnings.length} unresolved link warning(s):`);
  for (const w of warnings) console.warn(`  - ${w}`);
  if (STRICT) {
    const blocking = warnings.filter((w) => !isKnownForwardRef(w));
    if (blocking.length) {
      console.error(
        `[gen-site] STRICT: ${blocking.length} unresolved link(s) not declared as forward references.`,
      );
      process.exitCode = 1;
    }
  }
} else {
  console.log('[gen-site] no unresolved internal links.');
}
