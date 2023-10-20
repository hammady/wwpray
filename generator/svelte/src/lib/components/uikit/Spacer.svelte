<script lang="ts">
	const SIZES = {
		x: {
			sm: 'w-1',
			md: 'w-2',
			lg: 'w-3',
			xl: 'w-4'
		},
		y: {
			sm: 'h-1',
			md: 'h-2',
			lg: 'h-3',
			xl: 'h-4'
		}
	} as const;

	export let size: keyof (typeof SIZES)['y'] = 'sm';
	export let axis: keyof typeof SIZES = 'y';
</script>

<div class={SIZES[axis][size]} />
