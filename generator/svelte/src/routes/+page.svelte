<script lang="ts">
	import GroupByTabs from '$lib/components/app/GroupByTabs.svelte';
	import { EGroupBy } from '$lib/constants';
	import MasjidLastUpdated from '$lib/components/app/MasjidLastUpdated.svelte';
	import { getMasjidRoute, sortMasjidsForPrayer, getSortedPrayers } from '$lib/utils';
	import { goto } from '$app/navigation';
	import PrayerTimeChanged from '$lib/components/app/PrayerTimeChanged.svelte';
	import { filteredMasjids } from '$lib/stores/masjids';

	$: prayers = getSortedPrayers($filteredMasjids);
</script>

<GroupByTabs groupBy={EGroupBy.Prayer} />

{#each prayers as prayer, i (prayer)}
	<h2 class="capitalize">
		{prayer}

		{#if i === 0}
			(Next)
		{/if}
	</h2>
	<div class="border border-neutral-content/50 max-w-[90vw] overflow-x-auto">
		<table class="mt-1 table">
			<thead>
				<tr>
					<th>Masjid</th>
					<th>Iqama</th>
					<th>Last Updated</th>
					<th>Last Changed</th>
				</tr>
			</thead>
			<tbody>
				{#each sortMasjidsForPrayer($filteredMasjids, prayer) as [id, { display_name: name, iqamas, last_updated: lastUpdated }]}
					<tr
						role="button"
						class="hover:!bg-primary/5 cursor-pointer"
						on:click={() => goto(getMasjidRoute(id))}
					>
						<td class="capitalize">
							<a href={getMasjidRoute(id)}>{name}</a>
						</td>
						<td>
							{iqamas[prayer].time}
						</td>
						<td>
							<MasjidLastUpdated isShort {lastUpdated} />
						</td>
						<td>
							{#if iqamas[prayer].changed_on}
								<PrayerTimeChanged changedOn={iqamas[prayer].changed_on} />
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/each}
