from unittest import TestCase
from sources.bases.tma import TMASource as TMA


class TestTMA(TestCase):
    days = {
        "100": "One Hundred",
        "300": "Three Hundred"
    }
    timezone = "America/Toronto"

    def test_find_nearest_day_when_day_is_in_list(self):
        tma = TMA(TestTMA.timezone, masjid_id=0)
        self.assertEqual(tma._find_nearest_day(100, TestTMA.days), "One Hundred")
        self.assertEqual(tma._find_nearest_day(300, TestTMA.days), "Three Hundred")

    def test_find_nearest_day_when_day_is_between_two_existing_days(self):
        tma = TMA(TestTMA.timezone, masjid_id=0)
        self.assertEqual(tma._find_nearest_day(200, TestTMA.days), "One Hundred")

    def test_find_nearest_day_when_day_is_smaller_than_smallest_day_in_list(self):
        tma = TMA(TestTMA.timezone, masjid_id=0)
        self.assertEqual(tma._find_nearest_day(50, TestTMA.days), "Three Hundred")

    def test_find_nearest_day_when_day_is_larger_than_largest_day_in_list(self):
        tma = TMA(TestTMA.timezone, masjid_id=0)
        self.assertEqual(tma._find_nearest_day(350, TestTMA.days), "Three Hundred")

    def test_find_nearest_day_when_day_is_not_in_list(self):
        days = {
            "400": "Four Hundred"
        }
        tma = TMA(TestTMA.timezone, masjid_id=0)
        self.assertIsNone(tma._find_nearest_day(100, days))
