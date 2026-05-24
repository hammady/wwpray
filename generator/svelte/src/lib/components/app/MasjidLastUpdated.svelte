<script lang="ts">
	import { convertToRelativeTime } from '$lib/utils';
	import { clock } from '$lib/stores/clock';

	export let lastUpdated: string;
	export let isShort = false;

	const timeRendered = (node: HTMLTimeElement, params: { lastUpdated: string; tick: number }) => {
		node.innerHTML = convertToRelativeTime(params.lastUpdated);
		return {
			update({ lastUpdated }: { lastUpdated: string }) {
				node.innerHTML = convertToRelativeTime(lastUpdated);
			}
		};
	};
</script>

<span>
	{#if !isShort}
		{'Last updated '}
	{/if}
	<time datetime={lastUpdated} use:timeRendered={{ lastUpdated, tick: $clock }}>
		<noscript>{lastUpdated} UTC</noscript>
	</time>{#if !isShort}
		{'.'}
	{/if}
</span>
