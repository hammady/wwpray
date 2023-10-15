<script lang="ts">
	import { EAlertType } from '$lib/constants';

	export let type = EAlertType.Info;
	let classes = '';
	export { classes as class };
</script>

<div class="toast {classes}">
	<div class="alert {type}">
		<span>
			<slot />
		</span>
	</div>
</div>
