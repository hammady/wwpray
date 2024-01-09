<script lang="ts">
	import type { TDuration, TPrayer } from "$lib/types";
    import CalendarIcon from "$lib/icons/calendar.svg?component";
    import PrayingIcon from "$lib/icons/praying.svg?component";
    import ClockIcon from "$lib/icons/clock.svg?component";
	import { getCurrentLocalDateTime, getDayNameFromDate, getFormattedDate, tw } from "$lib/utils";
    import DurationCounter from './DurationCounter.svelte'

    export let nextPrayer: TPrayer;
    export let timeRemainingForNextPrayer: TDuration;
    let classes = '';
    export { classes as class }

    const today = getCurrentLocalDateTime();
    const formattedToday = getFormattedDate(today);
    const todayName = getDayNameFromDate(today);
    const sectionClasses = "flex flex-col gap-3 items-center p-5";
    const cardClasses = "bg-bg01 shadow-card rounded-2xl";
    const cardMDClasses = "md:bg-bg01 md:shadow-card md:rounded-2xl";
    const mdResetClasses = "md:bg-transparent md:shadow-none md:rounded-none md:p-0"
</script>

<div class={tw(cardMDClasses, "flex md:items-center flex-col md:flex-row justify-between w-full p-8 lg:px-24 gap-8 md:gap-11", classes)} >
    <div class={tw(sectionClasses, cardClasses, mdResetClasses)}>
        <div class="flex items-center gap-1">
            <CalendarIcon class="w-4 h-4" />
            <span class="text-xs">Today</span>
        </div>
        <span class="mt-1 text-2xl font-semibold">
            {todayName}
        </span>
        <time datetime={today.toISOString()}>
            {formattedToday}
        </time>
    </div>

    <div class="hidden divider divider-horizontal md:flex" />

    <div class={tw(sectionClasses, cardClasses, mdResetClasses)}>
        <div class="flex items-center gap-1">
            <PrayingIcon class="w-4 h-4" />
            <span class="text-xs">Next Prayer</span>
        </div>
        <span class="mt-1 text-2xl font-semibold">
            {nextPrayer.name}
        </span>
    </div>

    <div class="hidden divider divider-horizontal md:flex" />

    <div class={tw(sectionClasses, cardClasses, mdResetClasses)}>
        <div class="flex items-center gap-1">
            <ClockIcon class="w-4 h-4" />
            <span class="text-xs">Time remaining for next prayer</span>
        </div>
        <span class="mt-1 text-2xl font-semibold">
            <DurationCounter duration={timeRemainingForNextPrayer} />
        </span>
    </div>
</div>



