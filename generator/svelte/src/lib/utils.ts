import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import calendar from 'dayjs/plugin/calendar';
import utc from 'dayjs/plugin/utc';
import keys from 'lodash/keys';
import type { IMasjid } from './types';
import { EGroupBy, GROUP_BY_ROUTES } from './constants';

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

export const extractPrayersFromMasjids = (masjids: [string, IMasjid][]) => {
	if (!masjids.length) return [];
	const masjid = masjids[0][1];
	if (!masjid) return [];

	const prayerNames = keys(masjid.iqamas);
	return prayerNames;
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
