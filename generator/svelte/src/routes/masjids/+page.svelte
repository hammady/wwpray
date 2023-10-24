<script lang="ts">
	import GroupByTabs from '$lib/components/app/GroupByTabs.svelte';
	import { EGroupBy } from '$lib/constants';
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<GroupByTabs groupBy={EGroupBy.Masjid} />
