import { writable, type Writable } from 'svelte/store';
import { toast } from './toast';

export const masjidListElement: Writable<HTMLUListElement | null> = writable(null);

export const onMasjidSubscribeClick = (
	name: string,
	masjidListElement: HTMLUListElement | null
) => {
	const checkbox = masjidListElement?.querySelector<HTMLInputElement>(`#${name}`);

	if (!checkbox) {
		toast.error('Something went wrong, please try again later');
		return;
	}

	checkbox.checked = true;
};
