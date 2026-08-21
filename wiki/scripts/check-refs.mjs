// check-refs.mjs — referential integrity checker for the reasoning repository.
//
// Two guarantees:
//  1. Every inline markdown link in the repo that targets a local `.md` file
//     must resolve to a real file. Broken traceability links are errors.
//  2. Every bare mention of a record identifier (`ADR-XXXX`, `I-XX`, `GX`, `EX`,
//     `E0X`) must resolve to an existing record. Unknown identifiers fail in
//     strict mode. `E` is three registers: unpadded tests, Gate-M0 efficiency
//     states E0--E3 and zero-padded equipment item references.
//
// Exit code 1 when there are broken links, so CI can gate on it.
//
// Usage: node wiki/scripts/check-refs.mjs [--strict]

import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const posix = (p) => p.split(path.sep).join('/');
const STRICT = process.argv.includes('--strict');

const SKIP_DIRS = new Set([
  '.git',
  '.codebase-memory',
  'node_modules',
  'dist',
  '.astro',
  'other_planes', // heavy reference assets, not documentation
  'INSPIRATION',
]);
const SKIP_PREFIXES = ['wiki/src/content/docs', 'wiki/dist', 'wiki/node_modules', 'wiki/.astro'];

// ---------------------------------------------------------------------------
// known record sets

const listIds = (dir, re) =>
  new Set(
    readdirSync(path.join(ROOT, ...dir.split('/')))
      .filter((f) => re.test(f))
      .map((f) => f.match(re)[1]),
  );

const ADR_IDS = listIds('decisions', /^ADR-(\d{4})/);
const I_IDS = listIds('research', /^I-(\d{2})/);

const tableIds = (rel, re) => {
  const out = new Set();
  const md = readFileSync(path.join(ROOT, ...rel.split('/')), 'utf8');
  for (const m of md.matchAll(re)) out.add(m[1]);
  return out;
};
const G_IDS = tableIds('gaps/README.md', /\*\*G(\d{1,2})\*\*/g);
const E_IDS = tableIds('tests/README.md', /\*\*E(\d{1,2})\*\*/g);
const MISSION_E_IDS = tableIds(
  'calculations/mission_contract.py',
  /identifier="E(\d)_/g,
);

// The `E` prefix carries three registers: tests are written unpadded
// (E1...E9, tests/README.md), Gate-M0 efficiency states are E0...E3, and
// controlled equipment item balloons are written zero-padded (E01...E21).
// Mission states are read from mission_contract.py; equipment items are read
// from the canonical mass-skeleton reference map. An unknown reference still
// fails instead of being silently accepted.
// Retired numbers (E02/E03) count as known: they are deliberately never reused,
// so text that explains the retirement must not be reported as a broken record.
const EQUIPMENT_IDS = tableIds('calculations/generate_blueprints.py', /"E(\d{2})"/g);

// historical records that are intentionally fileless (kept for the record):
// superseded ADR numbers (decisions/README "Superseded or cancelled") and
// withdrawn tests (tests/README "Withdrawn").
const listCells = (rel, re) => {
  const out = [];
  const md = readFileSync(path.join(ROOT, ...rel.split('/')), 'utf8');
  for (const m of md.matchAll(re)) {
    for (const cell of m[1].split(',')) out.push(cell.trim());
  }
  return out;
};
for (const n of listCells('decisions/README.md', /^\| ([0-9,\s]+) \|/gm)) ADR_IDS.add(n);
for (const n of tableIds('tests/README.md', /^\| (E\d{1,2}) \|/gm)) E_IDS.add(n.replace('E', ''));

// ---------------------------------------------------------------------------
// scan

const errors = [];
const warnings = [];
const files = [];

function walk(rel) {
  const abs = path.join(ROOT, ...rel.split('/'));
  for (const entry of readdirSync(abs)) {
    const relFull = rel ? `${rel}/${entry}` : entry;
    const absFull = path.join(ROOT, ...relFull.split('/'));
    if (SKIP_DIRS.has(entry)) continue;
    if (SKIP_PREFIXES.some((p) => posix(relFull).startsWith(p))) continue;
    if (statSync(absFull).isDirectory()) {
      walk(relFull);
    } else if (entry.endsWith('.md') || entry.endsWith('.mdx')) {
      files.push(relFull);
    }
  }
}
walk('');

for (const rel of files) {
  const abs = path.join(ROOT, ...rel.split('/'));
  const md = readFileSync(abs, 'utf8');
  const dir = path.posix.dirname(posix(rel));

  // 1. inline links to local .md files
  for (const m of md.matchAll(/\]\(([^()\s]+\.(?:md|mdx))(#[^)]*)?\)/g)) {
    const href = m[1];
    if (/^(https?:|mailto:|#|\/)/.test(href)) continue;
    const resolved = path.resolve(ROOT, dir, href);
    if (!existsSync(resolved)) {
      errors.push(`broken link in ${rel}: ${href}`);
    }
  }

  // 2. bare record identifiers
  for (const m of md.matchAll(/\bADR-(\d{4})\b/g)) {
    if (!ADR_IDS.has(m[1])) warnings.push(`unknown ADR-${m[1]} in ${rel}`);
  }
  for (const m of md.matchAll(/\bI-(\d{2})\b/g)) {
    if (!I_IDS.has(m[1])) warnings.push(`unknown I-${m[1]} in ${rel}`);
  }
  for (const m of md.matchAll(/\bG(\d{1,2})\b/g)) {
    if (!G_IDS.has(m[1])) warnings.push(`unknown G${m[1]} in ${rel}`);
  }
  for (const m of md.matchAll(/\bE(\d{1,2})\b/g)) {
    // padded -> equipment item. Unpadded E0--E3 can be a Gate-M0 mission state;
    // the test register independently uses E1...E9.
    const known = m[1].length === 2
      ? EQUIPMENT_IDS.has(m[1])
      : E_IDS.has(m[1]) || MISSION_E_IDS.has(m[1]);
    if (!known) warnings.push(`unknown E${m[1]} in ${rel}`);
  }
}

// ---------------------------------------------------------------------------

console.log(`[check-refs] scanned ${files.length} markdown files.`);
console.log(
  `[check-refs] known records: ${ADR_IDS.size} ADR, ${I_IDS.size} I, ${G_IDS.size} G, ` +
    `${E_IDS.size} E tests, ${MISSION_E_IDS.size} E mission states, ` +
    `${EQUIPMENT_IDS.size} E equipment items.`,
);

if (warnings.length) {
  console.warn(
    `[check-refs] ${warnings.length} unknown identifier warning(s)` +
      `${STRICT ? ' (strict mode: blocking)' : ''}:`,
  );
  for (const w of [...new Set(warnings)].slice(0, 40)) console.warn(`  - ${w}`);
}
if (errors.length) {
  console.error(`[check-refs] ${errors.length} broken link(s):`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exitCode = 1;
} else if (STRICT && warnings.length) {
  process.exitCode = 1;
} else {
  console.log('[check-refs] no broken local links.');
}
