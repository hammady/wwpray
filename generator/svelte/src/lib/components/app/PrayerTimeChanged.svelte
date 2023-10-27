<script lang="ts">
	import { convertToCalendarTime } from '$lib/utils';

	export let changedOn: string | undefined;
</script>

{#if changedOn}
	{convertToCalendarTime(changedOn)}
{/if}
