import type { LayoutLoad } from './$types';

// Prerender the whole app at build time
export const prerender = true;

export const load = (async () => {
	return {};
}) satisfies LayoutLoad;
