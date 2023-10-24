<script lang="ts">
	import MasjidsList from '$lib/components/app/MasjidsList.svelte';
	import type { LayoutData } from './$types';

	export let data: LayoutData;
	let masjids = data.masjids;
</script>

<MasjidsList bind:masjids />
