export const APP_NAME = 'Where & When to Pray';

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
	Prayer = 'Prayer',
	Masjid = 'Masjid',
	jumas = 'Jumas'
}

export const GROUP_BY_ROUTES = {
	[EGroupBy.Prayer]: '/', // TODO Make a /prayers route
	[EGroupBy.Masjid]: '/masjids',
	[EGroupBy.jumas]: '/jumas'
};
