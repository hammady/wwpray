import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import calendar from 'dayjs/plugin/calendar';
import utc from 'dayjs/plugin/utc';
import { keys } from 'lodash';
import type { IMasjid } from './types';
import { EGroupBy, GROUP_BY_ROUTES } from './constants';

dayjs.extend(relativeTime);
dayjs.extend(utc);
dayjs.extend(calendar);

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

export const extractPrayersFromMasjids = (masjids: [string, IMasjid][]) => {
	if (!masjids.length) return [];
	const masjid = masjids[0][1];
	if (!masjid) return [];

	const prayerNames = keys(masjid.iqamas);
	return prayerNames;
};

export const getMasjidRoute = (id: string) => {
	return `${GROUP_BY_ROUTES[EGroupBy.Masjid]}#masjid_${id}`;
};
