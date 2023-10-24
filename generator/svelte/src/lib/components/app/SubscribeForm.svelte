<script lang="ts">
	import { SUBSCRIPTION_SIDEOVER_ID } from '$lib/constants';
	import { subscribeToMasjid } from '$lib/service';
	import { masjidListElement } from '$lib/stores/elements';
	import { toast } from '$lib/stores/toast';
	import type { IMasjid } from '$lib/types';
	import Spacer from '../uikit/Spacer.svelte';

	export let masjids: [string, IMasjid][];
	export let sideInputElement: HTMLInputElement;

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

		sideInputElement.checked = false;
		form.reset();
	};
</script>

<form
	class="flex flex-col flex-grow min-h-0 px-2 py-4 prose prose-li:my-0 prose-ul:px-0"
	method="GET"
	action={SUBSCRIPTION_SIDEOVER_ID}
	on:submit={onMasjidSubscribeSubmit}
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
	<ul class="w-full mt-1" bind:this={$masjidListElement}>
		{#each masjids as [id, { display_name: name }]}
			<li>
				<label class="label justify-start cursor-pointer my-1">
					<input
						{id}
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
