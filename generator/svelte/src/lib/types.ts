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

export interface IMasjid {
	iqamas: Record<string, { time: string }>;
	jumas: string[];
	display_name: string;
	address: string;
	website: string;
}

export type TMasjidsJSON = {
	max_jumaas: number;
	masjids: Record<string, IMasjid>;
};
