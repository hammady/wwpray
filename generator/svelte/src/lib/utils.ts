import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import calendar from 'dayjs/plugin/calendar';
import utc from 'dayjs/plugin/utc';
import keys from 'lodash/keys';
import type { IMasjid, TPrayer } from './types';
import { EGroupBy, GROUP_BY_ROUTES, PRAYER_NAMES } from './constants';

dayjs.extend(relativeTime);
dayjs.extend(utc);
dayjs.extend(calendar);

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
	return dayjs.utc().local().format('YYYY-MM-DD HH:mm:ss');
};

/** Data transformation */

export const getPrayers = () => {
	const prayers: TPrayer[] = [];

	for (let i = 0; i < PRAYER_NAMES.length; i++) {
		const prayer = PRAYER_NAMES[i];
		(prayer as TPrayer).next = PRAYER_NAMES[i + 1] || PRAYER_NAMES[0];
		const prayerWithNext = prayer as TPrayer;
		prayers.push(prayerWithNext);
	}

	return prayers;
};

export const getCurrentPrayerForMasjid = (masjid: IMasjid) => {
	const currentTime = dayjs.utc().local().format('HH:mm:ss');
	const prayers = getPrayers();

	const currentPrayer = prayers.find((prayer) => {
		const prayerTime = masjid.iqamas[prayer]?.time;

		if (!prayerTime) return false;

		return currentTime < prayerTime;
	});

	if (!currentPrayer) {
		throw new Error('Something wrong, No current prayer found');
	}

	return currentPrayer;
};

export const getCurrentPrayerForMasjids = (masjids: [string, IMasjid][]) => {
	const firstMasjid = masjids[0][1];
	return getCurrentPrayerForMasjid(firstMasjid);
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

/** Path helpers */

export const getMasjidRoute = (id: string) => {
	return `${GROUP_BY_ROUTES[EGroupBy.Masjid]}#masjid_${id}`;
};

/** Classname helpers */
export { tw } from 'tail-cn';
