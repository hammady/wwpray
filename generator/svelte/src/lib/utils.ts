import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import utc from 'dayjs/plugin/utc';
import { keys } from 'lodash';
import type { IMasjid } from './types';

dayjs.extend(relativeTime);
dayjs.extend(utc);

export const convertToRelativeTime = (isoDate: string) => {
	return dayjs.utc(isoDate).fromNow();
};

export const extractPrayersFromMasjids = (masjids: [string, IMasjid][]) => {
	if (!masjids.length) return [];
	const masjid = masjids[0][1];
	if (!masjid) return [];

	const prayerNames = keys(masjid.iqamas);
	return prayerNames;
};
