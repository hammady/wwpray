import { browser } from '$app/environment';
import type { TMasjidsJSON } from '$lib/types';
import entries from 'lodash/entries';
import type { LayoutLoad } from './$types';
import { getFilteredMasjids } from '$lib/utils';

export const prerender = true;

export const load: LayoutLoad = async () => {
	const data = (await import('./notified.json')) as TMasjidsJSON;
	const searchParams = browser ? new URLSearchParams(location.search) : null;

	const search = (browser && searchParams?.get('search')) || '';

	const masjids = entries(data.masjids);
	const filteredMasjids = getFilteredMasjids(search, masjids);

	const message = searchParams?.get('message');

	return {
		masjids,
		filteredMasjids,
		message
	};
};
