<script lang="ts">
	import type { IMasjid } from '$lib/types';
	import entries from 'lodash/entries';
	import Divider from '../uikit/Divider.svelte';
	import { SUBSCRIPTION_SIDEOVER_ID } from '$lib/constants';
	import { toast } from '$lib/stores/toast';
	import { masjidListElement } from '$lib/stores/elements';

	export let masjids: [string, IMasjid][];

	const onMasjidSubscribeClick = (name: string) => {
		const checkbox = $masjidListElement?.querySelector<HTMLInputElement>(`#${name}`);

		if (!checkbox) {
			toast.error('Something went wrong, please try again later');
			return;
		}

		checkbox.checked = true;
	};
</script>

{#if masjids}
	<div class="w-full">
		{#each masjids as [name, { display_name: displayName, address, website, iqamas, jumas }], i}
			<h2 class="flex items-center justify-between">
				<a href={website}>
					{displayName}
				</a>

				<button on:click={() => onMasjidSubscribeClick(name)}>
					<label class="btn btn-primary btn-sm drawer-button" for={SUBSCRIPTION_SIDEOVER_ID}>
						Subscribe
					</label>
				</button>
			</h2>

			<p>Address: {address}</p>

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
{/if}
