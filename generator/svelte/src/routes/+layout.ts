import { browser } from '$app/environment';
import type { TMasjidsJSON } from '$lib/types';
import entries from 'lodash/entries';
import type { LayoutLoad } from './$types';

export const prerender = true;

export const load: LayoutLoad = async () => {
	const data = (await import('./notified.json')) as TMasjidsJSON;
	const searchParams = browser ? new URLSearchParams(location.search) : null;
	const search = browser && searchParams?.get('search');
	// Reactive declarations, those are re-evaluated when the variables they depend on change.
	const masjids = entries(data.masjids).filter(([name]) => {
		if (!search) return true;
		return name.toLowerCase().includes(search.toLowerCase());
	});

	const message = searchParams?.get('message');

	return {
		masjids,
		message
	};
};
