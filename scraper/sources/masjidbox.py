from .base import Source
from datetime import datetime, date, time

class MasjidBoxSource(Source):
    def __init__(self, apikey, xkey, xfrom):
        # get today's midnight time in iso format including local time zone
        today = datetime.combine(date.today(), time(0)).astimezone().isoformat(timespec='milliseconds')
        super().__init__("MasjidBox", headers={
            "apikey": apikey,
            "x-key": xkey,
            "x-from": xfrom
        }, url=f"https://api.masjidbox.com/1.0/masjidbox/landing/athany?get=wg&days=9&begin={today}")
        
    def parse(self):
        if self._response is None:
            raise Exception("No response set for source: " + self.name)
        
        def parse_time(time):
            return datetime.fromisoformat(time).strftime("%-I:%M %p")
        
        timetable = self._response.json()['timetable']
        today_iqamas = timetable[0]['iqamah']

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
                jumas = [parse_time(juma) for juma in day['jumuah']]
                break

        return iqamas, jumas