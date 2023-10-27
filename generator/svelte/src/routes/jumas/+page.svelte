<script lang="ts">
	import GroupByTabs from '$lib/components/app/GroupByTabs.svelte';
	import JumasList from '$lib/components/app/JumasList.svelte';
	import { EGroupBy } from '$lib/constants';
	import type { PageData } from '../jumas/$types';

	export let data: PageData;
</script>

<GroupByTabs groupBy={EGroupBy.jumas} />
<JumasList masjids={data.masjids} />
