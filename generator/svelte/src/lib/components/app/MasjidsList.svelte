<script lang="ts">
	import type { IMasjid } from '$lib/types';
	import entries from 'lodash/entries';
	import Divider from '../uikit/Divider.svelte';
	import { SUBSCRIPTION_SIDEOVER_ID } from '$lib/constants';
	import { toast } from '$lib/stores/toast';
	import { convertToRelativeTime } from '$lib/utils';

	export let masjids: [string, IMasjid][];
	export let masjidsListElement: HTMLUListElement;

	const onMasjidSubscribeClick = (name: string) => {
		const checkbox = masjidsListElement.querySelector<HTMLInputElement>(`#${name}`);

		if (!checkbox) {
			toast.error('Something went wrong, please try again later');
			return;
		}

		checkbox.checked = true;
	};

	const timeRendered = (node: HTMLTimeElement, lastUpdated: string) => {
		node.innerHTML = convertToRelativeTime(lastUpdated);
	};
</script>

<div class="w-full">
	{#each masjids as [name, { display_name: displayName, last_updated: lastUpdated, address, website, iqamas, jumas }], i}
		<h2 class="flex items-center justify-between">
			<a href={website}>
				{displayName}
			</a>

			<button on:click={() => onMasjidSubscribeClick(name)}>
				<label class="btn btn-primary btn-sm drawer-button" for={SUBSCRIPTION_SIDEOVER_ID}>
					Subscribe
				</label>
			</button>
		</h2>

		<p>Address: {address}</p>

		<div class="px-2 md:px-4">
			<span>
				Last updated <time datetime={lastUpdated} use:timeRendered={lastUpdated}>
					<noscript>{lastUpdated} UTC</noscript>
				</time>.
			</span>
			<div class="max-w-[90vw] overflow-x-auto">
				<table class="mt-1 table table-zebra border border-neutral-content/50">
					<thead>
						<tr>
							<th>Iqama</th>
							<th>Time</th>
						</tr>
					</thead>
					<tbody>
						{#each entries(iqamas) as [iqama, { time }]}
							<tr>
								<td>{iqama}</td>
								<td>{time}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<h3>Jumas</h3>
			<ul>
				{#each jumas as juma}
					<li>
						{juma}
					</li>
				{/each}
			</ul>
			{#if i !== masjids.length - 1}
				<Divider />
			{/if}
		</div>
	{/each}
</div>
