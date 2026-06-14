<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import type { IMasjid } from '$lib/types';
	import { getNextPrayerForMasjids, getCurrentUTCDateSeconds, getIqamaRelativeTime } from '$lib/utils';
	import { clock } from '$lib/stores/clock';

	export let masjids: [string, IMasjid][];
	export let showJumas: boolean = false;

	// Set to true to test Friday behaviour
	const isFriday = new Date().getDay() === 5;

	let mapContainer: HTMLDivElement;
	let map: import('leaflet').Map | undefined;
	let leafletLib: typeof import('leaflet') | undefined;
	let markersLayer: import('leaflet').LayerGroup | undefined;
	let isMapReady = false;
	let locationMessage: string | null = null;

	let openPopup: import('leaflet').Popup | null = null;
	let openMasjid: IMasjid | null = null;
	let openPrayerName = '';
	let openIsJumas = false;

	const unsubscribeClock = clock.subscribe(() => {
		if (openPopup && openMasjid) {
			openPopup.setContent(
				openIsJumas
					? buildJumasPopupContent(openMasjid)
					: buildPopupContent(openMasjid, openPrayerName)
			);
		}
	});

	$: mappableMasjids = masjids.filter(
		([, m]) => typeof m.latitude === 'number' && typeof m.longitude === 'number'
	);

	$: if (isMapReady) {
		createMarkers(showJumas);
	}

	function getNextJumaInfo(masjid: IMasjid): { label: string; seconds: number | null; found: boolean; index: number; total: number } {
		const secondsArr = masjid.jumas_seconds_since_midnight_utc ?? [];
		const jumasArr = masjid.jumas ?? [];
		const total = jumasArr.length;
		const currentTime = getCurrentUTCDateSeconds();
		let minTime = Infinity;
		let minIndex = -1;
		for (let i = 0; i < secondsArr.length; i++) {
			const s = secondsArr[i];
			if (s != null && s >= currentTime && s < minTime) {
				minTime = s;
				minIndex = i;
			}
		}
		if (minIndex === -1) {
			return { label: 'No upcoming Jumaa prayers', seconds: null, found: false, index: -1, total };
		}
		const baseLabel = jumasArr[minIndex] ?? '';
		return {
			label: `${baseLabel} (${minIndex + 1}/${total} Jumaa prayers)`,
			seconds: secondsArr[minIndex] ?? null,
			found: true,
			index: minIndex,
			total
		};
	}

	function buildJumasPopupContent(masjid: IMasjid): string {
		const jumasArr = masjid.jumas ?? [];
		const secondsArr = masjid.jumas_seconds_since_midnight_utc ?? [];

		const destParam = `${masjid.latitude},${masjid.longitude}`;
		const googleUrl = `https://www.google.com/maps/dir/?api=1&destination=${destParam}`;
		const appleUrl = `https://maps.apple.com/?daddr=${destParam}`;

		const jumasHtml =
			jumasArr.length > 0
				? jumasArr
						.map((label, i) => {
							if (!isFriday) {
								return `<div class="popup-juma-item">
									<div class="popup-prayer"><strong>${label}</strong></div>
								</div>`;
							}
							const s = secondsArr[i] ?? null;
							const relTime = getIqamaRelativeTime(s);
							const isPast = relTime?.isPast ?? false;
							const timeLabel = relTime?.label ?? '';
							return `<div class="popup-juma-item">
								<div class="popup-prayer"><strong class="${isPast ? 'popup-time-past' : ''}">${label}</strong></div>
								${timeLabel ? `<div class="popup-remaining ${isPast ? 'popup-remaining-past' : 'popup-remaining-future'}">${timeLabel}</div>` : ''}
							</div>`;
						})
						.join('')
				: `<div class="popup-prayer">No Jumu'ah times available</div>`;

		return `
			<div class="masjid-popup">
				<div class="popup-name">${masjid.display_name}</div>
				<div class="popup-jumas">${jumasHtml}</div>
				<div class="popup-directions-label">Get directions</div>
				<div class="popup-directions-row">
					<a class="popup-directions" href="${appleUrl}" target="_blank" rel="noopener noreferrer">🗺 Apple Maps</a>
					<a class="popup-directions" href="${googleUrl}" target="_blank" rel="noopener noreferrer">🗺 Google Maps</a>
				</div>
			</div>`;
	}

	function buildPopupContent(masjid: IMasjid, prayerName: string): string {
		const iqamaTime = masjid.iqamas[prayerName]?.time ?? '';
		const prayerLabel = prayerName.charAt(0).toUpperCase() + prayerName.slice(1);

		const iqamaSeconds = masjid.iqamas[prayerName]?.seconds_since_midnight_utc ?? null;
		const relTime = getIqamaRelativeTime(iqamaSeconds);
		const timeRemainingStr = relTime?.label ?? '';
		const isPast = relTime?.isPast ?? false;

		const destParam = `${masjid.latitude},${masjid.longitude}`;
		const googleUrl = `https://www.google.com/maps/dir/?api=1&destination=${destParam}`;
		const appleUrl = `https://maps.apple.com/?daddr=${destParam}`;

		return `
			<div class="masjid-popup">
				<div class="popup-name">${masjid.display_name}</div>
				<div class="popup-prayer">${prayerLabel}: <strong class="${isPast ? 'popup-time-past' : ''}">${iqamaTime}</strong></div>
				${timeRemainingStr ? `<div class="popup-remaining ${isPast ? 'popup-remaining-past' : 'popup-remaining-future'}">${timeRemainingStr}</div>` : ''}
				<div class="popup-directions-label">Get directions</div>
				<div class="popup-directions-row">
					<a class="popup-directions" href="${appleUrl}" target="_blank" rel="noopener noreferrer">🗺 Apple Maps</a>
					<a class="popup-directions" href="${googleUrl}" target="_blank" rel="noopener noreferrer">🗺 Google Maps</a>
				</div>
			</div>`;
	}

	function createMarkers(isJumasMode: boolean) {
		if (!map || !markersLayer || !leafletLib) return;
		const L = leafletLib;
		markersLayer.clearLayers();
		const markerTime = getCurrentUTCDateSeconds();

		if (isJumasMode) {
			for (const [, masjid] of mappableMasjids) {
				const { label, seconds: nextSeconds, found } = getNextJumaInfo(masjid);
				const isStale = Date.now() - new Date(masjid.last_updated + 'Z').getTime() > 86_400_000;
				const relTime = nextSeconds != null ? getIqamaRelativeTime(nextSeconds) : null;
				const isPast = !found || (relTime?.isPast ?? false);
				const markerClass = [isFriday && isPast ? 'marker-past' : 'marker-future', isStale ? 'marker-stale' : ''].join(' ').trim();
				const markerLabel = isFriday ? label : 'Tap to show Jumaa prayers';

				const icon = L.divIcon({
					className: '',
					html: `<div class="masjid-map-marker ${markerClass}">
						<span class="marker-name">${masjid.display_name}</span>
						<span class="marker-divider">·</span>
						<span class="marker-time">${markerLabel}</span>
					</div>`,
					iconAnchor: [0, 0]
				});

				const marker = L.marker([masjid.latitude as number, masjid.longitude as number], { icon })
					.addTo(markersLayer)
					.bindPopup(() => buildJumasPopupContent(masjid), { minWidth: 200 });

				marker.on('popupopen', (e) => {
					openMasjid = masjid;
					openPrayerName = '';
					openIsJumas = true;
					openPopup = (e as unknown as { popup: import('leaflet').Popup }).popup;
				});
				marker.on('popupclose', () => {
					openPopup = null;
					openMasjid = null;
					openIsJumas = false;
				});
			}
		} else {
			const nextPrayerName = getNextPrayerForMasjids(mappableMasjids)?.name ?? '';
			const nextPrayerLabel = nextPrayerName.charAt(0).toUpperCase() + nextPrayerName.slice(1);

			for (const [, masjid] of mappableMasjids) {
				const iqamaSeconds = masjid.iqamas[nextPrayerName]?.seconds_since_midnight_utc;
				const iqamaTime = masjid.iqamas[nextPrayerName]?.time ?? '';
				const isStale = Date.now() - new Date(masjid.last_updated + 'Z').getTime() > 86_400_000;
				const isPast =
					iqamaSeconds != null &&
					((iqamaSeconds - markerTime) % 86400 + 86400) % 86400 > 43200;
				const markerClass = [isPast ? 'marker-past' : 'marker-future', isStale ? 'marker-stale' : ''].join(' ').trim();

				const icon = L.divIcon({
					className: '',
					html: `<div class="masjid-map-marker ${markerClass}">
						<span class="marker-name">${masjid.display_name}</span>
						<span class="marker-divider">·</span>
						<span class="marker-time">${nextPrayerLabel} ${iqamaTime}</span>
					</div>`,
					iconAnchor: [0, 0]
				});

				const marker = L.marker([masjid.latitude as number, masjid.longitude as number], { icon })
					.addTo(markersLayer)
					.bindPopup(() => buildPopupContent(masjid, nextPrayerName), { minWidth: 200 });

				marker.on('popupopen', (e) => {
					openMasjid = masjid;
					openPrayerName = nextPrayerName;
					openIsJumas = false;
					openPopup = (e as unknown as { popup: import('leaflet').Popup }).popup;
				});
				marker.on('popupclose', () => {
					openPopup = null;
					openMasjid = null;
					openIsJumas = false;
				});
			}
		}
	}

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

			map = L.map(mapContainer);
			leafletLib = L;

			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
				attribution:
					'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
				maxZoom: 19
			}).addTo(map);

			markersLayer = L.layerGroup().addTo(map);
			isMapReady = true;

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
					locationMessage = '📍 Allow location access to show nearby masjids within 5 km';
					navigator.geolocation.getCurrentPosition(
						(pos) => {
							locationMessage = null;
							const { latitude, longitude } = pos.coords;
							const userLatLng = L.latLng(latitude, longitude);

							map!.setView(userLatLng, 13);

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
		unsubscribeClock();
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

	:global(.marker-stale) {
		opacity: 0.4;
		border-color: #cbd5e0;
		box-shadow: none;
	}

	:global(.marker-past .marker-time) {
		color: #e53e3e;
	}

	:global(.marker-future .marker-time) {
		color: #16a34a;
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

	:global(.popup-time-past) {
		text-decoration: line-through;
		color: #a0aec0;
	}

	:global(.popup-remaining-past) {
		color: #e53e3e;
		font-weight: 600;
	}

	:global(.popup-remaining-future) {
		color: #16a34a;
		font-weight: 600;
	}

	:global(.popup-jumas) {
		margin-bottom: 4px;
	}

	:global(.popup-juma-item) {
		padding: 3px 0;
		border-bottom: 1px solid #f0f0f0;
	}

	:global(.popup-juma-item:last-child) {
		border-bottom: none;
		margin-bottom: 6px;
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
