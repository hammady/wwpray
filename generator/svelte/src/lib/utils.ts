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
import keys from 'lodash/keys';

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

export const getFormattedDate = (date: Dayjs) => {
	return date.format('DD MMM YYYY');
};

export const getDayNameFromDate = (date: Dayjs) => {
	return date.format('dddd');
};

export const parsePrayerTime = (dateStr: string) => {
	return dayjs(dateStr.toUpperCase(), 'h:mm A').local();
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
		const prayerTime = masjid.iqamas[prayer.name]?.time;
		const prayerDateTime = parsePrayerTime(prayerTime);
		if (!prayerTime) return false;
		return prayerDateTime.isAfter(currentTime);
	});

	if (!nextPrayer) {
		console.error('Something wrong, No next prayer found');
		return prayers[0];
	}

	return nextPrayer;
};

export const isPrayerComesAfter = (prayer1: TPrayer, prayer2: TPrayer) => {
	const prayer1Name = prayer1.name.toLocaleLowerCase();
	const prayer2Name = prayer2.name.toLocaleLowerCase();

	const prayersNames = keys(EPrayer);

	const prayer1Index = prayersNames.indexOf(prayer1Name);
	const prayer2Index = prayersNames.indexOf(prayer2Name);

	return prayer1Index > prayer2Index;
};

export const findMasjidWithMostNextPrayer = (masjids: [string, IMasjid][]) => {
	let mostNextPrayer: TPrayer | null = null;
	let mostMasjid: IMasjid | null = null;

	for (const masjid of masjids) {
		const masjidData = masjid[1];
		const masjidNextPrayer = getNextPrayerForMasjid(masjidData);

		if (!mostNextPrayer || isPrayerComesAfter(masjidNextPrayer, mostNextPrayer)) {
			mostNextPrayer = masjidNextPrayer;
			mostMasjid = masjidData;
		}
	}

	return { masjid: mostMasjid, nextPrayer: mostNextPrayer };
};

export const getNextPrayerForMasjids = (masjids: [string, IMasjid][]) => {
	const { nextPrayer } = findMasjidWithMostNextPrayer(masjids);
	return nextPrayer;
};

export const getTimeRemainingForNextPrayer = (majids: [string, IMasjid][]) => {
	const { masjid, nextPrayer } = findMasjidWithMostNextPrayer(majids);
	if (!masjid || !nextPrayer) return null;

	const currentTime = getCurrentLocalDateTime();

	const prayerTime = masjid.iqamas[nextPrayer.name]?.time;
	const prayerDateTime = parsePrayerTime(prayerTime);
	if (!prayerTime) return null;

	let seconds = prayerDateTime.diff(currentTime, 'seconds');
	let minutes = Math.floor(seconds / SECONDS_PER_MINUTE);
	seconds = seconds % SECONDS_PER_MINUTE;
	const hours = Math.floor(minutes / MINUTES_PER_HOUR);
	minutes = minutes % MINUTES_PER_HOUR;

	return { hours, minutes, seconds };
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
