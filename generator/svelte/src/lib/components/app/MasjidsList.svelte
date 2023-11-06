<script lang="ts">
	import entries from 'lodash/entries';
	import Divider from '../uikit/Divider.svelte';
	import SubscribeButton from './SubscribeButton.svelte';
	import MasjidLastUpdated from './MasjidLastUpdated.svelte';
	import PrayerTimeChanged from './PrayerTimeChanged.svelte';
	import { tw } from 'tail-cn';
	import { isNextIqama } from '$lib/utils';
	import { filteredMasjids } from '$lib/stores/masjids';
</script>

<div class="w-full">
	{#each $filteredMasjids as [name, { display_name: displayName, last_updated: lastUpdated, address, website, iqamas, jumas }], i}
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
				<table class="mt-1 table border border-neutral-content/50">
					<thead>
						<tr>
							<th>Masjid</th>
							<th>Iqama</th>
							<th>Last Changed</th>
						</tr>
					</thead>
					<tbody>
						{#each entries(iqamas) as [iqama, { time, changed_on: changedOn }]}
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
								<td>{time}</td>
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
