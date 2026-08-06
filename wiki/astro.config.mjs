import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { fileURLToPath } from 'node:url';
import { BASE, SITE, REPO } from './base.mjs';

// https://astro.build/config
export default defineConfig({
  site: SITE,
  base: BASE,
  vite: {
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
        'Open 3D-printed FPV aircraft platform — the reasoning is the product. Design guide, ADRs, research threads, gaps and reproducible calculations.',
      favicon: '/favicon.svg',
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
          label: 'Guide',
          items: [
            { label: 'Getting started', link: '/guide/01-getting-started/' },
            { label: 'How to read this repo', link: '/guide/02-how-to-read/' },
            { label: 'Architecture', link: '/guide/03-architecture/' },
            { label: 'Glossary', link: '/guide/04-glossary/' },
            { label: 'Contributing', link: '/guide/05-contributing/' },
          ],
        },
        {
          label: 'Salamandra',
          items: [
            { label: 'Overview', link: '/salamandra/' },
            { label: 'Design guide v0.1', link: '/salamandra/design-guide/' },
            { label: 'Justification', link: '/salamandra/design-guide-justification/' },
            { label: 'Open points', link: '/salamandra/design-guide-open-points/' },
          ],
        },
        {
          label: 'Decisions (ADR)',
          collapsed: true,
          items: [{ autogenerate: { directory: 'decisions', collapsed: true } }],
        },
        {
          label: 'Research',
          collapsed: true,
          items: [{ autogenerate: { directory: 'research', collapsed: true } }],
        },
        { label: 'Gaps', link: '/gaps/' },
        { label: 'Tests', link: '/tests/' },
        {
          label: 'Calculations',
          items: [
            { label: 'Scripts', link: '/calculations/' },
            { label: 'Reproduction guide', link: '/calculations/reproduction-guide/' },
          ],
        },
        {
          label: 'Reference',
          collapsed: true,
          items: [{ autogenerate: { directory: 'reference', collapsed: true } }],
        },
        {
          label: 'Platform',
          items: [
            { label: 'Project readme', link: '/platform/readme/' },
            { label: 'Changelog', link: '/platform/changelog/' },
            { label: 'Contributing', link: '/platform/contributing/' },
            { label: 'AI working rules', link: '/platform/ai-context/' },
            { label: 'Licence', link: '/platform/license-docs/' },
          ],
        },
      ],
    }),
  ],
});
