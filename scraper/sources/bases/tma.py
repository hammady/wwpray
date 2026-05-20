from .base import Source


class TMASource(Source):
    def __init__(self, timezone, masjid_id):
        super().__init__("The Masjid App", headers={
            "Accept": "application/json",
        }, url=f"https://themasjidapp.net/{masjid_id}",
        timezone=timezone)
    
    @staticmethod
    def _find_nearest_day_with_index(day_of_year, days):
        # find the nearest day in the list of days, returning (day_number, day_data)
        started_on = day_of_year
        while True:
            if str(day_of_year) in days:
                return (day_of_year, days[str(day_of_year)])
            day_of_year -= 1
            if day_of_year < 1:
                day_of_year = 366
            if day_of_year == started_on:
                return None

    @staticmethod
    def _find_nearest_day(day_of_year, days):
        # find the nearest day in the list of days
        result = TMASource._find_nearest_day_with_index(day_of_year, days)
        return result[1] if result is not None else None

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

        collected = {}
        search_from = day_of_year
        visited_days = set()
        while len(collected) < len(self._five_prayers):
            result = self._find_nearest_day_with_index(search_from, days)
            if result is None:
                break
            found_day, day_data = result
            if found_day in visited_days:
                break
            visited_days.add(found_day)
            for key in self._five_prayers:
                mapped_key = self._get_prayer_mapping(key)
                if key not in collected and mapped_key in day_data:
                    collected[key] = day_data[mapped_key]
            search_from = found_day - 1
            if search_from < 1:
                search_from = 366

        if len(collected) < len(self._five_prayers):
            raise Exception("No iqamas found for source: " + self.name)

        iqamas = self.generate_iqamas_output(
            [collected[key] for key in self._five_prayers]
        )

        jumas = [f"{juma['timeDesc']} - {juma['locationDesc']}" for juma in masjid["jumas"]]

        return iqamas, jumas
