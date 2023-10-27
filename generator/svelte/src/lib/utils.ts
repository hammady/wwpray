import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import calendar from 'dayjs/plugin/calendar';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import utc from 'dayjs/plugin/utc';
import type { IMasjid, TPrayer } from './types';
import { EGroupBy, GROUP_BY_ROUTES, PRAYER_NAMES } from './constants';

dayjs.extend(utc);
dayjs.extend(relativeTime);
dayjs.extend(calendar);
dayjs.extend(customParseFormat);

/** Date helpers */
export const convertToRelativeTime = (isoDate: string) => {
	return dayjs.utc(isoDate).fromNow();
};

export const convertToCalendarTime = (isoDate?: string) => {
	if (!isoDate) return null;

	return dayjs.utc(isoDate).calendar(null, {
		sameDay: '[Today]',
		nextDay: '[Tomorrow]',
		nextWeek: '[Next Week]',
		lastDay: '[Yesterday]',
		lastWeek: '[Last Week]',
		sameElse: 'DD/MM/YYYY'
	});
};

export const isToday = (isoDate: string) => {
	return dayjs.utc(isoDate).isSame(dayjs.utc(), 'day');
};

export const isYesterday = (isoDate: string) => {
	return dayjs.utc(isoDate).isSame(dayjs.utc().subtract(1, 'day'), 'day');
};

export const isOlderThanAWeek = (isoDate: string) => {
	return dayjs.utc(isoDate).isBefore(dayjs.utc().subtract(7, 'day'), 'day');
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
		throw new Error('Something wrong, No current prayer found');
	}

	return nextPrayer;
};

export const getNextPrayerForMasjids = (masjids: [string, IMasjid][]) => {
	const firstMasjid = masjids[0][1];
	return getNextPrayerForMasjid(firstMasjid);
};

export const getSortedPrayers = (masjids: [string, IMasjid][]) => {
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
	return masjids.sort((a, b) => {
		const aPrayer = a[1].iqamas[prayerName];
		const bPrayer = b[1].iqamas[prayerName];

		if (!aPrayer) return 1;
		if (!bPrayer) return -1;

		return aPrayer.time.localeCompare(bPrayer.time);
	});
};

export const isNextIqama = (masjids: [string, IMasjid][], masjidName: string, iqama: string) => {
	const masjid = masjids.find((m) => m[0] === masjidName)?.[1];

	if (!masjid) {
		throw new Error('Something wrong, masjid not found');
	}

	return getNextPrayerForMasjid(masjid).name === iqama;
};

/** Path helpers */

export const getMasjidRoute = (id: string) => {
	return `${GROUP_BY_ROUTES[EGroupBy.Masjid]}#masjid_${id}`;
};

/** Classname helpers */
export { tw } from 'tail-cn';
