import { EAlertType, TOAST_TIMEOUT } from '$lib/constants';
import type { IToast } from '$lib/types';
import { writable } from 'svelte/store';

export const toasts = writable<IToast[]>([]);

const addToast = (type: EAlertType, message: string) => {
	toasts.update((t) => [{ type, message, id: Date.now() }, ...t]);

	setTimeout(() => {
		toasts.update((t) => t.filter((toast) => toast.id !== t[0].id));
	}, TOAST_TIMEOUT);
};

export const toast = (message: string) => {
	addToast(EAlertType.Info, message);
};

toast.info = (message: string) => {
	addToast(EAlertType.Info, message);
};

toast.success = (message: string) => {
	addToast(EAlertType.Success, message);
};

toast.error = (message: string) => {
	addToast(EAlertType.Error, message);
};

toast.warn = (message: string) => {
	addToast(EAlertType.Warning, message);
};
