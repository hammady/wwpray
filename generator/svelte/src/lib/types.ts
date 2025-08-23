import type { EAlertType } from './constants';

export interface IToast {
	type: EAlertType;
	message: string;
	id: number;
}

export interface ISubscribeArgs {
	email: string;
	topics: string[];
}

export interface ISubscribeResponse {
	message: string;
	topics: string[];
}

export type TIqama = {
	time: string;
	changed_on?: string;
	seconds_since_midnight_utc: number | null;
};

export interface IMasjid {
	iqamas: Record<string, TIqama>;
	jumas: string[];
	display_name: string;
	address: string;
	website: string;
	last_updated: string;
}

export type TMasjidsJSON = {
	masjids: Record<string, IMasjid>;
};

export type TPrayer = {
	name: string;
	next: TPrayer;
};

export type TDuration = {
	hours: number;
	minutes: number;
	seconds: number;
};
