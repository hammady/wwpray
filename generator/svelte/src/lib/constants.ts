export const APP_NAME = 'Where & When to Pray';
export const APP_NAME_SHORT = 'wwpray';

export enum EAlertType {
	Info = 'alert-info',
	Success = 'alert-success',
	Warning = 'alert-warning',
	Error = 'alert-error'
}

export const ALERT_ICONS = {
	[EAlertType.Success]: 'check-circle',
	[EAlertType.Error]: 'x-circle',
	[EAlertType.Info]: 'information-circle',
	[EAlertType.Warning]: 'exclamation-circle'
};

export const TOAST_TIMEOUT = 5000;

export const SUBSCRIPTION_SIDEOVER_ID = 'subscription-sideover';

export enum EGroupBy {
	Prayer = 'Prayers',
	Masjid = 'Masjids',
	jumas = 'Jumas'
}

export const GROUP_BY_ROUTES = {
	[EGroupBy.Prayer]: '/', // TODO Make a /prayers route
	[EGroupBy.Masjid]: '/masjids',
	[EGroupBy.jumas]: '/jumas'
};

export const PRAYER_NAMES = ['fajr', 'zuhr', 'asr', 'maghrib', 'isha'];

export enum EDay {
	Sunday,
	Monday,
	Tuesday,
	Wednesday,
	Thursday,
	Friday,
	Saturday
}

export enum EPrayer {
	Fajr = 'fajr',
	Zuhr = 'zuhr',
	Asr = 'asr',
	Maghrib = 'maghrib',
	Isha = 'isha'
}

export const MINUTES_PER_HOUR = 60;
export const SECONDS_PER_MINUTE = 60;