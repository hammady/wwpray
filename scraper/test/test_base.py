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

    # test parsing of jumas arrays

    def make_source(self):
        return Source("test", timezone=self.timezone)

    def expected_seconds(self, hour, minute):
        return hour * self.seconds_in_hour + minute * 60 - self.timezone_offset

    def test_parse_jumas_returns_same_size(self):
        source = self.make_source()
        jumas = ["First Prayer: 12:15 PM", "Second Prayer: 1:15 PM", "Third Prayer: 2:30PM"]
        self.assertEqual(len(source.parse_jumas(jumas)), len(jumas))

    def test_parse_jumas_empty(self):
        source = self.make_source()
        self.assertEqual(source.parse_jumas([]), [])

    def test_parse_jumas_prayer_prefix_with_space(self):
        source = self.make_source()
        jumas = ["First Prayer: 12:15 PM", "Second Prayer: 1:15 PM", "Third Prayer: 2:30PM"]
        self.assertEqual(source.parse_jumas(jumas), [
            self.expected_seconds(12, 15),
            self.expected_seconds(13, 15),
            self.expected_seconds(14, 30),
        ])

    def test_parse_jumas_lowercase_pm(self):
        source = self.make_source()
        jumas = ["First Prayer: 1:00 pm", "Second Prayer: 2:00 pm", "Third Prayer: 3:00 pm"]
        self.assertEqual(source.parse_jumas(jumas), [
            self.expected_seconds(13, 0),
            self.expected_seconds(14, 0),
            self.expected_seconds(15, 0),
        ])

    def test_parse_jumas_picks_first_time(self):
        # "Khutbah ... - Jammah ..." should pick the Khutbah (first) time
        source = self.make_source()
        jumas = [
            "1st: Khutbah: 1:05 pm - Jammah: 1:25 pm",
            "2nd: Khutbah: 1:40 pm - Jammah: 02:00 pm",
            "3rd: Khutbah: 02:15 pm - Jammah: 02:35 pm",
            "4th: Khutbah: 02:50 pm - Jammah: 03:10 pm",
        ]
        self.assertEqual(source.parse_jumas(jumas), [
            self.expected_seconds(13, 5),
            self.expected_seconds(13, 40),
            self.expected_seconds(14, 15),
            self.expected_seconds(14, 50),
        ])

    def test_parse_jumas_dotted_meridiem(self):
        # times formatted as "P.M."
        source = self.make_source()
        jumas = [
            "Sheikh 1 - (English) 12:15 P.M.",
            "Sheikh 2 - (English) 1:15 P.M.",
            "Sheikh 3 - (Arabic) 2:15 PM",
            "Sheikh 4 - (English) 3:15 P.M.",
        ]
        self.assertEqual(source.parse_jumas(jumas), [
            self.expected_seconds(12, 15),
            self.expected_seconds(13, 15),
            self.expected_seconds(14, 15),
            self.expected_seconds(15, 15),
        ])

    def test_parse_jumas_azaan_iqama_picks_first(self):
        # "Azaan: 1:30PM, Iqama: 1:50PM" should pick Azaan (first) time
        source = self.make_source()
        jumas = ["Azaan: 1:30PM, Iqama: 1:50PM"]
        self.assertEqual(source.parse_jumas(jumas), [self.expected_seconds(13, 30)])

    def test_parse_jumas_with_trailing_text(self):
        # time followed by parenthetical notes
        source = self.make_source()
        jumas = [
            "1st Jumma: 1:25 PM (Local Imam) at Masjid (Limited Parking)",
            "2nd Jumma: 2:15 PM (Visiting Imam) at Masjid (Limited Parking)",
            "3rd Jumma: 3:10 PM (Visiting Imam) at Masjid (Limited Parking)",
        ]
        self.assertEqual(source.parse_jumas(jumas), [
            self.expected_seconds(13, 25),
            self.expected_seconds(14, 15),
            self.expected_seconds(15, 10),
        ])

    def test_parse_jumas_no_space_pm(self):
        # time with no space before PM and multiple location lines
        source = self.make_source()
        jumas = [
            "MNN Masjid: 1st: 1:15PM",
            "MNN Masjid: 2nd: 2:15PM",
            "MNN Masjid: 3rd: 3:00PM",
            "Ruth Thompson School Gym: 1st: 1:30PM",
            "Ruth Thompson School Gym: 2nd: 2:15PM",
        ]
        self.assertEqual(source.parse_jumas(jumas), [
            self.expected_seconds(13, 15),
            self.expected_seconds(14, 15),
            self.expected_seconds(15, 0),
            self.expected_seconds(13, 30),
            self.expected_seconds(14, 15),
        ])

    def test_parse_jumas_time_at_start(self):
        # time at the start followed by description
        source = self.make_source()
        jumas = [
            "12:35 pm - Shalimar. Walk-in. Come 5 mins early.",
            "1:35 pm - Shalimar. Walk-in. Come 5 mins early.",
        ]
        self.assertEqual(source.parse_jumas(jumas), [
            self.expected_seconds(12, 35),
            self.expected_seconds(13, 35),
        ])

    def test_parse_jumas_glued_label(self):
        # "PrayerKhutbah" glued before the dash and time
        source = self.make_source()
        jumas = [
            "1st PrayerKhutbah - 1:30 PM - English",
            "2nd PrayerKhutbah - 2:30 PM - Urdu",
            "3rd PrayerKhutbah - 3:30 PM - English",
        ]
        self.assertEqual(source.parse_jumas(jumas), [
            self.expected_seconds(13, 30),
            self.expected_seconds(14, 30),
            self.expected_seconds(15, 30),
        ])

    def test_parse_jumas_no_time_returns_none(self):
        source = self.make_source()
        self.assertEqual(source.parse_jumas(["No time here", "1:00 PM"]), [
            None,
            self.expected_seconds(13, 0),
        ])