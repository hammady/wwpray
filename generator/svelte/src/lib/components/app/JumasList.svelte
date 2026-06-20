<script lang="ts">
	import { EGroupBy, GROUP_BY_ROUTES } from '$lib/constants';
	import { filteredMasjids } from '$lib/stores/masjids';
	import Divider from '../uikit/Divider.svelte';
	import MasjidLastUpdated from './MasjidLastUpdated.svelte';
	import SubscribeButton from './SubscribeButton.svelte';
	import { getIqamaRelativeTime } from '$lib/utils';
	import { clock } from '$lib/stores/clock';

	// Set to true to test Friday behaviour
	const isFriday = new Date().getDay() === 5;
</script>

{#if $filteredMasjids}
	<div class="w-full">
		{#each $filteredMasjids as [name, { display_name: displayName, jumas, jumas_seconds_since_midnight_utc: jumasSeconds, last_updated: lastUpdated, latitude, longitude }], i}
			{@const isStale = Date.now() - new Date(lastUpdated + 'Z').getTime() > 86_400_000}
			<h2>
				<a href="{GROUP_BY_ROUTES[EGroupBy.Masjid]}#masjid_{name}">
					{displayName}
				</a>
			</h2>
			<div class="not-prose mb-3">
				<SubscribeButton {name} />
			</div>

			<MasjidLastUpdated {lastUpdated} />

			{#if latitude != null && longitude != null}
				{@const dest = `${latitude},${longitude}`}
				<p class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
					<span class="text-base-content/50 text-xs uppercase tracking-wide">Get directions:</span>
					<a href="https://maps.apple.com/?daddr={dest}" target="_blank" rel="noopener noreferrer" class="font-semibold text-primary no-underline">🗺 Apple Maps</a>
					<a href="https://www.google.com/maps/dir/?api=1&destination={dest}" target="_blank" rel="noopener noreferrer" class="font-semibold text-primary no-underline">🗺 Google Maps</a>
				</p>
			{/if}

			<div class="px-2 md:px-4">
				<ul class:opacity-40={isStale}>
					{#each jumas as juma, j}
						{@const relTime = isFriday ? getIqamaRelativeTime(jumasSeconds?.[j] ?? null, $clock) : null}
						<li>
							<span class:line-through={relTime?.isPast} class:opacity-40={relTime?.isPast}>{juma}</span>
							{#if relTime?.label}
								<span class="inline-block min-w-[6rem] tabular-nums text-xs font-medium ml-1 {relTime.isPast ? 'text-red-500' : 'text-green-600'}">({relTime.label})</span>
							{/if}
						</li>
					{/each}
				</ul>
				{#if i !== $filteredMasjids.length - 1}
					<Divider />
				{/if}
			</div>
		{/each}
	</div>
{/if}
