<script>
	import Navbar from '$lib/components/Navbar.svelte';
	import Toast from '$lib/components/Toast.svelte';
	import { toast, toasts } from '$lib/stores/toast';
	import { flip } from 'svelte/animate';
	import '../app.css';

	setTimeout(() => {
		toast.success('Success!');
	}, 1500);

	setTimeout(() => {
		toast.error('Error!');
	}, 3000);

	setTimeout(() => {
		toast.info('Info!');
	}, 4500);

	setTimeout(() => {
		toast.warn('Warning!');
	}, 5500);
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
