from requests import get as requests_get, post as requests_post
from datetime import datetime
import pytz
import re

class Source:
    def __init__(self, name, url=None, timezone='', headers={},
                http_method='GET', request_body=None):
        self.name = name
        self._url = url
        self._timezone = timezone
        self._headers = headers
        self.display_name = None
        self.website = None
        self.address = None
        self._five_prayers = ["fajr", "zuhr", "asr", "maghrib", "isha"]
        self._counter_labels = [
            'First', 'Second', 'Third', 'Fourth', 'Fifth',
            'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth']
        if http_method not in ['GET', 'POST']:
            raise ValueError("http_method must be either 'GET' or 'POST'")
        self._http_method = requests_get if http_method == 'GET' else requests_post
        self._request_body = request_body

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

        # Normalize: remove any space(s) before AM/PM
        time_string = re.sub(r'\s+(AM|PM)$', r'\1', time_string.strip(), flags=re.IGNORECASE)
        format = '%I:%M%p'
        try:
            time = datetime.strptime(time_string, format)
        except ValueError:
            # fallback to last minute of day if the time string is not in the expected format
            time = datetime.strptime('11:59PM', format)
        time = time.replace(year=current_time.year, month=current_time.month, day=current_time.day)

        # Get the time in seconds since the start of the day
        seconds = int((time - time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())

        # Subtract the timezone offset so that the time is in UTC
        return int(seconds - current_time.utcoffset().total_seconds())
    
    def request(self):
        if self._url is None:
            raise Exception("No URL set for source: " + self.name)
        response = self._http_method(
            self._url,
            headers=self._headers,
            data=self._request_body,
            timeout=(3.05, 6)) # 3.05 seconds to connect, 6 seconds to read
        response.raise_for_status()
        self._response = response

    def parse(self):
        raise NotImplementedError

    def generate_iqamas_output(self, iqama_times):
        if len(iqama_times) != len(self._five_prayers):
            raise Exception(f"Expected {len(self._five_prayers)} iqama times, got {len(iqama_times)}")

        return {
            f"{key}": {
                "time": iqama_time,
                "seconds_since_midnight_utc": self._parse_time(iqama_time, self._timezone)
            }
            for key, iqama_time in zip(self._five_prayers, iqama_times)
        }
