import type { EAlertType } from './constants';

export interface IToast {
	type: EAlertType;
	message: string;
}

export interface ISubscribeArgs {
	email: string;
	topics: string[];
}

export interface ISubscribeResponse {
	message: string;
	topics: string[];
}
