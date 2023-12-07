import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import calendar from 'dayjs/plugin/calendar';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import utc from 'dayjs/plugin/utc';
import type { IMasjid, TPrayer } from './types';
import { EDay, EGroupBy, EPrayer, GROUP_BY_ROUTES, PRAYER_NAMES } from './constants';

dayjs.extend(utc);
dayjs.extend(relativeTime);
dayjs.extend(calendar);
dayjs.extend(customParseFormat);

/** Date helpers */
export const convertToRelativeTime = (isoDate: string) => {
	return dayjs.utc(isoDate).fromNow();
};

export const convertToCalendarTime = (dateStr?: string) => {
	if (!dateStr) return null;

	return dayjs.utc(dateStr).local().calendar(null, {
		sameDay: '[Today]',
		nextDay: '[Tomorrow]',
		nextWeek: '[Next Week]',
		lastDay: '[Yesterday]',
		lastWeek: '[Last Week]',
		sameElse: 'DD/MM/YYYY'
	});
};

export const isToday = (dateStr: string) => {
	return dayjs(dateStr).isSame(dayjs(), 'day');
};

export const isYesterday = (isoDate: string) => {
	return dayjs(isoDate).isSame(dayjs().subtract(1, 'day'), 'day');
};

export const isOlderThanAWeek = (isoDate: string) => {
	return dayjs(isoDate).isBefore(dayjs().subtract(7, 'day'), 'day');
};

export const getCurrentLocalDateTime = () => {
	return dayjs.utc().local();
};

/** Data transformation */

export const getPrayers = () => {
	const prayers: Partial<TPrayer>[] = PRAYER_NAMES.map((prayer) => ({ name: prayer }));
	const tPrayers: TPrayer[] = [];

	for (let i = 0; i < prayers.length; i++) {
		const prayer = prayers[i];
		const next = prayers[i + 1] || prayers[0];
		prayer.next = next as TPrayer;
		tPrayers.push(prayer as TPrayer);
	}

	return tPrayers;
};

export const getNextPrayerForMasjid = (masjid: { iqamas: Record<string, { time: string }> }) => {
	const currentTime = getCurrentLocalDateTime();
	const prayers = getPrayers();

	const nextPrayer = prayers.find((prayer) => {
		const prayerTime = masjid.iqamas[prayer.name]?.time.toUpperCase();
		const prayerDateTime = dayjs(prayerTime, 'h:mm A').local();
		if (!prayerTime) return false;
		return prayerDateTime.isAfter(currentTime);
	});

	if (!nextPrayer) {
		console.error('Something wrong, No next prayer found');
		return prayers[0];
	}

	return nextPrayer;
};

export const getNextPrayerForMasjids = (masjids: [string, IMasjid][]) => {
	const firstMasjid = masjids[0][1];
	return getNextPrayerForMasjid(firstMasjid);
};

export const getSortedPrayers = (masjids: [string, IMasjid][]) => {
	if (!masjids.length) return [];

	const prayers = getPrayers();
	let nextPrayer = getNextPrayerForMasjids(masjids);
	const sortedPrayers: TPrayer[] = [];

	while (sortedPrayers.length < prayers.length) {
		sortedPrayers.push(nextPrayer);
		nextPrayer = nextPrayer.next;
	}

	return sortedPrayers.map((prayer) => prayer.name);
};

export const sortMasjidsForPrayer = (masjids: [string, IMasjid][], prayerName: string) => {
	return [...masjids].sort((a, b) => {
		const aPrayer = a[1].iqamas[prayerName];
		const bPrayer = b[1].iqamas[prayerName];

		if (!aPrayer) return 1;
		if (!bPrayer) return -1;

		const aSeconds = aPrayer.seconds_since_midnight_utc;
		const bSeconds = bPrayer.seconds_since_midnight_utc;

		return aSeconds - bSeconds;
	});
};

export const isNextIqama = (masjids: [string, IMasjid][], masjidName: string, iqama: string) => {
	const masjid = masjids.find((m) => m[0] === masjidName)?.[1];

	if (!masjid) {
		console.error('Something wrong, masjid not found');
		return false;
	}

	return getNextPrayerForMasjid(masjid).name === iqama;
};

export const getCurrentPrayer = (masjids: [string, IMasjid][]) => {
	const currentTime = getCurrentLocalDateTime();
	const prayers = getPrayers();

	let leastRemainingTime = Infinity;
	let currentPrayer: TPrayer | undefined;

	for (const masjid of masjids) {
		const masjidPrayers = masjid[1].iqamas;
		for (const prayer of prayers) {
			const prayerTime = masjidPrayers[prayer.name]?.time.toUpperCase();
			if (!prayerTime) continue;
			const prayerDateTime = dayjs(prayerTime, 'h:mm A').local();
			const remainingTime = prayerDateTime.diff(currentTime, 'second');
			if (remainingTime < leastRemainingTime) {
				leastRemainingTime = remainingTime;
				currentPrayer = prayer;
			}
		}
	}

	return currentPrayer;
};

export const shouldDefaultToJumas = (masjids: [string, IMasjid][]) => {
	const currentPrayer = getCurrentPrayer(masjids);

	const isThursday = dayjs().day() === EDay.Thursday;
	const isFriday = dayjs().day() === EDay.Friday;

	const isMaghrib = currentPrayer?.name === EPrayer.Maghrib;
	const isIsha = currentPrayer?.name === EPrayer.Isha;

	return (isThursday && (isMaghrib || isIsha)) || (isFriday && !isMaghrib && !isIsha);
};

export const getFilteredMasjids = (search: string, masjids: [string, IMasjid][]) =>
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	masjids.filter(([_, masjid]) => {
		const name = masjid.display_name.toLowerCase();
		const address = masjid.address.toLowerCase();
		search ??= '';
		search = search.toLowerCase();
		search = search.trim();

		return name.toLowerCase().includes(search) || address.toLowerCase().includes(search);
	});

/** Path helpers */

export const getMasjidRoute = (id: string) => {
	return `${GROUP_BY_ROUTES[EGroupBy.Masjid]}#masjid_${id}`;
};

/** Classname helpers */
export { tw } from 'tail-cn';
