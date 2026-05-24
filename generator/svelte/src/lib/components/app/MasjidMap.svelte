<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import type { IMasjid } from '$lib/types';
	import { getNextPrayerForMasjids, getCurrentUTCDateSeconds } from '$lib/utils';

	export let masjids: [string, IMasjid][];

	let mapContainer: HTMLDivElement;
	let map: import('leaflet').Map | undefined;
	let locationMessage: string | null = null;

	function buildPopupContent(masjid: IMasjid, prayerName: string): string {
		const iqamaTime = masjid.iqamas[prayerName]?.time ?? '';
		const prayerLabel = prayerName.charAt(0).toUpperCase() + prayerName.slice(1);

		const iqamaSeconds = masjid.iqamas[prayerName]?.seconds_since_midnight_utc;
		let timeRemainingStr = '';
		let isPast = false;
		if (iqamaSeconds != null) {
			const currentTime = getCurrentUTCDateSeconds();
			// Circular time diff: always in [0, 86400). > 43200 means iqama is in the past.
			const diff = ((iqamaSeconds - currentTime) % 86400 + 86400) % 86400;
			isPast = diff > 43200;
			if (!isPast) {
				const hours = Math.floor(diff / 3600);
				const mins = Math.floor((diff % 3600) / 60);
				timeRemainingStr = hours > 0 ? `in ${hours}h ${mins}m` : `in ${mins}m`;
			} else {
				const secondsAgo = 86400 - diff;
				const hours = Math.floor(secondsAgo / 3600);
				const mins = Math.floor((secondsAgo % 3600) / 60);
				timeRemainingStr = hours > 0 ? `${hours}h ${mins}m ago` : `${mins}m ago`;
			}
		}

		const destParam = `${masjid.latitude},${masjid.longitude}`;
		const googleUrl = `https://www.google.com/maps/dir/?api=1&destination=${destParam}`;
		const appleUrl = `https://maps.apple.com/?daddr=${destParam}`;

		return `
			<div class="masjid-popup">
				<div class="popup-name">${masjid.display_name}</div>
				<div class="popup-prayer${isPast ? ' popup-prayer-past' : ''}">${prayerLabel}: <strong>${iqamaTime}</strong></div>
				${timeRemainingStr ? `<div class="popup-remaining${isPast ? ' popup-remaining-past' : ''}">${timeRemainingStr}</div>` : ''}
				<div class="popup-directions-label">Get directions</div>
				<div class="popup-directions-row">
					<a class="popup-directions" href="${appleUrl}" target="_blank" rel="noopener noreferrer">🗺 Apple Maps</a>
					<a class="popup-directions" href="${googleUrl}" target="_blank" rel="noopener noreferrer">🗺 Google Maps</a>
				</div>
			</div>`;
	}

	$: mappableMasjids = masjids.filter(
		([, m]) => typeof m.latitude === 'number' && typeof m.longitude === 'number'
	);

	onMount(async () => {
		try {
			const leaflet = await import('leaflet');
			const L = leaflet.default ?? leaflet;

			if (!mapContainer) {
				console.error('MasjidMap: mapContainer is null');
				return;
			}
			if (mappableMasjids.length === 0) {
				console.warn('MasjidMap: no masjids with coordinates');
				return;
			}

			// Initialize map without a view — we'll set it after geolocation resolves
			map = L.map(mapContainer);

			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
				attribution:
					'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
				maxZoom: 19
			}).addTo(map);

			// Add masjid markers
			const nextPrayerName = getNextPrayerForMasjids(mappableMasjids)?.name ?? '';
			const nextPrayerLabel = nextPrayerName.charAt(0).toUpperCase() + nextPrayerName.slice(1);
			const markerTime = getCurrentUTCDateSeconds();

			for (const [, masjid] of mappableMasjids) {
				const iqamaSeconds = masjid.iqamas[nextPrayerName]?.seconds_since_midnight_utc;
				const iqamaTime = masjid.iqamas[nextPrayerName]?.time ?? '';
				const markerPast = iqamaSeconds != null &&
					((iqamaSeconds - markerTime) % 86400 + 86400) % 86400 > 43200;

				const icon = L.divIcon({
					className: '',
					html: `<div class="masjid-map-marker${markerPast ? ' marker-past' : ''}">
						<span class="marker-name">${masjid.display_name}</span>
						<span class="marker-divider">·</span>
						<span class="marker-time">${nextPrayerLabel} ${iqamaTime}</span>
					</div>`,
					iconAnchor: [0, 0]
				});

				L.marker([masjid.latitude as number, masjid.longitude as number], { icon })
					.addTo(map)
					.bindPopup(() => buildPopupContent(masjid, nextPrayerName), { minWidth: 200 });
			}

			// Close popup when clicking anywhere inside it (including direction links)
			map.on('popupopen', (e) => {
				const container = e.popup.getElement();
				if (container) {
					container.addEventListener('click', () => map!.closePopup(), { once: false });
				}
			});

			// Try to center on user location (5 km radius), fall back to masjid bounding box
			const centerOnUserLocation = (): Promise<boolean> =>
				new Promise((resolve) => {
					if (!navigator.geolocation) return resolve(false);
					locationMessage =
					'📍 Allow location access to show nearby masjids within 5 km';
					navigator.geolocation.getCurrentPosition(
(pos) => {						locationMessage = null;
						const { latitude, longitude } = pos.coords;
						const userLatLng = L.latLng(latitude, longitude);

// 5 km radius — zoom 13 ≈ 4.5 km center-to-edge on a 480px tall map
						map!.setView(userLatLng, 13);

							// Show a subtle pulsing dot for the user's position
							L.circleMarker(userLatLng, {
								radius: 8,
								fillColor: '#3b82f6',
								fillOpacity: 0.9,
								color: '#ffffff',
								weight: 2
							})
								.addTo(map!)
								.bindPopup('You are here');

							resolve(true);
						},
						() => {
						locationMessage = '📍 Location not shared — showing all masjids';
						resolve(false);
					},
						{ timeout: 6000, maximumAge: 60_000 }
					);
				});

			const centeredOnUser = await centerOnUserLocation();

			if (!centeredOnUser) {
				// Fall back to bounding box of all masjids
				const bounds = L.latLngBounds(
					mappableMasjids.map(([, m]) => [m.latitude as number, m.longitude as number])
				);
				map.fitBounds(bounds, { padding: [8, 8] });
			}
		} catch (e) {
			console.error('MasjidMap init error:', e);
		}
	});

	onDestroy(() => {
		map?.remove();
	});
</script>

<div class="not-prose relative">
	{#if locationMessage}
		<div
			class="location-message"
			role="button"
			tabindex="0"
			on:click={() => (locationMessage = null)}
			on:keydown={(e) => e.key === 'Enter' && (locationMessage = null)}
		>{locationMessage} &times;</div>
	{/if}
	<div bind:this={mapContainer} class="masjid-map"></div>
</div>

<style>
	.masjid-map {
		width: 100%;
		height: 480px;
		border-radius: 1rem;
		overflow: hidden;
		z-index: 0;
	}

	.location-message {
		position: absolute;
		top: 12px;
		left: 50%;
		transform: translateX(-50%);
		z-index: 1000;
		background: white;
		border: 1.5px solid #e2e8f0;
		border-radius: 9999px;
		padding: 8px 18px;
		font-size: 13px;
		font-weight: 500;
		color: #1a202c;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
		white-space: nowrap;
		cursor: pointer;
	}

	:global(.masjid-map-marker) {
		display: inline-flex;
		align-items: center;
		gap: 4px;
		background: white;
		border: 1.5px solid #e2e8f0;
		border-radius: 9999px;
		padding: 5px 12px;
		font-size: 12px;
		font-weight: 600;
		white-space: nowrap;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
		cursor: pointer;
		transition: transform 0.1s ease, box-shadow 0.1s ease;
		color: #1a202c;
	}

	:global(.masjid-map-marker:hover) {
		transform: scale(1.06);
		box-shadow: 0 4px 14px rgba(0, 0, 0, 0.22);
		z-index: 1000;
	}

	:global(.marker-past) {
		opacity: 0.4;
		border-color: #cbd5e0;
		box-shadow: none;
	}

	:global(.marker-name) {
		font-weight: 700;
	}

	:global(.marker-divider) {
		color: #a0aec0;
		font-weight: 400;
	}

	:global(.marker-time) {
		color: #4a5568;
		font-weight: 500;
	}

	:global(.masjid-popup) {
		font-family: inherit;
		min-width: 200px;
	}

	:global(.popup-name) {
		font-size: 14px;
		font-weight: 700;
		color: #1a202c;
		margin-bottom: 6px;
	}

	:global(.popup-prayer) {
		font-size: 13px;
		color: #4a5568;
		margin-bottom: 2px;
	}

	:global(.popup-remaining) {
		font-size: 12px;
		color: #718096;
		margin-bottom: 8px;
	}

	:global(.popup-prayer-past) {
		text-decoration: line-through;
		color: #a0aec0;
	}

	:global(.popup-remaining-past) {
		color: #e53e3e;
		font-weight: 600;
	}

	:global(.popup-directions-label) {
		font-size: 11px;
		color: #718096;
		margin-top: 8px;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	:global(.popup-directions-row) {
		display: flex;
		gap: 12px;
		margin-top: 4px;
	}

	:global(.popup-directions) {
		font-size: 13px;
		font-weight: 600;
		color: #3b82f6;
		text-decoration: none;
	}

	:global(.popup-directions:hover) {
		text-decoration: underline;
	}
</style>
