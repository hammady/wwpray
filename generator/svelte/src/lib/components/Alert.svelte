<script lang="ts">
	import { ALERT_PATHS, EAlertType } from '$lib/constants';

	export let type = EAlertType.Info;
	let classes = '';
	export { classes as class };
</script>

<div class="alert {type} {classes}">
	<svg
		xmlns="http://www.w3.org/2000/svg"
		class="stroke-current shrink-0 h-6 w-6"
		fill="none"
		stroke-linecap="round"
		stroke-linejoin="round"
		stroke-width="2"
		viewBox="0 0 24 24"
	>
		<path d={ALERT_PATHS[type]} />
	</svg>
	<span>
		<slot />
	</span>
</div>
