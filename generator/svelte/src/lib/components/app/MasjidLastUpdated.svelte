<script lang="ts">
	import { convertToRelativeTime } from '$lib/utils';

	export let lastUpdated: string;
	export let isShort = false;

	const timeRendered = (node: HTMLTimeElement, lastUpdated: string) => {
		node.innerHTML = convertToRelativeTime(lastUpdated);
	};
</script>

<span>
	{#if !isShort}
		{'Last updated '}
	{/if}
	<time datetime={lastUpdated} use:timeRendered={lastUpdated}>
		<noscript>{lastUpdated} UTC</noscript>
	</time>{#if !isShort}
		{'.'}
	{/if}
</span>
