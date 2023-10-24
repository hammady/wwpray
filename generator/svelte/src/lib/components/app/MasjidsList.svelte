<script lang="ts">
	import type { IMasjid } from '$lib/types';
	import entries from 'lodash/entries';
	import Divider from '../uikit/Divider.svelte';
	import { convertToRelativeTime } from '$lib/utils';
	import SubscribeButton from './SubscribeButton.svelte';

	export let masjids: [string, IMasjid][];

	const timeRendered = (node: HTMLTimeElement, lastUpdated: string) => {
		node.innerHTML = convertToRelativeTime(lastUpdated);
	};
</script>

{#if masjids}
	<div class="w-full">
		{#each masjids as [name, { display_name: displayName, last_updated: lastUpdated, address, website, iqamas, jumas }], i}
			<h2 class="flex items-center justify-between">
				<a href={website}>
					{displayName}
				</a>

				<SubscribeButton {name} />
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
									<td class="capitalize">{iqama}</td>
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
{/if}
