from .base import Source
from time import time

class MasjidalSource(Source):
    def __init__(self, masjid_id, extra_jumas=[]):
        epoch_ms = int(time()*1000)
        super().__init__("Masjidal", headers={
            "Accept": "*/*"
        }, url=f"https://masjidal.com/api/v1/time?masjid_id={masjid_id}&_={epoch_ms}")
        self._extra_jumas = extra_jumas

    def parse(self):
        if self._response is None:
            raise Exception("No response set for source: " + self.name)
        payload = self._response.json()
        if payload["status"] != "success":
            raise Exception(f"Error from source: {self.name} - status: {payload['status']}, message: {payload['message']}")

        combined_times = payload["data"]["iqama"]

        five_prayers = ["fajr", "zuhr", "asr", "maghrib", "isha"]

        iqamas = {f"{key}": {"time": combined_times[key]} for key in five_prayers}

        # reduce combined times to just the jummah times by removing the 5 prayers
        for key in five_prayers:
            del combined_times[key]

        # append the extra jumas to the juma times
        juma_times = list(combined_times.values()) + self._extra_jumas

        # construct the final juma labels
        jumas = [f"{label} Prayer: {value}"
                 for value, label in zip(juma_times, self._counter_labels)]

        return iqamas, jumas
