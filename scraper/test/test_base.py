from unittest import TestCase
from sources.bases.base import Source
from datetime import datetime
import pytz

class TestSource(TestCase):
    timezone = "America/Toronto"
    # calculate the timezone offset in seconds
    now = datetime.now()
    timezone_offset = pytz.timezone(timezone).localize(now).utcoffset().total_seconds()

    seconds_in_hour = 3600

    def test_timezone_offset(self):
        # Toronto is in EST (UTC-5) during the winter and EDT (UTC-4) during the summer
        dst_adjustment = pytz.timezone(self.timezone).dst(self.now).total_seconds()
        self.assertEqual(self.timezone_offset, -5 * self.seconds_in_hour + dst_adjustment)

    def assert_time_equals(self, time_string, expected_seconds_since_midnight):
        self.assertEqual(
            Source._parse_time(time_string, self.timezone),
            expected_seconds_since_midnight - self.timezone_offset)
        
    # test parsing times from midnight to midnight in the standard 12-hour format with AM/PM

    def test_parse_time_12_00_AM(self):
        self.assert_time_equals("12:00 AM", 0)

    def test_parse_time_12_01_AM(self):
        self.assert_time_equals("12:01 AM", 60)

    def test_parse_time_12_59_AM(self):
        self.assert_time_equals("12:59 AM", self.seconds_in_hour - 60)

    def test_parse_time_1_00_AM(self):
        self.assert_time_equals("1:00 AM", self.seconds_in_hour)

    def test_parse_time_12_00_PM(self):
        self.assert_time_equals("12:00 PM", 12 * self.seconds_in_hour)

    def test_parse_time_7_00_PM(self):
        self.assert_time_equals("7:00 PM", 19 * self.seconds_in_hour)

    def test_parse_time_8_00_PM(self):
        self.assert_time_equals("8:00 PM", 20 * self.seconds_in_hour)

    def test_parse_time_11_00_PM(self):
        self.assert_time_equals("11:00 PM", 23 * self.seconds_in_hour)

    def test_parse_time_11_59_PM(self):
        self.assert_time_equals("11:59 PM", 24 * self.seconds_in_hour - 60)

    # test variations of the time format

    def test_parse_time_12_00_am(self):
        self.assert_time_equals("12:00 am", 0)

    def test_parse_time_12_00_pm(self):
        self.assert_time_equals("12:00 pm", 12 * self.seconds_in_hour)

    def test_parse_time_11_59_pm(self):
        self.assert_time_equals("11:59 pm", 24 * self.seconds_in_hour - 60)

    def test_parse_time_01_00_am(self):
        self.assert_time_equals("01:00 am", 1 * self.seconds_in_hour)

    def test_parse_time_08_00_pm(self):
        self.assert_time_equals("08:00 pm", 20 * self.seconds_in_hour)

    def test_parse_time_10_30pm(self):
        self.assert_time_equals("10:30pm", 22 * self.seconds_in_hour + 30 * 60)

    def test_parse_time_1_30am(self):
        self.assert_time_equals("1:30am", 1 * self.seconds_in_hour + 30 * 60)

    def test_parse_time_10_30PM(self):
        self.assert_time_equals("10:30PM", 22 * self.seconds_in_hour + 30 * 60)

    def test_parse_time_1_30AM(self):
        self.assert_time_equals("1:30AM", 1 * self.seconds_in_hour + 30 * 60)

    def test_parse_time_invalid(self):
        self.assertIsNone(Source._parse_time("invalid_time", self.timezone))