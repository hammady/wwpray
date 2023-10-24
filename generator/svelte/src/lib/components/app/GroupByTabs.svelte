<script lang="ts">
	import { EGroupBy, GROUP_BY_ROUTES } from '$lib/constants';
	import values from 'lodash/values';

	export let groupBy: EGroupBy;
</script>

<div class="w-full tabs">
	{#each values(EGroupBy) as value}
		<a
			class="flex-1 tab tab-bordered no-underline"
			class:tab-active={value === groupBy}
			href={GROUP_BY_ROUTES[value]}
		>
			Group by {value}
		</a>
	{/each}
</div>
