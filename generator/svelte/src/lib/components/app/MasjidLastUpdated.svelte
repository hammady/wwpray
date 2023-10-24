<script lang="ts">
	import { convertToRelativeTime } from '$lib/utils';

	export let lastUpdated: string;

	const timeRendered = (node: HTMLTimeElement, lastUpdated: string) => {
		node.innerHTML = convertToRelativeTime(lastUpdated);
	};
</script>

<span>
	Last updated <time datetime={lastUpdated} use:timeRendered={lastUpdated}>
		<noscript>{lastUpdated} UTC</noscript>
	</time>.
</span>
