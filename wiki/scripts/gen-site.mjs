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
  copyFileSync,
} from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { BASE, REPO, SITE } from '../base.mjs';

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
  s
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/^>\s?/gm, '')
    .replace(/\*\*|__|`/g, '')
    .replace(/\s+/g, ' ')
    .trim();

const tableCell = (s) => clean(s).replace(/\|/g, '\\|');

const extractTitle = (md) => {
  const m = md.match(/^#\s+(.+?)\s*$/m);
  return m ? m[1].trim() : null;
};

// Starlight renders the frontmatter title as the page H1. Canonical documents
// already begin with an H1. Some older research documents also use H1 for major
// sections, so their complete heading tree must move down one level at publish
// time. Code fences are left byte-for-byte unchanged.
const withoutSourceTitle = (md) => {
  const lines = md.split(/\r?\n/);
  let inFence = false;
  let firstTitleRemoved = false;
  let h1Count = 0;

  for (const line of lines) {
    if (!inFence && /^#\s+/.test(line)) h1Count += 1;
    if (/^\s*(?:```|~~~)/.test(line)) inFence = !inFence;
  }

  inFence = false;
  const normalized = lines.flatMap((line) => {
    if (/^\s*(?:```|~~~)/.test(line)) {
      inFence = !inFence;
      return [line];
    }
    if (!inFence && /^#\s+/.test(line) && !firstTitleRemoved) {
      firstTitleRemoved = true;
      return [];
    }
    if (!inFence && h1Count > 1 && /^(#{1,5})\s+/.test(line)) return [`#${line}`];
    return [line];
  });

  return normalized.join('\n').replace(/^\s*\n/, '');
};

const extractLeadParagraph = (md) => {
  const paragraph = md
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .find(
      (p) =>
        p.length >= 40 &&
        !/^(?:#|\||---|```|>|\*\*[^*\n]+:\*\*)/.test(p),
    );
  return paragraph ? clean(paragraph).slice(0, 320) : '';
};

const extractDescription = (md) => {
  const status = extractField(md, 'Status');
  return status ? clean(status) : extractLeadParagraph(md);
};

function extractField(md, labelPattern) {
  const re = new RegExp(
    `\\*\\*(?:${labelPattern}):\\*\\*\\s*([\\s\\S]*?)(?=` +
      `\\s*(?:·\\s*)?\\*\\*[A-Z][^*\\n]*:\\*\\*|\\n\\s*\\n|\\n---|\\n#{1,6}\\s|$)`,
    'i',
  );
  return md.match(re)?.[1]?.trim() || '';
}

const frontmatter = (title, description, editUrl) =>
  `---\ntitle: ${JSON.stringify(title)}\ndescription: ${JSON.stringify(
    description || '',
  )}\neditUrl: ${JSON.stringify(editUrl)}\n---\n\n`;

// ---------------------------------------------------------------------------
// release metadata, derived from canonical sources to prevent wiki-only drift

const DESIGN_GUIDE_SOURCE = 'design/Salamandra-Design-Guide-v0.1.md';
const designGuideMd = readAbs(DESIGN_GUIDE_SOURCE);
const GUIDE_VERSION = designGuideMd.match(/\*\*Version\s+([0-9.]+)\*\*/)?.[1] || 'unknown';

const releaseDocs = readdirSync(path.join(ROOT, 'docs'))
  .filter((f) => /release-v[0-9.]+\.md$/i.test(f))
  .map((file) => {
    const md = readAbs(`docs/${file}`);
    const tag = md.match(/\*\*Tag:\*\*\s*`(v\d+\.\d+\.\d+)`/)?.[1];
    return tag ? { file, md, tag, version: tag.slice(1).split('.').map(Number) } : null;
  })
  .filter(Boolean)
  .sort((a, b) => {
    for (let i = 0; i < 3; i += 1) {
      if (a.version[i] !== b.version[i]) return b.version[i] - a.version[i];
    }
    return 0;
  });

if (!releaseDocs.length) throw new Error('No tagged release document found in docs/.');
const CURRENT_RELEASE = releaseDocs[0];

const correctionNumbers = [...readAbs('CHANGELOG.md').matchAll(/\bC(\d{1,3})\b/g)].map(
  (m) => Number(m[1]),
);
const LATEST_CORRECTION = correctionNumbers.length ? Math.max(...correctionNumbers) : 0;
const ADR_FILE_COUNT = readdirSync(path.join(ROOT, 'decisions')).filter((f) =>
  /^ADR-\d{4}.*\.md$/.test(f),
).length;
const RESEARCH_FILE_COUNT = readdirSync(path.join(ROOT, 'research')).filter((f) =>
  /^I-\d{2}.*\.md$/.test(f),
).length;
const SCRIPT_FILE_COUNT = readdirSync(path.join(ROOT, 'calculations')).filter((f) =>
  f.endsWith('.py'),
).length;

// ---------------------------------------------------------------------------
// mount table: canonical source (repo-relative posix path) -> destination

const mounted = new Map(); // srcRel -> { dest }

const add = (srcRel, dest) => mounted.set(srcRel, { dest });

add(DESIGN_GUIDE_SOURCE, 'salamandra/design-guide.md');
add('design/Salamandra-Design-Guide-Advanced-v0.1.md', 'salamandra/design-guide-advanced.md');
add('design/Design-Guide-Justification-v0.1.md', 'salamandra/design-guide-justification.md');
add('design/Design-Guide-Open-Points-v0.1.md', 'salamandra/design-guide-open-points.md');
add(
  'design/Low-Speed-Trim-Redesign-and-E2A-Plan.md',
  'salamandra/low-speed-trim-redesign-and-e2a-plan.md',
);
add(
  'design/NF-Design-Guide-2024-Consolidated-Audit-and-Release-Programme.md',
  'salamandra/nf-design-guide-consolidated-audit-and-release-programme.md',
);
add(
  'design/NF-Design-Guide-2024-Repository-Audit-Part-06-Design-Method-Synthesis.md',
  'salamandra/nf-design-guide-part-06-design-method-synthesis.md',
);
add(
  'design/NF-Design-Guide-2024-Repository-Audit.md',
  'salamandra/nf-design-guide-repository-audit.md',
);
add(
  'design/NF-Design-Guide-2024-Repository-Audit-Part-02-Airfoil-Trim.md',
  'salamandra/nf-design-guide-part-02-airfoil-trim.md',
);
add(
  'design/NF-Design-Guide-2024-Repository-Audit-Part-03-Directional-Stability.md',
  'salamandra/nf-design-guide-part-03-directional-stability.md',
);
add(
  'design/NF-Design-Guide-2024-Repository-Audit-Part-04-Structure-Aeroelasticity.md',
  'salamandra/nf-design-guide-part-04-structure-aeroelasticity.md',
);
add(
  'design/NF-Design-Guide-2024-Repository-Audit-Part-05-Wingtips-Drag-Flaps.md',
  'salamandra/nf-design-guide-part-05-wingtips-drag-flaps.md',
);

for (const f of readdirSync(path.join(ROOT, 'decisions'))
  .filter((f) => /^ADR-\d{4}.*\.md$/.test(f))
  .sort()) {
  add(`decisions/${f}`, `decisions/${f.toLowerCase()}`);
}
add('decisions/README.md', 'decisions/overview.md');
add('decisions/REDESIGN-DISPOSITION.md', 'decisions/redesign-disposition.md');

for (const f of readdirSync(path.join(ROOT, 'research'))
  .filter((f) => /^I-\d{2}.*\.md$/.test(f))
  .sort()) {
  add(`research/${f}`, `research/${f.toLowerCase()}`);
}
add('research/README.md', 'research/overview.md');
add('first_investigation.md', 'research/first-investigation.md');

add('gaps/README.md', 'gaps/index.md');
add('tests/README.md', 'tests/index.md');
add(
  'tests/E2A-printed-section-polars/README.md',
  'tests/e2a-printed-section-polars.md',
);
add(
  'tests/MP04-hardware-characterisation/README.md',
  'tests/mp04-hardware-characterisation.md',
);
add('calculations/README.md', 'calculations/reproduction-guide.md');
add(
  'calculations/trim_redesign_out/README.md',
  'calculations/trim-redesign-output.md',
);
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
// generated SVG drawing set
//
// geometry/drawings/manifest.json is written by calculations/drawing_index.py
// from the same run that renders the sheets. The wiki never re-describes a
// drawing: it publishes what the manifest says, so a regenerated drawing set
// updates the served page with no manual edit.

const DRAWINGS_SRC = path.join(ROOT, 'geometry', 'drawings');
const DRAWING_MANIFEST = path.join(DRAWINGS_SRC, 'manifest.json');

function readDrawingManifest() {
  if (!existsSync(DRAWING_MANIFEST)) {
    throw new Error(
      'geometry/drawings/manifest.json is missing; run python3 calculations/generate_blueprints.py',
    );
  }
  const manifest = JSON.parse(readFileSync(DRAWING_MANIFEST, 'utf8'));
  if (manifest.schema !== 1) {
    throw new Error(`unsupported drawing manifest schema ${manifest.schema}`);
  }
  if (!Array.isArray(manifest.sheets) || !manifest.sheets.length) {
    throw new Error('drawing manifest declares no sheets');
  }
  return manifest;
}

const drawingManifest = readDrawingManifest();
const drawingUrl = (file) => `${BASE}drawings/${file}`;

function renderDrawingGallery() {
  return drawingManifest.sheets
    .map((sheet) => {
      const url = drawingUrl(sheet.file);
      return (
        `### ${sheet.number} · ${sheet.heading}\n\n` +
        `[![${sheet.description}](${url})](${url})\n\n` +
        `${sheet.note}\n\n` +
        `**Sheet** ${sheet.scale} · **Authority** ${sheet.authority}.`
      );
    })
    .join('\n\n');
}

// ---------------------------------------------------------------------------
// URL resolution

const destToUrl = (dest) => {
  const dir = path.posix.dirname(dest);
  // Starlight removes dots from generated slugs (e.g. release-v0.4 -> release-v04).
  // Mirror that normalization here so generated cross-links match built routes.
  const baseName = path.posix
    .basename(dest)
    .replace(/\.(md|mdx)$/, '')
    .replace(/\./g, '');
  const slug = baseName === 'index' ? '' : baseName + '/';
  return BASE + (dir === '.' ? '' : dir + '/') + slug;
};

const CURRENT_RELEASE_DEST = `reference/${CURRENT_RELEASE.file.toLowerCase()}`;
const CURRENT_RELEASE_PAGE = destToUrl(CURRENT_RELEASE_DEST)
  .slice(BASE.length)
  .replace(/\/+$/, '');
const metadataTokens = new Map([
  ['BASE', BASE],
  ['GUIDE_VERSION', GUIDE_VERSION],
  ['RELEASE_TAG', CURRENT_RELEASE.tag],
  ['CURRENT_RELEASE_URL', destToUrl(CURRENT_RELEASE_DEST)],
  ['LATEST_CORRECTION', String(LATEST_CORRECTION)],
  ['ADR_FILE_COUNT', String(ADR_FILE_COUNT)],
  ['RESEARCH_FILE_COUNT', String(RESEARCH_FILE_COUNT)],
  ['SCRIPT_FILE_COUNT', String(SCRIPT_FILE_COUNT)],
  ['DRAWINGS', renderDrawingGallery()],
]);

function expandTokens(md) {
  return md.replace(/\{\{([A-Z0-9_]+)\}\}/g, (match, key) => {
    if (!metadataTokens.has(key)) {
      warn(`Unknown wiki metadata token ${match}`);
      return match;
    }
    return metadataTokens.get(key);
  });
}

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

    // canonical drawings are served from the copied public/drawings/ folder
    if (/^geometry\/drawings\/[^/]+\.svg$/.test(norm)) {
      return '](' + drawingUrl(path.posix.basename(norm)) + anchor + ')';
    }

    // other canonical geometry files (drawing contract, airfoil coordinates) are
    // not served pages: link them to the repository so traceability survives.
    if (/^geometry\//.test(norm)) {
      return '](' + `https://github.com/${REPO}/blob/main/${norm}` + anchor + ')';
    }

    // Large reference PDFs are intentionally excluded from the generated site.
    // Preserve their evidence links through the repository source view.
    if (/^INSPIRATION\//.test(norm)) {
      return '](' + `https://github.com/${REPO}/blob/main/${norm}` + anchor + ')';
    }

    if (base.endsWith('.py')) {
      if (norm.startsWith('calculations/')) {
        // A line reference (#L67, #L26-L28) resolves only in the repository
        // source view. Carrying it onto the generated reproduction guide, which
        // has no such anchor, produced 14 built-site integrity failures from
        // docs/12 alone: the evidence links of an audit document, broken by the
        // rewrite that was meant to preserve them (C51). Line-anchored script
        // links therefore go to the file itself; plain ones keep the guide.
        if (/^#L\d/.test(anchor)) {
          return '](' + `https://github.com/${REPO}/blob/main/${norm}` + anchor + ')';
        }
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
    writeOut(spec.dest, frontmatter(title, desc, EDIT + srcRel) + withoutSourceTitle(md));
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
    const source = readFileSync(path.join(CONTENT, ...relFull.split('/')), 'utf8').replace(/^\uFEFF/, '');
    const md = rewriteLinks(expandTokens(source), siteDir);
    const dest = relFull === 'home.md' ? 'index.md' : relFull;
    writeOut(dest, md);
  }
}

// ---------------------------------------------------------------------------
// header parser shared by the generated index tables

function parseHeader(srcRel) {
  const md = readAbs(srcRel);
  const title = extractTitle(md) || '';
  const status = extractField(md, 'Status');
  const confidence = extractField(md, 'Confidence');
  const reversible = extractField(md, 'Reversible');
  return { title, status, confidence, reversible };
}

const indexPage = (title, desc, body) =>
  frontmatter(title, desc, EDIT + 'wiki/scripts/gen-site.mjs') + withoutSourceTitle(body);

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
        `| [ADR-${r.num}](${r.url}) | ${tableCell(r.title.replace(/^ADR-\d{4}\s*—\s*/, ''))} | ${tableCell(r.status) || '—'} | ${tableCell(r.confidence) || '—'} | ${tableCell(r.reversible) || '—'} |`,
    )
    .join('\n');
  writeOut(
    'decisions/index.md',
    indexPage(
      'Engineering decisions (ADR)',
      `Auto-generated index of ${rows.length} published decision records, including their current status and confidence.`,
      `# Decision record (ADR)

Use this index when the question is **“Why did the design adopt this choice?”** Each
record states the context, alternatives, decision, consequences, confidence and review
trigger. A provisional or disputed record is not equivalent to an active, high-confidence
decision.

> Generated from \`decisions/\` at build time. The [record overview](./overview/)
> also lists intentionally missing historical numbers and superseded decisions.

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
      const status = extractField(md, 'Status');
      const closes = extractField(md, '(?:Partially )?Closes');
      const feeds = extractField(md, 'Feeds');
      const num = f.match(/^I-(\d{2})/)?.[1] || '';
      return {
        num,
        title: tableCell(title.replace(/^I-\d{2}\s*—\s*/, '')),
        status: tableCell(status),
        closes: tableCell(closes),
        feeds: tableCell(feeds),
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

Use this index when the question is **“What evidence and analysis support the record?”**
A research thread documents its question, method, sources, findings and limitations. It
does not make the final design decision; that belongs in the [ADR index](../decisions/).

> Generated from \`research/\` at build time. Status, closure and downstream consumers
> are parsed from each thread's metadata block.

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
    ['Historical Design Guide', 'design-guide', `Version ${GUIDE_VERSION}: reproducible v0.6 CAD geometry under the Master Plan hold.`],
    ['Justification', 'design-guide-justification', 'Derivations, evidence and sources behind the historical candidate values.'],
    ['Open points', 'design-guide-open-points', 'Unresolved v0.6 assumptions and physical acceptance gates retained for comparison.'],
  ];
  const table = items
    .map(([label, slug, desc]) => `| [${label}](${slug}/) | ${desc} |`)
    .join('\n');
  writeOut(
    'salamandra/index.md',
    indexPage(
      'Salamandra — historical v0.6 candidate',
      'The reproducible forward-swept v0.6 comparison baseline retained under the Master Plan redesign.',
      `# Salamandra historical v0.6 candidate

Salamandra is the platform's first reference aircraft: a modular PETG forward-swept
flying wing with a common CORE and interchangeable PANEL wings. The tagged
**${CURRENT_RELEASE.tag} / Design Guide v${GUIDE_VERSION}** package remains internally
reproducible, but the Master Plan v2.4 treats it as candidate A rather than the selected
redesign. Its former **≤ 1.15 Wh/km at 95 km/h** objective is now only the E3 continuity
comparator.

> This release is an audit and comparison baseline, **not current production-CAD
> authority or flight qualification**. Begin new work with the
> [Master Plan](${destToUrl('reference/05-master-plan.md')}); use the
> [v0.6 release notes](${destToUrl(CURRENT_RELEASE_DEST)}) to reconstruct historical work.

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
      const isRelease = /release-v/i.test(f);
      const role = f === CURRENT_RELEASE.file
        ? 'Latest tagged release — historical baseline'
        : isRelease
          ? 'Historical release'
          : f.toLowerCase() === 'readme.md'
            ? 'Directory map'
            : 'Project reference';
      return {
        title: tableCell(title),
        url,
        role,
        // A document's status belongs in its body; the index summary should say
        // what the document contains. This is especially important for releases,
        // where a summary of merely "RELEASED" is not useful navigation.
        desc: tableCell(extractLeadParagraph(md) || extractDescription(md)),
      };
    });
  const table = rows
    .map((r) => `| [${r.title}](${r.url}) | ${r.role} | ${r.desc || '—'} |`)
    .join('\n');
  writeOut(
    'reference/index.md',
    indexPage(
      'Reference documents',
      `The Master Plan, active specifications, conventions and historical ${CURRENT_RELEASE.tag} release record.`,
      `# Reference documents

Controlled specifications, conventions, plans and release history. Start with the
**Master Design Plan** and active Article #1 requirements. The latest tagged release is
the reproducible v0.6 comparison baseline; it is not production authority for the
redesign, and older release notes remain audit records.

> Generated from \`docs/\` at build time.

| Document | Role | Summary |
|---|---|---|
${table}
`,
    ),
  );
}

function genCalculationsIndex() {
  const reproductionGuide = readAbs('calculations/README.md');
  const descriptionFromGuide = (file) => {
    const escaped = file.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const description = reproductionGuide.match(
      new RegExp('^\\| `' + escaped + '` \\| ([^|]+) \\|', 'm'),
    )?.[1];
    return description ? clean(description) : '';
  };
  const scripts = readdirSync(path.join(ROOT, 'calculations'))
    .filter((f) => f.endsWith('.py'))
    .sort()
    .map((f) => {
      const abs = path.join(ROOT, 'calculations', f);
      const src = readFileSync(abs, 'utf8');
      const doc = src.match(/^(?:#![^\n]*\n)?\s*"""([\s\S]*?)"""/)?.[1] || '';
      const summary =
        doc
          .split('\n')
          .map((l) => l.trim())
          .filter(Boolean)[0] || '';
      return {
        f,
        // The reproduction guide is the maintained English catalog. Fall back
        // to the Python module docstring for a newly added, not-yet-documented tool.
        summary: tableCell(descriptionFromGuide(f) || clean(summary)),
      };
    });
  const table = scripts
    .map((s) => `| \`${s.f}\` | ${s.summary} |`)
    .join('\n');
  writeOut(
    'calculations/index.md',
    indexPage(
      'Reproducible calculations',
      `Auto-generated index of ${scripts.length} validated, rerunnable analysis scripts.`,
      `# Reproducible calculations

Derived values in the active contracts and historical design are produced by rerunnable
Python analyses.
Measured inputs retain source provenance; estimates remain explicitly tagged and are not
made more certain merely because a script propagates them.

> Generated from \`calculations/\` at build time. Read the [reproduction guide](./reproduction-guide/)
> for tool versions, inputs, external XFOIL gates and validation discipline.

## Start with the system contract

\`\`\`bash
python calculations/verify_calculations.py
python calculations/verify_calculations.py --fast
python calculations/mutation_test.py
\`\`\`

The default verifier checks cross-module equality and executes every deterministic local
command-line analysis. \`--fast\` restricts it to the interface contracts; the mutation
campaign proves that deliberate defects are detected. XFOIL and physical tests remain
explicit external gates.

## High-value entry points

\`\`\`bash
python calculations/mission_contract.py          # active Article #1 mission
python calculations/hardware_manifest.py         # M1 candidate interface
python calculations/hardware_candidate_trade.py # MP-04 procurement screen
python calculations/hardware_measurements.py --check
python calculations/generate_hardware_dummies.py --check
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
    ['changelog', `Change log (corrections through C${LATEST_CORRECTION})`],
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
// llms.txt — site map for AI agents, generated per the llmstxt.org spec:
// H1 + blockquote summary + H2 sections of markdown hyperlinks [name](url): notes.

function genLlmsTxt() {
  const section = (title, items) => {
    if (!items.length) return [];
    return ['', `## ${title}`, ''].concat(
      items.map(([label, page, note]) => {
        const url = pagePaths.get(page);
        const absoluteUrl = url ? new URL(url, new URL(SITE).origin).href : null;
        return absoluteUrl ? `- [${label}](${absoluteUrl})${note ? `: ${note}` : ''}` : null;
      }).filter(Boolean),
    );
  };
  const lines = [
    '# Salamandra',
    '',
    '> Evidence-first, community-driven 3D-printed FPV aircraft programme. The reasoning is the product:',
    '> every decision carries its rationale, source and provenance tag (`[M]`/`[D]`/`[E]`/`[I]`).',
    '> Derived values are rerunnable; measured inputs retain provenance; unresolved assumptions remain visible.',
    ...section('Getting started', [
      ['Getting started', 'guide/01-getting-started', 'The shortest path from zero to a working model'],
      ['How to read this repository', 'guide/02-how-to-read', 'Folder map and traceability flow'],
      ['Architecture', 'guide/03-architecture', 'How research, decisions, gaps, tests and calculations feed each other'],
      ['Drawings and SVG workflow', 'guide/06-drawings', 'Generated A3 design-review sheets and their authority boundary'],
      ['Glossary', 'guide/04-glossary', 'Confidence tags, identifiers, signs and key terms'],
      ['Contributing', 'guide/05-contributing', 'Order of value of contributions and the workflow'],
    ]),
    ...section('Design', [
      ['Master Design Plan', 'reference/05-master-plan', 'Programme sequence, gates and current authorization'],
      ['MP-04 campaign', 'research/i-33-mp04-propulsion-procurement-and-hardware-characterisation', 'Current procurement and physical-characterisation work'],
      ['H01–H22 protocol', 'tests/mp04-hardware-characterisation', 'Machine-readable physical evidence and closure method'],
      ['Historical Salamandra v0.6', 'salamandra', 'The forward-swept comparison candidate retained for audit'],
      [`Historical Design Guide v${GUIDE_VERSION}`, 'salamandra/design-guide', `Reproducible ${CURRENT_RELEASE.tag} geometry under hold`],
    ]),
    ...section('Reference', [
      ['Decision record (ADR)', 'decisions', 'One file per decision: context, alternatives, consequences'],
      ['Research threads', 'research', 'What was searched, found, and with what sources'],
      ['Gap register', 'gaps', 'What we do not know and how it gets closed'],
      ['Experimental program', 'tests', 'The tests that turn estimates into measurements'],
      ['Calculations', 'calculations', 'Validated, rerunnable analysis scripts'],
      ['Reproduction guide', 'calculations/reproduction-guide', 'Commands and validation discipline'],
      ['Objectives and requirements', 'reference/00-objectives-and-requirements', 'The active Gate-M0 product contract'],
      ['Hardware and power manifest', 'reference/17-article-1-hardware-manifest', 'The active pre-measurement M1 interface'],
      [`Historical release ${CURRENT_RELEASE.tag}`, CURRENT_RELEASE_PAGE, 'Latest tagged comparison package and migration record'],
      ['Historical Phase-1 plan', 'reference/03-phase-1-plan', 'Superseded geometry and stability work sequence'],
    ]),
    ...section('Platform', [
      ['Project readme', 'platform/readme', 'Status and full navigation'],
      ['Changelog', 'platform/changelog', `Correction record through C${LATEST_CORRECTION}`],
      ['Contributing', 'platform/contributing', 'Full contribution guide'],
    ]),
    ...section('Optional', [
      ['First investigation', 'research/first-investigation', 'The original Rev 1.0 research'],
      ['AI working rules', 'platform/ai-context', 'The rules AI assistants follow here'],
      ['Documentation licence', 'platform/license-docs', 'CC BY-SA 4.0'],
    ]),
  ];
  const out = path.join(WIKI, 'public', 'llms.txt');
  mkdirSync(path.dirname(out), { recursive: true });
  writeFileSync(out, lines.join('\n') + '\n', 'utf8');
  console.log('[gen-site] regenerated llms.txt per the llmstxt.org spec.');
}

function copyDrawings() {
  const source = DRAWINGS_SRC;
  const destination = path.join(WIKI, 'public', 'drawings');
  if (!existsSync(source)) {
    throw new Error('canonical geometry/drawings directory is missing');
  }
  const drawings = readdirSync(source).filter((name) => name.endsWith('.svg')).sort();
  if (!drawings.length) {
    throw new Error('canonical geometry/drawings directory contains no SVG sheets');
  }
  // Publication gate: the served sheets must be exactly the sheets the manifest
  // describes, byte for byte. A stale manifest fails the build instead of
  // shipping a page that describes a drawing nobody can see.
  const declared = drawingManifest.sheets.map((sheet) => sheet.file).sort();
  if (declared.join('|') !== drawings.join('|')) {
    throw new Error(
      `drawing manifest lists [${declared}] but geometry/drawings holds [${drawings}]; ` +
        'run python3 calculations/generate_blueprints.py',
    );
  }
  for (const sheet of drawingManifest.sheets) {
    const bytes = readFileSync(path.join(source, sheet.file));
    const digest = createHash('sha256').update(bytes).digest('hex');
    if (digest !== sheet.sha256) {
      throw new Error(
        `${sheet.file} does not match its manifest digest; ` +
          'run python3 calculations/generate_blueprints.py',
      );
    }
  }
  rmSync(destination, { recursive: true, force: true });
  mkdirSync(destination, { recursive: true });
  for (const drawing of drawings) {
    copyFileSync(path.join(source, drawing), path.join(destination, drawing));
  }
  console.log(`[gen-site] copied ${drawings.length} manifest-verified SVG drawing(s).`);
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
copyDrawings();
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
