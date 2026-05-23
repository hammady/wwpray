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
	import { shouldDefaultToJumas } from '$lib/utils';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import MasjidMap from '$lib/components/app/MasjidMap.svelte';

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
		<h1 class="mb-3">{APP_NAME}</h1>
		<div class="not-prose flex flex-wrap items-center gap-3 mb-6">
			<a
				href="https://github.com/hammady/wwpray"
				target="_blank"
				rel="noopener noreferrer"
				class="flex items-start gap-1.5 text-sm text-base-content/60 hover:text-base-content transition-colors no-underline"
				title="Proudly open source"
			>
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5 shrink-0 mt-0.5" aria-hidden="true">
					<path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
				</svg>
				<span>Proudly open source</span>
			</a>
			<label class="btn btn-primary btn-sm drawer-button ml-auto whitespace-nowrap" for={SUBSCRIPTION_SIDEOVER_ID}>
				Get iqama change alerts
			</label>
		</div>
		<MasjidMap masjids={$masjids} />

		<div class="my-8"></div>

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
