<script lang="ts">
	import { EGroupBy, GROUP_BY_ROUTES } from '$lib/constants';
	import { filteredMasjids } from '$lib/stores/masjids';
	import type { IMasjid } from '$lib/types';
	import Divider from '../uikit/Divider.svelte';
	import MasjidLastUpdated from './MasjidLastUpdated.svelte';
</script>

{#if $filteredMasjids}
	<div class="w-full">
		{#each $filteredMasjids as [name, { display_name: displayName, jumas, last_updated: lastUpdated }], i}
			<h2 class="flex items-center justify-between">
				<a href="{GROUP_BY_ROUTES[EGroupBy.Masjid]}#masjid_{name}">
					{displayName}
				</a>
			</h2>

			<MasjidLastUpdated {lastUpdated} />

			<div class="px-2 md:px-4">
				<ul>
					{#each jumas as juma}
						<li>
							{juma}
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
