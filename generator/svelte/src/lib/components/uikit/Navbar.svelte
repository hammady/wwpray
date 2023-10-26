<script lang="ts">
	import { APP_NAME } from '$lib/constants';
</script>

<nav class="top-0 z-50 navbar bg-base-100 md:px-4 2xl:px-8 h-navbar shadow-md">
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
	</div>
</nav>
