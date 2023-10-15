<script lang="ts">
	import { APP_NAME } from '$lib/constants';
</script>

<nav class="sticky top-0 z-50 navbar bg-base-100 md:px-4 2xl:px-8 h-navbar shadow-md">
	<div class="flex-1">
		<a href="/" class="btn btn-ghost normal-case text-xl">
			{APP_NAME}
		</a>
	</div>
	<div class="flex gap-4">
		<form action="/" method="GET">
			<div class="form-control pl-6">
				<input
					name="search"
					type="text"
					placeholder="Search for masjid"
					class="input input-bordered w-56 md:w-72"
				/>
			</div>
		</form>
		<button class="btn btn-ghost btn-circle">
			<div class="indicator">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-5 w-5"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					><path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
					/></svg
				>
				<span class="badge badge-xs badge-primary indicator-item" />
			</div>
		</button>
	</div>
</nav>
