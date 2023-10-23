import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
dayjs.extend(relativeTime);

export const convertToRelativeTime = (isoDate: string) => dayjs().from(isoDate);
