<script lang="ts">
	export let { id, ...props } = $$props as {
		id: string;
		'close-aria-label': string;
	};
</script>

<div class="drawer drawer-end">
	<input {id} type="checkbox" class="drawer-toggle" />
	<div class="drawer-content">
		<slot name="page" />
	</div>
	<div class="drawer-side z-[100]">
		<label for={id} aria-label={props['close-aria-label']} class="drawer-overlay" />
		<div
			class="relative menu p-4 w-[clamp(320px,90vw,420px)] min-h-full bg-base-200 text-base-content"
		>
			<slot name="side" />
		</div>
	</div>
</div>
