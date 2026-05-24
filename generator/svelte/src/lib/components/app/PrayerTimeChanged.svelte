<script lang="ts">
	import { browser } from '$app/environment';
	import { convertToCalendarTime, isOlderThanAWeek, isToday, isYesterday, tw } from '$lib/utils';
	import { clock } from '$lib/stores/clock';

	export let changedOn: string | undefined;

	$: today = ($clock, changedOn && browser && isToday(changedOn));
	$: yesterday = ($clock, changedOn && browser && isYesterday(changedOn));
	$: olderThanAWeek = ($clock, changedOn && browser && isOlderThanAWeek(changedOn));
	$: changedOnCalendarTime = ($clock, convertToCalendarTime(changedOn));
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
