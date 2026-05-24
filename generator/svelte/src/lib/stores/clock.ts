import { readable } from 'svelte/store';

/** Ticks at each whole-minute boundary (10:02:00, 10:03:00, …). */
export const clock = readable(Date.now(), (set) => {
	let id: ReturnType<typeof setTimeout>;

	function tick() {
		set(Date.now());
		id = setTimeout(tick, 1_000);
	}

	tick(); // fire immediately, then every second

	return () => clearTimeout(id);
});
