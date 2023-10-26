<script lang="ts">
	import { SUBSCRIPTION_SIDEOVER_ID } from '$lib/constants';
	import { masjidListElement, onMasjidSubscribeClick } from '$lib/stores/elements';

	export let name: string;
	const onSubscribe = () => {
		return onMasjidSubscribeClick(name, $masjidListElement);
	};
</script>

<button on:click={onSubscribe}>
	<label class="btn btn-primary btn-sm drawer-button" for={SUBSCRIPTION_SIDEOVER_ID}>
		Subscribe
	</label>
</button>
