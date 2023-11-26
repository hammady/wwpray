<script lang="ts">
	import GroupByTabs from '$lib/components/app/GroupByTabs.svelte';
	import MasjidsList from '$lib/components/app/MasjidsList.svelte';
	import { EGroupBy } from '$lib/constants';
</script>

<GroupByTabs groupBy={EGroupBy.Masjid} />
<MasjidsList />
