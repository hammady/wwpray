from requests import get as requests_get
from datetime import datetime
import pytz

class Source:
    def __init__(self, name, url=None, headers = {}):
        self.name = name
        self.display_name = None
        self.website = None
        self.address = None
        self._headers = headers
        self._url = url
        self._five_prayers = ["fajr", "zuhr", "asr", "maghrib", "isha"]
        self._counter_labels = [
            'First', 'Second', 'Third', 'Fourth', 'Fifth',
            'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth']

    @staticmethod
    def _get_current_time_in_timezone(timezone):
        # Get the current time in UTC
        current_time = datetime.now(pytz.utc)
        
        # Convert UTC time to the specified timezone
        specified_timezone = pytz.timezone(timezone)
        return current_time.astimezone(specified_timezone)

    @staticmethod
    def _parse_time(time_string, timezone):
        # Get the current time in the specified timezone
        current_time = Source._get_current_time_in_timezone(timezone)

        # Parse the time string
        time = datetime.strptime(time_string, '%I:%M %p')
        time = time.replace(year=current_time.year, month=current_time.month, day=current_time.day)

        # Get the time in seconds since the start of the day
        seconds = int((time - time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())

        # Subtract the timezone offset so that the time is in UTC
        return seconds - current_time.utcoffset().total_seconds()
    
    def request(self):
        if self._url is None:
            raise Exception("No URL set for source: " + self.name)
        response = requests_get(
            self._url,
            headers=self._headers,
            timeout=(3.05, 2)) # 3.05 seconds to connect, 2 seconds to read
        response.raise_for_status()
        self._response = response

    def parse(self):
        raise NotImplementedError
