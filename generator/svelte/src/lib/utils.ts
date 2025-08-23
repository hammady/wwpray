import dayjs, { Dayjs } from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import calendar from 'dayjs/plugin/calendar';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import utc from 'dayjs/plugin/utc';
import type { IMasjid, TPrayer } from './types';
import {
	EDay,
	EGroupBy,
	EPrayer,
	GROUP_BY_ROUTES,
	MINUTES_PER_HOUR,
	PRAYER_NAMES,
	SECONDS_PER_MINUTE
} from './constants';

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

export const getCurrentUTCDateSeconds = () => {
	const todayUTC = dayjs().utc();
	const today = todayUTC.hour(0).minute(0).second(0).millisecond(0);
	return todayUTC.diff(today, 'seconds');
};

export const getFormattedDate = (date: Dayjs) => {
	return date.format('DD MMM YYYY');
};

export const getDayNameFromDate = (date: Dayjs) => {
	return date.format('dddd');
};

/** Data transformation */

const getPrayers = () => {
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

export const getNextPrayerForMasjid = (masjid: {
	iqamas: Record<string, { seconds_since_midnight_utc: number | null }>;
}) => {
	const currentTime = getCurrentUTCDateSeconds();
	const prayers = getPrayers();

	const nextPrayer = prayers.find((prayer) => {
		const prayerTime = masjid.iqamas[prayer.name]?.seconds_since_midnight_utc;
		if (!prayerTime) return false;
		return prayerTime > currentTime;
	});

	if (!nextPrayer) {
		console.error('Something wrong, No next prayer found');
		return prayers[0];
	}

	return nextPrayer;
};

export const findMasjidWithLeastNextPrayer = (masjids: [string, IMasjid][]) => {
	const masjid = masjids[0][1];
	const nextPrayer = getNextPrayerForMasjid(masjid);

	return { masjid, nextPrayer };
};

export const getNextPrayerForMasjids = (masjids: [string, IMasjid][], now?: number) => {
	if (!masjids.length) return undefined;
	const prayers = getPrayers();
	const currentTime = typeof now === 'number' ? now : getCurrentUTCDateSeconds();

	// For each prayer, find the minimum future iqama time across all masjids
	let soonestPrayer: TPrayer | undefined = undefined;
	let soonestTime = Number.POSITIVE_INFINITY;

	for (const prayer of prayers) {
		let minTime = Number.POSITIVE_INFINITY;
		for (const [, masjid] of masjids) {
			const iqama = masjid.iqamas[prayer.name];
			if (iqama && typeof iqama.seconds_since_midnight_utc === 'number') {
				const t = iqama.seconds_since_midnight_utc;
				if (t > currentTime && t < minTime) {
					minTime = t;
				}
			}
		}
		// Only update if this prayer's soonest time is earlier than any previous
		if (minTime < soonestTime) {
			soonestTime = minTime;
			soonestPrayer = prayer;
		}
	}

	// If all prayers are in the past, return the first prayer (e.g., for after isha)
	if (!soonestPrayer) {
		soonestPrayer = prayers[0];
	}
	return soonestPrayer;
};

export const getTimeRemainingForNextPrayer = (masjids: [string, IMasjid][], now?: number) => {
	if (!masjids.length) return null;
	const currentTime = typeof now === 'number' ? now : getCurrentUTCDateSeconds();
	const nextPrayer = getNextPrayerForMasjids(masjids, currentTime);
	if (!nextPrayer) return null;

	// Find all times for that prayer
	const times: number[] = masjids
		.map(([, masjid]) => masjid.iqamas[nextPrayer.name]?.seconds_since_midnight_utc)
		.filter((t): t is number => typeof t === 'number');
	if (!times.length) return null;

	// Find the soonest future time
	const futureTimes = times.filter(t => t > currentTime);
	let soonestTime: number;
	if (futureTimes.length > 0) {
		soonestTime = Math.min(...futureTimes);
	} else {
		// All are in the past, so wrap to the earliest for the next day
		soonestTime = Math.min(...times);
	}

	let seconds = soonestTime - currentTime;
	if (seconds < 0) {
		seconds += 24 * 60 * 60;
	}
	let minutes = Math.floor(seconds / SECONDS_PER_MINUTE);
	const remainingSeconds = seconds % SECONDS_PER_MINUTE;
	const hours = Math.floor(minutes / MINUTES_PER_HOUR);
	minutes = minutes % MINUTES_PER_HOUR;

	return { hours, minutes, seconds: remainingSeconds };
};

export const getSortedPrayers = (masjids: [string, IMasjid][]) => {
	if (!masjids.length) return [];

	const prayers = getPrayers();
	let nextPrayer = getNextPrayerForMasjids(masjids);
	const sortedPrayers: TPrayer[] = [];

	while (sortedPrayers.length < prayers.length) {
		if (!nextPrayer) continue;
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

		const aSeconds = aPrayer.seconds_since_midnight_utc ?? 0;
		const bSeconds = bPrayer.seconds_since_midnight_utc ?? 0;

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
	const sortedPrayers = getSortedPrayers(masjids);
	return sortedPrayers[sortedPrayers.length - 1];
};

export const shouldDefaultToJumas = (masjids: [string, IMasjid][]) => {
	const currentPrayer = getCurrentPrayer(masjids);

	const isFriday = dayjs().day() === EDay.Friday;
	const isZuhrNext = currentPrayer === EPrayer.Fajr;

	return isFriday && isZuhrNext;
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
