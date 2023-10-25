import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import utc from 'dayjs/plugin/utc';
dayjs.extend(relativeTime);
dayjs.extend(utc);

export const convertToRelativeTime = (isoDate: string) => {
	return dayjs.utc(isoDate).fromNow();
};
