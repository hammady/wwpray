<script lang="ts">
	import '../app.css';
	import Navbar from '$lib/components/uikit/Navbar.svelte';
	import Toast from '$lib/components/uikit/Toast.svelte';
	import { toasts } from '$lib/stores/toast';
	import { flip } from 'svelte/animate';
	import SideOver from '$lib/components/uikit/SideOver.svelte';
	import { APP_NAME, EGroupBy, GROUP_BY_ROUTES, SUBSCRIPTION_SIDEOVER_ID } from '$lib/constants';
	import Spacer from '$lib/components/uikit/Spacer.svelte';
	import Alert from '$lib/components/uikit/Alert.svelte';
	import SubscribeForm from '$lib/components/app/SubscribeForm.svelte';
	import type { LayoutData } from './$types';
	import { filteredMasjids, masjids } from '$lib/stores/masjids';
	import { onMount } from 'svelte';
	import {
		getNextPrayerForMasjids,
		getTimeRemainingForNextPrayer,
		shouldDefaultToJumas
	} from '$lib/utils';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import SummaryCard from '$lib/components/app/SummaryCard.svelte';

	export let data: LayoutData;
	$masjids = data.masjids;
	$filteredMasjids = data.filteredMasjids;
	let message = data.message;

	let sideInputElement: HTMLInputElement;

	onMount(() => {
		const jumasRoute = GROUP_BY_ROUTES[EGroupBy.jumas];
		const isJumasRoute = $page.url.pathname === jumasRoute;

		if (!isJumasRoute && shouldDefaultToJumas(data.filteredMasjids)) {
			goto(jumasRoute);
		}
	});

	$: nextPrayer = getNextPrayerForMasjids($masjids);
	$: timeRemainingForNextPrayer = getTimeRemainingForNextPrayer($masjids);

	onMount(() => {
		let interval = setInterval(() => {
			timeRemainingForNextPrayer = getTimeRemainingForNextPrayer($masjids);
		}, 1000);

		return () => clearInterval(interval);
	});
</script>

<svelte:head>
	<title>{APP_NAME}</title>
	<meta name="description" content="Prayer times for various masjids in tabular format" />
</svelte:head>

<Navbar />
<SideOver
	bind:sideInput={sideInputElement}
	id={SUBSCRIPTION_SIDEOVER_ID}
	close-aria-label="close subscriptions sideover"
>
	<div slot="page" class="max-w-6xl px-6 py-12 mx-auto prose lg:px-8">
		<h1>{APP_NAME}</h1>
		<p>
			A website that shows the prayer times for a list of masjids. The data is fetched from the
			masjid websites once daily. You can subscribe to one or more masjids and receive email
			notifications when the prayer times change. You can unsubscribe at any time by clicking the
			unsubscribe link in the email. We employ a strict privacy policy and will never share your
			email with anyone.
		</p>

		{#if nextPrayer && timeRemainingForNextPrayer}
			<SummaryCard {nextPrayer} {timeRemainingForNextPrayer} class="my-8 md:my-16" />
		{/if}

		{#if message}
			<Spacer />
			<Alert>{message}</Alert>
			<Spacer />
		{/if}

		<slot />
	</div>

	<SubscribeForm slot="side" bind:sideInputElement />
</SideOver>

<ul
	class="fixed inset-0 top-navbar left-1/2 -translate-x-1/2 translate-y-8 flex flex-col gap-4 z-[200] pointer-events-none"
>
	{#each $toasts as toast (toast.id)}
		<li class="pointer-events-auto" animate:flip>
			<Toast type={toast.type}>
				{toast.message}
			</Toast>
		</li>
	{/each}
</ul>
