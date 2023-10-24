<script lang="ts">
	import GroupByTabs from '$lib/components/app/GroupByTabs.svelte';
	import MasjidsList from '$lib/components/app/MasjidsList.svelte';
	import { EGroupBy } from '$lib/constants';
	import type { LayoutData } from './$types';

	export let data: LayoutData;
	let masjids = data.masjids;
</script>

<GroupByTabs groupBy={EGroupBy.Prayer} />
<MasjidsList bind:masjids />
