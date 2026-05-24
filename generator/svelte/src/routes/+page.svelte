<script lang="ts">
	import GroupByTabs from '$lib/components/app/GroupByTabs.svelte';
	import { EGroupBy } from '$lib/constants';
	import MasjidLastUpdated from '$lib/components/app/MasjidLastUpdated.svelte';
	import { getMasjidRoute, sortMasjidsForPrayer, getSortedPrayers, getIqamaRelativeTime } from '$lib/utils';
	import { goto } from '$app/navigation';
	import PrayerTimeChanged from '$lib/components/app/PrayerTimeChanged.svelte';
	import { filteredMasjids } from '$lib/stores/masjids';

	$: prayers = getSortedPrayers($filteredMasjids);

	const prayerEmojis: Record<string, string> = {
		fajr: '🌄',
		zuhr: '☀️',
		asr: '🌤️',
		maghrib: '🌇',
		isha: '🌙',
	};
</script>

<GroupByTabs groupBy={EGroupBy.Prayer} />

{#each prayers as prayer, i (prayer)}
	<h2 class="capitalize">
		{prayer}{prayerEmojis[prayer] ? ` ${prayerEmojis[prayer]}` : ''}

		{#if i === 0}
			(Next)
		{/if}
	</h2>
	<div class="max-w-[90vw] overflow-x-auto rounded-xl ring-1 ring-primary/30 shadow-sm">
		<table class="table table-zebra">
			<thead>
				<tr class="bg-primary text-xs uppercase tracking-wide [&>th]:!text-primary-content">
					<th>Masjid</th>
					<th>Iqama</th>
					<th>Last Updated</th>
					<th>Last Changed</th>
				</tr>
			</thead>
			<tbody>
				{#each sortMasjidsForPrayer($filteredMasjids, prayer) as [id, { display_name: name, iqamas, last_updated: lastUpdated }] (id)}
					{@const isStale = Date.now() - new Date(lastUpdated + 'Z').getTime() > 86_400_000}
					{@const rel = getIqamaRelativeTime(iqamas[prayer].seconds_since_midnight_utc)}
					<tr
						role="button"
						class="hover:!bg-primary/5 cursor-pointer"
						class:opacity-40={isStale}
						on:click={() => goto(getMasjidRoute(id))}
					>
						<td class="capitalize">
							<a href={getMasjidRoute(id)}>{name}</a>
						</td>
						<td>
							<span class:line-through={i === 0 && rel?.isPast}>{iqamas[prayer].time}</span>
							{#if i === 0 && rel}
								<span class="text-xs font-medium ml-1 {rel.isPast ? 'text-red-500' : 'text-green-600'}">({rel.label})</span>
							{/if}
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
