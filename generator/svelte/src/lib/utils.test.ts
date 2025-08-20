import { describe, it, expect } from 'vitest';
import { getNextPrayerForMasjids } from './utils';
import { getTimeRemainingForNextPrayer } from './utils';
import type { IMasjid } from './types';

// Helper to create a masjid with specific iqama times
function makeMasjid(iqamas: Record<string, number>): IMasjid {
	return {
		display_name: 'Test Masjid',
		address: '123 Test St',
		website: '',
		last_updated: '',
		jumas: [],
		iqamas: Object.fromEntries(
			Object.entries(iqamas).map(([name, seconds]) => [name, { time: '', seconds_since_midnight_utc: seconds }])
		)
	};
}

// Helper to create a pair of masjids A and B
function makeMasjidPair(): [string, IMasjid][] {
	return [
		['A', makeMasjid({ fajr: 25000, zuhr: 40000, asr: 60000, maghrib: 80000, isha: 90000 })],
		['B', makeMasjid({ fajr: 26000, zuhr: 41000, asr: 61000, maghrib: 81000, isha: 91000 })],
	];
}

describe('getNextPrayerForMasjids', () => {
	it('returns the next prayer when all prayers are in the future', () => {
		const now = 20000; // 5:33 AM
		const masjids = makeMasjidPair();
		const result = getNextPrayerForMasjids(masjids, now);
		expect(result?.name).toBe('fajr');
	});

	it('returns the next closest prayer by latest iqama time', () => {
		const now = 30000; // 8:00 AM
		const masjids = makeMasjidPair();
		const result = getNextPrayerForMasjids(masjids, now);
		expect(result?.name).toBe('zuhr');
	});

	it('returns the next prayer even if current time is after zuhr for A but before zuhr for B', () => {
		const now = 40500; // 11:21:40 AM
		const masjids = makeMasjidPair();
		const result = getNextPrayerForMasjids(masjids, now);
		expect(result?.name).toBe('zuhr');
	});

	it('returns the first prayer if all are in the past', () => {
		const now = 95000; // after isha
		const masjids = makeMasjidPair();
		const result = getNextPrayerForMasjids(masjids, now);
		expect(result?.name).toBe('fajr');
	});

	it('returns undefined if masjids is empty', () => {
		const result = getNextPrayerForMasjids([]);
		expect(result).toBeUndefined();
	});
});

describe('getTimeRemainingForNextPrayer', () => {
	it('returns correct time remaining for next prayer when all prayers are in the future', () => {
		const now = 20000; // 5:33 AM
		const masjids = makeMasjidPair();
		const result = getTimeRemainingForNextPrayer(masjids, now);
		// Next prayer is fajr at 25000 (A), so 25000-20000 = 5000 seconds
		// 5000 seconds = 1 hour, 23 minutes, 20 seconds
		expect(result).toEqual({ hours: 1, minutes: 23, seconds: 20 });
	});

	it('returns correct time remaining for next prayer just before zuhr', () => {
		const now = 40900; // 11:21:40 AM
		const masjids = makeMasjidPair();
		const result = getTimeRemainingForNextPrayer(masjids, now);
		// Next prayer is zuhr at 41000 (A), so 41000-40900 = 100 seconds
		// 100 seconds = 1 minute, 40 seconds
		expect(result).toEqual({ hours: 0, minutes: 1, seconds: 40 });
	});

	it('returns correct time remaining for next prayer after zuhr', () => {
		const now = 41100; // after zuhr for both, next is asr
		const masjids = makeMasjidPair();
		const result = getTimeRemainingForNextPrayer(masjids, now);
		// Next prayer is asr at 60000 (A), so 60000-41100 = 18900 seconds
		// 18900 seconds = 5 hours, 15 minutes, 0 seconds
		expect(result).toEqual({ hours: 5, minutes: 15, seconds: 0 });
	});

	it('returns correct time remaining for next prayer after isha (wraps to fajr)', () => {
		const now = 95000; // after isha
		const masjids = makeMasjidPair();
		const result = getTimeRemainingForNextPrayer(masjids, now);
		// Next prayer is fajr at 25000 (A), so 25000-95000 = -70000 + 86400 = 16400
		// 16400 seconds = 4 hours, 33 minutes, 20 seconds
		expect(result).toEqual({ hours: 4, minutes: 33, seconds: 20 });
	});

	it('returns null if masjids is empty', () => {
		const result = getTimeRemainingForNextPrayer([], 20000);
		expect(result).toBeNull();
	});
});
