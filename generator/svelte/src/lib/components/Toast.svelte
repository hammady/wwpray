<script lang="ts">
	import { ALERT_ICONS, type EAlertType } from '$lib/constants';
	import { fly } from 'svelte/transition';
	import Icon from '@krowten/svelte-heroicons/Icon.svelte';
	export let type: EAlertType;
	let classes = '';
	export { classes as class };
</script>

<div transition:fly={{ y: -16, duration: 300 }} class="alert {type} {classes}">
	<div class="flex items-center gap-2 text-white font-bold">
		<Icon name={ALERT_ICONS[type]} class="h-6 w-6 text-crrent" />
		<span>
			<slot />
		</span>
	</div>
</div>
