<script lang="ts">
	import { EGroupBy, GROUP_BY_ROUTES } from '$lib/constants';
	import type { IMasjid } from '$lib/types';
	import Divider from '../uikit/Divider.svelte';

	export let masjids: [string, IMasjid][];
</script>

{#if masjids}
	<div class="w-full">
		{#each masjids as [name, { display_name: displayName, jumas }], i}
			<h2 class="flex items-center justify-between">
				<a href="{GROUP_BY_ROUTES[EGroupBy.Masjid]}#masjid_{name}">
					{displayName}
				</a>
			</h2>

			<div class="px-2 md:px-4">
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
