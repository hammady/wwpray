import { writable, type Writable } from 'svelte/store';

export const masjidListElement: Writable<HTMLUListElement | null> = writable(null);
