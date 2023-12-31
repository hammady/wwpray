from .base import Source
from datetime import datetime, date, time
import pytz


class MasjidBoxSource(Source):
    def __init__(self, apikey, masjidbox_id, timezone):
        self._today = self._get_midnight_in_timezone(timezone).isoformat()
        super().__init__("MasjidBox", headers={
            "Apikey": apikey
        }, url=f"https://api.masjidbox.com/1.0/masjidbox/landing/athany/{masjidbox_id}?get=at&days=9&begin={self._today}",
        timezone=timezone)
    
    @staticmethod
    def _get_midnight_in_timezone(timezone):
        # Get the current time in the specified timezone
        current_time_in_timezone = Source._get_current_time_in_timezone(timezone)
        
        # Set the time to midnight
        midnight_in_timezone = current_time_in_timezone.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return midnight_in_timezone

    @staticmethod
    def _get_prayer_mapping(prayer):
        if prayer == 'zuhr':
            return 'dhuhr'
        else:
            return prayer

    def parse(self):
        if self._response is None:
            raise Exception("No response set for source: " + self.name)
        
        def parse_time(time):
            return datetime.fromisoformat(time).strftime("%-I:%M %p")
        
        timetable = self._response.json()['timetable']

        # search for today, expected to be first element but sometimes not
        today_iqamas = None
        for day in timetable:
            if day['date'] == self._today:
                today_iqamas = day['iqamah']
                break

        iqamas = self.generate_iqamas_output(
            [
                parse_time(today_iqamas[self._get_prayer_mapping(key)])
                for key in self._five_prayers
            ]
        )

        # iterate on timetable until we find jumuah key then parse and return it
        jumas = []
        for day in timetable:
            if 'jumuah' in day:
                jumas = [f"{label} Prayer: {parse_time(juma)}" for juma, label in zip(day['jumuah'], self._counter_labels)]
                break

        return iqamas, jumas
