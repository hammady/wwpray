<script lang="ts">
	import { page } from '$app/stores';
	import Divider from '$lib/components/Divider.svelte';
	import type { PageData } from './$types';
	import entries from 'lodash/entries';
	import { browser } from '$app/environment';
	import { APP_NAME } from '$lib/constants';
	import SideOver from '$lib/components/SideOver.svelte';
	import { env } from '$env/dynamic/public';
	import Spacer from '$lib/components/Spacer.svelte';
	import Alert from '$lib/components/Alert.svelte';
	import { toast } from '$lib/stores/toast';
	import { subscribeToMasjid } from '$lib/service';

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
	});

	const SUBSCRIPTION_SIDEOVER_ID = 'subscription-sideover';
	const SUBSCRIPTIONS_BASE_URL = env.PUBLIC_SUBSCRIPTIONS_BASE_URL;

	let masjidsList: HTMLUListElement;
	const onMasjidSubscribeClick = (name: string) => {
		const checkbox = masjidsList.querySelector<HTMLInputElement>(`#${name}`);

		if (!checkbox) {
			toast.error('Something went wrong, please try again later');
			return;
		}

		checkbox.checked = true;
	};

	export let sideInput: HTMLInputElement;
	// Progressive Enhancement
	// Works in case JS is enabled, otherwise the form will be submitted normally
	const onMasjidSubscribeSubmit = (e: Event) => {
		e.preventDefault();

		const form = e.target as HTMLFormElement;
		const formData = new FormData(form);
		const email = formData.get('email') as string;
		const topics = formData.getAll('topics') as string[];

		if (!email) {
			toast.error('Please enter a valid email');
			return;
		}

		if (!topics.length) {
			toast.error('Please select at least one masjid');
			return;
		}

		subscribeToMasjid({ email, topics });

		sideInput.checked = false;
		form.reset();
	};
</script>

<svelte:head>
	<title>{APP_NAME}</title>
	<meta name="description" content="Prayer times for various masjids in tabular format" />
</svelte:head>

<SideOver
	bind:sideInput
	id={SUBSCRIPTION_SIDEOVER_ID}
	close-aria-label="close subscriptions sideover"
>
	<div slot="page" class="mx-auto prose max-w-6xl py-12 px-6 lg:px-8">
		<h1>{APP_NAME}</h1>
		<p>
			A website that shows the prayer times for a list of masjids.
			The data is fetched from the masjid websites once daily.
			You can subscribe to one or more masjids and receive email notifications when the prayer times change.
			You can unsubscribe at any time by clicking the unsubscribe link in the email.
			We employ a strict privacy policy and will never share your email with anyone.
		</p>

		{#if message}
			<Spacer />
			<Alert>{message}</Alert>
			<Spacer />
		{/if}

		<div class="w-full">
			{#each masjids as [name, { iqamas, jumas }], i}
				<h2 class="flex items-center justify-between">
					<span>{name}</span>

					<button on:click={() => onMasjidSubscribeClick(name)}>
						<label class="btn btn-primary btn-sm drawer-button" for={SUBSCRIPTION_SIDEOVER_ID}>
							Subscribe
						</label>
					</button>
				</h2>

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
		on:submit={onMasjidSubscribeSubmit}
	>
		<h2>Subscribe to changes in prayer times</h2>

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
		<ul class="w-full mt-1" bind:this={masjidsList}>
			{#each masjids as [name]}
				<li>
					<label class="label justify-start cursor-pointer my-1">
						<input
							id={name}
							type="checkbox"
							name="topics"
							class="checkbox checkbox-primary"
							value={name}
						/>
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
