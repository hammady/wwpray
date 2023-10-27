<script lang="ts">
	import { convertToCalendarTime, isOlderThanAWeek, isToday, isYesterday, tw } from '$lib/utils';

	export let changedOn: string | undefined;

	$: today = changedOn && isToday(changedOn);
	$: yesterday = changedOn && isYesterday(changedOn);
	$: olderThanAWeek = changedOn && isOlderThanAWeek(changedOn);
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
