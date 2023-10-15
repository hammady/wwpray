<script lang="ts">
	import type { EAlertType } from '$lib/constants';
	import { fly } from 'svelte/transition';

	export let type: EAlertType;
	let classes = '';
	export { classes as class };
</script>

<div transition:fly={{ y: -16, duration: 300 }} class={classes}>
	<div class="alert {type}">
		<span>
			<slot />
		</span>
	</div>
</div>
