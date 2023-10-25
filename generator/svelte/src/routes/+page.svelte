<script lang="ts">
	import GroupByTabs from '$lib/components/app/GroupByTabs.svelte';
	import { EGroupBy } from '$lib/constants';
	import type { LayoutData } from './$types';
	import MasjidLastUpdated from '$lib/components/app/MasjidLastUpdated.svelte';
	import { convertToCalendarTime, extractPrayersFromMasjids } from '$lib/utils';

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
					<th>Iqama Time</th>
					<th>Last Updated</th>
					<th>Changed On</th>
				</tr>
			</thead>
			<tbody>
				{#each masjids as [_, { display_name: name, website, iqamas, last_updated: lastUpdated }]}
					<tr>
						<td class="capitalize">
							<a target="_blank" href={website}>{name}</a>
						</td>
						<td>
							{iqamas[prayer].time}
						</td>
						<td>
							<MasjidLastUpdated {lastUpdated} />
						</td>
						<td>
							{#if iqamas[prayer].changed_on}
								{convertToCalendarTime(iqamas[prayer].changed_on)}
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/each}
