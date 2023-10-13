<script lang="ts">
	import { page } from '$app/stores';
	import Divider from '$lib/components/Divider.svelte';
	import type { PageData } from './$types';
	import entries from 'lodash/entries';
	import { browser } from '$app/environment';
	import { APP_NAME } from '$lib/constants';
	import SideOver from '$lib/components/SideOver.svelte';
	import { env } from '$env/dynamic/public';
	import { enhance } from '$app/forms';
	import Spacer from '$lib/components/Spacer.svelte';

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

	const SUBSCRIPTION_SIDEOVER_ID = 'subscription-sideover';
	const SUBSCRIPTIONS_BASE_URL = env.PUBLIC_SUBSCRIPTIONS_BASE_URL;
</script>

<svelte:head>
	<title>{APP_NAME}</title>
	<meta name="description" content="Prayer times for various masjids in tabular format" />
</svelte:head>

<SideOver id={SUBSCRIPTION_SIDEOVER_ID} close-aria-label="close subscriptions sideover">
	<div slot="page" class="mx-auto prose max-w-6xl py-12 px-6 lg:px-8">
		<h1>Masjid Prayer Times</h1>
		<p>
			View prayer times for various masjids below. To find a specific masjid, use the search bar at
			the top.
		</p>

		<div class="w-full capitalize">
			{#each masjids as [name, { iqamas, jumas }], i}
				<div class="flex items-center justify-between">
					<h2>{name}</h2>

					<label for={SUBSCRIPTION_SIDEOVER_ID} class="btn btn-primary drawer-button">
						Subscribe
					</label>
				</div>
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

	<form
		slot="side"
		class="flex flex-col flex-grow min-h-0 px-2 py-4 prose prose-li:my-0 prose-ul:px-0"
		method="GET"
		action={SUBSCRIPTIONS_BASE_URL}
		use:enhance
	>
		<h2>Subscribe to Masjid Prayer Times</h2>

		<div class="form-control w-full">
			<label for="email" class="label">
				<span class="label-text text-base font-medium">What is your email?</span>
			</label>
			<input
				type="email"
				name="email"
				id="email"
				placeholder="Type your email here"
				class="input input-bordered w-full"
			/>
		</div>
		<Spacer size="lg" />
		<label for="topics" class="label text-base font-medium">
			<span>Which masjids do you want to subscribe to?</span>
		</label>
		<ul class="w-full mt-1">
			{#each masjids as [name]}
				<li>
					<label class="label justify-start cursor-pointer my-1">
						<input type="checkbox" name="topics" class="checkbox checkbox-primary" value={name} />
						<span class="label-text">{name}</span>
					</label>
				</li>
			{/each}
		</ul>
		<div class="mt-auto flex items-center gap-4">
			<button class="btn btn-primary flex-[0.8]" type="submit"> Subscribe </button>
			<label
				for={SUBSCRIPTION_SIDEOVER_ID}
				class="flex-[0.2] btn btn-outline btn-neutral drawer-button"
			>
				Close
			</label>
		</div>
	</form>
</SideOver>

<style>
	.prose {
		text-wrap: balance;
	}
</style>
