// Verify every internal navigation link in the production Astro output.
// This complements source-level reference checks by catching routing transforms
// such as Starlight's dot removal from generated slugs.

import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { BASE } from '../base.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DIST = path.resolve(HERE, '..', 'dist');
const ORIGIN = 'https://built-site.invalid';

if (!existsSync(DIST)) {
  console.error('[check-built-links] wiki/dist does not exist; run npm run build first.');
  process.exit(1);
}

const htmlFiles = [];
const walk = (dir) => {
  for (const entry of readdirSync(dir)) {
    const absolute = path.join(dir, entry);
    if (statSync(absolute).isDirectory()) walk(absolute);
    else if (entry.endsWith('.html')) htmlFiles.push(absolute);
  }
};
walk(DIST);

const routeForFile = (file) => {
  const relative = path.relative(DIST, file).split(path.sep).join('/');
  if (relative === 'index.html') return BASE;
  if (relative.endsWith('/index.html')) return BASE + relative.slice(0, -'index.html'.length);
  return BASE + relative;
};

const candidateFiles = (pathname) => {
  const relative = decodeURIComponent(pathname.slice(BASE.length)).replace(/^\/+/, '');
  if (!relative) return [path.join(DIST, 'index.html')];
  if (relative.endsWith('/')) return [path.join(DIST, ...relative.split('/'), 'index.html')];
  return [
    path.join(DIST, ...relative.split('/')),
    path.join(DIST, ...`${relative}.html`.split('/')),
    path.join(DIST, ...relative.split('/'), 'index.html'),
  ];
};

const htmlCache = new Map();
const readHtml = (file) => {
  if (!htmlCache.has(file)) htmlCache.set(file, readFileSync(file, 'utf8'));
  return htmlCache.get(file);
};
const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const failures = new Set();
let checked = 0;

for (const sourceFile of htmlFiles) {
  const sourceHtml = readHtml(sourceFile);
  const sourceRoute = routeForFile(sourceFile);
  const h1Count = [...sourceHtml.matchAll(/<h1\b/gi)].length;
  if (h1Count !== 1) failures.add(`${sourceRoute} has ${h1Count} H1 elements; expected exactly one`);
  if (!/<html\b[^>]*\blang=["']en["']/i.test(sourceHtml)) {
    failures.add(`${sourceRoute} does not declare lang="en"`);
  }
  if (!/<title>[^<]+<\/title>/i.test(sourceHtml)) {
    failures.add(`${sourceRoute} has no non-empty document title`);
  }
  const links = sourceHtml.matchAll(/<a\b[^>]*\bhref=["']([^"']+)["']/gi);

  for (const match of links) {
    const href = match[1];
    if (/^(?:mailto:|tel:|javascript:|data:)/i.test(href)) continue;

    let targetUrl;
    try {
      targetUrl = new URL(href, ORIGIN + sourceRoute);
    } catch {
      failures.add(`${sourceRoute} -> malformed URL: ${href}`);
      continue;
    }
    if (targetUrl.origin !== ORIGIN) continue;
    checked += 1;

    if (!targetUrl.pathname.startsWith(BASE)) {
      failures.add(`${sourceRoute} -> ${href} escapes deployment base ${BASE}`);
      continue;
    }

    const targetFile = candidateFiles(targetUrl.pathname).find((file) => existsSync(file));
    if (!targetFile) {
      failures.add(`${sourceRoute} -> ${href} has no built target`);
      continue;
    }

    if (targetUrl.hash) {
      const fragment = decodeURIComponent(targetUrl.hash.slice(1));
      const id = escapeRegExp(fragment);
      if (!new RegExp(`(?:id|name)=["']${id}["']`).test(readHtml(targetFile))) {
        failures.add(`${sourceRoute} -> ${href} has no matching anchor`);
      }
    }
  }
}

if (failures.size) {
  console.error(`[check-built-links] ${failures.size} built-site integrity failure(s):`);
  for (const failure of [...failures].sort()) console.error(`  - ${failure}`);
  process.exit(1);
}

console.log(
  `[check-built-links] ${checked} internal links and semantic page shells across ` +
    `${htmlFiles.length} HTML pages: OK.`,
);
