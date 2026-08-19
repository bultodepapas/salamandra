// Single source of truth for the wiki's deployment identity.
// Change the repository once here; the generator and the Astro config both read it.
export const REPO = 'bultodepapas/salamandra';
const [OWNER, NAME] = REPO.split('/');
export const SITE = `https://${OWNER}.github.io/${NAME}/`;
export const BASE = `/${NAME}/`;
