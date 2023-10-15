<script lang="ts">
	import { ALERT_ICONS, EAlertType } from '$lib/constants';
	import Icon from '@krowten/svelte-heroicons/Icon.svelte';

	export let type = EAlertType.Info;
	let classes = '';
	export { classes as class };
</script>

<div class="alert {type} {classes}">
	<Icon name={ALERT_ICONS[type]} class="w-6 h-6 text-current" />
	<span>
		<slot />
	</span>
</div>
