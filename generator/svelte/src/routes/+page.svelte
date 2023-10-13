<script lang="ts">
	import { page } from '$app/stores';
	import Divider from '$lib/components/Divider.svelte';
	import type { PageData } from './$types';
	import entries from 'lodash/entries';
	import { browser } from '$app/environment';
	import { APP_NAME } from '$lib/constants';

	// This data object is the one returned by the load function
	// wait we didn't assign it to anything, how does it work?
	// This is the magic of Svelte :D
	export let data: PageData;

	// Reactive declarations, those are re-evaluated when the variables they depend on change.
	$: url = $page.url;
	$: search = browser && url.searchParams.get('search');
	$: masjids = entries(data.masjids).filter(([name]) => {
		if (!search) return true;
		return name.toLowerCase().includes(search.toLowerCase());
	});
</script>

<svelte:head>
	<title>{APP_NAME}</title>
	<meta name="description" content="Prayer times for various masjids in tabular format" />
</svelte:head>

<div class="mx-auto prose max-w-6xl py-12 px-6 lg:px-8">
	<h1>Masjid Prayer Times</h1>
	<p>
		View prayer times for various masjids below. To find a specific masjid, use the search bar at
		the top.
	</p>

	<div class="w-full capitalize">
		{#each masjids as [name, { iqamas, jumas }], i}
			<h2>{name}</h2>
			<div class="overflow-x-auto px-4">
				<table class="table table-zebra">
					<thead>
						<tr>
							<th>Iqama</th>
							<th>Time</th>
						</tr>
					</thead>
					<tbody>
						{#each entries(iqamas) as [iqama, { time }]}
							<tr>
								<td>{iqama}</td>
								<td>{time}</td>
							</tr>
						{/each}
					</tbody>
				</table>
				<h3>Jumas</h3>
				<ul>
					{#each jumas as juma}
						<li>
							{juma}
						</li>
					{/each}
				</ul>
			</div>
			{#if i !== masjids.length - 1}
				<Divider />
			{/if}
		{/each}
	</div>
</div>

<style>
	.prose {
		text-wrap: balance;
	}
</style>
