<script lang="ts">
	import entries from 'lodash/entries';
	import Divider from '../uikit/Divider.svelte';
	import SubscribeButton from './SubscribeButton.svelte';
	import MasjidLastUpdated from './MasjidLastUpdated.svelte';
	import PrayerTimeChanged from './PrayerTimeChanged.svelte';
	import { tw } from 'tail-cn';
	import { isNextIqama, getIqamaRelativeTime } from '$lib/utils';
	import { filteredMasjids } from '$lib/stores/masjids';
</script>

<div class="w-full">
	{#each $filteredMasjids as [name, { display_name: displayName, last_updated: lastUpdated, address, website, iqamas, jumas, latitude, longitude }], i}
		{@const isStale = Date.now() - new Date(lastUpdated + 'Z').getTime() > 86_400_000}
		<h2>
			<a target="_blank" href={website} id="masjid_{name}">
				{displayName}
			</a>
		</h2>
		<div class="not-prose mb-3">
			<SubscribeButton {name} />
		</div>

		<p>Address: {address}</p>

		{#if latitude != null && longitude != null}
			{@const dest = `${latitude},${longitude}`}
			<p class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
				<span class="text-base-content/50 text-xs uppercase tracking-wide">Get directions:</span>
				<a href="https://maps.apple.com/?daddr={dest}" target="_blank" rel="noopener noreferrer" class="font-semibold text-primary no-underline">🗺 Apple Maps</a>
				<a href="https://www.google.com/maps/dir/?api=1&destination={dest}" target="_blank" rel="noopener noreferrer" class="font-semibold text-primary no-underline">🗺 Google Maps</a>
			</p>
		{/if}

		<div class="px-2 md:px-4">
			<MasjidLastUpdated {lastUpdated} />

			<div class="max-w-[90vw] overflow-x-auto rounded-xl ring-1 ring-primary/30 shadow-sm">
				<table class="table table-zebra">
					<thead>
						<tr class="bg-primary text-xs uppercase tracking-wide [&>th]:!text-primary-content">
							<th>Prayer</th>
							<th>Iqama</th>
							<th>Last Changed</th>
						</tr>
					</thead>
					<tbody class:opacity-40={isStale}>
							{#each entries(iqamas) as [iqama, { time, changed_on: changedOn, seconds_since_midnight_utc: iqamaSeconds }]}
								{@const rel = getIqamaRelativeTime(iqamaSeconds)}
								<tr
									class={tw([
										'!bg-primary/5 font-semibold',
										isNextIqama($filteredMasjids, name, iqama)
									])}
								>
									<td class="capitalize">
										{iqama}

										{#if isNextIqama($filteredMasjids, name, iqama)}
											(Next)
										{/if}
									</td>
									<td>
										<span class:line-through={isNextIqama($filteredMasjids, name, iqama) && rel?.isPast}>{time}</span>
										{#if isNextIqama($filteredMasjids, name, iqama) && rel}
											<span class="text-xs font-medium ml-1 {rel.isPast ? 'text-red-500' : 'text-green-600'}">({rel.label})</span>
										{/if}
									</td>
								<td>
									<PrayerTimeChanged {changedOn} />
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			{#if i !== $filteredMasjids.length - 1}
				<Divider />
			{/if}
		</div>
	{/each}
</div>
