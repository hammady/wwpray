import { PUBLIC_SUBSCRIPTIONS_BASE_URL } from '$env/static/public';
import { toast } from './stores/toast';
import type { ISubscribeArgs, ISubscribeResponse } from './types';

export const subscribeToMasjid = async ({ email, topics }: ISubscribeArgs) => {
	const url = new URL(PUBLIC_SUBSCRIPTIONS_BASE_URL);
	url.searchParams.append('email', email);
	for (const topic of topics) {
		url.searchParams.append('topics', topic);
	}

	const response = await fetch(url, {
		method: 'POST',
		headers: {
			Accept: 'application/json'
		}
	});

	const data = (await response.json()) satisfies ISubscribeResponse;

	if (!response.ok) {
		toast.error(data?.message ?? 'An error occurred');
	}

	data.message && toast.success(data.message);
};
