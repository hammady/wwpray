<script lang="ts">
	import type { IMasjid } from '$lib/types';
	import entries from 'lodash/entries';
	import Divider from '../uikit/Divider.svelte';
	import SubscribeButton from './SubscribeButton.svelte';
	import MasjidLastUpdated from './MasjidLastUpdated.svelte';
	import { convertToCalendarTime } from '$lib/utils';

	export let masjids: [string, IMasjid][];
</script>

{#if masjids}
	<div class="w-full">
		{#each masjids as [name, { display_name: displayName, last_updated: lastUpdated, address, website, iqamas, jumas }], i}
			<h2 class="flex items-center justify-between">
				<a target="_blank" href={website} id="masjid_{name}">
					{displayName}
				</a>

				<SubscribeButton {name} />
			</h2>

			<p>Address: {address}</p>

			<div class="px-2 md:px-4">
				<MasjidLastUpdated {lastUpdated} />

				<div class="max-w-[90vw] overflow-x-auto">
					<table class="mt-1 table table-zebra border border-neutral-content/50">
						<thead>
							<tr>
								<th>Iqama</th>
								<th>Time</th>
								<th>Changed</th>
							</tr>
						</thead>
						<tbody>
							{#each entries(iqamas) as [iqama, { time, changed_on: changedOn }]}
								<tr>
									<td class="capitalize">{iqama}</td>
									<td>{time}</td>
									<td>
										{#if changedOn}
											{convertToCalendarTime(changedOn)}
										{/if}
									</td>
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
