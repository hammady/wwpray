from .base import Source


class TMASource(Source):
    def __init__(self, timezone, masjid_id):
        super().__init__("The Masjid App", headers={
            "Accept": "application/json",
        }, url=f"https://themasjidapp.net/{masjid_id}",
        timezone=timezone)
    
    @staticmethod
    def _find_nearest_day(day_of_year, days):
        # find the nearest day in the list of days
        started_on = day_of_year
        while True:
            if str(day_of_year) in days:
                return days[str(day_of_year)]
            day_of_year -= 1
            if day_of_year < 1:
                day_of_year = 366
            if day_of_year == started_on:
                return None

    @staticmethod
    def _get_prayer_mapping(prayer):
        if prayer == 'zuhr':
            return 'dhuhr'
        else:
            return prayer

    def parse(self):
        if self._response is None:
            raise Exception("No response set for source: " + self.name)
        masjid = self._response.json()["masjid"]
        days = masjid["iqamas"]
        today = Source._get_current_time_in_timezone(self._timezone)
        day_of_year = today.timetuple().tm_yday
        nearest_day = self._find_nearest_day(day_of_year, days)
        if nearest_day is None:
            raise Exception("No iqamas found for source: " + self.name)
        
        iqamas = self.generate_iqamas_output(
            [
                nearest_day[self._get_prayer_mapping(key)]
                for key in self._five_prayers
            ]
        )

        jumas = [f"{juma['timeDesc']} - {juma['locationDesc']}" for juma in masjid["jumas"]]

        return iqamas, jumas
