from .base import Source
from datetime import datetime, date, time
import pytz


class MasjidBoxSource(Source):
    def __init__(self, apikey, masjidbox_id, timezone):
        self._today = self._get_midnight_in_timezone(timezone).isoformat()
        super().__init__("MasjidBox", headers={
            "Apikey": apikey
        }, url=f"https://api.masjidbox.com/1.0/masjidbox/landing/athany/{masjidbox_id}?get=at&days=9&begin={self._today}")
    
    @staticmethod
    def _get_midnight_in_timezone(timezone):
        # Get the current time in UTC
        current_time = datetime.now(pytz.utc)
        
        # Convert UTC time to the specified timezone
        specified_timezone = pytz.timezone(timezone)
        current_time_in_timezone = current_time.astimezone(specified_timezone)
        
        # Set the time to midnight
        midnight_in_timezone = current_time_in_timezone.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return midnight_in_timezone
    
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

        iqamas = {
            "fajr": {
                "time": parse_time(today_iqamas['fajr'])
            },
            "zuhr": {
                "time": parse_time(today_iqamas['dhuhr'])
            },
            "asr": {
                "time": parse_time(today_iqamas['asr'])
            },
            "maghrib": {
                "time": parse_time(today_iqamas['maghrib'])
            },
            "isha": {
                "time": parse_time(today_iqamas['isha'])
            },
        }

        # iterate on timetable until we find jumuah key then parse and return it
        jumas = []
        for day in timetable:
            if 'jumuah' in day:
                jumas = [f"{label} Prayer: {parse_time(juma)}" for juma, label in zip(day['jumuah'], self._counter_labels)]
                break

        return iqamas, jumas
