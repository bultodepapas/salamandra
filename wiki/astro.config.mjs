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
        'Open 3D-printed FPV aircraft engineering with a traceable design record, reproducible analyses and explicit physical acceptance gates.',
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
            { label: 'Glossary & notation', link: '/guide/04-glossary/' },
            { label: 'Contributing', link: '/guide/05-contributing/' },
          ],
        },
        {
          label: 'Current baseline',
          items: [
            {
              label: 'Current release',
              link: '/reference/11-release-v04/',
              badge: { text: 'v0.4.0', variant: 'success' },
            },
            { label: 'Salamandra overview', link: '/salamandra/' },
            { label: 'Design guide', link: '/salamandra/design-guide/' },
            { label: 'Justification', link: '/salamandra/design-guide-justification/' },
            {
              label: 'Open gates',
              link: '/salamandra/design-guide-open-points/',
              badge: { text: 'physical', variant: 'caution' },
            },
            { label: 'Test programme', link: '/tests/' },
          ],
        },
        {
          label: 'Evidence & decisions',
          collapsed: true,
          items: [
            { label: 'Decision index', link: '/decisions/' },
            { label: 'Research index', link: '/research/' },
            { label: 'Gap register', link: '/gaps/' },
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
