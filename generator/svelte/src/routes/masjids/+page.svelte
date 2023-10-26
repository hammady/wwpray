<script lang="ts">
	import GroupByTabs from '$lib/components/app/GroupByTabs.svelte';
	import MasjidsList from '$lib/components/app/MasjidsList.svelte';
	import { EGroupBy } from '$lib/constants';
	import type { PageData } from './$types';

	export let data: PageData;
	let masjids = data.masjids;
</script>

<GroupByTabs groupBy={EGroupBy.Masjid} />
<MasjidsList bind:masjids />
