import type { IMasjid } from '$lib/types';
import { writable } from 'svelte/store';

export const masjids = writable<[string, IMasjid][]>([]);

export const filteredMasjids: typeof masjids = writable([]);
