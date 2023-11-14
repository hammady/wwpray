<script lang="ts">
	import { browser } from '$app/environment';
	import { convertToCalendarTime, isOlderThanAWeek, isToday, isYesterday, tw } from '$lib/utils';

	export let changedOn: string | undefined;

	$: today = changedOn && browser && isToday(changedOn);
	$: yesterday = changedOn && browser && isYesterday(changedOn);
	$: olderThanAWeek = changedOn && browser && isOlderThanAWeek(changedOn);
	$: changedOnCalendarTime = convertToCalendarTime(changedOn);
</script>

{#if changedOn && !olderThanAWeek}
	<span
		class={tw(
			'font-medium',
			['font-bold text-danger', today],
			['font-semibold text-warning', yesterday]
		)}
	>
		{changedOnCalendarTime}
	</span>
{/if}
