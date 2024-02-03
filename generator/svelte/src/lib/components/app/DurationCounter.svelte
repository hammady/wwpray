<script lang="ts">
	import type { TDuration } from '$lib/types';
	import DurationCounterNumber from './DurationCounterNumber.svelte';

	export let duration: TDuration;
</script>

<div class="flex items-center gap-2">
	<DurationCounterNumber value={duration.hours} label="hours" />
	<span class="text-2xl -translate-y-2.5 text-black/30">:</span>
	<DurationCounterNumber value={duration.minutes} label="minutes" />
	<span class="text-2xl -translate-y-2.5 text-black/30">:</span>
	<DurationCounterNumber value={duration.seconds} label="seconds" />
</div>
