import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { fileURLToPath } from 'node:url';
import { BASE, SITE, REPO } from './base.mjs';

// https://astro.build/config
export default defineConfig({
  site: SITE,
  base: BASE,
  vite: {
    build: {
      // Mermaid is deliberately lazy-loaded only on diagram pages. Its isolated
      // vendor chunk is larger than Vite's generic 500 kB advisory threshold.
      chunkSizeWarningLimit: 700,
    },
    resolve: {
      alias: {
        '@components': fileURLToPath(new URL('./src/components/', import.meta.url)),
      },
    },
  },
  integrations: [
    starlight({
      title: 'Salamandra',
      description:
        'Evidence-first 3D-printed FPV aircraft design: mission, measured hardware, mass skeleton, architecture trade and controlled CAD handoff.',
      favicon: '/favicon.svg',
      head: [
        {
          tag: 'meta',
          attrs: { name: 'theme-color', content: '#12161d' },
        },
      ],
      editLink: {
        baseUrl: `https://github.com/${REPO}/edit/main/`,
      },
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: `https://github.com/${REPO}`,
        },
      ],
      customCss: ['./src/styles/custom.css'],
      sidebar: [
        {
          label: 'Start here',
          items: [
            { label: 'Overview', link: '/' },
            { label: 'Getting started', link: '/guide/01-getting-started/' },
            { label: 'How to read the record', link: '/guide/02-how-to-read/' },
            { label: 'Engineering architecture', link: '/guide/03-architecture/' },
            { label: 'Drawings & SVG workflow', link: '/guide/06-drawings/' },
            { label: 'Glossary & notation', link: '/guide/04-glossary/' },
            { label: 'Contributing', link: '/guide/05-contributing/' },
          ],
        },
        {
          label: 'Current programme',
          items: [
            {
              label: 'Master Plan',
              link: '/reference/05-master-plan/',
              badge: { text: 'v2.4', variant: 'success' },
            },
            { label: 'Article #1 requirements', link: '/reference/00-objectives-and-requirements/' },
            { label: 'Hardware manifest', link: '/reference/17-article-1-hardware-manifest/' },
            {
              label: 'MP-04 campaign',
              link: '/research/i-33-mp04-propulsion-procurement-and-hardware-characterisation/',
              badge: { text: 'active', variant: 'caution' },
            },
            {
              label: 'H01–H22 protocol',
              link: '/tests/mp04-hardware-characterisation/',
              badge: { text: '0/22', variant: 'caution' },
            },
            { label: 'ADR redesign disposition', link: '/decisions/redesign-disposition/' },
          ],
        },
        {
          label: 'Historical v0.6 baseline',
          collapsed: true,
          items: [
            {
              label: 'Release v0.6.0',
              link: '/reference/16-release-v06/',
              badge: { text: 'history', variant: 'note' },
            },
            { label: 'Salamandra overview', link: '/salamandra/' },
            { label: 'Design guide v0.24', link: '/salamandra/design-guide/' },
            { label: 'Justification', link: '/salamandra/design-guide-justification/' },
            { label: 'Open points', link: '/salamandra/design-guide-open-points/' },
            { label: 'Generated drawings', link: '/guide/06-drawings/' },
          ],
        },
        {
          label: 'Evidence & decisions',
          collapsed: true,
          items: [
            { label: 'Decision index', link: '/decisions/' },
            { label: 'Research index', link: '/research/' },
            { label: 'Gap register', link: '/gaps/' },
            { label: 'Test programme', link: '/tests/' },
            { label: 'Measured references', link: '/reference/02-measured-references/' },
          ],
        },
        {
          label: 'Calculations',
          items: [
            { label: 'Tool index', link: '/calculations/' },
            { label: 'Reproduction guide', link: '/calculations/reproduction-guide/' },
          ],
        },
        {
          label: 'All decision records',
          collapsed: true,
          items: [{ autogenerate: { directory: 'decisions', collapsed: true } }],
        },
        {
          label: 'All research threads',
          collapsed: true,
          items: [{ autogenerate: { directory: 'research', collapsed: true } }],
        },
        {
          label: 'Plans & release archive',
          collapsed: true,
          items: [{ autogenerate: { directory: 'reference', collapsed: true } }],
        },
        {
          label: 'Project governance',
          collapsed: true,
          items: [
            { label: 'Project readme', link: '/platform/readme/' },
            { label: 'Changelog', link: '/platform/changelog/' },
            { label: 'Full contribution guide', link: '/platform/contributing/' },
            { label: 'AI working rules', link: '/platform/ai-context/' },
            { label: 'Documentation licence', link: '/platform/license-docs/' },
          ],
        },
      ],
    }),
  ],
});
