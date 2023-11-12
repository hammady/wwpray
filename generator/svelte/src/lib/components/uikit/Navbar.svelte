<script lang="ts">
	import { browser } from '$app/environment';
	import { APP_NAME_SHORT } from '$lib/constants';
	import { filteredMasjids, masjids } from '$lib/stores/masjids';
	import { getFilteredMasjids } from '$lib/utils';
	import { onMount } from 'svelte';
	import type { FormEventHandler } from 'svelte/elements';

	// When JS is enabled, search immediately on type
	const onSearch: FormEventHandler<HTMLInputElement> = (event) => {
		const search = (event.target as HTMLInputElement).value;

		$filteredMasjids = getFilteredMasjids(search, $masjids);
	};

	$: isJSEnabled = browser;

	onMount(() => {
		isJSEnabled = true;
	});
</script>

<nav class="top-0 z-50 navbar bg-base-100 px-4 2xl:px-8 h-max sm:h-navbar shadow-md">
	<div class="flex-1">
		<a
			href="/"
			class="btn btn-ghost font-bold upper-case tracking-thin text-lg md:text-xl text-primary"
		>
			{APP_NAME_SHORT}
		</a>
	</div>
	<div class="flex gap-4">
		<div class="pl-6">
			{#if isJSEnabled}
				<input
					name="search"
					type="text"
					placeholder="Search for masjid"
					class="input input-bordered focus:input-primary w-56 md:w-80 focus:border-none"
					on:input={onSearch}
				/>
			{/if}
		</div>
	</div>
</nav>
