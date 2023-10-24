<script lang="ts">
	import GroupByTabs from '$lib/components/app/GroupByTabs.svelte';
	import { EGroupBy } from '$lib/constants';
	import { extractPrayersFromMasjids } from '$lib/utils';
	import entries from 'lodash/entries';
	import type { LayoutData } from './$types';
	import SubscribeButton from '$lib/components/app/SubscribeButton.svelte';
	import MasjidLastUpdated from '$lib/components/app/MasjidLastUpdated.svelte';

	export let data: LayoutData;
	$: masjids = data.masjids;
	$: prayers = extractPrayersFromMasjids(masjids);
</script>

<GroupByTabs groupBy={EGroupBy.Prayer} />

{#each prayers as prayer (prayer)}
	<h2 class="capitalize">{prayer}</h2>
	<div class="max-w-[90vw] overflow-x-auto">
		<table class="mt-1 table table-zebra border border-neutral-content/50">
			<thead>
				<tr>
					<th>Masjid</th>
					<th>Address</th>
					<th>Time</th>
					<th>Last Updated</th>
					<th>Subscribe</th>
				</tr>
			</thead>
			<tbody>
				{#each masjids as [id, { display_name: name, address, website, iqamas, last_updated: lastUpdated }]}
					<tr>
						<td class="capitalize">
							<a target="_blank" href={website}>{name}</a>
						</td>
						<td>
							{address}
						</td>
						<td>
							{iqamas[prayer].time}
						</td>
						<td>
							<MasjidLastUpdated {lastUpdated} />
						</td>
						<td>
							<SubscribeButton name={id} />
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/each}
