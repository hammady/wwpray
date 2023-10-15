<script>
	import Navbar from '$lib/components/Navbar.svelte';
	import Toast from '$lib/components/Toast.svelte';
	import { toasts } from '$lib/stores/toast';
	import { flip } from 'svelte/animate';
	import '../app.css';
</script>

<ul class="fixed top-navbar left-1/2 -translate-x-1/2 translate-y-8 flex flex-col gap-4 z-[100]">
	{#each $toasts as toast (toast.message)}
		<li animate:flip>
			<Toast type={toast.type}>
				{toast.message}
			</Toast>
		</li>
	{/each}
</ul>

<Navbar />
<slot />
