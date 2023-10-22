<script lang="ts">
	import { page } from '$app/stores';
	import type { PageData } from './$types';
	import entries from 'lodash/entries';
	import { browser } from '$app/environment';
	import { APP_NAME, SUBSCRIPTION_SIDEOVER_ID } from '$lib/constants';
	import SideOver from '$lib/components/uikit/SideOver.svelte';
	import Spacer from '$lib/components/uikit/Spacer.svelte';
	import Alert from '$lib/components/uikit/Alert.svelte';
	import MasjidsList from '$lib/components/app/MasjidsList.svelte';
	import SubscribeForm from '$lib/components/app/SubscribeForm.svelte';
	import type { IMasjid } from '$lib/types';

	// This data object is the one returned by the load function
	// wait we didn't assign it to anything, how does it work?
	// This is the magic of Svelte :D
	export let data: PageData;

	// Reactive declarations, those are re-evaluated when the variables they depend on change.
	$: url = $page.url;
	$: search = browser && url.searchParams.get('search');
	$: message = browser && url.searchParams.get('message');
	$: masjids = entries(data.masjids).filter(([name]) => {
		if (!search) return true;
		return name.toLowerCase().includes(search.toLowerCase());
	}) as [string, IMasjid][];

	let masjidsListElement: HTMLUListElement;
	let sideInputElement: HTMLInputElement;
</script>

<svelte:head>
	<title>{APP_NAME}</title>
	<meta name="description" content="Prayer times for various masjids in tabular format" />
</svelte:head>

<SideOver
	bind:sideInput={sideInputElement}
	id={SUBSCRIPTION_SIDEOVER_ID}
	close-aria-label="close subscriptions sideover"
>
	<div slot="page" class="mx-auto prose max-w-6xl py-12 px-6 lg:px-8">
		<h1>{APP_NAME}</h1>
		<p>
			A website that shows the prayer times for a list of masjids. The data is fetched from the
			masjid websites once daily. You can subscribe to one or more masjids and receive email
			notifications when the prayer times change. You can unsubscribe at any time by clicking the
			unsubscribe link in the email. We employ a strict privacy policy and will never share your
			email with anyone.
		</p>

		{#if message}
			<Spacer />
			<Alert>{message}</Alert>
			<Spacer />
		{/if}

		<MasjidsList {masjids} {masjidsListElement} />
	</div>

	<SubscribeForm slot="side" {masjids} bind:masjidsListElement bind:sideInputElement />
</SideOver>
