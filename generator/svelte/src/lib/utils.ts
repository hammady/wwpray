import dayjs from 'dayjs';
import localizedFormat from 'dayjs/plugin/localizedFormat';
dayjs.extend(localizedFormat);

export const formatISODate = (date: string) => dayjs(date).format('L LT');
