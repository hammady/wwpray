import type { PageServerLoad } from './$types';

// This function is called on the server before the page is loaded.
// it returns the data to be used by `+page.svelte` file.
// In static mode, it is called at build time.
export const load = (async () => {
	// read the JSON file, this wil soon be handled in a different way
	// possibly as a payload in the request
	const res = await import('./notified.json');

	return {
		...res.default
	};
}) satisfies PageServerLoad;
